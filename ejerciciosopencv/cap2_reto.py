import cv2
import numpy as np

def nada(x): pass

cv2.namedWindow('Control')
cv2.createTrackbar('H Min', 'Control', 0, 179, nada)
cv2.createTrackbar('H Max', 'Control', 179, 179, nada)
cv2.createTrackbar('S Min', 'Control', 0, 255, nada)
cv2.createTrackbar('S Max', 'Control', 255, 255, nada)
cv2.createTrackbar('V Min', 'Control', 0, 255, nada)
cv2.createTrackbar('V Max', 'Control', 255, 255, nada)

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret: break

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
    cv2.imshow('Resultado', resultado)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'):
        break
    elif tecla == ord('g'):
        valores = np.array([h_min, h_max, s_min, s_max, v_min, v_max])
        np.save('color_favorito.npy', valores)
        print("Valores guardados")
    elif tecla == ord('c'):
        try:
            valores = np.load('color_favorito.npy')
            cv2.setTrackbarPos('H Min', 'Control', int(valores[0]))
            cv2.setTrackbarPos('H Max', 'Control', int(valores[1]))
            cv2.setTrackbarPos('S Min', 'Control', int(valores[2]))
            cv2.setTrackbarPos('S Max', 'Control', int(valores[3]))
            cv2.setTrackbarPos('V Min', 'Control', int(valores[4]))
            cv2.setTrackbarPos('V Max', 'Control', int(valores[5]))
            print("Valores cargados")
        except:
            print("No se encontró archivo")
    elif tecla == ord('r'):
        cv2.setTrackbarPos('H Min', 'Control', 0)
        cv2.setTrackbarPos('H Max', 'Control', 179)
        cv2.setTrackbarPos('S Min', 'Control', 0)
        cv2.setTrackbarPos('S Max', 'Control', 255)
        cv2.setTrackbarPos('V Min', 'Control', 0)
        cv2.setTrackbarPos('V Max', 'Control', 255)
        print("Valores restablecidos")

cap.release()
cv2.destroyAllWindows()