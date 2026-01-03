## 1. Code Changes

- [x] 1.1 Remove `StdioServerTransport` import from `src/serve.ts`
- [x] 1.2 Remove `MCP_TRANSPORT` environment variable checks
- [x] 1.3 Remove stdio-specific error handling (stdin/stdout management)
- [x] 1.4 Always create `StreamableHTTPServerTransport` (remove conditional)
- [x] 1.5 Always create HTTP server (remove conditional)
- [x] 1.6 Remove stdio-specific process.stdin handlers
- [x] 1.7 Update server startup logging to reflect HTTP-only mode
- [x] 1.8 Update CLI serve command description in `src/index.ts`

## 2. Documentation Updates

- [x] 2.1 Remove IDE installation sections from README.md (Claude Code, VS Code, Cursor, JetBrains)
- [x] 2.2 Update README.md transport documentation to reflect HTTP-only
- [x] 2.3 Remove stdio references from README.md
- [x] 2.4 Update AGENTS.md to remove stdio transport notes
- [x] 2.5 Update openspec/project.md architecture patterns section
- [x] 2.6 Update CLAUDE.md MCP server integration section
- [x] 2.7 Add migration note about breaking change

## 3. Testing

- [x] 3.1 Update deployment tests to reflect HTTP-only mode
- [x] 3.2 Remove any stdio transport tests
- [x] 3.3 Verify HTTP server starts correctly
- [x] 3.4 Verify port configuration works
- [x] 3.5 Run full test suite

## 4. Validation

- [x] 4.1 Run `npm run lint` and fix any issues
- [x] 4.2 Run `npm run typecheck` and fix any type errors
- [x] 4.3 Run `npm run build` and verify successful compilation
- [x] 4.4 Run `openspec validate remove-stdio-http-only --strict` and fix any issues
- [x] 4.5 Verify all documentation changes are accurate

## 5. Version Bump

- [x] 5.1 Bump version to 0.2.0 (major version bump for breaking change)
- [x] 5.2 Update version in package.json
- [x] 5.3 Update version in src/serve.ts
- [x] 5.4 Update version in Dockerfile
- [x] 5.5 Run `npm install` to update package-lock.json

