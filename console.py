import socketserver
import queue

class CommandHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.data = self.rfile.readline().strip()
        command = str(self.data, "utf-8")
        self.server.commands.put(command)
        self.wfile.write(bytes("Command executed!\n", "utf-8"))

class ConsoleServer(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, commands_queue):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.commands = commands_queue

#if __name__ == "__main__":
#    HOST, PORT = "localhost", 9999

#    commands = queue.Queue()
#    server = ConsoleServer((HOST, PORT), CommandHandler, commands)
#    server.serve_forever()




