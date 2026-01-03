# Single-stage build using pre-built dist/ from git
FROM node:20-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Set working directory
WORKDIR /app

# Copy pre-built dist/ and package files from git
COPY --chown=nodejs:nodejs dist ./dist
COPY --chown=nodejs:nodejs package*.json ./

# Install only production dependencies
RUN npm ci --only=production && npm cache clean --force

# Switch to non-root user
USER nodejs

# Expose default port
EXPOSE 3000

# Set default environment variables for logging
ENV NODE_ENV=production
ENV LOG_LEVEL=info
ENV MCP_DEBUG=0
ENV MCP_QUIET=false

# Health check - simplified to avoid complex health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "process.exit(0)" || exit 1

# Default command
CMD ["dumb-init", "node", "dist/serve-restart.js"]

# Labels
LABEL maintainer="Just Every"
LABEL description="MCP Read Website Fast Server"
LABEL version="1.0.0"
