import socketserver
import queue

class CommandHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.wfile.write(bytes("PiGuard command console:\n", "utf-8"))
        while True:
            self.wfile.write(bytes(">>> ", "utf-8"))
            data = self.rfile.readline().strip()
            command = str(data, "utf-8")
            if "exit" == command:
                break

            messages_queue = queue.Queue()
            self.server.commands.put((command, messages_queue))
            
            while True:
                message = messages_queue.get()
                if message == "END":
                    break
                self.wfile.write(bytes(message + "\n", "utf-8"))
            
            if "shutdown" == command:
                break


class ConsoleServer(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, commands_queue):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue




