
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

__version__ = "0.1.1"
NAME = "http_plus_purplelemons_dev"

from http.server import HTTPServer
from typing import Callable
from .auth import Auth
from .handler import Handler
from .communications import RouteExistsError, Request, Response, GQLResponse, StreamResponse

class Server:
    """
    Main class for the HTTP Plus server library.
    * Initialize the server with `server = Server(host, port)`.
    * Listen to HTTP methods with `@server.<method>(path)`,
        for example `@server.get("/")`.
    """

    def __init__(self, /, *, brython:bool=True, page_dir:str="./pages", error_dir="./errors", debug:bool=False, **kwargs):
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
        self.handler.brython = brython
        self.handler.page_dir = page_dir[:-1] if page_dir.endswith("/") else page_dir
        self.handler.error_dir = error_dir[:-1] if error_dir.endswith("/") else error_dir

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

    def gql(self, schema:str, endpoint:str="/api/graphql"):
        """
        A decorator that adds a route to the server. Listens *ONLY* to GET requests.

        If you use a keyword wildcard in the route url, arguments will be passed into
        the function via **kwargs (e.g. `@server.gql("/product/:id")` passes in `{"id": "..."}`).

        Args:
            endpoint (str): The endpoint that the server will listen on.
        """
        def decorator(func:Callable):
            try:
                self.handler.gql_endpoints[endpoint] = func
                self.handler.gql_schemas[endpoint] = schema
            except KeyError:
                raise RouteExistsError(endpoint)
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
