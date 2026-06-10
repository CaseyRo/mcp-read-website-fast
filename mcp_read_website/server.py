"""FastMCP server for fast web content extraction."""

from __future__ import annotations

import logging
import shutil
from enum import Enum
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from mcp_read_website.auth import BearerTokenVerifier
from mcp_read_website.config import settings
from mcp_read_website.crawler import crawl_website, list_page_links

logger = logging.getLogger(__name__)

SERVER_INSTRUCTIONS = """\
read-website-fast turns web pages into clean, token-efficient Markdown for
reading and summarization. It strips nav, sidebars, and boilerplate (Mozilla
Readability) and renders JavaScript-heavy pages (Crawl4AI / Playwright).

Choosing a tool:
- read_website — fetch one URL (pages=1, the default) or crawl a whole
  same-origin section (pages=3-10) and get back clean Markdown plus the page
  title and outbound links. This is the workhorse.
- list_links — preview a page's title and links WITHOUT pulling full content.
  Call this first when you are unsure which pages to read, then feed the chosen
  URL into read_website. Much cheaper than a multi-page crawl for discovery.
- get_cache_status / clear_cache — inspect or reset the on-disk fetch cache.

Recommended workflow for reading a docs section:
1. list_links(url) to see the table of contents.
2. read_website(url, pages=N) on the most relevant entry point.

Tuning:
- pages: 1 for a single page; raise it (max 20) to follow same-origin links
  via breadth-first crawl. Multi-page crawls report progress as they run.
- max_chars: caps the returned characters (default 50000) to protect the
  context window. Set 0 for unlimited.
- output: 'markdown' (default) for reading, 'json' for structured
  title+links+markdown, 'both' to get the rendered text and the JSON payload.

This is a content-extraction tool, not a scraper: do not use it to bypass
access controls or to bulk-harvest sites. Pages behind a paywall or login are
detected and reported rather than circumvented.
"""

# Build authentication (bearer token via MCP_API_KEY). Fail-fast in HTTP mode.
_auth = None
if settings.mcp_api_key:
    _auth = BearerTokenVerifier(api_key=settings.mcp_api_key.get_secret_value())
elif settings.transport == "http":
    raise SystemExit(
        "MCP_API_KEY is required in HTTP mode. Refusing to start "
        "an unauthenticated server."
    )

mcp = FastMCP("read-website-fast", instructions=SERVER_INSTRUCTIONS, auth=_auth)


class OutputFormat(str, Enum):
    markdown = "markdown"
    json = "json"
    both = "both"


class ReadResult(BaseModel):
    """Structured result of reading or crawling one or more web pages."""

    url: str = Field(description="The (normalized) URL that was read")
    markdown: str = Field(
        default="",
        description=(
            "Clean Markdown content. For multi-page crawls, pages are "
            "concatenated with source markers. Empty when output='json' or on "
            "a hard failure."
        ),
    )
    title: str | None = Field(default=None, description="Page title of the entry URL")
    links: list[str] = Field(
        default_factory=list,
        description="Outbound links discovered while reading (de-duplicated)",
    )
    error: str | None = Field(
        default=None,
        description="Error or warning message; null on full success",
    )
    pages_requested: int = Field(
        default=1, description="Number of pages requested for the crawl"
    )
    pages_fetched: int = Field(
        default=0, description="Number of pages successfully fetched"
    )
    pages_failed: int = Field(
        default=0, description="Number of pages that failed to load"
    )


class LinksResult(BaseModel):
    """Structured result of a lightweight link-discovery pass."""

    url: str = Field(description="The (normalized) URL that was inspected")
    title: str | None = Field(default=None, description="Page title")
    links: list[str] = Field(
        default_factory=list, description="Outbound links discovered on the page"
    )
    link_count: int = Field(default=0, description="Number of links returned")
    error: str | None = Field(default=None, description="Error message; null on success")


class CacheStatus(BaseModel):
    """On-disk fetch cache statistics."""

    cache_dir: str = Field(description="Filesystem path of the cache directory")
    cache_size: int = Field(default=0, description="Total cache size in bytes")
    cache_files: int = Field(default=0, description="Number of files in the cache")
    cache_size_formatted: str = Field(
        default="0.00 MB", description="Human-readable cache size"
    )
    error: str | None = Field(default=None, description="Error message; null on success")


class CacheClearResult(BaseModel):
    """Outcome of clearing the on-disk cache."""

    status: str = Field(description="'success' or 'error'")
    message: str = Field(description="Human-readable outcome message")


@mcp.tool(
    tags={"read"},
    annotations={
        "title": "Read Website",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
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
    ctx: Context | None = None,
) -> ReadResult:
    """Fetch a web page and return clean Markdown. Handles JavaScript-rendered sites.

    Use pages=1 (default) for a single URL. Increase pages to follow same-origin
    links via BFS crawl (e.g. pages=5 to read an entire docs section).

    Use output='json' when you need structured data including the page title and
    all outbound links — useful for deciding what to crawl next.

    Tip: call list_links first to preview available pages before a multi-page crawl.

    Returns a structured ReadResult (url, markdown, title, links, error, and
    crawl page counts). The 'output' argument controls whether 'markdown' is
    populated: 'json' omits it, 'markdown'/'both' include it.
    """
    progress = None
    if ctx is not None:
        if pages > 1:
            await ctx.info(f"Crawling up to {pages} same-origin pages from {url}")
        else:
            await ctx.info(f"Reading {url}")

        async def progress(fetched: int, total: int, current_url: str) -> None:
            await ctx.report_progress(progress=fetched, total=total)
            await ctx.debug(f"Fetched {fetched}/{total}: {current_url}")

    result = await crawl_website(
        url,
        max_pages=pages,
        timeout=timeout_seconds * 1000,
        max_chars=max_chars,
        progress=progress,
    )

    if ctx is not None:
        if result.error:
            await ctx.warning(result.error)
        else:
            await ctx.info(
                f"Done: {result.pages_fetched} page(s) fetched, "
                f"{len(result.links)} link(s) found"
            )

    include_markdown = output in (OutputFormat.markdown, OutputFormat.both)

    # Raise only on a hard failure with no usable content in markdown mode,
    # preserving the original behavior.
    if (
        output == OutputFormat.markdown
        and result.error
        and not result.markdown
    ):
        raise ValueError(f"Failed to fetch content: {result.error}")

    return ReadResult(
        url=url,
        markdown=result.markdown if include_markdown else "",
        title=result.title,
        links=result.links or [],
        error=result.error,
        pages_requested=result.pages_requested,
        pages_fetched=result.pages_fetched,
        pages_failed=result.pages_failed,
    )


@mcp.tool(
    tags={"read"},
    annotations={
        "title": "List Links",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
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
) -> LinksResult:
    """Returns the page title and all outbound links without returning full page content.

    Use this before read_website(pages=N) to preview what pages are available
    and select relevant ones. Much cheaper than a full crawl for link discovery.
    """
    result = await list_page_links(
        url,
        same_origin_only=same_origin_only,
        timeout=timeout_seconds * 1000,
    )
    links = result.get("links", []) or []
    return LinksResult(
        url=result.get("url", url),
        title=result.get("title"),
        links=links,
        link_count=result.get("link_count", len(links)),
        error=result.get("error"),
    )


def _read_cache_status() -> CacheStatus:
    """Compute cache statistics (shared by tool + resource)."""
    cache_dir = settings.cache_dir
    try:
        if not cache_dir.exists():
            return CacheStatus(cache_dir=str(cache_dir))

        files = list(cache_dir.iterdir())
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        return CacheStatus(
            cache_dir=str(cache_dir),
            cache_size=total_size,
            cache_files=len(files),
            cache_size_formatted=f"{total_size / 1024 / 1024:.2f} MB",
        )
    except Exception as e:
        return CacheStatus(
            cache_dir=str(cache_dir),
            error=f"Failed to get cache status: {e}",
        )


@mcp.tool(
    tags={"cache-admin"},
    annotations={
        "title": "Cache Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_cache_status() -> CacheStatus:
    """Returns cache size and file count. Use before deciding whether to re-fetch a URL."""
    return _read_cache_status()


@mcp.tool(
    tags={"cache-admin"},
    annotations={
        "title": "Clear Cache",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def clear_cache(ctx: Context | None = None) -> CacheClearResult:
    """Clears the on-disk cache. Use when stale content is suspected or cache is too large."""
    try:
        if ctx is not None:
            await ctx.info(f"Clearing cache at {settings.cache_dir}")
        shutil.rmtree(settings.cache_dir, ignore_errors=True)
        return CacheClearResult(status="success", message="Cache cleared successfully")
    except Exception as e:
        return CacheClearResult(status="error", message=str(e))


# ---------------------------------------------------------------------------
# Resources: readable reference/context data (no side effects).
# ---------------------------------------------------------------------------


@mcp.resource(
    "readwebsite://cache/status",
    name="Cache status",
    description="Current on-disk fetch-cache size and file count.",
    mime_type="application/json",
    tags={"cache-admin"},
)
def cache_status_resource() -> CacheStatus:
    """Expose cache statistics as a readable resource (context, not an action)."""
    return _read_cache_status()


@mcp.resource(
    "readwebsite://config",
    name="Server config",
    description="Effective runtime configuration and operating limits.",
    mime_type="application/json",
    tags={"config"},
)
def config_resource() -> dict:
    """Effective configuration and the hard limits enforced by the crawler."""
    from mcp_read_website import crawler as _crawler

    return {
        "service": "read-website-fast",
        "version": _version,
        "transport": settings.transport,
        "cache_dir": str(settings.cache_dir),
        "auth_required": settings.mcp_api_key is not None,
        "limits": {
            "max_pages": 20,
            "min_timeout_seconds": 5,
            "max_timeout_seconds": 120,
            "default_max_chars": 50000,
            "max_chars_ceiling": 500000,
            "max_page_chars": _crawler.MAX_PAGE_CHARS,
            "max_total_chars": _crawler.MAX_TOTAL_CHARS,
            "max_crawl_seconds": _crawler.MAX_CRAWL_SECONDS,
            "max_concurrent_browsers": 3,
            "inter_request_delay_seconds": _crawler.INTER_REQUEST_DELAY,
        },
    }


@mcp.resource(
    "readwebsite://usage",
    name="Usage guide",
    description="How to choose between the tools and tune crawl parameters.",
    mime_type="text/markdown",
    tags={"config"},
)
def usage_resource() -> str:
    """Human/LLM-readable usage guidance (mirrors the server instructions)."""
    return SERVER_INSTRUCTIONS


# ---------------------------------------------------------------------------
# Prompts: guided multi-step workflows.
# ---------------------------------------------------------------------------


@mcp.prompt(
    name="read_docs_section",
    description="Guide: preview a page's links, then crawl the relevant section into Markdown.",
    tags={"read"},
)
def read_docs_section(
    url: Annotated[str, Field(description="Entry URL of the docs section to read")],
    topic: Annotated[
        str, Field(description="What you are trying to learn or find")
    ] = "",
) -> str:
    """Return a prompt that walks the model through the preview-then-crawl pattern."""
    topic_line = f' focused on: "{topic}"' if topic else ""
    return (
        f"I want to read the documentation section at {url}{topic_line}.\n\n"
        "Follow this workflow:\n"
        f"1. Call list_links(url=\"{url}\") to preview the available pages "
        "(title + same-origin links). Do NOT fetch full content yet.\n"
        "2. From those links, pick the entry point and an appropriate `pages` "
        "value (1 for a single page, 3-10 to read a whole section; max 20).\n"
        f"3. Call read_website(url=..., pages=N) to pull the clean Markdown. "
        "Keep max_chars at the default unless you need more.\n"
        "4. Summarize the answer and cite the source URLs from the result's "
        "`links`/source markers.\n\n"
        "Prefer the smallest crawl that answers the question to stay "
        "token-efficient."
    )


@mcp.prompt(
    name="summarize_page",
    description="Guide: read a single URL and produce a concise, structured summary.",
    tags={"read"},
)
def summarize_page(
    url: Annotated[str, Field(description="URL of the page to summarize")],
) -> str:
    """Return a prompt for a single-page read + structured summary."""
    return (
        f"Read {url} and summarize it.\n\n"
        f"1. Call read_website(url=\"{url}\", pages=1).\n"
        "2. If the result has an `error` indicating a paywall or login wall, "
        "say so plainly rather than guessing the content.\n"
        "3. Otherwise produce: a one-line TL;DR, 3-6 key points, and any "
        "notable links from the result's `links`.\n"
        "Keep it concise and faithful to the source."
    )


from datetime import datetime, timezone as _tz  # noqa: E402
from starlette.requests import Request as _SReq  # noqa: E402
from starlette.responses import JSONResponse as _SResp  # noqa: E402

_start_time = datetime.now(_tz.utc)

try:
    from mcp_read_website import __version__ as _version
except ImportError:
    _version = "0.1.0"


@mcp.custom_route("/health", methods=["GET"])
async def _health(request: _SReq) -> _SResp:
    return _SResp({
        "status": "healthy",
        "service": "read-website-fast",
        "version": _version,
        "upstream_reachable": True,
        "uptime_seconds": int((datetime.now(_tz.utc) - _start_time).total_seconds()),
    })


@mcp.custom_route("/healthz", methods=["GET"])
async def _healthz(request: _SReq) -> _SResp:
    return await _health(request)


def main() -> None:
    """Entry point for the mcp-read-website-fast server."""
    if settings.transport == "http":
        mcp.run(
            transport="streamable-http",
            host=settings.host,
            port=settings.port,
            stateless_http=True,
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
