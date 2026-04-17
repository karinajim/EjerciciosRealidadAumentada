#Import sys
import sys
#Importamos componentes visuales
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton

#Una funcion para Cambiar de color de fondo de la ventana
def color(hex_color, color):
    ventana.setStyleSheet(f"background-color: {hex_color}; color: {color};")
    
#Creamos aplicación
app = QApplication(sys.argv)

ventana = QWidget() #Creamos una ventana
ventana.setWindowTitle("Colores") #Añadimos titulo a la ventana
ventana.setGeometry(200,200,400,200) #Posicion (x,y) ancho (350), alto (200)

#Diccionario de colores
colores = {
    "Rojo": "#ff4d4d",
    "Azul": "#4da6ff",
    "Verde": "#4dff88",
    "Negro": "#1c1c1c"
}

#Variable x de posicion del boton
x = 30

#Ciclo for para recorrer cada uno de los elementos de diccionario de colores
for nombre, hex_color in colores.items():
    boton = QPushButton(nombre, ventana)
    boton.move(x, 80)
    boton.clicked.connect(lambda _, c=hex_color: color(c, "yellow"))
    x+=80
    
#Mostrar ventana
ventana.show()
#Ejecutar app
sys.exit(app.exec()) 