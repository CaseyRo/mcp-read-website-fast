## Context

The MCP server currently supports two transport modes:
1. **Stdio** (default) - For IDE integration (Cursor, VS Code, Claude Code, JetBrains)
2. **HTTP Streamable** - For Docker/remote deployments

The requirement is to remove stdio support and make HTTP the only transport option.

## Goals / Non-Goals

### Goals
- Simplify server architecture by removing transport selection logic
- Always use HTTP streamable transport
- Update all documentation to reflect HTTP-only deployment
- Remove all stdio-related code and dependencies

### Non-Goals
- Supporting both transports (stdio is being removed)
- Backward compatibility with stdio clients
- IDE integration via stdio

## Decisions

### Decision: Remove Stdio Transport Entirely
**Rationale**: Simplifies codebase, removes conditional logic, aligns with deployment model. The product will be HTTP-only.

**Alternatives considered**:
1. Keep both transports but make HTTP default - Rejected: adds complexity, not needed
2. Deprecate stdio with warning - Rejected: clean break is better for maintenance

### Decision: Always Start HTTP Server
**Rationale**: No environment variable needed - server always starts HTTP server on configured port (default 3000).

**Alternatives considered**:
1. Keep MCP_TRANSPORT but only allow 'streamable-http' - Rejected: unnecessary complexity
2. Require explicit HTTP configuration - Rejected: HTTP is now the only option

### Decision: Remove IDE Installation Instructions
**Rationale**: IDEs that use stdio can no longer integrate. Only HTTP-capable MCP clients can use this server.

**Alternatives considered**:
1. Keep instructions with deprecation notice - Rejected: misleading, they won't work
2. Provide HTTP-based IDE integration guide - Considered but out of scope for this change

## Risks / Trade-offs

### Risks
- **Breaking change for IDE users**: Users of Cursor, VS Code, Claude Code, JetBrains will lose functionality
- **Adoption impact**: May reduce user base if HTTP-only deployment is more complex
- **Client compatibility**: Not all MCP clients support HTTP transport

### Mitigations
- Clear documentation about HTTP-only requirement
- Docker deployment makes HTTP setup straightforward
- Version bump to indicate breaking change

### Trade-offs
- **Simplicity vs Compatibility**: Choosing simplicity (single transport) over compatibility (multiple transports)
- **Deployment model**: Favoring server-based deployment over local IDE integration

## Migration Plan

### For Users
1. **IDE users**: Must migrate to HTTP-capable MCP clients or use Docker deployment
2. **Docker users**: No changes needed (already using HTTP)
3. **CLI users**: No changes needed (CLI still works independently)

### Code Changes
1. Remove `StdioServerTransport` import
2. Remove `MCP_TRANSPORT` environment variable checks
3. Remove stdio-specific error handling
4. Always create HTTP server
5. Update all documentation

### Rollback
If needed, can revert to previous commit that supports both transports.

## Open Questions

- Should we provide migration guide for IDE users?
- Do we need to check if HTTP transport is supported by target MCP clients?
- Should we add validation to ensure port is available before starting?

