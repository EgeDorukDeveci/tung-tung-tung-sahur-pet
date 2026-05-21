#!/usr/bin/env python3
import json
import os
import shutil
import zipfile

from PIL import Image


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET_ID = "codex-woodling"
PET_NAME = "Codex Woodling"
DESCRIPTION = (
    "A cute awkward wooden log mascot with expressive eyes, tiny arms, "
    "long legs, and coding-agent reaction animations."
)
ATLAS_COLS = 8
ATLAS_ROWS = 9
CELL_W = 192
CELL_H = 208
SOURCE_FRAME_W = 64
SOURCE_FRAME_H = 64
SOURCE_FRAMES = 4

# OpenPets/Codex custom pets use a fixed 8 x 9 atlas. The app owns the
# reaction table, so keep every row populated and center our smaller sprite
# inside each 192 x 208 cell.
ROW_TO_SOURCE = [
    "idle",
    "coding",
    "success",
    "success",
    "error",
    "thinking",
    "searching",
    "terminal",
    "falling",
]
SOURCE_STATES = [
    "idle",
    "thinking",
    "coding",
    "terminal",
    "searching",
    "success",
    "falling",
    "error",
]
SOURCE_STATE_ROW = {state: index for index, state in enumerate(SOURCE_STATES)}


def _windows_user_codex_pets_dir():
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        return os.path.join(userprofile, ".codex", "pets", PET_ID)

    parts = os.path.abspath(ROOT).split(os.sep)
    if len(parts) > 4 and parts[1:4] == ["mnt", "c", "Users"]:
        return os.path.join(
            os.sep,
            "mnt",
            "c",
            "Users",
            parts[4],
            ".codex",
            "pets",
            PET_ID,
        )

    return os.path.join(os.path.expanduser("~"), ".codex", "pets", PET_ID)


def _save_webp(src, dest, scale=1):
    image = Image.open(src).convert("RGBA")
    if scale != 1:
        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    image.save(dest, "WEBP", lossless=True, exact=True, method=6)


def _build_openpets_atlas(src, dest):
    source = Image.open(src).convert("RGBA")
    atlas = Image.new("RGBA", (ATLAS_COLS * CELL_W, ATLAS_ROWS * CELL_H), (0, 0, 0, 0))

    sprite_scale = 2
    sprite_w = SOURCE_FRAME_W * sprite_scale
    sprite_h = SOURCE_FRAME_H * sprite_scale
    cell_x = (CELL_W - sprite_w) // 2
    cell_y = CELL_H - sprite_h - 22

    for row, state in enumerate(ROW_TO_SOURCE):
        source_row = SOURCE_STATE_ROW[state]
        for col in range(ATLAS_COLS):
            source_col = col % SOURCE_FRAMES
            frame = source.crop(
                (
                    source_col * SOURCE_FRAME_W,
                    source_row * SOURCE_FRAME_H,
                    (source_col + 1) * SOURCE_FRAME_W,
                    (source_row + 1) * SOURCE_FRAME_H,
                )
            )
            frame = frame.resize((sprite_w, sprite_h), Image.Resampling.NEAREST)
            atlas.alpha_composite(frame, (col * CELL_W + cell_x, row * CELL_H + cell_y))

    atlas.save(dest, "WEBP", lossless=True, exact=True, method=6)


def main():
    out_dir = _windows_user_codex_pets_dir()
    dist_dir = os.path.join(ROOT, "dist")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)

    pet_json = {
        "id": PET_ID,
        "displayName": PET_NAME,
        "description": DESCRIPTION,
        "spritesheetPath": "spritesheet.webp",
    }

    with open(os.path.join(out_dir, "pet.json"), "w", encoding="utf-8") as f:
        json.dump(pet_json, f, indent=2)
        f.write("\n")

    spritesheet_out = os.path.join(out_dir, "spritesheet.webp")
    preview_out = os.path.join(out_dir, "preview.webp")
    _build_openpets_atlas(
        os.path.join(ROOT, "assets", "codex_woodling_spritesheet.png"),
        spritesheet_out,
    )
    shutil.copyfile(spritesheet_out, preview_out)

    # Keep a copy in the project for inspection/versioning.
    project_pack = os.path.join(ROOT, "openpets", PET_ID)
    if os.path.exists(project_pack):
        shutil.rmtree(project_pack)
    shutil.copytree(out_dir, project_pack)

    zip_path = os.path.join(dist_dir, f"{PET_ID}-openpets.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in ("pet.json", "spritesheet.webp", "preview.webp"):
            z.write(os.path.join(out_dir, name), arcname=name)

    print(out_dir)
    print(project_pack)
    print(zip_path)


if __name__ == "__main__":
    main()
