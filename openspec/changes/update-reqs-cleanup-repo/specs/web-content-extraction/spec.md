## ADDED Requirements

### Requirement: Fetch Web Content as Markdown
The system SHALL fetch web pages from HTTP/HTTPS URLs and convert them to clean Markdown format.

#### Scenario: Single page fetch
- **WHEN** a valid URL is provided
- **THEN** the system fetches the page content, extracts readable content using Mozilla Readability, converts HTML to Markdown, and returns the result

#### Scenario: Multiple pages fetch
- **WHEN** a URL is provided with pages parameter > 1
- **THEN** the system fetches the initial page, extracts links from the markdown, follows same-origin links up to the specified page limit, and combines all pages into a single markdown document with page separators

#### Scenario: Error handling
- **WHEN** a URL cannot be fetched or content cannot be extracted
- **THEN** the system returns an error message while still returning any partial content that was successfully extracted

### Requirement: Content Extraction Quality
The system SHALL extract clean, readable content using Mozilla Readability algorithm (same as Firefox Reader View).

#### Scenario: Noise removal
- **WHEN** a web page contains navigation, ads, and other non-content elements
- **THEN** the extracted markdown contains only the main article content without navigation, ads, or other noise

#### Scenario: Link preservation
- **WHEN** content contains links
- **THEN** all links are preserved in the markdown output with absolute URLs

### Requirement: Crawling Options
The system SHALL support configurable crawling behavior.

#### Scenario: Robots.txt respect
- **WHEN** respectRobots option is enabled (default)
- **THEN** the system checks and respects robots.txt rules before fetching pages

#### Scenario: Same-origin restriction
- **WHEN** sameOriginOnly option is enabled (default)
- **THEN** the system only follows links that are on the same origin as the initial URL

#### Scenario: Custom user agent
- **WHEN** a custom user agent is provided
- **THEN** the system uses that user agent for all HTTP requests

#### Scenario: Cookie support
- **WHEN** a cookiesFile path is provided
- **THEN** the system uses Netscape-format cookies for authenticated requests

### Requirement: Timeout and Concurrency
The system SHALL support configurable timeout and concurrency limits.

#### Scenario: Request timeout
- **WHEN** a request exceeds the configured timeout (default 30s)
- **THEN** the system aborts the request and returns an error

#### Scenario: Concurrency limit
- **WHEN** multiple pages are being fetched
- **THEN** the system respects the maxConcurrency limit (default 3) to avoid overwhelming servers

