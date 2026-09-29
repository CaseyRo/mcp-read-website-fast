# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A fast, token-efficient web content extractor that converts web pages to clean Markdown. Designed for LLM/RAG pipelines, it provides an MCP server interface using Crawl4AI (Playwright-based) for content extraction including JavaScript-rendered pages.

**This is NOT a scraping tool.** It is designed for content extraction and understanding — reading docs, articles, and reference material for AI agents.

## Core Modules & Files

- `mcp_read_website/server.py`: FastMCP server — 4 tools (read_website, list_links, get_cache_status, clear_cache), entry point
- `mcp_read_website/crawler.py`: Crawl4AI wrapper — single-page, multi-page BFS, link discovery
- `mcp_read_website/config.py`: Pydantic Settings (transport, host, port, cache_dir, mcp_api_key)
- `mcp_read_website/auth.py`: Bearer token auth (MCP_API_KEY via SecretStr)
- `mcp_read_website/usage.py`: Usage telemetry middleware, vendored from `CDiT-infrastructure/scripts/mcp_usage_middleware.py` (do not edit here)

## Commands

### Development
```bash
uv run mcp-read-website-fast                        # Run MCP server (stdio)
TRANSPORT=http uv run mcp-read-website-fast          # Run MCP server (HTTP on port 8000)
```

### Code Quality
```bash
uv run pytest                   # Run all tests (unit + live)
uv run pytest -m "not live"     # Run unit tests only (no network)
uv run ruff check .             # Lint
uv run ruff format .            # Format
```

### Docker
```bash
docker compose up --build    # Build and run container
```

## Pre-Commit Requirements

**IMPORTANT**: Always run these commands before committing:

```bash
uv run pytest -m "not live"    # Ensure unit tests pass
uv run ruff check .            # Check linting
```

Only commit if all commands succeed without errors.

## Architecture

Python 3.12 FastMCP 4 (`fastmcp>=4.0.10,<5.0.0`) server using Crawl4AI for web content extraction.

FastMCP 4 conventions in this repo:
- Tool annotations use `mcp.types.ToolAnnotations` with snake_case fields (`read_only_hint`, ...).
- Tool failures `raise ToolError(...)`; never return an error dict or status field.
- No `ctx.info`/`ctx.debug`/`ctx.warning` logging; progress goes through `ctx.report_progress`.
- HTTP runs with `stateless_http=True` on `run()`; do not pass `allowed_hosts`.
- `CacheStatus` keeps camelCase wire keys via `alias` + `serialize_by_alias` (fastmcp 4 ignores `serialization_alias`).

### Tools

| Tool | Purpose |
|------|---------|
| `read_website` | Fetch URL(s), return clean Markdown. Supports multi-page BFS. |
| `list_links` | Lightweight link discovery — returns title + links without full content |
| `get_cache_status` | Report cache size and file count |
| `clear_cache` | Clear on-disk cache |

### Key Design Decisions

- **Cache**: Uses Crawl4AI's built-in cache (`CacheMode.ENABLED`), stored at `~/.cache/mcp-read-website-fast`
- **Truncation**: `max_chars=50000` default prevents context window overflow
- **Pages cap**: Max 20 pages per crawl to prevent abuse
- **Timeout**: Exposed as `timeout_seconds` (user-friendly) converted to ms internally
- **Auth**: `MCP_API_KEY` loaded via Pydantic `SecretStr` in Settings

## Testing Instructions

- Run tests with `uv run pytest`
- `tests/test_crawler.py`: Pure function tests (no network)
- `tests/test_server.py`: Tool registration and schema tests (no network)
- `tests/test_mcp_protocol.py`: MCP surface through an in-memory client: registration, snake_case annotations, a mocked read, ToolError paths, one telemetry line (no network)
- `tests/test_live.py`: Integration tests against real sites (The Verge, Medium, GitHub)
- Mark live tests: `@pytest.mark.live`
- Skip live tests: `uv run pytest -m "not live"`

## CI and Releases

- `.github/workflows/ci.yml`: one job named `test` (ruff + `pytest -m "not live"`, `FASTMCP_MCP_CAMELCASE_COMPAT=false`) on PRs and pushes to `main`. `main` is protected and requires `test`.
- `.github/workflows/release.yml`: tag-only. On push to `main` it tests, runs pip-audit, and pushes the next patch tag (latest `v*` + 1). It never commits to `main`; keep the `pyproject.toml` version static.
- Deploy: the Komodo stack builds from source (`build: .`) on the push webhook. No image is published.

## Repository Etiquette

- Branch names: `feature/description`, `fix/issue-number`
- Conventional commits (`feat:`, `fix:`, `chore:`)
- Update README.md for user-facing changes
- Add tests for new functionality

## Developer Environment Setup

1. Clone repository
2. Install Python 3.12+ and uv
3. Run `uv sync`
4. Run `uv run mcp-read-website-fast` for development

## Project-Specific Warnings

- **Docker Image Size**: Crawl4AI + Playwright + Chromium = ~500MB+ image
- **Memory Usage**: Large pages can consume significant memory
- **URL Validation**: Always validate and sanitize URLs
- **First Request Latency**: Browser startup adds latency on first crawl
- **Not a scraper**: Do not add bulk scraping features or bypass access controls
