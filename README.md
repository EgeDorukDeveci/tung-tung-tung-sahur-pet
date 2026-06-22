# Codex Woodling

Codex Woodling is a tiny pixel-art desktop pet for Codex. It lives on the
desktop, reacts to Codex activity, sleeps when nothing is happening, and wakes
when you click it.

This project intentionally uses one character only: **Codex Woodling**.

## Start

Use the hidden desktop launcher:

```text
C:\Users\egedo\Desktop\Codex Woodling.vbs
```

Double-clicking it starts Woodling with `pythonw.exe`, so it should not open a
terminal window.

Startup is intentionally disabled for now. Do not add the old `.cmd` launcher
to Windows startup; that was the source of repeated terminal windows.

## What It Does

- Click Woodling to wake it.
- New Codex prompt: `thinking`.
- Reading/searching files: `searching`.
- Editing code: `coding`.
- Running commands/tests: `terminal`.
- Finished turn: `success` jump.
- Codex inactive for 5 minutes: walk to bottom-left and `sleeping`.
- Codex appears closed/offline: `error`.

## Safe Hook Design

Hooks are enabled, but they are file-only and safe:

```text
Codex hook -> writes activity.json
Woodling app -> reads activity.json
```

The hook does **not** start Woodling, call `woodling.cmd`, run `tasklist`, or
spawn a command chain.

Hook config:

```text
C:\Users\egedo\.codex\hooks.json
```

Activity file:

```text
C:\Users\egedo\AppData\Local\CodexWoodling\activity.json
```

Debug log:

```text
C:\Users\egedo\AppData\Local\CodexWoodling\codex_activity.log
```

## Commands

From PowerShell:

```powershell
cd "C:\Users\egedo\Desktop\tung tung tung sahur pet"
.\woodling.cmd status
.\woodling.cmd wake
.\woodling.cmd sleeping
.\woodling.cmd thinking 10
.\woodling.cmd coding 10
.\woodling.cmd terminal 10
.\woodling.cmd searching 10
.\woodling.cmd jump
.\woodling.cmd stop
```

## Troubleshooting

If terminal windows start opening repeatedly:

1. Empty or remove `C:\Users\egedo\.codex\hooks.json`.
2. Remove any `Codex Woodling.cmd` or `Codex Woodling.vbs` file from Windows
   Startup.
3. Stop Woodling:

```powershell
cd "C:\Users\egedo\Desktop\tung tung tung sahur pet"
.\woodling.cmd stop
```

Then start only with:

```text
C:\Users\egedo\Desktop\Codex Woodling.vbs
```

If old prompt states replay after reopening, remove:

```text
C:\Users\egedo\AppData\Local\CodexWoodling\activity.json
C:\Users\egedo\AppData\Local\CodexWoodling\control.json
```

The current app ignores stale activity from before the pet process started, but
clearing those files is still a simple reset.
