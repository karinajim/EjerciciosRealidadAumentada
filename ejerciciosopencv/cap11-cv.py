import cv2
import cv2.aruco as aruco
import numpy as np

def dibujar_cubo(img, esquinas, imgpts):
    """Dibuja las aristas del cubo proyectado"""
    imgpts = np.int32(imgpts).reshape(-1, 2)
    # Base (z=0) - verde
    for i, j in zip([0,1,2,3], [1,2,3,0]):
        cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (0,255,0), 3)
    # Verticales - azul
    for i, j in zip([0,1,2,3], [4,5,6,7]):
        cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255,0,0), 3)
    # Tapa (z=l) - rojo
    for i, j in zip([4,5,6,7], [5,6,7,4]):
        cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (0,0,255), 3)
    return img

# Parámetros de cámara aproximados (sin calibrar)
matriz_camara = np.array([[1000, 0, 640],
                          [0, 1000, 360],
                          [0, 0, 1]], dtype=np.float32)
dist_coefs = np.zeros((4, 1))

tamanio_marcador = 0.05  # 5 cm
lado_cubo = 0.03          # 3 cm

# Vértices del cubo en 3D (centrado en origen del marcador)
cubo_3d = np.float32([
    [-lado_cubo/2, -lado_cubo/2, 0], [ lado_cubo/2, -lado_cubo/2, 0],
    [ lado_cubo/2,  lado_cubo/2, 0], [-lado_cubo/2,  lado_cubo/2, 0],  # Base
    [-lado_cubo/2, -lado_cubo/2, lado_cubo], [ lado_cubo/2, -lado_cubo/2, lado_cubo],
    [ lado_cubo/2,  lado_cubo/2, lado_cubo], [-lado_cubo/2,  lado_cubo/2, lado_cubo]   # Tapa
])

# Detector ArUco
diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    esquinas, ids, _ = detector.detectMarkers(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, esquinas, ids)
        for i in range(len(ids)):
            # Puntos 3D del marcador (esquinas en su sistema)
            obj_points = np.array([
                [-tamanio_marcador/2,  tamanio_marcador/2, 0],
                [ tamanio_marcador/2,  tamanio_marcador/2, 0],
                [ tamanio_marcador/2, -tamanio_marcador/2, 0],
                [-tamanio_marcador/2, -tamanio_marcador/2, 0]
            ], dtype=np.float32)

            success, rvec, tvec = cv2.solvePnP(obj_points, esquinas[i][0], matriz_camara, dist_coefs)
            if success:
                # Proyectar cubo 3D a 2D
                imgpts, _ = cv2.projectPoints(cubo_3d, rvec, tvec, matriz_camara, dist_coefs)
                frame = dibujar_cubo(frame, esquinas[i][0], imgpts)
                cv2.drawFrameAxes(frame, matriz_camara, dist_coefs, rvec, tvec, 0.03)

    cv2.imshow('Cubo 3D AR', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()