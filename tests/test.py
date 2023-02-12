
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_DELETE(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")
    
    def do_PATCH(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, world!")

server = HTTPServer(("0.0.0.0", 8080), RequestHandler)
server.serve_forever()
