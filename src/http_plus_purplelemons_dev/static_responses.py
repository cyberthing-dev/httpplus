
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

def SEND_RESPONSE_CODE(code:int,path:str="") -> str:
    """Used explicitly for error code responses (400-599) for now.
    Informational responses should be header-only,
    and sucessful responses *usually* require a specified body."""
    return {
        # 400-499 - client error
        400: _400,
        401: _401,
        403: _403,
        404: _404,
        405: _405,
        406: _406,
        407: _407,
        408: _408,
        409: _409,
        410: _410,
        411: _411,
        412: _412,
        413: _413,
        414: _414,
        415: _415,
        416: _416,
        417: _417,
        418: _418,
        421: _421,
        426: _426,
        428: _428,
        429: _429,
        431: _431,
        451: _451,
        # 500-599 - server error
        500: _500,
        501: _501,
        502: _502,
        503: _503,
        504: _504,
        505: _505,
        506: _506,
        510: _510,
        511: _511,
    }[code](path)

def generate_html(code:int,title:str,body:str,include_explanation:bool=True) -> str:
    explanation = f"<h3>Read more about the error <a href='https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{code}'>here</a>.</h3>" if include_explanation else ""
    return f"""<!DOCTYPE HTML>
<html>
<head>
    <title>{title}</title>
</head>
<body>
    <h1>{body}</h1>
    <img src="https://http.cat/{code}.jpg" alt="{title}" />
    {explanation}
</body>
</html>"""

# Informational responses 100-199
...

# Successful responses 200-299
...

# Redirection responses 300-399
...

# Client error responses 400-499
def _400(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 400 error page."""
    message = f'"{path}"' if path else "The endpoint you were looking for"
    return generate_html(400,"Bad Request",f"{message} could not be understood by the server.")

def _401(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 401 error page."""
    message = f'"{path}"' if path else "this page."
    return generate_html(401,"Unauthorized",f"You are not authorized to access {message}")

def _403(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 403 error page."""
    message = f'"{path}"' if path else "this page."
    return generate_html(403,"Forbidden",f"You are forbidden from accessing {message}")

def _404(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 404 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(404,"Not Found", f"{message} could not be found.")

def _405(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 405 error page."""
    message = f'"{path}"' if path else "this page"
    return generate_html(405,"Method Not Allowed",f"The method you requested to access {message} is not allowed.")

def _406(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 406 error page."""
    message = f'"{path}"' if path else "this page."
    return generate_html(406,"Not Acceptable",f"The server cannot provide a response that is acceptable to the client for {message}")

def _407(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 407 error page."""
    message = f'"{path}"' if path else "The endpoint you were looking for"
    return generate_html(407,"Proxy Authentication Required",f"{message} requires authentication from a proxy server.")

def _408(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 408 error page."""
    message = f'"{path}"' if path else "The endpoint"
    return generate_html(408,"Request Timeout",f"{message} did not receive a response from the client in time.")

def _409(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 409 error page."""
    message = f'"{path}"' if path else "Your request"
    return generate_html(409,"Conflict",f"{message} experienced a conflict with the server while processing.")

def _410(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 410 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(410,"Gone",f"{message} is no longer available and has been permenantly deleted.")

def _411(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 411 error page."""
    message = f'"{path}"' if path else "The endpoint you were looking for"
    return generate_html(411,"Length Required",f"{message} requires a Content-Length header to be sent with the request.")

def _412(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 412 error page."""
    message = f'"{path}"' if path else "the endpoint."
    return generate_html(412,"Precondition Failed",f"The server failed the precondition check(s) you supplied in your request for {message}")

def _413(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 413 error page."""
    message = f'"{path}"' if path else "The request"
    return generate_html(413,"Payload Too Large",f"{message} was too large for the server to process.")

def _414(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 414 error page."""
    return generate_html(414,"URI Too Long",f"The requested URI was too long for the server to process.")

def _415(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 415 error page."""
    message = f'"{path}"' if path else "this page."
    return generate_html(415,"Unsupported Media Type",f"The server does not support the media type you requested for {message}")

def _416(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 416 error page."""
    message = f'"{path}"' if path else "The requested `Range` header"
    return generate_html(416,"Range Not Satisfiable",f"{message} is not satisfiable.")

def _417(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 417 error page."""
    message = f'"{path}"' if path else "The requested `Expect` header"
    return generate_html(417,"Expectation Failed",f"{message} failed to meet the expectations of the server.")

def _418(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 418 error page."""
    return generate_html(418,"I'm a teapot",f"The server is apparently a teapot.",include_explanation=False)

def _421(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 421 error page."""
    message = f'"{path}"' if path else "The requested `Host` header"
    return generate_html(421,"Misdirected Request",f"{message} is misdirected at a server that cannot produce a response. This response if from a server that is designed to handle requests for multiple domains.",include_explanation=False)

def _426(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 426 error page."""
    message = f'"{path}"' if path else "this endpoint"
    return generate_html(426,"Upgrade Required",f"The protocol used for requesting {message} is not supported, but newer versions may be.")

def _428(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 428 error page."""
    message = f'"{path}"' if path else "the endpoint"
    return generate_html(428,"Precondition Required",f"Your request for {message} must include a `If-Match` header.")

def _429(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 429 error page."""
    message = f'"{path}"' if path else "this endpoint"
    return generate_html(429,"Too Many Requests",f"You have sent too many requests to {message} in a given amount of time.")

def _431(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 431 error page."""
    message = f'"{path}"' if path else "this endpoint"
    return generate_html(431,"Request Header Fields Too Large",f" Your request for {message} contained too many header fields.")

def _451(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 451 error page."""
    message = f'"{path}"' if path else "This endpoint"
    return generate_html(451,"Unavailable For Legal Reasons",f"{message} is unavailable due to legal reasons.")

# Server error responses 500-599
def _500(path:str="", /, exception:str=None, *args, **kwargs) -> str:
    """Returns the HTML for the 500 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(500,"Internal Server Error",f"{message} experienced an error during internal processing." + (f" Error: {exception}" if exception else ""))

def _501(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 501 error page."""
    message = f'"{path}"' if path else "the page you were looking for"
    return generate_html(501,"Not Implemented",f"The request method for {message} is not implemented.")

def _502(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 502 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(502,"Bad Gateway",f"{message} received an invalid response from an upstream server.")

def _503(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 503 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(503,"Service Unavailable",f"{message} is currently unavailable.")

def _504(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 504 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(504,"Gateway Timeout",f"{message} did not receive a response from an upstream server in time.")

def _505(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 505 error page."""
    message = f'"{path}"' if path else "the page"
    return generate_html(505,"HTTP Version Not Supported",f"Your request for {message} asked for an unsupported HTTP version.")

def _506(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 506 error page."""
    message = f'"{path}"' if path else "The endpoint"
    return generate_html(506,"Variant Also Negotiates",f"{message} is configured to negotiate content, but the server is unable to do so.")

def _510(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 510 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(510,"Not Extended",f"{message} requires a proxy/extension to process the request, but the proxy is not configured to do so.")

def _511(path:str="", *args, **kwargs) -> str:
    """Returns the HTML for the 511 error page."""
    message = f'"{path}"' if path else "The page you were looking for"
    return generate_html(511,"Network Authentication Required",f"{message} requires <em>network</em> authentication to access.")
