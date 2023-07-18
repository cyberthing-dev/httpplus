from http.server import BaseHTTPRequestHandler
from typing import Callable
from os.path import exists
import os
from traceback import print_exception as print_exc, format_exc
from . import __version__
from .communications import Route, GQLResponse, Response, StreamResponse, Request
from .static_responses import SEND_RESPONSE_CODE
from .content_types import detect_content_type
import json

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
        "stream": {},
        # Again, not an HTTP method. Used for GraphQL.
        "gql": {}
    }
    page_dir:str
    error_dir:str
    debug:bool
    server_version:str = f"http+/{__version__}"
    protocol_version:str = "HTTP/1.1"
    status:int
    brython:bool
    gql_endpoints:dict[str,Callable[...,GQLResponse]] = {}
    "Endpoint to GQL resolver mappings"
    gql_schemas:dict[str,str] = {}
    "Endpoint to GQL schema mappings"

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
            # Getting body:
            length = int(self.headers.get("Content-Length", 0))
            self.body = ""
            if length:
                self.body = self.rfile.read(length).decode()
            # Setting up json
            self.json = {}
            if self.headers.get("Content-Type") == "application/json":
                self.json = json.loads(self.body)

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
                
                # GQL
                if self.path in self.gql_endpoints:
                    self.gql_endpoints[self.path](Request(self, params={}), GQLResponse(self))()
                    return

                # file serve
                if method_name == "get":
                    path = self.path
                    if "." in path.split("/")[-1]:
                        extension = path.split("/")[-1].split(".")[-1].lower()
                        # everything up to the .
                        path = path[:-len(extension)-1]
                    else:
                        # otherwise, assume html
                        extension = "html"

                    if extension == "html":
                        # check if python script in directory
                        py_files = []
                        for file in os.listdir(f"{self.page_dir}{path}"):
                            if file.endswith(".py"):
                                py_files.append(file)
                        if py_files:
                            html_filename = f"{self.page_dir}{path}/.{extension}"
                            with open(html_filename, 'r') as f:
                                html = f.read()

                                body_location = html.index("<body")
                                # insert `onload="brython()"` into body tag
                                html = html[:body_location+5] + " onload=\"brython()\"" + html[body_location+5:]

                                end_of_body = html.index("</body>")
                                script_injection = "<script src=\"https://cdn.jsdelivr.net/npm/brython@3/brython.min.js\">\n</script><script src=\"https://cdn.jsdelivr.net/npm/brython@3/brython_stdlib.js\"></script>\n"
                                for py_file in py_files:
                                    with open(f"{self.page_dir}{path}/{py_file}", 'r') as f:
                                        py_script = f.read()
                                    script_injection += f"<script type=\"text/python\">{py_script}</script>\n"

                                new_html = html[:end_of_body] + script_injection + html[end_of_body:]

                                self.send_response(200)
                                self.send_header("Content-Type", "text/html")
                                self.send_header("Content-Length", len(new_html))
                                self.end_headers()
                                self.wfile.write(new_html.encode())
                            return

                    elif extension in ["css", "js", "py"]:
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
                        self.responses[method_name][func_path](Request(self, params=kwargs), Response(self))()
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
