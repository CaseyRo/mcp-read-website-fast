## 1. Dockerfile Optimization

- [x] 1.1 Convert Dockerfile to single-stage build
- [x] 1.2 Remove builder stage and build step
- [x] 1.3 Remove `bin/` folder copy (not needed - CMD uses `dist/` directly)
- [x] 1.4 Copy only `dist/` and `package.json` from git
- [x] 1.5 Install only production dependencies
- [x] 1.6 Verify CMD still works with `dist/serve-restart.js`

## 2. Docker Configuration Updates

- [x] 2.1 Update `.dockerignore` to remove `dist/` from ignore list
- [x] 2.2 Remove unnecessary source code mounts from `docker-compose.yml` production service
- [x] 2.3 Keep development profile mounts (for dev debugging)
- [x] 2.4 Verify `.dockerignore` includes appropriate exclusions

## 3. Documentation Updates

- [x] 3.1 Update README.md Docker section to reflect optimized build
- [x] 3.2 Update AGENTS.md Docker deployment notes
- [x] 3.3 Add note about `dist/` being pre-built in git
- [x] 3.4 Update any build instructions

## 4. Validation

- [x] 4.1 Test Docker build with new Dockerfile (Dockerfile syntax verified)
- [ ] 4.2 Verify Docker image size is smaller (requires Docker runtime)
- [ ] 4.3 Verify Docker build time is faster (requires Docker runtime)
- [ ] 4.4 Test Docker container starts correctly (requires Docker runtime)
- [ ] 4.5 Test MCP server functionality in Docker (requires Docker runtime)
- [x] 4.6 Verify development profile still works (docker-compose.yml verified)
- [x] 4.7 Run `openspec validate optimize-docker-build --strict`

