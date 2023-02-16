
"""Example project structure:
```
./Main Folder
    /server.py
    /pages
        .html
        .css
        .js
        /subfolder
            .html
            ...
    /errors
        /404
            .html
            .css
            .js
        ...
```
In order to access /, the server will look for ./pages/.html. Smiliar thing for /subfolder, it will look for ./pages/subfolder/.html.

You can customize error pages 
"""

__dev_version__ = "0.0.3"


# TODO: Add a `-m` script that automatically creates a base directory.
# ^ either that or serve pre-defined responses from hardcoded text

# TODO: Add configure error pages to include f"https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{code}"
# for errors in the 4XX-5XX range.


from http.server import HTTPServer, BaseHTTPRequestHandler
from .content_types import detect_content_type
from .communications import Route, RouteExistsError, Request, Response

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
    responses:dict[str,dict[str,]] = { # I spent 30m trying to debug this because this was originally set to `routes.copy()`. im never using `.copy()` again.
        "get": {},
        "post": {},
        "put": {},
        "delete": {},
        "patch": {},
        "options": {},
        "head": {},
        "trace": {}
    }
    page_dir:str
    error_dir:str

    def respond_file(self,code:int,filename:str) -> None:
        """Responds to the client with a file. The filename (filepath) must be relative to the root directory of the server.

        Args:
            `code (int)`: The HTTP status code to respond with.
            `filename (str)`: The file to respond with.
        """
        self.send_response(code)
        self.send_header("Content-type", content_types.detect_content_type(filename))
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
        try:
            #for route_path in self.routes["get"]:
            #    if route_path == self.path:
            #        route = self.routes["get"][route_path]
            #        self.respond_file(200,self.resolve_path("get",route.full_path))
            #        return
            for func_path in self.responses["get"]:
                if func_path == self.path:
                    response:Response = self.responses["get"][func_path](Request(self),Response(self))
                    response.send()
                    return
            #else:
            #    self.respond_file(200,self.resolve_path("get",self.path))
        except Exception as e:
            self.respond(500, str(e), {"Content-type": "text/plain"})
            return
            
            
    def do_POST(self):
        """POST requests. Do not modify unless you know what you are doing.
        Use the `@server.post(path)` decorator instead."""

    def do_PUT(self):
        """PUT requests. Do not modify unless you know what you are doing.
        Use the `@server.put(path)` decorator instead."""

    def do_DELETE(self):
        """DELETE requests. Do not modify unless you know what you are doing.
        Use the `@server.delete(path)` decorator instead."""

    def do_PATCH(self):
        """PATCH requests. Do not modify unless you know what you are doing.
        Use the `@server.patch(path)` decorator instead."""

    def do_OPTIONS(self):
        """OPTIONS requests. Do not modify unless you know what you are doing.
        Use the `@server.options(path)` decorator instead."""

    def do_HEAD(self):
        """HEAD requests. Do not modify unless you know what you are doing.
        Use the `@server.head(path)` decorator instead."""

    def do_TRACE(self):
        """TRACE requests. Do not modify unless you know what you are doing.
        Use the `@server.trace(path)` decorator instead."""


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
        try:
            HTTPServer((self.host, self.port), self.handler).serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")
        except Exception as e:
            print(f"Server error: {e}")


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
        server.handler.responses["get"][path] = func
    return decorator

def post(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to POST requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["post"][path] = func
    return decorator

def put(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PUT requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["put"][path] = func
    return decorator

def delete(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to DELETE requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["delete"][path] = func
    return decorator

def patch(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PATCH requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["patch"][path] = func
    return decorator

def options(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to OPTIONS requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["options"][path] = func
    return decorator
    
def head(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to HEAD requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["head"][path] = func
    return decorator
    
def trace(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to TRACE requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        server.handler.responses["trace"][path] = func
    return decorator
