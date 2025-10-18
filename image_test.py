import cv2 as cv
import numpy as np 
#c:\\home\\misdatos\\imagen.jpg
img = cv.imread("colorful.jpg",1)
#print(img.shape[:2])
img2 = np.zeros(img.shape[:2], np.uint8) # Crea una imagen negra
b,g,r=cv.split(img) # Separa los canales
b1=cv.merge([b, img2, img2]) #Fusiona los canales
g1=cv.merge([img2, g, img2])
r1=cv.merge([img2, img2, r])
res1 = cv.merge([g,r,b])
cv.imshow('res1', res1) # Muestra la imagen fusionada
cv.imshow('b', b)
cv.imshow('g', g)
cv.imshow('r', r)
cv.imshow('b1', b1)
cv.imshow('g1', g1)
cv.imshow('r1', r1)
cv.imshow('marco2', img2)
cv.imshow('marco', img)
cv.waitKey(0)
cv.destroyAllWindows()
