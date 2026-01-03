## Context

The `read_website` MCP tool currently returns content as Markdown text in the MCP response format:
```json
{
  "content": [
    {
      "type": "text",
      "text": "# Page Title\n\nContent here..."
    }
  ]
}
```

The underlying `fetchMarkdown` function already returns structured data including `markdown`, `title`, `links`, and `error`, but this metadata is not exposed to MCP clients.

## Goals / Non-Goals

### Goals
- Add optional `output` parameter to control response format
- Support three output modes: `markdown` (default), `json`, `both`
- Maintain backward compatibility (default behavior unchanged)
- Expose structured metadata (title, links) in JSON format

### Non-Goals
- Changing the default output format (must remain markdown)
- Removing markdown support
- Changing the underlying `fetchMarkdown` API

## Decisions

### Decision: Output Parameter Values
**Rationale**: Three clear options:
- `"markdown"` - Current behavior, human-readable
- `"json"` - Structured data for programmatic use
- `"both"` - Maximum flexibility, includes both formats

**Alternatives considered**:
1. Boolean flag `json: true/false` - Rejected: Less flexible, doesn't support "both"
2. Enum with more options - Rejected: Three options are sufficient for current needs

### Decision: JSON Output Structure
**Rationale**: When `output: "json"` or `output: "both"`, return structured JSON with:
- `markdown` - The markdown content
- `title` - Page title (if available)
- `links` - Array of extracted links
- `url` - Source URL(s)
- `error` - Error message (if any)

**Alternatives considered**:
1. Return raw `fetchMarkdown` result - Rejected: May include internal fields, needs sanitization
2. Different structure - Rejected: Standard structure is clearer

### Decision: "Both" Format Implementation
**Rationale**: When `output: "both"`, return two content items:
1. Text content with markdown (for human readability)
2. JSON content with structured data (for programmatic use)

This allows clients to use whichever format they prefer.

**Alternatives considered**:
1. Single JSON object containing both - Rejected: Less flexible, harder to parse
2. Separate tool calls - Rejected: Inefficient, requires two requests

### Decision: Default to Markdown
**Rationale**: Maintain backward compatibility. Existing clients expect markdown text.

**Alternatives considered**:
1. Default to JSON - Rejected: Breaking change
2. No default, require explicit choice - Rejected: Breaks backward compatibility

## Risks / Trade-offs

### Risks
- **Response size increase**: "both" format doubles response size
  - **Mitigation**: Only used when explicitly requested
  - **Mitigation**: Clients can choose single format if size is concern

- **Complexity**: More code paths to test and maintain
  - **Mitigation**: Well-defined enum values, clear structure

### Trade-offs
- **Flexibility vs Simplicity**: Adding options increases flexibility but adds complexity
- **Backward compatibility vs New features**: Default maintains compatibility while enabling new use cases

## Migration Plan

### For Users
1. **No changes needed**: Default behavior unchanged
2. **Opt-in**: Users can add `output: "json"` or `output: "both"` parameter when needed
3. **Gradual adoption**: Can migrate to JSON format when ready

### Code Changes
1. Add `output` parameter to tool input schema
2. Modify tool handler to format response based on `output` parameter
3. Add tests for all three output formats
4. Update documentation

### Rollback
If needed, can revert parameter addition. Default behavior remains unchanged.

## Open Questions

- Should JSON output include additional metadata (e.g., fetch timestamp, cache status)?
- Should "both" format use separate content items or a combined structure?

