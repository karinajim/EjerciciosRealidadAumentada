# cap15_ejercicio.py - Probador virtual de gafas y sombrero
import cv2
import mediapipe as mp
import numpy as np

# ------------------------------------------------------------
# Crear accesorios virtuales (PNG con alpha)
# ------------------------------------------------------------
def crear_gafas():
    img = np.zeros((100, 200, 4), dtype=np.uint8)
    img[:, :, 3] = 0
    cv2.rectangle(img, (30, 40), (80, 70), (0, 0, 0, 200), -1)
    cv2.rectangle(img, (120, 40), (170, 70), (0, 0, 0, 200), -1)
    cv2.rectangle(img, (80, 50), (120, 60), (0, 0, 0, 255), -1)
    return img

def crear_sombrero():
    img = np.zeros((150, 200, 4), dtype=np.uint8)
    img[:, :, 3] = 0
    cv2.rectangle(img, (70, 20), (130, 80), (139, 69, 19, 255), -1)
    cv2.ellipse(img, (100, 80), (70, 20), 0, 0, 360, (139, 69, 19, 255), -1)
    return img

gafas = crear_gafas()
sombrero = crear_sombrero()
accesorio_actual = "gafas"  # Cambia con teclas 1 y 2

# ------------------------------------------------------------
# MediaPipe Face Mesh
# ------------------------------------------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
                                  refine_landmarks=True, min_detection_confidence=0.5)

def superponer(frame, overlay, x, y, w, h):
    if overlay is None: return frame
    overlay = cv2.resize(overlay, (w, h))
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            frame[y:y+h, x:x+w, c] = frame[y:y+h, x:x+w, c] * (1 - alpha) + overlay[:, :, c] * alpha
    return frame

cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

print("👓 Probador virtual. Teclas: 1-Gafas, 2-Sombrero, q-Salir")

while True:
    ret, frame = cap.read()
    if not ret: break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]

        # Obtener puntos clave
        ojo_izq = (int(landmarks[33].x * w), int(landmarks[33].y * h))
        ojo_der = (int(landmarks[362].x * w), int(landmarks[362].y * h))
        frente = (int(landmarks[10].x * w), int(landmarks[10].y * h))

        if accesorio_actual == "gafas":
            centro_x = (ojo_izq[0] + ojo_der[0]) // 2
            centro_y = (ojo_izq[1] + ojo_der[1]) // 2
            ancho = int(abs(ojo_der[0] - ojo_izq[0]) * 2.5)
            alto = int(ancho * 0.4)
            x1 = centro_x - ancho // 2
            y1 = centro_y - alto // 2 - 15
            frame = superponer(frame, gafas, x1, y1, ancho, alto)

        elif accesorio_actual == "sombrero":
            ancho = int(abs(ojo_der[0] - ojo_izq[0]) * 2.0)
            alto = int(ancho * 0.75)
            x1 = frente[0] - ancho // 2
            y1 = frente[1] - alto + 30
            frame = superponer(frame, sombrero, x1, y1, ancho, alto)

    cv2.putText(frame, f"Accesorio: {accesorio_actual}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow('Probador Virtual', frame)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'): break
    elif tecla == ord('1'): accesorio_actual = "gafas"
    elif tecla == ord('2'): accesorio_actual = "sombrero"

cap.release()
cv2.destroyAllWindows()