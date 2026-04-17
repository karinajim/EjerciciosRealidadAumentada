score = 0.85 #Nivel de confianza

if score > 0.90:
    print("Es seguro")
elif score > 0.70:
    print("Medianamente seguro")
else:
    print("Mejor pregunto al usuario, no estoy seguro")
    
#Declara una variable llamada edad y dependiendo de ella clasifica en:
#niño cuando edad <15, joven < 25,
#adulto <45 y adulto mayor 

edad = 300
if edad <0 or edad > 125:
    print("Edad no valida")
elif edad < 15:
    print("Es niño")
elif edad <25:
    print ("Es joven")
elif edad <45:
    print ("Es adulto")
else: 
    print("Adulto mayor")