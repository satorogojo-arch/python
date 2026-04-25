# 🖐 Real-Time Hand Gesture Control System

A modular, real-time hand gesture recognition system that uses your webcam to detect hand landmarks and map gestures to system actions like cursor control, scrolling, clicking, and media playback.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange)

---

## ✨ Features

- **Real-time hand tracking** via MediaPipe (21 landmarks per hand)
- **5 built-in gestures** with debounce for stable recognition
- **System control** — mouse cursor, scroll, click, media keys
- **Volume & brightness** control (Windows)
- **Polished HUD overlay** — FPS counter, gesture label, guide panel
- **Fully modular** — swap/add gestures by editing `config.py`

## 📋 Gesture Reference

| Gesture | Action | How to Perform |
|---------|--------|----------------|
| 🖐 Open Palm | Pause / Stop | Extend all five fingers |
| ✊ Fist | Play / Start | Close all fingers into a fist |
| ☝ Index Pointer | Move Cursor | Point only your index finger |
| ✌ Two Fingers | Scroll | Extend index + middle fingers, move hand up/down |
| 🤏 Pinch | Click | Touch thumb tip to index tip |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or newer
- A webcam
- Windows OS (for volume/brightness; gesture detection works on any OS)

### Installation

```bash
# 1. Navigate to the project folder
cd "hand gesture"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `Q` | Quit the application |
| `S` | Toggle system control ON/OFF |
| `G` | Show/hide gesture guide overlay |

## ⚙️ Customization

All settings live in **`config.py`**:

| Setting | What it does |
|---------|-------------|
| `MAX_NUM_HANDS` | Number of hands to track (1 or 2) |
| `PINCH_DISTANCE_THRESHOLD` | Sensitivity for pinch detection |
| `CURSOR_SMOOTHING_ALPHA` | Cursor smoothness (0 = very smooth, 1 = raw) |
| `GESTURE_DEBOUNCE_FRAMES` | Frames before gesture switch (higher = more stable) |
| `SYSTEM_CONTROL_ENABLED` | Start with system control on/off |
| `GESTURE_ACTIONS` | Map gesture names to action keys |

## 🏗 Project Structure

```
hand gesture/
├── config.py              # All settings and thresholds
├── hand_detector.py       # MediaPipe hand detection wrapper
├── gesture_recognizer.py  # Gesture classification logic
├── system_controller.py   # Gesture → system action mapping
├── ui_overlay.py          # HUD overlay rendering
├── main.py                # Main application loop
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot open webcam" | Check `CAMERA_INDEX` in `config.py` (try 0, 1, or 2) |
| Low FPS | Lower `MIN_DETECTION_CONFIDENCE` or reduce `FRAME_WIDTH/HEIGHT` |
| Gesture flickering | Increase `GESTURE_DEBOUNCE_FRAMES` |
| Cursor too jittery | Lower `CURSOR_SMOOTHING_ALPHA` (e.g., 0.2) |
| Volume not working | Ensure `pycaw` and `comtypes` are installed (Windows only) |

## 📄 License

MIT — free for personal and commercial use.
