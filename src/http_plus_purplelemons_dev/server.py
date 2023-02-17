
from .types import Method, Headers, Request, Body
import socketserver
import socket

class Handler(socketserver.BaseRequestHandler):

    request:socket.socket
    method:Method
    path:str
    protocol:str
    headers:Headers
    body:Body
    
    def handle(self):
        # Per IBM [1], the maximum size of a HTTP request is 2MB (2x10^6 bytes).
        raw=self.request.recv(2*10**6)
        self.method=Method(raw.split(b" ")[0].decode())
        self.path=raw.split(b" ")[1].decode()
        self.protocol=raw.split(b" ")[2].split(b"\r")[0].decode()
        self.headers=Headers(raw.split(b"\r\n\r\n")[0].split(b"\r\n")[1:])
        # above code (except for recv) runs at about 10.6 micro seconds.




# Notes:
# This is the socket branch of httpplus. The goal is to provide at least same functions that the main branch does, hopefully more.
# By directly interfacing with the socket, I hope that time per request will be reduced.
# I'm not sure if I'll post the numbers, but if you want to, please make a pull request.

#  [1] https://www.ibm.com/mysupport/s/question/0D50z00005q4C8LCAU/how-to-set-maximum-acceptable-http-request-post-size?language=en_US
