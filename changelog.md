# Changelog

Dates are in YYYY/MM/DD format, time is in America/Chicago (CDT/CST), UTC-5/-6. (I've lived in America my whole life, don't @ me, using YYYY/MM/DD is hard enough)
* [Developmental](#developmental-00x) -- This stage will end when I finish implementing all the features I want to.
* [Pre-release](#) -- This stage will end when I finish gathering feedback from the community and adding new features.
* [Release](#) -- This stage will be continuous and offer bug fixes, maybe new features.

## Developmental (0.0.X)
2023/01/16-

### v0.0.10 (2023/02/23 )
* Updated TODOs.
* Moved `Response.send()` to `Response.__call__()`. This may prevent devs from accidentally calling `Response.send()`.
* Moved response code setting in `Response._call__()` to be executed before header setting.

### v0.0.9 (2023/02/23 17:15)
* Default error pages now include http code cat!
* `http.Server()` binding now defaults to `127.0.0.1:8080` in accordance with the `http_plus.server` module script defaults.
* `Handler.error()` now sends the error traceback to the page.
* [tests/server.py](./tests/server.py) now has a test for the error page demonstration.
* Updated TODOs... again...

### v0.0.8 (2023/02/23 12:33)
* Added `http_plus.init()` which initializes the current directory for HTTP+
* `@http_plus.<method>()` now raises `RouteExistsError` if `path` already exists for the given method.
* `@http_plus.all()` is now more code efficient and looks cleaner pogchamp.
* Fixed some comment format errors.

### v0.0.7 (2023/02/22 21:18)
* Added listner logic to all methods (originally only `@http_plus.get()` listened).
* Fixed `@http_plus.all()` because evidently i forgot to check if it was working.
* Added more todos.
* Updated the [test server](./tests/server.py) to test 0.0.7 features.

### v0.0.6 (2023/02/22 01:10)
* Added changelog
* Aded TODOs to [main module file](./src/http_plus_purplelemons_dev/__init__.py).
* tests/server.py now utilizes full functions for testing.
* [Request.params](./src/http_plus_purplelemons_dev/communications.py) class provides a simple and easy way of accessing parameters passed in from the uri.
```py
# Sample demonstration
@http_plus.get(server,"/example/:id")
def _(req,res):
    id_param = req.params.id
    return res.send(f"Your id is {id_param}")
```

