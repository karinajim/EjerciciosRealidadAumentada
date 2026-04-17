import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

lienzo = None
ultima_pos = None
color = (0, 255, 0)
grosor = 5

while True:
    ret, frame = cap.read()
    if not ret: break
    if lienzo is None: lienzo = np.zeros_like(frame)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        h, w = frame.shape[:2]
        x = int(hand.landmark[8].x * w)
        y = int(hand.landmark[8].y * h)
        indice_ext = hand.landmark[8].y < hand.landmark[6].y
        medio_ext = hand.landmark[12].y < hand.landmark[10].y
        if indice_ext and not medio_ext:
            if ultima_pos:
                cv2.line(lienzo, ultima_pos, (x,y), color, grosor)
            cv2.circle(lienzo, (x,y), grosor//2, color, -1)
            ultima_pos = (x,y)
        elif indice_ext and medio_ext:
            if ultima_pos:
                cv2.line(lienzo, ultima_pos, (x,y), (0,0,0), grosor*2)
            cv2.circle(lienzo, (x,y), grosor, (0,0,0), -1)
            ultima_pos = (x,y)
        else:
            ultima_pos = None
        mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
    else:
        ultima_pos = None
    res = cv2.addWeighted(frame, 0.7, lienzo, 0.3, 0)
    cv2.imshow('Pintura con Dedos', res)
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'): break
    elif tecla == ord('c'): lienzo = np.zeros_like(frame)
    elif tecla == ord('1'): color = (0,255,0)
    elif tecla == ord('2'): color = (0,0,255)
    elif tecla == ord('3'): color = (255,0,0)

cap.release()
cv2.destroyAllWindows()