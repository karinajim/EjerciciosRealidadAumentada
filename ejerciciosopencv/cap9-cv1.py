import cv2
import cv2.aruco as aruco
import numpy as np

# Cargar diccionario de marcadores 6x6 (250 posibles)
diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parametros = aruco.DetectorParameters()
detector = aruco.ArucoDetector(diccionario, parametros)

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print("Detectando marcadores ArUco. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detectar marcadores
    esquinas, ids, rechazados = detector.detectMarkers(frame)

    if ids is not None:
        # Dibujar marcadores detectados
        aruco.drawDetectedMarkers(frame, esquinas, ids)

        # Mostrar ID de cada marcador
        for i, esquina in enumerate(esquinas):
            centro_x = int(np.mean(esquina[0][:, 0]))
            centro_y = int(np.mean(esquina[0][:, 1]))
            cv2.putText(frame, f"ID: {ids[i][0]}", (centro_x - 20, centro_y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, f"Marcadores: {len(ids) if ids is not None else 0}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.imshow('Detector ArUco', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()