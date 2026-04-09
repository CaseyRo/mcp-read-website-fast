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

Python 3.12 FastMCP server using Crawl4AI for web content extraction.

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
- `tests/test_live.py`: Integration tests against real sites (The Verge, Medium, GitHub)
- Mark live tests: `@pytest.mark.live`
- Skip live tests: `uv run pytest -m "not live"`

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
