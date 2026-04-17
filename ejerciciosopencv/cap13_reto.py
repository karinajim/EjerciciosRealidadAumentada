# cap13_reto.py
import cv2
import mediapipe as mp
import numpy as np

def calcular_ear(landmarks, indices, w, h):
    puntos = []
    for idx in indices:
        x = int(landmarks[idx].x * w)
        y = int(landmarks[idx].y * h)
        puntos.append((x, y))
    p1,p2,p3,p4,p5,p6 = puntos[0], puntos[1], puntos[2], puntos[3], puntos[4], puntos[5]
    ear = (np.linalg.norm(np.array(p2)-np.array(p6)) + np.linalg.norm(np.array(p3)-np.array(p5))) / \
          (2.0 * np.linalg.norm(np.array(p1)-np.array(p4)))
    return ear, puntos

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                  min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

# Índices de los ojos
ojo_izq = [33, 133, 157, 158, 159, 160, 161, 173]
ojo_der = [362, 263, 387, 388, 389, 390, 391, 398]
contador = 0
umbral = 0.22
parpadeo_activo = False

while True:
    ret, frame = cap.read()
    if not ret: break
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        ear_izq, pts_izq = calcular_ear(landmarks, ojo_izq, w, h)
        ear_der, pts_der = calcular_ear(landmarks, ojo_der, w, h)
        ear = (ear_izq + ear_der) / 2.0
        if ear < umbral and not parpadeo_activo:
            contador += 1
            parpadeo_activo = True
        elif ear >= umbral:
            parpadeo_activo = False
        for p in pts_izq + pts_der:
            cv2.circle(frame, p, 2, (0,255,255), -1)
        cv2.putText(frame, f"EAR: {ear:.2f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        cv2.putText(frame, f"Parpadeos: {contador}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        mp_drawing.draw_landmarks(frame, results.multi_face_landmarks[0], mp_face_mesh.FACEMESH_CONTOURS,
                                  landmark_drawing_spec=None,
                                  connection_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0), thickness=1))
    cv2.imshow('Detector de Parpadeo', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()