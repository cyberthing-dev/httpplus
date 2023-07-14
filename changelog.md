# Changelog

Dates are in YYYY/MM/DD format, time is in America/Chicago (CDT/CST), UTC-0500/-0600. (I've lived in America my whole life, don't @ me, using YYYY/MM/DD is hard enough)
* [Developmental](#developmental-00x) -- This stage will end when I finish implementing all the features I want to. Found in [src/http_plus_purplelemons_dev](./src/http_plus_purplelemons_dev). Changes can be tracked [here](https://github.com/orgs/cyberthing-dev/projects/2/views/1).
* [Pre-release](#) -- This stage will end when I finish gathering feedback from the community and adding new features. Changes can be tracked [here](https://github.com/orgs/cyberthing-dev/projects/3/views/1).
* [Release](#) -- This stage will be continuous and offer bug fixes, maybe new features.

## Developmental (0.0.X)
2023/01/16-2023/07/17

### v0.0.20 (2023/07/13 21:51)
* Backticks (`) have been removed from wrapping parameter names in method docstrings, which prevented code editors from properly displaying type hints/parameter descriptions.
* `communications.Response` is now compatable with Windows file paths now.
* Changelog now has an end date for developmental versions and links to project tracker.

### v0.0.19 (2023/07/13 18:21)
* `Server.listen()` now accepts optional IP and port (the IP will default to `127.0.0.1` if `debug:bool` is `True`, otherwise it listens on all interfaces via `0.0.0.0`).
* General documentation improvement (especially the `Server` class).
* Removed `Server.base()` because it isn't being used anywhere ¯\\\_(ツ)_/¯

### v0.0.18 (2023/07/13 14:45)
* `SEND_RESPONSE_CODE` and `Handler.error()` now accept the `traceback:str` parameter. An error explanation is already sent, but the traceback can be optionally supplied by setting `debug:bool=True` in the `Server()` constructor.
* `Handler.respond()` now sends `Content-length` & `Content-type`. This should have been fixed in v0.0.15, but was overlooked.

### v0.0.17 (2023/07/13 01:14)
* `Response.send_file()` will serve some file at the given path.
* `Response.prompt_download()` will prompt the client to recieve a download.

### v0.0.16 (2023/07/12)
* Moved TODOs to github issues.

### v0.0.15 (2023/07/11 18:07)
* Updated TODOS.
* Fixed documentation & code formatting and added clarification.
* `Auth.generate()` now accepts `token_size:int` as an argument for adjusting security level. Defaults to 128.
* The handler can now serve static files from `./pages/`.
* `Handler.respond_file()` now uses `Content-length`... 15 versions into dev... this is something that I should have caught a long time ago...
* HTTP/1.0 -> HTTP/1.1!
* Note: i believe http+ will be ready for pre-release within a week. This was a huge update.

### v0.0.14 (2023/07/09 15:08)
* Moved project to [Cyberthing](https://github.com/cyberthing-dev).
* Updated TODOs.
* `@server(path)` now works! I'm not sure why i couldn't get it to work at first, but it works now!
* Added [HTML objects!](./src/http_plus_purplelemons_dev/html.py)

### v0.0.13 (2023/04/12 13:54)
* [Authorization!](./src/http_plus_purplelemons_dev/auth.py). Handles automatically generating tokens and will keep track of data associated with the token.

### v0.0.12 (2023/04/11 16:16)
* Event streams! Use `@http_plus.stream(...,"/path/to/endpoint")` and a [StreamResponse](https://github.com/search?q=repo%3Apurplelemons-dev/httpplus%20StreamResponse&type=code) object is used as the response.

### v0.0.11 (2023/04/03 12:57)
* Updated TODOs.
* Cancelled decorator debug capabilities because it was too much work.
* Route types. Defaults to `str`, but specified with `@http_plus.<method>(...,"/path/to/endpoint/:var:<type>")`.

### v0.0.10 (2023/02/23 18:20)
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

