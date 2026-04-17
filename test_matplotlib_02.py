#Importamos matplotlib
import matplotlib.pyplot as plt
import numpy as np 

#Datos resumidos usando Numpy 
gasto_ahorradores = [10,15,20,25,30,12,18]
ahorro_ahorradores =[80,85,70,90,95,88,75]

#Datos de compradores
gasto_compradores = [70,80,90,85,95,75,88]
ahorro_compradores = [20,15,10,25,5,18,12]

#Dibujamos un grafico de puntos
plt.figure(figsize=(8,5)) #Tamaño de la ventana 

plt.scatter(gasto_ahorradores, ahorro_ahorradores, color ='blue', label="Ahorradores", s=100, edgecolors= 'black')

plt.scatter(gasto_compradores, ahorro_compradores, color ='red', label="Compradores", s=100, edgecolors= 'black', marker="s")
plt.title("Segmentacion de Clientes por IA", fontsize= 20)
plt.xlabel("Nivel de Gasto ($), fontsize=14")
plt.ylabel("Nivel de Ahorro ($), fontsize=14")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()