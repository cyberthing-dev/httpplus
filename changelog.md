# Changelog

Dates are in YYYY/MM/DD format, time is in America/Chicago (CDT/CST), UTC-5/-6. (I've lived in America my whole life, don't @ me, using YYYY/MM/DD is hard enough)
* [Developmental](#developmental-00x) -- This stage will end when I finish implementing all the features I want to.
* [Pre-release](#) -- This stage will end when I finish gathering feedback from the community and adding new features.
* [Release](#) -- This stage will be continuous and offer bug fixes, maybe new features.

## Developmental (0.0.X)
2023/01/16-

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

