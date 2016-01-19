from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import queue


class RestRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        command = self.path[1:]
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


class RestServer(HTTPServer):

    def __init__(self, server_address, RequestHandlerClass, commands_queue):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue
