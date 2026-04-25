"""
main.py — Entry point for the Hand Gesture Control System.

Orchestrates the webcam loop, hand detection, gesture recognition,
system control, and UI overlay rendering.

Controls:
    Q  — Quit
    S  — Toggle system control mode (ON / Display-only)
    G  — Toggle gesture guide overlay
"""

import time
import cv2

import config
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from system_controller import SystemController
from ui_overlay import UIOverlay


def main():
    # ------------------------------------------------------------------ #
    #  Initialise components
    # ------------------------------------------------------------------ #
    print("[main] Starting Hand Gesture Control System...")
    print(f"[main] Screen size: {config.SCREEN_W}x{config.SCREEN_H}")
    print(f"[main] System control: {'ON' if config.SYSTEM_CONTROL_ENABLED else 'OFF'}")

    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print("[main] ERROR: Cannot open webcam. Check CAMERA_INDEX in config.py.")
        return

    detector   = HandDetector()
    recognizer = GestureRecognizer()
    controller = SystemController()
    overlay    = UIOverlay()

    # FPS tracking
    prev_time = time.time()
    fps = 0.0

    print("[main] Running — press 'Q' to quit.")

    # ------------------------------------------------------------------ #
    #  Main loop
    # ------------------------------------------------------------------ #
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[main] Failed to read frame. Exiting.")
                break

            # Mirror the frame for a natural experience
            frame = cv2.flip(frame, 1)

            # --- Detect hands ---
            hands = detector.detect(frame)

            gesture = "None"
            action_text = "Idle"

            if hands:
                hand = hands[0]  # Use primary hand

                # Draw landmarks
                detector.draw_landmarks(frame, hand)

                # Recognise gesture
                gesture = recognizer.recognize(hand.landmarks)

                # Execute action
                action_text = controller.execute(gesture, hand.landmarks)

            # --- FPS calculation ---
            curr_time = time.time()
            fps = 1.0 / max(curr_time - prev_time, 1e-6)
            prev_time = curr_time

            # --- Draw HUD ---
            overlay.draw_hud(
                frame,
                gesture=gesture,
                action_text=action_text,
                fps=fps,
                num_hands=len(hands),
                system_control=config.SYSTEM_CONTROL_ENABLED,
            )

            # --- Display ---
            cv2.imshow("Hand Gesture Control", frame)

            # --- Key handling ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('s') or key == ord('S'):
                config.SYSTEM_CONTROL_ENABLED = not config.SYSTEM_CONTROL_ENABLED
                state = "ON" if config.SYSTEM_CONTROL_ENABLED else "OFF"
                print(f"[main] System control toggled: {state}")
            elif key == ord('g') or key == ord('G'):
                overlay.show_guide = not overlay.show_guide

    except KeyboardInterrupt:
        print("\n[main] Interrupted by user.")

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    print("[main] Shutting down...")
    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[main] Done.")


if __name__ == "__main__":
    main()
