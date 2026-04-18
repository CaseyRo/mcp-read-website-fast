FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY mcp_read_website/ ./mcp_read_website/

RUN pip install --no-cache-dir . && \
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

ENV TRANSPORT=http
ENV HOST=0.0.0.0
ENV HOME=/home/mcp
ENV CRAWL4AI_DB_FOLDER=/data/fastmcp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python3 -c "import urllib.request,json,sys; r=urllib.request.urlopen('http://localhost:8000/health',timeout=3); d=json.loads(r.read()); sys.exit(0 if d.get('status')=='healthy' else 1)"

CMD ["mcp-read-website-fast"]
