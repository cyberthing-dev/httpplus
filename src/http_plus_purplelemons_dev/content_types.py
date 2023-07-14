
"""
Responsible for defining and detecting the content type of a file based on the file extension.
"""

TYPES = {
    "json": "application/json",
    "txt": "text/plain",
    "html": "text/html",
    "css": "text/css",
    "js": "text/javascript",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "ico": "image/x-icon",
    "webp": "image/webp",
    "mp3": "audio/mpeg",
    "mp4": "video/mp4",
    "webm": "video/webm",
    "ogg": "audio/ogg",
    "pdf": "application/pdf",
    "zip": "application/zip",
    "gz": "application/gzip",
    "tar": "application/x-tar",
    "rar": "application/x-rar-compressed",
    "7z": "application/x-7z-compressed",
    "xml": "application/xml",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "eot": "application/vnd.ms-fontobject",
    "ttf": "font/ttf",
    "otf": "font/otf",
    "jsonld": "application/ld+json",
    "wasm": "application/wasm",
    "manifest": "application/manifest+json",
    "map": "application/json",
    "webmanifest": "application/manifest+json",
    "webapp": "application/manifest+json",
    "json5": "application/json5",
    "yaml": "application/yaml",
    "yml": "application/yaml",
    "toml": "application/toml",
    "md": "text/markdown",
    "markdown": "text/markdown",
    "mdx": "text/markdown",
    "mdown": "text/markdown",
    "mkd": "text/markdown",
    "mkdn": "text/markdown",
    "mkdown": "text/markdown",
    "ron": "application/ron",
    "ronn": "application/ron",
    "ron-rb": "application/ron",
    "ron-rs": "application/ron",
    "ronn-rb": "application/ron",
    "ronn-rs": "application/ron",
    "rs": "text/rust",
    "rb": "text/ruby",
    "py": "text/python",
    "pyc": "application/x-python-code"
}

def detect_content_type(filename:str) -> str:
    """
    Detects the content type of a file based on the file extension.

    Args:
        filename (str): The name of the file to detect.
    Returns:
        str: The content type of the file.
    """
    try:
        return TYPES[filename.split(".")[-1]]
    except KeyError:
        return "application/octet-stream"
