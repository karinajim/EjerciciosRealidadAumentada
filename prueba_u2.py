import sys
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel,
                             QFileDialog, QMessageBox, QHeaderView, QGroupBox,
                             QFormLayout, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CanvasNotas(FigureCanvas):
    """Canvas personalizado para gráficas de Matplotlib"""
    def __init__(self, parent=None):
        self.figura = Figure(figsize=(8, 6))
        super().__init__(self.figura)

class ControlNotas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_notas = None
        self.initUI()
        
    def initUI(self):
        """Configura la interfaz principal"""
        self.setWindowTitle("Control de Notas de Estudiantes")
        self.setGeometry(100, 100, 1200, 700)
        
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        
        # Barra de herramientas superior
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
        
        # Tabs principales
        self.tabs = QTabWidget()
        layout_principal.addWidget(self.tabs)
        
        self.init_tab_notas()
        self.init_tab_estadisticas()
        self.init_tab_visualizaciones()
        
    def init_tab_notas(self):
        """Pestaña de notas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.tabla_notas = QTableWidget()
        self.tabla_notas.setSortingEnabled(True)
        layout.addWidget(QLabel("Notas de Estudiantes:"))
        layout.addWidget(self.tabla_notas)
        
        self.tabs.addTab(tab, "Notas")
        
    def init_tab_estadisticas(self):
        """Pestaña de estadísticas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.stats_group = QGroupBox("Estadísticas Generales")
        form_layout = QFormLayout()
        
        self.lbl_total_estudiantes = QLabel("0")
        self.lbl_aprobados = QLabel("0")
        self.lbl_reprobados = QLabel("0")
        self.lbl_promedio_general = QLabel("0.00")
        self.lbl_nota_maxima = QLabel("0.00")
        self.lbl_nota_minima = QLabel("0.00")
        
        form_layout.addRow("Total estudiantes:", self.lbl_total_estudiantes)
        form_layout.addRow("Aprobados (≥6):", self.lbl_aprobados)
        form_layout.addRow("Reprobados (<6):", self.lbl_reprobados)
        form_layout.addRow("Promedio general:", self.lbl_promedio_general)
        form_layout.addRow("Nota máxima:", self.lbl_nota_maxima)
        form_layout.addRow("Nota mínima:", self.lbl_nota_minima)
        
        self.stats_group.setLayout(form_layout)
        layout.addWidget(self.stats_group)
        
        self.txt_aprobados = QTextEdit()
        self.txt_aprobados.setReadOnly(True)
        layout.addWidget(QLabel("✓ Estudiantes Aprobados:"))
        layout.addWidget(self.txt_aprobados)
        
        self.tabs.addTab(tab, "Estadísticas")
        
    def init_tab_visualizaciones(self):
        """Pestaña de visualizaciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("Histograma de Notas:"))
        self.canvas_histograma = CanvasNotas()
        layout.addWidget(self.canvas_histograma)
        
        self.tabs.addTab(tab, "Visualizaciones")
        
    def cargar_archivo(self):
        """Carga el archivo CSV de notas"""
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo CSV", "", "Archivos CSV (*.csv)")
        
        if archivo:
            try:
                self.df_notas = pd.read_csv(archivo)
                
                # Validar columnas requeridas
                columnas_requeridas = ['Estudiante', 'Nota1', 'Nota2', 'Nota3']
                if not all(col in self.df_notas.columns for col in columnas_requeridas):
                    QMessageBox.critical(self, "Error", 
                        "El CSV debe contener: Estudiante, Nota1, Nota2, Nota3")
                    return
                
                # Calcular promedio con numpy
                notas = self.df_notas[['Nota1', 'Nota2', 'Nota3']].values
                promedios = np.mean(notas, axis=1)
                self.df_notas['Promedio'] = np.round(promedios, 2)
                
                # Determinar estado (aprobado/reprobado)
                self.df_notas['Estado'] = self.df_notas['Promedio'].apply(
                    lambda x: 'Aprobado' if x >= 6 else 'Reprobado')
                
                # Actualizar tabla
                self.actualizar_tabla_notas()
                self.actualizar_estadisticas()
                self.actualizar_histograma()
                
                QMessageBox.information(self, "Éxito", "Archivo cargado correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar archivo: {str(e)}")
    
    def actualizar_tabla_notas(self):
        """Actualiza la tabla de notas con colores según estado"""
        if self.df_notas is None:
            return
            
        self.tabla_notas.setRowCount(len(self.df_notas))
        self.tabla_notas.setColumnCount(6)
        self.tabla_notas.setHorizontalHeaderLabels(
            ["Estudiante", "Nota1", "Nota2", "Nota3", "Promedio", "Estado"])
        
        for i, (idx, row) in enumerate(self.df_notas.iterrows()):
            items = [
                QTableWidgetItem(str(row['Estudiante'])),
                QTableWidgetItem(str(row['Nota1'])),
                QTableWidgetItem(str(row['Nota2'])),
                QTableWidgetItem(str(row['Nota3'])),
                QTableWidgetItem(str(row['Promedio'])),
                QTableWidgetItem(str(row['Estado']))
            ]
            
            # Colorear según estado
            color = QColor(200, 255, 200) if row['Estado'] == 'Aprobado' else QColor(255, 200, 200)
            for j, item in enumerate(items):
                item.setBackground(QBrush(color))
                self.tabla_notas.setItem(i, j, item)
        
        self.tabla_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas generales"""
        if self.df_notas is None:
            return
        
        total = len(self.df_notas)
        aprobados = len(self.df_notas[self.df_notas['Estado'] == 'Aprobado'])
        reprobados = total - aprobados
        promedio_general = np.mean(self.df_notas['Promedio'])
        nota_maxima = np.max(self.df_notas['Promedio'])
        nota_minima = np.min(self.df_notas['Promedio'])
        
        self.lbl_total_estudiantes.setText(str(total))
        self.lbl_aprobados.setText(f"{aprobados} ({aprobados/total*100:.1f}%)")
        self.lbl_reprobados.setText(f"{reprobados} ({reprobados/total*100:.1f}%)")
        self.lbl_promedio_general.setText(f"{promedio_general:.2f}")
        self.lbl_nota_maxima.setText(f"{nota_maxima:.2f}")
        self.lbl_nota_minima.setText(f"{nota_minima:.2f}")
        
        # Lista de aprobados
        aprobados_list = self.df_notas[self.df_notas['Estado'] == 'Aprobado']
        texto = "\n".join([f"• {row['Estudiante']}: {row['Promedio']}" 
                          for _, row in aprobados_list.iterrows()])
        self.txt_aprobados.setText(texto if texto else "No hay estudiantes aprobados")
    
    def actualizar_histograma(self):
        """Genera histograma de notas"""
        if self.df_notas is None:
            return
        
        self.canvas_histograma.figura.clear()
        ax = self.canvas_histograma.figura.add_subplot(111)
        
        # Histograma de todos los promedios
        ax.hist(self.df_notas['Promedio'], bins=10, color='#4CAF50', edgecolor='black', alpha=0.7)
        ax.axvline(6, color='red', linestyle='--', linewidth=2, label='Nota mínima aprobatoria')
        ax.set_xlabel('Promedio')
        ax.set_ylabel('Cantidad de estudiantes')
        ax.set_title('Distribución de Notas')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        self.canvas_histograma.draw()

def main():
    app = QApplication(sys.argv)
    ventana = ControlNotas()
    ventana.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
