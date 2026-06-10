"""Tests for the MCP server tool and resource registration."""

import pytest

import mcp_read_website.server as server_module
from mcp_read_website.crawler import CrawlResult
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
    async def test_read_website_returns_structured_output(self):
        """read_website should advertise a structured output schema."""
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "read_website")
        mcp_tool = tool.to_mcp_tool()
        assert mcp_tool.outputSchema is not None
        props = mcp_tool.outputSchema.get("properties", {})
        # Existing top-level fields must remain present.
        for field in ("url", "markdown", "title", "links", "error"):
            assert field in props

    @pytest.mark.asyncio
    async def test_reference_resources_registered(self):
        """Cache status, config, and usage are exposed as readable resources."""
        resources = await mcp.list_resources()
        uris = {str(r.uri) for r in resources}
        assert "readwebsite://cache/status" in uris
        assert "readwebsite://config" in uris
        assert "readwebsite://usage" in uris

    @pytest.mark.asyncio
    async def test_prompts_registered(self):
        """Guided workflow prompts are available."""
        prompts = await mcp.list_prompts()
        names = {p.name for p in prompts}
        assert "read_docs_section" in names
        assert "summarize_page" in names

    @pytest.mark.asyncio
    async def test_server_name(self):
        assert mcp.name == "read-website-fast"

    @pytest.mark.asyncio
    async def test_server_has_instructions(self):
        assert mcp.instructions
        assert "read_website" in mcp.instructions


class TestBackwardCompat:
    """Guard the wire-compatible behavior that existing clients depend on."""

    @pytest.mark.asyncio
    async def test_cache_status_emits_camelcase_keys(self):
        """get_cache_status must emit the original camelCase wire keys."""
        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "get_cache_status")

        # Output schema must advertise the original camelCase keys.
        mcp_tool = tool.to_mcp_tool()
        schema_props = (mcp_tool.outputSchema or {}).get("properties", {})
        for key in ("cacheSize", "cacheFiles", "cacheSizeFormatted"):
            assert key in schema_props, f"missing camelCase key {key} in output schema"

        # Actual structured data must also use the camelCase keys.
        result = await tool.run({})
        structured = result.structured_content
        for key in ("cacheSize", "cacheFiles", "cacheSizeFormatted"):
            assert key in structured, f"missing camelCase key {key} in structured output"
        # snake_case variants must NOT leak onto the wire (back-compat).
        for key in ("cache_size", "cache_files", "cache_size_formatted"):
            assert key not in structured, f"snake_case key {key} leaked onto the wire"
        # New additive key is allowed.
        assert "cache_dir" in structured

    @pytest.mark.asyncio
    async def test_read_website_json_includes_markdown(self, monkeypatch):
        """output='json' must include the markdown content, matching main."""

        async def fake_crawl(url, **kwargs):
            return CrawlResult(
                markdown="# Hello\n\nbody text",
                title="Hello",
                links=["https://example.com/a"],
                error=None,
                pages_requested=1,
                pages_fetched=1,
                pages_failed=0,
            )

        monkeypatch.setattr(server_module, "crawl_website", fake_crawl)

        tools = await mcp.list_tools()
        tool = next(t for t in tools if t.name == "read_website")

        result = await tool.run({"url": "https://example.com", "output": "json"})
        structured = result.structured_content
        assert structured["markdown"] == "# Hello\n\nbody text"
        assert structured["title"] == "Hello"
        assert structured["links"] == ["https://example.com/a"]
