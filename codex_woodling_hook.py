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
    name = str(event.get("hook_event_name") or "")
    event_key = name.replace("_", "").lower()
    tool = str(event.get("tool_name") or "")
    tool_key = tool.lower()
    tool_input = event.get("tool_input") or {}
    command = ""
    if isinstance(tool_input, dict):
        command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    low = command.lower()

    if event_key == "userpromptsubmit":
        return "thinking", 45, "prompt"
    if event_key == "stop":
        return "success", 5, "turn-finished"
    if event_key == "pretooluse":
        if any(word in tool_key for word in ("apply_patch", "edit", "write")) or "apply_patch" in low:
            return "coding", 5, tool
        search_tools = ("search", "read", "list", "glob", "grep", "find", "view_image", "web")
        search_words = (
            "rg ",
            "grep",
            "find ",
            "get-childitem",
            "ls",
            "dir",
            "get-content",
            "cat ",
            "sed ",
            "head ",
            "tail ",
            "git show",
            "git diff",
            "git status",
        )
        if any(word in tool_key for word in search_tools) or any(word in low for word in search_words):
            return "searching", 4, (command or tool)[:90]
        if any(word in tool_key for word in ("bash", "shell", "command", "exec", "terminal")) or command:
            return "terminal", 4, command[:90]
        return "thinking", 4, tool
    if event_key == "posttooluse":
        return "thinking", 2, tool
    return "idle", 4, name or "unknown"


def read_event():
    try:
        raw = sys.stdin.buffer.read()
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            text = raw.decode("utf-16")
        else:
            text = raw.decode("utf-8-sig")
        return json.loads(text)
    except Exception:
        return {}


def main():
    event = read_event()
    activity, seconds, detail = classify(event)
    hook_name = event.get("hook_event_name", "unknown")
    write_activity(activity, seconds, hook_name, detail)
    log(activity, hook_name, detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
