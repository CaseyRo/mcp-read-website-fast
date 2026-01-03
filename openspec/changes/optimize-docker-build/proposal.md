# Change: Optimize Docker Build for Docker-Only Deployment

## Why

The product is only deployed via Docker containers, never run standalone. The current Dockerfile uses a multi-stage build that:
- Installs all dependencies (including dev dependencies) to build TypeScript
- Builds the project from source
- Then installs only production dependencies in the final stage

Since `dist/` is now committed to git, we can optimize the Docker build to:
- Skip the build stage entirely (use pre-built `dist/` from git)
- Remove unnecessary `bin/` folder (not needed - CMD already uses `dist/serve-restart.js` directly)
- Simplify to single-stage build for faster builds and smaller images
- Update `.dockerignore` to include `dist/` since it's now committed

This will make Docker builds faster, simpler, and produce smaller images.

## What Changes

- **REMOVED**: Multi-stage build (builder stage no longer needed)
- **REMOVED**: `bin/` folder from Docker image (not needed - CMD uses `dist/` directly)
- **REMOVED**: TypeScript build step in Dockerfile (use pre-built `dist/` from git)
- **MODIFIED**: Dockerfile to single-stage build using pre-built `dist/`
- **MODIFIED**: `.dockerignore` to include `dist/` (remove it from ignore list)
- **MODIFIED**: `docker-compose.yml` to remove unnecessary source code mounts in production
- **MODIFIED**: Documentation to reflect Docker-only optimization

## Impact

- **Affected specs**:
  - `docker-deployment` capability - build process and image structure
- **Affected code**:
  - `Dockerfile` - Simplify to single-stage build
  - `.dockerignore` - Include `dist/` folder
  - `docker-compose.yml` - Remove unnecessary source mounts
  - `README.md` - Update Docker documentation
  - `AGENTS.md` - Update Docker deployment notes
- **Breaking changes**: **NO**
  - Docker images will work the same way, just built differently
  - No API or runtime changes
- **Performance improvements**:
  - Faster Docker builds (no TypeScript compilation)
  - Smaller Docker images (no build tools, dev dependencies, or source code)
  - Faster container startup (fewer layers to process)

