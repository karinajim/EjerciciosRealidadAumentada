
import cv2
import mediapipe as mp
import numpy as np
import random
import time
import json
import os

# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------
ANCHO, ALTO = 1280, 720
PUNTOS = 0
VIDAS = 3
NIVEL = 1
PUNTOS_NIVEL = 100
VELOCIDAD_BASE = 5
OBJETOS = []
ULTIMO_GESTO = 0
TIEMPO_GESTO = 1.0

# ------------------------------------------------------------
# MediaPipe Hands
# ------------------------------------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

def detectar_gesto(landmarks):
    # Puntas y nudillos
    punta_indice = landmarks.landmark[8]
    punta_medio = landmarks.landmark[12]
    punta_anular = landmarks.landmark[16]
    punta_menique = landmarks.landmark[20]
    nudillo_indice = landmarks.landmark[6]

    dedos = 0
    if punta_indice.y < nudillo_indice.y: dedos += 1
    if punta_medio.y < landmarks.landmark[10].y: dedos += 1
    if punta_anular.y < landmarks.landmark[14].y: dedos += 1
    if punta_menique.y < landmarks.landmark[18].y: dedos += 1

    if dedos == 0: return "puño"
    elif dedos == 1 and punta_indice.y < nudillo_indice.y: return "señalar"
    elif dedos == 2 and punta_indice.y < nudillo_indice.y and punta_medio.y < landmarks.landmark[10].y: return "paz"
    elif dedos == 5: return "abierta"
    return "none"

def aplicar_gesto(gesto, tiempo_actual, pos_mano):
    global PUNTOS, OBJETOS, ULTIMO_GESTO, VELOCIDAD_BASE
    if gesto == "none": return
    if tiempo_actual - ULTIMO_GESTO < TIEMPO_GESTO: return
    ULTIMO_GESTO = tiempo_actual

    if gesto == "puño":
        for obj in OBJETOS:
            obj['velocidad'] = max(1, obj['velocidad'] * 0.5)
    elif gesto == "paz":
        PUNTOS += 20
    elif gesto == "abierta" and pos_mano:
        mx, my = pos_mano
        OBJETOS = [obj for obj in OBJETOS if np.sqrt((mx-obj['x'])**2 + (my-obj['y'])**2) > 100]

def crear_objeto():
    tipo = random.choice(['bueno', 'malo', 'especial'])
    radio = 30 if tipo == 'especial' else 20
    velocidad = VELOCIDAD_BASE * (2.0 if tipo == 'malo' else 1.0)
    puntos = 10 if tipo == 'bueno' else (-10 if tipo == 'malo' else 50)
    return {'x': random.randint(50, ANCHO-50), 'y': 50.0, 'tipo': tipo,
            'radio': radio, 'velocidad': velocidad, 'puntos': puntos}

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
    if not pos_mano: return
    mx, my = pos_mano
    sobrevivientes = []
    for obj in OBJETOS:
        if np.sqrt((mx-obj['x'])**2 + (my-obj['y'])**2) < obj['radio'] + 30:
            PUNTOS += obj['puntos']
            if obj['tipo'] == 'malo':
                VIDAS -= 1
        else:
            sobrevivientes.append(obj)
    OBJETOS = sobrevivientes

def guardar_ranking(nombre):
    entrada = {'nombre': nombre, 'puntos': PUNTOS, 'nivel': NIVEL}
    ranking = []
    if os.path.exists('ranking.json'):
        with open('ranking.json', 'r') as f:
            ranking = json.load(f)
    ranking.append(entrada)
    ranking.sort(key=lambda x: x['puntos'], reverse=True)
    with open('ranking.json', 'w') as f:
        json.dump(ranking[:10], f, indent=2)

def dibujar_ui(frame, gesto):
    cv2.putText(frame, f"Puntos: {PUNTOS}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.putText(frame, f"Vidas: {VIDAS}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0) if VIDAS>0 else (0,0,255), 2)
    cv2.putText(frame, f"Nivel: {NIVEL}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
    cv2.putText(frame, f"Gesto: {gesto}", (ANCHO-200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

# ------------------------------------------------------------
# Captura
# ------------------------------------------------------------
cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)

print("🎮 AR Catcher - Usa gestos: ✊ Puño, ✌️ Paz, 🖐️ Abierta")
inicio = time.time()

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = hands.process(rgb)

    pos_mano = None
    gesto = "none"
    if resultados.multi_hand_landmarks:
        hand = resultados.multi_hand_landmarks[0]
        muneca = hand.landmark[0]
        pos_mano = (int(muneca.x * ANCHO), int(muneca.y * ALTO))
        gesto = detectar_gesto(hand)
        aplicar_gesto(gesto, time.time(), pos_mano)
        cv2.circle(frame, pos_mano, 30, (255,255,255), 3)
        mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    # Nivel y dificultad
    NIVEL = PUNTOS // PUNTOS_NIVEL + 1
    VELOCIDAD_BASE = 5 + (NIVEL - 1) * 2

    if len(OBJETOS) < 10 and random.random() < 0.02:
        OBJETOS.append(crear_objeto())

    actualizar_objetos()
    verificar_colisiones(pos_mano)

    for obj in OBJETOS:
        if obj['tipo'] == 'bueno':
            color = (0,255,0)
        elif obj['tipo'] == 'malo':
            color = (0,0,255)
        else:
            color = (255,255,0)
        # Convertir coordenadas a entero al dibujar
        cx, cy = int(obj['x']), int(obj['y'])
        cv2.circle(frame, (cx, cy), obj['radio'], color, -1)
        cv2.circle(frame, (cx, cy), obj['radio'], (255,255,255), 2)

    dibujar_ui(frame, gesto)
    cv2.imshow('AR Catcher - Reto', frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or VIDAS <= 0:
        if VIDAS <= 0:
            print(f"💀 Game Over! Puntos: {PUNTOS}, Nivel: {NIVEL}")
            nombre = input("Tu nombre para el ranking: ")
            guardar_ranking(nombre)
        break

cap.release()
cv2.destroyAllWindows()