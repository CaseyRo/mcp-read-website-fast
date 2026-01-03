## 1. Documentation Updates

- [x] 1.1 Update CLAUDE.md to remove references to non-existent directories (crawler/, parser/, cache/)
- [x] 1.2 Update CLAUDE.md to reference @just-every/crawl instead of old modules
- [x] 1.3 Update README.md architecture section to match actual code structure
- [x] 1.4 Remove chunker reference from README.md
- [x] 1.5 Verify all documentation accurately describes current implementation

## 2. Code Cleanup

- [x] 2.1 Remove unused `src/utils/chunker.ts` file
- [x] 2.2 Remove `uuid` dependency from package.json
- [x] 2.3 Run `npm install` to update package-lock.json
- [x] 2.4 Verify no other files import chunker or uuid
- [x] 2.5 Check for any other unused files or dependencies

## 3. Repository Organization

- [x] 3.1 Review .gitignore for completeness
- [x] 3.2 Verify package.json "files" array includes all necessary files
- [x] 3.3 Check for any orphaned or duplicate files
- [x] 3.4 Ensure all test files are in appropriate locations

## 4. Test Coverage

- [x] 4.1 Add unit tests for fetchMarkdown function (success cases)
- [x] 4.2 Add unit tests for fetchMarkdown function (error cases)
- [x] 4.3 Add unit tests for MCP server tool handler
- [x] 4.4 Add unit tests for MCP server resource handlers
- [x] 4.5 Add unit tests for CLI command parsing
- [x] 4.6 Verify all tests pass with `npm test`

## 5. Validation

- [x] 5.1 Run `npm run lint` and fix any issues
- [x] 5.2 Run `npm run typecheck` and fix any type errors
- [x] 5.3 Run `npm run build` and verify successful compilation
- [x] 5.4 Run `openspec validate update-reqs-cleanup-repo --strict` and fix any issues
- [x] 5.5 Verify all documentation changes are accurate

