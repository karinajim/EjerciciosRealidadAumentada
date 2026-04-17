# cap5_ejercicio_corregido.py
import cv2
import numpy as np
import time
import os
import urllib.request
import ssl

# Desactivar verificación SSL para descarga (solución temporal)
ssl._create_default_https_context = ssl._create_unverified_context

# Cargar Haar Cascade
haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Intentar cargar modelo DNN
prototxt = "deploy.prototxt"
modelo = "res10_300x300_ssd_iter_140000.caffemodel"

if not os.path.exists(prototxt) or not os.path.exists(modelo):
    print("Descargando modelo DNN (puede tardar unos segundos)...")
    url_proto = "https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/deploy.prototxt"
    url_model = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
    try:
        urllib.request.urlretrieve(url_proto, prototxt)
        urllib.request.urlretrieve(url_model, modelo)
        print("Modelo descargado correctamente.")
    except Exception as e:
        print(f"Error al descargar el modelo DNN: {e}")
        print("Se usará solo Haar Cascade.")
        red_dnn = None
else:
    red_dnn = cv2.dnn.readNetFromCaffe(prototxt, modelo) if os.path.exists(prototxt) else None

cap = cv2.VideoCapture(1)  # Cámara externa

if not cap.isOpened():
    print("No se pudo abrir la cámara. Probando índice 0...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se encontró ninguna cámara.")
        exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_haar = frame.copy()
    frame_dnn = frame.copy() if red_dnn is not None else None
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- HAAR ---
    inicio = time.time()
    rostros_haar = haar_cascade.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in rostros_haar:
        cv2.rectangle(frame_haar, (x, y), (x+w, y+h), (255, 0, 0), 2)
    fps_haar = 1.0 / (time.time() - inicio + 1e-6)

    # --- DNN (si está disponible) ---
    if red_dnn is not None:
        inicio = time.time()
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
        red_dnn.setInput(blob)
        detecciones = red_dnn.forward()
        h, w = frame.shape[:2]
        for i in range(detecciones.shape[2]):
            conf = detecciones[0, 0, i, 2]
            if conf > 0.5:
                box = detecciones[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                cv2.rectangle(frame_dnn, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame_dnn, f"{conf:.2f}", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        fps_dnn = 1.0 / (time.time() - inicio + 1e-6)
    else:
        fps_dnn = 0

    # Mostrar FPS
    cv2.putText(frame_haar, f"Haar FPS: {fps_haar:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow('Haar Cascade', frame_haar)

    if red_dnn is not None:
        cv2.putText(frame_dnn, f"DNN FPS: {fps_dnn:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('DNN', frame_dnn)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()