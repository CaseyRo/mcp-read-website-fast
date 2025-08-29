# AGENTS Instructions

This file documents key architectural notes for the `mcp-read-website-fast` project. Update it whenever architectural changes or significant investigations occur.

## HTTP Gateway Rationale
- The project includes an HTTP gateway that fetches external web pages and presents them through the Model Context Protocol (MCP) tooling.
- Running this gateway locally minimizes token usage and latency by avoiding remote services.
- The gateway handles polite crawling (robots.txt compliance, rate limiting) and caching to reduce redundant network requests.

## Protocol Nuances
- Supports both HTTP and HTTPS schemes.
- Uses a stream-first design and SHA-256 hashed URLs for caching.
- Follows MCP tool conventions; the `read_website` tool is the entry point for clients.
- Clearly surface HTTP status codes and network errors to the client to aid troubleshooting.

## Debugging Tips
- Start the MCP server in development mode with `npm run serve:dev` for interactive debugging.
- Fetch individual URLs via `npm run dev fetch <url>` to reproduce issues.
- Enable verbose logging by setting `LOG_LEVEL=debug` or `MCP_DEBUG=1`.
- Clear caches with `npm run dev clear-cache` when testing repeated fetches.
- Run the test suite with `npm test` to verify changes.

## Maintenance
- Keep this document up to date. Whenever architecture evolves or investigations uncover new behaviors, add notes here so future contributors understand the rationale and debugging strategies.
