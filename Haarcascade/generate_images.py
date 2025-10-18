import numpy as np
import cv2 as cv
import math 

rostro = cv.CascadeClassifier('Haarcascade\haarcascade_frontalface_alt2.xml')
cap = cv.VideoCapture('Haarcascade\korean.mp4')
#cap = cv.VideoCapture(0)
i = 0  
while True:
    ret, frame = cap.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    rostros = rostro.detectMultiScale(gray, 1.3, 5)
    for(x, y, w, h) in rostros:
       #frame = cv.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
       frame2 = frame[ y:y+h, x:x+w]
       #frame3 = frame[x+30:x+w-30, y+30:y+h-30]
       
       frame2 = cv.resize(frame2, (100, 100), interpolation=cv.INTER_AREA)
       
        
       if(i%2==0):
           cv.imwrite('Haarcascade/sentimientos-dataset/smile/smile'+str(i)+'.jpg', frame2)

           cv.imshow('rostro', frame2)
    cv.imshow('rostros', frame)
    i = i+1
    k = cv.waitKey(1)
    if k == 27:
        break
cap.release()
cv.destroyAllWindows()