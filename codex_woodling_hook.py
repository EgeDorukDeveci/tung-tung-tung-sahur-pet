#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time


ROOT = os.path.dirname(os.path.realpath(__file__))
APP = os.path.join(ROOT, "app.py")
LOG_NAME = "codex_activity.log"


def control_dir():
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        return os.path.join(local_appdata, "CodexWoodling")
    parts = os.path.abspath(ROOT).split(os.sep)
    if len(parts) > 4 and parts[1:4] == ["mnt", "c", "Users"]:
        return os.path.join(
            os.sep,
            "mnt",
            "c",
            "Users",
            parts[4],
            "AppData",
            "Local",
            "CodexWoodling",
        )
    return os.path.join(os.path.expanduser("~"), ".codex_woodling")


def log(activity, event, detail=""):
    try:
        path = control_dir()
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, LOG_NAME), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {activity} {event} {detail}\n")
    except Exception:
        pass


def ping(activity, seconds):
    subprocess.run(
        [sys.executable, APP, "--status", activity, "--duration", str(seconds)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def classify(event):
    name = event.get("hook_event_name", "")
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    command = ""
    if isinstance(tool_input, dict):
        command = str(tool_input.get("command") or "")
    low = command.lower()

    if name == "UserPromptSubmit":
        return "thinking", 20, "prompt"
    if name == "Stop":
        return "success", 5, "turn-finished"
    if name == "PreToolUse":
        if tool in {"apply_patch", "Edit", "Write"}:
            return "coding", 20, tool
        if tool == "Bash":
            search_words = ("rg ", "grep", "find ", "ls", "dir", "cat ", "sed ", "head ", "tail ", "git show", "git diff", "git status")
            code_words = ("apply_patch", "python", "py ", "npm", "pnpm", "node", "pytest", "ruff", "tsc", "build", "git commit")
            if any(word in low for word in search_words):
                return "searching", 14, command[:90]
            if any(word in low for word in code_words):
                return "terminal", 14, command[:90]
            return "terminal", 10, command[:90]
        return "thinking", 10, tool
    if name == "PostToolUse":
        return "thinking", 5, tool
    return "idle", 4, name or "unknown"


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}
    activity, seconds, detail = classify(event)
    ping(activity, seconds)
    log(activity, event.get("hook_event_name", "unknown"), detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
