"""
gesture_recognizer.py — Pure-logic gesture classification from hand landmarks.

No side effects — takes landmark data, returns a gesture name string.
Includes debounce logic to prevent gesture flickering.
"""

import math
from typing import List, Tuple

import config


class GestureRecognizer:
    """
    Classifies a set of 21 hand landmarks into one of the supported gestures.

    Supported gestures:
        • "Open Palm"    — all five fingers extended
        • "Fist"         — all five fingers curled
        • "Index Pointer" — only index finger extended
        • "Two Fingers"  — index + middle extended, rest curled
        • "Pinch"        — thumb tip close to index tip
        • "None"         — no recognisable gesture
    """

    # Finger tip and PIP (proximal interphalangeal) landmark IDs.
    # For the thumb we compare tip to IP joint (id 3) since it moves laterally.
    FINGER_TIPS = [4, 8, 12, 16, 20]
    FINGER_PIPS = [3, 6, 10, 14, 18]
    FINGER_NAMES = ["thumb", "index", "middle", "ring", "pinky"]

    def __init__(self):
        # Debounce state
        self._prev_gesture: str = "None"
        self._streak: int = 0

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def recognize(self, landmarks: List[Tuple[float, float, float]]) -> str:
        """
        Classify the gesture from normalized (0-1) landmarks.

        Args:
            landmarks: list of 21 (x, y, z) tuples (normalised coordinates).

        Returns:
            Gesture name string.
        """
        raw_gesture = self._classify(landmarks)
        return self._debounce(raw_gesture)

    # ------------------------------------------------------------------ #
    #  Classification logic
    # ------------------------------------------------------------------ #
    def _classify(self, lm: List[Tuple[float, float, float]]) -> str:
        """Determine the raw gesture (before debounce)."""

        # --- Check pinch first (overrides other gestures) ---
        pinch_dist = self._distance(lm[4], lm[8])
        hand_diag = self._hand_diagonal(lm)
        if hand_diag > 0 and (pinch_dist / hand_diag) < config.PINCH_DISTANCE_THRESHOLD:
            return "Pinch"

        # --- Determine which fingers are extended ---
        extended = self._get_extended_fingers(lm)
        num_extended = sum(extended)

        # All five up → Open Palm
        if num_extended == 5:
            return "Open Palm"

        # None up → Fist
        if num_extended == 0:
            return "Fist"

        # Only index → Index Pointer
        if extended == [False, True, False, False, False]:
            return "Index Pointer"

        # Index + middle → Two Fingers (V / peace sign)
        if extended == [False, True, True, False, False]:
            return "Two Fingers"

        # Index + middle (thumb may be out too, common natural pose)
        if extended[1] and extended[2] and not extended[3] and not extended[4]:
            return "Two Fingers"

        return "None"

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def _get_extended_fingers(self, lm) -> List[bool]:
        """
        Return a list of 5 bools indicating whether each finger is extended.

        Thumb uses a lateral check (x-axis) instead of vertical because
        the thumb moves sideways relative to the palm.
        """
        extended = []
        for i, (tip_id, pip_id) in enumerate(
            zip(self.FINGER_TIPS, self.FINGER_PIPS)
        ):
            if i == 0:
                # Thumb: compare x position.  For a right hand appearing
                # in a mirrored frame the thumb tip is to the LEFT of the
                # IP joint when extended.  We use abs difference > threshold
                # as a simpler heuristic that works for both hands.
                extended.append(
                    abs(lm[tip_id][0] - lm[pip_id][0]) > config.FINGER_EXTEND_THRESHOLD * 2
                )
            else:
                # Other fingers: tip y < pip y means extended (y increases downward).
                extended.append(
                    lm[tip_id][1] < lm[pip_id][1] - config.FINGER_EXTEND_THRESHOLD
                )
        return extended

    @staticmethod
    def _distance(p1: Tuple[float, ...], p2: Tuple[float, ...]) -> float:
        """Euclidean distance between two 2-D or 3-D points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1[:2], p2[:2])))

    @staticmethod
    def _hand_diagonal(lm: List[Tuple[float, float, float]]) -> float:
        """Diagonal of the hand's bounding box (normalised coordinates)."""
        xs = [p[0] for p in lm]
        ys = [p[1] for p in lm]
        return math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2)

    # ------------------------------------------------------------------ #
    #  Debounce
    # ------------------------------------------------------------------ #
    def _debounce(self, gesture: str) -> str:
        """
        Only switch to a new gesture after it has been detected for
        GESTURE_DEBOUNCE_FRAMES consecutive frames.
        """
        if gesture == self._prev_gesture:
            self._streak += 1
        else:
            self._streak = 1
            self._prev_gesture = gesture

        if self._streak >= config.GESTURE_DEBOUNCE_FRAMES:
            return gesture

        # Not enough consecutive frames yet — return the last stable gesture
        # (or "None" at the very start).
        return self._prev_gesture if self._streak >= config.GESTURE_DEBOUNCE_FRAMES else gesture
