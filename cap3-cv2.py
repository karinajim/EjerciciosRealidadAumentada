import cv2
import numpy as np

class ContadorObjetos:
    def __init__(self):
        self.contadores = {
            "Triángulo": 0,
            "Cuadrado": 0,
            "Rectángulo": 0,
            "Círculo": 0,
            "Desconocido": 0
        }
        self.objetos_previos = set()  # Para trackear objetos únicos
        self.beep_activado = False
    
    def detectar_formas(self, contorno):
        """Identifica la forma basada en el contorno"""
        peri = cv2.arcLength(contorno, True)
        aproximacion = cv2.approxPolyDP(contorno, 0.04 * peri, True)
        vertices = len(aproximacion)
        
        if vertices == 3:
            return "Triángulo"
        elif vertices == 4:
            (x, y, w, h) = cv2.boundingRect(aproximacion)
            aspect_ratio = w / float(h)
            
            if 0.95 <= aspect_ratio <= 1.05:
                return "Cuadrado"
            else:
                return "Rectángulo"
        elif vertices > 6:
            area = cv2.contourArea(contorno)
            (x, y), radio = cv2.minEnclosingCircle(contorno)
            area_circulo = np.pi * radio ** 2
            
            if abs(area - area_circulo) / area_circulo < 0.3:
                return "Círculo"
        
        return "Desconocido"
    
    def get_identificador_unico(self, contorno):
        """Crea un identificador único basado en posición y tamaño"""
        M = cv2.moments(contorno)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            area = cv2.contourArea(contorno)
            # Redondear para agrupar objetos cercanos
            return (round(cX/50), round(cY/50), round(area/100))
        return None
    
    def procesar_frame(self, frame):
        """Procesa un frame y actualiza contadores"""
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
        bordes = cv2.Canny(desenfoque, 50, 150)
        
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
        
        contadores_frame = {k: 0 for k in self.contadores.keys()}
        objetos_actuales = set()
        
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            if area < 500:
                continue
            
            # Detectar forma
            forma = self.detectar_formas(contorno)
            contadores_frame[forma] += 1
            
            # Obtener identificador único
            obj_id = self.get_identificador_unico(contorno)
            if obj_id:
                objetos_actuales.add(obj_id)
                
                # Verificar si es nuevo
                if obj_id not in self.objetos_previos:
                    print(f"✨ Nuevo objeto detectado: {forma}")
                    print('\a')  # Beep (en terminal)
                    self.contadores[forma] += 1
            
            # Dibujar contorno
            cv2.drawContours(frame, [contorno], -1, (0, 255, 0), 2)
            
            # Dibujar etiqueta
            M = cv2.moments(contorno)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.putText(frame, forma, (cX - 50, cY - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        self.objetos_previos = objetos_actuales
        return frame, contadores_frame

def main():
    cap = cv2.VideoCapture(0)
    contador = ContadorObjetos()
    
    print("📊 Contador automático de objetos")
    print("Presiona 'r' para reiniciar contadores")
    print("Presiona 'q' para salir")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame, conteo = contador.procesar_frame(frame)
        
        # Mostrar contadores en pantalla
        y_pos = 30
        cv2.putText(frame, "CONTADORES:", (10, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 25
        
        for forma, cantidad in contador.contadores.items():
            if cantidad > 0:
                color = (0, 255, 0) if forma != "Desconocido" else (0, 0, 255)
                texto = f"📐 {forma}: {cantidad}"
                cv2.putText(frame, texto, (20, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_pos += 20
        
        # Mostrar conteo actual del frame
        texto_actual = f"Actual: " + " ".join([f"{k[:3]}:{v}" for k, v in conteo.items() if v > 0])
        cv2.putText(frame, texto_actual, (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        cv2.imshow('Contador de Objetos', frame)
        
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('r'):
            contador.contadores = {k: 0 for k in contador.contadores.keys()}
            contador.objetos_previos.clear()
            print("🔄 Contadores reiniciados")
        elif tecla == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()