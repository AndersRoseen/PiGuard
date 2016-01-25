from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import queue
import storagemanager
import ssl


class RestRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.verify_authentication():
            api_type, parameter = self.decode_request()

            if api_type == "command" and parameter is not None:
                self.execute_command(parameter)
            elif api_type == "image" and parameter is not None:
                self.retrieve_image(parameter)
            elif api_type == "statuses":
                self.retrieve_statuses()
            else:
                self.send_error(400, "Method \"" + api_type + "\" not found!")

        else:
            self.do_AUTH()

    def decode_request(self):
        request_path = self.path[1:]
        if "/" in request_path:
            api_type = request_path[:request_path.index("/", 1)]
            parameter = request_path[request_path.index("/", 1)+1:]
            return api_type, parameter
        else:
            return request_path, None

    def verify_authentication(self):
        if self.headers['Authorization'] is not None and self.server.auth_manager.authenticate(self.headers["Authorization"][6:]):
            return True
        else:
            return False

    def do_AUTH(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"PiGuard\"")
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("Authentication failed!", "UTF-8"))

    def do_OK_HEAD(self, content_type):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def execute_command(self, command):
        messages_queue = queue.Queue()
        self.server.commands.put((command, messages_queue))

        command_output = list()
        while True:
            message = messages_queue.get()
            if message == "END":
                break
            command_output.append(message)

        json_response = dict()
        json_response["command_execution"] = "completed"
        json_response["command_output"] = command_output

        self.do_OK_HEAD("application/json")
        self.wfile.write(bytes(json.dumps(json_response), "utf-8"))

    def retrieve_image(self, image_name):
        try:
            if image_name.endswith(".jpg"):
                self.do_OK_HEAD("image/jpeg")
                storagemanager.manager.write_image_on_stream(image_name, self.wfile)
            else:
                self.send_error(500, "Permission denied")
        except:
            self.send_error(404, "File Not Found: %s" % image_name)

    def retrieve_statuses(self):
        try:
            self.do_OK_HEAD("application/json")
            storagemanager.manager.write_statuses_on_stream(self.wfile)
        except:
            self.send_error(404, "File Not Found: statuses.json")


class RestServer(HTTPServer):

    def __init__(self, server_address, RequestHandlerClass, commands_queue, auth_manager, certificate_path):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue
        self.socket = ssl.wrap_socket(self.socket, certfile=certificate_path, server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)
        self.auth_manager = auth_manager
