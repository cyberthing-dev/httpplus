
"""
Currently only supports commandline usage. Do not use this for programming servers.
Usage:
    `$ python -m http_plus_purplelemons_dev`
"""


if __name__=="__main__":
    import http_plus_purplelemons_dev as http_plus
    import argparse

    parser = argparse.ArgumentParser(description="A simple HTTP server.")
    parser.add_argument("-p", "--port", type=int, default=8080, help="The port to listen on.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enables debug mode.")
    parser.add_argument("--bind", type=str, default="0.0.0.0", help="The host IP to listen on.")
    parser.add_argument("---init", action="store_true", help="Does not start the server, but instead initializes the current directory for HTTP+")
    args = parser.parse_args()

    if args.init:
        http_plus.init()
        exit(0)

    server = http_plus.Server("0.0.0.0", args.port, debug=args.debug)

    @http_plus.get(server, "/")
    def _(req:http_plus.Request, res:http_plus.Response):
        return res.set_body("Hello, world!")

    server.listen()
