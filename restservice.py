from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from messages import Message
from piguardtyping import JSON
import json
import queue
import storagemanager
import authmanager
import configmanager
import ssl
import os


class RestRequestHandler(BaseHTTPRequestHandler):
    # Timeout to avoid the server getting stuck if connection is dropped
    timeout = 5

    def do_GET(self):
        if self.verify_authentication():
            api_type, parameter = self.decode_request()

            if api_type == "command" and parameter is not None:
                self.execute_command(parameter)
            elif api_type == "image" and parameter is not None:
                self.retrieve_image(parameter)
            elif api_type == "statuses":
                hours = 0
                if parameter is not None:
                    hours = int(parameter)
                self.retrieve_statuses(hours)
            elif api_type == "live_video":
                self.stream_camera()
            else:
                self.send_error(400, "Method \"" + api_type + "\" not found!")

        else:
            self.do_AUTH()

    def decode_request(self) -> (str, str):
        request_path = self.path[1:]
        if "/" in request_path:
            api_type = request_path[:request_path.index("/", 1)]
            parameter = request_path[request_path.index("/", 1)+1:]
            return api_type, parameter
        else:
            return request_path, None

    def verify_authentication(self) -> bool:
        if self.headers['Authorization'] is not None and authmanager.manager.authenticate(self.headers["Authorization"][6:]):
            return True
        else:
            return False

    def do_AUTH(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"PiGuard\"")
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("Authentication failed!", "UTF-8"))

    def do_OK_HEAD(self, content_type: str):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def execute_command(self, command: str):
        messages_queue = queue.Queue()
        self.server.commands.put((command, messages_queue))

        command_output = list()
        while True:
            message = messages_queue.get()
            if message == Message.END:
                break
            command_output.append(message)

        json_response = _generate_response(command_output)

        self.do_OK_HEAD("application/json")
        self.wfile.write(bytes(json.dumps(json_response), "utf-8"))

    def retrieve_image(self, image_name: str):
        try:
            if image_name.endswith(".jpg"):
                self.do_OK_HEAD("image/jpeg")
                storagemanager.manager.write_image_on_stream(image_name, self.wfile)
            else:
                self.send_error(500, "Permission denied")
        except:
            self.send_error(404, "File Not Found: %s" % image_name)

    def retrieve_statuses(self, hours: int):
        try:
            self.do_OK_HEAD("application/json")
            storagemanager.manager.write_statuses_on_stream(self.wfile, hours)
        except:
            self.send_error(404, "File Not Found: statuses.json")

    def stream_camera(self):
        try:
            self.do_OK_HEAD("multipart/x-mixed-replace; boundary=--frame")
            frame_queue = queue.Queue()
            messages_queue = queue.Queue()
            messages_queue.put(frame_queue)
            self.server.commands.put(("stream_camera", messages_queue))
            while True:
                frame = frame_queue.get(timeout=10)
                messages_queue.put(Message.NEXT)
                self.wfile.write(b"--frame\r\n")
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                self.wfile.write(frame.get_stream().read())
                self.wfile.write(b"\r\n")
        except:
            print("Streaming ended!")

        messages_queue.put(Message.END)


class RestServer(ThreadingMixIn, HTTPServer):

    def __init__(self, server_address: (str, int), RequestHandlerClass, commands_queue: queue.Queue, key_path: str, certificate_path: str):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue
        self.socket = ssl.wrap_socket(self.socket, keyfile=key_path, certfile=certificate_path, server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)


def get_ip_address() -> str:
    with os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d " " -f1') as f:
        return f.read()


def get_rest_server(commands_queue: queue.Queue) -> RestServer:
    certificate_path = configmanager.config["rest_service"]["server_certificate_location"]
    key_path = configmanager.config["rest_service"]["server_key_location"]
    HOST, PORT = get_ip_address(), 2728
    return RestServer((HOST, PORT), RestRequestHandler, commands_queue, key_path, certificate_path)


def _generate_response(output: [Message]) -> JSON:
    json_response = dict()
    json_response["response"] = dict()
    json_response["response"]["system_status"] = dict()
    if Message.status_started in output:
        json_response["response"]["system_status"]["started"] = True
    else:
        json_response["response"]["system_status"]["started"] = False

    if Message.mode_monitoring in output:
        json_response["response"]["system_status"]["mode"] = "monitoring"
    elif Message.mode_surveillance in output:
        json_response["response"]["system_status"]["mode"] = "surveillance"

    json_response["response"]["system_output"] = list(map(lambda m: m.name, output))

    return json_response

