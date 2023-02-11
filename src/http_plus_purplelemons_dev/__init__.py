
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

__dev_version__ = "0.0.2"


# TODO: Add a `-m` script that automatically creates a base directory.
# ^ either that or serve pre-defined responses from hardcoded text

# TODO: Add configure error pages to include f"https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{code}"
# for errors in the 4XX-5XX range.

# TODO: Initialize server via decorators (@server.get, @server.post, etc.)
