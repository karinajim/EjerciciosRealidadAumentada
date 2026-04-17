import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QComboBox, QGroupBox
)

from PyQt6.QtCore import Qt

# Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# ==============================
# Canvas de Matplotlib
# ==============================
class CanvasMatplotlib(FigureCanvas):

    def __init__(self):
        self.figura = Figure(figsize=(8, 5), dpi=100)
        self.ejes = self.figura.add_subplot(111)
        super().__init__(self.figura)
        self.figura.tight_layout()

    def graficar_linea(self, x, y, titulo="Grafica de linea"):
        self.ejes.clear()

        self.ejes.plot(x, y, 'b-', linewidth=2, marker='o')

        self.ejes.set_title(titulo, fontsize=14, fontweight='bold')
        self.ejes.set_xlabel('Eje X', fontsize=12)
        self.ejes.set_ylabel('Eje Y', fontsize=12)
        self.ejes.grid(True, alpha=0.3)

        self.draw()

    def graficar_barras(self, categorias, valores, titulo="Grafica de barras"):
        self.ejes.clear()

        colores = ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        barras = self.ejes.bar(
            categorias,
            valores,
            color=colores[:len(valores)]
        )

        self.ejes.set_title(titulo, fontsize=14, fontweight='bold')
        self.ejes.set_ylabel('Valores', fontsize=12)

        for barra in barras:
            altura = barra.get_height()
            self.ejes.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f'{altura:.1f}',
                ha='center',
                va='bottom'
            )

        self.draw()

    def graficar_dispersion(self, x, y, titulo='Gráfica de Dispersión'):
        self.ejes.clear()

        self.ejes.scatter(x, y, s=100, alpha=0.6, color='#2563eb')

        self.ejes.set_title(titulo, fontsize=14, fontweight='bold')
        self.ejes.set_xlabel('Eje X', fontsize=12)
        self.ejes.set_ylabel('Eje Y', fontsize=12)
        self.ejes.grid(True, alpha=0.3)

        self.draw()


# ==============================
# Ventana Principal
# ==============================
class VentanaGraficas(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('📈 Gráficas con Matplotlib')
        self.setGeometry(100, 100, 1000, 700)

        self.inicializar_interfaz()

    def inicializar_interfaz(self):

        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout_principal = QVBoxLayout()
        widget_central.setLayout(layout_principal)

        # ===== Controles =====
        grupo_controles = QGroupBox('⚙️ Controles')
        layout_controles = QHBoxLayout()
        grupo_controles.setLayout(layout_controles)

        layout_controles.addWidget(QLabel('Tipo de gráfica:'))

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(['Línea', 'Barras', 'Dispersión'])
        self.combo_tipo.currentTextChanged.connect(self.actualizar_grafica)
        layout_controles.addWidget(self.combo_tipo)

        layout_controles.addWidget(QLabel('Puntos:'))

        self.slider_puntos = QSlider(Qt.Orientation.Horizontal)
        self.slider_puntos.setMinimum(5)
        self.slider_puntos.setMaximum(50)
        self.slider_puntos.setValue(10)
        self.slider_puntos.valueChanged.connect(self.actualizar_grafica)
        layout_controles.addWidget(self.slider_puntos)

        self.label_puntos = QLabel('10')
        layout_controles.addWidget(self.label_puntos)

        boton_actualizar = QPushButton('🔄 Actualizar')
        boton_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        boton_actualizar.clicked.connect(self.actualizar_grafica)
        layout_controles.addWidget(boton_actualizar)

        layout_principal.addWidget(grupo_controles)

        # ===== Gráfica =====
        grupo_grafica = QGroupBox('📊 Visualización')
        layout_grafica = QVBoxLayout()
        grupo_grafica.setLayout(layout_grafica)

        self.canvas = CanvasMatplotlib()
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout_grafica.addWidget(self.toolbar)
        layout_grafica.addWidget(self.canvas)

        layout_principal.addWidget(grupo_grafica)

        self.actualizar_grafica()

    def actualizar_grafica(self):

        n_puntos = self.slider_puntos.value()
        self.label_puntos.setText(str(n_puntos))

        tipo = self.combo_tipo.currentText()

        x = np.linspace(0, 10, n_puntos)
        y = np.sin(x) * 2 + np.random.randn(n_puntos) * 0.3

        if tipo == 'Línea':
            self.canvas.graficar_linea(
                x, y,
                f'Gráfica de Línea ({n_puntos} puntos)'
            )

        elif tipo == 'Barras':
            categorias = [f'Cat {i+1}' for i in range(min(n_puntos, 10))]
            valores = np.abs(y[:len(categorias)])
            self.canvas.graficar_barras(
                categorias,
                valores,
                'Gráfica de Barras'
            )

        elif tipo == 'Dispersión':
            self.canvas.graficar_dispersion(
                x, y,
                f'Gráfica de Dispersión ({n_puntos} puntos)'
            )


# ==============================
# Ejecutar
# ==============================
def main():
    app = QApplication(sys.argv)
    ventana = VentanaGraficas()
    ventana.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()