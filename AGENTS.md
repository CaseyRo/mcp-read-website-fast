# Agent Notes

Architectural notes for coding agents working on `mcp-read-website-fast`.
For full guidance see [`CLAUDE.md`](./CLAUDE.md); this file is the short version.

## What this is

A Python 3.12 [FastMCP](https://github.com/jlowin/fastmcp) server that turns web
pages into clean, token-efficient Markdown for LLM/RAG pipelines. Content is
fetched and rendered with [Crawl4AI](https://github.com/unclecode/crawl4ai)
(Playwright/Chromium), then stripped to article content with Mozilla Readability
and converted to Markdown via `html2text`.

**This is a content-extraction tool, not a scraper.** Do not add bulk-harvesting
features or anything that bypasses access controls.

## Modules

- `mcp_read_website/server.py` — FastMCP app: tools, resources, prompts, `/health`, entry point (`main`).
- `mcp_read_website/crawler.py` — Crawl4AI wrapper: single-page + multi-page BFS, link discovery, SSRF guards, safety limits.
- `mcp_read_website/config.py` — Pydantic Settings (`TRANSPORT`, `HOST`, `PORT`, `MCP_API_KEY`, `cache_dir`).
- `mcp_read_website/auth.py` — Bearer-token verifier (timing-safe compare of `MCP_API_KEY`).

## Tools / surface

- `read_website` — fetch one URL or BFS-crawl a same-origin section (`pages` 1-20); returns a structured `ReadResult`.
- `list_links` — preview title + outbound links without pulling full content.
- `get_cache_status` / `clear_cache` — inspect / reset the on-disk fetch cache (tagged `cache-admin`).
- Resources: `readwebsite://config`, `readwebsite://cache/status`, `readwebsite://usage`.
- Prompts: `read_docs_section`, `summarize_page`.

## Transport

- Two transports: `stdio` (default, for local MCP clients) and `http` (streamable HTTP, for Docker/remote).
- HTTP mode is `stateless_http` and **fails fast** if `MCP_API_KEY` is unset — it refuses to start unauthenticated.
- HTTP serves `GET /health` and `/healthz` for container health checks.

## Protocol nuances

- Only `http`/`https` URLs are accepted; private/loopback/link-local/reserved IPs are blocked (SSRF protection).
- Same-origin (scheme + netloc) crawling by default; HTTP→HTTPS downgrades are filtered out.
- Pages behind paywalls/login walls are detected and reported, not circumvented.
- Safety limits live in `crawler.py`: 512 KB/page, 2 MB total, max 20 pages, 120 s overall timeout, max 3 concurrent browsers, 500 ms inter-request delay.

## Debugging

- Run stdio: `uv run mcp-read-website-fast`
- Run HTTP: `TRANSPORT=http MCP_API_KEY=dev uv run mcp-read-website-fast` (port 8000)
- Tests: `uv run pytest -m "not live"` (no network) or `uv run pytest -v` (includes live sites).
- Lint/format: `uv run ruff check .` / `uv run ruff format .`

## Docker

- `docker compose up --build` builds the single-stage Python image (Crawl4AI + Playwright/Chromium, ~500 MB+).
- Runs as a non-root `mcp` user; HTTP transport; cache persisted via the `fastmcp-data` volume.
- First crawl pays browser-startup latency.

## Maintenance

Keep this file accurate. When architecture changes, update it and `CLAUDE.md` together.
