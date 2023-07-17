
"""
## Example project structure:
```txt
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
In order to access the url `/`, the server will look for `./pages/.html`.
Smiliarly, requests to `/subfolder` will look for `./pages/subfolder/.html`.

You can customize error pages by creating a folder in `./errors` with the name of the error code.
"""

__dev_version__ = "0.0.24"
__version__ = __dev_version__
NAME = "http_plus_purplelemons_dev"


from http.server import HTTPServer, BaseHTTPRequestHandler
from .content_types import detect_content_type
from os.path import exists
from .communications import Route, RouteExistsError, Request, Response, StreamResponse
from .static_responses import SEND_RESPONSE_CODE
from traceback import print_exception as print_exc, format_exc
from typing import Callable
from .auth import Auth
import os.path
import datetime

class Handler(BaseHTTPRequestHandler):
    """
    A proprietary HTTP request handler for the server.
    It is highly suggested that you have a good understanding of
    `http.server` and httpplus before modifying or substituting this class.
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
    # I spent 30m trying to debug this because this was originally set to `routes.copy()`. im never using `.copy()` again.
    responses:dict[str,dict[str,Callable]] = {
        "get": {},
        "post": {},
        "put": {},
        "delete": {},
        "patch": {},
        "options": {},
        "head": {},
        "trace": {},
        # note: stream is not a valid HTTP method, but it is used for streaming responses.
        # see `.communications.StreamResponse`
        "stream": {}
    }
    page_dir:str
    error_dir:str
    debug:bool
    server_version:str = f"http+/{__version__}"
    protocol_version:str = "HTTP/1.1"
    status:int

    @property
    def ip(self):
        return self.client_address[0]
    
    @property
    def port(self):
        return self.client_address[1]
    
    @property
    def method(self):
        return self.command
    
    @property
    def proto(self):
        return self.protocol_version

    def custom_logger(self):
        "Override this"
        pass

    def log_message(self, fmt:str, *args) -> None:
        """
        Do not override. Use `@server.log`.
        """
        self.status = int(args[1])
        # bit of a hacky way of checking if the user has overriden the custom logger
        if self.custom_logger.__doc__ == "Override this":
            return super().log_message(fmt, *args)
        else:
            return self.custom_logger()

    def error(self, code:int, *, message:str=None, headers:dict[str,str]=None, traceback:str="", **kwargs) -> None:
        error_page_path = f"{self.error_dir}/{code}/.html"
        if exists(error_page_path):
            self.respond_file(code, error_page_path)
        else:
            self.respond(
                code = code,
                headers = headers,
                message = SEND_RESPONSE_CODE(
                    code = code,
                    path = message,
                    traceback = traceback,
                    **kwargs
                )
            )
            if self.debug: 
                print(f"Error {code} occured, but no error page was found at {error_page_path}.")

    def respond_file(self,code:int,filename:str) -> None:
        """
        Responds to the client with a file.
        The filename (filepath) must be relative to the root directory of the server.

        Args:
            code (int): The HTTP status code to respond with.
            filename (str): The file to respond with.
        """
        self.send_response(code)
        self.send_header("Content-type", detect_content_type(filename))
        with open(filename, "rb") as f:
            self.send_header("Content-length", os.path.getsize(filename))
            self.end_headers()
            self.wfile.write(f.read())

    def respond(self, code:int, message:str, headers:dict[str,str]) -> None:
        """Responds to the client with a message custom message. See `respond_file` for the prefered response method.

        Args:
            code (int): The HTTP status code to respond with.
            message (str): The message to respond with.
        """
        self.send_response(code)
        if headers:
            for header, value in headers.items():
                self.send_header(header, value)
        if "Content-type" not in self.headers:
            self.send_header("Content-type", "text/html")
        if "Content-length" not in self.headers and message:
            self.send_header("Content-length", len(message))
        self.end_headers()
        if message:
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

    @staticmethod
    def match_route(path:str, route:str) -> tuple[bool,dict[str,str]]:
        """Checks if a given `path` from a request matches a given `route` from a predefined route.

        Args:
            path (str): The path from the request.
            route (str): The route from the predefined route.
        Returns:
            tuple[bool,dict[str,str]]: A tuple containing a boolean value indicating whether the path
            matches the route, and a dictionary containing the keyword variables from the route.
        """
        if len(path.split("/")) == len(route.split("/")):
            kwargs={}
            for path_part, route_part in zip(path.split("/"), route.split("/")):
                if route_part.startswith(":"):
                    # Check if the route part specifies a type
                    split = route_part.split(":")[1:]
                    # standard route syntax validation

                    if len(split) == 2:
                        route_part, type_ = split
                    elif len(split) == 1:
                        route_part, type_ = route_part[1:], "str"
                    else:
                        raise ValueError("Invalid route syntax.")

                    try:
                        # Fancy way of converting the type string to a type
                        kwargs[route_part[1:]] = {
                            "int": int,
                            "float": float,
                            "str": str,
                            "bool": bool
                        }[type_]
                    except (KeyError,ValueError):
                        raise ValueError(f"Invalid type {type_}.")
                    # The route part does not specify a type, default to `str`
                    kwargs[route_part] = path_part
                elif route_part == "*":
                    # TODO: Implement further wildcard matching
                    pass
                elif route_part != path_part:
                    break
            else:
                return True, kwargs
        return False, {}

    def serve_filename(self, path:str, target_ext:str="html") -> "str|None":
        """
        Returns the filename of a path. If the path is not a file, returns `None`.

        Args:
            path (str): The requested uri path.
            target_ext (str, optional): The extension of the file to search for. Defaults to "html". Can be html, css, or js.
        Returns:
            str|None: The path to the desired file, or `None` if the file does not exist.
        """
        # Search for files in the form `pages/path/.ext`
        target = f"{self.page_dir}{path}/.{target_ext}"
        if not os.path.exists(target):
            # Search for files in the form `pages/path.ext`
            target = f"{self.page_dir}{path}.{target_ext}"
            if not os.path.exists(target):
                # if all else fails, index is poggers
                target = f"{self.page_dir}/index.{target_ext}"
                if not os.path.exists(target):
                    target = None
        return target

    @staticmethod
    def _make_method(http_method:Callable):
        """
        Wrapper for creating `do_<METHOD>` methods.
        """
        method_name = http_method.__name__[3:].lower()
        def method(self:"Handler"):
            try:
                # streams
                if self.headers.get("Accept") == "text/event-stream":
                    for func_path in self.responses["stream"]:
                        matched, kwargs = self.match_route(self.path, func_path)
                        if matched:
                            self.send_response(200)
                            self.send_header("Content-Type", "text/event-stream")
                            self.send_header("Cache-Control", "no-cache")
                            self.send_header("Connection", "keep-alive")
                            self.end_headers()
                            for event in self.responses["stream"][func_path](Request(self, params=kwargs), StreamResponse(self)):
                                self.wfile.write(event.to_bytes())
                            return
                if method_name == "get":
                    path = self.path
                    if "." in path.split("/")[-1]:
                        extension = path.split("/")[-1].split(".")[-1].lower()
                        # everything up to the .
                        path = path[:-len(extension)-1]
                    else:
                        # otherwise, assume html
                        extension = "html"
                    if extension in ["html", "css", "js"]:
                        filename = self.serve_filename(path, extension)
                        if filename is not None:
                            self.respond_file(200, filename)
                            return

                for route_path in self.routes[method_name]:
                    if route_path == self.path:
                        route = self.routes[method_name][route_path]
                        self.respond_file(200, self.resolve_path(method_name, route.full_path))
                        return
                for func_path in self.responses[method_name]:
                    matched, kwargs = self.match_route(self.path, func_path)
                    if matched:
                        response:Response = self.responses[method_name][func_path](Request(self, params=kwargs), Response(self))
                        response()
                        return
                else:
                    self.error(404, message=self.path)
            except Exception as e:
                if self.debug:
                    print_exc(e)
                self.error(
                    code = 500,
                    message = str(e),
                    traceback = format_exc() if self.debug else ""
                )
                return
        return method

    # it's condensed now! :D
    @_make_method
    def do_GET(self): return
    @_make_method
    def do_POST(self): return
    @_make_method
    def do_PUT(self): return
    @_make_method
    def do_DELETE(self): return
    @_make_method
    def do_PATCH(self): return
    @_make_method
    def do_OPTIONS(self): return
    @_make_method
    def do_HEAD(self): return
    @_make_method
    def do_TRACE(self): return

class Server:
    """
    Main class for the HTTP Plus server library.
    * Initialize the server with `server = Server(host, port)`.
    * Listen to HTTP methods with `@server.<method>(path)`,
        for example `@server.get("/")`.
    """

    def __init__(self, /, *, page_dir:str="./pages", error_dir="./errors", debug:bool=False, **kwargs):
        """
        Listen to HTTP methods with `@server.<method>(path)`, for example...
        ```
        @server.get("/")
        def _(req, res):
            return res.send("Hello, world!")
        ```
        More about the `req` and `res` objects can be found in `http_plus.communications`.
        
        Args:
            page_dir (str): The directory to serve pages from.
            error_dir (str): The directory to serve error pages from.
            debug (bool): Whether or not to print debug messages.
        """
        self.debug = debug
        self.handler = Handler
        self.handler.debug = debug
        self.handler.page_dir = page_dir
        self.handler.error_dir = error_dir

    def listen(self, port:int, ip:str=None) -> None:
        """
        Starts the server, a blocking loop on the current thread.
        The IP will default to all interfaces (`0.0.0.0`) if not specified, unless if the
        server was initialized with `debug=True`, in which case it will default to loopback
        (`127.0.0.1`).

        Args:
            port (int): The port to listen on. Must be available, otherwise the server will raise a binding error.
            ip (str): String in the form of an IP address to listen on. Must be an address on the current machine.
        """
        if self.debug:
            if ip is None:
                # Debug and no IP specified, use loopback
                ip = "127.0.0.1"
            print(f"Listening on http://{ip}{':'+str(port) if port != 80 else ''}/")
        elif ip is None:
            # No debug and no IP specified, use all interfaces
            ip = "0.0.0.0"
        try:
            HTTPServer((ip,port), self.handler).serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        except Exception as e:
            print(f"Server error: {e}")

    @staticmethod
    def _make_method(server_wrapper:Callable):
        """
        Wrapper for wrapping `@server.<METHOD>` methods.
        """
        # can someone confirm if this is a 3rd order function?
        # if not, idk what this is and lord forgive me for my sins
        def method(self:"Server", path:str):
            def decorator(func:Callable):
                try:
                    self.handler.responses[server_wrapper.__name__][path] = func
                except KeyError:
                    raise RouteExistsError(path)
            return decorator
        return method
    
    def log(self, func:Callable):
        """
        A decorator that adds a custom logger to the server.
        Your logger function should take in a `Handler` object as its only argument.
        """
        self.handler.custom_logger = func

    def all(self, path:str, exclude:list[str]=[]):
        """
        A decorator that adds a route to the server. Listens to all HTTP methods.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """
        def decorator(func:Callable):
            funcs = [self.get, self.post, self.put, self.delete, self.patch, self.options, self.head, self.trace]
            if exclude:
                # by far one of my most clever lines of code
                funcs.remove(*exclude)
            for method in funcs:
                try:
                    method(path)(func)
                except KeyError:
                    raise RouteExistsError(path)
        return decorator

    @_make_method
    def stream(self, path:str):
        """
        A decorator that adds a route to the server. Listens *ONLY* to GET requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.stream("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def get(self, path:str):
        """
        A decorator that adds a route to the server. Listens to GET requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def post(self, path:str):
        """
        A decorator that adds a route to the server. Listens to POST requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.post("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def put(self, path:str):
        """
        A decorator that adds a route to the server. Listens to PUT requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.put("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def delete(self, path:str):
        """
        A decorator that adds a route to the server. Listens to DELETE requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.delete("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def patch(self, path:str):
        """
        A decorator that adds a route to the server. Listens to PATCH requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.patch("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def options(self, path:str):
        """
        A decorator that adds a route to the server. Listens to OPTIONS requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.options("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def head(self, path:str):
        """
        A decorator that adds a route to the server. Listens to HEAD requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.head("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """

    @_make_method
    def trace(self, path:str):
        """
        A decorator that adds a route to the server. Listens to TRACE requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.trace("/product/:id")` passes in `{"id": "..."}`).

        Args:
            path (str): The path to respond to.
        """


def init():
    """
    Initializes the current directory for HTTP+
    """
    import os
    if not os.path.exists("pages"):
        os.mkdir("pages")
    if not os.path.exists("errors"):
        os.mkdir("errors")
    if not os.path.exists("server.py"):
        with open("server.py", "w") as f:
            print("""
import http_plus

server = http_plus.Server()

@server.get("/")
def _(req:http_plus.Request, res:http_plus.Response):
    res.set_header("Content-type", "text/html")
    return res.set_body("<h2>Hello, world!</h2>")

server.listen()
""", file=f)
