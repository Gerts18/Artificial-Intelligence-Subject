# SEGMENTA POR COLOR LAS FIGURAS DE UNA IMAGEN
# OBTENER LAS COORDENADAS DE CADA IMAGEN

#ESCOGER UN COLOR, MARCAR LA POSICION DE CADA UNO

import cv2 as cv

img = cv.imread('figura.png', 1)
#img2 = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

ubb = (170, 60, 60)
uba = (180, 255, 255)

mascara = cv.inRange(hsv, ubb, uba)

resultado = cv.bitwise_and(img, img, mask=mascara)

contornos, _ = cv.findContours(mascara, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

img_con_circulos = resultado.copy()

for contorno in contornos:
    puntos_coordenadas = contorno[:, 0, :]
    # Dibujar círculos en cada coordenada del contorno
    for punto in puntos_coordenadas:
        x, y = punto
        cv.circle(img_con_circulos, (x, y), radius=3, color=(255, 0, 0), thickness=-1)
    print("Coordenadas del contorno:", puntos_coordenadas)

cv.imshow('contornos', img_con_circulos)
cv.imshow('resultado', resultado)
cv.imshow('mascara1', mascara)
cv.imshow('img', img)


cv.waitKey(0)
cv.destroyAllWindows()