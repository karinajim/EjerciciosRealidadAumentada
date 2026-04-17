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
        print(f"⚠️ No se encontró '{ARCHIVO}'. Guarda primero con 'g'.")

def restablecer_valores(ventana):
    aplicar_valores(ventana, DEFAULT_HSV)
    print("🔄 Valores restablecidos a los valores por defecto.")

# ── CONFIGURACIÓN DE VENTANAS ──────────────────────────────
print("🖥️ Creando ventanas...")
cv2.namedWindow('Control')
cv2.namedWindow('Original')
cv2.namedWindow('Mascara')
cv2.namedWindow('Resultado')

# ── SLIDERS ───────────────────────────────────────────────
print("🎚️ Creando controles deslizantes...")
cv2.createTrackbar('H Min', 'Control', 0,   179, nada)
cv2.createTrackbar('H Max', 'Control', 179, 179, nada)
cv2.createTrackbar('S Min', 'Control', 0,   255, nada)
cv2.createTrackbar('S Max', 'Control', 255, 255, nada)
cv2.createTrackbar('V Min', 'Control', 0,   255, nada)
cv2.createTrackbar('V Max', 'Control', 255, 255, nada)

print("\n📋 CONTROLES:")
print("  g → Guardar valores HSV actuales")
print("  c → Cargar valores HSV guardados")
print("  r → Restablecer valores por defecto")
print("  q → Salir\n")

# ── INTENTAR ABRIR CÁMARA ──────────────────────────────────
print("📷 Buscando cámara...")

# Probar diferentes índices y backends
indice_camara = None
for i in range(3):  # Probar índices 0, 1, 2
    print(f"   Probando índice {i}...")
    # Probar con DirectShow (mejor para Windows)
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"   ✅ ¡Cámara encontrada en índice {i}!")
            indice_camara = i
            break
    cap.release()

# Si no funcionó con DirectShow, probar sin especificar backend
if indice_camara is None:
    for i in range(3):
        print(f"   Probando índice {i} (backend por defecto)...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"   ✅ ¡Cámara encontrada en índice {i}!")
                indice_camara = i
                break
        cap.release()

# Si NO se encontró cámara, usar video
if indice_camara is None:
    print("\n❌ No se encontró ninguna cámara.")
    print("📹 Usando video de prueba en su lugar...\n")
    
    # Descargar video de prueba si no existe
    video_path = 'video_prueba.avi'
    if not os.path.exists(video_path):
        print("   Descargando video de muestra...")
        import urllib.request
        url = 'https://github.com/opencv/opencv/raw/master/samples/data/vtest.avi'
        urllib.request.urlretrieve(url, video_path)
        print(f"   ✅ Video descargado: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    usando_video = True
else:
    cap = cv2.VideoCapture(indice_camara, cv2.CAP_DSHOW)
    usando_video = False
    print(f"\n✅ Cámara lista (índice {indice_camara})")

kernel = np.ones((5, 5), np.uint8)
pausa = False

print("\n🎬 INICIANDO...\n")

# ── BUCLE PRINCIPAL ────────────────────────────────────────
while True:
    if not pausa:
        ret, frame = cap.read()
        if not ret:
            if usando_video:
                # Reiniciar video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                print("❌ Error al leer de la cámara")
                break

    # Si no hay frame válido, salir
    if frame is None:
        print("❌ Frame vacío")
        break

    # Procesar frame
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
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

    # Contornos
    resultado = cv2.bitwise_and(frame, frame, mask=mascara)
    display = frame.copy()

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > 500:
            x, y, w, h = cv2.boundingRect(contorno)
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(display, f'Area: {int(area)}', (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Mostrar información en pantalla
    fuente = cv2.FONT_HERSHEY_SIMPLEX
    estado = "PAUSA" if pausa else "▶ REPRODUCIENDO"
    fuente_info = "VIDEO" if usando_video else f"CAMARA idx:{indice_camara}"
    
    cv2.putText(display, f'{fuente_info} | {estado} | g:guardar c:cargar r:reset q:salir space:pausa',
                (10, 20), fuente, 0.5, (255, 255, 0), 1)

    # Mostrar ventanas
    cv2.imshow('Original', display)
    cv2.imshow('Mascara', mascara)
    cv2.imshow('Resultado', resultado)

    # Teclas
    tecla = cv2.waitKey(30) & 0xFF
    if tecla == ord('q'):
        print("\n👋 Saliendo...")
        break
    elif tecla == ord('g'):
        guardar_valores('Control')
    elif tecla == ord('c'):
        cargar_valores('Control')
    elif tecla == ord('r'):
        restablecer_valores('Control')
    elif tecla == ord(' '):
        pausa = not pausa
        print("⏸️ Pausa" if pausa else "▶️ Reanudando")

# Limpiar
cap.release()
cv2.destroyAllWindows()
print("✅ Programa terminado correctamente")