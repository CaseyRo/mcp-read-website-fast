# Change: Remove Stdio Transport - HTTP Only

## Why

The product needs to run exclusively as an HTTP streamable server. This simplifies the architecture, removes transport selection complexity, and aligns with deployment requirements. Local IDE integration via stdio is no longer supported.

## What Changes

- **BREAKING**: Remove stdio transport support - the server will ONLY run via HTTP streamable transport
- **REMOVED**: `MCP_TRANSPORT` environment variable (no longer needed - always HTTP)
- **REMOVED**: `StdioServerTransport` import and usage
- **REMOVED**: All stdio-specific error handling and stdin/stdout management
- **MODIFIED**: Server startup to always use `StreamableHTTPServerTransport`
- **MODIFIED**: Default behavior - server always starts HTTP server on configured port
- **MODIFIED**: Documentation to remove all IDE integration instructions (Claude Code, VS Code, Cursor, JetBrains)
- **MODIFIED**: Installation instructions to reflect HTTP-only deployment
- **MODIFIED**: CLI help text to remove stdio references

## Impact

- **Affected specs**:
  - `mcp-server` capability - transport requirements
  - `cli-interface` capability - serve command description
- **Affected code**:
  - `src/serve.ts` - Remove stdio transport logic
  - `src/index.ts` - Update serve command description
  - `README.md` - Remove IDE installation sections, update transport docs
  - `AGENTS.md` - Update transport notes
  - `openspec/project.md` - Update architecture patterns
  - `CLAUDE.md` - Update MCP server integration docs
- **Breaking changes**: **YES - BREAKING CHANGE**
  - No longer works with IDEs that use stdio (Cursor, VS Code, Claude Code, JetBrains)
  - All clients must use HTTP transport
  - Installation method changes completely
- **Migration**:
  - Existing IDE users must switch to HTTP-based MCP clients or use Docker/remote deployment
  - Update all MCP client configurations to use HTTP endpoints instead of stdio commands
