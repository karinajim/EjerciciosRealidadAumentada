import cv2
import cv2.aruco as aruco
import numpy as np
import time

# Configurar detector
diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parametros = aruco.DetectorParameters()
detector = aruco.ArucoDetector(diccionario, parametros)

# ID de TU marcador (cámbialo por el que imprimiste)
MI_ID = 5

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print(f"Buscando marcador con ID {MI_ID}. Presiona 'q' para salir.")
ultimo_tiempo_detectado = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    esquinas, ids, _ = detector.detectMarkers(frame)
    mi_marcador_detectado = False

    if ids is not None:
        for i, esquina in enumerate(esquinas):
            marker_id = ids[i][0]
            color = (0, 0, 255)  # rojo por defecto

            if marker_id == MI_ID:
                mi_marcador_detectado = True
                color = (0, 255, 0)  # verde para el tuyo
                # Efecto visual: borde más grueso
                pts = esquina[0].astype(np.int32)
                cv2.polylines(frame, [pts], True, color, 4)
                # Mensaje personalizado
                cx, cy = int(np.mean(pts[:, 0])), int(np.mean(pts[:, 1]))
                cv2.putText(frame, "¡MI MARCADOR!", (cx - 60, cy - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                # Guardar foto al detectarlo (solo una vez por segundo para no saturar)
                ahora = time.time()
                if ahora - ultimo_tiempo_detectado > 1.0:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"mi_marcador_{timestamp}.png", frame)
                    print(f"📸 Foto guardada: mi_marcador_{timestamp}.png")
                    ultimo_tiempo_detectado = ahora
            else:
                # Dibujar marcadores normales
                aruco.drawDetectedMarkers(frame, [esquina], np.array([[marker_id]]))

            # Mostrar ID
            centro = np.mean(esquina[0], axis=0).astype(int)
            cv2.putText(frame, f"ID:{marker_id}", (centro[0]-15, centro[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow('Mi Marcador Personal', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()