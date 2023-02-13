
from communication import *
from content_types import detect_content_type, TYPES
from http_plus_purplelemons_dev.static_responses import SEND_RESPONSE_CODE


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        """Initializes the request handler."""
        self.extension_auto_search = list(TYPES.keys())
        super().__init__(request, client_address, server)

    def respond(self, code:int, message:str, content_type:str="text/plain", headers:dict[str,str]={}) -> None:
        """Responds to the client with a message custom message. See `respond_file` for the prefered response method.

        Args:
            `code (int)`: The HTTP status code to respond with.
            `message (str)`: The message to respond with.
        """
        self.send_response(code)
        self.send_header("Content-type", content_type)
        for header, value in headers.items():
            self.send_header(header, value)
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
        if request_path in [i.request_from for i in self.routes] and not override:
            raise RouteExistsError(request_path)
        self.routes.append(Route(request_path, directory, "pages"))


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
        try:
            route = self.resolve_route(self.path)
            if route:
                self.respond_file(200, route)
                return
            if not self.path.endswith("/"):
                self.path += "/"
            for extension in self.extension_auto_search:
                try:
                    self.respond_file(200, self.pages_dir[:-1] + self.path + extension)
                    return
                except FileNotFoundError:
                    pass
            else:
                try:
                    self.respond_file(404, self.errors_dir + "404/.html")
                except FileNotFoundError:
                    self.respond(404, SEND_RESPONSE_CODE(404,self.path), content_type="text/html")
        except Exception as e:
            print(e)
            self.respond(500, SEND_RESPONSE_CODE(500), content_type="text/html")
