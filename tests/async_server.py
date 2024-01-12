
import http_plus_purplelemons_dev as http_plus
from datetime import datetime as dt

server = http_plus.AsyncServer(debug=True)

auth = http_plus.Auth()

@server.log
def logger(r:http_plus.Handler):
    print(f"[{dt.now().strftime('%H:%M:%S')}] ({r.ip}) \"{r.method} {r.status} {r.path}\" {r.protocol_version}")

@server.get("/init")
async def _(req:http_plus.Request, res:http_plus.Response):
    resp = res.set_body("Hello, async world!")
    print(f"made response: {resp}")
    return resp

# listen
server.listen(8000)
