
def SEND_ERROR(code:int,path:str="") -> str:
    """This is my favorite function"""
    {
        404: ERROR_404,

    }[code](path)

def ERROR_404(path:str="") -> str:
    """Returns the HTML for the 404 error page. This is hardcoded for now, but I may dynamically generate a template."""
    message = path if path else "The page you were looking for"
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Not Found</title>
</head>
<body>
    <h1>{message} could not be found.</h1>
</body>
</html>"""

# TODO: Add more error functions
