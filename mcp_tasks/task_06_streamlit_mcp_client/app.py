import asyncio
import json
import os
import re
import shutil
from collections import Counter
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------- Design ----------------------------
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root{--bg:#f4fbf7;--white:#fff;--line:#d9eee2;--line2:#b7dcc8;--ink:#17352a;--muted:#5d776a;--green:#75c49b;--dark:#4ea978;--deep:#2f7d59;--soft:#e9f7ef;--sm:0 8px 24px rgba(54,116,83,.08);--md:0 16px 40px rgba(54,116,83,.12);--lg:0 26px 70px rgba(54,116,83,.15)}
    html,body,[class*="css"],.stApp{font-family:"DM Sans",Arial,sans-serif;color:var(--ink)}
    .stApp{background:radial-gradient(circle at 8% 0%,rgba(168,230,194,.26),transparent 27%),radial-gradient(circle at 94% 5%,rgba(117,196,155,.18),transparent 30%),linear-gradient(180deg,#f7fcf9 0%,var(--bg) 38%,#eef8f2 100%)}
    [data-testid="stHeader"]{background:transparent}.block-container{max-width:1500px;padding:2.1rem 3.2rem 4rem}
    @keyframes fadeUp{from{opacity:0;transform:translateY(15px)}to{opacity:1;transform:translateY(0)}}.animate-in{animation:fadeUp .5s cubic-bezier(.16,1,.3,1) forwards}
    .topbar{position:relative;overflow:hidden;background:linear-gradient(115deg,#eefaf3 0%,#d9f2e3 46%,#c9ecd8 100%);border:1px solid rgba(255,255,255,.86);box-shadow:var(--lg);border-radius:28px 28px 18px 18px;margin:0 0 1.5rem;padding:1.35rem 1.7rem 1.25rem;display:flex;align-items:baseline;gap:1rem}
    .topbar:after{content:"";position:absolute;width:220px;height:220px;right:-80px;top:-120px;border-radius:50%;background:rgba(255,255,255,.28)}
    .mark{position:relative;z-index:1;color:#183b2b;font-family:Manrope,sans-serif;font-size:1.6rem;font-weight:800;letter-spacing:-.045em}.mark span{color:var(--deep)}
    .tag{position:relative;z-index:1;color:#5a7969;font-size:.85rem;font-weight:600;border-left:1px solid #b9dcca;padding-left:1rem}
    section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(243,251,246,.97),rgba(236,247,241,.97));border-right:1px solid var(--line)}section[data-testid="stSidebar"]>div{padding-top:1.4rem}section[data-testid="stSidebar"] .stButton>button{width:100%}
    .tool-title{font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:800;margin:.1rem 0 .65rem}.tool-subtitle{color:var(--muted);font-size:.82rem;margin-bottom:1rem}
    .server-card,.tool-event{border:1px solid var(--line);background:rgba(255,255,255,.76);border-radius:16px;box-shadow:var(--sm)}.server-card{padding:.72rem .75rem .62rem;margin-bottom:.72rem}
    .server-name-row{display:flex;align-items:center;justify-content:space-between;gap:.45rem;margin-bottom:.48rem}.server-name{font-family:Manrope,sans-serif;font-size:.87rem;font-weight:800;word-break:break-word}
    .server-badge,.tool-event-badge{display:inline-flex;align-items:center;border-radius:999px;font-size:.58rem;font-weight:800;letter-spacing:.06em;white-space:nowrap}.server-badge{gap:.3rem;padding:.2rem .52rem}.server-badge.local{background:#edf8f1;color:var(--deep);border:1px solid #cce6d6}.server-badge.remote{background:#ddf4e8;color:#256947;border:1px solid #a9d9bc}
    .server-transport{color:var(--muted);font-size:.66rem;font-weight:700;margin-bottom:.45rem}.server-tool{display:flex;align-items:center;gap:.45rem;padding:.28rem .35rem;border-radius:9px;color:var(--ink);font-size:.76rem;background:rgba(241,250,245,.72);margin-top:.24rem}.server-tool-dot{width:6px;height:6px;border-radius:50%;background:var(--green);flex:none}
    div[data-testid="stRadio"]>div[role="radiogroup"]{background:rgba(255,255,255,.72);border:1px solid rgba(183,220,200,.86);box-shadow:var(--sm);border-radius:14px;padding:5px;display:flex;flex-wrap:wrap;gap:5px!important;justify-content:center;margin-bottom:1rem}div[data-testid="stRadio"] label{border-radius:10px;padding:6px 14px;font-size:.85rem;font-weight:600;color:#5c786b}div[data-testid="stRadio"] label:hover{background:var(--soft)}
    [data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px!important;box-shadow:var(--sm);background:var(--white)}
    [data-testid="stChatMessage"]{border:1px solid var(--line)!important;border-radius:20px!important;padding:1rem 1.1rem!important;margin-bottom:.9rem!important;box-shadow:var(--sm);background:rgba(255,255,255,.9)}[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){background:linear-gradient(135deg,#f1fbf5,#e4f6eb);border-color:#cbe7d6!important}[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]){background:rgba(255,255,255,.94)}[data-testid="stChatMessage"] p{line-height:1.6}[data-testid="stChatMessage"] pre{border:1px solid var(--line)!important;border-radius:12px!important;background:#f7fbf8!important}
    .tool-event{padding:.72rem .85rem;margin-bottom:.55rem}.tool-event-head{display:flex;align-items:center;gap:.45rem;flex-wrap:wrap;margin-bottom:.45rem}.tool-event-name{font-family:Manrope,sans-serif;font-size:.8rem;font-weight:800}.tool-event-badge{padding:.18rem .45rem;background:var(--soft);color:var(--deep);border:1px solid #cce6d6}.tool-event-label{color:var(--muted);font-size:.65rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:.5rem 0 .25rem}.tool-output{border:1px solid var(--line);border-radius:10px;background:#f5fbf7;padding:.6rem .68rem;font-family:Consolas,'SFMono-Regular',monospace;font-size:.72rem;line-height:1.48;color:#274438;white-space:pre-wrap;word-break:break-word;max-height:340px;overflow:auto}
    .stButton>button{border-radius:999px!important;border:1px solid var(--line2)!important;background:var(--white)!important;color:var(--deep)!important;font-weight:700!important;font-size:.82rem!important;padding:.45rem 1rem!important;box-shadow:var(--sm)!important;transition:all .2s cubic-bezier(.16,1,.3,1)!important}.stButton>button:hover{background:var(--dark)!important;color:#fff!important;border-color:var(--dark)!important;transform:translateY(-2px);box-shadow:var(--md)!important}
    div[data-testid="stTextInput"] input,div[data-testid="stChatInput"] textarea,div[data-testid="stSelectbox"]>div>div{border-radius:14px!important;border:1px solid var(--line2)!important;background:rgba(255,255,255,.9)!important}div[data-testid="stTextInput"] input:focus,div[data-testid="stChatInput"] textarea:focus{border-color:var(--dark)!important;box-shadow:0 0 0 2px rgba(78,169,120,.12),var(--sm)!important}div[data-testid="stAlert"]{border-radius:14px!important;box-shadow:var(--sm)}hr{border-color:var(--line)!important}
    @media(max-width:900px){.block-container{padding:1.25rem 1rem 3rem}.topbar{padding:1.15rem;border-radius:22px 22px 16px 16px;align-items:flex-start;flex-direction:column;gap:.35rem}.tag{border-left:0;border-top:1px solid #b9dcca;padding:.45rem 0 0}}
    @media(prefers-reduced-motion:reduce){.animate-in{animation:none}.stButton>button{transition:none!important}}
    </style>
    """, unsafe_allow_html=True)


def render_topbar():
    st.markdown('<div class="topbar animate-in"><div class="mark">MCP<span> Client</span></div><div class="tag">Multi-Server Chat · LangChain + Ollama</div></div>', unsafe_allow_html=True)


# ---------------------------- Config ----------------------------
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3.2")
# Folder that holds the task_0X server folders (defaults to this repo's mcp_tasks/).
BASE = Path(os.environ.get("MCP_TASKS_DIR", Path(__file__).resolve().parent.parent))
SERVER_LOAD_TIMEOUT = 90
SERVER_TIMEOUTS = {"custom-tools-remote": 300}
REMOTE_URL = "https://custom-tools-mcp.fastmcp.app/mcp"
TOOL_PREFIXES = {"custom-tools-remote": "remote_"}
TOOL_TIMEOUT = 180
MAX_TOOL_ROUNDS = 4
SERVER_TYPES = {
    "custom-tools": ("LOCAL", "STDIO"),
    "manim-server": ("LOCAL", "STDIO"),
    "weather": ("LOCAL", "STDIO"),
    "ddg-search": ("LOCAL", "STDIO"),
    "custom-tools-remote": ("DEPLOYED", "STREAMABLE HTTP"),
}

SYSTEM_PROMPT = (
    "You have access to tools. When the user asks about age, random numbers, "
    "weather, web search, or animations, call the relevant tool instead of "
    "answering from memory. After a tool returns a result, use that result to "
    "answer the user's question directly. Do not merely say that you used a tool. "
    "Give the actual answer or useful information returned by the tool. Mention "
    "which tool you used when useful, but never replace the answer with only the "
    "tool name. Tools whose names start with 'remote_' run on the deployed remote "
    "server. Use them only when the user asks for the remote or deployed server; "
    "otherwise use the local tools. To draw a simple shape, call draw_shape; use "
    "execute_manim_code only for custom animations. If a tool fails, tell the user "
    "the exact error text it returned. Never invent results and never substitute "
    "ASCII art or made-up output."
)


def server_info(name):
    return SERVER_TYPES.get(name, ("MCP", "UNKNOWN"))


def escape(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


@st.cache_resource(show_spinner=False)
def get_remote_oauth(url):
    from fastmcp.client.auth import OAuth
    return OAuth(
        mcp_url=url,
        client_name="MCP Streamlit Chat",
        additional_client_metadata={
            "token_endpoint_auth_method": os.environ.get("REMOTE_AUTH_METHOD", "client_secret_post")
        },
    )


# ---------------------------- Servers ----------------------------
def build_servers():
    servers = {}
    skipped = {}

    servers["custom-tools"] = {
        "transport": "stdio",
        # Needs a Python with FastMCP 4.x, which can't share an environment with this client.
        "command": os.environ.get("CUSTOM_TOOLS_PYTHON", "python"),
        "args": [str(BASE / "task_01_custom_tools_server" / "main.py")],
    }

    manim = BASE / "task_02_manim_mcp_server"
    servers["manim-server"] = {
        "transport": "stdio",
        "command": str(manim / ".venv" / "Scripts" / "python.exe"),
        "args": [str(manim / "src" / "manim_server.py")],
        "env": {"MANIM_EXECUTABLE": str(manim / ".venv" / "Scripts" / "manim.exe")},
    }

    weather_key = os.environ.get("ACCUWEATHER_API_KEY")
    if weather_key:
        servers["weather"] = {
            "transport": "stdio",
            "command": shutil.which("mcp-weather") or str(Path.home() / "AppData/Local/Programs/Python/Python313/Scripts/mcp-weather.exe"),
            "args": [],
            "env": {"ACCUWEATHER_API_KEY": weather_key},
        }
    else:
        skipped["weather"] = "ACCUWEATHER_API_KEY is not set"

    servers["ddg-search"] = {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "duckduckgo-websearch"],
    }

    token = os.environ.get("FASTMCP_TOKEN")
    if os.environ.get("SKIP_REMOTE") == "1":
        skipped["custom-tools-remote"] = "SKIP_REMOTE=1"
    elif token:
        servers["custom-tools-remote"] = {
            "transport": "streamable_http",
            "url": REMOTE_URL,
            "headers": {"Authorization": f"Bearer {token}"},
        }
    else:
        try:
            servers["custom-tools-remote"] = {
                "transport": "streamable_http",
                "url": REMOTE_URL,
                "auth": get_remote_oauth(REMOTE_URL),
            }
        except ImportError:
            skipped["custom-tools-remote"] = "OAuth needs fastmcp in the Streamlit environment: pip install fastmcp"

    good = {}
    for name, spec in servers.items():
        problems = validate_server(spec)
        if problems:
            skipped[name] = "; ".join(problems)
        else:
            good[name] = spec
    return good, skipped


def validate_server(spec):
    problems = []
    transport = spec.get("transport")

    if transport == "stdio":
        spec.setdefault("args", [])
        command = spec.get("command")
        if not command:
            problems.append("missing 'command'")
        elif shutil.which(command):
            spec["command"] = shutil.which(command)
        elif not Path(command).exists():
            problems.append(f"command not found: {command}")

        for arg in spec["args"]:
            if isinstance(arg, str) and arg.lower().endswith(".py") and not Path(arg).exists():
                problems.append(f"script not found: {arg}")

        for key, value in spec.get("env", {}).items():
            if key.endswith("EXECUTABLE") and not Path(value).exists():
                problems.append(f"{key} not found: {value}")

    elif transport in ("streamable_http", "sse"):
        if not spec.get("url"):
            problems.append("missing 'url'")
    else:
        problems.append(f"unsupported transport: {transport!r}")

    return problems


# ---------------------------- Helpers ----------------------------
def error_list(error):
    if isinstance(error, BaseExceptionGroup):
        result = []
        for item in error.exceptions:
            result.extend(error_list(item))
        return result
    return [error]


def describe_error(error):
    return " | ".join(
        "TimeoutError: no response in time" if isinstance(item, TimeoutError)
        else f"{type(item).__name__}: {item}"
        for item in error_list(error)
    )


def friendly_error(error):
    message = describe_error(error)
    if any(x in message.lower() for x in ("connect", "refused", "11434")):
        message += f"\n\nCould not reach Ollama. Make sure it is running (`ollama serve`) and the model is pulled (`ollama pull {MODEL_NAME}`)."
    return message


def result_to_text(result):
    if isinstance(result, tuple) and result:
        result = result[0]
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        text = []
        for item in result:
            if isinstance(item, str):
                text.append(item)
            elif isinstance(item, dict) and item.get("text"):
                text.append(item["text"])
            elif getattr(item, "text", None):
                text.append(item.text)
        if text:
            return "\n".join(text)
    try:
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception:
        return str(result)


def apply_prefix(server, tools):
    prefix = TOOL_PREFIXES.get(server)
    if not prefix:
        return tools
    return [
        tool.model_copy(update={
            "name": prefix + tool.name,
            "description": f"[deployed remote server] {tool.description}",
        })
        for tool in tools
    ]


def resolve_clashes(tools_by_server):
    counts = Counter(tool.name for tools in tools_by_server.values() for tool in tools)
    for server, tools in tools_by_server.items():
        for i, tool in enumerate(tools):
            if counts[tool.name] > 1:
                server_name = re.sub(r"[^0-9a-zA-Z]+", "_", server).strip("_")
                tools[i] = tool.model_copy(update={"name": f"{server_name}_{tool.name}"})


async def load_tools(client, server_names):
    by_server, by_name, failed, warnings = {}, {}, {}, []

    for name in server_names:
        try:
            tools = await asyncio.wait_for(
                client.get_tools(server_name=name),
                timeout=SERVER_TIMEOUTS.get(name, SERVER_LOAD_TIMEOUT),
            )
        except Exception as error:
            failed[name] = describe_error(error)
            continue
        by_server[name] = apply_prefix(name, list(tools))

    resolve_clashes(by_server)

    for server, tools in by_server.items():
        kept = []
        for tool in tools:
            if tool.name in by_name:
                warnings.append(f"Duplicate tool '{tool.name}' from '{server}' ignored")
                continue
            by_name[tool.name] = tool
            kept.append(tool)
        by_server[server] = kept

    return by_server, by_name, failed, warnings


# ---------------------------- App ----------------------------
st.set_page_config(
    page_title="MCP Multi-Server Chat",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


def init_state():
    ss = st.session_state
    if ss.get("initialized"):
        return

    ss.loop = asyncio.new_event_loop()
    ss.llm = ChatOllama(model=MODEL_NAME, temperature=0)
    servers, skipped = build_servers()
    ss.skipped = skipped
    ss.tools_by_server = {}
    ss.tools_by_name = {}
    ss.failed = {}
    ss.warnings = []

    if servers:
        with st.spinner("Connecting to MCP servers..."):
            try:
                client = MultiServerMCPClient(servers)
                (ss.tools_by_server, ss.tools_by_name, ss.failed, ss.warnings) = \
                    ss.loop.run_until_complete(load_tools(client, list(servers)))
            except Exception as error:
                ss.failed = {"(client setup)": describe_error(error)}

    tools = list(ss.tools_by_name.values())
    ss.llm_with_tools = ss.llm.bind_tools(tools) if tools else ss.llm
    ss.history = [SystemMessage(content=SYSTEM_PROMPT)]
    ss.transcript = []
    ss.initialized = True


init_state()
ss = st.session_state
render_topbar()


# ---------------------------- Sidebar ----------------------------
with st.sidebar:
    st.markdown(
        '<div class="tool-title">Connected tools</div><div class="tool-subtitle">MCP servers and available tools</div>',
        unsafe_allow_html=True,
    )

    if not ss.tools_by_name:
        st.write("No tools loaded. The model will answer without tools.")

    for server, tools in ss.tools_by_server.items():
        scope, transport = server_info(server)
        badge = "remote" if scope == "DEPLOYED" else "local"
        icon = "↗" if scope == "DEPLOYED" else "●"
        rows = "".join(
            f'<div class="server-tool"><span class="server-tool-dot"></span><span>{escape(tool.name)}</span></div>'
            for tool in tools
        )
        st.markdown(
            f'<div class="server-card"><div class="server-name-row"><div class="server-name">{escape(server)}</div>'
            f'<span class="server-badge {badge}">{icon} {scope}</span></div>'
            f'<div class="server-transport">{transport} &nbsp;·&nbsp; {len(tools)} tool(s)</div>{rows}</div>',
            unsafe_allow_html=True,
        )

    for server, reason in ss.failed.items():
        scope, transport = server_info(server)
        st.error(f"**{server}** · {scope} · {transport}\n\n{reason}")

    for server, reason in ss.skipped.items():
        scope, transport = server_info(server)
        st.warning(f"**{server}** · {scope} · {transport}\n\n{reason}")

    for warning in ss.warnings:
        st.info(warning)

    st.divider()

    if st.button("Reload servers"):
        for key in list(ss.keys()):
            del ss[key]
        st.rerun()

    if st.button("Clear chat"):
        ss.history = [SystemMessage(content=SYSTEM_PROMPT)]
        ss.transcript = []
        st.rerun()


# ---------------------------- Chat history ----------------------------
def render_tool_events(events):
    for event in events:
        icon = "✅" if event["ok"] else "❌"
        name = event["name"]
        location = "DEPLOYED" if name.startswith("remote_") else "LOCAL"
        output = event.get("result") or "(empty output)"
        args = json.dumps(event["args"], indent=2, ensure_ascii=False, default=str)

        with st.expander(f"{icon} {name} · {location}", expanded=False):
            st.markdown('<div class="tool-event-label">Arguments</div>', unsafe_allow_html=True)
            st.code(args, language="json")
            st.markdown('<div class="tool-event-label">Tool output</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="tool-output">{escape(output[:6000])}</div>',
                unsafe_allow_html=True,
            )


for item in ss.transcript:
    with st.chat_message(item["role"]):
        render_tool_events(item.get("tools", []))
        if item.get("error"):
            st.error(item["content"])
        else:
            st.markdown(item["content"])


# ---------------------------- Tool execution ----------------------------
async def run_turn(llm, llm_with_tools, tools_by_name, history, events):
    for _ in range(MAX_TOOL_ROUNDS):
        ai = await llm_with_tools.ainvoke(history)
        calls = getattr(ai, "tool_calls", None) or []

        if not calls:
            text = ai.content or ""
            history.append(AIMessage(content=text))
            return text

        history.append(ai)

        for i, call in enumerate(calls):
            name = call["name"]
            args = call.get("args") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            call_id = call.get("id") or f"call_{len(history)}_{i}"
            tool = tools_by_name.get(name)

            if tool is None:
                ok = False
                text = f"Error: unknown tool '{name}'. Available tools: {', '.join(tools_by_name) or 'none'}"
            else:
                try:
                    text = result_to_text(await asyncio.wait_for(tool.ainvoke(args), timeout=TOOL_TIMEOUT))
                    ok = True
                except TimeoutError:
                    ok = False
                    text = f"Error: {name} timed out after {TOOL_TIMEOUT}s and was stopped."
                except Exception as error:
                    ok = False
                    text = f"Error calling {name}: {describe_error(error)}"

            if ok and text.lstrip().lower().startswith(("execution failed", "error")):
                ok = False

            events.append({"name": name, "args": args, "result": text, "ok": ok})
            history.append(ToolMessage(tool_call_id=call_id, name=name, content=text))

    final = await llm.ainvoke(history)
    text = final.content or ""
    history.append(AIMessage(content=text))
    return text


# ---------------------------- Chat input ----------------------------
user_text = st.chat_input("Type a message…")

if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)

    history = ss.history
    checkpoint = len(history)
    history.append(HumanMessage(content=user_text))
    events = []
    error = False

    with st.chat_message("assistant"):
        try:
            answer = ss.loop.run_until_complete(
                run_turn(ss.llm, ss.llm_with_tools, ss.tools_by_name, history, events)
            )
        except Exception as exc:
            del history[checkpoint:]
            answer = friendly_error(exc)
            error = True

        render_tool_events(events)
        if error:
            st.error(answer)
        else:
            st.markdown(answer or "_(empty response)_")

    ss.transcript.append({"role": "user", "content": user_text})
    ss.transcript.append({
        "role": "assistant",
        "content": answer,
        "tools": events,
        "error": error,
    })
