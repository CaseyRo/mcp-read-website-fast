## ADDED Requirements

### Requirement: Disk-Based Caching
The system SHALL cache fetched content on disk using SHA-256 hashed URLs as cache keys.

#### Scenario: Cache storage
- **WHEN** a URL is fetched successfully
- **THEN** the system stores the result in the cache directory using a SHA-256 hash of the normalized URL as the filename

#### Scenario: Cache retrieval
- **WHEN** a URL is requested that has been cached
- **THEN** the system returns the cached content instead of making a new network request

#### Scenario: Cache directory configuration
- **WHEN** a cache directory is specified (via CLI option or default .cache)
- **THEN** the system uses that directory for all cache operations

### Requirement: Cache Management
The system SHALL provide mechanisms to inspect and clear the cache.

#### Scenario: Cache statistics
- **WHEN** cache status is requested (via MCP resource or CLI)
- **THEN** the system returns information about cache size, file count, and formatted size

#### Scenario: Cache clearing
- **WHEN** cache clear is requested
- **THEN** the system removes all cached files and directories

### Requirement: URL Normalization for Caching
The system SHALL normalize URLs before hashing to ensure consistent cache keys.

#### Scenario: URL normalization
- **WHEN** the same URL is requested with different formats (trailing slash, query params, etc.)
- **THEN** the system normalizes the URL before hashing to maximize cache hits

