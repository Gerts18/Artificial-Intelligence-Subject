"""
Script para limpieza profunda del corpus de texto
Incluye: stopwords, normalización y lematización
"""

import pandas as pd
import re
import unicodedata
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import spacy

# Descargar recursos necesarios de NLTK (ejecutar solo la primera vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Cargar modelo de spaCy para español (para lematización)
try:
    nlp = spacy.load('es_core_news_sm')
except OSError:
    print("Instalando modelo de spaCy para español...")
    print("Ejecuta: python -m spacy download es_core_news_sm")
    nlp = None


class LimpiadorTexto:
    """Clase para realizar limpieza profunda de texto en español"""
    
    def __init__(self, usar_lemmatizacion=True):
        """
        Inicializa el limpiador de texto
        
        Args:
            usar_lemmatizacion: Si True, usa spaCy para lematización. 
                              Si False, usa stemming de NLTK.
        """
        self.stop_words = set(stopwords.words('spanish'))
        self.usar_lemmatizacion = usar_lemmatizacion
        
        # Añadir stopwords personalizadas
        self.stop_words.update(['si', 'no', 'q', 'rt', 'vía'])
        
        if usar_lemmatizacion and nlp is None:
            print("⚠️ spaCy no disponible, usando stemming en su lugar")
            self.usar_lemmatizacion = False
        
        if not self.usar_lemmatizacion:
            self.stemmer = SnowballStemmer('spanish')
    
    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza el texto básico: lowercase, elimina acentos opcionales,
        elimina caracteres especiales
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        if not isinstance(texto, str):
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar URLs
        texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
        
        # Eliminar menciones y hashtags (opcional, comentar si se quieren mantener)
        texto = re.sub(r'@\w+', '', texto)
        texto = re.sub(r'#\w+', '', texto)
        
        # Eliminar emails
        texto = re.sub(r'\S+@\S+', '', texto)
        
        # Eliminar números (opcional, comentar si se quieren mantener)
        # texto = re.sub(r'\d+', '', texto)
        
        # Eliminar puntuación y caracteres especiales, mantener espacios
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        # Eliminar espacios al inicio y final
        texto = texto.strip()
        
        return texto
    
    def remover_acentos(self, texto: str) -> str:
        """
        Remueve acentos del texto (opcional, según necesidad)
        
        Args:
            texto: Texto con acentos
            
        Returns:
            Texto sin acentos
        """
        texto_nfd = unicodedata.normalize('NFD', texto)
        texto_sin_acentos = ''.join(
            char for char in texto_nfd 
            if unicodedata.category(char) != 'Mn'
        )
        return texto_sin_acentos
    
    def remover_stopwords(self, texto: str) -> str:
        """
        Remueve stopwords del texto
        
        Args:
            texto: Texto tokenizado
            
        Returns:
            Texto sin stopwords
        """
        tokens = word_tokenize(texto, language='spanish')
        tokens_filtrados = [
            palabra for palabra in tokens 
            if palabra not in self.stop_words and len(palabra) > 2
        ]
        return ' '.join(tokens_filtrados)
    
    def lematizar_texto(self, texto: str) -> str:
        """
        Lematiza el texto usando spaCy
        
        Args:
            texto: Texto a lematizar
            
        Returns:
            Texto lematizado
        """
        doc = nlp(texto)
        lemmas = [token.lemma_ for token in doc if not token.is_stop and len(token.text) > 2]
        return ' '.join(lemmas)
    
    def stemming_texto(self, texto: str) -> str:
        """
        Aplica stemming al texto usando NLTK
        
        Args:
            texto: Texto a procesar
            
        Returns:
            Texto con stemming aplicado
        """
        tokens = word_tokenize(texto, language='spanish')
        stems = [self.stemmer.stem(palabra) for palabra in tokens if len(palabra) > 2]
        return ' '.join(stems)
    
    def limpiar_texto_completo(self, texto: str, 
                               remover_acentos_flag=False,
                               aplicar_lemmatizacion=True) -> str:
        """
        Pipeline completo de limpieza de texto
        
        Args:
            texto: Texto a limpiar
            remover_acentos_flag: Si True, remueve acentos
            aplicar_lemmatizacion: Si True, aplica lematización/stemming. Si False, solo normaliza y remueve stopwords
            
        Returns:
            Texto completamente limpio
        """
        # 1. Normalización básica
        texto = self.normalizar_texto(texto)
        
        # 2. Remover acentos (opcional)
        if remover_acentos_flag:
            texto = self.remover_acentos(texto)
        
        # 3. Remover stopwords
        texto = self.remover_stopwords(texto)
        
        # 4. Lematización o Stemming (opcional)
        if aplicar_lemmatizacion:
            if self.usar_lemmatizacion:
                texto = self.lematizar_texto(texto)
            else:
                texto = self.stemming_texto(texto)
        
        return texto


def procesar_csv(archivo_entrada: str, 
                 archivo_salida: str = None,
                 columna_texto: str = 'texto',
                 usar_lemmatizacion: bool = True,
                 remover_acentos: bool = False) -> pd.DataFrame:
    """
    Procesa un archivo CSV aplicando limpieza profunda al corpus
    
    Args:
        archivo_entrada: Ruta al archivo CSV de entrada
        archivo_salida: Ruta al archivo CSV de salida (opcional)
        columna_texto: Nombre de la columna con el texto a limpiar
        usar_lemmatizacion: Si True usa lematización, si False usa stemming
        remover_acentos: Si True remueve acentos
        
    Returns:
        DataFrame con los datos procesados
    """
    print(f"📂 Cargando datos desde: {archivo_entrada}")
    
    # Detectar tipo de archivo y leer apropiadamente
    if archivo_entrada.endswith('.xlsx') or archivo_entrada.endswith('.xls'):
        df = pd.read_excel(archivo_entrada)
    else:
        df = pd.read_csv(archivo_entrada, encoding='utf-8', errors='ignore')
    
    print(f"📊 Total de registros: {len(df)}")
    print(f"📝 Columnas disponibles: {list(df.columns)}")
    
    if columna_texto not in df.columns:
        raise ValueError(f"La columna '{columna_texto}' no existe en el CSV")
    
    # Inicializar limpiador
    limpiador = LimpiadorTexto(usar_lemmatizacion=usar_lemmatizacion)
    
    # Crear columnas adicionales con diferentes niveles de procesamiento
    print("\n🧹 Iniciando limpieza del corpus...")
    
    # Texto normalizado (básico)
    print("  1️⃣ Normalizando texto...")
    df['texto_normalizado'] = df[columna_texto].apply(
        lambda x: limpiador.normalizar_texto(x) if pd.notna(x) else ""
    )
    
    # Texto sin stopwords
    print("  2️⃣ Removiendo stopwords...")
    df['texto_sin_stopwords'] = df['texto_normalizado'].apply(
        lambda x: limpiador.remover_stopwords(x) if x else ""
    )
    
    # Texto completamente limpio (SOLO normalizado sin stopwords, SIN lematización/stemming)
    print(f"  3️⃣ Generando texto limpio (sin stopwords, palabras completas)...")
    texto_limpio = df['texto_sin_stopwords'].copy()
    
    # Guardar texto original en columna separada antes de reemplazar
    df['texto_original'] = df[columna_texto].copy()
    
    # Reemplazar la columna de texto con el texto limpio
    df[columna_texto] = texto_limpio
    
    # Estadísticas
    print("\n📈 Estadísticas de limpieza:")
    print(f"  - Longitud promedio texto original: {df['texto_original'].str.len().mean():.2f} caracteres")
    print(f"  - Longitud promedio texto limpio: {df[columna_texto].str.len().mean():.2f} caracteres")
    print(f"  - Reducción promedio: {(1 - df[columna_texto].str.len().mean() / df['texto_original'].str.len().mean()) * 100:.2f}%")
    
    # Eliminar columnas intermedias, mantener solo original y limpio
    columnas_a_eliminar = ['texto_normalizado', 'texto_sin_stopwords']
    df = df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns])
    
    # Guardar resultado
    if archivo_salida:
        print(f"\n💾 Guardando resultados en: {archivo_salida}")
        df.to_csv(archivo_salida, index=False, encoding='utf-8')
        print("✅ Archivo guardado exitosamente")
        print(f"📝 Columnas en el archivo: {list(df.columns)}")
    
    return df


def mostrar_ejemplos(df: pd.DataFrame, n: int = 3):
    """
    Muestra ejemplos de textos antes y después de la limpieza
    
    Args:
        df: DataFrame con los textos procesados
        n: Número de ejemplos a mostrar
    """
    print(f"\n📋 Mostrando {n} ejemplos de limpieza:\n")
    print("=" * 100)
    
    for i in range(min(n, len(df))):
        print(f"\nEjemplo {i+1}:")
        if 'texto_original' in df.columns:
            print(f"Original:           {df.iloc[i]['texto_original'][:150]}...")
        print(f"Limpio (texto):     {df.iloc[i]['texto'][:150]}...")
        print("-" * 100)


if __name__ == "__main__":
    # Configuración
    ARCHIVO_ENTRADA = "RAG//limpieza//tweets_con_sentimientos.xlsx"
    ARCHIVO_SALIDA = "RAG//limpieza//dataset_limpio_tweets.csv"
    
    # Opciones de limpieza
    USAR_LEMMATIZACION = False  # False para NO aplicar lematización/stemming (mantiene palabras completas)
    REMOVER_ACENTOS = False      # True para remover acentos
    
    try:
        # Procesar el dataset
        df_limpio = procesar_csv(
            archivo_entrada=ARCHIVO_ENTRADA,
            archivo_salida=ARCHIVO_SALIDA,
            columna_texto='texto',
            usar_lemmatizacion=USAR_LEMMATIZACION,
            remover_acentos=REMOVER_ACENTOS
        )
        
        # Mostrar ejemplos
        mostrar_ejemplos(df_limpio, n=5)
        
        print("\n✨ ¡Proceso completado exitosamente!")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{ARCHIVO_ENTRADA}'")
        print("   Asegúrate de que el archivo esté en el directorio actual")
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
