import cv2
import numpy as np

def detectar_formas(contorno):
    """Identifica la forma basada en el contorno"""
    peri = cv2.arcLength(contorno, True)
    aproximacion = cv2.approxPolyDP(contorno, 0.04 * peri, True)
    vertices = len(aproximacion)

    if vertices == 3:
        return "Triángulo"
    elif vertices == 4:
        (x, y, w, h) = cv2.boundingRect(aproximacion)
        aspect_ratio = w / float(h)
        if 0.95 <= aspect_ratio <= 1.05:
            return "Cuadrado"
        else:
            return "Rectángulo"
    elif vertices > 6:
        area = cv2.contourArea(contorno)
        (x, y), radio = cv2.minEnclosingCircle(contorno)
        area_circulo = np.pi * radio ** 2
        if abs(area - area_circulo) / area_circulo < 0.3:
            return "Círculo"
    return "Desconocido"

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(desenfoque, 50, 150)

    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area < 500:
            continue

        forma = detectar_formas(contorno)
        cv2.drawContours(frame, [contorno], -1, (0, 255, 0), 2)

        M = cv2.moments(contorno)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.putText(frame, forma, (cX - 50, cY - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow('Detector de Formas', frame)
    cv2.imshow('Bordes Canny', bordes)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()