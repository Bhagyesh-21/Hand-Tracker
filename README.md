# Air Paint
Draw in the air with your index finger (MediaPipe hand landmarks + OpenCV).

    pip install -r requirements.txt
    python air_paint.py

| Gesture | Action |
|---|---|
| Index finger only | Draw |
| Index + middle fingers | Select / click toolbar button (hover on it) |
| Fist / open palm | Lift the pen |

Toolbar: 8 colours, Pen, Line, Rect, Circle, Eraser, Undo, Redo, Clear, Save, Size-/Size+.
Keys: q quit, c clear, z undo, y redo, s save, b background (camera/white/black), +/- size, h help, m skeleton.
Saved images go to ./paintings/. If the camera does not open, change CAM_INDEX at the top of air_paint.py.
Tuning knobs (SMOOTHING, MODE_STABLE_FRAMES, ...) are also at the top.
