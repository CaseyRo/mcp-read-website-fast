# mcp-read-website-fast

A fast, token-efficient web content extractor that converts web pages to clean Markdown. Built for LLM and RAG pipelines as an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server.

> **This is a content extraction tool, not a web scraper.** It is designed for reading and understanding web pages — documentation, articles, reference material — not for bulk data harvesting, competitive scraping, or circumventing access controls. Please use responsibly and respect website terms of service.

## What It Does

- Fetches web pages and converts them to clean, structured Markdown
- Handles JavaScript-rendered content (Playwright-based browser)
- Multi-page crawling via BFS link following (same-origin)
- Built-in caching for repeated requests
- Bearer token authentication for secure deployment
- Runs as an MCP server (stdio or HTTP transport)

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install & Run

```bash
# Clone and install
git clone https://github.com/just-every/mcp-read-website-fast.git
cd mcp-read-website-fast
uv sync

# Run (stdio transport — for MCP clients like Claude Desktop)
uv run mcp-read-website-fast

# Run (HTTP transport — for remote/Docker deployment)
TRANSPORT=http uv run mcp-read-website-fast
```

### Docker

```bash
docker compose up --build
```

The server will be available at `http://localhost:8010/mcp`.

## MCP Tools

### `read_website`

Fetch a web page and return clean Markdown.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | *required* | HTTP/HTTPS URL to fetch |
| `pages` | int (1-20) | 1 | Number of same-origin pages to crawl via BFS |
| `output` | enum | `"markdown"` | `"markdown"`, `"json"`, or `"both"` |
| `timeout_seconds` | int (5-120) | 30 | Per-page timeout. Increase for JS-heavy sites |
| `max_chars` | int (0-500000) | 50000 | Max characters returned. 0 = unlimited |

**Examples:**
```
# Read a single page
read_website(url="https://docs.example.com/api")

# Crawl a docs section (5 pages)
read_website(url="https://docs.example.com/api", pages=5)

# Get structured data with links for crawl planning
read_website(url="https://example.com", output="json")

# Increase timeout for slow sites
read_website(url="https://heavy-js-site.com", timeout_seconds=60)
```

### `list_links`

Preview all outbound links from a page without fetching full content. Use before `read_website(pages=N)` to pick relevant pages.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | *required* | URL to extract links from |
| `same_origin_only` | bool | `true` | Only return same-domain links |
| `timeout_seconds` | int (5-120) | 30 | Timeout in seconds |

### `get_cache_status`

Returns cache size and file count.

### `clear_cache`

Clears the on-disk cache. Use when stale content is suspected.

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | `stdio` or `http` |
| `HOST` | `127.0.0.1` | Bind address (use `0.0.0.0` for Docker) |
| `PORT` | `8000` | HTTP port |
| `MCP_API_KEY` | *(none)* | Bearer token for authentication |

## MCP Client Configuration

### Claude Desktop / Claude Code (stdio)

```json
{
  "mcpServers": {
    "read-website-fast": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-read-website-fast", "run", "mcp-read-website-fast"]
    }
  }
}
```

### Remote HTTP (with auth)

```json
{
  "mcpServers": {
    "read-website-fast": {
      "url": "https://your-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}
```

## Development

```bash
# Install with dev dependencies
uv sync

# Run tests (unit + server tests only, no network)
uv run pytest -m "not live"

# Run all tests including live integration tests
uv run pytest -v

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

### Test Structure

| File | What it tests | Network? |
|------|---------------|----------|
| `tests/test_crawler.py` | Link extraction, same-origin filtering | No |
| `tests/test_server.py` | Tool registration, params, schema | No |
| `tests/test_live.py` | Real sites: The Verge, Medium, GitHub, edge cases | Yes |

### Project Structure

```
mcp_read_website/
  server.py        # FastMCP app — tools, entry point
  crawler.py       # Crawl4AI wrapper — crawling + link extraction
  config.py        # Pydantic Settings
  auth.py          # Bearer token auth
tests/
  test_crawler.py  # Unit tests
  test_server.py   # Server registration tests
  test_live.py     # Live integration tests
```

## Deployment

### Docker Compose

```bash
# Set API key
echo "MCP_API_KEY=your-secret-key" > .env

# Build and run
docker compose up --build -d
```

### Komodo (CDIT infrastructure)

The `komodo.toml` is pre-configured for deployment to the CDIT server fleet. Push to `main` to trigger auto-deployment.

## Responsible Use

This tool is intended for:
- Reading documentation and reference material
- Analyzing publicly available web content
- Gathering information for research and summarization
- Powering RAG pipelines with web-sourced context

This tool is **not** intended for:
- Bulk scraping or data harvesting
- Circumventing paywalls or access controls
- Competitive intelligence scraping
- Any use that violates website terms of service

The tool respects `robots.txt` when configured to do so. Please be mindful of rate limits and server load when using multi-page crawling.

## License

MIT
