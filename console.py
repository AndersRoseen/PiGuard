import socketserver
import queue
import authmanager


class CommandHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.wfile.write(bytes("Welcome to PiGuard command console!\n", "utf-8"))

        authenticated = False
        failures = 0
        while failures < 3:
            self.wfile.write(bytes("Login (type username:password): ", "utf-8"))
            auth_data = str(self.rfile.readline().strip(), "utf-8")
            authenticated = authmanager.manager.encode_and_authenticate(auth_data)

            if authenticated:
                self.wfile.write(bytes("Login successful!\n", "utf-8"))
                break
            else:
                self.wfile.write(bytes("Login failed!\n", "utf-8"))
                failures += 1

        while authenticated:
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




