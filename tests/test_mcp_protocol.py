"""The MCP surface over the wire: registration, annotations, a round trip, telemetry.

Everything goes through an in-memory fastmcp Client, so this is what a
framework upgrade breaks first. No network: DNS and the Crawl4AI browser are
replaced with fakes, and the real crawler code runs in between.
"""

from __future__ import annotations

import json
import socket
from types import SimpleNamespace

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_read_website import crawler
from mcp_read_website.server import mcp

EXPECTED_TOOLS = {"read_website", "list_links", "get_cache_status", "clear_cache"}

PAGE_HTML = (
    "<html><head><title>Hello Page</title></head><body><article>"
    "<h1>Hello</h1><p>" + "Readable article body text for the test. " * 10 + "</p>"
    '<a href="https://example.com/next">next</a></article></body></html>'
)


class FakeCrawler:
    """Stands in for crawl4ai.AsyncWebCrawler (no browser, no network)."""

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def arun(self, url, config=None):
        if "blocked" in url:
            return SimpleNamespace(success=False, html="Please sign in to continue")
        return SimpleNamespace(
            success=True,
            html=PAGE_HTML,
            markdown="# Hello",
            links={"internal": [{"href": "https://example.com/next"}]},
            metadata={"title": "Hello Page"},
        )


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "93.184.215.14")
    monkeypatch.setattr(crawler, "AsyncWebCrawler", FakeCrawler)


async def test_server_registers_its_tools():
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == EXPECTED_TOOLS


async def test_annotations_survive_the_wire():
    async with Client(mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    read = tools["read_website"].annotations
    assert read.read_only_hint is True
    assert read.destructive_hint is False
    assert read.open_world_hint is True
    assert tools["list_links"].annotations.read_only_hint is True
    assert tools["get_cache_status"].annotations.open_world_hint is False
    clear = tools["clear_cache"].annotations
    assert clear.read_only_hint is False
    assert clear.destructive_hint is True


async def test_read_website_round_trips_without_network(offline):
    async with Client(mcp) as client:
        result = await client.call_tool("read_website", {"url": "https://example.com"})
    data = result.structured_content
    assert data["title"] == "Hello Page"
    assert "Readable article body text" in data["markdown"]
    assert data["links"] == ["https://example.com/next"]
    assert data["pages_fetched"] == 1
    assert data["error"] is None


async def test_failed_read_raises_tool_error(offline):
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="subscription or login"):
            await client.call_tool("read_website", {"url": "https://example.com/blocked"})


async def test_private_address_raises_tool_error():
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="private/internal"):
            await client.call_tool("list_links", {"url": "http://127.0.0.1"})


async def test_call_tool_writes_one_usage_line(offline, capsys):
    async with Client(mcp) as client:
        await client.call_tool("list_links", {"url": "https://example.com"})
    lines = [
        json.loads(line)
        for line in capsys.readouterr().err.splitlines()
        if '"mcp_usage"' in line
    ]
    assert len(lines) == 1
    assert lines[0]["server"] == "read-website-fast"
    assert lines[0]["tool"] == "list_links"
    assert lines[0]["outcome"] == "ok"
    assert "protocol" in lines[0]
