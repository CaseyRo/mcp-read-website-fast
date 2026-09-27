"""Usage telemetry: one stderr JSON line per tool call."""

import json

import pytest
from fastmcp import Client

import mcp_read_website.server as server_module
from mcp_read_website.server import mcp


@pytest.mark.asyncio
async def test_call_tool_writes_usage_line(monkeypatch, capsys):
    async def fake_links(url, **kwargs):
        return {"url": url, "title": "T", "links": [], "link_count": 0}

    monkeypatch.setattr(server_module, "list_page_links", fake_links)
    async with Client(mcp) as c:
        await c.call_tool("list_links", {"url": "https://example.com"})
    lines = [json.loads(l) for l in capsys.readouterr().err.splitlines() if '"mcp_usage"' in l]
    assert len(lines) == 1
    assert lines[0]["server"] == "read-website-fast"
    assert lines[0]["tool"] == "list_links"
    assert lines[0]["outcome"] == "ok"
