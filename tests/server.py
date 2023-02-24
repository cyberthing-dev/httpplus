
import http_plus_purplelemons_dev as http_plus

server = http_plus.Server("0.0.0.0", 80, debug=True)

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

server.listen()
