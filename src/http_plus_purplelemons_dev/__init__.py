
from .server import Handler
from socketserver import TCPServer

"""Example project structure:
```
./Main Folder
    /server.py
    /pages
        .html
        .css
        .js
        /subfolder
            .html
            ...
    /errors
        /404
            .html
            .css
            .js
        ...
```
In order to access /, the server will look for ./pages/.html. Smiliar thing for /subfolder, it will look for ./pages/subfolder/.html.

You can customize error pages 
"""

__dev_version__ = "0.0.3-socket/0.0.1"
__version__ = __dev_version__

class Server:

    def __init__(self, host:str, port:int, *, debug:bool=False, custom_handler:Handler=Handler):
        """
        HTTPPlus server.
        Modifable methods:
        - logger(self, message:str, level:str="info")
        
        """
        self.host=host
        self.port=port
        self.handler=custom_handler

    def run(self):
        """
        Blocking method that begins listening for requests.
        """
        self.server = TCPServer((self.host, self.port), self.handler)
        self.server.serve_forever()


def get(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def head(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def post(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def put(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def delete(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def connect(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def connect(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def options(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def trace(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

def patch(server:Server,path:str):
    def decorator(func):
        ...
    return decorator

