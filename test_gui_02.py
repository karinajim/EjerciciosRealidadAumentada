#Importar caracteristicas de sistema
import sys

#Importamos componentes graficos del Framework PyQt
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton

#Variable entera que incrementera en el programa
puntos = 0

#Funion que suma 1 a puntos y lo coloque en pantalla
def sumar():
    global puntos 
    puntos += 1
    etiqueta.setText(f"Puntos: {puntos}")
    
#Crear aplicacion 
app = QApplication(sys.argv)
#Creo ventana 
ventana = QWidget()
ventana.setGeometry(200,200, 300,200) #Punto(x,y) AnchoYAlto(300,200)

#Creo etiqueta 
etiqueta = QLabel("Puntos:  0 ", ventana) #Colocamos texto y el contenedor 
etiqueta.move(120,40) #Posicion dentro del contenedor(x,y)

#Creo un boton
boton = QPushButton("Sumar +1", ventana) #Texto, contenedor 
boton.move(100,100) #Posicion (x,y)
boton.clicked.connect(sumar) #conectamos el evento presionado con una funcion 

#Funcion que resta 1 a puntos
def restar():
    global puntos
    if puntos > 0:
        puntos -= 1
    etiqueta.setText(f"Puntos: {puntos}")

#Creo un boton para restar
boton_restar = QPushButton("Restar -1", ventana)
boton_restar.move(100, 150)
boton_restar.clicked.connect(restar)

#Mostrar ventana
ventana.show()
#Ejecutar la app
sys.exit(app.exec())