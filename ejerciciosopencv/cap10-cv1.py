import cv2
import cv2.aruco as aruco
import numpy as np
import os

def crear_imagen_prueba():
    """Crea una imagen PNG con transparencia (logo AR)"""
    img = np.zeros((200, 200, 4), dtype=np.uint8)
    # Fondo transparente
    img[:, :, 3] = 0
    # Círculo verde
    cv2.circle(img, (100, 100), 80, (0, 255, 0, 200), -1)
    # Texto AR
    cv2.putText(img, "AR", (60, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255, 255), 3)
    return img

def superponer_imagen(frame, img_overlay, esquinas_destino):
    """Superpone una imagen (con alpha) sobre las esquinas del marcador"""
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

# Cargar o crear imagen AR
if not os.path.exists("logo_ar.png"):
    img_ar = crear_imagen_prueba()
    cv2.imwrite("logo_ar.png", img_ar)
else:
    img_ar = cv2.imread("logo_ar.png", cv2.IMREAD_UNCHANGED)

# Detector ArUco
diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print("Superposición AR. Muestra un marcador. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret: break

    esquinas, ids, _ = detector.detectMarkers(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, esquinas, ids)
        for esquina in esquinas:
            frame = superponer_imagen(frame, img_ar, esquina[0])

    cv2.imshow('Superposición AR', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()