
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

__dev_version__ = "0.0.19"
__version__ = __dev_version__


from http.server import HTTPServer, BaseHTTPRequestHandler
from .content_types import detect_content_type
from os.path import exists
from .communications import Route, RouteExistsError, Request, Response, StreamResponse
from .static_responses import SEND_RESPONSE_CODE
from traceback import print_exception as print_exc, format_exc
from typing import Callable
from .auth import Auth
import os.path

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
            `code (int)`: The HTTP status code to respond with.
            `filename (str)`: The file to respond with.
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
            `code (int)`: The HTTP status code to respond with.
            `message (str)`: The message to respond with.
        """
        self.send_response(code)
        if headers:
            for header, value in headers.items():
                self.send_header(header, value)
        self.send_header("Content-type", "text/html")
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
            `path (str)`: The path from the request.
            `route (str)`: The route from the predefined route.
        Returns:
            `tuple[bool,dict[str,str]]`: A tuple containing a boolean value indicating whether the path
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

    @staticmethod
    def serve_filename(path:str) -> "str|None":
        """
        Returns the filename of a path. If the path is not a file, returns `None`.

        Args:
            `path (str)`: The requested uri path.
        Returns:
            `str|None`: The path to the desired file, or `None` if the file does not exist.
        """
        # Search for files in the form `pages/path/.html`
        target = f"pages{path}/.html"
        if not os.path.exists(target):
            # Search for files in the form `pages/path.html`
            target = f"pages{path}.html"
            if not os.path.exists(target):
                target = None

        return target

    def do_GET(self):
        """
        GET requests. Do not modify unless you know what you are doing.

        Use the `@server.get(path)` decorator instead.
        """
        try:
            # try looking for files to serve first
            filename = self.serve_filename(self.path)
            if filename is not None:
                self.respond_file(200, filename)
                return
            # try looking for routes to serve second
            for route_path in self.routes["get"]:
                if route_path == self.path:
                    route = self.routes["get"][route_path]
                    self.respond_file(200, self.resolve_path("get", route.full_path))
                    return
            # try functional responses 3rd
            for func_path in self.responses["get"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    # we execute the response function with the current request and response objects
                    response:Response = self.responses["get"][func_path](Request(self, params=kwargs), Response(self))
                    response()
                    return
            # try streams 4th
            for func_path in self.responses["stream"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    self.respond(200, "", {"Content-Type": "text/event-stream"})
                    for event in self.responses["stream"][func_path](Request(self, params=kwargs), StreamResponse(self)):
                        self.wfile.write(event.to_bytes())
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


    def do_POST(self):
        """
        POST requests. Do not modify unless you know what you are doing.

        Use the `@server.post(path)` decorator instead.
        """
        try:
            for route_path in self.routes["post"]:
                if route_path == self.path:
                    route = self.routes["post"][route_path]
                    self.respond_file(200, self.resolve_path("post",route.full_path))
                    return
            for func_path in self.responses["post"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["post"][func_path](Request(self, params=kwargs), Response(self))
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

    def do_PUT(self):
        """
        PUT requests. Do not modify unless you know what you are doing.

        Use the `@server.put(path)` decorator instead.
        """
        try:
            for route_path in self.routes["put"]:
                if route_path == self.path:
                    route = self.routes["put"][route_path]
                    self.respond_file(200, self.resolve_path("put", route.full_path))
                    return
            for func_path in self.responses["put"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["put"][func_path](Request(self, params=kwargs), Response(self))
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

    def do_DELETE(self):
        """
        DELETE requests. Do not modify unless you know what you are doing.

        Use the `@server.delete(path)` decorator instead.
        """
        try:
            for route_path in self.routes["delete"]:
                if route_path == self.path:
                    route = self.routes["delete"][route_path]
                    self.respond_file(200, self.resolve_path("delete", route.full_path))
                    return
            for func_path in self.responses["delete"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["delete"][func_path](Request(self, params=kwargs), Response(self))
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

    def do_PATCH(self):
        """
        PATCH requests. Do not modify unless you know what you are doing.

        Use the `@server.patch(path)` decorator instead.
        """
        try:
            for route_path in self.routes["patch"]:
                if route_path == self.path:
                    route = self.routes["patch"][route_path]
                    self.respond_file(200, self.resolve_path("patch", route.full_path))
                    return
            for func_path in self.responses["patch"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["patch"][func_path](Request(self, params=kwargs), Response(self))
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

    def do_OPTIONS(self):
        """
        OPTIONS requests. Do not modify unless you know what you are doing.

        Use the `@server.options(path)` decorator instead.
        """
        try:
            for route_path in self.routes["options"]:
                if route_path == self.path:
                    route = self.routes["options"][route_path]
                    self.respond_file(200, self.resolve_path("options", route.full_path))
                    return
            for func_path in self.responses["options"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["options"][func_path](Request(self, params=kwargs), Response(self))
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

    def do_HEAD(self):
        """
        HEAD requests. Do not modify unless you know what you are doing.

        Use the `@server.head(path)` decorator instead.
        """
        try:
            for route_path in self.routes["head"]:
                if route_path == self.path:
                    route = self.routes["head"][route_path]
                    self.respond_file(200, self.resolve_path("head", route.full_path))
                    return
            for func_path in self.responses["head"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["head"][func_path](Request(self, params=kwargs), Response(self))
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

    def do_TRACE(self):
        """
        TRACE requests. Do not modify unless you know what you are doing.

        Use the `@server.trace(path)` decorator instead.
        """
        try:
            for route_path in self.routes["trace"]:
                if route_path == self.path:
                    route = self.routes["trace"][route_path]
                    self.respond_file(200, self.resolve_path("trace", route.full_path))
                    return
            for func_path in self.responses["trace"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["trace"][func_path](Request(self, params=kwargs), Response(self))
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
            `page_dir (str)`: The directory to serve pages from.

            `error_dir (str)`: The directory to serve error pages from.

            `debug (bool)`: Whether or not to print debug messages.
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
            `port (int)`: The port to listen on. Must be available, otherwise the server will raise a binding error.

            `ip (str)`: String in the form of an IP address to listen on. Must be an address on the current machine.
        """
        if self.debug:
            print(f"Listening on http://{self.ip}{':'+str(self.port) if self.port != 80 else ''}/")
            if ip is None:
                # Debug and no IP specified, use loopback
                ip = "127.0.0.1"
        elif ip is None:
            # No debug and no IP specified, use all interfaces
            ip = "0.0.0.0"
        try:
            HTTPServer((ip,port), self.handler).serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        except Exception as e:
            print(f"Server error: {e}")

    def all(self, path:str):
        """
        A decorator that adds a route to the server. Listens to all HTTP methods.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            for method in (self.get, self.post, self.put, self.delete, self.options, self.head, self.trace):
                try:
                    method(path)(func)
                except KeyError:
                    raise RouteExistsError(path)
        return decorator

    def stream(self, path:str):
        """
        A decorator that adds a route to the server. Listens *ONLY* to GET requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["stream"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def get(self, path:str):
        """
        A decorator that adds a route to the server. Listens to GET requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                # not sure what this does or why none of the other methods do it
                # just gonna leave it here tho ¯\_(ツ)_/¯
                if any(Handler.match_route(route, path) for route in self.handler.routes["get"]):
                    raise RouteExistsError(path)
                self.handler.responses["get"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def post(self, path:str):
        """
        A decorator that adds a route to the server. Listens to POST requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["post"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def put(self, path:str):
        """
        A decorator that adds a route to the server. Listens to PUT requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["put"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def delete(self, path:str):
        """
        A decorator that adds a route to the server. Listens to DELETE requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["delete"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def patch(self, path:str):
        """
        A decorator that adds a route to the server. Listens to PATCH requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["patch"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def options(self, path:str):
        """
        A decorator that adds a route to the server. Listens to OPTIONS requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["options"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def head(self, path:str):
        """
        A decorator that adds a route to the server. Listens to HEAD requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["head"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator

    def trace(self, path:str):
        """
        A decorator that adds a route to the server. Listens to TRACE requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).

        Args:
            `path (str)`: The path to respond to.
        """
        def decorator(func):
            try:
                self.handler.responses["trace"][path] = func
            except KeyError:
                raise RouteExistsError(path)
        return decorator


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
