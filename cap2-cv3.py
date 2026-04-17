import cv2
import numpy as np
import time

def main():
    print("="*50)
    print("INICIANDO DETECTOR DE COLOR")
    print("="*50)
    
    print("Paso 1: Intentando abrir cámara...")
    # Intentar con DSHOW (más estable en Windows)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("✗ No se pudo abrir cámara con DSHOW, intentando con MSMF...")
        cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print("✗ No se pudo abrir cámara con ningún backend")
        print("Presiona Enter para salir...")
        input()
        return
    
    print("✓ Cámara abierta correctamente")
    
    # Configurar resolución
    print("Paso 2: Configurando resolución...")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Verificar resolución real
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"  Resolución configurada: {ancho}x{alto}")
    
    # Esperar a que la cámara se estabilice
    print("Paso 3: Estabilizando cámara...")
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"  Frame {i+1}: OK")
        else:
            print(f"  Frame {i+1}: Error")
        time.sleep(0.1)
    
    print("\nPaso 4: Creando ventanas...")
    cv2.namedWindow('1. Original', cv2.WINDOW_NORMAL)
    cv2.namedWindow('2. Mascara', cv2.WINDOW_NORMAL)
    cv2.namedWindow('3. Solo Color', cv2.WINDOW_NORMAL)
    
    print("✓ Ventanas creadas")
    print("\n" + "="*50)
    print("PROGRAMA EN EJECUCIÓN")
    print("Presiona 'q' para salir")
    print("="*50 + "\n")
    
    frame_count = 0
    
    while True:
        # Leer frame
        ret, frame = cap.read()
        frame_count += 1
        
        if not ret or frame is None:
            print(f"⚠ Error leyendo frame #{frame_count}")
            continue
        
        # Mostrar mensaje cada 30 frames
        if frame_count % 30 == 0:
            print(f"✓ Procesando... Frame #{frame_count}")
        
        # 1. Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 2. Definir rango de color (verde)
        verde_bajo = np.array([35, 50, 50])
        verde_alto = np.array([85, 255, 255])

        # 3. Crear la máscara
        mascara = cv2.inRange(hsv, verde_bajo, verde_alto)

        # 4. Limpieza
        kernel = np.ones((5,5), np.uint8)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

        # 5. Aplicar máscara
        resultado = cv2.bitwise_and(frame, frame, mask=mascara)

        # Mostrar
        cv2.imshow('1. Original', frame)
        cv2.imshow('2. Mascara', mascara)
        cv2.imshow('3. Solo Color', resultado)

        # Tecla para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nSaliendo por tecla 'q'...")
            break

    print(f"\nTotal frames procesados: {frame_count}")
    print("Liberando recursos...")
    cap.release()
    cv2.destroyAllWindows()
    print("Programa terminado")
    time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Presiona Enter para salir...")
        input()