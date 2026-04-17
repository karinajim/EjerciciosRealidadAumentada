import cv2
import numpy as np
import time
import math

# ==============================
# CONFIGURACIÓN
# ==============================
LIMITE_PERSONAS = 3
DISTANCIA_MINIMA = 50  # distancia para considerar misma persona

# Cargar Haar Cascade (viene con OpenCV, no necesita descarga)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Verificar que se cargó correctamente
if face_cascade.empty():
    print("❌ Error: No se pudo cargar Haar Cascade")
    exit()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Usar DSHOW para Windows

if not cap.isOpened():
    print("❌ No se pudo abrir la cámara")
    exit()

# Lista para almacenar centros detectados
personas_registradas = []

# ==============================
# FUNCIÓN PARA MEDIR DISTANCIA
# ==============================
def distancia(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# ==============================
# LOOP PRINCIPAL
# ==============================
print("\n👥 Contador de Personas - Haar Cascade")
print(f"Límite: {LIMITE_PERSONAS} personas")
print("Presiona 'q' para salir\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    inicio = time.time()
    
    # Convertir a escala de grises
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detectar rostros con Haar Cascade
    rostros = face_cascade.detectMultiScale(
        gris, 
        scaleFactor=1.1,      # Compensación por tamaño
        minNeighbors=5,       # Eliminar falsos positivos
        minSize=(50, 50)      # Tamaño mínimo del rostro
    )
    
    personas_actuales = []
    
    # Dibujar detecciones
    for (x, y, w, h) in rostros:
        centro = (x + w//2, y + h//2)
        personas_actuales.append(centro)
        
        # Dibujar rectángulo
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Dibujar centro
        cv2.circle(frame, centro, 5, (0, 0, 255), -1)
        
        # Mostrar coordenadas
        cv2.putText(frame, f"({centro[0]}, {centro[1]})", 
                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.4, (255, 255, 255), 1)
    
    # ==============================
    # SISTEMA DE CONTEO ÚNICO
    # ==============================
    for centro in personas_actuales:
        es_nueva = True
        
        for registrado in personas_registradas:
            if distancia(centro, registrado) < DISTANCIA_MINIMA:
                es_nueva = False
                break
        
        if es_nueva:
            personas_registradas.append(centro)
            print(f"✨ Nueva persona detectada! Total: {len(personas_registradas)}")
    
    total_personas = len(personas_registradas)
    
    # ==============================
    # ALERTA
    # ==============================
    if total_personas > LIMITE_PERSONAS:
        cv2.putText(frame, "⚠ LIMITE EXCEDIDO!", (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    
    # ==============================
    # TERMÓMETRO VISUAL
    # ==============================
    altura_termometro = 200
    base_x = frame.shape[1] - 70
    base_y = frame.shape[0] - 100
    
    # Fondo del termómetro
    cv2.rectangle(frame, (base_x, base_y - altura_termometro),
                  (base_x + 30, base_y), (100, 100, 100), -1)
    
    # Borde
    cv2.rectangle(frame, (base_x, base_y - altura_termometro),
                  (base_x + 30, base_y), (255, 255, 255), 2)
    
    # Nivel actual
    nivel = min(total_personas / LIMITE_PERSONAS, 1.0)
    altura_nivel = int(altura_termometro * nivel)
    
    if total_personas <= LIMITE_PERSONAS:
        color = (0, 255, 0)  # Verde
    else:
        color = (0, 0, 255)  # Rojo
    
    cv2.rectangle(frame,
                  (base_x, base_y - altura_nivel),
                  (base_x + 30, base_y),
                  color, -1)
    
    # Marcas de nivel
    for i in range(1, LIMITE_PERSONAS + 1):
        nivel_y = base_y - int(altura_termometro * (i / LIMITE_PERSONAS))
        cv2.line(frame, (base_x - 5, nivel_y), (base_x + 35, nivel_y), 
                 (200, 200, 200), 1)
    
    # ==============================
    # TEXTO Y FPS
    # ==============================
    fps = 1 / (time.time() - inicio + 1e-6)
    
    # Mostrar información
    cv2.putText(frame, f"Personas unicas: {total_personas}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    cv2.putText(frame, f"Detecciones: {len(personas_actuales)}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 1)
    
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    
    # Instrucciones
    cv2.putText(frame, "q: salir", (frame.shape[1] - 100, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Mostrar lista de personas registradas (debug)
    y_pos = 110
    cv2.putText(frame, "Registradas:", (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    y_pos += 20
    
    for i, p in enumerate(personas_registradas[-5:]):  # Últimas 5
        cv2.putText(frame, f"{i+1}: ({p[0]}, {p[1]})", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        y_pos += 15
    
    cv2.imshow("Contador de Personas - Haar Cascade", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==============================
# ESTADÍSTICAS FINALES
# ==============================
print("\n" + "="*40)
print("📊 ESTADÍSTICAS FINALES")
print("="*40)
print(f"Total de personas únicas detectadas: {len(personas_registradas)}")
print(f"Tiempo total de ejecución: {time.time() - inicio_global:.1f} segundos")
print("\n✅ Programa terminado")

cap.release()
cv2.destroyAllWindows()