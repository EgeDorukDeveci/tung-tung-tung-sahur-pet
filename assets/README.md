# Codex Woodling Sprite Assets

Original pixel-art desktop pet mascot for this app.

- `codex_woodling_spritesheet.png`: transparent production sheet, 256x448.
- `codex_woodling_spritesheet_left.png`: mirrored transparent sheet for left-facing walking.
- `codex_woodling_preview_x4.png`: nearest-neighbor preview sheet, 1024x1792.
- `codex_woodling_spritesheet.json`: frame size, state order, and palette metadata.

Sheet layout:

| Row | State | Animation idea |
| --- | --- | --- |
| 0 | idle | sway, blink, stick tap |
| 1 | thinking | head scratch, question mark, pacing lean |
| 2 | coding | excited face, code symbols, fast tapping |
| 3 | terminal | focused face, glowing prompt window |
| 4 | searching | magnifier and scrolling paper |
| 5 | success | happy bounce and sparkles |
| 6 | falling | arms-up fall with open mouth |
| 7 | error | confused slump, warning icon, glitch puff |

Each state has four 64x64 frames.
