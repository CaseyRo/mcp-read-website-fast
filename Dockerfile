FROM python:3.12-slim

WORKDIR /app

# ca-certificates: fastmcp 4 (httpx2 + truststore) verifies TLS against the OS trust store.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md ./
COPY mcp_read_website/ ./mcp_read_website/

# Bake git commit into the image
ARG GIT_COMMIT=unknown
RUN echo "${GIT_COMMIT}" > /app/.git_commit

RUN pip install --no-cache-dir uv && \
    uv export --frozen --no-dev --no-emit-project -o /tmp/requirements.txt && \
    pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt && \
    pip install --no-cache-dir --no-deps . && \
    rm /tmp/requirements.txt && \
    python -m crawl4ai.install && \
    addgroup --system mcp && adduser --system --home /home/mcp --ingroup mcp mcp && \
    mkdir -p /data/fastmcp /home/mcp/.crawl4ai && \
    chown -R mcp:mcp /data /home/mcp

# Install Playwright browsers AS the mcp user so binaries land in /home/mcp/.cache/ms-playwright/
USER mcp
ENV PLAYWRIGHT_BROWSERS_PATH=/home/mcp/.cache/ms-playwright
RUN playwright install chromium

# Switch back to root to install system deps, then back to mcp
USER root
RUN playwright install-deps chromium

USER mcp

# Release version (the git tag); /health reports it. Unset → pyproject version.
ARG APP_VERSION=""
ENV APP_VERSION=$APP_VERSION

ENV TRANSPORT=http
ENV HOST=0.0.0.0
ENV HOME=/home/mcp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python3 -c "import urllib.request,json,sys; r=urllib.request.urlopen('http://localhost:8000/health',timeout=3); d=json.loads(r.read()); sys.exit(0 if d.get('status')=='healthy' else 1)"

CMD ["mcp-read-website-fast"]
