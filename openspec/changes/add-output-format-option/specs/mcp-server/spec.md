## MODIFIED Requirements

### Requirement: Read Website Tool
The system SHALL provide a `read_website` MCP tool for fetching web content with an optional output format parameter.

#### Scenario: Tool execution with default output (markdown)
- **WHEN** the read_website tool is called with a valid URL and no output parameter
- **THEN** the system fetches the page, converts to markdown, and returns the content as text in MCP-compatible format
- **THEN** the response format is: `{ content: [{ type: "text", text: "<markdown>" }] }`

#### Scenario: Tool execution with markdown output
- **WHEN** the read_website tool is called with `output: "markdown"`
- **THEN** the system returns markdown content as text (same as default behavior)

#### Scenario: Tool execution with JSON output
- **WHEN** the read_website tool is called with `output: "json"`
- **THEN** the system returns structured JSON data with fields: `markdown`, `title`, `links`, `url`, and optionally `error`
- **THEN** the response format is: `{ content: [{ type: "text", text: "<json_string>" }] }` where the JSON string contains the structured data

#### Scenario: Tool execution with both output formats
- **WHEN** the read_website tool is called with `output: "both"`
- **THEN** the system returns both markdown and JSON formats
- **THEN** the response contains two content items: one with markdown text and one with JSON text

#### Scenario: Multiple pages with JSON output
- **WHEN** the read_website tool is called with `pages > 1` and `output: "json"`
- **THEN** the system fetches multiple pages and returns structured JSON with combined markdown and metadata for all pages

#### Scenario: Error handling with different output formats
- **WHEN** a tool execution fails and `output: "markdown"` (or default)
- **THEN** the system returns error message in markdown format
- **WHEN** a tool execution fails and `output: "json"`
- **THEN** the system returns error information in the JSON `error` field
- **WHEN** a tool execution fails and `output: "both"`
- **THEN** the system returns error information in both formats

#### Scenario: Invalid output parameter
- **WHEN** the read_website tool is called with an invalid `output` value (not "markdown", "json", or "both")
- **THEN** the system returns a validation error

## ADDED Requirements

### Requirement: Output Format Parameter
The `read_website` tool SHALL accept an optional `output` parameter that controls the response format.

#### Scenario: Output parameter definition
- **WHEN** the tool schema is inspected
- **THEN** the `output` parameter is defined as an optional enum with values: `["markdown", "json", "both"]`
- **THEN** the default value is `"markdown"`
- **THEN** the parameter description explains each format option

#### Scenario: JSON output structure
- **WHEN** `output: "json"` is specified
- **THEN** the JSON response contains the following fields:
  - `markdown` (string) - The markdown content
  - `title` (string, optional) - Page title if available
  - `links` (string[], optional) - Array of extracted links
  - `url` (string | string[]) - Source URL(s)
  - `error` (string, optional) - Error message if any errors occurred

