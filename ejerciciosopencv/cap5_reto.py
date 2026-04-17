# cap5_reto_corregido.py
import cv2
import numpy as np
import os
import urllib.request
import ssl

# Solución para problemas de certificado en algunas redes
ssl._create_default_https_context = ssl._create_unverified_context

# --- Configuración del modelo DNN ---
prototxt = "deploy.prototxt"
modelo = "res10_300x300_ssd_iter_140000.caffemodel"

# URLs oficiales actualizadas (OpenCV Zoo)
url_proto = "https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/deploy.prototxt"
url_model = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"

if not os.path.exists(prototxt) or not os.path.exists(modelo):
    print("Descargando modelo DNN...")
    try:
        urllib.request.urlretrieve(url_proto, prototxt)
        urllib.request.urlretrieve(url_model, modelo)
        print("Modelo descargado correctamente.")
        red_dnn = cv2.dnn.readNetFromCaffe(prototxt, modelo)
    except Exception as e:
        print(f"Error al descargar el modelo DNN: {e}")
        print("Se usará únicamente Haar Cascade (menor precisión).")
        red_dnn = None
else:
    red_dnn = cv2.dnn.readNetFromCaffe(prototxt, modelo)

# Cargar Haar Cascade como respaldo
haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- Cámara externa ---
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Cámara 1 no disponible, intentando cámara 0...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se encontró ninguna cámara.")
        exit()

# Parámetros de tracking
umbral_distancia = 60
limite_personas = 3

print("Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    centros_actuales = []
    h, w = frame.shape[:2]

    # --- Detección con DNN si está disponible ---
    if red_dnn is not None:
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
        red_dnn.setInput(blob)
        detecciones = red_dnn.forward()

        for i in range(detecciones.shape[2]):
            conf = detecciones[0, 0, i, 2]
            if conf > 0.5:
                box = detecciones[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                centros_actuales.append((cx, cy))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    else:
        # Fallback a Haar Cascade
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = haar_cascade.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w_rect, h_rect) in rostros:
            cx, cy = x + w_rect // 2, y + h_rect // 2
            centros_actuales.append((cx, cy))
            cv2.rectangle(frame, (x, y), (x + w_rect, y + h_rect), (0, 255, 0), 2)

    # --- Eliminar detecciones duplicadas ---
    personas_unicas = []
    for c in centros_actuales:
        duplicado = False
        for u in personas_unicas:
            if np.linalg.norm(np.array(c) - np.array(u)) < umbral_distancia:
                duplicado = True
                break
        if not duplicado:
            personas_unicas.append(c)

    # --- Alerta si se supera el límite ---
    if len(personas_unicas) >= limite_personas:
        cv2.putText(frame, f"¡ALERTA! {len(personas_unicas)} personas", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        print('\a', end='', flush=True)   # Beep en terminal

    # --- Termómetro visual ---
    barra_x, barra_y = 10, 80
    ancho_max, alto = 200, 20
    cv2.rectangle(frame, (barra_x, barra_y), (barra_x + ancho_max, barra_y + alto), (255, 255, 255), 2)
    llenado = min(len(personas_unicas) * (ancho_max // limite_personas), ancho_max)
    cv2.rectangle(frame, (barra_x, barra_y), (barra_x + llenado, barra_y + alto), (0, 0, 255), -1)

    cv2.putText(frame, f"Personas: {len(personas_unicas)}", (10, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('Contador de Personas', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()