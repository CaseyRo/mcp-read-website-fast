## MODIFIED Requirements

### Requirement: Docker Image Build Process
The Docker image SHALL be built using a single-stage process that copies pre-built `dist/` folder from git and installs only production dependencies.

#### Scenario: Docker build with pre-built dist
- **WHEN** Docker build is executed
- **THEN** the build process copies `dist/` and `package.json` from the repository
- **THEN** only production dependencies are installed
- **THEN** no TypeScript compilation or build step is performed
- **THEN** the resulting image contains only runtime files

#### Scenario: Docker image contents
- **WHEN** the Docker image is inspected
- **THEN** it contains `dist/` folder with compiled JavaScript
- **THEN** it contains `package.json` for dependency management
- **THEN** it does NOT contain `src/` source code
- **THEN** it does NOT contain `bin/` wrapper script (not needed for Docker)
- **THEN** it does NOT contain build tools or dev dependencies

#### Scenario: Docker container startup
- **WHEN** the Docker container starts
- **THEN** it executes `dist/serve-restart.js` directly
- **THEN** the MCP server starts successfully
- **THEN** the server listens on the configured port

## REMOVED Requirements

### Requirement: Multi-Stage Docker Build
**Reason**: Since `dist/` is now committed to git, a multi-stage build with TypeScript compilation is no longer needed. A single-stage build using pre-built `dist/` is simpler and faster.

**Migration**: Docker builds will now use the pre-built `dist/` folder from git instead of building from source.

### Requirement: Build Tools in Docker Image
**Reason**: With pre-built `dist/`, build tools (TypeScript compiler, dev dependencies) are no longer needed in the Docker image.

**Migration**: Build tools are removed from the Docker image. All builds happen before committing to git.

