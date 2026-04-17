#Ejemplo prompts
prompts = ["Hola", "Dame un poema", "Explicame Python"]

for p in prompts:
    print(f"Procesando el prompt: {p}")

#Imprimir un rango de valores
for i in range(5):
    print(i)
    
#Tabla de multiplicar
for i in range(1,11):
    print(f"5x{i}={5*i}")
    
    
#Numero de 3 en 3 hastal 1000
for i in range(3, 1001, 3):
    print(i, end = ",")
print()
    
    
#Imprimir numeros nones hasta el 100
for i in range (1, 101):
    if i % 2 != 1:
        print(i, end=" ")
    
    
    
#Imprimir numeros nones hasta el 100
for i in range (1, 101):
    if i % 2 == 0:
        print(i, end=" ")