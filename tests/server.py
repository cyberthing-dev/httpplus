
import http_plus_purplelemons_dev as http_plus
from time import sleep

server = http_plus.Server("0.0.0.0", 8000, debug=True)

auth = http_plus.Auth()

@http_plus.get(server, "/")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, world!")

@http_plus.get(server, "/test")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, test!")

@http_plus.get(server, "/kwtest/:testnum")
def _(req:http_plus.Request, res:http_plus.Response):
    # Both below work, except in the case of using Python syntax.
    testnum = req.params.testnum
    testnum = req.param("testnum")
    return res.set_body(f"Hello, {testnum=}!")

@http_plus.get(server, "/kwtest/*/test")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, .../*/test!")

@http_plus.post(server, "/posty")
def _(req:http_plus.Request, res:http_plus.Response):
    res.set_header("Content-Type", "text/html")
    return res.set_body("\n".join(f"{k}: {v}" for k, v in req.json.items()))

@http_plus.all(server, "/all")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.set_body("Hello, all methods!")

@http_plus.get(server, "/error_test")
def _(req:http_plus.Request, res:http_plus.Response):
    raise Exception("This is an error test, completely normal stuff dont worry lol why are you worrying i said stop worrying stop crying why are you crying this is normal.")

@http_plus.get(server, "/google")
def _(req:http_plus.Request, res:http_plus.Response):
    return res.redirect("https://google.com")

@http_plus.stream(server, "/stream_test")
def _(req:http_plus.Request, res:http_plus.StreamResponse):
    for i in range(10):
        yield res.event(str(i), "test")
        sleep(1)

@http_plus.get(server, "/auth_test")
def _(req:http_plus.Request, res:http_plus.Response):
    if req.authorization is not None:
        scheme, token = req.authorization
        user = auth[token]
        return res.set_body(f"Hello, authenticated user!\nName: {user.username}\nID: {user.id}")
    return res.set_body("You are not authenticated.")

@http_plus.get(server, "/get_authed")
def _(req:http_plus.Request, res:http_plus.Response):
    token = auth.generate(
        username="test",
        id=1234
    )
    return res.set_body({
        "token": token
    })

server.listen()
