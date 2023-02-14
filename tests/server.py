
import http_plus_purplelemons_dev.server as http_plus

server = http_plus.Server("0.0.0.0", 80)
@http_plus.get(server, "/")
def _(request:http_plus.Request, response:http_plus.Response):
    response.set_body("Hello, world!")
    return response

server.listen()
