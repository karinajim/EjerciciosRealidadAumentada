import cv2
import numpy as np
import os

def nada(x):
    pass

# Valores por defecto
DEFAULT_HSV = np.array([
    [0, 179],    # H min, H max
    [0, 255],    # S min, S max
    [0, 255]     # V min, V max
])

ARCHIVO = 'color_favorito.npy'

def aplicar_valores(ventana, valores):
    """Aplica valores HSV a los sliders."""
    cv2.setTrackbarPos('H Min', ventana, int(valores[0][0]))
    cv2.setTrackbarPos('H Max', ventana, int(valores[0][1]))
    cv2.setTrackbarPos('S Min', ventana, int(valores[1][0]))
    cv2.setTrackbarPos('S Max', ventana, int(valores[1][1]))
    cv2.setTrackbarPos('V Min', ventana, int(valores[2][0]))
    cv2.setTrackbarPos('V Max', ventana, int(valores[2][1]))

def obtener_valores(ventana):
    """Lee los valores actuales de los sliders."""
    return np.array([
        [cv2.getTrackbarPos('H Min', ventana), cv2.getTrackbarPos('H Max', ventana)],
        [cv2.getTrackbarPos('S Min', ventana), cv2.getTrackbarPos('S Max', ventana)],
        [cv2.getTrackbarPos('V Min', ventana), cv2.getTrackbarPos('V Max', ventana)],
    ])

def guardar_valores(ventana):
    valores = obtener_valores(ventana)
    np.save(ARCHIVO, valores)
    print(f"✅ Valores guardados en '{ARCHIVO}': {valores.tolist()}")

def cargar_valores(ventana):
    if os.path.exists(ARCHIVO):
        valores = np.load(ARCHIVO)
        aplicar_valores(ventana, valores)
        print(f"📂 Valores cargados desde '{ARCHIVO}': {valores.tolist()}")
    else:
        print(f"⚠️  No se encontró '{ARCHIVO}'. Guarda primero con 'g'.")

def restablecer_valores(ventana):
    aplicar_valores(ventana, DEFAULT_HSV)
    print("🔄 Valores restablecidos a los valores por defecto.")

# ── Ventanas ──────────────────────────────────────────────
cv2.namedWindow('Control')
cv2.namedWindow('Original')
cv2.namedWindow('Mascara')
cv2.namedWindow('Resultado')

# ── Sliders ───────────────────────────────────────────────
cv2.createTrackbar('H Min', 'Control', 0,   179, nada)
cv2.createTrackbar('H Max', 'Control', 179, 179, nada)
cv2.createTrackbar('S Min', 'Control', 0,   255, nada)
cv2.createTrackbar('S Max', 'Control', 255, 255, nada)
cv2.createTrackbar('V Min', 'Control', 0,   255, nada)
cv2.createTrackbar('V Max', 'Control', 255, 255, nada)

print("Controles:")
print("  g → Guardar valores HSV actuales")
print("  c → Cargar valores HSV guardados")
print("  r → Restablecer valores por defecto")
print("  q → Salir")

# ── Captura ───────────────────────────────────────────────
cap = cv2.VideoCapture(1)
kernel = np.ones((5, 5), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Leer sliders
    h_min = cv2.getTrackbarPos('H Min', 'Control')
    h_max = cv2.getTrackbarPos('H Max', 'Control')
    s_min = cv2.getTrackbarPos('S Min', 'Control')
    s_max = cv2.getTrackbarPos('S Max', 'Control')
    v_min = cv2.getTrackbarPos('V Min', 'Control')
    v_max = cv2.getTrackbarPos('V Max', 'Control')

    # Máscara
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mascara = cv2.inRange(hsv, lower, upper)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN,  kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

    # Contornos con rectángulo y área
    resultado = cv2.bitwise_and(frame, frame, mask=mascara)
    display   = frame.copy()

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > 500:
            x, y, w, h = cv2.boundingRect(contorno)
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(display, f'Area: {int(area)}', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Mostrar teclas activas en pantalla
    cv2.putText(display, 'g:guardar  c:cargar  r:reset  q:salir',
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    cv2.imshow('Original', display)
    cv2.imshow('Mascara',  mascara)
    cv2.imshow('Resultado', resultado)

    # ── Teclas ────────────────────────────────────────────
    tecla = cv2.waitKey(1) & 0xFF
    if   tecla == ord('q'): break
    elif tecla == ord('g'): guardar_valores('Control')
    elif tecla == ord('c'): cargar_valores('Control')
    elif tecla == ord('r'): restablecer_valores('Control')

cap.release()
cv2.destroyAllWindows()