
f"""
Currently only supports command line usage. Do not use this in production.
Usage:
    `$ python -m http_plus_purplelemons_dev [-p PORT] [-d] [--bind IP] [-i] [--log '<fmt>'] [-s] [--page-dir PATH] [--error-dir PATH]`

Run `$ python -m http_plus_purplelemons_dev -h` for more information.
"""

from . import init, Server, Request, Response, NAME

assert __name__ == "__main__", f"Do not import this module. Please run this module directly via `python -m {NAME}`."

import argparse
from datetime import datetime as dt

parser = argparse.ArgumentParser(description="A simple HTTP server.")
parser.add_argument("-p", "--port", type=int, default=8000, help="The port to listen on.")
parser.add_argument("-d", "--debug", action="store_true", help="Enables debug mode.")
parser.add_argument("--bind", type=str, help="The host IP to listen on.")
parser.add_argument("-i","--init", action="store_true", help="Does not start the server, but instead initializes the current directory for HTTP+")
parser.add_argument("--log","--format", metavar="'<fmt>'", type=str, help="The format for the log message. !ip is the client IP, !date is the day in YYYY/MM/DD, !time is the time in HH:MM:SS, !method is the HTTP request method, !path is the URI, !status is the HTTP response code, and !proto is the HTTP protocol version the request is made over.")
parser.add_argument("-s", "--save", action="store_true", help="Saves the log to a file.")
parser.add_argument("--page-dir", metavar="PATH", type=str, default="./pages", help="The directory to serve pages from.")
parser.add_argument("--error-dir", metavar="PATH", type=str, default="./errors", help="The directory to serve error pages from.")

args = parser.parse_args()

if args.init:
    init()
    exit(0)

server = Server(
    page_dir = args.page_dir,
    error_dir = args.error_dir,
    debug = args.debug
)

if args.log is not None:
    @server.log
    def _(r:Request):
        time = dt.now().strftime("%H:%M:%S")
        date = dt.now().strftime("%Y/%m/%d")
        fmt:str = args.log
        print(fmt.replace("!ip", r.ip).replace("!date", date).replace("!time", time).replace("!method", r.method).replace("!path", r.path).replace("!status", str(r.status)).replace("!proto", r.protocol_version))

@server.get("/")
def _(req:Request, res:Response):
    return res.set_body("Hello, world!")

server.listen(port=args.port, ip=args.bind)
