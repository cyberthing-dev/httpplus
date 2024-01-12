from traceback import print_exception as print_exc
import aiofiles
import asyncio
from asyncio.transports import Transport
from typing import Callable
import json
from .communications import (
    STATUS_MESSAGES,
    Request,
    Response,
    StreamResponse,
    GQLResponse,
    Handler,
)
from datetime import datetime as dt


class AsyncHandler(asyncio.Protocol):
    # I need to figure out if AsyncHandler should inherit from both Handler and asyncio.Protocol

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
    body: "str|dict|list|None" = None
    http_version = "HTTP/1.1"
    headers: dict[str, str] = {}
    "`Content-Length` is set automatically"
    server_version: str

    @staticmethod
    def create_task(coro) -> asyncio.Task:
        pass

    @staticmethod
    def match_route(path: str, route: str) -> tuple[bool, dict[str, str]]:
        return Handler.match_route(path, route)

    def connection_made(self, transport: Transport) -> None:
        self.transport = transport
        return super().connection_made(transport)

    def send_data(self, message: str):
        self.transport.write(message.encode())

    def respond(self, code: int, message: str, body: str = ""):
        response = f"{self.http_version} {code} {message}\r\n"
        for header_key, header_value in self.headers.items():
            response += f"{header_key}: {header_value}\r\n"
        response += "\r\n"
        if body:
            response += f"{body}\r\n"
        self.send_data(response)

    # @staticmethod
    def send_response(self, response: "Response"):
        self.send_data(
            f"{self.http_version} {response.status_code} {STATUS_MESSAGES[response.status_code]}\r\n"
        )
        self.send_data(f"Content-Length: {len(response.body)}\r\n")
        self.send_data(f"Date: {dt.utcnow()}\r\n")
        self.send_data(f"Server: {self.server_version}\r\n")
        for header_key, header_value in response.headers.items():
            self.send_data(f"{header_key}: {header_value}\r\n")
        self.send_data("\r\n")
        self.send_data(response.body)

    def error(self, code: int, message: str, body: str = ""):
        self.respond(code, message, body)
        self.transport.close()

    @staticmethod
    def _make_method(http_method: Callable):
        method_name = http_method.__name__[3:].lower()

        def method(self: "AsyncHandler"):
            return self.responses[method_name][self.path]()

        return method

    def data_received(self, data: bytes) -> None:
        try:
            # headers
            headers = data.split(b"\r\n\r\n")[0]
            # exclude first line because it's the method
            headers = b"\r\n".join(headers.split(b"\r\n")[1:])
            client_headers = {}
            # limit to 3 b" " splits
            self.method, self.path, self.protocol_version = map(
                bytes.decode, data.split(b" ")[:3]
            )
            self.method, self.protocol_version = map(
                str.upper, (self.method, self.protocol_version)
            )

            for line in headers.split(b"\r\n"):
                name, value = line.split(b": ")
                client_headers[name.decode()] = value.decode()

            # body
            body: str = data.split(b"\r\n\r\n")[1].decode()
            if self.headers.get("Content-Type") == "application/json":
                body: "dict|list" = json.loads(body)

            if self.method in (
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "OPTIONS",
                "HEAD",
                "TRACE",
            ):
                # check for stream under GET
                ...
                # check for gql under POST
                ...
                # try file serve
                ...
                # also try brython
                # searh from reponses dict
                self.command = self.method.lower()
                for func_path in self.responses[self.command]:
                    self.client_address = self.transport.get_extra_info(
                        "peername"
                    )  # if that doesnt work, go here: https://stackoverflow.com/questions/61963107/when-asyncio-transport-get-extra-infopeername-returns-none

                    matched, kwargs = self.match_route(self.path, func_path)
                    if matched:
                        self.create_task(
                            self.responses[self.command][func_path](
                                Request(self, params=kwargs), Response(self)
                            )
                        ).add_done_callback(
                            lambda task: self.send_response(task.result())
                        )
                        return

                # otherwise, 404
                else:
                    self.error(
                        404, message=f"Not Found", body=f"Path {self.path} not found"
                    )
            else:
                self.error(405, "Method Not Allowed")

        except Exception as e:
            print_exc(e)
            self.error(500, "Internal Server Error")

    # @_make_method
    # def do_GET(self):
    #    return

    # @_make_method
    # def do_POST(self):
    #    return

    # @_make_method
    # def do_PUT(self):
    #    return

    # @_make_method
    # def do_DELETE(self):
    #    return

    # @_make_method
    # def do_PATCH(self):
    #    return

    # @_make_method
    # def do_OPTIONS(self):
    #    return

    # @_make_method
    # def do_HEAD(self):
    #    return

    # @_make_method
    # def do_TRACE(self):
    #    return
