import os
import re
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, LeakyReLU, Input
from keras.callbacks import EarlyStopping
import keras

"""
Una CNN guarda los conocimientos en la matriz de convolucion, generalmente al inicio tengo 32 filtros/kernel de convolucion para la primer capa, despues 64 y asi dependiendo del tamaño de la imagen.

RAG vs Fine-tunning
RAG es cuando solo se va a usar la informacion para que el modelo haga analisis atraves del corpus, para buscar informacion.
Finetunning, cuando quieres aplicarle estilo y forma de responder propio al modelo.

Lo que se busca al aplicar filtros/max pulling es reducir los pesos sinapticos y su dimensionalidad extrayendo la mayor cantidad de caracteristicas de los datos.

Con pregunta/respuesta le estamos dando ejemplos de como deberia responder el modelo. 

Soft-max sirve para diferenciar las clases que estoy viendo. A traves de softmax obtengo la probabilidad de que mi imagen de entrada pertenece a alguna de las clases que tengo.

El peso sinaptico se guarda en las matrices de convolucion. 

El dropout ayuda a evitar el sobreajuste. 

"""

# ----------------------------------------------------------------
# PASO 1: Cargar las imágenes
# ----------------------------------------------------------------

dirname = os.path.join(os.getcwd(), 'CNN_ejemplo/animals-dataset')
imgpath = dirname + os.sep

images = []
directories = []
dircount = []
prevRoot = ''
cant = 0

print("leyendo imagenes de ", imgpath)

for root, dirnames, filenames in os.walk(imgpath):
    for filename in filenames:
        if re.search("\.(jpg|jpeg|png|bmp|tiff)$", filename):
            cant = cant+1
            filepath = os.path.join(root, filename)
            image = plt.imread(filepath)
            images.append(image)
            b = "Leyendo... " + str(cant)
            print (b, end="\r")

    # --- Esta es la segunda parte de la imagen ---
    if prevRoot != root:
        print(root, cant)
        prevRoot = root
        directories.append(root)
        dircount.append(cant)
        cant = 0

dircount.append(cant)

dircount = dircount[1:]
#dircount[0] = dircount[0] + 1
print('Directorios leidos: ', len(directories))
print("Imagenes en cada directorio", dircount)
print('suma Total de imagenes en subdirs:', sum(dircount))

# ----------------------------------------------------------------
# PASO 2: Crear etiquetas y arrays finales
# ----------------------------------------------------------------
labels=[]
indice=0
for cantidad in dircount:
    for i in range(cantidad):
        labels.append(indice)
    indice=indice+1
print("Cantidad etiquetas creadas: ", len(labels))

deportes=[]
indice=0
for directorio in directories:
    name = directorio.split(os.sep)
    print(indice , name[len(name)-1])
    
    # --- Continuación del bucle (de la segunda imagen) ---
    deportes.append(name[len(name)-1])
    indice=indice+1

# --- Resto del código de la segunda imagen ---
y = np.array(labels)
X = np.array(images, dtype=np.uint8) #convierto de lista a numpy

# Find the unique numbers from the train labels
classes = np.unique(y)
nClasses = len(classes)
print('Total number of outputs : ', nClasses)
print('Output classes : ', classes)

# ----------------------------------------------------------------
# PASO 3: Dividir y preprocesar los datos 
# ----------------------------------------------------------------
# Mezclar todo y crear los grupos de entrenamiento y testing
train_X, test_X, train_Y, test_Y = train_test_split(X, y, test_size=0.2, stratify=y, random_state=13)
print('\nTraining data shape : ', train_X.shape, train_Y.shape)
print('Testing data shape : ', test_X.shape, test_Y.shape)

# Normalizar los datos de imagen (píxeles de 0-255 a 0-1)
train_X = train_X.astype('float32')
test_X = test_X.astype('float32')
train_X = train_X / 255.
test_X = test_X / 255.

# Convertir las etiquetas a formato one-hot encoding (forzando el mismo num. de clases)
train_Y_one_hot = to_categorical(train_Y, num_classes=nClasses)
test_Y_one_hot = to_categorical(test_Y, num_classes=nClasses)

# Mostrar el cambio
print('\nOriginal label:', train_Y[0])
print('After conversion to one-hot:', train_Y_one_hot[0])

# Crear un set de validación a partir del set de entrenamiento
train_X, valid_X, train_label, valid_label = train_test_split(train_X, train_Y_one_hot, test_size=0.2, random_state=13)

print('\nFinal shapes:')
print(train_X.shape, valid_X.shape, train_label.shape, valid_label.shape)

# ----------------------------------------------------------------
# PASO 4: Crear y entrenar el modelo
# ----------------------------------------------------------------

INIT_LR = 1e-3
epochs = 65 # Afinar los pesos sinpticos 
batch_size = 64  

sport_model = Sequential([
    # Usar Input como primera capa en lugar de input_shape
    Input(shape=(64, 64, 3)),
    
    # Primera capa: 64x64x3 -> 32x32x32
    Conv2D(32, kernel_size=(3, 3), activation='linear', padding='same'),
    LeakyReLU(negative_slope=0.1),  # Cambiar alpha por negative_slope
    MaxPooling2D((2, 2), padding='same'),
    Dropout(0.25),

    # Segunda capa: 32x32x32 -> 16x16x64
    Conv2D(64, kernel_size=(3, 3), activation='linear', padding='same'),
    LeakyReLU(negative_slope=0.1),
    MaxPooling2D((2, 2), padding='same'),
    Dropout(0.25),

    # Tercera capa: 16x16x64 -> 8x8x128
    Conv2D(128, kernel_size=(3, 3), activation='linear', padding='same'),
    LeakyReLU(negative_slope=0.1),
    MaxPooling2D((2, 2), padding='same'),
    Dropout(0.25),

    # Aplanar y capas densas
    Flatten(),
    Dense(128, activation='linear'),
    LeakyReLU(negative_slope=0.1),
    Dropout(0.5),
    Dense(nClasses, activation='softmax')
])

sport_model.summary()

sport_model.compile(
    loss=keras.losses.categorical_crossentropy,
    optimizer=keras.optimizers.Adagrad(learning_rate=INIT_LR),
    metrics=['accuracy']
)

# Entrenar el modelo
early_stopping = EarlyStopping(
    monitor='val_loss',           # Monitorear la pérdida de validación
    patience=5,                   # Número de épocas sin mejora antes de parar
    restore_best_weights=True,    # Restaurar los pesos de la mejor época
    verbose=1
)

sport_model_train = sport_model.fit(
    train_X, train_label,
    batch_size=batch_size,
    epochs=epochs,
    verbose=1,
    validation_data=(valid_X, valid_label),
    callbacks=[early_stopping]
)

# Evaluar el modelo en el conjunto de prueba
test_eval = sport_model.evaluate(test_X, test_Y_one_hot, verbose=1)
print('Test loss:', test_eval[0])
print('Test accuracy:', test_eval[1])

# Guardar el modelo con formato .keras
sport_model.save("recognice_animals.keras")  # Cambiar extensión
print('\nModelo guardado como recognice_animals.keras')