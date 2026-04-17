import sys # Importa el módulo 'sys' que proporciona acceso a variables y funciones específicas del sistema.
import pandas as pd #Pandas es una biblioteca para manipulación y análisis de datos.
import numpy as np # NumPy es una biblioteca para operaciones matemáticas y numéricas.
import matplotlib.pyplot as plt # Importa pyplot de matplotlib. Es una biblioteca para crear visualizaciones y gráficas.

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget, QFileDialog,
    QTableWidget, QTableWidgetItem, QLabel
)


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# Importa el canvas de matplotlib para integrar gráficas en Qt.
# FigureCanvas es el widget que contendrá la figura de matplotlib.

from matplotlib.figure import Figure
# Importa la clase Figure de matplotlib que representa la figura/gráfica.

class Ventana(QMainWindow):
    # Define una clase llamada 'Ventana' que hereda de QMainWindow.
    # Esta clase contendrá toda la interfaz gráfica.

    def __init__(self):
        # Método constructor que se ejecuta al crear una instancia de la clase.
        # Inicializa todos los componentes de la ventana.
        
        super().__init__()
        # Llama al constructor de la clase padre (QMainWindow) para inicializar correctamente.
        
        self.setWindowTitle("Control de Energía")
        # Establece el título de la ventana principal.
        
        self.setGeometry(100, 100, 900, 600)
        # Define la posición y tamaño de la ventana:
        # 100px desde la izquierda, 100px desde arriba, 900px de ancho, 600px de alto.

        self.boton = QPushButton("Cargar CSV")
        # Crea un botón con el texto "Cargar CSV" y lo guarda como atributo de la clase.
        
        self.boton.clicked.connect(self.cargar_datos)
        # Conecta la señal 'clicked' del botón al método 'cargar_datos'.
        # Cuando se haga clic en el botón, se ejecutará el método cargar_datos.

        self.label = QLabel("Resultados")
        # Crea una etiqueta con el texto "Resultados" que mostrará los resultados.

        self.tabla = QTableWidget()
        # Crea una tabla vacía donde se mostrarán los datos del CSV.
        
        self.figura = Figure()
        # Crea una figura de matplotlib donde se dibujará la gráfica.
        
        self.canvas = FigureCanvas(self.figura)
        # Crea un canvas de Qt que contiene la figura de matplotlib.
        # Esto permite mostrar la gráfica dentro de la interfaz Qt.

        layout = QVBoxLayout()
        # Crea un layout vertical que organizará los widgets de arriba a abajo.
        
        layout.addWidget(self.boton)
        # Añade el botón al layout vertical.
        
        layout.addWidget(self.label)
        # Añade la etiqueta al layout vertical.
        
        layout.addWidget(self.tabla)
        # Añade la tabla al layout vertical.
        
        layout.addWidget(self.canvas)
        # Añade el canvas (gráfica) al layout vertical.

        contenedor = QWidget()
        # Crea un widget contenedor que servirá como base para el layout.
        
        contenedor.setLayout(layout)
        # Asigna el layout vertical al widget contenedor.
        
        self.setCentralWidget(contenedor)
        # Establece el contenedor como el widget central de la ventana principal.
    
    def cargar_datos(self):
        # Método que se ejecuta al hacer clic en el botón "Cargar CSV".
        # Contiene toda la lógica para leer, procesar y mostrar los datos.
        
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir CSV", "", "CSV (*.csv)")
        # Abre un diálogo para seleccionar un archivo CSV.
        # Retorna la ruta del archivo seleccionado y un filtro (que ignoramos con _). ARGMAX PARA CALCULAR QUE DIA FUE MAYOR EL CONSUMO
        
        if archivo:
            # Verifica si se seleccionó un archivo (si archivo no está vacío).
            
            df = pd.read_csv(archivo)
            # Lee el archivo CSV usando pandas y lo convierte en un DataFrame.
            # df es una estructura de datos tabular.
            
            suma = np.sum(df["Consumo_kWh"])        

            promedio = np.mean(df["Consumo_kWh"])
            # Calcula el promedio de la columna "Consumo_kWh" usando numpy.
            
            maximo = np.max(df["Consumo_kWh"])
            # Encuentra el valor máximo en la columna "Consumo_kWh".
            
            

            idx_max = df["Consumo_kWh"].argmax()
            # Encuentra el índice (fila) donde está el valor máximo.
            
            dia_max = df.iloc[idx_max]["Dia"]
            # Obtiene el valor de la columna "Dia" en la fila del índice máximo.
            # .iloc accede a la fila por posición.
            
            #suma
            

            self.label.setText(
                f"Promedio Consumo: {promedio:.2f} kWh\n"
                f"Día con mayor consumo: {dia_max} ({maximo} kWh) ({suma} kWh)"
                f"Suma total: {suma} kWh/n"
            )
            # Actualiza el texto de la etiqueta con los resultados calculados.
            # {promedio:.2f} muestra el promedio con 2 decimales.
            # \n es un salto de línea.

            self.tabla.setRowCount(len(df))
            # Establece el número de filas de la tabla igual al número de filas del DataFrame.
            
            self.tabla.setColumnCount(len(df.columns))
            # Establece el número de columnas igual al número de columnas del DataFrame.
            
            self.tabla.setHorizontalHeaderLabels(df.columns)
            # Establece los encabezados de las columnas usando los nombres de las columnas del DataFrame.

            for i in range(len(df)):
                # Bucle para recorrer cada fila del DataFrame.
                for j in range(len(df.columns)):
                    # Bucle para recorrer cada columna del DataFrame.
                    
                    self.tabla.setItem(i, j,
                        QTableWidgetItem(str(df.iat[i, j]))
                    )
                    # Crea un item de tabla con el valor de la celda (convertido a string)
                    # y lo coloca en la posición [i, j] de la tabla.
                    # .iat accede al valor por posición [fila, columna].

            self.figura.clear()
            # Limpia la figura actual para dibujar una nueva gráfica.
            
            ax = self.figura.add_subplot(111)
            
            # Crea un eje (subplot) en la figura.
            # 111 significa: 1 fila, 1 columna, posición 1 (una sola gráfica).

            ax.bar(df["Dia"], df["Consumo_kWh"])
            # Dibuja una línea en el eje x (Día) vs eje y (Consumo_kWh).
            # marker="o" añade círculos en cada punto de datos.

            ax.set_title("Consumo de Energía por Día")
            # Establece el título de la gráfica.
            
            ax.set_xlabel("Día")
            # Establece la etiqueta del eje X.
            
            ax.set_ylabel("Consumo (kWh)")
            # Establece la etiqueta del eje Y.
            
            self.canvas.draw()
            # Actualiza el canvas para mostrar la nueva gráfica.

if __name__ == "__main__":
    # Este bloque solo se ejecuta si el script se ejecuta directamente
    # (no cuando se importa como módulo).
    
    app = QApplication(sys.argv)
    # Crea la aplicación Qt. sys.argv pasa los argumentos de línea de comandos.
    
    ventana = Ventana()
    # Crea una instancia de la clase Ventana.
    
    ventana.show()
    # Muestra la ventana en pantalla.
    
    sys.exit(app.exec())
    # Ejecuta el bucle principal de la aplicación.
    # app.exec() inicia el bucle de eventos de Qt.
    # sys.exit() asegura que el programa termine correctamente cuando se cierra la ventana.