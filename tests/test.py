
import aiofiles
import asyncio
from asyncio.transports import Transport

class AsyncHandler(asyncio.Protocol):
    def connection_made(self, transport: Transport) -> None:
        self.transport = transport
        return super().connection_made(transport)
    
    def send(self, message:str):
        self.transport.write(message.encode())

    async def do_GET(self):
        self.send("HTTP/1.1 200 OK\r\n\r\nhi!")

    async def process_request(self, method, path, headers, body):
        if method == "GET":
            await self.do_GET()
        else:
            self.send("HTTP/1.1 405 Method Not Allowed\r\n\r\n")


class AsyncServer:
    def __init__(self, /, *, brython:bool=True, page_dir:str="./pages", error_dir="./errors", debug:bool=False, **kwargs)-> "AsyncServer":
        self.debug = debug
        self.handler = AsyncHandler

    def listen(self, port:int, ip:str="0.0.0.0") -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        coro = loop.create_server(self.handler, ip, port)
        server = loop.run_until_complete(coro)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__=="__main__":
    server = AsyncServer(debug=True)
    server.listen(8080)
