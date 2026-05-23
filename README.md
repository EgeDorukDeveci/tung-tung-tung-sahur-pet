# Codex Woodling

A tiny always-on desktop pet for Codex.

This project is back to one character only: Codex Woodling.

## Use

There is a desktop launcher at:

```text
C:\Users\egedo\Desktop\Codex Woodling.vbs
```

Double-click it to wake Woodling. It starts the pet if it is not already
running. The launcher runs `pythonw.exe` directly, so it should not open a
terminal window.

The Windows startup launcher is intentionally not installed right now. Keep it
off until the hidden launcher is confirmed stable.

## Behavior

- Woodling runs in the background.
- Click Woodling to wake it.
- If Codex is inactive for 5 minutes, Woodling walks to the bottom-left corner
  and sleeps.
- If Codex appears closed/offline, Woodling shows the error animation.
- Codex hooks still drive the active states: thinking, searching, coding,
  terminal, success, and error.

## Commands

From PowerShell:

```powershell
cd "C:\Users\egedo\Desktop\tung tung tung sahur pet"
.\woodling.cmd wake
.\woodling.cmd status
.\woodling.cmd sleeping
.\woodling.cmd thinking 10
.\woodling.cmd coding 10
.\woodling.cmd terminal 10
.\woodling.cmd searching 10
.\woodling.cmd jump
.\woodling.cmd stop
```

Reinstall startup launcher:

```powershell
.\woodling.cmd install-startup
```

## Codex Hooks

The hook is installed globally at:

```text
C:\Users\egedo\.codex\hooks.json
```

It calls:

```text
codex_woodling_hook.py
```

The hook is intentionally safe: it only writes a tiny JSON file and a debug
log. It does not start Woodling, does not call `woodling.cmd`, and does not run
terminal/process-check commands.

Woodling reads:

```text
C:\Users\egedo\AppData\Local\CodexWoodling\activity.json
```

The debug activity log is:

```text
C:\Users\egedo\AppData\Local\CodexWoodling\codex_activity.log
```
