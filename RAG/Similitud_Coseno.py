import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo de gráficas
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# --- CONFIGURACIÓN ---
INPUT_FILE = 'RAG//dataset_sin_duplicados.csv'  # Cambia esto por tu archivo Excel (.xlsx) o CSV
TEXT_COLUMN = 'texto'  # Nombre de la columna que contiene los textos a comparar
OUTPUT_FILE = 'resultados_similitud.csv'  # Archivo de salida con los resultados
UMBRAL_SIMILITUD = 0.5  # Umbral para considerar textos similares (0.0 a 1.0)

def cargar_datos(archivo):
    """Carga datos desde Excel o CSV"""
    print(f"📂 Cargando archivo: {archivo}...")
    
    try:
        # Detectar el tipo de archivo y cargar
        if archivo.endswith('.xlsx') or archivo.endswith('.xls'):
            df = pd.read_excel(archivo)
        elif archivo.endswith('.csv'):
            df = pd.read_csv(archivo, encoding='utf-8')
        else:
            raise ValueError("Formato no soportado. Use .xlsx, .xls o .csv")
        
        print(f"✅ Cargados {len(df)} registros")
        return df
    
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo '{archivo}'")
        return None
    except Exception as e:
        print(f"❌ Error al cargar archivo: {e}")
        return None

def calcular_similitud_coseno(textos):
    """
    Calcula la matriz de similitud coseno entre todos los textos
    usando TF-IDF (Term Frequency-Inverse Document Frequency)
    """
    print("🔄 Vectorizando textos con TF-IDF...")
    
    # Crear vectorizador TF-IDF
    # - max_features: limita el vocabulario a las palabras más frecuentes
    # - ngram_range: usa unigramas y bigramas
    # - min_df: ignora palabras que aparecen en menos de 2 documentos
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        stop_words=None  # Puedes agregar stop words en español si lo deseas
    )
    
    # Convertir textos a vectores TF-IDF
    tfidf_matrix = vectorizer.fit_transform(textos)
    
    print("🔄 Calculando similitudes coseno...")
    # Calcular matriz de similitud coseno
    similitud_matrix = cosine_similarity(tfidf_matrix)
    
    return similitud_matrix, vectorizer

def encontrar_textos_similares(df, similitud_matrix, umbral=0.5):
    """
    Encuentra pares de textos con similitud mayor al umbral
    """
    print(f"🔍 Buscando textos similares (umbral: {umbral})...")
    
    resultados = []
    n = len(df)
    
    # Recorrer la matriz triangular superior (evitar duplicados)
    for i in range(n):
        for j in range(i + 1, n):
            similitud = similitud_matrix[i][j]
            
            if similitud >= umbral:
                resultados.append({
                    'indice_1': i,
                    'indice_2': j,
                    'texto_1': df.iloc[i][TEXT_COLUMN][:100] + '...',  # Primeros 100 chars
                    'texto_2': df.iloc[j][TEXT_COLUMN][:100] + '...',
                    'similitud': round(similitud, 4)
                })
    
    return pd.DataFrame(resultados)

def mostrar_estadisticas(similitud_matrix):
    """Muestra estadísticas de la matriz de similitud"""
    print("\n📊 ESTADÍSTICAS DE SIMILITUD:")
    print("=" * 50)
    
    # Obtener valores sin la diagonal (similitud consigo mismo = 1.0)
    n = similitud_matrix.shape[0]
    valores = []
    for i in range(n):
        for j in range(i + 1, n):
            valores.append(similitud_matrix[i][j])
    
    valores = np.array(valores)
    
    print(f"📈 Promedio de similitud: {valores.mean():.4f}")
    print(f"📈 Máxima similitud: {valores.max():.4f}")
    print(f"📉 Mínima similitud: {valores.min():.4f}")
    print(f"📊 Desviación estándar: {valores.std():.4f}")
    print(f"📊 Mediana: {np.median(valores):.4f}")
    print("=" * 50 + "\n")
    
    return valores

def visualizar_similitudes(similitud_matrix, valores, df):
    """Genera visualizaciones de las similitudes"""
    print("📊 Generando visualizaciones...\n")
    
    # Crear figura con múltiples subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. HEATMAP de la matriz de similitud
    ax1 = plt.subplot(2, 2, 1)
    # Limitar el heatmap a los primeros 50 textos si hay muchos
    n_mostrar = min(50, similitud_matrix.shape[0])
    matriz_visual = similitud_matrix[:n_mostrar, :n_mostrar]
    
    im = ax1.imshow(matriz_visual, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
    ax1.set_title(f'Heatmap de Similitud Coseno\n(primeros {n_mostrar} textos)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Índice del Texto', fontsize=11)
    ax1.set_ylabel('Índice del Texto', fontsize=11)
    plt.colorbar(im, ax=ax1, label='Similitud')
    
    # 2. HISTOGRAMA de distribución de similitudes
    ax2 = plt.subplot(2, 2, 2)
    ax2.hist(valores, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    ax2.axvline(valores.mean(), color='red', linestyle='--', linewidth=2, 
                label=f'Media: {valores.mean():.3f}')
    ax2.axvline(np.median(valores), color='green', linestyle='--', linewidth=2, 
                label=f'Mediana: {np.median(valores):.3f}')
    ax2.set_title('Distribución de Similitudes', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('Similitud Coseno', fontsize=11)
    ax2.set_ylabel('Frecuencia', fontsize=11)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. BOX PLOT
    ax3 = plt.subplot(2, 2, 3)
    bp = ax3.boxplot(valores, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][0].set_edgecolor('darkblue')
    bp['medians'][0].set_color('red')
    bp['medians'][0].set_linewidth(2)
    ax3.set_title('Diagrama de Caja de Similitudes', fontsize=14, fontweight='bold', pad=20)
    ax3.set_ylabel('Similitud Coseno', fontsize=11)
    ax3.set_xticklabels(['Todos los pares'])
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. TOP 10 PARES MÁS SIMILARES (Gráfico de barras)
    ax4 = plt.subplot(2, 2, 4)
    n = similitud_matrix.shape[0]
    pares = []
    for i in range(n):
        for j in range(i + 1, n):
            pares.append((i, j, similitud_matrix[i][j]))
    
    pares.sort(key=lambda x: x[2], reverse=True)
    top_10 = pares[:10]
    
    etiquetas = [f'{i}-{j}' for i, j, _ in top_10]
    similitudes = [sim for _, _, sim in top_10]
    
    bars = ax4.barh(range(len(etiquetas)), similitudes, color='coral', edgecolor='darkred')
    ax4.set_yticks(range(len(etiquetas)))
    ax4.set_yticklabels(etiquetas)
    ax4.set_xlabel('Similitud Coseno', fontsize=11)
    ax4.set_title('Top 10 Pares Más Similares', fontsize=14, fontweight='bold', pad=20)
    ax4.invert_yaxis()
    ax4.set_xlim(0, 1)
    ax4.grid(True, alpha=0.3, axis='x')
    
    # Agregar valores en las barras
    for i, (bar, sim) in enumerate(zip(bars, similitudes)):
        ax4.text(sim + 0.01, i, f'{sim:.3f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.suptitle('Análisis de Similitud de Textos usando Coseno', 
                 fontsize=16, fontweight='bold', y=1.00)
    plt.subplots_adjust(top=0.96)
    
    print("✅ Mostrando gráficas...")
    plt.show()

def mostrar_top_similares(df, similitud_matrix, top=10):
    """Muestra los pares de textos más similares"""
    print(f"\n🏆 TOP {top} PARES MÁS SIMILARES:")
    print("=" * 80)
    
    n = len(df)
    pares = []
    
    for i in range(n):
        for j in range(i + 1, n):
            pares.append((i, j, similitud_matrix[i][j]))
    
    # Ordenar por similitud descendente
    pares.sort(key=lambda x: x[2], reverse=True)
    
    for idx, (i, j, sim) in enumerate(pares[:top], 1):
        print(f"\n{idx}. Similitud: {sim:.4f}")
        print(f"   Texto {i}: {df.iloc[i][TEXT_COLUMN][:80]}...")
        print(f"   Texto {j}: {df.iloc[j][TEXT_COLUMN][:80]}...")
    
    print("=" * 80 + "\n")

def main():
    print("🚀 ANÁLISIS DE SIMILITUD DE TEXTOS CON COSENO\n")
    
    # 1. Cargar datos
    df = cargar_datos(INPUT_FILE)
    if df is None:
        return
    
    # 2. Verificar que existe la columna de texto
    if TEXT_COLUMN not in df.columns:
        print(f"❌ Error: La columna '{TEXT_COLUMN}' no existe en el archivo")
        print(f"   Columnas disponibles: {', '.join(df.columns)}")
        return
    
    # 3. Limpiar datos nulos
    df = df[df[TEXT_COLUMN].notna()].reset_index(drop=True)
    textos = df[TEXT_COLUMN].astype(str).tolist()
    
    print(f"📝 Total de textos a analizar: {len(textos)}\n")
    
    # 4. Calcular similitud coseno
    similitud_matrix, vectorizer = calcular_similitud_coseno(textos)
    
    # 5. Mostrar estadísticas
    valores = mostrar_estadisticas(similitud_matrix)
    
    # 6. Visualizar gráficas
    visualizar_similitudes(similitud_matrix, valores, df)
    
    # 7. Mostrar top similares
    mostrar_top_similares(df, similitud_matrix, top=10)
    
    # 8. Encontrar y guardar textos similares
    resultados_df = encontrar_textos_similares(df, similitud_matrix, UMBRAL_SIMILITUD)
    
    if len(resultados_df) > 0:
        print(f"✅ Se encontraron {len(resultados_df)} pares de textos similares")
        resultados_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"💾 Resultados guardados en: {OUTPUT_FILE}")
    else:
        print(f"⚠️  No se encontraron textos con similitud >= {UMBRAL_SIMILITUD}")
    
    # 9. Opción: Guardar matriz completa
    print("\n💡 Guardando matriz de similitud completa...")
    matriz_df = pd.DataFrame(
        similitud_matrix,
        columns=[f'Doc_{i}' for i in range(len(textos))],
        index=[f'Doc_{i}' for i in range(len(textos))]
    )
    matriz_df.to_csv('matriz_similitud_completa.csv', encoding='utf-8')
    print("✅ Matriz guardada en: matriz_similitud_completa.csv")
    
    print("\n🎉 ¡Análisis completado!")

if __name__ == "__main__":
    main()
