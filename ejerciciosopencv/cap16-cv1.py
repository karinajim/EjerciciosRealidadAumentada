# cap16_ejercicio_corregido.py
import cv2
import mediapipe as mp
import numpy as np
import random
import time

# ------------------------------------------------------------
# Configuración del juego
# ------------------------------------------------------------
ANCHO, ALTO = 1280, 720
PUNTOS = 0
VIDAS = 3
VELOCIDAD_BASE = 5
OBJETOS = []

# Colores
COLOR_BUENO = (0, 255, 0)
COLOR_MALO = (0, 0, 255)

# ------------------------------------------------------------
# MediaPipe Hands
# ------------------------------------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def crear_objeto():
    tipo = random.choice(['bueno', 'malo'])
    radio = 20
    x = random.randint(50, ANCHO - 50)
    y = 50.0  # Usamos float para el movimiento suave, luego convertiremos a int al dibujar
    velocidad = VELOCIDAD_BASE * (1.5 if tipo == 'malo' else 1.0)
    puntos = 10 if tipo == 'bueno' else -5
    return {'x': x, 'y': y, 'tipo': tipo, 'radio': radio, 'velocidad': velocidad, 'puntos': puntos}

def actualizar_objetos():
    global OBJETOS, PUNTOS
    nuevos = []
    for obj in OBJETOS:
        obj['y'] += obj['velocidad']
        if obj['y'] < ALTO + 50:
            nuevos.append(obj)
        elif obj['tipo'] == 'bueno':
            PUNTOS = max(0, PUNTOS - 2)
    OBJETOS = nuevos

def verificar_colisiones(pos_mano):
    global OBJETOS, PUNTOS, VIDAS
    if pos_mano is None: return
    mx, my = pos_mano
    sobrevivientes = []
    for obj in OBJETOS:
        dist = np.sqrt((mx - obj['x'])**2 + (my - obj['y'])**2)
        if dist < obj['radio'] + 30:
            PUNTOS += obj['puntos']
            if obj['tipo'] == 'malo':
                VIDAS -= 1
        else:
            sobrevivientes.append(obj)
    OBJETOS = sobrevivientes

def dibujar_ui(frame):
    cv2.putText(frame, f"Puntos: {PUNTOS}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.putText(frame, f"Vidas: {VIDAS}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0) if VIDAS>0 else (0,0,255), 2)
    cv2.rectangle(frame, (10, 100), (10 + VIDAS*50, 130), (0,255,0), -1)

# ------------------------------------------------------------
# Captura de video
# ------------------------------------------------------------
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)

print("🎮 AR Catcher. Atrapa verdes, esquiva rojos. 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)  # Espejo para movimiento natural
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = hands.process(rgb)

    pos_mano = None
    if resultados.multi_hand_landmarks:
        hand = resultados.multi_hand_landmarks[0]
        muneca = hand.landmark[0]
        pos_mano = (int(muneca.x * ANCHO), int(muneca.y * ALTO))
        cv2.circle(frame, pos_mano, 30, (255,255,255), 3)
        mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    # Crear objetos aleatoriamente
    if len(OBJETOS) < 10 and random.random() < 0.02:
        OBJETOS.append(crear_objeto())

    actualizar_objetos()
    verificar_colisiones(pos_mano)

    # Dibujar objetos (convertir coordenadas a int)
    for obj in OBJETOS:
        color = COLOR_BUENO if obj['tipo'] == 'bueno' else COLOR_MALO
        cx, cy = int(obj['x']), int(obj['y'])
        cv2.circle(frame, (cx, cy), obj['radio'], color, -1)
        cv2.circle(frame, (cx, cy), obj['radio'], (255,255,255), 2)

    dibujar_ui(frame)
    cv2.imshow('AR Catcher', frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or VIDAS <= 0:
        if VIDAS <= 0:
            print(f"💀 Game Over! Puntuación final: {PUNTOS}")
            time.sleep(2)
        break

cap.release()
cv2.destroyAllWindows()