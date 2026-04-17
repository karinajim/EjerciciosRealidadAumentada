#Importar caracteristicas de sistema
import sys
#Importo componentes graficos 
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

#cambiar color
def cambiar_color(marcado):
    if marcado:

        ventana.setStyleSheet("background-color: lightgreen; color:blue;")
    else:
        ventana.setStyleSheet("background-color: lightpink; color: black;")



#Funcion para calcular una suma
def calcular():
    try:
        a = float(caja1.text())
        b = float(caja2.text())
        resultado.setText(str(round(a+b,2)))
    except ValueError:
        resultado.setText("Error")

#Creo la aalicacion
app = QApplication(sys.argv)

#Ventana
ventana = QWidget()
ventana.setGeometry(200,200,300,220)
ventana.setWindowTitle("Minicalculadora")

#Cajas de texto
caja1 = QLineEdit(ventana) #Colocamos un argumento el contenedor
caja1.move(50,40)

caja2 = QLineEdit(ventana)
caja2.move(50,80)

#Boton 
boton = QPushButton("Sumar", ventana)
boton.move(50,120)
boton.clicked.connect(calcular)

#boton para cambiar color
btn_cambiar =QPushButton("Cambiar color", ventana)
btn_cambiar.move(150,120)
btn_cambiar.clicked.connect(cambiar_color)
btn_cambiar.setCheckable(True) #Hacer que el boton sea presionable

#Etiqueta de resultado
resultado = QLabel("Resultado", ventana)
resultado.move(180,70)

#Mostramos ventana
ventana.show()
sys.exit(app.exec())