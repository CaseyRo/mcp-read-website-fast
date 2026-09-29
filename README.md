# mcp-read-website-fast

A fast, token-efficient web content extractor that converts web pages to clean Markdown. Built for LLM and RAG pipelines as an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server, it is for anyone who wants an AI assistant to read documentation, articles and reference pages, including JavaScript-rendered ones, without pulling raw HTML into the context window.

This repository is a fork of [just-every/mcp-read-website-fast](https://github.com/just-every/mcp-read-website-fast) (MIT). The original is a TypeScript/Node server; this fork is a Python rewrite on [FastMCP](https://github.com/PrefectHQ/fastmcp) 4 and [Crawl4AI](https://github.com/unclecode/crawl4ai). Credit for the idea and the original implementation goes to the upstream authors.

> **This is a content extraction tool, not a web scraper.** It is designed for reading and understanding web pages (documentation, articles, reference material), not for bulk data harvesting, competitive scraping, or circumventing access controls. Please use it responsibly and respect website terms of service.

## What it does

- Fetches web pages and converts them to clean, structured Markdown
- Handles JavaScript-rendered content (Crawl4AI with a headless Chromium browser)
- Crawls several pages of one site breadth-first (same origin only)
- Caches fetched pages on disk for repeated requests
- Blocks private, loopback and link-local addresses (SSRF protection)
- Runs as an MCP server over stdio or streamable HTTP, with bearer token authentication in HTTP mode

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- A Chromium build for Playwright (installed with one command below)
- Docker with Compose, if you want to run it as a container (the image is about 500 MB because it bundles Chromium)

## Install and run

### Local

```bash
git clone https://github.com/CaseyRo/mcp-read-website-fast.git
cd mcp-read-website-fast
uv sync
uv run playwright install chromium

# stdio transport, for local MCP clients like Claude Desktop or Claude Code
uv run mcp-read-website-fast

# HTTP transport, for remote clients (requires MCP_API_KEY)
TRANSPORT=http MCP_API_KEY=change-me uv run mcp-read-website-fast
# listens on http://127.0.0.1:8000/mcp
```

### Docker

```bash
echo "MCP_API_KEY=change-me" > .env
docker compose up --build -d
```

The Compose file builds the image from source and runs the HTTP transport. The server is available at `http://localhost:8010/mcp`. `GET /health` (and `/healthz`) returns the service status, `version` and `git_commit`; the container health check uses it. Pass `GIT_COMMIT` and `APP_VERSION` as build args so `/health` reports the running build. The Crawl4AI page cache lives in the container at `/home/mcp/.crawl4ai` and does not survive a container recreate.

## MCP client configuration

### stdio

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

### Remote HTTP

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

## Configuration

All configuration comes from environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | `stdio` or `http` (streamable HTTP, stateless). The Docker image sets `http`. |
| `HOST` | `127.0.0.1` | Bind address for HTTP. The Docker image sets `0.0.0.0`. |
| `PORT` | `8000` | HTTP port. |
| `MCP_API_KEY` | *(unset)* | Bearer token clients must send. Required when `TRANSPORT=http`. |
| `CRAWL4_AI_BASE_DIRECTORY` | `$HOME` | Crawl4AI's base directory. Its page cache (`.crawl4ai/crawl4ai.db` plus stored page bodies) is what `get_cache_status` reports and `clear_cache` empties. |
| `GIT_COMMIT` | `unknown` | Commit reported by `/health` (also a build arg). |
| `APP_VERSION` | package version | Release version reported by `/health` (build arg). |

## Authentication

In HTTP mode every request must carry `Authorization: Bearer <MCP_API_KEY>`. The token is compared in constant time. If `MCP_API_KEY` is unset in HTTP mode, the server exits at startup instead of running unauthenticated. There is no OAuth. In stdio mode the client launches the server as a local process and no token is used.

For a public deployment, put the server behind a reverse proxy or MCP gateway that terminates TLS.

## MCP tools

### `read_website`

Fetch a web page and return clean Markdown.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | *required* | HTTP or HTTPS URL to fetch |
| `pages` | int (1-20) | 1 | Number of same-origin pages to crawl breadth-first |
| `output` | enum | `"markdown"` | `"markdown"`, `"json"`, or `"both"` |
| `timeout_seconds` | int (5-120) | 30 | Per-page timeout. Increase for JS-heavy sites |
| `max_chars` | int (0-500000) | 50000 | Max characters returned. 0 means unlimited |

Returns a structured result (`url`, `markdown`, `title`, `links`, `error`, plus the crawl counts `pages_requested`, `pages_fetched` and `pages_failed`), so clients get a machine-readable output schema. Multi-page crawls report progress as each page is fetched. If nothing can be fetched (in any output mode), the call fails with a tool error that carries the diagnosis, for example a paywall or login wall; when some pages of a multi-page crawl fail, the rest is returned and the misses are reported in the `error` field.

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

Preview the outbound links of a page without fetching full content. Use it before `read_website(pages=N)` to pick relevant pages.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | *required* | URL to extract links from |
| `same_origin_only` | bool | `true` | Only return same-origin links |
| `timeout_seconds` | int (5-120) | 30 | Timeout in seconds |

### `get_cache_status`

Returns cache size and file count.

### `clear_cache`

Clears the on-disk cache. Use it when stale content is suspected.

Tools are tagged `read` (the two content tools) and `cache-admin` (`get_cache_status`, `clear_cache`), so a deployment can hide the destructive cache tool with FastMCP `include_tags` / `exclude_tags`.

## MCP resources

Readable reference data (no side effects), under the `readwebsite://` URI scheme:

| Resource | Description |
|----------|-------------|
| `readwebsite://config` | Effective runtime config and the hard limits the crawler enforces |
| `readwebsite://cache/status` | Current cache size and file count |
| `readwebsite://usage` | Guidance on choosing tools and tuning crawl parameters |

## MCP prompts

| Prompt | Purpose |
|--------|---------|
| `read_docs_section` | Preview links with `list_links`, then crawl the relevant docs section |
| `summarize_page` | Read a single URL and produce a concise, structured summary |

## Limits

Hard limits in `crawler.py`: 512 KB per page, 2 MB per crawl, 20 pages per crawl, 120 seconds overall timeout, at most 3 concurrent browser sessions, and a 500 ms delay between requests. The crawler does not check `robots.txt`, so keep multi-page crawls small and mind the load you put on other people's servers.

## Usage telemetry

A small middleware (`mcp_read_website/usage.py`) writes one JSON line per tool call to stderr with the server name, tool name, duration and outcome. It never logs arguments or results, and it sends nothing anywhere; the lines stay in your process logs.

## Development

```bash
uv sync

# Offline tests (no network)
uv run pytest -m "not live"

# All tests, including live requests to real sites
uv run pytest -v

# Lint and format
uv run ruff check .
uv run ruff format .
```

| File | What it tests | Network? |
|------|---------------|----------|
| `tests/test_crawler.py` | Link extraction, same-origin filtering, URL validation | No |
| `tests/test_server.py` | Tool registration, parameters, schemas | No |
| `tests/test_mcp_protocol.py` | The MCP surface through an in-memory client: tools, annotations, one mocked read, tool errors, usage telemetry | No |
| `tests/test_live.py` | Real sites and edge cases | Yes |

Project layout:

```
mcp_read_website/
  server.py        # FastMCP app: tools, resources, prompts, /health, entry point
  crawler.py       # Crawl4AI wrapper: crawling, link extraction, safety limits
  config.py        # Pydantic settings
  auth.py          # Bearer token verifier
  usage.py         # Usage telemetry middleware
```

`.github/workflows/ci.yml` runs one job, `test`, on every pull request and every push to `main`: `ruff check` and the offline tests, with `FASTMCP_MCP_CAMELCASE_COMPAT=false` so any leftover camelCase MCP field access fails. `main` is protected and requires `test` to pass before a pull request can merge. `.github/workflows/security.yml` runs `pip-audit` weekly and when dependencies change.

## Releases

Releases are tag-only. Every push to `main` that changes more than Markdown or tests runs `.github/workflows/release.yml`: it runs the offline tests and `pip-audit`, then pushes the next patch tag (latest `v*` tag + 1). Nothing is committed back to `main`: the version in `pyproject.toml` is static, and `CHANGELOG.md` is no longer updated automatically. No container image is published; the Compose file builds from source.

## Responsible use

This tool is intended for:
- Reading documentation and reference material
- Analyzing publicly available web content
- Gathering information for research and summarization
- Powering RAG pipelines with web-sourced context

This tool is not intended for:
- Bulk scraping or data harvesting
- Circumventing paywalls or access controls (pages behind a paywall or login are detected and reported, not bypassed)
- Competitive intelligence scraping
- Any use that violates website terms of service

## Support

If this server saves you time, you can [buy me a coffee](https://buymeacoffee.com/caseyberlin).

## License

MIT. See [LICENSE](LICENSE), which keeps the upstream copyright notice.
