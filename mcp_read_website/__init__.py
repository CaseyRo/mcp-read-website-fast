"""mcp-read-website-fast."""

import os
from importlib.metadata import PackageNotFoundError, version

try:
    # Releases are git tags; the image carries the tag as APP_VERSION.
    __version__ = os.environ.get("APP_VERSION") or version("mcp-read-website-fast")
except PackageNotFoundError:
    __version__ = "unknown"
