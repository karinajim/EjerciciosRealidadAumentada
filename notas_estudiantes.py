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
QTableWidgetItem, QLabel, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CanvasAsistencia(FigureCanvas):
    """"Asistencia de Estudiantes Karina Cristal Carrillo Jimenez"""
    def __init__(self, figure=None):
        super().__init__(self.figure)

class ControlNotas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_notas = None
        self.initUI()
        
        
def initUI(self):
        """Control de notas de estudiantes"""
    self.setWindowTitle("Aplicación de Datos, Control de Notas de Estudiantes")
    self.setGeometry(100,100,1400,800)
    # Widget central y layout principal
        widget_central = QWidget()
    self.setCentralWidget(widget_central)
    layout_principal = QVBoxLayout(widget_central)
        
#Barra de herramienta para cargar archivo CSV
    toolbar = QHBoxLayout()
    self.btn_cargar = QPushButton("Cargar CSV")
    self.btn_cargar.clicked.connect(self.cargar_archivo)
    self.btn_cargar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
    toolbar.addWidget(self.btn_cargar)
    toolbar.addStretch()
    layout_principal.addLayout(toolbar)
        
        self.boton.clicked.connect(self.cargar_datos)
        self.label = QLabel("Resultados")
        self.tabla = QTableWidget()
        self.figura = Figure()
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