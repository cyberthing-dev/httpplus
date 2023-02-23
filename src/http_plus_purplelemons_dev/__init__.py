
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

__dev_version__ = "0.0.8"
__version__ = __dev_version__


# XTODO: Add configure error pages to include f"https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{code}"
# for errors in the 4XX-5XX range.
# TODO: Use http code cat for default errors instead of what's currently going on.

# TODO: Add a `@route` decorator that can be used to register a route.

# TODO: Add `debug=True` mode to decorators for routes and responses.

# TODO: Allow datatype checking in route and response uri (example below)
# @route("/example/:<var>:<type>")
# If the type is not specified, it will default to `str`. If the type is violated, it will return a 400 "expected <type> for <var>" error.
# Valid types should be str, bool, int, float, bin, and hex.

# TODO: Add HTML object for response bodies.
# HTML.body, .head, .render(**kwargs), etc.

# TODO: Add .match_route check to adding new routes, currently wildcard routes will conflict with other routes.

from http.server import HTTPServer, BaseHTTPRequestHandler
from .content_types import detect_content_type
from os.path import exists
from .communications import Route, RouteExistsError, Request, Response
from .static_responses import SEND_RESPONSE_CODE
from traceback import print_exception as print_exc

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
    server_version:str = f"http+/{__version__}"

    def error(self,code:int, *, message:str=None, headers:dict[str,str]=None) -> None:
        error_page_path = f"{self.error_dir}/{code}/.html"
        if exists(error_page_path):
            self.respond_file(code, error_page_path)
        else:
            self.respond(code,SEND_RESPONSE_CODE(code,message),headers)

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
        if len(path.split("/")) == len(route.split("/")):
            temp={}
            for path_part, route_part in zip(path.split("/"), route.split("/")):
                if route_part.startswith(":"):
                    temp[route_part[1:]] = path_part
                elif route_part == "*":
                    # TODO: Implement further wildcard matching
                    pass
                elif route_part != path_part:
                    break
            else:
                return True, temp
        return False, {}

    def do_GET(self):
        """GET requests. Do not modify unless you know what you are doing.
        Use the `@server.get(path)` decorator instead."""
        try:
            for route_path in self.routes["get"]:
                if route_path == self.path:
                    route = self.routes["get"][route_path]
                    #print(f"Given {self.path}, redirecting to {route.full_path}")
                    self.respond_file(200,self.resolve_path("get",route.full_path))
                    return
            for func_path in self.responses["get"]:
                matched, kwargs = self.match_route(self.path, func_path)
                if matched:
                    response:Response = self.responses["get"][func_path](Request(self, params=kwargs),Response(self))
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
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
                    response.send()
                    return
            else:
                self.error(404, message=self.path)
        except Exception as e:
            print_exc(e)
            self.respond(500, str(e), {"Content-type": "text/plain"})
            return


class Server:
    """
    Main class for the HTTP Plus server library.
    * Initialize the server with `server = Server(host, port)`.
    * Listen to HTTP methods with `@httpplus.server.<method>(server,path)`,
        for example `@httpplus.get("/")`.
    """

    def __init__(self, host:str="0.0.0.0", port:int=80, /, *, page_dir:str="./pages", error_dir="./errors", debug:bool=False, **kwargs):
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
            print(f"Listening on http://{self.host}:{self.port}")
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
