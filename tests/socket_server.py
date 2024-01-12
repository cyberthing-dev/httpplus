
from http.server import SimpleHTTPRequestHandler, HTTPServer
from json import dumps
from socket import socket

def dict_socket(sock:socket):
    return {
        "family": sock.family,
        "type": sock.type,
        "proto": sock.proto,
        "laddr": sock.getsockname(),
        "server": sock.getpeername()[0],
        "port": sock.getpeername()[1]
    }

class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        print(self)
        super().do_GET()

    def __repr__(self) -> str:
        for k,v in self.__dict__.items():
            print(f"{k}: {type(v)}")
            try:
                print(f"{k}: {v.__dict__}")
            except:
                print(f"{k} has no __dict__")
        return "hi"#self.__dict__["request"].__dict__
        #return dumps(self.__dict__, indent=2)



server = HTTPServer(("0.0.0.0", 80), Handler)
server.serve_forever()
