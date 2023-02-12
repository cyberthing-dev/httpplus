
from communication import *
from http.server import BaseHTTPRequestHandler, HTTPServer


class RouteExistsError(Exception):
    """Raised when a route already exists."""
    def __init__(self, route:str=None):
        super().__init__(f"Route {route} already exists." if message else "Route already exists.")

class Handler(BaseHTTPRequestHandler):
    """
    A proprietary HTTP request handler for the server.
    It is highly suggested that you have a good understanding of
        http.server and httpplus before modifying or substituting this class.
    """

    def __init__(self, request, client_address, server):
        """Initializes the request handler."""
        self.routes:dict[str,Route]
        super().__init__(request, client_address, server)


class Server:

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

    def base(self, request: Request, Response: Response) -> Response:
        """The base function for all routes.
        Args:
            `request (Request)`: The request object.
            `response (Response)`: The response object.
        """

    ### DECORATORS == boilerplate :( ###
    def all(path:str) -> function:
        """A decorator that adds a route to the server. Listens to all HTTP methods.
        Args:
            `path (str)`: The path to respond to.
        """
        # This code is very clever if i do say so myself
        @Server.get(path)
        @Server.post(path)
        @Server.put(path)
        @Server.delete(path)
        @Server.patch(path)
        @Server.options(path)
        @Server.head(path)
        @Server.trace(path)
        def decorator(func:function):
            ...
        return decorator

    def get(path:str) -> function:
        """A decorator that adds a route to the server. Listens to GET requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            response:Response = func()
            

        return decorator

    def post(path:str) -> function:
        """A decorator that adds a route to the server. Listens to POST requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator

    def put(path:str) -> function:
        """A decorator that adds a route to the server. Listens to PUT requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator

    def delete(path:str) -> function:
        """A decorator that adds a route to the server. Listens to DELETE requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator

    def patch(path:str) -> function:
        """A decorator that adds a route to the server. Listens to PATCH requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator

    def options(path:str) -> function:
        """A decorator that adds a route to the server. Listens to OPTIONS requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator
    
    def head(path:str) -> function:
        """A decorator that adds a route to the server. Listens to HEAD requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator
    
    def trace(path:str) -> function:
        """A decorator that adds a route to the server. Listens to TRACE requests.
        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func:function):
            ...
        return decorator

