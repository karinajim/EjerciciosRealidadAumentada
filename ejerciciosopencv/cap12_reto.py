# cap12_reto.py - Cubo 3D con parámetros calibrados
import cv2
import cv2.aruco as aruco
import numpy as np
import os

# Cargar calibración
if os.path.exists('parametros_camara.npz'):
    datos = np.load('parametros_camara.npz')
    matriz_camara = datos['matriz_camara']
    dist_coefs = datos['dist_coefs']
    print("Usando parámetros calibrados")
else:
    print("No se encontró calibración. Usando aproximados.")
    matriz_camara = np.array([[1000, 0, 640], [0, 1000, 360], [0, 0, 1]], dtype=np.float32)
    dist_coefs = np.zeros((4, 1))

tamanio_marcador = 0.05
lado_cubo = 0.03
cubo_3d = np.float32([
    [-lado_cubo/2, -lado_cubo/2, 0], [ lado_cubo/2, -lado_cubo/2, 0],
    [ lado_cubo/2,  lado_cubo/2, 0], [-lado_cubo/2,  lado_cubo/2, 0],
    [-lado_cubo/2, -lado_cubo/2, lado_cubo], [ lado_cubo/2, -lado_cubo/2, lado_cubo],
    [ lado_cubo/2,  lado_cubo/2, lado_cubo], [-lado_cubo/2,  lado_cubo/2, lado_cubo]
])

def dibujar_cubo(img, imgpts):
    imgpts = np.int32(imgpts).reshape(-1,2)
    for i,j in zip([0,1,2,3],[1,2,3,0]): cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (0,255,0), 3)
    for i,j in zip([0,1,2,3],[4,5,6,7]): cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255,0,0), 3)
    for i,j in zip([4,5,6,7],[5,6,7,4]): cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (0,0,255), 3)

diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
detector = aruco.ArucoDetector(diccionario, aruco.DetectorParameters())
cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    esquinas, ids, _ = detector.detectMarkers(frame)
    if ids is not None:
        aruco.drawDetectedMarkers(frame, esquinas, ids)
        for i in range(len(ids)):
            obj_points = np.array([
                [-tamanio_marcador/2,  tamanio_marcador/2, 0],
                [ tamanio_marcador/2,  tamanio_marcador/2, 0],
                [ tamanio_marcador/2, -tamanio_marcador/2, 0],
                [-tamanio_marcador/2, -tamanio_marcador/2, 0]], dtype=np.float32)
            success, rvec, tvec = cv2.solvePnP(obj_points, esquinas[i][0], matriz_camara, dist_coefs)
            if success:
                imgpts, _ = cv2.projectPoints(cubo_3d, rvec, tvec, matriz_camara, dist_coefs)
                dibujar_cubo(frame, imgpts)
                cv2.drawFrameAxes(frame, matriz_camara, dist_coefs, rvec, tvec, 0.03)
    cv2.imshow('Cubo Calibrado', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
cap.release()
cv2.destroyAllWindows()