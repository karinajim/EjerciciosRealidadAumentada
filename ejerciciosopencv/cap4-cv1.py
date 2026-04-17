# cap4_cv1.py - Enderezador de documentos (versión robusta)
import cv2
import numpy as np
import os

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
        return None

    contorno_doc = max(contornos, key=cv2.contourArea)
    peri = cv2.arcLength(contorno_doc, True)
    aprox = cv2.approxPolyDP(contorno_doc, 0.02 * peri, True)

    if len(aprox) != 4:
        return None

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
    if H is None:
        return None

    documento = cv2.warpPerspective(imagen, H, (max_ancho, max_alto))
    return documento


# --- Búsqueda automática de la imagen en ubicaciones comunes ---
posibles_rutas = [
    "../documento_foto.jpg",               # Subir un nivel
    "documento_foto.jpg",                  # Misma carpeta
    "../abc/documento_foto.jpg",           # Carpeta abc
    os.path.join("..", "..", "documento_foto.jpg")  # Dos niveles arriba
]

imagen = None
ruta_usada = None

for ruta in posibles_rutas:
    img = cv2.imread(ruta)
    if img is not None:
        imagen = img
        ruta_usada = ruta
        break

if imagen is None:
    print("❌ No se pudo cargar 'documento_foto.jpg' en ninguna de estas ubicaciones:")
    for r in posibles_rutas:
        print(f"   - {r}")
    print("\nAsegúrate de que el archivo existe y está en la carpeta correcta.")
    exit()

print(f"✅ Imagen cargada desde: {ruta_usada}")

documento = enderezar_documento(imagen)

cv2.imshow('Original con perspectiva', imagen)

if documento is not None:
    cv2.imshow('Documento enderezado', documento)
    print("✅ Documento enderezado correctamente.")
else:
    print("⚠️ No se pudo detectar un documento rectangular. Mostrando original.")
    cv2.imshow('Documento enderezado (fallo)', imagen)

print("Presiona cualquier tecla para cerrar las ventanas.")
cv2.waitKey(0)
cv2.destroyAllWindows()