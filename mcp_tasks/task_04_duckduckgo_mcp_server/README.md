# Task 04 — DuckDuckGo Search MCP Server

Free web search for the agent — no API key, no account and no rate-limit sign-up.

- **npm package:** [`duckduckgo-websearch`](https://www.npmjs.com/package/duckduckgo-websearch)
- **Source:** [HeiSir2014/duckduckgo-mcp-server](https://github.com/HeiSir2014/duckduckgo-mcp-server)
- **Tools:** `search` (web search) and `fetch_content` (URL → readable text)

## Why this server

- No API key or account required.
- **Node.js based**, so it adds no Python dependency conflicts alongside Tasks 01 and 02.
- The similarly named npm package `duckduckgo-mcp` requires the Bun runtime; `duckduckgo-websearch` is the Node equivalent.

## Setup

1. Check Node.js 18+ is installed: `node --version`
2. Add the entry from [`claude_config_snippet.json`](claude_config_snippet.json) to `claude_desktop_config.json`:

   ```json
   "ddg-search": { "command": "npx", "args": ["-y", "duckduckgo-websearch"] }
   ```

`npx` downloads and starts the server on demand, so nothing else needs installing. The Streamlit client (Task 06) launches it the same way.

## Test prompts

- *Use the ddg-search tool to search for "latest AI news 2026".*
- *Use the fetch_content tool to read https://example.com*
