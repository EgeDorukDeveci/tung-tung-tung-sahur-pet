#!/usr/bin/env python3
import json
import os
import shutil
import sys
import time


ROOT = os.path.dirname(os.path.realpath(__file__))
HOOK_SCRIPT = os.path.join(ROOT, "codex_woodling_hook.py")


def codex_home():
    if os.environ.get("CODEX_HOME"):
        return os.environ["CODEX_HOME"]
    parts = os.path.abspath(ROOT).split(os.sep)
    if len(parts) > 4 and parts[1:4] == ["mnt", "c", "Users"]:
        return os.path.join(os.sep, "mnt", "c", "Users", parts[4], ".codex")
    return os.path.join(os.path.expanduser("~"), ".codex")


def hook_command():
    script = HOOK_SCRIPT.replace("\\", "/")
    return f'{sys.executable} "{script}"'


def handler():
    return {
        "type": "command",
        "command": hook_command(),
        "timeout": 5,
        "statusMessage": "Updating Woodling",
    }


def hook_group(matcher=None):
    group = {"hooks": [handler()]}
    if matcher is not None:
        group["matcher"] = matcher
    return group


def is_woodling(group):
    for item in group.get("hooks", []):
        if isinstance(item, dict) and "codex_woodling_hook.py" in item.get("command", ""):
            return True
    return False


def add_or_replace(groups, new_group):
    kept = [group for group in groups if not is_woodling(group)]
    kept.append(new_group)
    return kept


def main():
    home = codex_home()
    os.makedirs(home, exist_ok=True)
    path = os.path.join(home, "hooks.json")
    data = {"hooks": {}}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        backup = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, backup)
        print(f"Backup: {backup}")

    hooks = data.setdefault("hooks", {})
    hooks["UserPromptSubmit"] = add_or_replace(hooks.get("UserPromptSubmit", []), hook_group())
    hooks["PreToolUse"] = add_or_replace(hooks.get("PreToolUse", []), hook_group("Bash|apply_patch|Edit|Write"))
    hooks["PostToolUse"] = add_or_replace(hooks.get("PostToolUse", []), hook_group("Bash|apply_patch|Edit|Write"))
    hooks["Stop"] = add_or_replace(hooks.get("Stop", []), hook_group())

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Installed Woodling hooks: {path}")
    print("Restart Codex, then open /hooks and trust the Woodling hook entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
