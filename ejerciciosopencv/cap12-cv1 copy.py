# capturar_calibracion.py
import cv2
import os

os.makedirs("calibracion", exist_ok=True)
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

patron = (8, 5)  # 8x5 esquinas internas para tablero 9x6
criterios = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
contador = 0

print("📸 Mueve el tablero. Presiona 'c' para capturar, 'q' para terminar.")

while True:
    ret, frame = cap.read()
    if not ret: break
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret_encontrado, esquinas = cv2.findChessboardCorners(gris, patron, None)
    if ret_encontrado:
        esquinas_subpix = cv2.cornerSubPix(gris, esquinas, (11,11), (-1,-1), criterios)
        cv2.drawChessboardCorners(frame, patron, esquinas_subpix, ret_encontrado)
    cv2.imshow('Captura Calibracion', frame)
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('c') and ret_encontrado:
        nombre = f"calibracion/img_{contador:03d}.png"
        cv2.imwrite(nombre, frame)
        print(f"✅ {nombre}")
        contador += 1
    elif tecla == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"🎉 {contador} imágenes capturadas.")