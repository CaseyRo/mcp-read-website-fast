# Project Context

## Purpose

`@just-every/mcp-read-website-fast` is a fast, token-efficient web content extraction tool for AI agents. It converts websites to clean Markdown while preserving links and structure. The project implements a Model Context Protocol (MCP) server that fetches web pages locally, strips noise, and converts content to Markdown with minimal token footprint. Designed for Claude Code, IDEs, and LLM pipelines.

Key goals:
- Fast startup with lazy loading for optimal performance
- Token-efficient content extraction
- Clean Markdown output with link preservation
- Polite crawling with robots.txt support and rate limiting
- Smart caching to reduce redundant network requests

## Tech Stack

### Core Technologies
- **TypeScript** (5.9.2+) - Primary language with strict mode enabled
- **Node.js** (>=20.0.0) - Runtime environment
- **ES Modules** - Native ESM with `type: "module"` in package.json
- **ES2022** - Target language version

### Key Dependencies
- **@modelcontextprotocol/sdk** (^1.17.4) - Official MCP SDK for server implementation
- **@just-every/crawl** (^1.0.8) - Core crawling and markdown conversion functionality
- **commander** (^14.0.0) - CLI argument parsing
- **chalk** (^5.3.0) - Terminal output coloring
- **uuid** (^11.1.0) - UUID generation

### Development Tools
- **Vitest** (^3.2.4) - Testing framework
- **TypeScript ESLint** (^8.41.0) - Linting and type checking
- **Prettier** - Code formatting (via eslint-plugin-prettier)
- **tsx** (^4.20.5) - TypeScript execution for development

### Deployment
- **Docker** - Containerization with docker-compose support
- **Node.js HTTP Server** - For streamable HTTP transport mode

## Project Conventions

### Code Style

- **TypeScript Strict Mode**: Enabled with all strict checks
  - `noUnusedLocals`, `noUnusedParameters`, `noImplicitReturns`, `noFallthroughCasesInSwitch`
- **ES Modules**: All imports use `.js` extensions (TypeScript requirement for ESM)
- **Formatting**: Prettier with ESLint integration
- **Linting**: ESLint with TypeScript rules
  - `@typescript-eslint/no-explicit-any`: Off (allows `any` when needed)
  - `no-console`: Off (console usage allowed for logging)
- **Naming**:
  - Files: kebab-case (e.g., `fetch-markdown.ts`)
  - Functions/Classes: camelCase
  - Constants: UPPER_SNAKE_CASE
- **Logging**: Custom logger using chalk for colored output, writes to stderr for MCP compatibility

### Architecture Patterns

- **MCP Server Pattern**: Implements Model Context Protocol server with tools and resources
- **Lazy Loading**: Heavy dependencies (like fetchMarkdown) are loaded on first use to improve startup time
- **Stream-First Design**: Low memory usage with streaming data processing
- **HTTP Transport**: Uses streamable HTTP transport exclusively - stdio transport has been removed
- **Auto-Restart**: Wrapper script (`serve-restart.ts`) provides automatic restart on crashes with exponential backoff
- **Error Handling**: Graceful shutdown on SIGINT/SIGTERM, careful handling of transport errors
- **Caching Strategy**: SHA-256 hashed URLs for cache keys, disk-based cache in `.cache` directory

### Testing Strategy

- **Framework**: Vitest for unit and integration tests
- **Test Location**: `test/` directory
- **Test Types**:
  - Deployment tests verify server startup and CLI functionality
  - Package structure validation
  - MCP tool structure verification
  - Dependency checks
- **Running Tests**: `npm test` or `vitest`
- **Coverage**: Tests verify critical paths including server initialization, CLI commands, and package configuration

### Git Workflow

- Standard git workflow (not explicitly documented)
- Repository: `git+https://github.com/just-every/mcp-read-website-fast.git`
- License: MIT

## Domain Context

### Model Context Protocol (MCP)
- MCP is a protocol for AI assistants to interact with external tools and resources
- This project implements an MCP server that provides web content extraction as a tool
- Tools are callable functions, Resources are read-only data sources
- The server runs exclusively via HTTP streamable transport (stdio transport has been removed)

### Web Content Extraction
- Uses Mozilla Readability (via @just-every/crawl) for content extraction - same algorithm as Firefox Reader View
- HTML to Markdown conversion using Turndown with GitHub Flavored Markdown (GFM) support
- Preserves links for knowledge graph construction
- Supports optional chunking for downstream processing

### Polite Crawling
- Respects robots.txt by default (can be disabled with `--no-robots`)
- Rate limiting to avoid overwhelming servers
- Configurable concurrency limits
- Same-origin only by default (can allow cross-origin with `--all-origins`)

### Caching
- SHA-256 hashed URLs as cache keys
- Disk-based cache in `.cache` directory (configurable)
- Cache can be cleared via CLI or MCP resource
- Cache statistics available via MCP resource

## Important Constraints

### Technical Constraints
- **Node.js Version**: Requires Node.js >=20.0.0
- **Transport Mode**: HTTP streamable transport only (stdio transport removed in v1.0.0)
- **Memory**: Stream-first design to minimize memory usage
- **Timeout**: Default 30s request timeout (configurable)
- **Page Limits**: Maximum 100 pages per crawl request
- **JavaScript**: Does not support JavaScript-rendered content (static HTML only)

### Protocol Constraints
- **MCP Protocol**: Must follow MCP tool and resource conventions
- **Output Format**: Must return text content in MCP-compatible format
- **Error Handling**: Must surface HTTP status codes and network errors clearly

### Deployment Constraints
- **Docker**: HTTP transport required for containerized deployments
- **Port Configuration**: Default port 3000, configurable via `PORT` env var or `--port` flag
- **Logging**: Must use stderr for MCP compatibility (stdout reserved for protocol)

## External Dependencies

### Core Services
- **@just-every/crawl**: Provides core crawling functionality including:
  - URL fetching and queue management
  - robots.txt parsing and compliance
  - Content extraction via Mozilla Readability
  - HTML to Markdown conversion via Turndown
  - Rate limiting and concurrency control

### Protocol
- **@modelcontextprotocol/sdk**: Official MCP SDK providing:
  - Server implementation
  - Transport layer (streamable HTTP)
  - Protocol message handling
  - Tool and resource definitions

### External Systems
- **Target Websites**: Fetches content from HTTP/HTTPS URLs
- **robots.txt**: Respects robots.txt files from target domains (when enabled)
- **DNS**: Requires DNS resolution for target URLs

### Optional Dependencies
- **Netscape Cookie Files**: Optional cookie support for authenticated pages via `cookiesFile` parameter
