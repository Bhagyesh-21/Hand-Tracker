"""
Air Paint - draw in the air with your index finger.

Gestures (hand facing the camera, view is mirrored):
    Index finger up only ............ DRAW
    Index + middle fingers up ....... SELECT (touch a toolbar button)
    Anything else (fist, palm) ...... IDLE (lift the pen)

Keys:
    q / ESC quit      c clear      z undo      y redo      s save PNG
    b cycle background (camera / white / black)
    + / - brush size  h toggle help      m toggle hand skeleton

Needs: pip install mediapipe opencv-python numpy
Model: hand_landmarker.task must sit next to this file.
"""
import datetime
import math
import os
import sys
import time

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "hand_landmarker.task")
SAVE_DIR = os.path.join(os.getcwd(), "paintings")

# ----------------------------------------------------------------- config
CAM_INDEX = 0
FRAME_W, FRAME_H = 1280, 720
SMOOTHING = 0.55          # 0 = no smoothing, closer to 1 = very smooth/laggy
MODE_STABLE_FRAMES = 3    # frames a gesture must hold before it counts
LOST_HAND_FRAMES = 6      # frames without a hand before the stroke ends
CLICK_COOLDOWN = 0.7      # seconds between action-button clicks
BRUSH_MIN, BRUSH_MAX = 2, 60

# name -> BGR. (20,20,20) is used for "black" so it still counts as ink.
COLORS = [
    ("Red", (60, 60, 240)),
    ("Orange", (0, 140, 255)),
    ("Yellow", (0, 230, 255)),
    ("Green", (80, 200, 60)),
    ("Blue", (230, 120, 30)),
    ("Purple", (200, 60, 150)),
    ("Black", (20, 20, 20)),
    ("White", (255, 255, 255)),
]
TOOLS = ["Pen", "Line", "Rect", "Circle", "Eraser"]
ACTIONS = ["Undo", "Redo", "Clear", "Save", "Size-", "Size+"]
ROW_H = 56
TOOLBAR_H = ROW_H * 2


# ----------------------------------------------------------------- helpers
class Button:
    def __init__(self, kind, value, label, rect, color=None):
        self.kind, self.value, self.label = kind, value, label
        self.rect, self.color = rect, color  # rect = x1, y1, x2, y2

    def hit(self, p):
        x1, y1, x2, y2 = self.rect
        return x1 <= p[0] < x2 and y1 <= p[1] < y2


def build_toolbar(width):
    buttons = []
    n = len(COLORS)
    bw = width // n
    for i, (name, bgr) in enumerate(COLORS):
        buttons.append(Button("color", bgr, name, (i * bw, 0, (i + 1) * bw, ROW_H), bgr))
    items = [("tool", t) for t in TOOLS] + [("action", a) for a in ACTIONS]
    bw = width // len(items)
    for i, (kind, name) in enumerate(items):
        buttons.append(Button(kind, name, name, (i * bw, ROW_H, (i + 1) * bw, TOOLBAR_H)))
    return buttons


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def finger_states(pts):
    """pts: 21 (x, y) pixel points. Returns [index, middle, ring, pinky] up?
    Compares tip vs PIP distance from the wrist so it works at any rotation."""
    wrist = pts[0]
    up = []
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        up.append(dist(pts[tip], wrist) > dist(pts[pip], wrist) * 1.08)
    return up


def classify(up):
    index, middle, ring, pinky = up
    if index and middle and not ring and not pinky:
        return "select"
    if index and not middle and not ring and not pinky:
        return "draw"
    return "idle"


def render_stroke(canvas, s):
    """Draw one stroke dict onto a BGR canvas (0 = empty / transparent)."""
    t = s["type"]
    if t == "clear":
        canvas[:] = 0
        return
    color = (0, 0, 0) if s["erase"] else s["color"]
    size = s["size"]
    pts = s["points"]
    if not pts:
        return
    if t == "Pen" or t == "Eraser":
        if len(pts) == 1:
            cv2.circle(canvas, pts[0], max(1, size // 2), color, -1, cv2.LINE_AA)
        else:
            cv2.polylines(canvas, [np.array(pts, np.int32)], False, color, size, cv2.LINE_AA)
            # round caps
            cv2.circle(canvas, pts[0], size // 2, color, -1, cv2.LINE_AA)
            cv2.circle(canvas, pts[-1], size // 2, color, -1, cv2.LINE_AA)
    else:
        a, b = pts[0], pts[-1]
        if t == "Line":
            cv2.line(canvas, a, b, color, size, cv2.LINE_AA)
        elif t == "Rect":
            cv2.rectangle(canvas, a, b, color, size, cv2.LINE_AA)
        elif t == "Circle":
            cv2.circle(canvas, a, int(dist(a, b)), color, size, cv2.LINE_AA)


def composite(frame, canvas, bg_mode):
    h, w = canvas.shape[:2]
    if bg_mode == "camera":
        base = frame.copy()
    elif bg_mode == "white":
        base = np.full((h, w, 3), 255, np.uint8)
    else:
        base = np.zeros((h, w, 3), np.uint8)
    mask = canvas.any(axis=2)
    base[mask] = canvas[mask]
    return base


# ----------------------------------------------------------------- app
class AirPaint:
    def __init__(self):
        self.cap = self.open_camera()
        ok, frame = self.cap.read()
        if not ok:
            sys.exit("ERROR: camera opened but no frame received.")
        self.h, self.w = frame.shape[:2]
        self.buttons = build_toolbar(self.w)

        self.canvas = np.zeros((self.h, self.w, 3), np.uint8)
        self.strokes, self.redo = [], []
        self.cur = None  # stroke in progress

        self.color = COLORS[0][1]
        self.tool = "Pen"
        self.size = 8
        self.bg_mode = "camera"
        self.show_help = True
        self.show_skeleton = True

        self.mode = "idle"
        self.cand, self.cand_n = "idle", 0
        self.lost = 0
        self.pos = None
        self.last_click = 0.0
        self.toast, self.toast_until = "", 0.0

        if not os.path.exists(MODEL_PATH):
            sys.exit(f"ERROR: model not found: {MODEL_PATH}")
        opts = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(opts)

    @staticmethod
    def open_camera():
        for backend in ([cv2.CAP_DSHOW, cv2.CAP_ANY] if os.name == "nt" else [cv2.CAP_ANY]):
            cap = cv2.VideoCapture(CAM_INDEX, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
                return cap
        sys.exit("ERROR: cannot open camera. Try changing CAM_INDEX at the top of the file.")

    # ------------------------------------------------------------ actions
    def say(self, text):
        self.toast, self.toast_until = text, time.time() + 1.5

    def rebuild(self):
        self.canvas[:] = 0
        for s in self.strokes:
            render_stroke(self.canvas, s)

    def do_undo(self):
        if self.strokes:
            self.redo.append(self.strokes.pop())
            self.rebuild()
            self.say("Undo")

    def do_redo(self):
        if self.redo:
            self.strokes.append(self.redo.pop())
            self.rebuild()
            self.say("Redo")

    def do_clear(self):
        self.commit({"type": "clear", "points": [], "color": None, "size": 0, "erase": False})
        self.canvas[:] = 0
        self.say("Cleared (Undo brings it back)")

    def do_save(self, frame):
        os.makedirs(SAVE_DIR, exist_ok=True)
        name = datetime.datetime.now().strftime("paint_%Y%m%d_%H%M%S.png")
        path = os.path.join(SAVE_DIR, name)
        out = composite(frame, self.canvas, self.bg_mode)
        cv2.imwrite(path, out)
        self.say(f"Saved {name}")
        print("Saved:", path)

    def commit(self, stroke):
        self.strokes.append(stroke)
        self.redo.clear()

    def press(self, b, frame):
        if b.kind == "color":
            self.color = b.value
            if self.tool == "Eraser":
                self.tool = "Pen"
            self.say(f"Colour: {b.label}")
            return
        if b.kind == "tool":
            self.tool = b.value
            self.say(f"Tool: {b.value}")
            return
        now = time.time()
        if now - self.last_click < CLICK_COOLDOWN:
            return
        self.last_click = now
        {
            "Undo": self.do_undo,
            "Redo": self.do_redo,
            "Clear": self.do_clear,
            "Save": lambda: self.do_save(frame),
            "Size-": lambda: self.change_size(-4),
            "Size+": lambda: self.change_size(+4),
        }[b.value]()

    def change_size(self, d):
        self.size = max(BRUSH_MIN, min(BRUSH_MAX, self.size + d))
        self.say(f"Brush size: {self.size}")

    # ------------------------------------------------------------ strokes
    def begin_stroke(self, p):
        erase = self.tool == "Eraser"
        self.cur = {
            "type": self.tool,
            "points": [p],
            "color": self.color,
            "size": self.size * 3 if erase else self.size,
            "erase": erase,
        }

    def extend_stroke(self, p):
        s = self.cur
        if s["type"] in ("Pen", "Eraser"):
            last = s["points"][-1]
            if dist(last, p) >= 2:
                s["points"].append(p)
                cv2.line(self.canvas, last, p, (0, 0, 0) if s["erase"] else s["color"],
                         s["size"], cv2.LINE_AA)
        else:  # shapes keep only start + current end
            s["points"] = [s["points"][0], p]

    def end_stroke(self):
        s, self.cur = self.cur, None
        if not s:
            return
        if s["type"] in ("Pen", "Eraser"):
            render_stroke(self.canvas, s)  # round caps / single tap
        else:
            if len(s["points"]) < 2 or dist(*s["points"]) < 4:
                return
            render_stroke(self.canvas, s)
        self.commit(s)

    # ------------------------------------------------------------ per frame
    def update_mode(self, new):
        if new == self.cand:
            self.cand_n += 1
        else:
            self.cand, self.cand_n = new, 1
        if self.cand_n >= MODE_STABLE_FRAMES and self.cand != self.mode:
            if self.mode == "draw":
                self.end_stroke()
            self.mode = self.cand
            self.pos = None  # restart smoothing

    def smooth(self, raw):
        if self.pos is None:
            self.pos = raw
        else:
            a = SMOOTHING
            self.pos = (a * self.pos[0] + (1 - a) * raw[0], a * self.pos[1] + (1 - a) * raw[1])
        return int(self.pos[0]), int(self.pos[1])

    def process(self, frame, ts_ms):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.landmarker.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts_ms)
        cursor, pts = None, None
        if res.hand_landmarks:
            self.lost = 0
            lm = res.hand_landmarks[0]
            pts = [(int(p.x * self.w), int(p.y * self.h)) for p in lm]
            self.update_mode(classify(finger_states(pts)))
            cursor = self.smooth(pts[8])
        else:
            self.lost += 1
            if self.lost >= LOST_HAND_FRAMES:
                if self.mode == "draw":
                    self.end_stroke()
                self.mode, self.cand, self.cand_n, self.pos = "idle", "idle", 0, None
        if cursor:
            in_bar = cursor[1] < TOOLBAR_H
            if self.mode == "draw" and not in_bar:
                if self.cur is None:
                    self.begin_stroke(cursor)
                else:
                    self.extend_stroke(cursor)
            elif self.mode == "draw" and in_bar and self.cur is not None:
                self.end_stroke()
            if self.mode == "select" and self.cur is None:
                for b in self.buttons:
                    if b.hit(cursor):
                        self.press(b, frame)
                        break
        return cursor, pts

    # ------------------------------------------------------------ drawing UI
    def is_active(self, b):
        return (b.kind == "color" and b.value == self.color and self.tool != "Eraser") or \
               (b.kind == "tool" and b.value == self.tool)

    def draw_ui(self, img, cursor, pts):
        bar = img.copy()
        for b in self.buttons:
            x1, y1, x2, y2 = b.rect
            fill = b.color if b.color is not None else (60, 60, 60)
            cv2.rectangle(bar, (x1, y1), (x2, y2), fill, -1)
        cv2.addWeighted(bar, 0.85, img, 0.15, 0, img)
        for b in self.buttons:
            x1, y1, x2, y2 = b.rect
            active = self.is_active(b)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255) if active else (0, 0, 0),
                          4 if active else 1)
            label = b.label
            if b.label == "Size-" or b.label == "Size+":
                label = f"{b.label} ({self.size})"
            dark = b.color is not None and sum(b.color) > 450
            tc = (0, 0, 0) if dark else (255, 255, 255)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.putText(img, label, (x1 + (x2 - x1 - tw) // 2, y1 + (y2 - y1 + th) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, tc, 1, cv2.LINE_AA)

        # shape preview
        if self.cur and self.cur["type"] not in ("Pen", "Eraser") and len(self.cur["points"]) == 2:
            render_stroke(img, self.cur)

        if self.show_skeleton and pts:
            for c in vision.HandLandmarksConnections.HAND_CONNECTIONS:
                cv2.line(img, pts[c.start], pts[c.end], (200, 200, 200), 1, cv2.LINE_AA)
            for p in pts:
                cv2.circle(img, p, 3, (0, 200, 0), -1)

        if cursor:
            r = max(6, (self.size * 3 if self.tool == "Eraser" else self.size) // 2)
            if self.mode == "draw":
                cv2.circle(img, cursor, r, self.color if self.tool != "Eraser" else (255, 255, 255), -1)
                cv2.circle(img, cursor, r + 2, (255, 255, 255), 1, cv2.LINE_AA)
            elif self.mode == "select":
                cv2.circle(img, cursor, 16, (0, 255, 255), 3, cv2.LINE_AA)
            else:
                cv2.circle(img, cursor, 10, (180, 180, 180), 2, cv2.LINE_AA)

        label = {"draw": "DRAW", "select": "SELECT", "idle": "IDLE"}[self.mode]
        cv2.putText(img, f"{label} | {self.tool} | size {self.size} | bg {self.bg_mode}",
                    (10, self.h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        if self.show_help:
            lines = ["1 finger = draw   2 fingers = select/click   fist/palm = lift pen",
                     "q quit  c clear  z undo  y redo  s save  b background  +/- size  m skeleton  h help"]
            for i, t in enumerate(lines):
                cv2.putText(img, t, (10, TOOLBAR_H + 26 + i * 24), cv2.FONT_HERSHEY_SIMPLEX,
                            0.55, (0, 0, 0), 3, cv2.LINE_AA)
                cv2.putText(img, t, (10, TOOLBAR_H + 26 + i * 24), cv2.FONT_HERSHEY_SIMPLEX,
                            0.55, (255, 255, 255), 1, cv2.LINE_AA)
        if time.time() < self.toast_until:
            cv2.putText(img, self.toast, (self.w // 2 - 150, self.h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(img, self.toast, (self.w // 2 - 150, self.h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, cv2.LINE_AA)

    # ------------------------------------------------------------ main loop
    def run(self):
        print(__doc__)
        t0 = time.time()
        last_ts = -1
        while True:
            ok, frame = self.cap.read()
            if not ok:
                continue
            frame = cv2.flip(frame, 1)
            ts = max(int((time.time() - t0) * 1000), last_ts + 1)
            last_ts = ts
            cursor, pts = self.process(frame, ts)

            shown = composite(frame, self.canvas, self.bg_mode)
            self.draw_ui(shown, cursor, pts)
            cv2.imshow("Air Paint", shown)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            elif key == ord("c"):
                self.do_clear()
            elif key == ord("z"):
                self.do_undo()
            elif key == ord("y"):
                self.do_redo()
            elif key == ord("s"):
                self.do_save(frame)
            elif key == ord("b"):
                modes = ["camera", "white", "black"]
                self.bg_mode = modes[(modes.index(self.bg_mode) + 1) % 3]
            elif key in (ord("+"), ord("=")):
                self.change_size(+2)
            elif key in (ord("-"), ord("_")):
                self.change_size(-2)
            elif key == ord("h"):
                self.show_help = not self.show_help
            elif key == ord("m"):
                self.show_skeleton = not self.show_skeleton
            if cv2.getWindowProperty("Air Paint", cv2.WND_PROP_VISIBLE) < 1:
                break
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    AirPaint().run()
