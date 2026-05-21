#!/usr/bin/env python3
import ctypes
import os
import subprocess
import sys
import time


ROOT = os.path.dirname(os.path.realpath(__file__))
CTL = os.path.join(ROOT, "woodlingctl.py")

USER32 = ctypes.windll.user32 if os.name == "nt" else None


def _python():
    return sys.executable or "python"


def _pet(state, duration=4):
    subprocess.Popen(
        [_python(), CTL, state, str(duration)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _active_window_title():
    if not USER32:
        return ""
    hwnd = USER32.GetForegroundWindow()
    if not hwnd:
        return ""
    length = USER32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    USER32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value.lower()


def _looks_like_codex(title):
    needles = ("codex", "chatgpt", "openai")
    return any(needle in title for needle in needles)


def main():
    _pet("idle", 3)
    last_state = None
    while True:
        title = _active_window_title()
        state = "thinking" if _looks_like_codex(title) else "idle"
        if state != last_state:
            _pet(state, 5)
            last_state = state
        time.sleep(2)


if __name__ == "__main__":
    raise SystemExit(main())
