import cv2 as cv 
import numpy as np 
import os
dataSet = 'Haarcascade//sentimientos-dataset'
faces  = os.listdir(dataSet)
print(faces)

labels = []
facesData = []
label = 0 
for face in faces:
    facePath = dataSet+'/'+face
    for faceName in os.listdir(facePath):
        labels.append(label)
        img = cv.imread(facePath+'/'+faceName, 0)
        img = cv.resize(img, (100, 100))  # Asegurar tamaño uniforme
        facesData.append(img)
    label = label + 1
print(np.count_nonzero(np.array(labels)==0)) 

faceRecognizer = cv.face.EigenFaceRecognizer_create()
faceRecognizer.train(facesData, np.array(labels))
faceRecognizer.write('Haarcascade\Eigenface-sentimientos.xml')