"""
system_controller.py — Maps recognized gestures to OS-level actions.

Actions include:
  - Cursor movement (pyautogui)
  - Left click
  - Scrolling
  - Media play/pause (simulated key press)
  - Volume control (pycaw)  [optional]
  - Brightness control (screen-brightness-control)  [optional]
"""

import time
import pyautogui
import numpy as np
from typing import List, Tuple, Optional

import config

# Disable pyautogui fail-safe and delay
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# --------------------------------------------------------------------------- #
#  Optional: Volume control via pycaw (Windows only)
# --------------------------------------------------------------------------- #
_volume_interface = None
_volume_range = None

if config.VOLUME_ENABLED:
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        _volume_interface = devices.EndpointVolume
        _volume_range = _volume_interface.GetVolumeRange()
    except Exception as e:
        print(f"[system_controller] Volume control unavailable: {e}")

# --------------------------------------------------------------------------- #
#  Optional: Brightness control
# --------------------------------------------------------------------------- #
_sbc = None
if config.BRIGHTNESS_ENABLED:
    try:
        import screen_brightness_control as sbc
        _sbc = sbc
    except Exception as e:
        print(f"[system_controller] Brightness control unavailable: {e}")


class SystemController:
    """
    Executes system actions based on detected gestures and landmark data.
    Call execute() every frame with the current gesture and landmarks.
    """

    def __init__(self):
        # Smoothed cursor position (EMA)
        self._smooth_x: float = config.SCREEN_W / 2
        self._smooth_y: float = config.SCREEN_H / 2

        # Previous index-finger y for scroll delta
        self._prev_index_y: Optional[float] = None

        # Cooldown for play/pause to avoid repeated triggers
        self._last_action_time: float = 0
        self._action_cooldown: float = 1.0  # seconds

        # Track pinch state — click fires only on rising edge
        self._pinch_active: bool = False

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def execute(
        self,
        gesture: str,
        landmarks: Optional[List[Tuple[float, float, float]]] = None,
    ) -> str:
        """
        Perform the action mapped to *gesture*.

        Returns:
            Human-readable action description for the UI overlay.
        """
        if not config.SYSTEM_CONTROL_ENABLED:
            return f"[Display Only] {gesture}"

        action_key = config.GESTURE_ACTIONS.get(gesture, "idle")

        if action_key == "cursor" and landmarks:
            return self._move_cursor(landmarks)
        if action_key == "scroll" and landmarks:
            return self._scroll(landmarks)
        if action_key == "click":
            return self._click()
        if action_key == "pause":
            return self._play_pause("Pause")
        if action_key == "play":
            return self._play_pause("Play")

        # Reset transient state when gesture changes
        if action_key != "scroll":
            self._prev_index_y = None
        if action_key != "click":
            self._pinch_active = False

        return "Idle"

    # ------------------------------------------------------------------ #
    #  Cursor movement
    # ------------------------------------------------------------------ #
    def _move_cursor(self, lm) -> str:
        """Move mouse cursor to screen position mapped from index tip."""
        ix, iy = lm[8][0], lm[8][1]  # index finger tip (normalised)

        # Map webcam ROI (with margin) → full screen
        margin = config.CURSOR_FRAME_MARGIN / config.FRAME_WIDTH
        raw_x = np.interp(ix, [margin, 1 - margin], [0, config.SCREEN_W])
        raw_y = np.interp(iy, [margin, 1 - margin], [0, config.SCREEN_H])

        # EMA smoothing to reduce jitter
        a = config.CURSOR_SMOOTHING_ALPHA
        self._smooth_x = a * raw_x + (1 - a) * self._smooth_x
        self._smooth_y = a * raw_y + (1 - a) * self._smooth_y

        sx = max(0, min(config.SCREEN_W - 1, int(self._smooth_x)))
        sy = max(0, min(config.SCREEN_H - 1, int(self._smooth_y)))

        pyautogui.moveTo(sx, sy, _pause=False)
        return f"Cursor -> ({sx}, {sy})"

    # ------------------------------------------------------------------ #
    #  Scroll
    # ------------------------------------------------------------------ #
    def _scroll(self, lm) -> str:
        """Scroll based on vertical movement of the index finger."""
        iy = lm[8][1]

        if self._prev_index_y is None:
            self._prev_index_y = iy
            return "Scroll ready"

        delta = self._prev_index_y - iy  # positive = hand UP = scroll up
        self._prev_index_y = iy

        if abs(delta) < config.SCROLL_DEAD_ZONE:
            return "Scroll (waiting)"

        amount = int(delta * config.SCROLL_SPEED * 10)
        pyautogui.scroll(amount, _pause=False)
        direction = "UP" if amount > 0 else "DOWN"
        return f"Scroll {direction} ({amount})"

    # ------------------------------------------------------------------ #
    #  Click
    # ------------------------------------------------------------------ #
    def _click(self) -> str:
        """Fire a left-click only on the rising edge of a pinch."""
        if not self._pinch_active:
            self._pinch_active = True
            pyautogui.click(_pause=False)
            return "Click!"
        return "Pinch held"

    # ------------------------------------------------------------------ #
    #  Play / Pause
    # ------------------------------------------------------------------ #
    def _play_pause(self, label: str) -> str:
        """Simulate media play/pause key with cooldown."""
        now = time.time()
        if now - self._last_action_time < self._action_cooldown:
            return f"{label} (cooldown)"
        self._last_action_time = now
        pyautogui.press("playpause")
        return label

    # ------------------------------------------------------------------ #
    #  Volume & Brightness utilities
    # ------------------------------------------------------------------ #
    @staticmethod
    def set_volume(level: float) -> None:
        """Set system volume. *level* is 0.0 - 1.0."""
        if _volume_interface is None:
            return
        min_db, max_db, _ = _volume_range
        target = np.interp(level, [0, 1], [min_db, max_db])
        _volume_interface.SetMasterVolumeLevel(float(target), None)

    @staticmethod
    def set_brightness(level: float) -> None:
        """Set screen brightness. *level* is 0.0 - 1.0."""
        if _sbc is None:
            return
        _sbc.set_brightness(int(level * 100))
