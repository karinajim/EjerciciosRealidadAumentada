# cap15_reto_corregido.py
import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime

# ------------------------------------------------------------
# Crear accesorios virtuales (PNG con transparencia)
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

def crear_bigote():
    img = np.zeros((50, 120, 4), dtype=np.uint8)
    img[:, :, 3] = 0
    cv2.ellipse(img, (30, 25), (20, 10), 0, 0, 360, (0, 0, 0, 255), -1)
    cv2.ellipse(img, (90, 25), (20, 10), 0, 0, 360, (0, 0, 0, 255), -1)
    return img

gafas = crear_gafas()
sombrero = crear_sombrero()
bigote = crear_bigote()
accesorios = {"gafas": gafas, "sombrero": sombrero, "bigote": bigote}
accesorio_actual = "gafas"

# ------------------------------------------------------------
# Función para superponer imagen con alpha
# ------------------------------------------------------------
def superponer_imagen(fondo, overlay, x, y, w, h):
    if overlay is None or w <= 0 or h <= 0:
        return fondo
    overlay_redim = cv2.resize(overlay, (w, h))
    if overlay_redim.shape[2] == 4:
        alpha = overlay_redim[:, :, 3] / 255.0
        for c in range(3):
            fondo[y:y+h, x:x+w, c] = (
                fondo[y:y+h, x:x+w, c] * (1 - alpha) + overlay_redim[:, :, c] * alpha
            )
    return fondo

# ------------------------------------------------------------
# MediaPipe Face Mesh
# ------------------------------------------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ------------------------------------------------------------
# Captura de video
# ------------------------------------------------------------
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir ninguna cámara.")
        exit()

print("🛍️ Catálogo: 1-Gafas, 2-Sombrero, 3-Bigote, f-Foto, q-Salir")

while True:
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0:
        print("⚠️ Frame vacío, reintentando...")
        continue

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]

        # Puntos clave
        ojo_izq = (int(landmarks[33].x * w), int(landmarks[33].y * h))
        ojo_der = (int(landmarks[362].x * w), int(landmarks[362].y * h))
        frente = (int(landmarks[10].x * w), int(landmarks[10].y * h))
        nariz = (int(landmarks[1].x * w), int(landmarks[1].y * h))
        boca_izq = (int(landmarks[61].x * w), int(landmarks[61].y * h))
        boca_der = (int(landmarks[291].x * w), int(landmarks[291].y * h))

        if accesorio_actual == "gafas":
            centro_x = (ojo_izq[0] + ojo_der[0]) // 2
            centro_y = (ojo_izq[1] + ojo_der[1]) // 2
            ancho = int(abs(ojo_der[0] - ojo_izq[0]) * 2.5)
            alto = int(ancho * 0.4)
            x1, y1 = centro_x - ancho//2, centro_y - alto//2 - 15
            frame = superponer_imagen(frame, gafas, x1, y1, ancho, alto)

        elif accesorio_actual == "sombrero":
            ancho = int(abs(ojo_der[0] - ojo_izq[0]) * 2.0)
            alto = int(ancho * 0.75)
            x1, y1 = frente[0] - ancho//2, frente[1] - alto + 30
            frame = superponer_imagen(frame, sombrero, x1, y1, ancho, alto)

        elif accesorio_actual == "bigote":
            centro_x = nariz[0]
            centro_y = (nariz[1] + (boca_izq[1] + boca_der[1])//2) // 2
            ancho = int(abs(boca_der[0] - boca_izq[0]) * 1.2)
            alto = ancho // 2
            x1, y1 = centro_x - ancho//2, centro_y - alto//2
            frame = superponer_imagen(frame, bigote, x1, y1, ancho, alto)

    # Mostrar información
    cv2.putText(frame, f"Accesorio: {accesorio_actual}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow('Catalogo Virtual', frame)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'):
        break
    elif tecla == ord('1'):
        accesorio_actual = "gafas"
    elif tecla == ord('2'):
        accesorio_actual = "sombrero"
    elif tecla == ord('3'):
        accesorio_actual = "bigote"
    elif tecla == ord('f'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"probador_{accesorio_actual}_{timestamp}.png"
        cv2.imwrite(nombre, frame)
        print(f"📸 Foto guardada: {nombre}")

cap.release()
cv2.destroyAllWindows()