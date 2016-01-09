import socketserver


class CommandHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.wfile.write(bytes("PiGuard command console:\n", "utf-8"))
        while True:
            self.wfile.write(bytes(">>> ", "utf-8"))
            data = self.rfile.readline().strip()
            command = str(data, "utf-8")
            if "exit" == command:
                break
            
            self.server.commands.put(command)
            
            while True:
                message = self.server.messages.get()
                if message == "END":
                    break
                self.wfile.write(bytes(message + "\n", "utf-8"))
            
            if "shutdown" == command:
                break


class ConsoleServer(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, commands_queue, messages_queue):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue
        self.messages = messages_queue





