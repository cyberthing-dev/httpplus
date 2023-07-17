
import http_plus_purplelemons_dev as http_plus
from time import sleep
from datetime import datetime as dt

server = http_plus.Server(debug=True)

auth = http_plus.Auth()

@server.log
def logger(r:http_plus.Handler):
    print(f"[{dt.now().strftime('%H:%M:%S')}] ({r.ip}) \"{r.method} {r.path}\" {r.protocol_version}")

@server.get("/")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, world!")

@server.get("/test")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, test!")

@server.get("/kwtest/:testnum")
def _(req:http_plus.Request, res:http_plus.Response):
    # Both below work, except in the case of using Python syntax.
    testnum = req.params.testnum
    testnum = req.param("testnum")
    return res.set_body(f"Hello, {testnum=}!")

@server.get("/kwtest/*/test")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, .../*/test!")

@server.post("/posty")
def _(req:http_plus.Request, res:http_plus.Response):
    res.set_header("Content-Type", "text/html")
    return res.set_body("\n".join(f"{k}: {v}" for k, v in req.json.items()))

@server.all("/all")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, all methods!")

@server.get("/error_test")
def _(req:http_plus.Request, res:http_plus.Response):
    raise Exception("This is an error test, completely normal stuff dont worry lol why are you worrying i said stop worrying stop crying why are you crying this is normal.")

@server.get("/google")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.redirect("https://google.com")

@server.stream("/stream_test")
def _(req:http_plus.Request, res:http_plus.StreamResponse):
    for i in range(10):
        yield res.event(str(i), "message")
        sleep(1)

@server.get("/auth_test")
def _(req:http_plus.Request, res:http_plus.Response):
    if req.authorization is not None:
        scheme, token = req.authorization
        user = auth[token]
        return res.set_body(f"Hello, authenticated user!\nName: {user.username}\nID: {user.id}")
    return res.set_body("You are not authenticated.")

@server.get("/get_authed")
def _(req:http_plus.Request, res:http_plus.Response):
    token = auth.generate(
        username="test",
        id=1234
    )
    return res.set_body({
        "token": token
    })

@server.get("/send_file")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.send_file("test.txt")

@server.get("/prompt_download")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.prompt_download("test.txt")

@server.get("/error_test")
def _(req:http_plus.Request, res:http_plus.Response):
    0/0
    return res.set_body("Hello, error_test!")

server.listen(8000)
