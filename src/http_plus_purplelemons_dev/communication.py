
from http.server import BaseHTTPRequestHandler
from dataclasses import dataclass
from json import loads, dumps

class RouteExistsError(Exception):
    """Raised when a route already exists."""
    def __init__(self, route:str=...):
        super().__init__(f"Route {route} already exists." if route else "Route already exists.")

@dataclass
class Route:
    """Custom dataclass for optimizing route creation, readability, and resolution.

    Attributes:
        `send_to (str)`: The directory to respond with in the form of `./path/to/directory/`, `path/to/file.ext`, etc..
        `route_type (str)`: The type of route. Can be either `pages` or `errors`.
    """
    send_to:str
    route_type:str

class Request:
    """
    Request object, passed into HTTP method listeners as the first argument.
    """
    def __init__(self, request:BaseHTTPRequestHandler):
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
    """
    Response object, passed into HTTP method listeners as the second argument.
    You must return this from the HTTP method listener function.
    """
    def __init__(self, response:BaseHTTPRequestHandler):
        self.response = response
        self.headers = {}
        self.body = b""
        self.status = 200
        self.linked = False
        self._route: Route

    def set_header(self, header:str, value:str) -> None:
        self.headers[header] = value
    
    def set_body(self, body:bytes|str|dict) -> None:
        """
        Automatically pareses the body into bytes, and sets the Content-Type header to application/json if the body is a dict.
        Will be overwritten if `Response

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

    def route(self,path_to:str,link:bool=False):
        """
        Will route to the specified path (`path_to`).
        If `link` is True, this will route to a page rather than a file or directory.
        (Note: If this is a linked route, then path can be a url to another page entirely.)

        Args:
            `path_to (str)`: The path to route to.
            `link (bool)`: Whether or not to route to a page.
        """
        if link:
            self.headers["Location"] = path_to
            self.status = 302 # Found == temporary redirect
        else:
            self._route = Route(path_to, "pages")

