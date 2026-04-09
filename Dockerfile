FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY mcp_read_website/ ./mcp_read_website/

RUN pip install --no-cache-dir . && \
    python -m crawl4ai.install && \
    playwright install --with-deps chromium && \
    addgroup --system mcp && adduser --system --home /home/mcp --ingroup mcp mcp && \
    mkdir -p /data/fastmcp /home/mcp/.crawl4ai && \
    chown -R mcp:mcp /data /home/mcp

USER mcp

ENV TRANSPORT=http
ENV HOST=0.0.0.0
ENV HOME=/home/mcp
ENV CRAWL4AI_DB_FOLDER=/data/fastmcp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "from urllib.request import urlopen;from urllib.error import HTTPError,URLError;exec('try:\n urlopen(\"http://localhost:8000/mcp\")\nexcept HTTPError:\n pass\nexcept URLError:\n raise')"

CMD ["mcp-read-website-fast"]
