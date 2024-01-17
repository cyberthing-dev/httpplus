"""
Responsible for defining communication objects and functions.
"""

from json import dumps, loads
from dataclasses import dataclass
from typing import Any, Callable
from platform import system as detect_os
import graphql
from http.server import BaseHTTPRequestHandler
from typing import Callable
from os.path import exists
import os
from traceback import print_exception as print_exc, format_exc
from . import __version__
from .static_responses import SEND_RESPONSE_CODE
from .content_types import detect_content_type
import json

STATUS_MESSAGES = {
    # INFORMATIONAL
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    # SUCCESS
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-status",
    208: "Already Reported",
    226: "IM Used",
    # REDIRECTION
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    # CLIENT ERROR
    400: "Bad Request",
    401: "Unathorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    421: "Misdirected Request",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    # SERVER ERROR
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
}


class Handler(BaseHTTPRequestHandler):
    """
    A proprietary HTTP request handler for the server.
    It is highly suggested that you have a good understanding of
    `http.server` and httpplus before modifying or substituting this class.
    """

    routes: dict[str, dict[str, "Route"]] = {
        "get": {},
        "post": {},
        "put": {},
        "delete": {},
        "patch": {},
        "options": {},
        "head": {},
        "trace": {},
    }
    # I spent 30m trying to debug this because this was originally set to `routes.copy()`. im never using `.copy()` again.
    responses: dict[str, dict[str, Callable]] = {
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
        "gql": {},
    }
    page_dir: str
    error_dir: str
    debug: bool
    server_version: str = f"http+/{__version__}"
    protocol_version: str = "HTTP/1.1"
    status: int
    body: str = ""
    json: dict = {}
    brython: bool
    gql_endpoints: dict[str, Callable[..., "GQLResponse"]] = {}
    "Endpoint to GQL resolver mappings"
    gql_schemas: dict[str, str] = {}
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

    def log_message(self, fmt: str, *args) -> None:
        """
        Do not override. Use `@server.log`.
        """
        self.status = int(args[1])
        # bit of a hacky way of checking if the user has overriden the custom logger
        if self.custom_logger.__doc__ == "Override this":
            return super().log_message(fmt, *args)
        else:
            return self.custom_logger()

    def error(
        self,
        code: int,
        *,
        message: str = None,
        headers: dict[str, str] = None,
        traceback: str = "",
        **kwargs,
    ) -> None:
        error_page_path = f"{self.error_dir}/{code}/.html"
        if exists(error_page_path):
            self.respond_file(code, error_page_path)
        else:
            self.respond(
                code=code,
                headers=headers,
                message=SEND_RESPONSE_CODE(
                    code=code, path=message, traceback=traceback, **kwargs
                ),
            )
            if self.debug:
                print(
                    f"Error {code} occured, but no error page was found at {error_page_path}."
                )

    def respond_file(self, code: int, filename: str) -> None:
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

    def respond(self, code: int, message: str, headers: dict[str, str]) -> None:
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

    def resolve_path(self, method: str, path: str) -> str:
        """
        Returns the content at the path of a *local* url or file.
        For url redirection, use `Response.redirect`.
        """
        for route in self.routes[method]:
            if route == path:
                return self.routes[method][route].send_to
        return path

    @staticmethod
    def match_route(path: str, route: str) -> tuple[bool, dict[str, str]]:
        """Checks if a given `path` from a request matches a given `route` from a predefined route.

        Args:
            path (str): The path from the request.
            route (str): The route from the predefined route.
        Returns:
            tuple[bool,dict[str,str]]: A tuple containing a boolean value indicating whether the path
            matches the route, and a dictionary containing the keyword variables from the route.
        """
        if len(path.split("/")) == len(route.split("/")):
            kwargs = {}
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
                            "bool": bool,
                        }[type_]
                    except (KeyError, ValueError):
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

    def serve_filename(self, path: str, target_ext: str = "html") -> "str|None":
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
    def _make_method(http_method: Callable):
        """
        Wrapper for creating `do_<METHOD>` methods.
        """
        method_name = http_method.__name__[3:].lower()

        def method(self: "Handler"):
            # Getting body:
            length = int(self.headers.get("Content-Length", 0))
            if length:
                self.body = self.rfile.read(length).decode()
            # Setting up json
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
                            for event in self.responses["stream"][func_path](
                                Request(self, params=kwargs), StreamResponse(self)
                            ):
                                event: Event
                                self.wfile.write(event.to_bytes())
                            return

                # GQL
                if self.path in self.gql_endpoints:
                    self.gql_endpoints[self.path](
                        Request(self, params={}), GQLResponse(self)
                    )()
                    return

                # file serve
                if method_name == "get":
                    path = self.path
                    if "." in path.split("/")[-1]:
                        extension = path.split("/")[-1].split(".")[-1].lower()
                        # everything up to the .
                        path = path[: -len(extension) - 1]
                    else:
                        # otherwise, assume html
                        extension = "html"

                    if extension == "html" and not os.path.exists(f"{self.page_dir}{path}.py"):
                        filename = self.serve_filename(path, extension)
                        if filename is not None:
                            self.respond_file(200, filename)
                            return

                    elif extension == "html" and self.brython:
                        # check if python script in directory
                        py_files = []
                        for file in os.listdir(f"{self.page_dir}{path}"):
                            if file.endswith(".py"):
                                py_files.append(file)
                        if py_files:
                            html_filename = f"{self.page_dir}{path}/.{extension}"
                            with open(html_filename, "r") as f:
                                html = f.read()

                                body_location = html.index("<body")
                                # insert `onload="brython()"` into body tag
                                html = (
                                    html[: body_location + 5]
                                    + ' onload="brython()"'
                                    + html[body_location + 5 :]
                                )

                                end_of_body = html.index("</body>")
                                script_injection = '<script src="https://cdn.jsdelivr.net/npm/brython@3/brython.min.js">\n</script><script src="https://cdn.jsdelivr.net/npm/brython@3/brython_stdlib.js"></script>\n'
                                for py_file in py_files:
                                    with open(
                                        f"{self.page_dir}{path}/{py_file}", "r"
                                    ) as f:
                                        py_script = f.read()
                                    script_injection += f'<script type="text/python">{py_script}</script>\n'

                                new_html = (
                                    html[:end_of_body]
                                    + script_injection
                                    + html[end_of_body:]
                                )

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
                        self.respond_file(
                            200, self.resolve_path(method_name, route.full_path)
                        )
                        return
                for func_path in self.responses[method_name]:
                    matched, kwargs = self.match_route(self.path, func_path)
                    if matched:
                        self.responses[method_name][func_path](
                            Request(self, params=kwargs), Response(self)
                        )()
                        return
                else:
                    self.error(404, message=self.path)
            except Exception as e:
                if self.debug:
                    print_exc(e)
                self.error(
                    code=500,
                    message=str(e),
                    traceback=format_exc() if self.debug else "",
                )
                return

        return method

    # it's condensed now! :D
    @_make_method
    def do_GET(self):
        return

    @_make_method
    def do_POST(self):
        return

    @_make_method
    def do_PUT(self):
        return

    @_make_method
    def do_DELETE(self):
        return

    @_make_method
    def do_PATCH(self):
        return

    @_make_method
    def do_OPTIONS(self):
        return

    @_make_method
    def do_HEAD(self):
        return

    @_make_method
    def do_TRACE(self):
        return


class RouteExistsError(Exception):
    def __init__(self, route: str = ...):
        """
        Raised when a route already exists.
        """
        super().__init__(
            f"Route {route} already exists." if route else "Route already exists."
        )


class Event:
    def __init__(self, data: str, event_name: str = None, id: str = None):
        """
        Used for streaming events to the client. Set up a listener with `http_plus.stream(path=str)`
        """
        self.data = data
        self.event_name = event_name
        self.id = id

    def to_bytes(self) -> bytes:
        message = ""
        if self.event_name:
            message += f"event: {self.event_name}\r\n"
        if self.id:
            message += f"id: {self.id}\r\n"
        message += f"data: {self.data}\r\n"
        message += "\r\n"
        return message.encode()


@dataclass
class Route:
    """Custom dataclass for optimizing route creation, readability, and resolution.

    Attributes:
        send_to (str): The directory to respond with in the form of `./path/to/directory/`, `path/to/file.ext`, etc..
        route_type (str): The type of route. Can be either `pages`, `errors`, or `static`.
        content (str): The content to respond with. Only used for `static` routes.
        content_type (str): The content type to respond with. Only used for `static` routes.
    """

    send_to: str
    route_type: str

    @property
    def full_path(self) -> str:
        """
        Returns the full path to the file to respond with.
        """
        return f"./{self.route_type}{self.send_to}"


class Request:
    """
    Request object, passed into HTTP method listeners as the first argument.
    """

    class Params:
        """
        Accessed from `Request.params`.

        Given the route `/example/:id`, you may use `Request.params.id`.
        However, if the route is `/example/example-id`, then you must use either
        `Request.params["example-id"]` or `Request.params.get("example-id")`.
        """

        def __init__(self, kwargs: dict[str, str]):
            for param, value in kwargs.items():
                # Fun fact, setattr is ~39% faster than __setattr__.
                setattr(self, param, value)

        def __getitem__(self, key: str) -> str:
            return getattr(self, key)

        def get(self, param: str) -> str:
            return getattr(self, param)

        def __repr__(self) -> str:
            return f"Request.params({self.__dict__})"

        def __str__(self) -> str:
            return self.__repr__()

        def __eq__(self, o: object) -> bool:
            if isinstance(o, Request.params):
                return self.__repr__() == o.__repr__()
            return False

    def __init__(self, request: Handler, /, *, params: dict[str, str]):
        self.request = request
        "The request object directly from the HTTP Server."
        self.path = request.path
        self.method = request.command
        self.headers = request.headers
        "The headers of the request (equivalent to request.headers)."
        self.authorization = self.get_auth()
        "The authorization header of the request, if it exists, in the format `(scheme,token)`. Is `None` if it doesn't exist."
        self.body = request.body
        self.ip, self.port = request.client_address
        self.params = self.Params(params)
        "The a dictionary-like object containing the parameters from the request url's keyword path."

    # Dunder pog
    def __repr__(self) -> str:
        return f"Request({self.method=}, {self.path=}, {self.headers=}, {self.body=})"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Request):
            return self.__repr__() == o.__repr__()
        return False

    def __ne__(self, o: object) -> bool:
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

    def get_header(self, header: str, default=None) -> str:
        try:
            return self.headers[header]
        except KeyError:
            return default

    def get_auth(self, default=None) -> "str|None":
        try:
            return self.headers["Authorization"].split(" ", 1)
        except (
            KeyError,
            AttributeError,
        ):  # note on commit 77290f6: i have no idea why the fuck it was AttributeError and furthermore have less of a clue as to why it was working fine
            return default

    @property
    def json(self) -> dict:
        return loads(self.body)

    @property
    def text(self) -> str:
        return self.body.decode()

    def param(self, param: str) -> str:
        return self.params[param]


class Response:
    """
    Response object, passed into HTTP method listeners as the second argument.

    You *must* return this from the HTTP method listener function.
    """

    def __init__(self, response: Handler):
        self.response = response
        self.headers: dict[str, str] = {}
        self.body: str = ""
        self.status_code = 200
        self.isLinked = False
        self._route: Route

    def __repr__(self) -> str:
        headers = self.headers
        status_code = self.status_code
        body = self.body
        return f"Response({headers=}, {status_code=}, {body=})"

    def set_header(self, header: str, value: str | Any) -> "Response":
        value = str(value)
        self.headers[header] = value
        return self

    def set_body(self, body: "bytes|str|dict") -> "Response":
        """
        Automatically pareses the body into bytes, and sets the Content-Type header to application/json if the body is a dict.
        Will be overwritten if `Response` is returned from the HTTP method listener function.

        Args:
            body (bytes|str|dict): The body of the response.
        """
        self.set_header("Content-Type", "text/plain")
        if isinstance(body, dict):
            self.set_header("Content-Type", "application/json")
            self.body = dumps(body)
        elif isinstance(body, bytes):
            self.set_header("Content-Type", "application/octet-stream")
            self.body = body.decode()
        else:
            self.body = body
        self.set_header("Content-Length", len(self.body))
        return self

    def send_file(self, path: str) -> "Response":
        """
        Serves a file to the client. This is useful if you want to do backend logic before sending a file.

        Args:
            path (str): The path to the file to send.
        """
        with open(path, "rb") as f:
            # .decode() could be more efficient because we .encode() later.
            self.body = f.read().decode()
        self.set_header("Content-Length", len(self.body))
        return self

    def prompt_download(self, path: str, filename: str = None) -> "Response":
        """
        Prompts a file download!

        Args:
            path (str): The path to the file to send.
            filename (str): The name of the file that the client receives.
             This can be different from what's at `path`.
             Defaults to the filename of the file at `path`.
        """
        if filename is None:
            if detect_os() == "Windows":
                filename = path.split("\\")[-1]
            else:
                filename = path.split("/")[-1]
        self.set_header("Content-Disposition", f"attachment; filename={filename}")
        # this is pretty clever, eh? eh?
        self.send_file(path)
        return self

    def status(self, code: int) -> "Response":
        """
        Sets the status code of the response.

        Args:
            code (int): The status code to set.
        """
        self.status_code = code
        return self

    def redirect(self, to: str) -> "Response":
        """
        Will redirect client to the specified destination.

        Args:
            to (str): The path to route to.
        """
        self.headers["Location"] = to
        self.status_code = 302  # Found == temporary redirect
        self.isLinked = True
        return self

    def __call__(self) -> None:
        """
        Sends the response to the client.
        You should not call this manually unless you are modifying `http_plus.Server`.
        """
        print("Response was called")
        self.response.send_response(self.status_code)
        for header, value in self.headers.items():
            self.response.send_header(header, value)
        self.response.end_headers()
        if not self.isLinked:
            self.response.wfile.write(self.body.encode())
        return


class StreamResponse(Response):
    """
    StreamResponse should be used exclusively with `@http_plus.stream(path=str)`.

    Yield events with `response.event(data=...,[event=...],[id=...])` where `data` is required
    and `event` and `id` is optional (`event` defaults to "message").
    """

    def event(self, data: str, event_name: str = None, id: int = None) -> Event:
        """
        Creates an event that will be streamed to the client. Yield this function to stream events to the client.

        `data` should be a string. Use `json.dumps()` to convert a dict or list to a string.

        Args:
            data (str): The data to stream to the client.
            event_name (str): The event to send the data as. Defaults to `"message"`. Listen to the event on the client with `EventSource.addEventListener(event_name, callback)`.
            id (int): The id of the event. Defaults to `None`.
             Listen to the event on the client with `EventSource.addEventListener(event_name, callback, { id: event_id })`.
        """
        return Event(data, event_name, id)


class GQLResponse(Response):
    """
    GQLResponse should be used exclusively with `@http_plus.gql(path=str)`.

    You *must* return this from the GraphQL method listener function.
    """

    def set_database(self, database: dict[str,]):
        """
        Resolves a GQL query with the specified database/dict.
        """
        self.database = database
        return self

    def _resolve(self) -> dict[str]:
        schema = self.response.gql_schemas[self.response.path]
        parsed_schema = graphql.build_schema(schema)
        query = self.response.json["query"]

        return graphql.graphql_sync(
            schema=parsed_schema, source=query, root_value=self.database
        ).data

    def __call__(self) -> None:
        resolved = self._resolve()
        if resolved is not None:
            self.set_body(resolved)
        else:
            self.status(500)
            self.set_body({"error": "An error occurred."})
        return super().__call__()
