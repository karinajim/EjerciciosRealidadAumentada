#Control de Notas de Estudiantes
#Calcular promedio usando numpy
#Agregar columna “Promedio”
#Mostrar aprobados (>=6)
#Gráfica de histograma de notas

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
QApplication, QMainWindow, QPushButton,
QVBoxLayout, QWidget, QFileDialog, QTableWidget,
QTableWidgetItem, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2

class Ventana(QMainWindow): 
    """Control de Notas de Estudiantes Karina Cristal Carrillo Jimenez"""
    def __init__(self, parent=None):
    super().__init__(parent)
self.setWindowTitle("Control de Notas de Estudiantes")
self.boton = QPushButton("Cargar CSV")
self.boton.clicked.connect(self.cargar_datos)
self.label = QLabel("Resultados")
self.tabla = QTableWidget()
self.figura = Figure(figsize=(8,6))
self.canvas = FigureCanvas(self.figura)
layout = QVBoxLayout()
layout.addWidget(self.boton)
layout.addWidget(self.label)
layout.addWidget(self.tabla)
layout.addWidget(self.canvas)
contenedor = QWidget()
contenedor.setLayout(layout)
self.setCentralWidget(contenedor)
def cargar_datos(self):
archivo, _ = QFileDialog.getOpenFileName(self, "Abrir CSV",

"", "CSV (*.csv)")
if archivo:
df = pd.read_csv(archivo)
# Ejemplo numpy
promedio = np.mean(df.iloc[:,1])
self.label.setText(f"Promedio: {promedio}")
# Mostrar tabla
self.tabla.setRowCount(len(df))
self.tabla.setColumnCount(len(df.columns))
self.tabla.setHorizontalHeaderLabels(df.columns)

for i in range(len(df)):
for j in range(len(df.columns)):
self.tabla.setItem(i, j,

QTableWidgetItem(str(df.iat[i, j])))

# Gráfica
self.figura.clear()
ax = self.figura.add_subplot(111)
ax.plot(df.iloc[:,1])
self.canvas.draw()

app = QApplication(sys.argv)
ventana = Ventana()
ventana.show()
sys.exit(app.exec())