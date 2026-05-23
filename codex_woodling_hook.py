#!/usr/bin/env python3
import json
import os
import sys
import time


ROOT = os.path.dirname(os.path.realpath(__file__))
LOG_NAME = "codex_activity.log"
ACTIVITY_NAME = "activity.json"


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


def write_activity(activity, seconds, event, detail=""):
    path = control_dir()
    os.makedirs(path, exist_ok=True)
    activity_path = os.path.join(path, ACTIVITY_NAME)
    tmp_path = activity_path + ".tmp"
    payload = {
        "state": activity,
        "duration": seconds,
        "event": event,
        "detail": detail,
        "sentAt": time.time(),
        "nonce": f"{time.time()}-{os.getpid()}",
    }
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.replace(tmp_path, activity_path)


def classify(event):
    name = event.get("hook_event_name", "")
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    command = ""
    if isinstance(tool_input, dict):
        command = str(tool_input.get("command") or "")
    low = command.lower()

    if name == "UserPromptSubmit":
        return "thinking", 45, "prompt"
    if name == "Stop":
        return "success", 5, "turn-finished"
    if name == "PreToolUse":
        if tool in {"apply_patch", "Edit", "Write"}:
            return "coding", 5, tool
        if tool == "Bash":
            search_words = ("rg ", "grep", "find ", "ls", "dir", "cat ", "sed ", "head ", "tail ", "git show", "git diff", "git status")
            code_words = ("apply_patch", "python", "py ", "npm", "pnpm", "node", "pytest", "ruff", "tsc", "build", "git commit")
            if any(word in low for word in search_words):
                return "searching", 4, command[:90]
            if any(word in low for word in code_words):
                return "terminal", 4, command[:90]
            return "terminal", 4, command[:90]
        return "thinking", 4, tool
    if name == "PostToolUse":
        return "thinking", 2, tool
    return "idle", 4, name or "unknown"


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}
    activity, seconds, detail = classify(event)
    hook_name = event.get("hook_event_name", "unknown")
    write_activity(activity, seconds, hook_name, detail)
    log(activity, hook_name, detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
