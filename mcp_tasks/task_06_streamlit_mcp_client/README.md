# Task 06 — Streamlit Multi-Server MCP Client

A chat UI that connects a local **Llama 3.2** model (via Ollama) to **five MCP servers at once** — four local stdio servers and one deployed remote server — and lets the model decide which tools to call.

<p align="center">
  <img src="../../screenshots/homepage.png" alt="Streamlit MCP client" width="900">
</p>

## Connected servers

| Server name | Source | Transport |
|---|---|---|
| `custom-tools` | [Task 01](../task_01_custom_tools_server) | stdio (local) |
| `manim-server` | [Task 02](../task_02_manim_mcp_server) | stdio (local, own venv) |
| `weather` | [Task 03](../task_03_weather_mcp_server) | stdio (local) |
| `ddg-search` | [Task 04](../task_04_duckduckgo_mcp_server) | stdio via `npx` (local) |
| `custom-tools-remote` | [Task 05](../task_05_deploy_horizon) | streamable HTTP (deployed) |

## Features

- **Pre-flight validation** — every server's command, script and executable paths are checked before connecting. A missing server shows up as a warning in the sidebar instead of crashing the app.
- **Fault isolation** — each server loads with its own timeout (300 s for the remote server, 90 s for local ones); one failing server never blocks the rest.
- **Name-clash handling** — remote tools are prefixed `remote_`, and any remaining duplicate names are namespaced by server.
- **Bounded agent loop** — up to 4 tool rounds per message and a 180 s timeout per tool call, then a final answer from the model.
- **Transparent tool calls** — every call is shown in an expander with its arguments, output and success/failure status, and tool output is HTML-escaped before rendering.
- **Honest failures** — the system prompt tells the model to report a tool's exact error text and never invent results.
- **Live sidebar** — connected servers with LOCAL / DEPLOYED badges, their tools, and any skipped or failed servers with the reason.

## Setup

```bash
cd mcp_tasks/task_06_streamlit_mcp_client
pip install -r requirements.txt
cp .env.example .env      # add ACCUWEATHER_API_KEY and FASTMCP_TOKEN
ollama pull llama3.2
```

> **Keep this client and FastMCP 4.x in separate environments.** `langchain-mcp-adapters` needs `mcp<2`, while FastMCP 4.x installs `mcp>=2`. The client reaches the remote server with a Bearer token (`FASTMCP_TOKEN`), so it doesn't need FastMCP itself.

The local servers must be set up first (see each task's README):

- **Task 01** is launched with the `python` on your `PATH`, which must have FastMCP installed. If you run this client from its own virtual environment, set `CUSTOM_TOOLS_PYTHON` to a Python that has FastMCP (for example your global Python).
- **Task 02** is launched from its own `.venv` (Windows layout: `.venv\Scripts\python.exe`).
- **Task 03** is found through the `mcp-weather` command registered by `pip install -e .`.

The client looks for the servers relative to this folder; set `MCP_TASKS_DIR` to point somewhere else.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `ACCUWEATHER_API_KEY` | No | Enables the `weather` server; skipped when unset |
| `FASTMCP_TOKEN` | No | Bearer token for the Horizon server |
| `SKIP_REMOTE` | No | Set to `1` to skip the remote server |
| `OLLAMA_MODEL` | No | Defaults to `llama3.2` |
| `CUSTOM_TOOLS_PYTHON` | No | Python used to launch the Task 01 server; defaults to `python` on `PATH` |
| `MCP_TASKS_DIR` | No | Folder containing the `task_0X` server folders |

## Run

```bash
ollama serve                 # if Ollama isn't already running
streamlit run app.py
```

## Example prompts

- *How old is someone born on 2001-03-14?*
- *Give me a random number between 1 and 50 using the remote server.*
- *What's the weather in Dhaka right now?*
- *Search the web for the latest LangGraph release.*
- *Draw a red hexagon that grows from the center.*
