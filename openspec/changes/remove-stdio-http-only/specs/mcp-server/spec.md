## MODIFIED Requirements

### Requirement: MCP Server Implementation
The system SHALL implement a Model Context Protocol (MCP) server that provides web content extraction as a tool. The server SHALL use HTTP streamable transport exclusively.

#### Scenario: Server startup
- **WHEN** the MCP server is started
- **THEN** it initializes with lazy loading of heavy dependencies for fast startup, uses HTTP streamable transport only, creates an HTTP server on the configured port (default 3000), and connects successfully

#### Scenario: HTTP transport required
- **WHEN** the MCP server starts
- **THEN** it always uses StreamableHTTPServerTransport and creates an HTTP server - stdio transport is not supported

#### Scenario: Port configuration
- **WHEN** the server starts
- **THEN** it listens on the port specified by the PORT environment variable or --port flag (default: 3000)

## REMOVED Requirements

### Requirement: Stdio Transport Support
**Reason**: The product now exclusively uses HTTP streamable transport. Stdio transport is removed to simplify architecture and align with deployment requirements.

**Migration**: IDE users who previously used stdio transport must migrate to HTTP-capable MCP clients or use Docker/remote deployment.

