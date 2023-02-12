
from http.server import BaseHTTPRequestHandler
from json import loads, dumps



class Request:
    """
    Request object, passed into HTTP method listeners as the first argument.
    """
    def __init__(self, request:BaseHTTPRequestHandler) -> "Request":
        self.request = request
        self.path = request.path
        self.method = request.command
        self.headers = request.headers
        self.body = request.rfile.read()
        self.ip, self.port = request.client_address


    # Dunder pog
    def __repr__(self) -> str:
        return f"Request({self.method=}, {self.path=}, {self.headers=}, {self.body=})"
    def __str__(self) -> str:
        return self.__repr__()
    def __eq__(self, o:object) -> bool:
        if isinstance(o, Request):
            return self.__repr__() == o.__repr__()
        return False
    def __ne__(self, o:object) -> bool:
        return not self.__eq__(o)
    def __hash__(self) -> int:
        return hash(self.__repr__())
    def __iter__(self) -> "Request":
        return self
    def __next__(self) -> "Request":
        raise StopIteration
    def __len__(self) -> int:
        return 0
    def __bool__(self) -> bool:
        return True

    def get_header(self, header:str) -> str:
        return self.headers[header]

    def json(self) -> dict:
        return loads(self.body)

    def text(self) -> str:
        return self.body.decode()


class Response:
    def __init__(self, response:BaseHTTPRequestHandler) -> "Response":
        self.response = response
        self.headers = {}
        self.body = b""
        self.status = 200

    def set_header(self, header:str, value:str) -> None:
        self.headers[header] = value
    
    def set_body(self, body:bytes|str|dict) -> None:
        """Automatically pareses the body into bytes, and sets the Content-Type header to application/json if the body is a dict.
        
        Args:
            `body (bytes|str|dict)`: The body of the response.
        """
        if isinstance(body, dict):
            self.set_header("Content-Type", "application/json")
            self.body = dumps(body).encode()
        elif isinstance(body, str):
            self.body = body.encode()
        else:
            self.body = body
