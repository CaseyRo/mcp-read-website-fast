"""Tests for the crawler module."""

import pytest

from mcp_read_website.crawler import (
    extract_markdown_links,
    filter_same_origin_links,
    validate_url,
)


class TestValidateUrl:
    def test_valid_https(self):
        assert validate_url("https://example.com") == "https://example.com"

    def test_valid_http(self):
        assert validate_url("http://example.com") == "http://example.com"

    def test_auto_adds_https(self):
        assert validate_url("example.com") == "https://example.com"

    def test_rejects_file_scheme(self):
        with pytest.raises(ValueError, match="Only http/https"):
            validate_url("file:///etc/passwd")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(ValueError, match="Only http/https"):
            validate_url("ftp://files.example.com")

    def test_rejects_localhost(self):
        with pytest.raises(ValueError, match="private/internal"):
            validate_url("http://127.0.0.1")

    def test_rejects_private_ip(self):
        with pytest.raises(ValueError, match="private/internal"):
            validate_url("http://192.168.1.1")

    def test_rejects_link_local(self):
        with pytest.raises(ValueError, match="private/internal"):
            validate_url("http://169.254.169.254/latest/meta-data/")

    def test_rejects_empty_hostname(self):
        with pytest.raises(ValueError, match="no hostname"):
            validate_url("http://")


class TestExtractMarkdownLinks:
    def test_extracts_markdown_links(self):
        md = "Check [Example](https://example.com) and [Docs](https://docs.example.com/guide)"
        links = extract_markdown_links(md, "https://example.com")
        assert "https://example.com" in links
        assert "https://docs.example.com/guide" in links

    def test_extracts_bare_urls(self):
        md = "Visit https://example.com/page for more info"
        links = extract_markdown_links(md, "https://example.com")
        assert "https://example.com/page" in links

    def test_resolves_relative_urls(self):
        md = "See [About](/about) for details"
        links = extract_markdown_links(md, "https://example.com")
        assert "https://example.com/about" in links

    def test_skips_anchors_mailto_tel(self):
        md = "[Top](#top) [Email](mailto:a@b.com) [Call](tel:123)"
        links = extract_markdown_links(md, "https://example.com")
        assert len(links) == 0

    def test_rejects_file_links_in_markdown(self):
        md = "[Secret](file:///etc/passwd)"
        links = extract_markdown_links(md, "https://example.com")
        assert not any("file://" in link for link in links)

    def test_deduplicates(self):
        md = "[A](https://example.com) [B](https://example.com)"
        links = extract_markdown_links(md, "https://example.com")
        assert links.count("https://example.com") == 1

    def test_empty_markdown(self):
        links = extract_markdown_links("", "https://example.com")
        assert links == []


class TestFilterSameOriginLinks:
    def test_filters_same_origin(self):
        links = [
            "https://example.com/a",
            "https://other.com/b",
            "https://example.com/c",
        ]
        result = filter_same_origin_links(links, "https://example.com")
        assert result == ["https://example.com/a", "https://example.com/c"]

    def test_blocks_http_downgrade(self):
        """HTTP links should not match HTTPS base URL (scheme check)."""
        links = ["http://example.com/a"]
        result = filter_same_origin_links(links, "https://example.com")
        assert result == []

    def test_handles_invalid_base_url(self):
        result = filter_same_origin_links(["https://a.com"], "not-a-url")
        assert result == []

    def test_empty_links(self):
        result = filter_same_origin_links([], "https://example.com")
        assert result == []
