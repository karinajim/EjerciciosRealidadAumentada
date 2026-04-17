import cv2
import numpy as np

def ordenar_puntos(puntos):
    puntos = puntos.reshape(4, 2)
    suma = puntos.sum(axis=1)
    diff = np.diff(puntos, axis=1)
    ordenados = np.zeros((4, 2), dtype=np.float32)
    ordenados[0] = puntos[np.argmin(suma)]
    ordenados[2] = puntos[np.argmax(suma)]
    ordenados[1] = puntos[np.argmin(diff)]
    ordenados[3] = puntos[np.argmax(diff)]
    return ordenados

def enderezar_documento(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(blur, 50, 150)
    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return imagen
    contorno_doc = max(contornos, key=cv2.contourArea)
    peri = cv2.arcLength(contorno_doc, True)
    aprox = cv2.approxPolyDP(contorno_doc, 0.02 * peri, True)
    if len(aprox) != 4:
        return imagen

    pts_origen = ordenar_puntos(aprox)
    (tl, tr, br, bl) = pts_origen
    ancho1 = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    ancho2 = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    max_ancho = max(int(ancho1), int(ancho2))
    alto1 = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    alto2 = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_alto = max(int(alto1), int(alto2))

    pts_destino = np.array([
        [0, 0],
        [max_ancho - 1, 0],
        [max_ancho - 1, max_alto - 1],
        [0, max_alto - 1]
    ], dtype=np.float32)

    H, _ = cv2.findHomography(pts_origen, pts_destino)
    documento = cv2.warpPerspective(imagen, H, (max_ancho, max_alto))
    return documento

# --- Carga de imagen ---
imagen = cv2.imread('documento_foto.jpg')
if imagen is None:
    # Crear imagen de prueba con márgenes amplios para que no se recorte
    img_prueba = np.zeros((700, 900, 3), dtype=np.uint8)
    cv2.putText(img_prueba, "DOCUMENTO DE PRUEBA", (150, 400),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    # Perspectiva más suave
    pts1 = np.float32([[0, 0], [900, 0], [900, 700], [0, 700]])
    pts2 = np.float32([[30, 60], [870, 40], [850, 640], [50, 620]])
    H_prueba, _ = cv2.findHomography(pts1, pts2)
    imagen = cv2.warpPerspective(img_prueba, H_prueba, (900, 700))

documento = enderezar_documento(imagen)

cv2.imshow('Original con perspectiva', imagen)
cv2.imshow('Documento enderezado', documento)
cv2.waitKey(0)
cv2.destroyAllWindows()