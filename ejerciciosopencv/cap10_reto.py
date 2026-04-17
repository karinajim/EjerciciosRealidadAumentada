import cv2
import numpy as np

def ordenar_puntos(puntos):
    """Ordena 4 puntos: superior-izq, superior-der, inferior-der, inferior-izq"""
    puntos = puntos.reshape(4, 2)
    suma = puntos.sum(axis=1)
    diff = np.diff(puntos, axis=1)
    ordenados = np.zeros((4, 2), dtype=np.float32)
    ordenados[0] = puntos[np.argmin(suma)]
    ordenados[2] = puntos[np.argmax(suma)]
    ordenados[1] = puntos[np.argmin(diff)]
    ordenados[3] = puntos[np.argmax(diff)]
    return ordenados

# Cargar video a reproducir (o usar cámara secundaria como demo)
video = None
# Si tienes un archivo de video, descomenta:
# video = cv2.VideoCapture("video.mp4")
# Si no, usaremos un patrón de colores animado
usar_video = False

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print("Reemplazo de pantalla. Muestra un monitor con borde claro.")
print("Presiona 'q' para salir.")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret: break

    # Detectar rectángulo de pantalla (usando bordes y contornos)
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bordes = cv2.Canny(gris, 50, 150)
    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contornos:
        # Buscar el contorno más grande y aproximar a polígono
        mayor = max(contornos, key=cv2.contourArea)
        peri = cv2.arcLength(mayor, True)
        aprox = cv2.approxPolyDP(mayor, 0.02 * peri, True)

        if len(aprox) == 4:
            pts = ordenar_puntos(aprox)
            cv2.polylines(frame, [pts.astype(np.int32)], True, (0, 255, 0), 3)

            # Crear contenido para "reemplazar" la pantalla
            h, w = frame.shape[:2]
            if usar_video and video is not None:
                ret_vid, frame_vid = video.read()
                if not ret_vid:
                    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    _, frame_vid = video.read()
            else:
                # Animación de colores
                frame_vid = np.zeros((300, 500, 3), dtype=np.uint8)
                color = ((frame_count * 5) % 255, (frame_count * 3) % 255, (frame_count * 7) % 255)
                cv2.rectangle(frame_vid, (0, 0), (500, 300), color, -1)
                cv2.putText(frame_vid, "PANTALLA AR", (120, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                frame_count += 1

            # Superponer usando homografía
            h_vid, w_vid = frame_vid.shape[:2]
            pts_origen = np.array([[0, 0], [w_vid, 0], [w_vid, h_vid], [0, h_vid]], dtype=np.float32)
            H, _ = cv2.findHomography(pts_origen, pts)
            warped = cv2.warpPerspective(frame_vid, H, (w, h))
            mascara = np.zeros((h, w), dtype=np.uint8)
            cv2.fillConvexPoly(mascara, pts.astype(np.int32), 255)
            mascara = cv2.GaussianBlur(mascara, (5, 5), 0) / 255.0
            for c in range(3):
                frame[:, :, c] = frame[:, :, c] * (1 - mascara) + warped[:, :, c] * mascara

    cv2.imshow('Reemplazo de Pantalla', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
if video: video.release()
cv2.destroyAllWindows()