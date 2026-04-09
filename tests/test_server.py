"""Tests for the MCP server tool and resource registration."""

import pytest

from mcp_read_website.server import mcp


class TestServerRegistration:
    """Verify the FastMCP server has the expected tools."""

    @pytest.mark.asyncio
    async def test_all_tools_registered(self):
        tools = await mcp.list_tools()
        tool_names = {t.name for t in tools}
        assert "read_website" in tool_names
        assert "list_links" in tool_names
        assert "get_cache_status" in tool_names
        assert "clear_cache" in tool_names

    @pytest.mark.asyncio
    async def test_read_website_params(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "read_website")
        mcp_tool = tool.to_mcp_tool()
        props = mcp_tool.inputSchema.get("properties", {})
        assert "url" in props
        assert "pages" in props
        assert "output" in props
        assert "timeout_seconds" in props
        assert "max_chars" in props

    @pytest.mark.asyncio
    async def test_read_website_url_required(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "read_website")
        mcp_tool = tool.to_mcp_tool()
        required = mcp_tool.inputSchema.get("required", [])
        assert "url" in required

    @pytest.mark.asyncio
    async def test_read_website_pages_max_is_20(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "read_website")
        mcp_tool = tool.to_mcp_tool()
        pages_schema = mcp_tool.inputSchema["properties"]["pages"]
        assert pages_schema.get("maximum") == 20

    @pytest.mark.asyncio
    async def test_list_links_params(self):
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "list_links")
        mcp_tool = tool.to_mcp_tool()
        props = mcp_tool.inputSchema.get("properties", {})
        assert "url" in props
        assert "same_origin_only" in props

    @pytest.mark.asyncio
    async def test_no_resources_registered(self):
        """Cache operations are now tools, not resources."""
        resources = await mcp.list_resources()
        assert len(resources) == 0

    @pytest.mark.asyncio
    async def test_server_name(self):
        assert mcp.name == "read-website-fast"
