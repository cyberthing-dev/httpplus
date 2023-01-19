
from http.server import BaseHTTPRequestHandler, HTTPServer
from content_types import detect_content_type
from dataclasses import dataclass

@dataclass
class Route:
    """Custom dataclass for optimizing route creation, readability, and resolution.

    Attributes:
        `request_from (str)`: The path to respond to.
        `send_to (str)`: The directory to respond with in the form of `./path/to/directory/`.
        `route_type (str)`: The type of route. Can be either `pages` or `errors`.
    """
    request_from:str
    send_to:str
    route_type:str

class RouteExistsError(Exception):
    """Raised when a route already exists."""
    pass

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        """Initializes the request handler."""
        self.routes:dict[str,str] = {
            "/": "./pages/",
            "/notfound": "./errors/404/"
        }
        self.extension_auto_search = [
            "html",
            "css",
            "js"
        ]
        self.errors_dir = "./errors/"
        self.pages_dir = "./pages/"
        super().__init__(request, client_address, server)

    def respond(self, code:int, message:str, content_type:str="text/plain") -> None:
        """Responds to the client with a message custom message. See `respond_file` for the prefered response method.

        Args:
            `code (int)`: The HTTP status code to respond with.
            `message (str)`: The message to respond with.
        """
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(message.encode())

    def respond_file(self, code:int, filename:str) -> None:
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

    def route(self, request_path:str, directory:str, override:bool=False) -> None:
        """Adds a route to the server.

        Args:
            `request_path (str)`: The path to respond to.
            `directory (str)`: The directory to respond with in the form of `./path/to/directory/`.
            `override (bool)`: Whether or not to override the route if it already exists. Raises RouteExistsError if the route already exists and `override` is False.
        """
        if request_path in self.routes and not override:
            raise RouteExistsError(f"Route {request_path} already exists.")
        self.routes[request_path] = directory

    def add_extension(self,extension:str):
        """Adds an extension to the list of extensions to search for when some path containing a file extension is requested.

        Args:
            `extension (str)`: The extension to add.
        """
        self.extension_auto_search.append(extension)

    def remove_extension(self,extension:str):
        """Removes an extension from the list of extensions to search for when some path containing a file extension is requested.

        Args:
            `extension (str)`: The extension to remove.
        """
        self.extension_auto_search.remove(extension)

    def do_GET(self) -> None:
        """Handles GET requests."""
        # path is the first part of the request, extension is everythign after the last `.`
        path, extension = ".".join(self.path.split(".")[:-1]), self.path.split(".")[-1]
        if self.path in self.routes:
            self.respond_file(200, self.routes[self.path] + ".html")
        else:
            try:
                self.respond_file(404, self.routes["/error"] + "404/.html")
            except FileNotFoundError:
                self.respond(404, "")
