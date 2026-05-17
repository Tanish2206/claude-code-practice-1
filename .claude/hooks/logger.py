#!/usr/bin/env python3
"""
Claude Code Universal Logger
Handles: UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, SessionStart, Stop
Writes to: logs/YYYY-MM-DD.log (append-only, one file per day)
Format: [HH:MM:SS] LEVEL    | ACTION      | description
"""

import json
import sys
import os
from datetime import datetime

# ── paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.getcwd()
LOGS_DIR     = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# ── helpers ────────────────────────────────────────────────────────────────
def now() -> str:
    return datetime.now().strftime("%H:%M:%S")

def write(level: str, action: str, description: str):
    """Append one structured line to today's log file."""
    line = f"[{now()}] {level:<8} | {action:<12} | {description}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def short(text: str, max_len: int = 120) -> str:
    """Truncate long strings so log lines stay readable."""
    text = str(text).replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len] + "..."

# ── event handlers ─────────────────────────────────────────────────────────
def handle_prompt(data: dict):
    prompt = short(data.get("prompt", ""), 100)
    write("INFO", "PROMPT", f'"{prompt}"')


def handle_pre_tool(data: dict):
    tool  = data.get("tool_name", "unknown")
    inp   = data.get("tool_input", {})

    if tool == "Read":
        write("INFO", "READ", f"reading  →  {inp.get('file_path', '?')}")

    elif tool in ("Write", "Edit", "MultiEdit"):
        write("INFO", "WRITE", f"writing  →  {inp.get('file_path', '?')}")

    elif tool == "Bash":
        cmd = short(inp.get("command", ""), 80)
        # detect archive move
        if "Archive" in cmd and ("mv " in cmd or "cp " in cmd):
            write("ARCHIVE", "MOVE", f"cmd: {cmd}")
        else:
            write("INFO", "BASH", f"cmd: {cmd}")

    elif tool == "Task":
        write("INFO", "AGENT", f"spawning agent  →  {short(inp.get('description', inp.get('prompt', '?')), 80)}")

    elif tool in ("Glob", "Grep"):
        write("INFO", tool.upper(), f"pattern: {inp.get('pattern', inp.get('glob', '?'))}")

    elif tool == "WebFetch":
        write("INFO", "WEBFETCH", f"url: {inp.get('url', '?')}")

    elif tool == "WebSearch":
        write("INFO", "WEBSEARCH", f"query: {inp.get('query', '?')}")

    elif tool.startswith("mcp__"):
        # mcp__servername__toolname
        parts = tool.split("__")
        server = parts[1] if len(parts) > 1 else "?"
        fn     = parts[2] if len(parts) > 2 else "?"
        write("INFO", "MCP", f"server: {server}  tool: {fn}  input: {short(str(inp), 60)}")

    else:
        write("INFO", "TOOL", f"tool: {tool}  input: {short(str(inp), 80)}")


def handle_post_tool(data: dict):
    tool     = data.get("tool_name", "unknown")
    inp      = data.get("tool_input", {})
    response = data.get("tool_response", {})

    if tool == "Write":
        write("INFO", "WRITE_OK", f"created/updated  →  {inp.get('file_path', '?')}")

    elif tool == "Bash":
        cmd      = short(inp.get("command", ""), 60)
        exit_code = response.get("exit_code", response.get("exitCode", "?"))
        if "Archive" in cmd and ("mv " in cmd or "cp " in cmd):
            write("ARCHIVE", "MOVE_OK", f"exit={exit_code}  cmd: {cmd}")
        else:
            write("INFO", "BASH_OK", f"exit={exit_code}  cmd: {cmd}")

    elif tool == "Task":
        usage = response.get("usage", {})
        tokens = usage.get("input_tokens", "?") if usage else "?"
        write("INFO", "AGENT_OK", f"agent done  tokens_in={tokens}  desc: {short(inp.get('description', inp.get('prompt', '?')), 60)}")

    elif tool == "Read":
        write("INFO", "READ_OK", f"read  →  {inp.get('file_path', '?')}")

    else:
        write("INFO", "TOOL_OK", f"tool: {tool}  done")


def handle_post_tool_failure(data: dict):
    tool = data.get("tool_name", "unknown")
    inp  = data.get("tool_input", {})
    err  = data.get("error", data.get("tool_response", {}).get("stderr", "unknown error"))

    if tool == "Bash":
        cmd = short(inp.get("command", ""), 60)
        write("ERROR", "BASH_FAIL", f"cmd: {cmd}  error: {short(str(err), 60)}")
    else:
        write("ERROR", "TOOL_FAIL", f"tool: {tool}  error: {short(str(err), 80)}")


def handle_session_start(data: dict):
    session_id = data.get("session_id", "?")
    write("INFO", "SESSION", f"session started  id={session_id}")
    write("INFO", "SESSION", f"working dir: {data.get('cwd', PROJECT_ROOT)}")


def handle_stop(data: dict):
    session_id = data.get("session_id", "?")
    write("INFO", "SESSION", f"session ended  id={session_id}")


# ── main dispatcher ────────────────────────────────────────────────────────
def main():
    try:
        raw  = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        write("ERROR", "LOGGER", f"could not parse stdin JSON: {e}")
        sys.exit(0)

    event = data.get("hook_event_name", "")

    dispatch = {
        "UserPromptSubmit":    handle_prompt,
        "PreToolUse":          handle_pre_tool,
        "PostToolUse":         handle_post_tool,
        "PostToolUseFailure":  handle_post_tool_failure,
        "SessionStart":        handle_session_start,
        "Stop":                handle_stop,
    }

    handler = dispatch.get(event)
    if handler:
        handler(data)
    else:
        write("INFO", "OTHER", f"event: {event}  data: {short(str(data), 80)}")

    sys.exit(0)   # always exit 0 — logger never blocks Claude


if __name__ == "__main__":
    main()