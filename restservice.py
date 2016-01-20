from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import queue


class RestRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        api_type = self.path[1:self.path.index("/", 1)]
        parameter = self.path[self.path.index("/", 1)+1:]

        if api_type == "command":
            self.execute_command(parameter)
        elif api_type == "image":
            self.retrieve_image(parameter)

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

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.wfile.write(bytes(json.dumps(json_response), "utf-8"))

    def retrieve_image(self, image_name):
        try:
            if image_name.endswith(".jpg"):
                image_file = open("/home/pi/Pictures/PiGuard/" + image_name, 'rb')
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                self.wfile.write(image_file.read())
                image_file.close()
            else:
                self.send_error(500, "Permission denied")
        except:
            self.send_error(404, "File Not Found: %s" % image_name)



class RestServer(HTTPServer):

    def __init__(self, server_address, RequestHandlerClass, commands_queue):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue
