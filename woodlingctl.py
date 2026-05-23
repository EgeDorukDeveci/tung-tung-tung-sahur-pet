#!/usr/bin/env python3
import os
import subprocess
import sys


APP = os.path.join(os.path.dirname(os.path.realpath(__file__)), "app.py")
ROOT = os.path.dirname(APP)


def startup_path():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    return os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "Codex Woodling.vbs")


def write_file(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    py = sys.executable or "python"
    if len(sys.argv) < 2 or sys.argv[1] in {"help", "-h", "--help"}:
        print("Usage: woodling start | wake | stop | status | install-startup | jump | idle | sleeping | thinking | coding | terminal | searching | success | error [seconds]")
        return 0

    cmd = sys.argv[1].lower()
    if cmd == "start":
        return subprocess.call([py, APP, "--start"])
    if cmd == "wake":
        subprocess.call([py, APP, "--start"])
        return subprocess.call([py, APP, "--status", "idle", "--duration", "20"])
    if cmd == "stop":
        return subprocess.call([py, APP, "--stop"])
    if cmd == "status":
        return subprocess.call([py, APP, "--health"])
    if cmd == "install-startup":
        path = startup_path()
        if not path:
            print("APPDATA is not available; cannot install startup shortcut.")
            return 1
        write_file(path, [f'CreateObject("WScript.Shell").Run "py ""{APP}"" --start", 0, False'])
        print(f"Installed startup launcher: {path}")
        return 0
    if cmd == "jump":
        return subprocess.call([py, APP, "--status", "success", "--duration", "5"])

    states = {"idle", "sleeping", "thinking", "coding", "terminal", "searching", "success", "error", "falling"}
    if cmd in states:
        duration = sys.argv[2] if len(sys.argv) > 2 else "8"
        return subprocess.call([py, APP, "--status", cmd, "--duration", duration])

    print(f"Unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
