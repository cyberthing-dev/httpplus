
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

__dev_version__ = "0.0.13"
__version__ = __dev_version__


# TODO: Native GraphQL support.

# TODO: Authentication support.
""" Example:
auth = http_plus.Auth()

@http_plus.get(server, "/home")
def _(req:http_plus.Request, res:http_plus.Response):
    token = req.authorization
    if not auth.check(token):
        return res.set_body("Invalid token", code=401)
    return res.set_body(f"Hello, {auth[token].username}! You have {auth[token].data} data.")

@http_plus.post(server, "/login")
def _(req:http_plus.Request, res:http_plus.Response):
    # ...
    # ... ensure username and password are correct...
    # ...
    token = auth.generate(
        username=req.json["username"],
        data=req.json["data"]
    )
    # auth.generate returns a string, which is the token. it also stores information given to it
    return res.set_body("Login page", code=401)
"""

# TODO: use functools.wraps to preserve function names and docstrings as well as get rid of the need to pass `server` into decorators.

# TODO: Add HTML object for response bodies. (see integration with brython)
# HTML.body, .head, .render(**kwargs), etc.

# TODO: Add .match_route check to adding new routes, currently wildcard routes will conflict with other routes.

# TODO: SEND_RESPONSE_CODE to accept `debug:bool` (maybe `traceback:bool`?) to know whether to print the traceback or not.

# TODO: SEND_RESPONSE_CODE to send error code and title in <h1> and other info in <p>.

# TODO: move TODOs to GitHub issues.

# TODO: `--log '<fmt>'` option for `python -m http_plus.server`
# Format options can include !time, !date, !method, !path, !code, !ip, !proto, !headers, !body
# Default format: [!time] [!ip] - "!method !path !proto" !code+

# TODO: Integrate with brython!

from http.server import HTTPServer, BaseHTTPRequestHandler
from .content_types import detect_content_type
from os.path import exists
from .communications import Route, RouteExistsError, Request, Response, StreamResponse
from .static_responses import SEND_RESPONSE_CODE
from traceback import print_exception as print_exc
from typing import Callable
from .auth import Auth

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
    responses:dict[str,dict[str,Callable]] = { # I spent 30m trying to debug this because this was originally set to `routes.copy()`. im never using `.copy()` again.
        "get": {},
        "post": {},
        "put": {},
        "delete": {},
        "patch": {},
        "options": {},
        "head": {},
        "trace": {},
        # note: stream is not a valid HTTP method, but it is used for streaming responses.
        "stream": {}
    }
    page_dir:str
    error_dir:str
    server_version:str = f"http+/{__version__}"

    def error(self,code:int, *, message:str=None, headers:dict[str,str]=None, **kwargs) -> None:
        error_page_path = f"{self.error_dir}/{code}/.html"
        if exists(error_page_path):
            self.respond_file(code, error_page_path)
        else:
            print(f"Error {code} occured, but no error page was found at {error_page_path}.")
            self.respond(code,SEND_RESPONSE_CODE(code,message,**kwargs),headers)

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
        if headers:
            for header, value in headers.items():
                self.send_header(header, value)
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
                        # Fancy way of converting
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

    def do_GET(self):
        """GET requests. Do not modify unless you know what you are doing.
        Use the `@server.get(path)` decorator instead."""
        try:
            # try files first
            for route_path in self.routes["get"]:
                if route_path == self.path:
                    route = self.routes["get"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("get",route.full_path))
                    return
            # try functional responses 2nd
            for func_path in self.responses["get"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["get"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            # try streams 3rd
            for func_path in self.responses["stream"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    self.respond(200, "", {"Content-Type": "text/event-stream"})
                    for event in self.responses["stream"][func_path](Request(self, params=kwargs),StreamResponse(self)):
                        self.wfile.write(event.to_bytes())
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return


    def do_POST(self):
        """POST requests. Do not modify unless you know what you are doing.
        Use the `@server.post(path)` decorator instead."""
        try:
            for route_path in self.routes["post"]:
                if route_path == self.path:
                    route = self.routes["post"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("post",route.full_path))
                    return
            for func_path in self.responses["post"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["post"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return

    def do_PUT(self):
        """PUT requests. Do not modify unless you know what you are doing.
        Use the `@server.put(path)` decorator instead."""
        try:
            for route_path in self.routes["put"]:
                if route_path == self.path:
                    route = self.routes["put"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("put",route.full_path))
                    return
            for func_path in self.responses["put"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["put"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return

    def do_DELETE(self):
        """DELETE requests. Do not modify unless you know what you are doing.
        Use the `@server.delete(path)` decorator instead."""
        try:
            for route_path in self.routes["delete"]:
                if route_path == self.path:
                    route = self.routes["delete"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("delete",route.full_path))
                    return
            for func_path in self.responses["delete"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["delete"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return

    def do_PATCH(self):
        """PATCH requests. Do not modify unless you know what you are doing.
        Use the `@server.patch(path)` decorator instead."""
        try:
            for route_path in self.routes["patch"]:
                if route_path == self.path:
                    route = self.routes["patch"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("patch",route.full_path))
                    return
            for func_path in self.responses["patch"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["patch"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return

    def do_OPTIONS(self):
        """OPTIONS requests. Do not modify unless you know what you are doing.
        Use the `@server.options(path)` decorator instead."""
        try:
            for route_path in self.routes["options"]:
                if route_path == self.path:
                    route = self.routes["options"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("options",route.full_path))
                    return
            for func_path in self.responses["options"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["options"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return

    def do_HEAD(self):
        """HEAD requests. Do not modify unless you know what you are doing.
        Use the `@server.head(path)` decorator instead."""
        try:
            for route_path in self.routes["head"]:
                if route_path == self.path:
                    route = self.routes["head"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("head",route.full_path))
                    return
            for func_path in self.responses["head"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["head"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=self.path, exception=e)
            return

    def do_TRACE(self):
        """TRACE requests. Do not modify unless you know what you are doing.
        Use the `@server.trace(path)` decorator instead."""
        try:
            for route_path in self.routes["trace"]:
                if route_path == self.path:
                    route = self.routes["trace"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("trace",route.full_path))
                    return
            for func_path in self.responses["trace"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["trace"][func_path](Request(self, params=kwargs),Response(self))
                    response()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.error(500, message=str(e))
            return


class Server:
    """
    Main class for the HTTP Plus server library.
    * Initialize the server with `server = Server(host, port)`.
    * Listen to HTTP methods with `@httpplus.server.<method>(server,path)`,
        for example `@http_plus.get("/")`.
    """

    def __init__(self, host:str="127.0.0.1", port:int=8080, /, *, page_dir:str="./pages", error_dir="./errors", debug:bool=False, **kwargs):
        """Initializes the server.
        Args:
            `host (str)`: The host to listen on. Defaults to all interfaces.
            `port (int)`: The port to listen on. Defaults to 80.
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
        """Starts the server, a blocking loop on the current thread."""
        if self.debug:
            print(f"Listening on http://{self.host}{':'+str(self.port) if self.port != 80 else ''}/")
        try:
            HTTPServer((self.host, self.port), self.handler).serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")
        except Exception as e:
            print(f"Server error: {e}")


    def base(self, request: Request, response: Response, **kwargs) -> Response:
        """The base function for all routes.
        Args:
            `request (Request)`: The request object.
            `response (Response)`: The response object.
            `**kwargs`: Arguments passed in by the route (e.g. `@server.get("/product/:id")` passes in `{"id": "..."}`).
        """
        return response


def init():
    """Initializes the current directory for HTTP+"""
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

@http_plus.get(server,"/")
def _(req:http_plus.Request, res:http_plus.Response):
    res.set_header("Content-type", "text/html")
    return res.set_body("<h2>Hello, world!</h2>")

server.listen()
""", file=f)

### DECORATORS == boilerplate :( ###
def all(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to all HTTP methods.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        for method in (get, post, put, delete, options, head, trace):
            try:
                method(server, path)(func)
            except KeyError:
                raise RouteExistsError(path)
    return decorator

def stream(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to all HTTP methods.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["stream"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator

def get(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to GET requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["get"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator

def post(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to POST requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["post"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator

def put(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PUT requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["put"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator

def delete(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to DELETE requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["delete"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator

def patch(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to PATCH requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["patch"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator

def options(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to OPTIONS requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["options"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator
    
def head(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to HEAD requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["head"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator
    
def trace(server:Server, path:str):
    """A decorator that adds a route to the server. Listens to TRACE requests.
    
    Args:
        `server (Server)`: You must declare the HTTP Plus server
            and specify it in method decorators.
        `path (str)`: The path to respond to.
    """
    def decorator(func):
        try:
            server.handler.responses["trace"][path] = func
        except KeyError:
            raise RouteExistsError(path)
    return decorator
