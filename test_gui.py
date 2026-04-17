# Importar modulo que me permite trabajar con objetos del sistema 
import sys 

#Importar componentes graficos que nos permitan trabajar dentro de ventanas 
from PyQt6.QtWidgets import QApplication, QWidget, QLabel 

# Crea una aplicacion
app = QApplication(sys.argv)

#Creanmos una ventana 
ventana = QWidget()
ventana.setWindowTitle("Mi  primera app en PyQt") # Titulo de la ventana
ventana.setGeometry(200,200,400,250) #Dimensiones a la ventana

texto = QLabel("Hola Karina Cristal Carrillo Jimenez", ventana) #Creo un texto y lo coloco dentro de la ventana
texto.move(100, 70) #posiciono mi texto en un punto de la ventana

ventana.show() #Muestra la ventana
sys.exit(app.exec())