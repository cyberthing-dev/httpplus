
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

