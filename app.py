#!/usr/bin/env python3
import json
import math
import os
import socket
import subprocess
import sys
import time

try:
    import tkinter as tk
except Exception:
    class _TkStub:
        Tk = object
        Canvas = object
        Menu = object

    tk = _TkStub()


APP_DIR = os.path.dirname(os.path.realpath(__file__))
MANIFEST_PATH = os.path.join(APP_DIR, "assets", "woodling.pet.json")
CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 47329
TRANSPARENT_BG = "#ff00ff"
WINDOW_PAD = 10
FLOOR_GAP = 40
WALK_SPEED = 30.0
FPS_MS = 33
SUCCESS_DURATION = 4.0
SUCCESS_JUMP_VELOCITY = -285.0
JUMP_GRAVITY = 900.0
FALL_GRAVITY = 1250.0


def control_dir():
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        return os.path.join(local_appdata, "CodexWoodling")

    parts = os.path.abspath(APP_DIR).split(os.sep)
    if len(parts) > 4 and parts[1:4] == ["mnt", "c", "Users"]:
        return os.path.join(
            os.sep,
            "mnt",
            "c",
            "Users",
            parts[4],
            "AppData",
            "Local",
            "CodexWoodling",
        )

    return os.path.join(os.path.expanduser("~"), ".codex_woodling")


CONTROL_DIR = control_dir()
CONTROL_PATH = os.path.join(CONTROL_DIR, "control.json")
PID_PATH = os.path.join(CONTROL_DIR, "woodling.pid")


def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["stateIndex"] = {state: i for i, state in enumerate(manifest["states"])}
    return manifest


MANIFEST = load_manifest()
STATES = set(MANIFEST["states"])
ALIASES = MANIFEST.get("aliases", {})


def normalize_state(state):
    state = (state or "idle").strip().lower()
    state = ALIASES.get(state, state)
    if state not in STATES:
        raise ValueError(f"Unknown state: {state}")
    return state


def send_command(state, duration=6.0):
    os.makedirs(CONTROL_DIR, exist_ok=True)
    payload = {
        "state": normalize_state(state),
        "duration": max(0.5, min(60.0, float(duration))),
        "nonce": f"{time.time()}-{os.getpid()}",
        "sentAt": time.time(),
    }
    data = json.dumps(payload).encode("utf-8")
    with open(CONTROL_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (CONTROL_HOST, CONTROL_PORT))
        sock.close()
    except Exception:
        pass


def make_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((CONTROL_HOST, CONTROL_PORT))
    sock.setblocking(False)
    return sock


def read_control_file():
    try:
        with open(CONTROL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def drain_socket(sock):
    commands = []
    while True:
        try:
            data, _addr = sock.recvfrom(4096)
        except BlockingIOError:
            break
        except Exception:
            break
        try:
            commands.append(json.loads(data.decode("utf-8")))
        except Exception:
            pass
    return commands


def start_detached():
    py = sys.executable or "python"
    flags = 0
    kwargs = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
    }
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        kwargs["creationflags"] = flags
    subprocess.Popen([py, os.path.realpath(__file__)], **kwargs)


class WoodlingApp(tk.Tk):
    def __init__(self):
        self.server = make_server_socket()
        super().__init__()

        os.makedirs(CONTROL_DIR, exist_ok=True)
        with open(PID_PATH, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))

        self.manifest = MANIFEST
        self.frame_w = self.manifest["frameWidth"]
        self.frame_h = self.manifest["frameHeight"]
        self.frames_per_state = self.manifest["framesPerState"]
        self.scale = self.manifest.get("scale", 1)
        self.window_w = self.frame_w * self.scale + WINDOW_PAD * 2
        self.window_h = self.frame_h * self.scale + WINDOW_PAD * 2

        self.title(self.manifest["displayName"])
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=TRANSPARENT_BG)
        try:
            self.wm_attributes("-transparentcolor", TRANSPARENT_BG)
        except Exception:
            pass

        self.geometry(f"{self.window_w}x{self.window_h}")
        self.canvas = tk.Canvas(
            self,
            width=self.window_w,
            height=self.window_h,
            bg=TRANSPARENT_BG,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.images_right = self.load_images(self.manifest["spritesheet"])
        self.images_left = self.load_images(self.manifest["spritesheetLeft"])

        self.status = "idle"
        self.forced_until = 0.0
        self.last_nonce = ""
        self.last_file_nonce = ""
        self.frame = 0
        self.phase = 0.0
        self.last_tick = time.time()
        self.walk_vx = -WALK_SPEED
        self.air_y = 0.0
        self.air_vy = 0.0
        self.drag_offset = None

        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.release_drag)
        self.bind("<ButtonPress-3>", self.menu)

        self.place_on_floor()
        self.after(FPS_MS, self.tick)
        self.after(120, self.poll_control)

    def load_images(self, sheet_name):
        path = os.path.join(APP_DIR, "assets", sheet_name)
        sheet = tk.PhotoImage(file=path)
        images = {}
        for state in self.manifest["states"]:
            row = self.manifest["stateIndex"][state]
            images[state] = []
            for col in range(self.frames_per_state):
                tile = tk.PhotoImage(width=self.frame_w, height=self.frame_h)
                tile.tk.call(
                    tile,
                    "copy",
                    sheet,
                    "-from",
                    col * self.frame_w,
                    row * self.frame_h,
                    (col + 1) * self.frame_w,
                    (row + 1) * self.frame_h,
                    "-to",
                    0,
                    0,
                )
                if self.scale != 1:
                    tile = tile.zoom(self.scale, self.scale)
                images[state].append(tile)
        images["_sheet"] = sheet
        return images

    def floor_y(self):
        return self.winfo_screenheight() - self.window_h - FLOOR_GAP

    def place_on_floor(self):
        x = self.winfo_screenwidth() - self.window_w - 20
        self.geometry(f"+{max(0, x)}+{max(0, self.floor_y())}")

    def current_visual_state(self):
        if self.air_y < 0 and self.air_vy > 0 and self.status != "success":
            return "falling"
        return self.status

    def current_images(self):
        return self.images_left if self.walk_vx < 0 else self.images_right

    def set_state(self, state, duration=6.0):
        self.status = normalize_state(state)
        self.forced_until = time.time() + duration
        if self.status == "success":
            self.air_y = 0.0
            self.air_vy = SUCCESS_JUMP_VELOCITY

    def poll_control(self):
        commands = drain_socket(self.server)
        file_payload = read_control_file()
        if file_payload:
            commands.append(file_payload)
        for payload in commands:
            nonce = payload.get("nonce", "")
            if not nonce or nonce == self.last_nonce:
                continue
            try:
                state = normalize_state(payload.get("state", "idle"))
                duration = float(payload.get("duration", 6.0))
            except Exception:
                continue
            self.last_nonce = nonce
            self.set_state(state, duration)
        self.after(120, self.poll_control)

    def tick(self):
        now = time.time()
        dt = max(0.001, min(0.08, now - self.last_tick))
        self.last_tick = now

        if self.forced_until and now >= self.forced_until:
            self.status = "idle"
            self.forced_until = 0.0

        bpm = {
            "idle": 42,
            "thinking": 82,
            "coding": 165,
            "terminal": 150,
            "searching": 112,
            "success": 130,
            "falling": 130,
            "error": 160,
        }.get(self.status, 80)
        self.phase = (self.phase + (2 * math.pi) * (bpm / 60.0) * dt) % (2 * math.pi)
        self.frame = int((self.phase / (2 * math.pi)) * self.frames_per_state) % self.frames_per_state

        self.tick_air(dt)
        if self.drag_offset is None:
            self.walk(dt)
        self.draw()
        self.after(FPS_MS, self.tick)

    def tick_air(self, dt):
        if self.air_y == 0 and self.air_vy == 0:
            return
        gravity = JUMP_GRAVITY if self.air_vy < 0 else FALL_GRAVITY
        self.air_vy += gravity * dt
        self.air_y += self.air_vy * dt
        if self.air_y >= 0:
            self.air_y = 0.0
            self.air_vy = 0.0

    def walk(self, dt):
        x = self.winfo_x() + self.walk_vx * dt
        max_x = self.winfo_screenwidth() - self.window_w
        if x <= 0 or x >= max_x:
            self.walk_vx *= -1
            self.phase = 0.0
            x = max(0, min(max_x, x))
        y = self.floor_y() + self.air_y
        self.geometry(f"+{int(x)}+{max(0, int(y))}")

    def draw(self):
        self.canvas.delete("all")
        state = self.current_visual_state()
        img = self.current_images()[state][self.frame]
        self.canvas.create_image(self.window_w // 2, self.window_h // 2, image=img)

    def start_drag(self, event):
        self.drag_offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def drag(self, event):
        if self.drag_offset:
            x = event.x_root - self.drag_offset[0]
            y = event.y_root - self.drag_offset[1]
            self.geometry(f"+{x}+{y}")

    def release_drag(self, _event):
        floor = self.floor_y()
        max_x = self.winfo_screenwidth() - self.window_w
        x = max(0, min(max_x, self.winfo_x()))
        self.air_y = min(0.0, self.winfo_y() - floor)
        self.air_vy = 35.0 if self.air_y < 0 else 0.0
        self.geometry(f"+{int(x)}+{max(0, int(floor + self.air_y))}")
        self.drag_offset = None

    def menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        for state in ("idle", "thinking", "coding", "terminal", "searching", "success", "error"):
            menu.add_command(label=state.title(), command=lambda s=state: self.set_state(s, 6))
        menu.add_separator()
        menu.add_command(label="Quit", command=self.destroy)
        menu.tk_popup(event.x_root, event.y_root)


def usage():
    states = "|".join(sorted(STATES))
    print(f"Usage: app.py --serve | --start | --status <{states}> [--duration seconds] | --stop")


def stop_existing():
    if os.name != "nt":
        return
    subprocess.call(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*tung tung tung sahur pet*app.py*' -or $_.CommandLine -like '*woodlingctl.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    args = sys.argv[1:]
    if not args or "--serve" in args:
        if not hasattr(tk, "PhotoImage"):
            print("Tkinter is required to show the desktop pet. Run with Windows Python, or use --status from WSL.")
            return 1
        try:
            app = WoodlingApp()
        except OSError:
            return 0
        app.mainloop()
        return 0

    if "--start" in args:
        start_detached()
        return 0

    if "--stop" in args:
        stop_existing()
        return 0

    if "--status" in args:
        try:
            state = args[args.index("--status") + 1]
        except Exception:
            usage()
            return 1
        duration = 6.0
        if "--duration" in args:
            try:
                duration = float(args[args.index("--duration") + 1])
            except Exception:
                duration = 6.0
        send_command(state, duration)
        print(f"sent status: {normalize_state(state)}")
        return 0

    usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
