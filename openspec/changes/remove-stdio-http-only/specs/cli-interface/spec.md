## MODIFIED Requirements

### Requirement: Serve Command
The system SHALL provide a `serve` command that starts the MCP server using HTTP streamable transport.

#### Scenario: Serve command execution
- **WHEN** the `serve` command is executed
- **THEN** the system starts the MCP server with HTTP streamable transport on the configured port

#### Scenario: Port configuration
- **WHEN** the `serve` command is executed with `--port` flag or PORT environment variable
- **THEN** the server listens on the specified port (default: 3000)

## REMOVED Requirements

### Requirement: Stdio Transport Option
**Reason**: The server no longer supports stdio transport. All references to stdio transport selection have been removed from CLI help text and documentation.

**Migration**: Users must configure HTTP transport. The `MCP_TRANSPORT` environment variable is no longer used.

