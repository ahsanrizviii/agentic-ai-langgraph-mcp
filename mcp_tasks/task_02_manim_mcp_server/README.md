# Task 02 — Manim MCP Server (hardened fork)

An MCP server that turns tool calls into rendered [Manim](https://www.manim.community/) animations.

Adapted from [abhiemj/manim-mcp-server](https://github.com/abhiemj/manim-mcp-server) (MIT — see [`LICENSE.txt`](LICENSE.txt)). The server was substantially reworked so that small local models (Llama 3.2 via Ollama) can drive it reliably and safely.

<p align="center">
  <img src="../../assets/manim_circle_to_square.gif" alt="Circle-to-square animation rendered through the MCP server" width="480">
</p>
<p align="center"><em>Animation rendered end-to-end from a single chat prompt.</em></p>

## Tools

| Tool | Purpose |
|---|---|
| `draw_shape(shape, color, animation)` | Renders a simple shape. The **server** writes the Manim code from whitelisted options, so even a small model produces a valid script. |
| `execute_manim_code(manim_code)` | Renders a complete, caller-written Manim script. |
| `cleanup_manim_temp_dir(directory)` | Deletes temporary render files — **only** inside the server's own `media/` folder. |

Supported options for `draw_shape`: shapes `circle, square, triangle, rectangle, pentagon, hexagon, star` · colors `blue, red, green, yellow, orange, purple, pink, white` · animations `create, fade_in, grow`.

## Changes from the upstream server

| Area | Upstream | This version |
|---|---|---|
| Small-model support | Model must write a full Manim script | New `draw_shape` tool generates the script server-side |
| Code injection | — | Only whitelisted values reach the generated code |
| `cleanup_manim_temp_dir` | Deletes **any** directory path it is given | Refuses any path outside the server's `media/` folder |
| Hung renders | No timeout | 150 s render timeout, `stdin` closed so the process never waits for input |
| Model output quirks | Fails on fenced code or missing imports | Strips Markdown fences and adds `from manim import *` when missing |
| Single-line scripts | Opaque Manim error | Clear error asking for a multi-line script or `draw_shape` |
| stdio protocol safety | `print()` to stdout (corrupts the MCP stream) | All diagnostics go to stderr |
| Result | `"Video generated."` | Returns the path of the rendered `.mp4` |
| Render speed | Default quality | Low-quality preview (`-pql`) for fast feedback |

## Setup (Windows)

The server uses the MCP **v1** API (`from mcp.server.fastmcp import FastMCP`), while Task 01's FastMCP 4.x needs `mcp>=2`. The two conflict in one environment, so this task gets its own virtual environment with `mcp<2` pinned:

```powershell
cd mcp_tasks\task_02_manim_mcp_server
.\setup.ps1          # creates .venv and installs "mcp<2" + manim
```

or manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Manim also needs FFmpeg (and a LaTeX distribution only if you render `Tex`/`MathTex`). See the [Manim installation guide](https://docs.manim.community/en/stable/installation.html).

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\manim_server.py
```

The server speaks MCP over stdio, so no console output is expected.

## Claude Desktop

Use [`claude_config_snippet.json`](claude_config_snippet.json) — it points both `command` and `MANIM_EXECUTABLE` at this task's `.venv`. Replace the paths with the location of your clone.

## Test prompt

> Use the manim-server tool to create a simple animation of a circle turning into a square.

**Result:** the video rendered and opened in the default media player; output is written under `src/media/manim_tmp/media/videos/`.
