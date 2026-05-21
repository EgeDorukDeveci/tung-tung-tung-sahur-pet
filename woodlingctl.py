#!/usr/bin/env python3
import os
import subprocess
import sys


APP = os.path.join(os.path.dirname(os.path.realpath(__file__)), "app.py")


def main():
    py = sys.executable or "python"
    if len(sys.argv) < 2 or sys.argv[1] in {"help", "-h", "--help"}:
        print("Usage: woodling start | stop | jump | idle | thinking | coding | terminal | searching | success | error [seconds]")
        return 0

    cmd = sys.argv[1].lower()
    if cmd == "start":
        return subprocess.call([py, APP, "--start"])
    if cmd == "stop":
        return subprocess.call([py, APP, "--stop"])
    if cmd == "jump":
        return subprocess.call([py, APP, "--status", "success", "--duration", "5"])

    states = {"idle", "thinking", "coding", "terminal", "searching", "success", "error", "falling"}
    if cmd in states:
        duration = sys.argv[2] if len(sys.argv) > 2 else "8"
        return subprocess.call([py, APP, "--status", cmd, "--duration", duration])

    print(f"Unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
