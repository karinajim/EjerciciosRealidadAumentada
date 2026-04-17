# generar_marcadores.py
import cv2
import cv2.aruco as aruco

diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

for i in range(5):
    marcador = aruco.generateImageMarker(diccionario, i, 400)
    # Añadir borde blanco para mejor detección
    marcador = cv2.copyMakeBorder(marcador, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)
    nombre = f"marcador_{i}.png"
    cv2.imwrite(nombre, marcador)
    print(f"✅ Marcador {i} guardado como {nombre}")