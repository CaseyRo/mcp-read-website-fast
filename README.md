# @just-every/mcp-read-website-fast

Fast, token-efficient web content extraction for AI agents - converts websites to clean Markdown.

[![npm version](https://badge.fury.io/js/@just-every%2Fmcp-read-website-fast.svg)](https://www.npmjs.com/package/@just-every/mcp-read-website-fast)
[![GitHub Actions](https://github.com/just-every/mcp-read-website-fast/workflows/Release/badge.svg)](https://github.com/just-every/mcp-read-website-fast/actions)

<a href="https://glama.ai/mcp/servers/@just-every/mcp-read-website-fast">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@just-every/mcp-read-website-fast/badge" alt="read-website-fast MCP server" />
</a>

## Overview

Existing MCP web crawlers are slow and consume large quantities of tokens. This pauses the development process and provides incomplete results as LLMs need to parse whole web pages.

This MCP package fetches web pages locally, strips noise, and converts content to clean Markdown while preserving links. Designed for HTTP-based MCP clients and LLM pipelines with minimal token footprint. Crawl sites locally with minimal dependencies.

**Note:** This package now uses [@just-every/crawl](https://www.npmjs.com/package/@just-every/crawl) for its core crawling and markdown conversion functionality.

**⚠️ Breaking Change (v1.0.0)**: This server now runs exclusively via HTTP transport. Stdio transport for IDE integration (Cursor, VS Code, Claude Code, JetBrains) is no longer supported. All clients must connect via HTTP.

## Features

- **Fast startup** using official MCP SDK with lazy loading for optimal performance
- **Content extraction** using Mozilla Readability (same as Firefox Reader View)
- **HTML to Markdown** conversion with Turndown + GFM support
- **Smart caching** with SHA-256 hashed URLs
- **Polite crawling** with robots.txt support and rate limiting
- **Concurrent fetching** with configurable depth crawling
- **Stream-first design** for low memory usage
- **Link preservation** for knowledge graphs

## Installation

### HTTP Transport Only

This MCP server runs exclusively via HTTP streamable transport. It does not support stdio transport for IDE integration.

### Docker Deployment (Recommended)

The easiest way to run the server is using Docker:

```bash
docker-compose up -d
```

See the [Docker](#docker) section below for detailed configuration options.

### Manual HTTP Server

Start the server manually:

```bash
npm run serve
# Or with custom port
PORT=8080 npm run serve
```

The server will listen on port 3000 by default (or the port specified by the `PORT` environment variable).

### MCP Client Configuration

Configure your HTTP-capable MCP client to connect to the server endpoint. The server exposes the MCP protocol over HTTP at `http://localhost:3000` (or your configured port).

## Docker

### Quick Start

```bash
# Build and run with Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t mcp-read-website-fast .
docker run -d -p 3000:3000 --name mcp-server mcp-read-website-fast
```

**Note**: The Docker build uses pre-built `dist/` files from git for faster builds. Ensure `dist/` is up-to-date before building.

### Docker Compose

The included `docker-compose.yml` provides a production-ready setup:

```bash
# Start server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Environment Variables

The Docker setup supports comprehensive environment variable configuration:

#### Transport Configuration
- `PORT=3000` - HTTP server port (default: 3000)

#### Logging Configuration
- `LOG_LEVEL=info` - Logging level (error, warn, info, debug)
- `MCP_DEBUG=0` - MCP debug mode (0=off, 1=on)
- `MCP_QUIET=false` - MCP quiet mode (true/false)

#### Server Configuration
- `NODE_ENV=production` - Node.js environment (production/development)
- `DEBUG_LEVEL=info` - Debug level override
- `VERBOSE_LOGGING=false` - Enable verbose logging

#### Development Settings
- `NODE_OPTIONS=--inspect=0.0.0.0:9229` - Enable Node.js inspector for debugging (can be set via environment variable)

### Custom Port

```bash
# Run on custom port
docker run -d -p 8080:8080 \
  -e PORT=8080 \
  --name mcp-server \
  mcp-read-website-fast
```

### Debugging with Docker

```bash
# Start with debug logging
LOG_LEVEL=debug docker-compose up -d

# Start with MCP debugging enabled
MCP_DEBUG=1 docker-compose up -d

# Start with Node.js inspector enabled
NODE_OPTIONS=--inspect=0.0.0.0:9229 docker-compose up -d

# View debug logs
docker-compose logs -f

# Connect to Node.js inspector (if enabled)
# Open http://localhost:9229 in Chrome DevTools
```

### HTTP Transport

The server runs exclusively via HTTP streamable transport. It automatically starts an HTTP server on the configured port.

```bash
# Start server (default port 3000)
npm run serve

# Start with custom port
PORT=8080 npm run serve

# Or using the restart wrapper directly
node dist/serve-restart.js
PORT=8080 node dist/serve-restart.js
```

The server listens on port `3000` by default. Override it with the `PORT` environment variable.

**Note:** This server only supports HTTP transport. Stdio transport for IDE integration is not supported.

## Features

- **Fast startup** using official MCP SDK with lazy loading for optimal performance
- **Content extraction** using Mozilla Readability (same as Firefox Reader View)
- **HTML to Markdown** conversion with Turndown + GFM support
- **Smart caching** with SHA-256 hashed URLs
- **Polite crawling** with robots.txt support and rate limiting
- **Concurrent fetching** with configurable depth crawling
- **Stream-first design** for low memory usage
- **Link preservation** for knowledge graphs

### Available Tools

- `read_website` - Fetches a webpage and converts it to clean markdown
  - Parameters:
    - `url` (required): The HTTP/HTTPS URL to fetch
    - `pages` (optional): Maximum number of pages to crawl (default: 1, max: 100)

### Available Resources

- `read-website-fast://status` - Get cache statistics
- `read-website-fast://clear-cache` - Clear the cache directory

## Development Usage

### Install

```bash
npm install
npm run build
```

### Single page fetch
```bash
npm run dev fetch https://example.com/article
```

### Crawl with depth
```bash
npm run dev fetch https://example.com --depth 2 --concurrency 5
```

### Output formats
```bash
# Markdown only (default)
npm run dev fetch https://example.com

# JSON output with metadata
npm run dev fetch https://example.com --output json

# Both URL and markdown
npm run dev fetch https://example.com --output both
```

### CLI Options

- `-p, --pages <number>` - Maximum number of pages to crawl (default: 1)
- `-c, --concurrency <number>` - Max concurrent requests (default: 3)
- `--no-robots` - Ignore robots.txt
- `--all-origins` - Allow cross-origin crawling
- `-u, --user-agent <string>` - Custom user agent
- `--cache-dir <path>` - Cache directory (default: .cache)
- `-t, --timeout <ms>` - Request timeout in milliseconds (default: 30000)
- `-o, --output <format>` - Output format: json, markdown, or both (default: markdown)

### Clear cache
```bash
npm run dev clear-cache
```

## Auto-Restart Feature

The MCP server includes automatic restart capability by default for improved reliability:

- Automatically restarts the server if it crashes
- Handles unhandled exceptions and promise rejections
- Implements exponential backoff (max 10 attempts in 1 minute)
- Logs all restart attempts for monitoring
- Gracefully handles shutdown signals (SIGINT, SIGTERM)

For development/debugging without auto-restart:
```bash
# Run directly without restart wrapper
npm run serve:dev
```

## Architecture

```
mcp-read-website-fast/
├── src/
│   ├── internal/
│   │   └── fetchMarkdown.ts  # Core API using @just-every/crawl
│   ├── utils/
│   │   ├── logger.ts         # Logging utilities
│   │   └── extractMarkdownLinks.ts  # Link extraction utilities
│   ├── index.ts              # CLI entry point
│   ├── serve.ts              # MCP server entry point
│   └── serve-restart.ts      # Auto-restart wrapper
```

## Development

```bash
# Run in development mode
npm run dev fetch https://example.com

# Build for production
npm run build

# Run tests
npm test

# Type checking
npm run typecheck

# Linting
npm run lint
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Troubleshooting

### Cache Issues
```bash
npm run dev clear-cache
```

### Timeout Errors
- Increase timeout with `-t` flag
- Check network connectivity
- Verify URL is accessible

### Content Not Extracted
- Some sites block automated access
- Try custom user agent with `-u` flag
- Check if site requires JavaScript (not supported)

## License

MIT
