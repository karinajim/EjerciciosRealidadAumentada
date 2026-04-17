import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget, QFileDialog, QTableWidget,
    QTableWidgetItem, QLabel, QHBoxLayout, QTextEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Notas de Estudiantes")
        self.setGeometry(100, 100, 800, 600)
        
        # Widgets principales
        self.boton_cargar = QPushButton("Cargar CSV")
        self.boton_cargar.clicked.connect(self.cargar_datos)
        
        self.boton_aprobados = QPushButton("Mostrar Aprobados")
        self.boton_aprobados.clicked.connect(self.mostrar_aprobados)
        self.boton_aprobados.setEnabled(False)
        
        self.label_titulo = QLabel("Resultados")
        self.label_titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.label_info = QLabel("")
        self.label_info.setStyleSheet("font-size: 12px; color: blue;")
        
        self.tabla = QTableWidget()
        self.texto_resultados = QTextEdit()
        self.texto_resultados.setMaximumHeight(100)
        self.texto_resultados.setReadOnly(True)
        
        # Configurar gráfica
        self.figura = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figura)
        
        # Layouts
        layout_botones = QHBoxLayout()
        layout_botones.addWidget(self.boton_cargar)
        layout_botones.addWidget(self.boton_aprobados)
        layout_botones.addStretch()
        
        layout_principal = QVBoxLayout()
        layout_principal.addLayout(layout_botones)
        layout_principal.addWidget(self.label_titulo)
        layout_principal.addWidget(self.label_info)
        layout_principal.addWidget(self.tabla)
        layout_principal.addWidget(self.texto_resultados)
        layout_principal.addWidget(self.canvas)
        
        contenedor = QWidget()
        contenedor.setLayout(layout_principal)
        self.setCentralWidget(contenedor)
        
        self.df = None
    
    def cargar_datos(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir CSV", "", "CSV (*.csv)")
        if archivo:
            try:
                # Cargar datos
                self.df = pd.read_csv(archivo)
                
                # Calcular promedio usando numpy
                notas = self.df.iloc[:, 1:4].values  # Nota1, Nota2, Nota3
                promedios = np.mean(notas, axis=1)
                
                # Agregar columna "Promedio"
                self.df['Promedio'] = np.round(promedios, 2)
                
                # Calcular estadísticas generales
                promedio_general = np.mean(promedios)
                nota_max = np.max(notas)
                nota_min = np.min(notas)
                
                # Actualizar label de información
                self.label_info.setText(
                    f"Promedio General: {promedio_general:.2f} | "
                    f"Nota Máxima: {nota_max:.2f} | "
                    f"Nota Mínima: {nota_min:.2f}"
                )
                
                # Mostrar tabla completa
                self.mostrar_tabla(self.df)
                
                # Generar histograma
                self.generar_histograma(notas.flatten())
                
                # Habilitar botón de aprobados
                self.boton_aprobados.setEnabled(True)
                
                # Mostrar mensaje en el área de texto
                self.texto_resultados.setText("Datos cargados correctamente. Se ha agregado la columna 'Promedio'.")
                
            except Exception as e:
                self.texto_resultados.setText(f"Error al cargar el archivo: {str(e)}")
    
    def mostrar_tabla(self, df):
        """Muestra el DataFrame en la tabla"""
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns)
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iat[i, j]))
                # Resaltar promedios >= 6 (aprobados)
                if df.columns[j] == 'Promedio' and df.iat[i, j] >= 6:
                    item.setBackground(QTableWidgetItem().background())
                    item.setForeground(QTableWidgetItem().foreground())
                self.tabla.setItem(i, j, item)
        
        # Ajustar columnas
        self.tabla.resizeColumnsToContents()
    
    def mostrar_aprobados(self):
        """Muestra solo los estudiantes aprobados (promedio >= 6)"""
        if self.df is not None:
            aprobados = self.df[self.df['Promedio'] >= 6]
            
            if len(aprobados) > 0:
                self.mostrar_tabla(aprobados)
                self.texto_resultados.setText(
                    f" {len(aprobados)} estudiantes aprobados (promedio >= 6):\n"
                    f"{aprobados[['Estudiante', 'Promedio']].to_string(index=False)}"
                )
            else:
                self.texto_resultados.setText(" No hay estudiantes aprobados")
    
    def generar_histograma(self, notas):
        """Genera un histograma de las notas"""
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        
        # Crear histograma
        ax.hist(notas, bins=10, edgecolor='black', alpha=0.7, color='skyblue')
        ax.set_xlabel('Notas')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Histograma de Notas')
        ax.grid(True, alpha=0.3)
        
        # Línea vertical para el promedio general
        if self.df is not None:
            promedio_general = np.mean(self.df['Promedio'])
            ax.axvline(promedio_general, color='red', linestyle='dashed', 
                      linewidth=2, label=f'Promedio: {promedio_general:.2f}')
            ax.legend()
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())