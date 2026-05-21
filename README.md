# Codex Woodling

A tiny OpenPets-inspired desktop pet runtime for the custom Woodling character.
It is not OpenPets and does not depend on OpenPets.

## Start

From PowerShell:

```powershell
cd "C:\Users\egedo\Desktop\tung tung tung sahur pet"
.\woodling.cmd start
```

The pet runs detached, stays on the bottom of the screen, walks left/right, and
falls back to the floor if you drag it upward and release it.

## Control

```powershell
.\woodling.cmd idle
.\woodling.cmd thinking 10
.\woodling.cmd coding 10
.\woodling.cmd terminal 10
.\woodling.cmd searching 10
.\woodling.cmd success 5
.\woodling.cmd error 10
.\woodling.cmd jump
```

Stop it:

```powershell
.\woodling.cmd stop
```

## From WSL

The status command works from WSL too because the control file lives in the
shared Windows user folder:

```bash
python3 "/mnt/c/Users/egedo/Desktop/tung tung tung sahur pet/app.py" --status thinking --duration 10
```

## Pet Format

The pet manifest is:

```text
assets/woodling.pet.json
```

It declares:

- sprite sheets
- frame size
- frames per state
- state names
- aliases

The runtime reads this manifest and displays the matching animation state.
