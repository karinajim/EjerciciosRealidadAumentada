import cv2
import numpy as np

def nada(x):
    pass

# Crear ventanas
cv2.namedWindow('Control')
cv2.namedWindow('Original')
cv2.namedWindow('Mascara')
cv2.namedWindow('Resultado')

# Crear sliders para controlar el rango HSV
cv2.createTrackbar('H Min', 'Control', 0, 179, nada)
cv2.createTrackbar('H Max', 'Control', 179, 179, nada)
cv2.createTrackbar('S Min', 'Control', 0, 255, nada)
cv2.createTrackbar('S Max', 'Control', 255, 255, nada)
cv2.createTrackbar('V Min', 'Control', 0, 255, nada)
cv2.createTrackbar('V Max', 'Control', 255, 255, nada)

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos('H Min', 'Control')
    h_max = cv2.getTrackbarPos('H Max', 'Control')
    s_min = cv2.getTrackbarPos('S Min', 'Control')
    s_max = cv2.getTrackbarPos('S Max', 'Control')
    v_min = cv2.getTrackbarPos('V Min', 'Control')
    v_max = cv2.getTrackbarPos('V Max', 'Control')

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mascara = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((5,5), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

    resultado = cv2.bitwise_and(frame, frame, mask=mascara)

    cv2.imshow('Original', frame)
    cv2.imshow('Mascara', mascara)
    cv2.imshow('Resultado', resultado)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()