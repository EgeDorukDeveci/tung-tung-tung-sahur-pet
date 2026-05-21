#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import threading
import time


ROOT = os.path.dirname(os.path.realpath(__file__))
CTL = os.path.join(ROOT, "woodlingctl.py")
APP = os.path.join(ROOT, "app.py")


def _python():
    return sys.executable or "python"


def _pet(state, duration=12):
    subprocess.Popen(
        [_python(), CTL, state, str(duration)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _start_pet():
    subprocess.Popen(
        [_python(), CTL, "start"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _find_codex():
    override = os.environ.get("CODEX_WOODLING_CODEX")
    if override:
        return [override]
    own_dir = os.path.abspath(ROOT)
    for path in os.environ.get("PATH", "").split(os.pathsep):
        exe = os.path.join(path, "codex.exe" if os.name == "nt" else "codex")
        if os.path.exists(exe) and os.path.abspath(os.path.dirname(exe)) != own_dir:
            return [exe]
    found = shutil.which("codex")
    if found:
        return [found]
    if os.name == "nt":
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            win_codex = os.path.join(userprofile, ".codex", "bin", "wsl", "codex")
            drive, tail = os.path.splitdrive(win_codex)
            if drive and os.path.exists(win_codex):
                drive_letter = drive[0].lower()
                wsl_codex = f"/mnt/{drive_letter}{tail.replace(os.sep, '/')}"
                return ["wsl.exe", "-e", wsl_codex]
    return None


def _heartbeat(proc):
    tick = 0
    while proc.poll() is None:
        state = "thinking" if tick % 3 else "terminal"
        _pet(state, 8)
        tick += 1
        time.sleep(6)


def main():
    codex = _find_codex()
    if not codex:
        print("Could not find the real codex command. Set CODEX_WOODLING_CODEX to its path.")
        return 1

    _start_pet()
    _pet("thinking", 10)
    time.sleep(0.25)

    proc = subprocess.Popen([*codex, *sys.argv[1:]])
    thread = threading.Thread(target=_heartbeat, args=(proc,), daemon=True)
    thread.start()
    code = proc.wait()

    if code == 0:
        _pet("success", 5)
    else:
        _pet("error", 10)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
