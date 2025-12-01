# Importación de librerías esenciales
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Carga del Corpus
df = pd.read_csv('Proyecto3//dataset_sintetico_5000_ampliado.csv')

# Limitar a las primeras 200 filas
#df = df.head(200)

# Inspección inicial
print(f"Total de tweets cargados: {len(df)}")
print("Primeras filas:")
print(df[['texto', 'tema']].head())

# 2. Preprocesamiento: Manejo de Duplicados
# Identificamos tweets únicos para el análisis semántico puro
tweets_unicos = df['texto'].unique()
print(f"Tweets únicos: {len(tweets_unicos)}")

# Nota: Para el análisis de similitud, usaremos los tweets únicos para evitar
# sesgos de repetición sintética, pero mantendremos la referencia a sus temas.
df_unique = df.drop_duplicates(subset=['texto']).reset_index(drop=True)

# 3. Cargar el modelo pre-entrenado
# Este modelo genera vectores de 384 dimensiones
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generar embeddings
# batch_size=64 es un buen equilibrio para esta longitud de modelo y datos
embeddings = model.encode(df_unique['texto'].tolist(), batch_size=64, show_progress_bar=True)

print(f"Forma de la matriz de embeddings: {embeddings.shape}")
# Debería mostrar (N_unicos, 384)

# 4. Calcular la matriz de similitud coseno (N x N)
similarity_matrix = cosine_similarity(embeddings)

# Convertir a DataFrame para facilitar el análisis con etiquetas
df_sim = pd.DataFrame(similarity_matrix, index=df_unique.index, columns=df_unique.index)

# 5. Asignar colores a los temas para la visualización
tema_dict = {tema: idx for idx, tema in enumerate(df_unique['tema'].unique())}
colores = df_unique['tema'].map(tema_dict)

# Ordenar la matriz por tema para ver los bloques en el heatmap
df_unique['sort_idx'] = df_unique['tema'] # Helper para ordenar
sorted_idx = df_unique.sort_values('tema').index
sorted_sim_matrix = df_sim.loc[sorted_idx, sorted_idx]

# Plotear Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(sorted_sim_matrix, cmap='viridis', xticklabels=False, yticklabels=False)
plt.title('Matriz de Similitud Coseno entre Tweets (Agrupados por Tema)')
plt.xlabel('Tweets (Ordenados por Tema)')
plt.ylabel('Tweets (Ordenados por Tema)')
plt.show()

