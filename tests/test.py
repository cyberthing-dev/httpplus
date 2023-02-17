
from socketserver import BaseRequestHandler, TCPServer

class handler(BaseRequestHandler):
    def handle(self):
        print(self.request.recv(1024))

server=TCPServer(("localhost", 8080), handler).serve_forever()
