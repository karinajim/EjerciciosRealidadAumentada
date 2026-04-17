import cv2
import numpy as np

def mostrar_valor_pixel(evento, x, y, flags, param):
    # (mismo callback que arriba)
    pass

def main():
    imagen = cv2.imread('test.jpg')
    if imagen is None:
        imagen = np.zeros((400, 600, 3), dtype=np.uint8)
        for i in range(400):
            for j in range(600):
                imagen[i, j] = [j % 256, i % 256, (i+j) % 256]

    cv2.namedWindow('Visor')
    cv2.setMouseCallback('Visor', mostrar_valor_pixel, imagen)

    modo = 'completa'  # completa, azul, verde, rojo

    while True:
        if modo == 'azul':
            frame = np.zeros_like(imagen)
            frame[:, :, 0] = imagen[:, :, 0]
        elif modo == 'verde':
            frame = np.zeros_like(imagen)
            frame[:, :, 1] = imagen[:, :, 1]
        elif modo == 'rojo':
            frame = np.zeros_like(imagen)
            frame[:, :, 2] = imagen[:, :, 2]
        else:
            frame = imagen

        cv2.imshow('Visor', frame)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord('1'):
            modo = 'azul'
        elif tecla == ord('2'):
            modo = 'verde'
        elif tecla == ord('3'):
            modo = 'rojo'
        elif tecla == ord('4'):
            modo = 'completa'
        elif tecla == ord('q') or tecla == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()