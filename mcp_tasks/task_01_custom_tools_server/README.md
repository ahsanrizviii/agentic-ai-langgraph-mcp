# Task 01 — Custom Tools MCP Server

A minimal MCP server built with **FastMCP 4.x** that exposes two tools over **stdio**.

| Tool | Signature | Notes |
|---|---|---|
| `calculate_age` | `calculate_age(date_of_birth: str) -> int` | Input format `YYYY-MM-DD`; handles birthdays that haven't happened yet this year |
| `random_number` | `random_number(min_value: int, max_value: int) -> int` | Inclusive range |

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
# Inspect the server and call a tool from the CLI
fastmcp inspect main.py
fastmcp call main.py calculate_age date_of_birth=2000-01-15

# Browser-based MCP Inspector (requires uv)
fastmcp dev inspector main.py

# stdio mode (silent — this is what Claude Desktop launches)
python main.py
```

## Claude Desktop

Add the entry from [`claude_config_snippet.json`](claude_config_snippet.json) to the `mcpServers` block of `claude_desktop_config.json`, replacing the path with the location of your clone.

## Test results

Verified through the FastMCP Inspector UI:

| Call | Result |
|---|---|
| `calculate_age("2000-01-15")` | `26` |
| `calculate_age("1995-06-15")` | `31` |
| `calculate_age("2026-09-19")` | `0` (born yesterday) |
| `random_number(5, 5)` | `5` (edge case: min = max) |
| `random_number(1, 100)` | integer in `[1, 100]` |

## Known Claude Desktop behaviour

Claude Desktop loads MCP tools lazily ("deferred loading"). A natural-language question such as *"how old is someone born in 2000?"* may be answered with Claude's own arithmetic instead of a tool call. Phrasing the request explicitly — *"Use the calculate_age tool to…"* — loads and runs the tool. This is documented client behaviour, not a configuration problem.
