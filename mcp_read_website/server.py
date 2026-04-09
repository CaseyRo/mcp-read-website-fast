"""FastMCP server for fast web content extraction."""

from __future__ import annotations

import json
import logging
import shutil
from enum import Enum
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from mcp_read_website.auth import BearerTokenVerifier
from mcp_read_website.config import settings
from mcp_read_website.crawler import crawl_website, list_page_links

logger = logging.getLogger(__name__)

# Build authentication (bearer token via MCP_API_KEY)
_auth = None
if settings.mcp_api_key:
    _auth = BearerTokenVerifier(api_key=settings.mcp_api_key.get_secret_value())
elif settings.transport == "http":
    logger.warning(
        "MCP_API_KEY is not set — HTTP server will run WITHOUT authentication. "
        "Set MCP_API_KEY to secure the endpoint."
    )

mcp = FastMCP("read-website-fast", auth=_auth)


class OutputFormat(str, Enum):
    markdown = "markdown"
    json = "json"
    both = "both"


@mcp.tool(
    annotations={
        "title": "Read Website",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def read_website(
    url: Annotated[str, Field(description="HTTP/HTTPS URL to fetch and convert to markdown")],
    pages: Annotated[int, Field(
        default=1, ge=1, le=20,
        description="Number of same-origin pages to crawl via BFS. Use 1 for a single page, 3-10 to read a documentation section. Max 20.",
    )] = 1,
    output: Annotated[OutputFormat, Field(
        default=OutputFormat.markdown,
        description='Output format: "markdown" (default) for reading/summarization, "json" for structured data with title and links, "both" for both',
    )] = OutputFormat.markdown,
    timeout_seconds: Annotated[int, Field(
        default=30, ge=5, le=120,
        description="Timeout per page in seconds. Increase for slow or JS-heavy sites. Default 30.",
    )] = 30,
    max_chars: Annotated[int, Field(
        default=50000, ge=0, le=500000,
        description="Maximum characters to return. 0 for unlimited. Default 50000. Prevents context window overflow on large pages.",
    )] = 50000,
) -> str:
    """Fetch a web page and return clean Markdown. Handles JavaScript-rendered sites.

    Use pages=1 (default) for a single URL. Increase pages to follow same-origin
    links via BFS crawl (e.g. pages=5 to read an entire docs section).

    Use output='json' when you need structured data including the page title and
    all outbound links — useful for deciding what to crawl next.

    Tip: call list_links first to preview available pages before a multi-page crawl.
    """
    result = await crawl_website(
        url,
        max_pages=pages,
        timeout=timeout_seconds * 1000,
        max_chars=max_chars,
    )

    json_data = {
        "markdown": result.markdown or "",
        "title": result.title,
        "links": result.links or [],
        "url": url,
        "error": result.error,
    }

    if output == OutputFormat.json:
        if result.error and not result.markdown:
            return json.dumps({"markdown": "", "title": None, "links": [], "url": url, "error": result.error}, indent=2)
        return json.dumps(json_data, indent=2)

    if output == OutputFormat.both:
        parts: list[str] = []
        if result.error and result.markdown:
            parts.append(f"**Warning:** {result.error}\n\n{result.markdown}")
        elif result.markdown:
            parts.append(result.markdown)
        parts.append("<!-- JSON_DATA -->")
        parts.append("```json\n" + json.dumps(json_data, indent=2) + "\n```")
        return "\n\n".join(parts)

    # Default: markdown
    if result.error and result.markdown:
        return f"**Warning:** {result.error}\n\n{result.markdown}"
    if result.error and not result.markdown:
        raise ValueError(f"Failed to fetch content: {result.error}")
    return result.markdown


@mcp.tool(
    annotations={
        "title": "List Links",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def list_links(
    url: Annotated[str, Field(description="URL to extract links from")],
    same_origin_only: Annotated[bool, Field(
        default=True,
        description="Only return links from the same domain. Set to false to include external links.",
    )] = True,
    timeout_seconds: Annotated[int, Field(
        default=30, ge=5, le=120,
        description="Timeout in seconds. Default 30.",
    )] = 30,
) -> str:
    """Returns the page title and all outbound links without returning full page content.

    Use this before read_website(pages=N) to preview what pages are available
    and select relevant ones. Much cheaper than a full crawl for link discovery.
    """
    result = await list_page_links(
        url,
        same_origin_only=same_origin_only,
        timeout=timeout_seconds * 1000,
    )
    return json.dumps(result, indent=2)


@mcp.tool(
    annotations={
        "title": "Cache Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def get_cache_status() -> str:
    """Returns cache size and file count. Use before deciding whether to re-fetch a URL."""
    cache_dir = settings.cache_dir
    try:
        if not cache_dir.exists():
            return json.dumps({"cacheSize": 0, "cacheFiles": 0, "cacheSizeFormatted": "0.00 MB"}, indent=2)

        files = list(cache_dir.iterdir())
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        return json.dumps({
            "cacheSize": total_size,
            "cacheFiles": len(files),
            "cacheSizeFormatted": f"{total_size / 1024 / 1024:.2f} MB",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": "Failed to get cache status", "message": str(e)}, indent=2)


@mcp.tool(
    annotations={
        "title": "Clear Cache",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def clear_cache() -> str:
    """Clears the on-disk cache. Use when stale content is suspected or cache is too large."""
    try:
        shutil.rmtree(settings.cache_dir, ignore_errors=True)
        return json.dumps({"status": "success", "message": "Cache cleared successfully"}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def main() -> None:
    """Entry point for the mcp-read-website-fast server."""
    if settings.transport == "http":
        mcp.run(transport="streamable-http", host=settings.host, port=settings.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
