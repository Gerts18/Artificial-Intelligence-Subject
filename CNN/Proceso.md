# Proceso de Creación de CNN para Clasificación de Animales

## Índice
1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [Versión 1: CNN.py - Implementación Básica](#versión-1-cnnpy)
3. [Versión 2: CNN2.py - Implementación Optimizada](#versión-2-cnn2py)
4. [Comparación de Enfoques](#comparación-de-enfoques)
5. [Resultados y Conclusiones](#resultados-y-conclusiones)

---

## Conceptos Fundamentales

### ¿Qué es una CNN?
Una **Red Neuronal Convolucional (CNN)** es una arquitectura de deep learning especializada en el procesamiento de datos visuales. Las CNN aprenden características jerárquicas de las imágenes de manera automática.

### Componentes Clave

#### 1. **Filtros/Kernels de Convolución**
- Son matrices que se deslizan sobre la imagen para detectar características
- **Primera capa**: 32 filtros detectan características básicas (bordes, colores)
- **Capas posteriores**: 64, 128, etc. detectan características más complejas
- **Los pesos sinápticos se guardan en estas matrices de convolución**

#### 2. **Max Pooling**
- Reduce las dimensiones espaciales (ancho x alto) de las características
- Extrae la característica más prominente de cada región
- **Objetivo**: Reducir los pesos sinápticos y dimensionalidad mientras se mantiene información relevante

#### 3. **Dropout**
- Apaga neuronas aleatoriamente durante el entrenamiento
- **Función**: Evitar el sobreajuste (overfitting)
- **Razón**: Previene que algunos pesos sinápticos dominen el aprendizaje

#### 4. **Flatten**
- Convierte la matriz multidimensional en un vector unidimensional
- Prepara los datos para las capas densas

#### 5. **Dense (Capas Densas)**
- Cada neurona está conectada con todas las neuronas de la capa anterior
- Realiza la clasificación final basándose en las características extraídas

#### 6. **Softmax**
- Función de activación final para clasificación multiclase
- **Función**: Convierte los valores de salida en probabilidades (suman 1.0)
- Indica la probabilidad de que la imagen pertenezca a cada clase

#### 7. **LeakyReLU**
- Función de activación que permite gradientes pequeños cuando la neurona no está activa
- **Ventaja**: Evita el problema de "neuronas muertas" que puede ocurrir con ReLU

---

## Versión 1: CNN.py - Implementación Básica

### Estructura del Proyecto
```
animals-dataset/
├── catarina/
├── gato/
├── hormiga/
├── perro/
└── tortuga/
```

### Paso 1: Carga de Imágenes
```python
# Recorre recursivamente el directorio del dataset
for root, dirnames, filenames in os.walk(imgpath):
    for filename in filenames:
        if re.search("\.(jpg|jpeg|png|bmp|tiff)$", filename):
            image = plt.imread(filepath)
            images.append(image)
```

**Características**:
- Lee todas las imágenes en memoria a la vez
- **Limitación**: Puede causar problemas de memoria (MemoryError) con datasets grandes
- Soporta múltiples formatos: JPG, PNG, BMP, TIFF

### Paso 2: Creación de Etiquetas
```python
labels = []
for cantidad in dircount:
    for i in range(cantidad):
        labels.append(indice)
    indice += 1
```

**Proceso**:
1. Cada carpeta representa una clase (animal)
2. Se asigna un índice numérico a cada clase
3. Se crea una etiqueta para cada imagen según su carpeta

### Paso 3: Preprocesamiento de Datos

#### División del Dataset
```python
train_X, test_X, train_Y, test_Y = train_test_split(
    X, y, 
    test_size=0.2,      # 20% para pruebas
    stratify=y,         # Mantiene proporción de clases
    random_state=13     # Reproducibilidad
)
```

**Conjuntos resultantes**:
- **Entrenamiento**: 80% de los datos
- **Prueba**: 20% de los datos
- El conjunto de entrenamiento se divide después en:
  - 80% entrenamiento real
  - 20% validación

#### Normalización
```python
train_X = train_X / 255.0
test_X = test_X / 255.0
```
- Convierte píxeles de rango [0-255] a [0-1]
- Ayuda a la red a aprender más rápido y estable

#### One-Hot Encoding
```python
train_Y_one_hot = to_categorical(train_Y, num_classes=nClasses)
```
- Convierte etiquetas numéricas a vectores binarios
- Ejemplo: clase 2 de 5 clases → [0, 0, 1, 0, 0]

### Paso 4: Arquitectura del Modelo

```python
sport_model = Sequential([
    Input(shape=(64, 64, 3)),  # Imágenes 64x64 RGB
    
    # BLOQUE 1: 64x64x3 → 32x32x32
    Conv2D(32, (3,3), padding='same'),
    LeakyReLU(negative_slope=0.1),
    MaxPooling2D((2,2)),
    Dropout(0.25),
    
    # BLOQUE 2: 32x32x32 → 16x16x64
    Conv2D(64, (3,3), padding='same'),
    LeakyReLU(negative_slope=0.1),
    MaxPooling2D((2,2)),
    Dropout(0.25),
    
    # BLOQUE 3: 16x16x64 → 8x8x128
    Conv2D(128, (3,3), padding='same'),
    LeakyReLU(negative_slope=0.1),
    MaxPooling2D((2,2)),
    Dropout(0.25),
    
    # CLASIFICADOR
    Flatten(),
    Dense(128),
    LeakyReLU(negative_slope=0.1),
    Dropout(0.5),
    Dense(nClasses, activation='softmax')
])
```

**Jerarquía de Aprendizaje**:
1. **Bloque 1**: Detecta bordes, colores básicos
2. **Bloque 2**: Detecta texturas, patrones simples
3. **Bloque 3**: Detecta formas complejas, partes de objetos
4. **Clasificador**: Toma decisión final sobre la clase

### Paso 5: Compilación y Entrenamiento

```python
sport_model.compile(
    loss='categorical_crossentropy',
    optimizer=Adagrad(learning_rate=0.001),
    metrics=['accuracy']
)
```

**Componentes**:
- **Loss Function**: Mide qué tan equivocadas son las predicciones
- **Optimizer (Adagrad)**: Ajusta los pesos para minimizar el loss
- **Metric**: Accuracy - porcentaje de predicciones correctas

#### Callbacks: Early Stopping
```python
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)
```

**Función**: 
- Detiene el entrenamiento si la validación no mejora en 5 épocas
- Previene sobreajuste y ahorra tiempo de cómputo
- Restaura los mejores pesos encontrados

### Configuración de Entrenamiento
- **Learning Rate**: 0.001
- **Épocas**: 65 (con early stopping puede parar antes)
- **Batch Size**: 32 imágenes procesadas simultáneamente
- **Tamaño de Imagen**: 64x64 píxeles

---

## Versión 2: CNN2.py - Implementación Optimizada

### Mejoras Principales

#### 1. **Generadores de Datos (Image Data Generators)**
```python
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2
)
```

**Ventajas**:
- **Soluciona MemoryError**: No carga todas las imágenes en memoria a la vez
- **Data Augmentation**: Genera variaciones de las imágenes durante el entrenamiento
  - Rotaciones hasta 20°
  - Desplazamientos horizontales y verticales (20%)
  - Flips horizontales
  - Zoom aleatorio (20%)
- **Efecto**: Incrementa artificialmente el tamaño del dataset

#### 2. **Mayor Resolución**
- **CNN.py**: 64x64 píxeles
- **CNN2.py**: 128x128 píxeles
- **Beneficio**: Más detalle visual, mejor reconocimiento de características

#### 3. **Arquitectura Mejorada**

```python
# BLOQUE 1: 128x128x3 → 64x64x32
Conv2D(32, (3,3), padding='same')
LeakyReLU(alpha=0.1)
MaxPooling2D((2,2))
Dropout(0.3)

# BLOQUE 2: 64x64x32 → 32x32x64
Conv2D(64, (3,3), padding='same')
LeakyReLU(alpha=0.1)
MaxPooling2D((2,2))
Dropout(0.3)

# BLOQUE 3: 32x32x64 → 16x16x128
Conv2D(128, (3,3), padding='same')
LeakyReLU(alpha=0.1)
MaxPooling2D((2,2))
Dropout(0.3)

# BLOQUE 4: 16x16x128 → 8x8x128
Conv2D(128, (3,3), padding='same')
LeakyReLU(alpha=0.1)
MaxPooling2D((2,2))
Dropout(0.3)

# CLASIFICADOR
Flatten()
Dense(512)
LeakyReLU(alpha=0.1)
Dropout(0.5)
Dense(128)
Dense(nClasses, activation='softmax')
```

**Mejoras**:
- **4 bloques convolucionales** (vs 3 en CNN.py)
- **Capa densa más grande**: 512 neuronas (vs 128)
- **Capa intermedia adicional**: Dense(128) antes de la salida
- **Mayor capacidad de aprendizaje** para patrones complejos

#### 4. **Optimizador Mejorado**
```python
optimizer = Adam(learning_rate=0.001)
```
- **Adam vs Adagrad**: Adam ajusta learning rate adaptativamente
- Generalmente converge más rápido y mejor

#### 5. **Callbacks Avanzados**

**ReduceLROnPlateau**:
```python
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,      # Reduce LR a la mitad
    patience=3,      # Espera 3 épocas sin mejora
    min_lr=1e-7
)
```
- Reduce automáticamente el learning rate cuando el entrenamiento se estanca
- Permite escapar de mínimos locales

**Early Stopping Mejorado**:
```python
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    min_delta=0.001,  # Mejora mínima requerida
    restore_best_weights=True
)
```

#### 6. **Guardado del Historial**
```python
with open('training_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)
```
- Permite analizar el entrenamiento después
- Útil para regenerar gráficas sin reentrenar

#### 7. **Visualización Automática**
- Genera gráficas de accuracy y loss automáticamente
- Guarda las gráficas en formato PNG de alta resolución (300 DPI)

---

## Comparación de Enfoques

| Aspecto | CNN.py (Básico) | CNN2.py (Optimizado) |
|---------|-----------------|----------------------|
| **Carga de Datos** | Todo en memoria | Generadores (batch a batch) |
| **Resolución** | 64x64 | 128x128 |
| **Data Augmentation** | No | Sí (múltiples transformaciones) |
| **Bloques Conv** | 3 | 4 |
| **Neuronas Densas** | 128 | 512 → 128 |
| **Optimizador** | Adagrad | Adam |
| **Callbacks** | EarlyStopping | EarlyStopping + ReduceLROnPlateau |
| **Memoria Requerida** | Alta (todo el dataset) | Baja (solo un batch) |
| **Escalabilidad** | Limitada | Excelente |
| **Tiempo por Época** | Menor | Mayor (imágenes más grandes) |
| **Precisión Esperada** | Buena | Mejor |

---

## Flujo de Datos en una CNN

```
Imagen de Entrada (128x128x3)
         ↓
    Conv2D(32)      ← Detecta bordes, colores
         ↓
    MaxPooling      ← Reduce a 64x64
         ↓
    Conv2D(64)      ← Detecta texturas
         ↓
    MaxPooling      ← Reduce a 32x32
         ↓
    Conv2D(128)     ← Detecta formas complejas
         ↓
    MaxPooling      ← Reduce a 16x16
         ↓
    Conv2D(128)     ← Detecta objetos completos
         ↓
    MaxPooling      ← Reduce a 8x8
         ↓
    Flatten         ← Convierte a vector [1 x 8192]
         ↓
    Dense(512)      ← Combina características
         ↓
    Dense(128)      ← Refina representación
         ↓
    Dense(5)        ← 5 clases: [catarina, gato, hormiga, perro, tortuga]
         ↓
    Softmax         ← Convierte a probabilidades
         ↓
    Predicción: [0.05, 0.15, 0.02, 0.75, 0.03]
                                    ↑
                            Clase predicha: Perro (75%)
```

---
## Resultados y Conclusiones

### Métricas de Evaluación

**Training Accuracy**: 
- Precisión en datos de entrenamiento
- Si es muy alta y val_accuracy baja → Overfitting

**Validation Accuracy**:
- Precisión en datos que el modelo NO ha visto
- Mejor indicador del rendimiento real

**Test Accuracy**:
- Evaluación final en conjunto completamente nuevo
- Métrica definitiva de desempeño

### Criterios de Éxito
- **Excelente**: >90% accuracy en validación
- **Bueno**: 80-90% accuracy
- **Regular**: 70-80% accuracy
- **Necesita mejora**: <70% accuracy

### Posibles Problemas y Soluciones

#### Overfitting (Sobreajuste)
**Síntomas**: Training accuracy alta, validation accuracy baja

**Soluciones**:
1. Aumentar Dropout (0.3 → 0.5)
2. Agregar más Data Augmentation
3. Reducir número de parámetros
4. Conseguir más datos de entrenamiento

#### Underfitting (Subajuste)
**Síntomas**: Training accuracy y validation accuracy bajas

**Soluciones**:
1. Aumentar complejidad del modelo (más capas/filtros)
2. Entrenar más épocas
3. Aumentar learning rate
4. Reducir Dropout

#### Convergencia Lenta
**Síntomas**: Accuracy mejora muy lentamente

**Soluciones**:
1. Aumentar learning rate
2. Cambiar optimizador (Adagrad → Adam)
3. Aumentar batch size
4. Normalizar mejor los datos

---

## Archivos Generados

### Modelo Entrenado
- **CNN.py**: `recognice_animals.keras`
- **CNN2.py**: `animal_classifier_optimized-2.h5`

### Historial
- `training_history.pkl`: Datos de entrenamiento para análisis posterior

### Visualizaciones
- `training_results.png`: Gráficas de accuracy y loss

---

## Comandos para Usar el Modelo

### Cargar Modelo
```python
from tensorflow.keras.models import load_model

# Para CNN.py
model = load_model('recognice_animals.keras')

# Para CNN2.py
model = load_model('animal_classifier_optimized-2.h5')
```

### Hacer Predicciones
```python
import numpy as np
from tensorflow.keras.preprocessing import image

# Cargar imagen
img = image.load_img('test_image.jpg', target_size=(128, 128))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0

# Predecir
predictions = model.predict(img_array)
class_idx = np.argmax(predictions[0])
confidence = predictions[0][class_idx] * 100

print(f"Clase predicha: {class_names[class_idx]}")
print(f"Confianza: {confidence:.2f}%")
```

**Fecha de Creación**: Diciembre 17, 2025  
**Dataset**: 5 clases de animales (catarina, gato, hormiga, perro, tortuga), cada clase con +5000 imagenes