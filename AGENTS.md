<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Agent Notes

## Reasoning

- The server runs exclusively via HTTP streamable transport. Stdio transport has been removed to simplify architecture.
- The server automatically starts an HTTP server on the configured port (default: 3000, configurable via `PORT` environment variable).
- All MCP clients must connect via HTTP transport - IDE integration via stdio is no longer supported.

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
- Start the MCP server with custom port using `PORT=<port> npm run serve`.
- Fetch individual URLs via `npm run dev fetch <url>` to reproduce issues.
- Enable verbose logging by setting `LOG_LEVEL=debug` or `MCP_DEBUG=1`.
- Clear caches with `npm run dev clear-cache` when testing repeated fetches.
- Run the test suite with `npm test` to verify changes.

## Docker Deployment
- Use `docker-compose up -d` for production deployment with automatic restarts.
- The Docker container runs with HTTP transport (the only supported transport).
- Cache is persisted via Docker volumes for better performance across restarts.
- Health checks ensure the container is restarted if the MCP server becomes unresponsive.
- Non-root user security and proper signal handling via dumb-init.
- **Debugging**: Use `docker-compose --profile development up -d` for enhanced debugging with debug logging and Node.js inspector.
- **Profiles**: Production profile (port 3000) and development profile (port 3001) with different logging levels.
- **Environment Variables**: Comprehensive logging configuration via `LOG_LEVEL`, `MCP_DEBUG`, and `MCP_QUIET`.

## Maintenance
- Keep this document up to date. Whenever architecture evolves or investigations uncover new behaviors, add notes here so future contributors understand the rationale and debugging strategies.
