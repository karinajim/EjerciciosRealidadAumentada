# cap17_reto.py - Dashboard de rendimiento
import cv2
import numpy as np
import psutil
import time
from collections import deque

class DashboardRendimiento:
    def __init__(self, historial=100):
        self.hist_fps = deque(maxlen=historial)
        self.hist_cpu = deque(maxlen=historial)
        self.hist_mem = deque(maxlen=historial)
        self.proc = psutil.Process()

    def actualizar(self):
        cpu = self.proc.cpu_percent()
        mem = self.proc.memory_info().rss / 1024 / 1024  # MB
        fps = 30 + np.random.randn() * 5  # Simulación (reemplazar con FPS real)
        self.hist_cpu.append(cpu)
        self.hist_mem.append(mem)
        self.hist_fps.append(fps)
        return cpu, mem, fps

    def dibujar_grafico(self, frame, datos, x, y, ancho, alto, color, max_val):
        if len(datos) < 2: return
        puntos = []
        for i, val in enumerate(datos):
            px = x + int((i / len(datos)) * ancho)
            py = y + alto - int((val / max_val) * alto)
            puntos.append((px, py))
        for i in range(len(puntos)-1):
            cv2.line(frame, puntos[i], puntos[i+1], color, 2)

    def dibujar(self, frame):
        cpu, mem, fps = self.actualizar()
        h, w = frame.shape[:2]
        # Panel semi-transparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (w-300, 10), (w-10, 250), (0,0,0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        # Texto de métricas
        cv2.putText(frame, f"CPU: {cpu:.1f}%", (w-280, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(frame, f"MEM: {mem:.1f} MB", (w-280, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        cv2.putText(frame, f"FPS: {fps:.1f}", (w-280, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        # Gráficos
        self.dibujar_grafico(frame, self.hist_cpu, w-280, 100, 260, 40, (0,0,255), 100)
        self.dibujar_grafico(frame, self.hist_mem, w-280, 160, 260, 40, (255,0,0), 500)
        self.dibujar_grafico(frame, self.hist_fps, w-280, 220, 260, 40, (0,255,255), 60)

dashboard = DashboardRendimiento()
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    # Simular app AR (dibujar algo)
    cv2.putText(frame, "App AR con Dashboard", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    dashboard.dibujar(frame)
    cv2.imshow('Dashboard Rendimiento', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()