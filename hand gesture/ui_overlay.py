"""
ui_overlay.py — Draws a polished HUD overlay on the video frame.

Renders:
  • Semi-transparent status bar with gesture name + FPS
  • Hand count and system-control mode indicator
  • Gesture guide panel (toggle with 'g' key)
"""

import cv2
import numpy as np

import config


class UIOverlay:
    """Renders HUD elements on top of the webcam frame."""

    # Gesture icons (simple text representations)
    GESTURE_ICONS = {
        "Open Palm":     "🖐",
        "Fist":          "✊",
        "Index Pointer": "👆",
        "Two Fingers":   "✌",
        "Pinch":         "🤏",
        "None":          "—",
    }

    def __init__(self):
        self.show_guide = False  # Toggle with 'g' key

    # ------------------------------------------------------------------ #
    #  Main draw call
    # ------------------------------------------------------------------ #
    def draw_hud(
        self,
        frame: np.ndarray,
        gesture: str,
        action_text: str,
        fps: float,
        num_hands: int,
        system_control: bool,
    ) -> None:
        """Draw all HUD elements onto *frame* (mutates in place)."""
        h, w = frame.shape[:2]

        # --- Top status bar (semi-transparent) ---
        self._draw_status_bar(frame, gesture, fps, num_hands, system_control, w)

        # --- Action text at bottom ---
        self._draw_action_bar(frame, action_text, h, w)

        # --- Gesture guide (optional) ---
        if self.show_guide:
            self._draw_gesture_guide(frame, h, w)

    # ------------------------------------------------------------------ #
    #  Status bar
    # ------------------------------------------------------------------ #
    def _draw_status_bar(self, frame, gesture, fps, num_hands, sys_ctrl, w):
        """Top bar: gesture name | FPS | hand count | mode."""
        bar_h = 50
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, bar_h), (30, 30, 30), -1)
        cv2.addWeighted(overlay, config.HUD_BG_ALPHA, frame, 1 - config.HUD_BG_ALPHA, 0, frame)

        # Gesture name
        icon = self.GESTURE_ICONS.get(gesture, "")
        gesture_text = f"Gesture: {gesture}  {icon}"
        cv2.putText(
            frame, gesture_text, (15, 33),
            cv2.FONT_HERSHEY_SIMPLEX, config.HUD_FONT_SCALE,
            config.HUD_COLOR, config.HUD_THICKNESS,
        )

        # FPS
        fps_text = f"FPS: {int(fps)}"
        cv2.putText(
            frame, fps_text, (w - 140, 33),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (0, 200, 255), 1,
        )

        # Hand count dot
        dot_color = (0, 255, 0) if num_hands > 0 else (0, 0, 200)
        cv2.circle(frame, (w - 25, 25), 10, dot_color, -1)

        # System control indicator
        mode = "SYS ON" if sys_ctrl else "DISPLAY"
        mode_color = (0, 255, 100) if sys_ctrl else (100, 100, 255)
        cv2.putText(
            frame, mode, (w - 260, 33),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_color, 1,
        )

    # ------------------------------------------------------------------ #
    #  Action bar
    # ------------------------------------------------------------------ #
    def _draw_action_bar(self, frame, action_text, h, w):
        """Bottom bar showing the current action being executed."""
        bar_h = 40
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - bar_h), (w, h), (30, 30, 30), -1)
        cv2.addWeighted(overlay, config.HUD_BG_ALPHA, frame, 1 - config.HUD_BG_ALPHA, 0, frame)

        cv2.putText(
            frame, f"Action: {action_text}", (15, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55,
            (220, 220, 220), 1,
        )

        # Hint
        cv2.putText(
            frame, "Q:Quit  S:Sys  G:Guide", (w - 280, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
            (150, 150, 150), 1,
        )

    # ------------------------------------------------------------------ #
    #  Gesture guide panel
    # ------------------------------------------------------------------ #
    def _draw_gesture_guide(self, frame, h, w):
        """Side panel listing all available gestures."""
        panel_w = 250
        x0 = w - panel_w - 10
        y0 = 60
        panel_h = 200

        overlay = frame.copy()
        cv2.rectangle(overlay, (x0, y0), (x0 + panel_w, y0 + panel_h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        cv2.putText(
            frame, "Gesture Guide", (x0 + 10, y0 + 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 200), 1,
        )

        gestures = [
            ("Open Palm", "Pause / Stop"),
            ("Fist", "Play / Start"),
            ("Index Finger", "Move Cursor"),
            ("Two Fingers", "Scroll"),
            ("Pinch", "Click"),
        ]
        for i, (name, action) in enumerate(gestures):
            y = y0 + 55 + i * 28
            cv2.putText(
                frame, f"{name}: {action}", (x0 + 15, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1,
            )
