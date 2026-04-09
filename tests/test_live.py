"""Live integration tests against real websites.

These tests hit real URLs and require network access + Playwright browsers.
Run with: uv run pytest tests/test_live.py -v
Skip with: uv run pytest -m "not live"
"""

import pytest

from mcp_read_website.crawler import crawl_website, list_page_links, CrawlResult

# Mark all tests in this module as live (requires network + browser)
pytestmark = pytest.mark.live


def _assert_valid_result(result: CrawlResult, min_length: int = 100):
    """Common assertions for a successful crawl."""
    assert result.markdown, "Expected non-empty markdown"
    assert len(result.markdown) >= min_length, (
        f"Expected at least {min_length} chars, got {len(result.markdown)}"
    )
    assert result.error is None or result.markdown, "Error with no content"


class TestSimpleSites:
    """Test against simple, stable sites that should always work."""

    @pytest.mark.asyncio
    async def test_example_com(self):
        result = await crawl_website("https://example.com")
        _assert_valid_result(result, min_length=50)
        assert result.title is not None

    @pytest.mark.asyncio
    async def test_httpbin_html(self):
        result = await crawl_website("https://httpbin.org/html")
        _assert_valid_result(result, min_length=100)
        assert "Herman Melville" in result.markdown or "Moby" in result.markdown


class TestDifficultSites:
    """Test against JS-heavy and paywall-adjacent sites."""

    @pytest.mark.asyncio
    async def test_theverge_article(self):
        """The Verge uses heavy JS rendering and complex layouts."""
        result = await crawl_website(
            "https://www.theverge.com",
            max_pages=1,
            timeout=60000,
        )
        _assert_valid_result(result, min_length=200)

    @pytest.mark.asyncio
    async def test_medium_article(self):
        """Medium uses JS rendering and has paywall/interstitials."""
        result = await crawl_website(
            "https://medium.com/about",
            max_pages=1,
            timeout=60000,
        )
        _assert_valid_result(result, min_length=100)

    @pytest.mark.asyncio
    async def test_github_readme(self):
        """GitHub renders READMEs dynamically."""
        result = await crawl_website(
            "https://github.com/unclecode/crawl4ai",
            max_pages=1,
            timeout=60000,
        )
        _assert_valid_result(result, min_length=200)


class TestMultiPage:
    """Test multi-page BFS crawling."""

    @pytest.mark.asyncio
    async def test_multi_page_crawl(self):
        """Crawl example.com with 2 pages — should find and follow links."""
        result = await crawl_website(
            "https://example.com",
            max_pages=2,
            timeout=60000,
        )
        _assert_valid_result(result, min_length=50)

    @pytest.mark.asyncio
    async def test_max_pages_respected(self):
        """Ensure we never exceed max_pages."""
        result = await crawl_website(
            "https://httpbin.org/html",
            max_pages=1,
        )
        source_count = result.markdown.count("<!-- Source:")
        assert source_count <= 1


class TestListLinks:
    """Test the list_links link discovery tool."""

    @pytest.mark.asyncio
    async def test_list_links_returns_links(self):
        result = await list_page_links("https://example.com")
        assert "url" in result
        assert "links" in result
        assert "link_count" in result
        assert isinstance(result["links"], list)

    @pytest.mark.asyncio
    async def test_list_links_same_origin_filter(self):
        result = await list_page_links(
            "https://example.com",
            same_origin_only=True,
        )
        for link in result["links"]:
            assert "example.com" in link

    @pytest.mark.asyncio
    async def test_list_links_returns_title(self):
        result = await list_page_links("https://example.com")
        assert result.get("title") is not None


class TestTruncation:
    """Test max_chars truncation."""

    @pytest.mark.asyncio
    async def test_truncation_applied(self):
        result = await crawl_website(
            "https://example.com",
            max_chars=100,
        )
        # Should be truncated with a note
        assert "truncated" in result.markdown.lower()

    @pytest.mark.asyncio
    async def test_no_truncation_when_zero(self):
        result = await crawl_website(
            "https://example.com",
            max_chars=0,
        )
        assert "truncated" not in result.markdown.lower()


class TestEdgeCases:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_nonexistent_domain(self):
        result = await crawl_website("https://this-domain-does-not-exist-12345.com")
        assert result.error is not None or result.markdown == ""

    @pytest.mark.asyncio
    async def test_404_page(self):
        result = await crawl_website("https://httpbin.org/status/404")
        assert isinstance(result, CrawlResult)

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Very short timeout should fail gracefully."""
        result = await crawl_website(
            "https://httpbin.org/delay/10",
            timeout=1000,
        )
        assert isinstance(result, CrawlResult)
