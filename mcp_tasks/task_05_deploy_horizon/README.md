# Task 05 — Deploying an MCP Server to Prefect Horizon

The Task 01 custom-tools server, deployed as a **remote** MCP server on [Prefect Horizon](https://www.prefect.io/horizon) and served over **streamable HTTP**.

| Tool | Description |
|---|---|
| `calculate_age(date_of_birth)` | Age from a `YYYY-MM-DD` date of birth |
| `random_number(min_value, max_value)` | Random integer in an inclusive range |

**Endpoint:** `https://custom-tools-mcp.fastmcp.app/mcp`

## Deploy

Horizon deploys straight from a GitHub repository, so this folder (`main.py` + `requirements.txt`) also lives in its own repo that is connected to Horizon, with the `mcp` object in `main.py` as the server entrypoint. Horizon builds it and exposes it at a public HTTPS URL — no Dockerfile or hosting setup needed.

## Connect from Claude Desktop

Remote MCP servers are **not** added through `claude_desktop_config.json` — that file only supports local stdio servers. Add them in the app instead:

> **Settings → Connectors → Add → Custom → Web →** enter the URL above

The free plan allows one custom connector.

Claude Desktop connects to remote servers from Anthropic's cloud rather than from your machine, so the endpoint has to be publicly reachable — which Horizon handles automatically.

## Connect from the Streamlit client (Task 06)

The client registers this server as `custom-tools-remote` and prefixes its tools with `remote_` (`remote_calculate_age`, `remote_random_number`) so they never clash with the identical local tools. Authentication uses a Horizon token passed as a Bearer header — set `FASTMCP_TOKEN` in the client's `.env`.

## Run locally

```bash
pip install -r requirements.txt
python main.py
```
