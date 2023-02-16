
import http_plus_purplelemons_dev as http_plus

server = http_plus.Server("0.0.0.0", 80, debug=True)
@http_plus.get(server, "/")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, world!")

server.listen()
