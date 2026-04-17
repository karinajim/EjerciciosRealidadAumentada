import cv2
import numpy as np

def ordenar_puntos(puntos):
    """Ordena 4 puntos en el orden: superior-izq, superior-der, inferior-der, inferior-izq"""
    puntos = puntos.reshape(4, 2)
    suma = puntos.sum(axis=1)
    diff = np.diff(puntos, axis=1)
    
    ordenados = np.zeros((4, 2), dtype=np.float32)
    ordenados[0] = puntos[np.argmin(suma)]  # Superior-izq
    ordenados[2] = puntos[np.argmax(suma)]  # Inferior-der
    ordenados[1] = puntos[np.argmin(diff)]  # Superior-der
    ordenados[3] = puntos[np.argmax(diff)]  # Inferior-izq
    
    return ordenados

def detectar_documento(imagen):
    """Encuentra el contorno del documento (asumimos el más grande)"""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    bordes = cv2.Canny(desenfoque, 50, 150)
    
    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Buscar el contorno más grande
    contorno_doc = max(contornos, key=cv2.contourArea)
    
    # Aproximar a un polígono
    peri = cv2.arcLength(contorno_doc, True)
    aproximacion = cv2.approxPolyDP(contorno_doc, 0.02 * peri, True)
    
    return aproximacion

def enderezar_documento(imagen):
    """Aplica transformación para enderezar el documento"""
    # Detectar esquinas del documento
    esquinas = detectar_documento(imagen)
    
    if len(esquinas) != 4:
        print("No se detectó un documento rectangular")
        return imagen
    
    # Ordenar puntos
    pts_origen = ordenar_puntos(esquinas)
    
    # Calcular dimensiones del documento enderezado
    (tl, tr, br, bl) = pts_origen
    ancho1 = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    ancho2 = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    max_ancho = max(int(ancho1), int(ancho2))
    
    alto1 = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    alto2 = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_alto = max(int(alto1), int(alto2))
    
    # Puntos destino (rectángulo perfecto)
    pts_destino = np.array([
        [0, 0],
        [max_ancho - 1, 0],
        [max_ancho - 1, max_alto - 1],
        [0, max_alto - 1]
    ], dtype=np.float32)
    
    # Calcular homografía
    H, _ = cv2.findHomography(pts_origen, pts_destino)
    
    # Aplicar transformación
    documento = cv2.warpPerspective(imagen, H, (max_ancho, max_alto))
    
    return documento

def main():
    print("📄 Enderezador de documentos")
    print("=" * 40)
    
    # Cargar imagen (crear una de prueba si no existe)
    imagen = cv2.imread('documento_foto.jpg')
    
    if imagen is None:
        print("Creando imagen de prueba con perspectiva...")
        # Crear imagen de prueba
        imagen = np.zeros((600, 800, 3), dtype=np.uint8)
        cv2.putText(imagen, "DOCUMENTO DE PRUEBA", (100, 300),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # Añadir perspectiva artificial
        pts1 = np.float32([[0, 0], [800, 0], [800, 600], [0, 600]])
        pts2 = np.float32([[50, 100], [750, 50], [780, 550], [30, 500]])
        H_prueba, _ = cv2.findHomography(pts1, pts2)
        imagen = cv2.warpPerspective(imagen, H_prueba, (800, 600))
    
    # Enderezar
    documento = enderezar_documento(imagen)
    
    # Mostrar resultados
    cv2.imshow('Original con perspectiva', imagen)
    cv2.imshow('Documento enderezado', documento)
    
    print("Procesamiento completado")
    print("Presiona cualquier tecla para salir")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()