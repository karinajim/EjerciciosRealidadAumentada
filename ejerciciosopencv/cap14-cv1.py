# cap14_ejercicio.py - Sistema multi-marcador
import cv2
import cv2.aruco as aruco
import numpy as np
import os

# ------------------------------------------------------------
# Base de datos de contenido por ID
# ------------------------------------------------------------
base_datos = {
    0: {"tipo": "texto", "contenido": "ID 0 - Texto AR", "color": (0, 255, 0)},
    1: {"tipo": "imagen", "contenido": "logo_ar.png"},
    2: {"tipo": "video", "contenido": "video.mp4", "loop": True}
}

# ------------------------------------------------------------
# Funciones de utilidad
# ------------------------------------------------------------
def crear_imagen_prueba():
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    img[:, :, 3] = 0
    cv2.circle(img, (100, 100), 80, (0, 255, 0, 200), -1)
    cv2.putText(img, "AR", (60, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255, 255), 3)
    return img

def superponer_imagen(frame, img_overlay, esquinas_destino):
    h_img, w_img = img_overlay.shape[:2]
    pts_origen = np.array([[0, 0], [w_img-1, 0], [w_img-1, h_img-1], [0, h_img-1]], dtype=np.float32)
    H, _ = cv2.findHomography(pts_origen, esquinas_destino.astype(np.float32))
    img_warped = cv2.warpPerspective(img_overlay, H, (frame.shape[1], frame.shape[0]))
    if img_overlay.shape[2] == 4:
        mascara = img_warped[:, :, 3] / 255.0
        for c in range(3):
            frame[:, :, c] = frame[:, :, c] * (1 - mascara) + img_warped[:, :, c] * mascara
    else:
        cv2.fillConvexPoly(frame, esquinas_destino.astype(np.int32), (0, 255, 0))
    return frame

# ------------------------------------------------------------
# Cargar recursos
# ------------------------------------------------------------
if not os.path.exists("logo_ar.png"):
    img_ar = crear_imagen_prueba()
    cv2.imwrite("logo_ar.png", img_ar)
else:
    img_ar = cv2.imread("logo_ar.png", cv2.IMREAD_UNCHANGED)

video_cap = None
if os.path.exists("video.mp4"):
    video_cap = cv2.VideoCapture("video.mp4")

# ------------------------------------------------------------
# Detector ArUco
# ------------------------------------------------------------
diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print("📦 Sistema multi-marcador. Muestra IDs 0,1,2. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret: break

    esquinas, ids, _ = detector.detectMarkers(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, esquinas, ids)
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id in base_datos:
                info = base_datos[marker_id]
                pts = esquinas[i][0]

                if info["tipo"] == "texto":
                    centro = np.mean(pts, axis=0).astype(int)
                    cv2.putText(frame, info["contenido"], (centro[0]-50, centro[1]),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, info["color"], 2)

                elif info["tipo"] == "imagen":
                    frame = superponer_imagen(frame, img_ar, pts)

                elif info["tipo"] == "video" and video_cap is not None:
                    ret_vid, frame_vid = video_cap.read()
                    if not ret_vid and info.get("loop", False):
                        video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret_vid, frame_vid = video_cap.read()
                    if ret_vid:
                        frame = superponer_imagen(frame, frame_vid, pts)

    cv2.imshow('Sistema Multi-Marcador', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
if video_cap: video_cap.release()
cv2.destroyAllWindows()