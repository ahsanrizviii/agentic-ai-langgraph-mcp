"""Manim MCP server (stdio).

Tools
- draw_shape: render a simple shape from plain parameters. The server writes
  the Manim code itself, so even a small model gets a valid script.
- execute_manim_code: render a complete Manim script written by the caller.
- cleanup_manim_temp_dir: delete temporary render files (only inside ./media).

Never print to stdout here: stdout is the MCP protocol channel. Use stderr.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("manim-server")

# Path to the manim executable; falls back to whatever is on PATH.
MANIM_EXECUTABLE = os.getenv("MANIM_EXECUTABLE", "manim")

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
TMP_DIR = os.path.join(BASE_DIR, "manim_tmp")
os.makedirs(BASE_DIR, exist_ok=True)

RENDER_TIMEOUT = 150  # seconds


# --------------------------------------------------------------------------- #
# Shared renderer
# --------------------------------------------------------------------------- #
def _render_scene(manim_code: str) -> str:
    """Write manim_code to scene.py, render it, and describe the result."""
    os.makedirs(TMP_DIR, exist_ok=True)
    script_path = os.path.join(TMP_DIR, "scene.py")

    # Strip markdown fences some models wrap around code.
    fenced = re.search(r"```(?:python|py)?[ \t]*\n(.*?)```", manim_code, re.DOTALL)
    if fenced:
        manim_code = fenced.group(1)

    # Small models often forget the import; add it if missing.
    if "import manim" not in manim_code and "from manim" not in manim_code:
        manim_code = "from manim import *\n\n" + manim_code

    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(manim_code)

        result = subprocess.run(
            [MANIM_EXECUTABLE, "-pql", script_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=TMP_DIR,
            stdin=subprocess.DEVNULL,  # never wait for interactive input
            timeout=RENDER_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"Execution failed: render timed out after {RENDER_TIMEOUT} s."
    except Exception as e:
        return f"Error during execution: {e}"

    if result.returncode != 0:
        return f"Execution failed: {result.stderr[-1500:]}"

    videos = glob.glob(os.path.join(TMP_DIR, "media", "videos", "**", "*.mp4"), recursive=True)
    latest = max(videos, key=os.path.getmtime) if videos else "(not found)"
    print(f"Video: {latest}", file=sys.stderr)
    return f"Execution successful. Video generated: {latest}"


# --------------------------------------------------------------------------- #
# draw_shape: the server writes the Manim code, so the model only picks options
# --------------------------------------------------------------------------- #
_SHAPES = {
    "circle": "Circle(radius=1.5)",
    "square": "Square(side_length=3)",
    "triangle": "Triangle()",
    "rectangle": "Rectangle(width=4, height=2.5)",
    "pentagon": "RegularPolygon(n=5)",
    "hexagon": "RegularPolygon(n=6)",
    "star": "Star()",
}
_COLORS = ["blue", "red", "green", "yellow", "orange", "purple", "pink", "white"]
_ANIMATIONS = {
    "create": "Create(obj)",
    "fade_in": "FadeIn(obj)",
    "grow": "GrowFromCenter(obj)",
}


def build_shape_code(shape: str, color: str, animation: str) -> str:
    """Return Manim source for a shape, or raise ValueError for bad options."""
    shape = shape.strip().lower()
    color = color.strip().lower()
    animation = animation.strip().lower()
    if shape not in _SHAPES:
        raise ValueError(f"Unknown shape '{shape}'. Choose from: {', '.join(_SHAPES)}.")
    if color not in _COLORS:
        raise ValueError(f"Unknown color '{color}'. Choose from: {', '.join(_COLORS)}.")
    if animation not in _ANIMATIONS:
        raise ValueError(f"Unknown animation '{animation}'. Choose from: {', '.join(_ANIMATIONS)}.")
    # Only whitelisted values reach the generated code, so tool arguments
    # can never inject arbitrary Python.
    return (
        "from manim import *\n\n"
        "class DrawShape(Scene):\n"
        "    def construct(self):\n"
        f"        obj = {_SHAPES[shape]}\n"
        f"        obj.set_color({color.upper()})\n"
        f"        self.play({_ANIMATIONS[animation]})\n"
        "        self.wait(0.5)\n"
    )


@mcp.tool()
def draw_shape(shape: str = "circle", color: str = "blue", animation: str = "create") -> str:
    """Draw a simple shape and render it to a video.

    shape: circle, square, triangle, rectangle, pentagon, hexagon, or star.
    color: blue, red, green, yellow, orange, purple, pink, or white.
    animation: create, fade_in, or grow.
    Use this for simple shapes instead of execute_manim_code.
    """
    try:
        code = build_shape_code(shape, color, animation)
    except ValueError as e:
        return f"Execution failed: {e}"
    return _render_scene(code)


# --------------------------------------------------------------------------- #
# execute_manim_code: for complete, hand-written scripts
# --------------------------------------------------------------------------- #
@mcp.tool()
def execute_manim_code(manim_code: str) -> str:
    """Render a complete Manim script to a video.

    manim_code must be a full multi-line Python script with proper indentation:
    start with `from manim import *`, define exactly one Scene subclass whose
    name is NOT a Manim class name (never call it Circle or Triangle), and put
    self.play(...) calls inside construct(self). For plain shapes, prefer the
    draw_shape tool.
    """
    if "\n" not in manim_code.strip() and "class " in manim_code:
        return (
            "Execution failed: the code has no line breaks. Send it as a multi-line "
            "Python script with correct indentation, or use the draw_shape tool."
        )
    return _render_scene(manim_code)


# --------------------------------------------------------------------------- #
# Cleanup (restricted to this server's media folder)
# --------------------------------------------------------------------------- #
@mcp.tool()
def cleanup_manim_temp_dir(directory: str = "") -> str:
    """Delete Manim temporary render files. Only paths inside this server's media folder are allowed."""
    target = os.path.abspath(directory) if directory else TMP_DIR
    base = os.path.abspath(BASE_DIR)
    try:
        inside = os.path.commonpath([target, base]) == base
    except ValueError:  # e.g. different drives on Windows
        inside = False
    if not inside:
        return f"Refused: {target} is outside the media folder."
    try:
        if os.path.exists(target):
            shutil.rmtree(target)
            return f"Cleanup successful for directory: {target}"
        return f"Directory not found: {target}"
    except Exception as e:
        return f"Failed to clean up directory: {target}. Error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")