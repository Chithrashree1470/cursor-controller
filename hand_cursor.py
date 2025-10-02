import cv2
import mediapipe as mp
import pyautogui
import math
import time

# ------------------ AUTOMATIC CAMERA DETECTION ------------------
cap = None
for i in range(5):  # tries camera indexes 0 to 4
    temp_cap = cv2.VideoCapture(i)
    if temp_cap.isOpened():
        cap = temp_cap
        print(f"Camera opened at index {i}")
        break
    temp_cap.release()

if cap is None:
    print("No working camera found! Exiting...")
    exit()

screen_width, screen_height = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

click_down = False
drag_mode = False
prev_scroll_y = 0

# For smoothing cursor movement
prev_cursor_x, prev_cursor_y = 0, 0
smoothing = 5  # higher = smoother

# ------------------ LOOP ------------------
while True:
    success, img = cap.read()
    if not success:
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    h, w, _ = img.shape

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        lm = hand_landmarks.landmark

        # ---------------- FINGERTIP COORDS ----------------
        index = lm[8]
        thumb = lm[4]
        middle = lm[12]
        ring = lm[16]
        pinky = lm[20]

        # Map to screen coordinates
        ix, iy = int(index.x * screen_width), int(index.y * screen_height)
        # Smoothing cursor movement
        ix = prev_cursor_x + (ix - prev_cursor_x)//smoothing
        iy = prev_cursor_y + (iy - prev_cursor_y)//smoothing
        prev_cursor_x, prev_cursor_y = ix, iy

        pyautogui.moveTo(ix, iy)

        tx, ty = int(thumb.x * screen_width), int(thumb.y * screen_height)
        mx, my = int(middle.x * screen_width), int(middle.y * screen_height)

        # ---------------- DISTANCES ----------------
        distance_thumb_index = math.hypot(tx - ix, ty - iy)
        distance_thumb_middle = math.hypot(tx - mx, ty - my)

        # ---------------- LEFT CLICK ----------------
        if distance_thumb_index < 40:
            if not click_down:
                pyautogui.click()
                click_down = True
            cv2.putText(img, "LEFT CLICK", (30,50), cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        else:
            click_down = False

        # ---------------- RIGHT CLICK ----------------
        if distance_thumb_middle < 40:
            pyautogui.click(button='right')
            cv2.putText(img, "RIGHT CLICK", (30,100), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

        # ---------------- DRAG & DROP ----------------
        if distance_thumb_index < 40:
            if not drag_mode:
                pyautogui.mouseDown()
                drag_mode = True
            cv2.putText(img, "DRAG MODE", (30,150), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
        else:
            if drag_mode:
                pyautogui.mouseUp()
                drag_mode = False

        # ---------------- SCROLL ----------------
        scroll_y = int(index.y * screen_height)
        if prev_scroll_y != 0:
            if scroll_y - prev_scroll_y > 20:
                pyautogui.scroll(-50)
                cv2.putText(img,"SCROLL DOWN",(30,200),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
            elif prev_scroll_y - scroll_y > 20:
                pyautogui.scroll(50)
                cv2.putText(img,"SCROLL UP",(30,200),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
        prev_scroll_y = scroll_y

        # ---------------- FINGERS UP DETECTION ----------------
        fingers = []
        # Thumb
        if lm[4].x < lm[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
        # Other fingers
        for tip in [8,12,16,20]:
            if lm[tip].y < lm[tip-2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        # ---------------- COPY / CUT / PASTE / SELECT ALL ----------------
        if fingers == [0,1,1,0,0]:
            pyautogui.hotkey('ctrl','c')
            cv2.putText(img,"COPY",(30,250),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        elif fingers == [0,1,1,1,0]:
            pyautogui.hotkey('ctrl','x')
            cv2.putText(img,"CUT",(30,250),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        elif fingers == [0,1,1,1,1]:
            pyautogui.hotkey('ctrl','v')
            cv2.putText(img,"PASTE",(30,250),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
        elif fingers == [1,1,1,1,1]:
            pyautogui.hotkey('ctrl','a')
            cv2.putText(img,"SELECT ALL",(30,250),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)

        # ---------------- VISUAL FINGERTIPS ----------------
        fingertip_coords = [(index, (0,255,0)), (thumb,(0,0,255)), (middle,(255,0,0)),
                            (ring,(0,255,255)),(pinky,(255,0,255))]
        for f, color in fingertip_coords:
            cx, cy = int(f.x*w), int(f.y*h)
            cv2.circle(img,(cx,cy),10,color,-1)

        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # ---------------- SHOW IMAGE ----------------
    cv2.imshow("Hand Gesture Cursor", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
