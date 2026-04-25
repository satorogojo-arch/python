"""
config.py — Central configuration for the Hand Gesture Control System.

All tunable parameters live here so gestures can be customized
without touching detection or control logic.
"""

import pyautogui

# ---------------------------------------------------------------------------
# Screen dimensions (used to map webcam coordinates → screen coordinates)
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = pyautogui.size()

# ---------------------------------------------------------------------------
# Webcam settings
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0          # Default webcam
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# ---------------------------------------------------------------------------
# MediaPipe Hands settings
# ---------------------------------------------------------------------------
MAX_NUM_HANDS           = 1       # Track one hand (user preference)
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE  = 0.6

# ---------------------------------------------------------------------------
# Gesture recognition thresholds
# ---------------------------------------------------------------------------

# A finger is "extended" when its TIP is above (lower y) its PIP joint
# by at least this fraction of the hand's bounding-box height.
FINGER_EXTEND_THRESHOLD = 0.02

# Pinch: distance between thumb-tip (4) and index-tip (8)
# as a fraction of the hand diagonal — below this → pinch detected.
PINCH_DISTANCE_THRESHOLD = 0.07

# Number of consecutive frames a gesture must persist before it is reported
# (prevents flickering between gestures).
GESTURE_DEBOUNCE_FRAMES = 4

# ---------------------------------------------------------------------------
# Cursor / mouse control
# ---------------------------------------------------------------------------
CURSOR_SMOOTHING_ALPHA = 0.35     # EMA smoothing (0 = max smooth, 1 = raw)
CURSOR_FRAME_MARGIN    = 80       # px margin inside webcam frame for mapping

# Scroll speed multiplier (pixels per frame of vertical delta)
SCROLL_SPEED = 15

# Minimum vertical movement (normalized) to trigger a scroll tick
SCROLL_DEAD_ZONE = 0.01

# ---------------------------------------------------------------------------
# System control mode (toggle with 's' key at runtime)
# ---------------------------------------------------------------------------
SYSTEM_CONTROL_ENABLED = True     # Start with system control ON

# ---------------------------------------------------------------------------
# Volume / brightness mapping (optional — used when pinch-slide is detected)
# ---------------------------------------------------------------------------
VOLUME_ENABLED     = True
BRIGHTNESS_ENABLED = True

# ---------------------------------------------------------------------------
# UI / overlay
# ---------------------------------------------------------------------------
HUD_FONT_SCALE   = 0.7
HUD_THICKNESS    = 2
HUD_COLOR        = (0, 255, 200)     # Cyan-green
HUD_BG_ALPHA     = 0.55              # Transparency for status bar
LANDMARK_RADIUS  = 5
CONNECTION_THICKNESS = 2

# Finger colors for landmark drawing (BGR)
FINGER_COLORS = {
    "thumb":  (255, 100, 100),   # Blue-ish
    "index":  (100, 255, 100),   # Green
    "middle": (100, 100, 255),   # Red
    "ring":   (255, 255, 100),   # Cyan
    "pinky":  (255, 100, 255),   # Magenta
    "palm":   (200, 200, 200),   # Gray
}

# ---------------------------------------------------------------------------
# Gesture → action mapping names
# These string keys are used by SystemController to dispatch actions.
# ---------------------------------------------------------------------------
GESTURE_ACTIONS = {
    "Open Palm":    "pause",
    "Fist":         "play",
    "Index Pointer":"cursor",
    "Two Fingers":  "scroll",
    "Pinch":        "click",
    "None":         "idle",
}
