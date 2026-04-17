# cap14_reto.py - Libro AR básico
import cv2
import cv2.aruco as aruco
import numpy as np

# ------------------------------------------------------------
# Páginas del libro (asociadas a IDs de marcadores)
# ------------------------------------------------------------
paginas = {
    0: {"titulo": "Portada", "descripcion": "Bienvenido al Libro AR"},
    1: {"titulo": "Animales", "descripcion": "El leon es el rey de la selva"},
    2: {"titulo": "Vehiculos", "descripcion": "Los coches electricos son el futuro"},
    3: {"titulo": "Naturaleza", "descripcion": "Los arboles producen oxigeno"}
}

diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print("📖 Libro AR. Muestra marcadores 0-3. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret: break

    esquinas, ids, _ = detector.detectMarkers(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, esquinas, ids)
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id in paginas:
                pts = esquinas[i][0].astype(np.int32)
                # Dibujar un rectángulo decorativo alrededor del marcador
                cv2.polylines(frame, [pts], True, (255, 215, 0), 3)
                # Mostrar título y descripción cerca del marcador
                x, y = pts[0][0], pts[0][1] - 50
                info = paginas[marker_id]
                cv2.putText(frame, info["titulo"], (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, info["descripcion"], (x, y + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Libro AR', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()