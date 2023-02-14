
from communication import *
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    """
    A proprietary HTTP request handler for the server.
    It is highly suggested that you have a good understanding of
        http.server and httpplus before modifying or substituting this class.
    """

    routes:dict[str,dict[str,Route]] = {
        "get": {},
        "post": {},
        "put": {},
        "delete": {},
        "patch": {},
        "options": {},
        "head": {},
        "trace": {}
    }

    @staticmethod
    def resolve_path(path:str) -> str:
        """
        Returns the content at the path of a *local* url or file.
        For url redirection, use `Response.redirect`.
        """
        ...

    def do_GET(self):
        for path in self.routes["get"]:
            if self.path == path:
                self.routes["get"][path].send_to


class Server:
    """
    Main class for the HTTP Plus server library.
    * Initialize the server with `server = Server(host, port)`.
    * Listen to HTTP methods with `@server.<method>(path)`,
        for example `@server.get("/")`.
    """

    def __init__(self, host:str, port:int, *, debug:bool=False, **kwargs):
        """Initializes the server.
        Args:
            `host (str)`: The host to listen on.
            `port (int)`: The port to listen on.
            `debug (bool)`: Whether or not to print debug messages.
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.handler = Handler

    def listen(self) -> None:
        """Starts the server, a blocking operation on the current thread."""
        if self.debug:
            print(f"Listening on http://{self.host}:{self.port}")
        HTTPServer((self.host, self.port), self.handler).serve_forever()

    def base(self, request: Request, response: Response) -> Response:
        """The base function for all routes.
        Args:
            `request (Request)`: The request object.
            `response (Response)`: The response object.
        """
        return response


### DECORATORS == boilerplate :( ###
def all(server:Server, path:str):
    """
    A decorator that adds a route to the server. Listens to all HTTP methods.
    Args:
        `path (str)`: The path to respond to.
    """
    # This code is very clever if i do say so myself
    @get(server, path)
    @post(server, path)
    @put(server, path)
    @delete(server, path)
    @patch(server, path)
    @options(server, path)
    @head(server, path)
    @trace(server, path)
    def decorator(func):
        ...
    return decorator

def get(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to GET requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        if response.isLinked:
            ...

    return decorator

def post(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to POST requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator

def put(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PUT requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator

def delete(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to DELETE requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator

def patch(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PATCH requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator

def options(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to OPTIONS requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator
    
def head(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to HEAD requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator
    
def trace(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to TRACE requests.
    Args:
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        ...
    return decorator

