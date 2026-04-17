# generar_datos.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Generar datos de estudiantes y notas
estudiantes = ['Juan Pérez', 'María González', 'Carlos López', 'Ana Martínez',
               'Luis Rodríguez', 'Carmen Silva', 'Pedro Torres', 'Laura Ramírez',
               'Roberto Díaz', 'Sofía Castro', 'Miguel Vega', 'Patricia Luna',
               'Fernando Ruiz', 'Gabriela Soto', 'Alejandro Mora']

print("🎓 Generando datos de estudiantes...")

datos_notas = []
for estudiante in estudiantes:
    # Generar notas aleatorias entre 1 y 10
    nota1 = np.random.randint(1, 11)
    nota2 = np.random.randint(1, 11)
    nota3 = np.random.randint(1, 11)
    
    datos_notas.append({
        'Estudiante': estudiante,
        'Nota1': nota1,
        'Nota2': nota2,
        'Nota3': nota3
    })

# Crear DataFrame
df_notas = pd.DataFrame(datos_notas)

# Calcular promedio usando numpy
promedios = np.mean(df_notas[['Nota1', 'Nota2', 'Nota3']], axis=1)
df_notas['Promedio'] = np.round(promedios, 2)

# Guardar CSV
df_notas.to_csv('notas_estudiantes.csv', index=False)

# Estadísticas
aprobados = df_notas[df_notas['Promedio'] >= 6]
reprobados = df_notas[df_notas['Promedio'] < 6]
promedio_general = np.mean(df_notas['Promedio'])
nota_maxima = np.max(df_notas[['Nota1', 'Nota2', 'Nota3']].values)
nota_minima = np.min(df_notas[['Nota1', 'Nota2', 'Nota3']].values)

print("\n Archivo 'notas_estudiantes.csv' generado correctamente")
print(f" Total de estudiantes: {len(df_notas)}")
print(f" Promedio general: {promedio_general:.2f}")
print(f" Nota máxima: {nota_maxima}")
print(f" Nota mínima: {nota_minima}")
print(f" Aprobados: {len(aprobados)} ({len(aprobados)/len(df_notas)*100:.1f}%)")
print(f" Reprobados: {len(reprobados)} ({len(reprobados)/len(df_notas)*100:.1f}%)")

print("\n rimeros 5 registros:")
print(df_notas.head())

print("\n Estudiantes aprobados:")
print(aprobados[['Estudiante', 'Promedio']].to_string(index=False))

# Generar histograma
print("\n Generando histograma...")
plt.figure(figsize=(10, 6))
plt.hist(df_notas[['Nota1', 'Nota2', 'Nota3']].values.flatten(), 
         bins=10, 
         edgecolor='black', 
         color='skyblue',
         alpha=0.7,
         range=(0, 10))
plt.axvline(6, color='red', linestyle='dashed', linewidth=2, label='Mínimo aprobatorio (6)')
plt.axvline(promedio_general, color='green', linestyle='dashed', linewidth=2, label=f'Promedio general ({promedio_general:.2f})')
plt.xlabel('Notas')
plt.ylabel('Frecuencia')
plt.title('Histograma de Notas de Estudiantes')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('histograma_notas.png', dpi=300, bbox_inches='tight')
plt.show()

print("Histograma guardado como 'histograma_notas.png'")