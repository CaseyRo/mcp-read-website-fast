## 1. Tool Schema Updates

- [x] 1.1 Add `output` parameter to `read_website` tool input schema
- [x] 1.2 Define parameter as enum: `["markdown", "json", "both"]`
- [x] 1.3 Set default value to `"markdown"` for backward compatibility
- [x] 1.4 Add parameter description to tool schema

## 2. Response Format Implementation

- [x] 2.1 Implement markdown output format (default, existing behavior)
- [x] 2.2 Implement JSON output format with structured data
- [x] 2.3 Implement "both" output format (markdown + JSON)
- [x] 2.4 Extract and structure metadata (title, links, url, error) for JSON output
- [x] 2.5 Handle error cases for all output formats

## 3. Testing

- [x] 3.1 Add test for default markdown output (backward compatibility)
- [x] 3.2 Add test for JSON output format
- [x] 3.3 Add test for "both" output format
- [x] 3.4 Add test for invalid output parameter value
- [x] 3.5 Add test for error handling with different output formats
- [x] 3.6 Verify backward compatibility (no output parameter = markdown)

## 4. Documentation

- [x] 4.1 Update tool description to mention output format option
- [x] 4.2 Document JSON output structure
- [x] 4.3 Document "both" output format behavior
- [x] 4.4 Add examples for each output format

## 5. Validation

- [x] 5.1 Run `npm run lint` and fix any issues
- [x] 5.2 Run `npm run typecheck` and fix any type errors
- [x] 5.3 Run `npm test` and verify all tests pass
- [x] 5.4 Run `openspec validate add-output-format-option --strict`

