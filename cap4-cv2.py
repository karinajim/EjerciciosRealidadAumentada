import cv2
import numpy as np

class CorrectorSelfies:
    def __init__(self):
        # Cargar clasificador de rostros
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.intensidad = 0  # 0 = sin efecto, 100 = máximo
        
    def detectar_rostro(self, frame):
        """Detecta el rostro y devuelve puntos clave aproximados"""
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = self.face_cascade.detectMultiScale(gris, 1.1, 4)
        
        if len(rostros) == 0:
            return None, None
        
        # Tomar el rostro más grande
        (x, y, w, h) = max(rostros, key=lambda r: r[2] * r[3])
        
        # Puntos aproximados (basados en proporciones faciales)
        puntos = {
            'ojo_izq': (x + int(w * 0.3), y + int(h * 0.3)),
            'ojo_der': (x + int(w * 0.7), y + int(h * 0.3)),
            'nariz': (x + w//2, y + int(h * 0.6)),
            'boca': (x + w//2, y + int(h * 0.8)),
            'menton': (x + w//2, y + h - 10),
            'frente': (x + w//2, y + 10)
        }
        
        return (x, y, w, h), puntos
    
    def aplicar_correccion(self, frame, rostro_rect, puntos):
        """Aplica transformación para corregir distorsión"""
        x, y, w, h = rostro_rect
        
        if self.intensidad == 0:
            return frame
        
        # Crear puntos de origen (el rostro actual)
        pts_origen = np.float32([
            puntos['ojo_izq'],
            puntos['ojo_der'],
            [puntos['boca'][0] - 20, puntos['boca'][1]],
            [puntos['boca'][0] + 20, puntos['boca'][1]]
        ])
        
        # Calcular factor de corrección
        factor = 1.0 + (self.intensidad / 200.0)  # 1.0 a 1.5
        
        # Crear puntos de destino (rostro corregido)
        pts_destino = np.float32([
            [puntos['ojo_izq'][0] - int(5 * self.intensidad / 10), 
             puntos['ojo_izq'][1]],
            [puntos['ojo_der'][0] + int(5 * self.intensidad / 10), 
             puntos['ojo_der'][1]],
            [puntos['boca'][0] - 20, puntos['boca'][1] + int(10 * self.intensidad / 10)],
            [puntos['boca'][0] + 20, puntos['boca'][1] + int(10 * self.intensidad / 10)]
        ])
        
        # Calcular matriz de transformación
        M = cv2.getPerspectiveTransform(pts_origen, pts_destino)
        
        # Aplicar solo a la región del rostro
        rostro = frame[y:y+h, x:x+w]
        h_rostro, w_rostro = rostro.shape[:2]
        
        rostro_corregido = cv2.warpPerspective(rostro, M, (w_rostro, h_rostro))
        
        # Combinar
        resultado = frame.copy()
        resultado[y:y+h, x:x+w] = rostro_corregido
        
        return resultado
    
    def run(self):
        """Ejecuta el corrector de selfies en tiempo real"""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return
        
        print("Corrector de Selfies")
        print("Controles:")
        print("  'i' / 'd': Aumentar/Disminuir intensidad")
        print("  'r': Resetear")
        print("  'q': Salir")
        
        cv2.namedWindow('Corrector de Selfies')
        cv2.createTrackbar('Intensidad', 'Corrector de Selfies', 0, 100, 
                          lambda x: setattr(self, 'intensidad', x))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detectar rostro
            rostro_rect, puntos = self.detectar_rostro(frame)
            
            if rostro_rect:
                x, y, w, h = rostro_rect
                
                # Dibujar rectángulo del rostro
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Dibujar puntos clave
                if puntos:
                    for nombre, (px, py) in puntos.items():
                        cv2.circle(frame, (px, py), 3, (0, 0, 255), -1)
                
                # Aplicar corrección
                if self.intensidad > 0:
                    frame = self.aplicar_correccion(frame, rostro_rect, puntos)
                    cv2.putText(frame, f"Corrección: {self.intensidad}%", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No se detecta rostro", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Corrector de Selfies', frame)
            
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q'):
                break
            elif tecla == ord('r'):
                self.intensidad = 0
                cv2.setTrackbarPos('Intensidad', 'Corrector de Selfies', 0)
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    corrector = CorrectorSelfies()
    corrector.run()