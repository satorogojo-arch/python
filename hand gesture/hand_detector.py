"""
hand_detector.py — Wraps MediaPipe Tasks Hand Landmarker API.

Uses the new mediapipe.tasks.python.vision.HandLandmarker (Tasks API)
instead of the deprecated mp.solutions.hands.

Responsibilities:
  - Initialize MediaPipe hand-tracking pipeline
  - Process each video frame and return structured landmark data
  - Provide a helper to draw landmarks on the frame
"""

import os
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

import config

# Path to the hand landmarker model (downloaded separately)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")


@dataclass
class HandData:
    """Structured container for a single detected hand."""
    landmarks: List[Tuple[float, float, float]]   # 21 (x, y, z) normalized
    pixel_landmarks: List[Tuple[int, int]]         # 21 (px_x, px_y)
    handedness: str                                 # "Left" or "Right"
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0) # x_min, y_min, w, h


class HandDetector:
    """
    High-level wrapper around MediaPipe Tasks Hand Landmarker.

    Usage:
        detector = HandDetector()
        hands = detector.detect(frame)
        for hand in hands:
            detector.draw_landmarks(frame, hand)
    """

    # Finger-connection groups for coloured drawing
    FINGER_LANDMARK_IDS = {
        "thumb":  [1, 2, 3, 4],
        "index":  [5, 6, 7, 8],
        "middle": [9, 10, 11, 12],
        "ring":   [13, 14, 15, 16],
        "pinky":  [17, 18, 19, 20],
        "palm":   [0, 1, 5, 9, 13, 17, 0],
    }

    def __init__(
        self,
        max_hands: int = config.MAX_NUM_HANDS,
        detection_conf: float = config.MIN_DETECTION_CONFIDENCE,
        tracking_conf: float = config.MIN_TRACKING_CONFIDENCE,
    ):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Hand landmarker model not found at {MODEL_PATH}.\n"
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            )

        base_options = mp_python.BaseOptions(
            model_asset_path=MODEL_PATH
        )
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=tracking_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._frame_timestamp_ms = 0

    # --------------------------------------------------------------------- #
    #  Detection
    # --------------------------------------------------------------------- #
    def detect(self, frame: np.ndarray) -> List[HandData]:
        """
        Process a BGR frame and return a list of HandData objects.

        Args:
            frame: BGR image from OpenCV (uint8, HxWx3).

        Returns:
            List of HandData, one per detected hand (may be empty).
        """
        h, w, _ = frame.shape

        # Convert BGR → RGB and wrap in MediaPipe Image
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Monotonically increasing timestamp (required for VIDEO mode)
        self._frame_timestamp_ms += 33  # ~30 FPS
        result = self.landmarker.detect_for_video(mp_image, self._frame_timestamp_ms)

        detected_hands: List[HandData] = []

        if not result.hand_landmarks:
            return detected_hands

        for i, hand_lms in enumerate(result.hand_landmarks):
            # Normalised landmarks (0-1)
            norm_landmarks = [
                (lm.x, lm.y, lm.z) for lm in hand_lms
            ]

            # Pixel landmarks
            px_landmarks = [
                (int(lm.x * w), int(lm.y * h)) for lm in hand_lms
            ]

            # Bounding box
            xs = [p[0] for p in px_landmarks]
            ys = [p[1] for p in px_landmarks]
            x_min, y_min = min(xs), min(ys)
            bbox = (x_min, y_min, max(xs) - x_min, max(ys) - y_min)

            # Handedness label
            label = "Unknown"
            if result.handedness and i < len(result.handedness):
                label = result.handedness[i][0].category_name

            detected_hands.append(
                HandData(
                    landmarks=norm_landmarks,
                    pixel_landmarks=px_landmarks,
                    handedness=label,
                    bbox=bbox,
                )
            )

        return detected_hands

    # --------------------------------------------------------------------- #
    #  Drawing
    # --------------------------------------------------------------------- #
    def draw_landmarks(self, frame: np.ndarray, hand: HandData) -> None:
        """Draw coloured landmark dots and finger connections on *frame*."""
        px = hand.pixel_landmarks

        # Draw connections per finger group
        for finger, ids in self.FINGER_LANDMARK_IDS.items():
            color = config.FINGER_COLORS.get(finger, (255, 255, 255))
            for i in range(len(ids) - 1):
                pt1 = px[ids[i]]
                pt2 = px[ids[i + 1]]
                cv2.line(frame, pt1, pt2, color, config.CONNECTION_THICKNESS)

        # Draw landmark dots
        for idx, pt in enumerate(px):
            cv2.circle(frame, pt, config.LANDMARK_RADIUS, (255, 255, 255), -1)
            cv2.circle(frame, pt, config.LANDMARK_RADIUS - 2, (0, 0, 0), -1)

    # --------------------------------------------------------------------- #
    #  Cleanup
    # --------------------------------------------------------------------- #
    def close(self):
        """Release MediaPipe resources."""
        self.landmarker.close()
