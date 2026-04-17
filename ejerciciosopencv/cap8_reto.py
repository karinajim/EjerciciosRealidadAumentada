import cv2
import mediapipe as mp
import numpy as np
import time

def calcular_angulo(a,b,c):
    a,b,c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cos_ang = np.dot(ba, bc) / (np.linalg.norm(ba)*np.linalg.norm(bc)+1e-6)
    return np.degrees(np.arccos(np.clip(cos_ang, -1.0, 1.0)))

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

mala_postura_inicio = None
umbral_mala_postura = 160
alerta_activa = False

while True:
    ret, frame = cap.read()
    if not ret: break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        h,w = frame.shape[:2]
        landmarks = results.pose_landmarks.landmark
        hombro = (int(landmarks[11].x*w), int(landmarks[11].y*h))
        cadera = (int(landmarks[23].x*w), int(landmarks[23].y*h))
        rodilla = (int(landmarks[25].x*w), int(landmarks[25].y*h))
        angulo = calcular_angulo(hombro, cadera, rodilla)
        tiempo_actual = time.time()
        if angulo < umbral_mala_postura:
            if mala_postura_inicio is None:
                mala_postura_inicio = tiempo_actual
            elif tiempo_actual - mala_postura_inicio > 5:
                alerta_activa = True
        else:
            mala_postura_inicio = None
            alerta_activa = False
        cv2.circle(frame, hombro, 5, (255,0,0), -1)
        cv2.circle(frame, cadera, 5, (0,255,0), -1)
        cv2.circle(frame, rodilla, 5, (0,0,255), -1)
        cv2.line(frame, hombro, cadera, (255,255,0), 2)
        cv2.line(frame, cadera, rodilla, (255,255,0), 2)
        color = (0,0,255) if angulo < umbral_mala_postura else (0,255,0)
        cv2.putText(frame, f"Angulo: {angulo:.1f}", (10,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        if alerta_activa:
            cv2.putText(frame, "¡SIENTATE DERECHO!", (10,100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
        elif mala_postura_inicio:
            restante = 5 - (tiempo_actual - mala_postura_inicio)
            cv2.putText(frame, f"Enderezate en {restante:.1f}s", (10,100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    cv2.imshow('Detector de Postura', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()