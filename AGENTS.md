# Agent Notes

## Reasoning

- Introduced an `MCP_TRANSPORT` environment variable so the server can switch between stdio and Streamable HTTP transports. Stdio remains the default for compatibility.
- When `MCP_TRANSPORT=streamable-http`, a lightweight HTTP server is created and requests are passed to the MCP transport. The port can be configured via `PORT` (defaults to `3000`).
- README and CLI help now document how to launch the server with the Streamable HTTP transport for clients that can't use stdio.
- Added a `--port` flag so the HTTP port can be set directly when launching via `npx`, which maps to the same `PORT` environment variable.

These notes explain why the environment variable exists and how to run the server in each mode.
