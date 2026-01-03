# Change: Update Requirements, Clean Up Repo, and Improvements

## Why

The repository has several areas that need attention:

1. **No OpenSpec specifications exist** - The project lacks formal requirements documentation, making it difficult to track what the system should do and validate changes
2. **Outdated documentation** - CLAUDE.md and README reference old architecture (crawler/, parser/, cache/ directories) that no longer exist after migrating to @just-every/crawl
3. **Unused code and dependencies** - chunker.ts utility is never imported, and uuid dependency is unused
4. **Incomplete test coverage** - Only deployment tests exist; core functionality lacks unit tests
5. **Documentation inconsistencies** - Architecture descriptions don't match current codebase structure

This change will establish a solid foundation with proper specifications, clean up technical debt, and improve maintainability.

## What Changes

- **ADDED**: Initial OpenSpec specifications documenting current system behavior
  - `web-content-extraction` capability (core fetchMarkdown functionality)
  - `mcp-server` capability (MCP tool and resource definitions)
  - `cli-interface` capability (CLI commands and options)
  - `caching` capability (cache management and statistics)

- **MODIFIED**: Documentation files to reflect current architecture
  - Update CLAUDE.md to remove references to non-existent directories
  - Update README.md architecture section to match actual code structure
  - Ensure all documentation references @just-every/crawl instead of old modules

- **REMOVED**: Unused code and dependencies
  - Remove `src/utils/chunker.ts` (never imported)
  - Remove `uuid` dependency from package.json (never used)
  - Update README to remove chunker reference

- **IMPROVED**: Test coverage and code quality
  - Add unit tests for core fetchMarkdown functionality
  - Add tests for MCP server tool/resource handlers
  - Verify all utilities are actually used

- **IMPROVED**: Repository organization
  - Ensure .gitignore is comprehensive
  - Verify all files in package.json "files" array are necessary
  - Check for any other unused files

## Impact

- **Affected specs**: New capabilities being created (web-content-extraction, mcp-server, cli-interface, caching)
- **Affected code**:
  - `CLAUDE.md` - Documentation updates
  - `README.md` - Architecture section updates
  - `package.json` - Dependency removal
  - `src/utils/chunker.ts` - File removal
  - `test/` - New test files
- **Breaking changes**: None - this is cleanup and documentation
- **Migration**: No migration needed, purely additive and cleanup work
