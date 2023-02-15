
from communication import *
from content_types import detect_content_type
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
    responses:dict[str,dict[str,Response]] = routes.copy()
    page_dir:str
    error_dir:str

    def respond_file(self,code:int,filename:str) -> None:
        """Responds to the client with a file. The filename (filepath) must be relative to the root directory of the server.

        Args:
            `code (int)`: The HTTP status code to respond with.
            `filename (str)`: The file to respond with.
        """
        self.send_response(code)
        self.send_header("Content-type", detect_content_type(filename))
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())
    
    def respond(self, code:int, message:str, headers:dict[str,str]) -> None:
        """Responds to the client with a message custom message. See `respond_file` for the prefered response method.

        Args:
            `code (int)`: The HTTP status code to respond with.
            `message (str)`: The message to respond with.
        """
        self.send_response(code)
        self.send_header("Content-type", headers["Content-type"])
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(message.encode())

    def resolve_path(self,method:str,path:str) -> str:
        """
        Returns the content at the path of a *local* url or file.
        For url redirection, use `Response.redirect`.
        """
        for route in self.routes[method]:
            if route == path:
                return self.routes[method][route].send_to
        return path

    def do_GET(self):
        """GET requests. Do not modify unless you know what you are doing.
        Use the `@server.get(path)` decorator instead."""
        for route_path in self.routes["get"]:
            if route_path == self.path:
                route = self.routes["get"][route_path]
                if route.isLinked:
                    self.respond_file(200,self.resolve_path("get",route.send_to))
                self.respond_file(200,self.resolve_path("get",self.path))
                return


class Server:
    """
    Main class for the HTTP Plus server library.
    * Initialize the server with `server = Server(host, port)`.
    * Listen to HTTP methods with `@httpplus.server.<method>(server,path)`,
        for example `@httpplus.server.get("/")`.
    """

    def __init__(self, host:str, port:int, *, page_dir:str="./pages/", error_dir="./errors/", debug:bool=False, **kwargs):
        """Initializes the server.
        Args:
            `host (str)`: The host to listen on.
            `port (int)`: The port to listen on.
            `page_dir (str)`: The directory to serve pages from.
            `error_dir (str)`: The directory to serve error pages from.
            `debug (bool)`: Whether or not to print debug messages.
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.handler = Handler
        self.handler.page_dir = page_dir
        self.handler.error_dir = error_dir

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
    """A decorator that adds a route to the server. Listens to all HTTP methods.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
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
        return func
    return decorator

def get(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to GET requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["get"][path] = response
    return decorator

def post(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to POST requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["post"][path] = response
    return decorator

def put(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PUT requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["put"][path] = response
    return decorator

def delete(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to DELETE requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["delete"][path] = response
    return decorator

def patch(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PATCH requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["patch"][path] = response
    return decorator

def options(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to OPTIONS requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["options"][path] = response
    return decorator
    
def head(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to HEAD requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["head"][path] = response
    return decorator
    
def trace(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to TRACE requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        response:Response = func()
        server.handler.responses["trace"][path] = response
    return decorator

