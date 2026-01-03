## Context

The product is exclusively deployed via Docker containers. The current Dockerfile uses a multi-stage build:
1. **Builder stage**: Installs all dependencies (including dev), copies source, builds TypeScript
2. **Production stage**: Copies built `dist/`, `bin/`, and `package.json`, installs only production deps

Since `dist/` is now committed to git, we can optimize this significantly.

## Goals / Non-Goals

### Goals
- Eliminate build step from Docker (use pre-built `dist/` from git)
- Simplify Dockerfile to single-stage build
- Reduce Docker image size (remove build tools, dev dependencies, source code)
- Speed up Docker builds (no TypeScript compilation)
- Remove unnecessary files from Docker image (`bin/` folder not needed)

### Non-Goals
- Supporting standalone/npm package deployment (Docker-only)
- Maintaining backward compatibility with old Docker images
- Supporting development mode in Docker (keep dev profile for that)

## Decisions

### Decision: Use Pre-Built `dist/` from Git
**Rationale**: Since `dist/` is now committed to git, we can use it directly without building. This eliminates the need for:
- TypeScript compiler in Docker
- Dev dependencies in Docker
- Source code in Docker
- Multi-stage build complexity

**Alternatives considered**:
1. Keep multi-stage build but optimize it - Rejected: Still slower and more complex than needed
2. Build in CI and copy artifact - Rejected: Adds CI complexity, git approach is simpler

### Decision: Remove `bin/` Folder from Docker
**Rationale**: The Dockerfile CMD already uses `dist/serve-restart.js` directly. The `bin/` folder is only needed for npm package users (not Docker). Removing it reduces image size and complexity.

**Alternatives considered**:
1. Keep `bin/` for consistency - Rejected: Unnecessary for Docker-only deployment
2. Use `bin/` as entry point - Rejected: Adds indirection, CMD already works with `dist/`

### Decision: Single-Stage Build
**Rationale**: With pre-built `dist/`, we only need:
- Copy `dist/` and `package.json`
- Install production dependencies
- Run the server

No need for builder stage, build tools, or source code.

**Alternatives considered**:
1. Keep multi-stage for "clean" separation - Rejected: Unnecessary complexity for Docker-only
2. Conditional build (build if dist missing) - Rejected: Adds complexity, dist should always be in git

### Decision: Update `.dockerignore` to Include `dist/`
**Rationale**: Since `dist/` is now committed to git and we want to use it in Docker, we need to remove it from `.dockerignore`.

**Alternatives considered**:
1. Keep `dist/` ignored and build in Docker - Rejected: Defeats the purpose of committing dist
2. Copy `dist/` explicitly in Dockerfile - Rejected: `.dockerignore` should reflect what we want

## Risks / Trade-offs

### Risks
- **Outdated `dist/` in git**: If `dist/` is committed but source changed, Docker will run old code
  - **Mitigation**: Ensure `dist/` is always rebuilt and committed before Docker builds
  - **Mitigation**: CI/CD should verify `dist/` matches source

- **Larger git repository**: Committing `dist/` increases repo size
  - **Mitigation**: `dist/` is only ~60KB, acceptable trade-off for faster Docker builds

### Trade-offs
- **Simplicity vs Flexibility**: Choosing simplicity (single-stage, pre-built) over flexibility (build anywhere)
- **Git size vs Build speed**: Trading slightly larger git repo for much faster Docker builds
- **Docker-only vs Universal**: Optimizing for Docker-only deployment (acceptable given requirement)

## Migration Plan

### For Users
1. **No changes needed**: Docker images work the same way, just built differently
2. **Faster builds**: Users will notice faster `docker build` times
3. **Smaller images**: Users will get smaller Docker images

### Code Changes
1. Simplify `Dockerfile` to single-stage build
2. Update `.dockerignore` to include `dist/`
3. Remove `bin/` copy from Dockerfile
4. Update `docker-compose.yml` to remove unnecessary source mounts
5. Update documentation

### Rollback
If needed, can revert to previous multi-stage Dockerfile. The old approach still works.

## Open Questions

- Should we add a CI check to ensure `dist/` matches source before Docker builds?
- Should we document the requirement to rebuild `dist/` before committing?

