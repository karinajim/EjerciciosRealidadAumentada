import cv2
import subprocess
import sys

print("="*50)
print("DIAGNÓSTICO DE CÁMARA")
print("="*50)
print(f"Versión de OpenCV: {cv2.__version__}")
print(f"Python versión: {sys.version}")
print()

# Método 1: Probar todos los índices posibles
print("1. BUSCANDO CÁMARAS POR ÍNDICE:")
print("-"*30)

indices_encontrados = []

for i in range(10):  # Probar índices del 0 al 9
    try:
        # Probar con diferentes backends
        for backend_name, backend_flag in [
            ("DEFAULT", None),
            ("DSHOW", cv2.CAP_DSHOW),
            ("MSMF", cv2.CAP_MSMF),
            ("FFMPEG", cv2.CAP_FFMPEG),
            ("IMAGES", cv2.CAP_IMAGES),
            ("ANY", cv2.CAP_ANY)
        ]:
            try:
                if backend_flag:
                    cap = cv2.VideoCapture(i, backend_flag)
                else:
                    cap = cv2.VideoCapture(i)
                
                if cap.isOpened():
                    # Intentar leer un frame
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"  ✓ Cámara {i} con backend {backend_name}: OK")
                        print(f"    - Resolución: {frame.shape[1]}x{frame.shape[0]}")
                        print(f"    - FPS aproximado: {cap.get(cv2.CAP_PROP_FPS)}")
                        indices_encontrados.append((i, backend_name))
                        cap.release()
                        break  # Salir si encontramos con este backend
                    else:
                        print(f"  ✗ Cámara {i} con backend {backend_name}: no se pueden leer frames")
                cap.release()
            except Exception as e:
                print(f"  ✗ Cámara {i} con backend {backend_name}: Error - {str(e)[:50]}")
    except:
        pass

print()

# Método 2: Usar el comando del sistema (Windows)
print("2. DISPOSITIVOS DE VIDEO EN WINDOWS:")
print("-"*30)
try:
    # Usar PowerShell para listar dispositivos de video
    ps_command = "Get-WmiObject Win32_PnPEntity | Where-Object {$_.Name -like '*camera*' -or $_.Name -like '*webcam*' -or $_.Name -like '*video*'} | Select-Object Name, Status"
    result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
    
    if result.stdout.strip():
        print(result.stdout)
    else:
        print("  No se encontraron dispositivos de cámara con PowerShell")
except:
    print("  Error al ejecutar PowerShell")

print()

# Método 3: Usar dispositivo por defecto
print("3. PROBANDO CÁMARA POR DEFECTO:")
print("-"*30)
cap_default = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Forzar DSHOW
if cap_default.isOpened():
    ret, frame = cap_default.read()
    if ret:
        print("  ✓ Cámara funciona con CAP_DSHOW")
        cv2.imwrite("test_capture.jpg", frame)
        print("  ✓ Imagen de prueba guardada como 'test_capture.jpg'")
    cap_default.release()
else:
    print("  ✗ No funciona con CAP_DSHOW")

print()

# Resumen
print("="*50)
print("RESUMEN:")
print("="*50)
if indices_encontrados:
    print(f"✅ Cámaras encontradas: {len(indices_encontrados)}")
    for idx, backend in indices_encontrados:
        print(f"   - Índice {idx} con backend {backend}")
    
    print("\n📝 RECOMENDACIÓN:")
    mejor_idx = indices_encontrados[0][0]
    mejor_backend = indices_encontrados[0][1]
    
    if mejor_backend == "DEFAULT":
        backend_code = ""
    elif mejor_backend == "DSHOW":
        backend_code = ", cv2.CAP_DSHOW"
    elif mejor_backend == "MSMF":
        backend_code = ", cv2.CAP_MSMF"
    else:
        backend_code = ""
    
    print(f"Usa este código:")
    print(f"cap = cv2.VideoCapture({mejor_idx}{backend_code})")
else:
    print("❌ No se encontró ninguna cámara")
    print("\nPOSIBLES SOLUCIONES:")
    print("1. Abre la aplicación 'Cámara' de Windows y verifica que funciona")
    print("2. Desconecta y vuelve a conectar la cámara (si es externa)")
    print("3. Actualiza los drivers de la cámara desde Administrador de dispositivos")
    print("4. Prueba con una cámara USB diferente")
    print("5. Reinicia el equipo")