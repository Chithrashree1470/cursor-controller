#############################################
# Virtual Mouse with Dual-Hand Gesture Control
#############################################

import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import autopy
import time
import math
import os
from pathlib import Path

# -------------------- Main Function --------------------
def start():

    # -------------------- Configuration --------------------
    WEBCAM_WIDTH, WEBCAM_HEIGHT = 640, 480
    SMOOTHENING = 5
    FRAME_REDUCTION = 100
    STOP_HOLD_TIME = 2.0
    CLICK_COOLDOWN = 0.5
    PASTE_COOLDOWN = 8.0
    SCROLL_COOLDOWN = 0.25

    # -------------------- Initialize --------------------
    cap = cv2.VideoCapture(0)
    cap.set(3, WEBCAM_WIDTH)
    cap.set(4, WEBCAM_HEIGHT)
    screen_width, screen_height = autopy.screen.size()

    screenshot_dir = Path.home() / "Pictures" / "GestureScreenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    p_loc_x, p_loc_y = 0, 0
    c_loc_x, c_loc_y = 0, 0
    last_action_time = 0
    last_paste_time = 0
    last_scroll_time = 0
    stop_gesture_start_time = None

    # -------------------- Mediapipe Detector --------------------
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # -------------------- Helper Functions --------------------
    def fingers_up(hand_label, lm):
        tip_ids = [4, 8, 12, 16, 20]
        fingers = []
        if hand_label == "Right":
            fingers.append(1 if lm[tip_ids[0]][1] < lm[tip_ids[0] - 1][1] else 0)
        else:
            fingers.append(1 if lm[tip_ids[0]][1] > lm[tip_ids[0] - 1][1] else 0)
        for id in range(1, 5):
            fingers.append(1 if lm[tip_ids[id]][2] < lm[tip_ids[id] - 2][2] else 0)
        return fingers

    def find_distance(p1, p2, lm):
        return math.hypot(lm[p2][1] - lm[p1][1], lm[p2][2] - lm[p1][2])

    # -------------------- Main Loop --------------------
    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        current_time = time.time()

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_no, hand_label_data in enumerate(results.multi_handedness):
                hand_label = hand_label_data.classification[0].label
                lm_list = []
                for id, lm in enumerate(results.multi_hand_landmarks[hand_no].landmark):
                    h, w, c = img.shape
                    lm_list.append([id, int(lm.x * w), int(lm.y * h)])
                mp_draw.draw_landmarks(img, results.multi_hand_landmarks[hand_no], mp_hands.HAND_CONNECTIONS)

                fingers = fingers_up(hand_label, lm_list)

                # RIGHT HAND — MOUSE CONTROL
                if hand_label == "Right":
                    can_act = (current_time - last_action_time) > CLICK_COOLDOWN

                    # Move pointer
                    if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0:
                        x1, y1 = lm_list[8][1:]
                        x3 = np.interp(x1, (FRAME_REDUCTION, WEBCAM_WIDTH - FRAME_REDUCTION), (0, screen_width))
                        y3 = np.interp(y1, (FRAME_REDUCTION, WEBCAM_HEIGHT - FRAME_REDUCTION), (0, screen_height))
                        c_loc_x = p_loc_x + (x3 - p_loc_x) / SMOOTHENING
                        c_loc_y = p_loc_y + (y3 - p_loc_y) / SMOOTHENING
                        autopy.mouse.move(c_loc_x, c_loc_y)
                        p_loc_x, p_loc_y = c_loc_x, c_loc_y

                    # Left Click
                    elif fingers[0:3] == [1, 0, 1] and can_act:
                        pyautogui.click()
                        last_action_time = current_time

                    # Right Click
                    elif fingers[0:3] == [1, 1, 0] and can_act:
                        pyautogui.rightClick()
                        last_action_time = current_time

                    # Double Click
                    elif fingers[0:3] == [1, 0, 0] and can_act:
                        pyautogui.doubleClick()
                        last_action_time = current_time

                    # Scroll Up
                    elif fingers == [0, 1, 0, 0, 0] and (current_time - last_scroll_time > SCROLL_COOLDOWN):
                        pyautogui.scroll(150)
                        last_scroll_time = current_time

                    # Scroll Down
                    elif fingers == [0, 1, 0, 0, 1] and (current_time - last_scroll_time > SCROLL_COOLDOWN):
                        pyautogui.scroll(-150)
                        last_scroll_time = current_time

                # LEFT HAND — COPY/PASTE/STOP
                elif hand_label == "Left":
                    dist_scr = find_distance(4, 12, lm_list)

                    if dist_scr < 30:
                        filepath = screenshot_dir / f"screenshot_{time.time()}.png"
                        pyautogui.screenshot(str(filepath))

                    elif fingers == [1, 1, 1, 0, 0]:
                        pyautogui.hotkey('ctrl', 'a')

                    elif fingers == [1, 1, 1, 1, 0]:
                        pyautogui.hotkey('ctrl', 'c')

                    elif fingers == [1, 0, 0, 0, 0]:
                        pyautogui.hotkey('ctrl', 'v')

                    elif fingers == [0, 0, 0, 0, 0]:
                        if stop_gesture_start_time is None:
                            stop_gesture_start_time = time.time()
                        elapsed = time.time() - stop_gesture_start_time
                        if elapsed >= STOP_HOLD_TIME:
                            cap.release()
                            cv2.destroyAllWindows()
                            return  # exits start()

                else:
                    stop_gesture_start_time = None

        cv2.imshow("Gesture Virtual Mouse", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# -------------------- Entry Point --------------------
if __name__ == "__main__":
    start()
