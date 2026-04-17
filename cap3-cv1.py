import cv2
import numpy as np

print("📸 Probando cámara después del reset...")

# Intentar abrir con DSHOW
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if cap.isOpened():
    print("✅ Cámara abierta con DSHOW")
    
    # Configurar
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Leer frame
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame capturado: {frame.shape}")
        cv2.imshow('Prueba - Presiona cualquier tecla', frame)
        cv2.waitKey(0)
    else:
        print("❌ No se pudo leer frame")
    
    cap.release()
else:
    print("❌ No se pudo abrir con DSHOW")

cv2.destroyAllWindows()