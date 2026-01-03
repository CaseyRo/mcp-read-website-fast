## ADDED Requirements

### Requirement: MCP Server Implementation
The system SHALL implement a Model Context Protocol (MCP) server that provides web content extraction as a tool.

#### Scenario: Server startup
- **WHEN** the MCP server is started
- **THEN** it initializes with lazy loading of heavy dependencies for fast startup, supports both stdio and HTTP transports, and connects successfully

#### Scenario: Transport selection
- **WHEN** MCP_TRANSPORT environment variable is set to "streamable-http"
- **THEN** the server uses HTTP transport and listens on the configured port (default 3000)
- **WHEN** MCP_TRANSPORT is not set or set to stdio
- **THEN** the server uses stdio transport for IDE integration

### Requirement: Read Website Tool
The system SHALL provide a `read_website` MCP tool for fetching web content.

#### Scenario: Tool execution
- **WHEN** the read_website tool is called with a valid URL
- **THEN** the system fetches the page, converts to markdown, and returns the content in MCP-compatible format

#### Scenario: Multiple pages parameter
- **WHEN** the read_website tool is called with pages parameter > 1
- **THEN** the system fetches up to the specified number of pages (max 100) and combines them into a single markdown document

#### Scenario: Error handling
- **WHEN** a tool execution fails
- **THEN** the system returns a clear error message with context about what went wrong

### Requirement: Cache Status Resource
The system SHALL provide a `read-website-fast://status` resource for cache statistics.

#### Scenario: Status retrieval
- **WHEN** the status resource is read
- **THEN** the system returns JSON with cache size, file count, and formatted size information

### Requirement: Clear Cache Resource
The system SHALL provide a `read-website-fast://clear-cache` resource for cache management.

#### Scenario: Cache clearing
- **WHEN** the clear-cache resource is read
- **THEN** the system removes all cached files and returns a success status

### Requirement: Auto-Restart Capability
The system SHALL automatically restart on crashes with exponential backoff.

#### Scenario: Crash recovery
- **WHEN** the server crashes due to an unhandled exception
- **THEN** the auto-restart wrapper restarts the server with exponential backoff (max 10 attempts in 1 minute)

#### Scenario: Graceful shutdown
- **WHEN** the server receives SIGINT or SIGTERM
- **THEN** the server closes connections gracefully and exits cleanly

### Requirement: Logging
The system SHALL provide structured logging that writes to stderr for MCP compatibility.

#### Scenario: Log levels
- **WHEN** LOG_LEVEL environment variable is set
- **THEN** the logger respects the specified level (error, warn, info, debug)
- **WHEN** MCP_DEBUG is set
- **THEN** debug logging is enabled even in MCP mode

