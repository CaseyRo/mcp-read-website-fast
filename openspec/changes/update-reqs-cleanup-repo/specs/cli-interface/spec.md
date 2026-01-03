## ADDED Requirements

### Requirement: CLI Command Structure
The system SHALL provide a CLI interface using Commander for command-line usage.

#### Scenario: Fetch command
- **WHEN** the `fetch <url>` command is executed
- **THEN** the system fetches the URL and outputs markdown to stdout

#### Scenario: Clear cache command
- **WHEN** the `clear-cache` command is executed
- **THEN** the system removes all cached files and confirms the action

#### Scenario: Serve command
- **WHEN** the `serve` command is executed
- **THEN** the system starts the MCP server

### Requirement: Fetch Command Options
The system SHALL support various options for the fetch command.

#### Scenario: Pages option
- **WHEN** `--pages <number>` is provided
- **THEN** the system fetches up to the specified number of pages (default: 1, max: 100)

#### Scenario: Concurrency option
- **WHEN** `--concurrency <number>` is provided
- **THEN** the system uses the specified concurrency limit for parallel requests

#### Scenario: Robots.txt option
- **WHEN** `--no-robots` is provided
- **THEN** the system ignores robots.txt rules

#### Scenario: Cross-origin option
- **WHEN** `--all-origins` is provided
- **THEN** the system allows following links to different origins

#### Scenario: User agent option
- **WHEN** `--user-agent <string>` is provided
- **THEN** the system uses the specified user agent for requests

#### Scenario: Cache directory option
- **WHEN** `--cache-dir <path>` is provided
- **THEN** the system uses the specified directory for caching (default: .cache)

#### Scenario: Timeout option
- **WHEN** `--timeout <ms>` is provided
- **THEN** the system uses the specified timeout in milliseconds (default: 30000)

#### Scenario: Cookies file option
- **WHEN** `--cookies-file <path>` is provided
- **THEN** the system uses the Netscape cookie file for authenticated requests

#### Scenario: Output format option
- **WHEN** `--output <format>` is provided with "json", "markdown", or "both"
- **THEN** the system outputs in the specified format (default: markdown)

### Requirement: CLI Help and Version
The system SHALL provide help text and version information.

#### Scenario: Help display
- **WHEN** `--help` is provided or no command is given
- **THEN** the system displays usage information and available commands

#### Scenario: Version display
- **WHEN** `--version` is provided
- **THEN** the system displays the package version

