import pandas as pd
import numpy as np
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

# Este script analiza el sentimiento de tweets en español usando un modelo preentrenado de Hugging Face 

# Ruta del archivo
archivo_entrada = r'RAG//recoleccion//tweets.csv.xlsx'
archivo_salida = r'RAG//limpieza//tweets_con_sentimientos.xlsx'

print("Cargando el archivo...")
# Leer el archivo Excel
df = pd.read_excel(archivo_entrada)

print(f"Total de tweets: {len(df)}")
print(f"\nColumnas encontradas: {list(df.columns)}")
print(f"\nPrimeras filas:")
print(df.head())

# Inicializar el modelo de análisis de sentimientos para español
# Usando un modelo preentrenado en español
print("\nCargando modelo de análisis de sentimientos...")
sentiment_analyzer = pipeline(
    "sentiment-analysis", 
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    truncation=True,
    max_length=512
)

def analizar_sentimiento(texto):
    """
    Analiza el sentimiento de un texto.
    El modelo retorna 1-5 estrellas, las convertimos a: negativo, neutral, positivo
    """
    try:
        if pd.isna(texto) or texto == "" or not isinstance(texto, str):
            return "neutral"
        
        # Analizar el sentimiento
        resultado = sentiment_analyzer(texto[:512])[0]
        estrellas = int(resultado['label'].split()[0])
        
        # Convertir estrellas a sentimiento
        if estrellas <= 2:
            return "negativo"
        elif estrellas == 3:
            return "neutral"
        else:
            return "positivo"
    except Exception as e:
        print(f"Error analizando texto: {str(e)[:50]}")
        return "neutral"

# Procesar cada tweet
print("\nAnalizando sentimientos de los tweets...")
sentimientos = []

for idx, row in df.iterrows():
    texto = row['texto']
    sentimiento = analizar_sentimiento(texto)
    sentimientos.append(sentimiento)
    
    # Mostrar progreso cada 10 tweets
    if (idx + 1) % 10 == 0:
        print(f"Procesados {idx + 1}/{len(df)} tweets...")

# Actualizar la columna de sentimiento
df['sentimiento'] = sentimientos

# Mostrar estadísticas
print("\n" + "="*50)
print("ANÁLISIS COMPLETADO")
print("="*50)
print("\nDistribución de sentimientos:")
print(df['sentimiento'].value_counts())
print(f"\nPorcentajes:")
print(df['sentimiento'].value_counts(normalize=True) * 100)

# Guardar el archivo actualizado
print(f"\nGuardando archivo en: {archivo_salida}")
df.to_excel(archivo_salida, index=False)

print("\n✓ Proceso completado exitosamente!")
print(f"✓ Archivo guardado: {archivo_salida}")
