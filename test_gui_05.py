# Importamos sys
import sys
# Elementos visuales a utilizar
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt

# Creamos plantilla de una ventana
class JuegoBolita(QWidget):
    # Funcion que ejecuta al crear un objeto
    def __init__(self):
        # Llamamos al constructora del padre
        super().__init__()
        # Colocamos titulo a ventana
        self.setWindowTitle("Bolita en movimiento")
        # Dimensiones a la ventana
        self.setGeometry(200,200,400,300)
        # Posicion inicial a la bolita
        self.x = 50
        self.y = 50
        #Variable para el juego activo
        self.juego_activo = True
        
        # Tamaño de la bolita
        self.bolita_size = 30
        # Dimensiones de la ventana
        self.ventana_width = 400
        self.ventana_height = 300
        
        self.crear_interfaz()
    
    # Esta funcion crea la interfaz grafica de la ventana
    def crear_interfaz(self):
        # Creamos la bolita
        self.bolita = QLabel(self)
        self.bolita.setGeometry(self.x, self.y, self.bolita_size, self.bolita_size)
        self.bolita.setStyleSheet("background-color: red; border-radius: 15px;")
        
        # Creamos el primer enemigo
        self.enemigo = QLabel(self)
        self.enemigo.setGeometry(180, 120, 40, 40)
        self.enemigo.setStyleSheet("background-color: black;")
        
        # Creamos el segundo enemigo
        self.enemigo2 = QLabel(self)
        self.enemigo2.setGeometry(280, 80, 35, 35)
        self.enemigo2.setStyleSheet("background-color: blue; border-radius: 17px;")
        
        # Creamos el tercer enemigo (nuevo)
        self.enemigo3 = QLabel(self)
        self.enemigo3.setGeometry(100, 200, 45, 45)
        self.enemigo3.setStyleSheet("background-color: green; border-radius: 22px;")
        
        # Botones
        self.btn_arriba = QPushButton("↑", self)
        self.btn_arriba.move(300, 50)
        self.btn_arriba.clicked.connect(self.arriba)
        
        # Botones abajo
        self.btn_abajo = QPushButton("↓", self)
        self.btn_abajo.move(300, 130)
        self.btn_abajo.clicked.connect(self.abajo)
        
        # Botones delante
        self.btn_delante = QPushButton("→", self)
        self.btn_delante.move(340, 90)
        self.btn_delante.clicked.connect(self.delante)
        
        # Botones atras
        self.btn_atras = QPushButton("←", self)
        self.btn_atras.move(260, 90)
        self.btn_atras.clicked.connect(self.atras)
        
        # Botón de reinicio
        self.btn_reinicio = QPushButton("Reiniciar", self)
        self.btn_reinicio.move(300, 200)
        self.btn_reinicio.clicked.connect(self.reiniciar_juego)
        self.btn_reinicio.hide()  # Ocultamos inicialmente
    
    # Función para verificar límites
    def verificar_limites(self, nueva_x, nueva_y):
        # Limitar coordenada X para que no sea menor a 0
        if nueva_x < 0:
            return 0, nueva_y
        # Limitar coordenada Y para que no sea menor a 0
        if nueva_y < 0:
            return nueva_x, 0
        # Limitar coordenada X para que no salga por la derecha
        if nueva_x > self.ventana_width - self.bolita_size:
            return self.ventana_width - self.bolita_size, nueva_y
        # Limitar coordenada Y para que no salga por abajo
        if nueva_y > self.ventana_height - self.bolita_size:
            return nueva_x, self.ventana_height - self.bolita_size
        return nueva_x, nueva_y
    
    # Funcion de movimiento hacia arriba 
    def arriba(self):
        if self.juego_activo:
            self.x, self.y = self.verificar_limites(self.x, self.y - 10)
            self.actualizar()
    
    # Funcion de movimiento hacia abajo
    def abajo(self):
        if self.juego_activo:
            self.x, self.y = self.verificar_limites(self.x, self.y + 10)
            self.actualizar()
        
    # Funcion de movimiento hacia delante 
    def delante(self):
        if self.juego_activo:
            self.x, self.y = self.verificar_limites(self.x + 10, self.y)
            self.actualizar()
        
    # Funcion de movimiento hacia atras
    def atras(self):
        if self.juego_activo:
            self.x, self.y = self.verificar_limites(self.x - 10, self.y)
            self.actualizar()
    
    # Funcion que mueve la bolita 
    def actualizar(self): 
        self.bolita.move(self.x, self.y)
        self.detectar_colision()
        print(f"Posición: ({self.x}, {self.y})")
        
    # Funcion que detecta colisiones con todos los enemigos
    def detectar_colision(self):
        if not self.juego_activo:
            return
            
        # Detectar colisión con el primer enemigo
        if self.bolita.geometry().intersects(self.enemigo.geometry()):
            self.game_over("¡Chocaste con el enemigo negro!")
            return
            
        # Detectar colisión con el segundo enemigo
        if self.bolita.geometry().intersects(self.enemigo2.geometry()):
            self.game_over("¡Chocaste con el enemigo azul!")
            return
            
        # Detectar colisión con el tercer enemigo
        if self.bolita.geometry().intersects(self.enemigo3.geometry()):
            self.game_over("¡Chocaste con el enemigo verde!")
            return
    
    def game_over(self, mensaje):
        self.juego_activo = False 
        self.bolita.hide()  # Ocultamos bolita
        QMessageBox.critical(self, "GAME OVER", mensaje)
        self.desactivar_botones()
        self.btn_reinicio.show()  # Mostramos botón de reinicio
    
    def desactivar_botones(self):
        self.btn_arriba.setEnabled(False)
        self.btn_abajo.setEnabled(False)
        self.btn_delante.setEnabled(False)
        self.btn_atras.setEnabled(False)
    
    def reiniciar_juego(self):
        # Restablecer posición de la bolita
        self.x = 50
        self.y = 50
        self.bolita.move(self.x, self.y)
        self.bolita.show()
        
        # Activar juego
        self.juego_activo = True
        
        # Activar botones de movimiento
        self.btn_arriba.setEnabled(True)
        self.btn_abajo.setEnabled(True)
        self.btn_delante.setEnabled(True)
        self.btn_atras.setEnabled(True)
        
        # Ocultar botón de reinicio
        self.btn_reinicio.hide()
        
        print("Juego reiniciado")

# Creamos nuestra aplicacion
app = QApplication(sys.argv)
ventana = JuegoBolita()
ventana.show()
sys.exit(app.exec())
        
    
    
        