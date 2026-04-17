# cap17_ejercicio.py - Profiling de rendimiento AR
import cv2
import time
from collections import deque

class ARProfiler:
    def __init__(self, ventana=30):
        self.metricas = {'captura': deque(maxlen=ventana),
                         'procesamiento': deque(maxlen=ventana),
                         'render': deque(maxlen=ventana),
                         'total': deque(maxlen=ventana)}

    def tic(self, etapa):
        self.metricas[etapa].append(time.time())

    def toc(self, etapa):
        if len(self.metricas[etapa]) > 0:
            self.metricas[etapa][-1] = time.time() - self.metricas[etapa][-1]

    def get_fps(self):
        if len(self.metricas['total']) > 0:
            return len(self.metricas['total']) / sum(self.metricas['total'])
        return 0

    def dibujar_grafico(self, frame, x, y, ancho, alto):
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x+ancho, y+alto), (0,0,0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        colores = {'captura': (255,0,0), 'procesamiento': (0,255,0), 'render': (0,0,255)}
        for i, etapa in enumerate(['captura', 'procesamiento', 'render']):
            if len(self.metricas[etapa]) > 0:
                tiempos = list(self.metricas[etapa])
                max_t = max(max(tiempos), 0.001) * 1000
                for j, t in enumerate(tiempos):
                    altura = int((t * 1000 / max_t) * (alto - 20))
                    cv2.line(frame, (x + j, y + alto - 10),
                             (x + j, y + alto - 10 - altura), colores[etapa], 1)
        cv2.putText(frame, f"FPS: {self.get_fps():.1f}", (x, y+20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

# Simulación de app AR
profiler = ARProfiler()
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

while True:
    profiler.tic('total')
    profiler.tic('captura')
    ret, frame = cap.read()
    if not ret: break
    profiler.toc('captura')

    profiler.tic('procesamiento')
    # Simular procesamiento pesado (ej. detección)
    time.sleep(0.005)
    profiler.toc('procesamiento')

    profiler.tic('render')
    # Simular renderizado
    time.sleep(0.003)
    cv2.putText(frame, "AR App Profiling", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    profiler.toc('render')

    profiler.toc('total')
    profiler.dibujar_grafico(frame, frame.shape[1]-220, 10, 200, 100)
    cv2.imshow('Profiling AR', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()