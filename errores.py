#Bloque try -except 
try: 
    #Intentar realizar la instrucción 
    resultado = 10 / 0  #Causa error
except Exception as e: 
    print(f"Hubo un error: {e}. Pero el programa sirve vivo.")
finally:
    print("Sigo vivo otra vez")