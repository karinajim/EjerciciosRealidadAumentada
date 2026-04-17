# cap11_reto.py - Iniciales 3D con rotación y color por distancia
import cv2
import cv2.aruco as aruco
import numpy as np
import math

# ------------------------------------------------------------
# Parámetros de cámara (aproximados, luego usarás los calibrados)
# ------------------------------------------------------------
matriz_camara = np.array([[1000, 0, 640],
                          [0, 1000, 360],
                          [0, 0, 1]], dtype=np.float32)
dist_coefs = np.zeros((4, 1))
tamanio_marcador = 0.05  # 5 cm

# ------------------------------------------------------------
# Definir segmentos 3D para las letras "A" y "R"
# ------------------------------------------------------------
segmentos_3d = []

# Letra A (coordenadas normalizadas alrededor del origen)
A = [
    ([-0.02, -0.02, 0.01], [ 0.00,  0.03, 0.01]),  # / izquierda
    ([ 0.02, -0.02, 0.01], [ 0.00,  0.03, 0.01]),  # \ derecha
    ([-0.01,  0.00, 0.01], [ 0.01,  0.00, 0.01])   # - medio
]

# Letra R
R = [
    ([ 0.03, -0.02, 0.01], [ 0.03,  0.03, 0.01]),  # | vertical
    ([ 0.03,  0.03, 0.01], [ 0.05,  0.03, 0.01]),  # - superior
    ([ 0.05,  0.03, 0.01], [ 0.05,  0.00, 0.01]),  # | bajada
    ([ 0.05,  0.00, 0.01], [ 0.03,  0.00, 0.01]),  # - medio
    ([ 0.04,  0.00, 0.01], [ 0.05, -0.02, 0.01])   # \ pierna
]

segmentos_3d = A + R

# ------------------------------------------------------------
# Detector ArUco
# ------------------------------------------------------------
diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

angulo_rot = 0  # grados

print("🎨 Reto Capítulo 11 - Iniciales AR 3D")
print("Muestra un marcador ArUco. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    esquinas, ids, _ = detector.detectMarkers(frame)

    if ids is not None:
        aruco.drawDetectedMarkers(frame, esquinas, ids)

        for i in range(len(ids)):
            # Esquinas 3D del marcador
            obj_points = np.array([
                [-tamanio_marcador/2,  tamanio_marcador/2, 0],
                [ tamanio_marcador/2,  tamanio_marcador/2, 0],
                [ tamanio_marcador/2, -tamanio_marcador/2, 0],
                [-tamanio_marcador/2, -tamanio_marcador/2, 0]
            ], dtype=np.float32)

            success, rvec, tvec = cv2.solvePnP(
                obj_points, esquinas[i][0], matriz_camara, dist_coefs
            )

            if success:
                # Distancia a la cámara (norma del vector de traslación)
                distancia = np.linalg.norm(tvec)

                # Color dependiente de la distancia (rojo cerca, azul lejos)
                # Mapeo simple: cerca -> rojo (0,0,255), lejos -> azul (255,0,0)
                intensidad = min(1.0, distancia / 0.5)  # 0.5 m como referencia
                color = (
                    int(255 * intensidad),        # Azul
                    0,                            # Verde
                    int(255 * (1 - intensidad))   # Rojo
                )

                # Rotación automática alrededor del eje Y
                angulo_rot = (angulo_rot + 2) % 360
                R_extra, _ = cv2.Rodrigues(np.array([0, math.radians(angulo_rot), 0]))

                # Proyectar y dibujar cada segmento
                for (p1, p2) in segmentos_3d:
                    # Aplicar rotación extra a los puntos
                    p1_rot = np.dot(R_extra, np.array(p1))
                    p2_rot = np.dot(R_extra, np.array(p2))

                    # Proyectar puntos 3D a 2D
                    pts_3d = np.float32([p1_rot, p2_rot]).reshape(-1, 3)
                    pts_2d, _ = cv2.projectPoints(pts_3d, rvec, tvec, matriz_camara, dist_coefs)
                    pts_2d = pts_2d.reshape(-1, 2).astype(int)

                    # Dibujar línea
                    cv2.line(frame, tuple(pts_2d[0]), tuple(pts_2d[1]), color, 3)

                # Mostrar distancia en pantalla
                cv2.putText(frame, f"Distancia: {distancia:.2f} m", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # Dibujar ejes del marcador
                cv2.drawFrameAxes(frame, matriz_camara, dist_coefs, rvec, tvec, 0.03)

    cv2.imshow('Iniciales AR 3D', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()