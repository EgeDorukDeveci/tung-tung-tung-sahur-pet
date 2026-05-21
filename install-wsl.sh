#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

ln -sf "$ROOT/codex-woodling" "$BIN_DIR/codex-woodling"
ln -sf "$ROOT/woodlingctl.py" "$BIN_DIR/woodlingctl"

chmod +x "$ROOT/codex-woodling" "$ROOT/codex_woodling.py" "$ROOT/woodlingctl.py"

printf '%s\n' "Installed WSL launchers:"
printf '%s\n' "  $BIN_DIR/codex-woodling"
printf '%s\n' "  $BIN_DIR/woodlingctl"
printf '%s\n' ""
printf '%s\n' "Make sure this is in your shell profile if needed:"
printf '%s\n' '  export PATH="$HOME/.local/bin:$PATH"'
