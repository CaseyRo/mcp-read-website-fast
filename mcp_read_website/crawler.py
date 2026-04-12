"""Crawl4AI wrapper for single-page and multi-page web content extraction."""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import re
import socket
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin

import html2text
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from readability import Document

logger = logging.getLogger(__name__)

# Safety limits
MAX_PAGE_CHARS = 512_000  # 512 KB per page
MAX_TOTAL_CHARS = 2_000_000  # 2 MB total output
MAX_QUEUE_FACTOR = 20  # never queue more than 20x max_pages links
MAX_CRAWL_SECONDS = 120  # 2 minute overall crawl timeout
INTER_REQUEST_DELAY = 0.5  # 500ms between requests to same domain

# Concurrency: max 3 simultaneous browser instances across all requests
crawl_semaphore = asyncio.Semaphore(3)

# HTML to markdown converter (shared instance)
_h2t = html2text.HTML2Text()
_h2t.ignore_links = False
_h2t.ignore_images = True
_h2t.body_width = 0

# Shared browser config — TLS validation enforced, debugging port disabled
_browser_config = BrowserConfig(
    headless=True,
    verbose=False,
    ignore_https_errors=False,
    extra_args=[
        "--remote-debugging-port=0",
        "--no-sandbox",              # Required for non-root Docker containers
        "--disable-dev-shm-usage",   # Prevent /dev/shm OOM in constrained containers
    ],
)


@dataclass
class CrawlResult:
    """Result of a website crawl."""

    markdown: str
    title: str | None = None
    links: list[str] = field(default_factory=list)
    error: str | None = None


_PAYWALL_PATTERNS = re.compile(
    r"subscribe|sign[\s-]?in|log[\s-]?in|create.*account|paywall|premium\s+content"
    r"|you.ve reached|reading limit|free articles|member(?:ship)?[\s-](?:required|only)"
    r"|continue reading.*(?:subscribe|sign[\s-]?in)",
    re.IGNORECASE,
)


def _diagnose_failure(url: str, result=None) -> str:
    """Return a specific error message when a page fails to load."""
    html = ""
    if result is not None:
        html = result.html or ""

    if html and _PAYWALL_PATTERNS.search(html):
        return (
            "This page appears to require a subscription or login. "
            "The site returned a paywall or sign-in prompt instead of article content."
        )

    return "Failed to load page. The site may be down or blocking automated access."


def validate_url(url: str) -> str:
    """Validate and normalize a URL. Raises ValueError for unsafe URLs."""
    # Auto-add scheme if missing
    if not url.startswith(("http://", "https://", "file://", "ftp://")):
        url = f"https://{url}"

    parsed = urlparse(url)

    # Enforce http/https only
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"Only http/https URLs are allowed, got: {parsed.scheme!r}. "
            f"Did you mean https://{parsed.netloc or url}?"
        )

    if not parsed.hostname:
        raise ValueError(f"Invalid URL: no hostname found in {url!r}")

    # Block private/loopback/link-local IP ranges (SSRF protection)
    try:
        resolved_ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        if resolved_ip.is_private or resolved_ip.is_loopback or resolved_ip.is_link_local or resolved_ip.is_reserved:
            raise ValueError(
                f"Access to private/internal networks is not allowed: {parsed.hostname} "
                f"resolves to {resolved_ip}"
            )
    except socket.gaierror:
        pass  # DNS resolution will fail naturally during crawl

    return url


def extract_markdown_links(markdown: str, base_url: str) -> list[str]:
    """Extract all HTTP/HTTPS links from markdown content."""
    links: list[str] = []

    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", markdown):
        url = match.group(2)
        if url and not url.startswith(("#", "mailto:", "tel:")):
            links.append(url)

    for match in re.finditer(r"https?://[^\s<>)\]]+", markdown):
        links.append(match.group(0))

    absolute: list[str] = []
    for link in links:
        try:
            if link.startswith(("http://", "https://")):
                absolute.append(link)
            else:
                resolved = urljoin(base_url, link)
                # Only queue http/https links (prevent file://, ftp:// injection)
                if resolved.startswith(("http://", "https://")):
                    absolute.append(resolved)
        except Exception:
            continue

    return list(dict.fromkeys(absolute))


def filter_same_origin_links(links: list[str], base_url: str) -> list[str]:
    """Filter links to same scheme + netloc (prevents HTTP downgrade)."""
    try:
        parsed_base = urlparse(base_url)
        base_origin = (parsed_base.scheme, parsed_base.netloc)
    except Exception:
        return []

    result: list[str] = []
    for link in links:
        try:
            p = urlparse(link)
            if (p.scheme, p.netloc) == base_origin:
                result.append(link)
        except Exception:
            continue
    return result


def _extract_links_from_result(result, current_url: str) -> list[str]:
    """Extract links from a crawl4ai CrawlResult, with markdown fallback."""
    links: list[str] = []

    if result.links and isinstance(result.links, dict):
        internal = result.links.get("internal", [])
        for link_obj in internal:
            href = link_obj.get("href", "") if isinstance(link_obj, dict) else str(link_obj)
            if href and href.startswith(("http://", "https://")):
                links.append(href)

    if not links:
        md = result.markdown
        md_text = md.raw_markdown if hasattr(md, "raw_markdown") else (str(md) if md else "")
        if md_text:
            links = extract_markdown_links(md_text, current_url)

    return links


def _get_markdown_text(result) -> str:
    """Extract clean article content using Mozilla Readability, with fallback.

    Uses Readability to strip nav, sidebars, footers, and boilerplate from
    the raw HTML, then converts the clean HTML to markdown via html2text.
    Falls back to crawl4ai's raw markdown if Readability produces nothing.
    """
    # Try Readability extraction from raw HTML first
    raw_html = result.html or ""
    if raw_html:
        try:
            doc = Document(raw_html)
            clean_html = doc.summary()
            if clean_html:
                text = _h2t.handle(clean_html).strip()
                if len(text) > 50:  # Readability produced meaningful content
                    if len(text) > MAX_PAGE_CHARS:
                        text = text[:MAX_PAGE_CHARS] + "\n\n<!-- Page content truncated at 512KB -->"
                    return text
        except Exception:
            logger.debug("Readability extraction failed, falling back to raw markdown")

    # Fallback: use crawl4ai's raw markdown
    md = result.markdown
    if hasattr(md, "raw_markdown"):
        text = md.raw_markdown or ""
    else:
        text = str(md) if md else ""

    if len(text) > MAX_PAGE_CHARS:
        text = text[:MAX_PAGE_CHARS] + "\n\n<!-- Page content truncated at 512KB -->"
    return text


def _get_title(result) -> str | None:
    """Extract page title, preferring Readability's cleaned title."""
    raw_html = result.html or ""
    if raw_html:
        try:
            doc = Document(raw_html)
            title = doc.short_title()
            if title:
                return title
        except Exception:
            pass
    return result.metadata.get("title") if result.metadata else None


async def list_page_links(
    url: str,
    *,
    same_origin_only: bool = True,
    timeout: int = 30000,
) -> dict:
    """Fetch a page and return only its title and links (no full content)."""
    url = validate_url(url)
    logger.info("list_links url=%s", url)

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        cache_mode=CacheMode.ENABLED,
        page_timeout=timeout,
    )

    try:
        async with crawl_semaphore:
            async with AsyncWebCrawler(config=_browser_config) as crawler:
                result = await crawler.arun(url, config=crawl_config)

                if not result.success:
                    return {
                        "url": url,
                        "title": None,
                        "links": [],
                        "error": _diagnose_failure(url, result),
                    }

                title = _get_title(result)
                links = _extract_links_from_result(result, url)

                if same_origin_only:
                    links = filter_same_origin_links(links, url)

                return {
                    "url": url,
                    "title": title,
                    "link_count": len(links),
                    "links": links,
                }
    except Exception as exc:
        logger.exception("Error in list_page_links for %s", url)
        return {"url": url, "title": None, "links": [], "error": f"Failed to load page: {exc}"}


async def _do_crawl(
    url: str,
    *,
    max_pages: int = 1,
    timeout: int = 30000,
    max_chars: int = 0,
) -> CrawlResult:
    """Internal crawl implementation with BFS link following."""
    visited: set[str] = set()
    to_visit: list[str] = [url]
    to_visit_set: set[str] = {url}
    all_results: list[dict] = []
    queue_limit = max_pages * MAX_QUEUE_FACTOR

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        cache_mode=CacheMode.ENABLED,
        page_timeout=timeout,
    )

    async with AsyncWebCrawler(config=_browser_config) as crawler:
        while to_visit and len(all_results) < max_pages:
            current_url = to_visit.pop(0)

            if current_url in visited:
                continue
            visited.add(current_url)

            # Rate limit between requests to same domain
            if all_results:
                await asyncio.sleep(INTER_REQUEST_DELAY)

            try:
                result = await crawler.arun(current_url, config=crawl_config)

                if result.success:
                    md_text = _get_markdown_text(result)
                    links = _extract_links_from_result(result, current_url)

                    page = {
                        "url": current_url,
                        "markdown": md_text,
                        "title": _get_title(result),
                        "links": links,
                        "error": None,
                    }
                    all_results.append(page)

                    if len(all_results) < max_pages:
                        same_origin = filter_same_origin_links(links, current_url)
                        for link in same_origin:
                            if link not in visited and link not in to_visit_set:
                                if len(to_visit) < queue_limit:
                                    to_visit.append(link)
                                    to_visit_set.add(link)
                else:
                    all_results.append({
                        "url": current_url,
                        "markdown": "",
                        "title": None,
                        "links": [],
                        "error": _diagnose_failure(current_url, result),
                    })

            except Exception as exc:
                logger.exception("Error crawling %s", current_url)
                all_results.append({
                    "url": current_url,
                    "markdown": "",
                    "title": None,
                    "links": [],
                    "error": f"Failed to fetch page: {exc}",
                })

    if not all_results:
        return CrawlResult(markdown="", error="No results returned")

    # Collect errors
    error_pages = [p for p in all_results if p.get("error")]
    success_pages = [p for p in all_results if not p.get("error")]
    error_msg = None
    if error_pages:
        urls = ", ".join(p["url"] for p in error_pages)
        error_msg = f"Some pages had errors: {urls}"

    # Build output
    parts: list[str] = []

    # Crawl summary for multi-page
    if max_pages > 1:
        parts.append(
            f"<!-- Crawl summary: requested={max_pages}, "
            f"fetched={len(success_pages)}, "
            f"errors={len(error_pages)} -->"
        )

    # Surface errors visibly at the top
    if error_pages:
        error_lines = [f"- {p['url']}: {p['error']}" for p in error_pages]
        parts.append("**Warning: Some pages failed to load:**\n" + "\n".join(error_lines) + "\n")

    for i, page in enumerate(all_results):
        if page.get("error") and not page.get("markdown"):
            continue

        content = ""
        if i > 0 or error_pages:
            content += "\n---\n\n"
        content += f"<!-- Source: {page['url']} -->\n"
        content += page.get("markdown", "")
        parts.append(content)

    combined_markdown = "\n".join(parts)

    # Apply max_chars truncation
    effective_max = max_chars if max_chars > 0 else MAX_TOTAL_CHARS
    if len(combined_markdown) > effective_max:
        combined_markdown = combined_markdown[:effective_max]
        combined_markdown += f"\n\n---\n*Content truncated at {effective_max} characters. Use a smaller `pages` value or increase `max_chars` to see more.*"

    return CrawlResult(
        markdown=combined_markdown,
        title=all_results[0].get("title"),
        links=[link for page in all_results for link in page.get("links", [])],
        error=error_msg,
    )


async def crawl_website(
    url: str,
    *,
    max_pages: int = 1,
    timeout: int = 30000,
    max_chars: int = 0,
) -> CrawlResult:
    """Crawl a website and return clean markdown.

    Uses iterative BFS to follow same-origin links up to max_pages.
    Enforces URL validation, concurrency limits, and overall timeout.
    """
    url = validate_url(url)
    logger.info("crawl_start url=%s max_pages=%d timeout=%d", url, max_pages, timeout)

    try:
        async with crawl_semaphore:
            result = await asyncio.wait_for(
                _do_crawl(url, max_pages=max_pages, timeout=timeout, max_chars=max_chars),
                timeout=MAX_CRAWL_SECONDS,
            )
    except asyncio.TimeoutError:
        logger.warning("crawl_timeout url=%s after %ds", url, MAX_CRAWL_SECONDS)
        return CrawlResult(
            markdown="",
            error=f"Crawl timed out after {MAX_CRAWL_SECONDS}s. Try fewer pages or a shorter timeout.",
        )
    except ValueError:
        raise  # Re-raise URL validation errors
    except Exception as exc:
        logger.exception("crawl_error url=%s", url)
        return CrawlResult(markdown="", error=f"Crawl failed: {exc}")

    logger.info("crawl_complete url=%s pages=%d error=%s", url, len(result.links) > 0, result.error)
    return result
