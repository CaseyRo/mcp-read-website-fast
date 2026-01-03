# Change: Add Output Format Option to read_website Tool

## Why

The `read_website` MCP tool currently only returns content as Markdown text. Some use cases benefit from structured JSON output (e.g., extracting metadata like title and links separately, programmatic processing). Adding an optional output format parameter allows clients to choose between:
- Markdown (default, current behavior) - for human-readable content
- JSON - for structured data with metadata
- Both - for maximum flexibility

## What Changes

- **ADDED**: Optional `output` parameter to `read_website` tool with values: `"markdown"` (default), `"json"`, or `"both"`
- **MODIFIED**: Tool response format to support JSON output when requested
- **MODIFIED**: Tool response format to support both formats when `output: "both"` is specified
- **MODIFIED**: `fetchMarkdown` result handling to structure JSON output with metadata (title, links, markdown, etc.)

## Impact

- **Affected specs**:
  - `mcp-server` capability - read_website tool definition and response format
- **Affected code**:
  - `src/serve.ts` - Add `output` parameter to tool schema, modify response format
  - `src/internal/fetchMarkdown.ts` - May need to expose additional metadata
  - `test/mcp-server.test.ts` - Add tests for new output formats
- **Breaking changes**: **NO**
  - Default behavior unchanged (returns markdown as before)
  - New parameter is optional
- **Backward compatibility**: **YES**
  - Existing clients continue to work without changes
  - Default output format is markdown (current behavior)

