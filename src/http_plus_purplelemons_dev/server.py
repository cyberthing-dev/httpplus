
from dataclasses import dataclass
from json import loads, dumps
from http.server import BaseHTTPRequestHandler, HTTPServer

class content_types:
    
    TYPES = {
        "json": "application/json",
        "txt": "text/plain",
        "html": "text/html",
        "css": "text/css",
        "js": "text/javascript",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "ico": "image/x-icon",
        "webp": "image/webp",
        "mp3": "audio/mpeg",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "ogg": "audio/ogg",
        "pdf": "application/pdf",
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "rar": "application/x-rar-compressed",
        "7z": "application/x-7z-compressed",
        "xml": "application/xml",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "eot": "application/vnd.ms-fontobject",
        "ttf": "font/ttf",
        "otf": "font/otf",
        "jsonld": "application/ld+json",
        "wasm": "application/wasm",
        "manifest": "application/manifest+json",
        "map": "application/json",
        "webmanifest": "application/manifest+json",
        "webapp": "application/manifest+json",
        "json5": "application/json5",
        "yaml": "application/yaml",
        "yml": "application/yaml",
        "toml": "application/toml",
        "md": "text/markdown",
        "markdown": "text/markdown",
        "mdx": "text/markdown",
        "mdown": "text/markdown",
        "mkd": "text/markdown",
        "mkdn": "text/markdown",
        "mkdown": "text/markdown",
        "ron": "application/ron",
        "ronn": "application/ron",
        "ron-rb": "application/ron",
        "ron-rs": "application/ron",
        "ronn-rb": "application/ron",
        "ronn-rs": "application/ron",
        "rs": "text/rust",
        "rb": "text/ruby",
        "py": "text/python",
        "pyc": "application/x-python-code"
    }

    def detect_content_type(filename:str) -> str:
        """Detects the content type of a file based on the file extension.

        Args:
            `filename (str)`: The name of the file to detect.

        Returns:
            `str`: The content type of the file.
        """
        try:
            return TYPES[filename.split(".")[-1]]
        except KeyError:
            return "application/octet-stream"


class RouteExistsError(Exception):
    """Raised when a route already exists."""
    def __init__(self, route:str=...):
        super().__init__(f"Route {route} already exists." if route else "Route already exists.")

@dataclass
class Route:
    """Custom dataclass for optimizing route creation, readability, and resolution.

    Attributes:
        `send_to (str)`: The directory to respond with in the form of `./path/to/directory/`, `path/to/file.ext`, etc..
        `route_type (str)`: The type of route. Can be either `pages`, `errors`, or `static`.
        `content (str)`: The content to respond with. Only used for `static` routes.
        `content_type (str)`: The content type to respond with. Only used for `static` routes.
    """
    send_to:str
    route_type:str

    @property
    def full_path(self) -> str:
        """Returns the full path to the file to respond with."""
        return f"./{self.route_type}{self.send_to}"

class Request:
    """
    Request object, passed into HTTP method listeners as the first argument.
    """
    def __init__(self, request:BaseHTTPRequestHandler):
        self.request = request
        self.path = request.path
        self.method = request.command
        self.headers = request.headers
        self.body = request.rfile.read(int(request.headers.get("Content-Length", 0)))
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

    @property
    def json(self) -> dict:
        return loads(self.body)

    @property
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
        self.body:str = ""
        self.status = 200
        self.isLinked = False
        self._route: Route

    def set_header(self, header:str, value:str) -> "Response":
        self.headers[header] = value
        return self

    def set_body(self, body:bytes|str|dict) -> "Response":
        """
        Automatically pareses the body into bytes, and sets the Content-Type header to application/json if the body is a dict.
        Will be overwritten if `Response

        Args:
            `body (bytes|str|dict)`: The body of the response.
        """
        if isinstance(body, dict):
            self.set_header("Content-Type", "application/json")
            self.body = dumps(body)
        elif isinstance(body, bytes):
            self.body = body.decode()
        else:
            self.body = body
        print(f"set body to {self.body}")
        return self

    def route(self,path_to:str,link:bool=False) -> "Response":
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
            self.isLinked = True
        else:
            self._route = Route(path_to, "pages")
        return self


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
    responses:dict[str,dict[str,]] = routes.copy()
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
        #self.send_header("Content-type", headers["Content-type"])
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
            print(self.path, self.responses, self.routes)
            for func_path in self.responses["get"]:
                if func_path == self.path:
                    response:Response = self.responses["get"][func_path](Request(self),Response(self))
                    
                    return
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


if __name__=="__main__":
    server = Server("localhost", 8080, debug=True)
    @all(server, "/")
    def _(req:Request, res:Response):
        return res.set_body("Hello, world!")
    server.listen()
