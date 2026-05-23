#!/usr/bin/env python3
import json
import os
import struct
import zlib


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets")
FRAME_W = 64
FRAME_H = 64
FRAMES = 4

STATES = [
    "idle",
    "thinking",
    "coding",
    "terminal",
    "searching",
    "success",
    "falling",
    "error",
    "sleeping",
]

P = {
    "clear": (0, 0, 0, 0),
    "outline": (74, 45, 28, 255),
    "dark": (104, 61, 31, 255),
    "mid": (183, 112, 54, 255),
    "wood": (207, 139, 70, 255),
    "light": (234, 171, 93, 255),
    "cream": (255, 231, 168, 255),
    "eye": (31, 22, 18, 255),
    "white": (255, 246, 224, 255),
    "blue": (83, 172, 190, 255),
    "green": (119, 204, 111, 255),
    "yellow": (255, 213, 87, 255),
    "red": (218, 84, 69, 255),
    "purple": (150, 112, 214, 255),
}


def img(w, h):
    return [[P["clear"] for _ in range(w)] for _ in range(h)]


def rect(im, x, y, w, h, c):
    for yy in range(max(0, y), min(len(im), y + h)):
        for xx in range(max(0, x), min(len(im[yy]), x + w)):
            im[yy][xx] = c


def px(im, x, y, c):
    if 0 <= y < len(im) and 0 <= x < len(im[0]):
        im[y][x] = c


def line(im, x0, y0, x1, y1, c, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        rect(im, x0 - thick // 2, y0 - thick // 2, thick, thick, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ellipse(im, cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) ** 2) * ry * ry + ((y - cy) ** 2) * rx * rx <= rx * rx * ry * ry:
                px(im, x, y, c)


def rounded_log(im, x, y, w, h, lean=0, squash=0):
    yy = y + squash
    hh = h - squash
    rect(im, x + 3 + lean, yy, w - 6, 1, P["outline"])
    rect(im, x + 1 + lean, yy + 1, w - 2, 2, P["outline"])
    rect(im, x + lean, yy + 3, w, hh - 6, P["outline"])
    rect(im, x + 1 + lean, yy + hh - 3, w - 2, 2, P["outline"])
    rect(im, x + 3 + lean, yy + hh - 1, w - 6, 1, P["outline"])
    rect(im, x + 3 + lean, yy + 2, w - 6, hh - 4, P["wood"])
    rect(im, x + 1 + lean, yy + 5, w - 2, hh - 10, P["wood"])
    rect(im, x + 5 + lean, yy + 2, 3, hh - 4, P["light"])
    rect(im, x + w - 7 + lean, yy + 4, 2, hh - 8, P["dark"])
    for off in (10, 21):
        line(im, x + 7 + lean, yy + off, x + 9 + lean, yy + off + 5, P["mid"])
        line(im, x + w - 10 + lean, yy + off + 2, x + w - 12 + lean, yy + off + 7, P["dark"])
    rect(im, x + 8 + lean, yy + 3, w - 16, 1, P["mid"])
    rect(im, x + 12 + lean, yy + 5, w - 24, 1, P["cream"])


def eyes(im, x, y, mood, blink=False):
    if mood == "sleeping":
        line(im, x + 12, y + 15, x + 20, y + 13, P["eye"], 2)
        line(im, x + 26, y + 13, x + 34, y + 15, P["eye"], 2)
        return
    if blink:
        rect(im, x + 13, y + 15, 7, 2, P["eye"])
        rect(im, x + 26, y + 15, 7, 2, P["eye"])
        return
    if mood == "error":
        line(im, x + 12, y + 12, x + 19, y + 19, P["eye"], 2)
        line(im, x + 19, y + 12, x + 12, y + 19, P["eye"], 2)
        rect(im, x + 27, y + 13, 6, 6, P["white"])
        rect(im, x + 29, y + 15, 2, 2, P["eye"])
        return
    if mood == "focused":
        rect(im, x + 13, y + 12, 8, 7, P["white"])
        rect(im, x + 26, y + 12, 8, 7, P["white"])
        rect(im, x + 16, y + 14, 3, 4, P["eye"])
        rect(im, x + 28, y + 14, 3, 4, P["eye"])
        rect(im, x + 12, y + 11, 7, 1, P["eye"])
        rect(im, x + 28, y + 11, 7, 1, P["eye"])
        return
    wide = mood in ("coding", "success")
    rect(im, x + 12, y + 10, 9, 11 if wide else 10, P["white"])
    rect(im, x + 26, y + 10, 9, 11 if wide else 10, P["white"])
    rect(im, x + 15, y + 13, 4, 5, P["eye"])
    rect(im, x + 28, y + 13, 4, 5, P["eye"])
    px(im, x + 16, y + 13, P["white"])
    px(im, x + 29, y + 13, P["white"])


def mouth(im, x, y, mood):
    if mood == "error":
        rect(im, x + 20, y + 29, 8, 2, P["eye"])
        px(im, x + 19, y + 30, P["eye"])
        px(im, x + 28, y + 30, P["eye"])
    elif mood == "focused":
        rect(im, x + 18, y + 27, 11, 2, P["eye"])
    elif mood == "coding":
        rect(im, x + 17, y + 27, 14, 4, P["eye"])
        rect(im, x + 19, y + 28, 10, 1, P["white"])
    elif mood == "falling":
        rect(im, x + 20, y + 26, 8, 8, P["eye"])
        rect(im, x + 22, y + 27, 4, 2, P["white"])
    elif mood == "sleeping":
        rect(im, x + 20, y + 28, 8, 2, P["eye"])
    elif mood == "success":
        rect(im, x + 16, y + 27, 15, 2, P["eye"])
        px(im, x + 17, y + 29, P["eye"])
        px(im, x + 29, y + 29, P["eye"])
    else:
        rect(im, x + 17, y + 27, 12, 2, P["eye"])
        px(im, x + 18, y + 29, P["eye"])
        px(im, x + 28, y + 29, P["eye"])


def limbs(im, ox, oy, state, frame):
    bob = 1 if frame in (1, 2) else 0
    if state == "sleeping":
        line(im, ox + 14, oy + 37, ox + 5, oy + 43, P["outline"], 3)
        line(im, ox + 39, oy + 37, ox + 49, oy + 43, P["outline"], 3)
        line(im, ox + 21, oy + 49, ox + 15, oy + 58, P["outline"], 3)
        line(im, ox + 33, oy + 49, ox + 40, oy + 58, P["outline"], 3)
        rect(im, ox + 11, oy + 58, 8, 2, P["outline"])
        rect(im, ox + 37, oy + 58, 8, 2, P["outline"])
        return
    if state == "thinking":
        line(im, ox + 16, oy + 31, ox + 10, oy + 24, P["outline"], 3)
        line(im, ox + 10, oy + 24, ox + 14, oy + 17, P["outline"], 3)
        line(im, ox + 40, oy + 32, ox + 45, oy + 40, P["outline"], 3)
    elif state == "coding":
        tap = -3 if frame % 2 == 0 else 4
        line(im, ox + 14, oy + 32, ox + 7, oy + 41 + tap, P["outline"], 3)
        line(im, ox + 41, oy + 32, ox + 50, oy + 41 - tap, P["outline"], 3)
    elif state == "terminal":
        line(im, ox + 14, oy + 32, ox + 9, oy + 41, P["outline"], 3)
        line(im, ox + 40, oy + 32, ox + 47, oy + 42, P["outline"], 3)
    elif state == "searching":
        line(im, ox + 14, oy + 32, ox + 7, oy + 39, P["outline"], 3)
        line(im, ox + 40, oy + 32, ox + 51, oy + 27, P["outline"], 3)
    elif state == "success":
        line(im, ox + 14, oy + 31, ox + 7, oy + 24, P["outline"], 3)
        line(im, ox + 40, oy + 31, ox + 50, oy + 22, P["outline"], 3)
    elif state == "falling":
        swing = -2 if frame % 2 == 0 else 2
        line(im, ox + 14, oy + 31, ox + 8 + swing, oy + 16, P["outline"], 3)
        line(im, ox + 40, oy + 31, ox + 49 + swing, oy + 15, P["outline"], 3)
    elif state == "error":
        line(im, ox + 14, oy + 34, ox + 9, oy + 43, P["outline"], 3)
        line(im, ox + 40, oy + 34, ox + 44, oy + 45, P["outline"], 3)
    else:
        line(im, ox + 14, oy + 32, ox + 7, oy + 41, P["outline"], 3)
        line(im, ox + 40, oy + 32, ox + 47, oy + 41, P["outline"], 3)
    spread = -1 if frame in (1, 3) else 1
    if state == "thinking":
        spread = -3 if frame in (1, 2) else 3
    line(im, ox + 22, oy + 48 - bob, ox + 17 + spread, oy + 60, P["outline"], 3)
    line(im, ox + 33, oy + 48 - bob, ox + 38 - spread, oy + 60, P["outline"], 3)
    rect(im, ox + 13 + spread, oy + 60, 8, 2, P["outline"])
    rect(im, ox + 36 - spread, oy + 60, 8, 2, P["outline"])


def prop(im, state, frame):
    if state == "idle":
        y = 46 + (frame % 2)
        line(im, 9, 38, 18, y + 15, P["dark"], 4)
        rect(im, 16, y + 12, 5, 3, P["mid"])
    elif state == "thinking":
        x = 48 + (frame % 2)
        rect(im, x, 9, 3, 3, P["yellow"])
        rect(im, x + 2, 12, 3, 3, P["yellow"])
        rect(im, x + 1, 17, 3, 2, P["yellow"])
        px(im, x + 2, 22, P["yellow"])
    elif state == "coding":
        line(im, 12, 8, 8, 11, P["blue"])
        line(im, 8, 11, 12, 14, P["blue"])
        line(im, 52, 10, 56, 13, P["green"])
        line(im, 56, 13, 52, 16, P["green"])
        rect(im, 45, 46 + frame % 2, 2, 7, P["purple"])
        rect(im, 53, 46 + frame % 2, 2, 7, P["purple"])
    elif state == "terminal":
        rect(im, 6, 43, 24, 14, P["outline"])
        rect(im, 8, 45, 20, 10, (35, 38, 32, 255))
        line(im, 11, 48, 15, 50, P["green"])
        line(im, 15, 50, 11, 52, P["green"])
        rect(im, 18 + frame % 3, 51, 5, 1, P["green"])
    elif state == "searching":
        ellipse(im, 50, 24, 6, 6, P["outline"])
        ellipse(im, 50, 24, 4, 4, (190, 230, 232, 180))
        line(im, 54, 29, 60, 35, P["outline"], 3)
        rect(im, 7, 43 + frame % 2, 14, 15, P["cream"])
        rect(im, 10, 47 + frame % 2, 8, 1, P["mid"])
        rect(im, 10, 51 + frame % 2, 7, 1, P["mid"])
    elif state == "success":
        for x, y in ((9, 14), (51, 10), (49, 49), (13, 47)):
            if (x + frame) % 2 == 0:
                px(im, x, y - 2, P["yellow"])
                px(im, x, y + 2, P["yellow"])
                px(im, x - 2, y, P["yellow"])
                px(im, x + 2, y, P["yellow"])
                px(im, x, y, P["white"])
    elif state == "falling":
        rect(im, 12 + frame % 2, 18, 2, 2, P["blue"])
        rect(im, 52 + frame % 2, 21, 2, 2, P["blue"])
    elif state == "error":
        rect(im, 48, 12, 9, 8, P["red"])
        rect(im, 51, 14, 2, 4, P["white"])
        px(im, 51, 19, P["white"])
        if frame % 2:
            rect(im, 8, 42, 6, 4, (120, 110, 120, 170))
            rect(im, 12, 39, 4, 3, (120, 110, 120, 120))
    elif state == "sleeping":
        x = 45 + frame
        rect(im, x, 13, 5, 2, P["blue"])
        rect(im, x + 4, 10, 5, 2, P["blue"])
        rect(im, x + 8, 7, 5, 2, P["blue"])


def frame(state, i):
    im = img(FRAME_W, FRAME_H)
    bob = 0
    lean = 0
    squash = 0
    mood = state
    if state == "idle":
        bob = 1 if i in (1, 2) else 0
        lean = -1 if i == 1 else 1 if i == 3 else 0
        mood = "idle"
    elif state == "thinking":
        lean = -2 if i in (1, 2) else 2
        mood = "idle"
    elif state == "coding":
        bob = -1 if i % 2 == 0 else 1
        mood = "coding"
    elif state == "terminal":
        mood = "focused"
    elif state == "searching":
        lean = 1 if i in (1, 2) else 0
        mood = "focused"
    elif state == "success":
        bob = -3 if i in (1, 2) else 0
        squash = 1 if i == 3 else 0
        mood = "success"
    elif state == "falling":
        bob = -1 if i % 2 else 1
        lean = -1 if i in (1, 2) else 1
        mood = "falling"
    elif state == "error":
        lean = -2 if i % 2 else 2
        bob = 2
        mood = "error"
    elif state == "sleeping":
        bob = 2 if i in (1, 2) else 1
        lean = -3
        squash = 2
        mood = "sleeping"
    ox = 11 + lean
    oy = 4 + bob
    limbs(im, ox, oy, state, i)
    rounded_log(im, ox + 6, oy + 4, 34, 46, 0, squash)
    eyes(im, ox + 6, oy + 4, mood, state == "idle" and i == 2)
    mouth(im, ox + 6, oy + 4, mood)
    prop(im, state, i)
    return im


def compose_sheet(scale=1):
    w = FRAME_W * FRAMES * scale
    h = FRAME_H * len(STATES) * scale
    sheet = img(w, h)
    for row, state in enumerate(STATES):
        for col in range(FRAMES):
            fr = frame(state, col)
            for y in range(FRAME_H):
                for x in range(FRAME_W):
                    c = fr[y][x]
                    if c[3] == 0:
                        continue
                    for sy in range(scale):
                        for sx in range(scale):
                            sheet[row * FRAME_H * scale + y * scale + sy][col * FRAME_W * scale + x * scale + sx] = c
    return sheet


def flip_horizontal(im):
    return [list(reversed(row)) for row in im]


def write_png(path, im):
    h = len(im)
    w = len(im[0])
    raw = bytearray()
    for row in im:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend((r, g, b, a))

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    sheet_path = os.path.join(OUT_DIR, "codex_woodling_spritesheet.png")
    left_sheet_path = os.path.join(OUT_DIR, "codex_woodling_spritesheet_left.png")
    preview_path = os.path.join(OUT_DIR, "codex_woodling_preview_x4.png")
    meta_path = os.path.join(OUT_DIR, "codex_woodling_spritesheet.json")
    manifest_path = os.path.join(OUT_DIR, "woodling.pet.json")
    write_png(sheet_path, compose_sheet(1))
    write_png(left_sheet_path, flip_horizontal(compose_sheet(1)))
    write_png(preview_path, compose_sheet(4))
    manifest = {
        "id": "codex-woodling",
        "displayName": "Codex Woodling",
        "description": "A small pixel-art wooden coding companion with explicit agent states.",
        "spritesheet": "codex_woodling_spritesheet.png",
        "spritesheetLeft": "codex_woodling_spritesheet_left.png",
        "frameWidth": FRAME_W,
        "frameHeight": FRAME_H,
        "framesPerState": FRAMES,
        "scale": 1,
        "states": STATES,
        "aliases": {
            "writing": "coding",
            "running": "terminal",
            "reading": "searching",
            "done": "success",
            "stuck": "error",
            "sleep": "sleeping",
            "asleep": "sleeping",
            "wake": "idle",
        },
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "name": "Codex Woodling",
                "frame_width": FRAME_W,
                "frame_height": FRAME_H,
                "frames_per_state": FRAMES,
                "states": STATES,
                "style": "transparent low-resolution pixel art, warm wood palette",
                "palette": {k: "#{:02x}{:02x}{:02x}{:02x}".format(*v) for k, v in P.items()},
            },
            f,
            indent=2,
        )
        f.write("\n")
    print(sheet_path)
    print(left_sheet_path)
    print(preview_path)
    print(meta_path)
    print(manifest_path)


if __name__ == "__main__":
    main()
