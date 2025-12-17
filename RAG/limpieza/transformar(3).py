import pandas as pd
import os

# --- CONFIGURACIÓN ---
# Cambia esto por el nombre real de tu archivo
INPUT_FILE = 'RAG//limpieza//dataset_limpio.csv' 
OUTPUT_FILE = 'corpus_narrativo_tweets_sinteticos.txt'

def crear_narrativa(row):
    """
    Toma una fila del DataFrame y la convierte en un párrafo narrativo
    rico en palabras clave para el modelo de embeddings.
    """
    # Extraemos datos, manejando posibles valores vacíos
    fecha = row.get('fecha', 'fecha desconocida')
    usuario = row.get('usuario', 'usuario anónimo')
    tema = row.get('tema', 'General')
    sentimiento = row.get('sentimiento', 'Neutro')
    texto = row.get('texto', '')
    likes = row.get('likes', 0)
    repost = row.get('reposts', 0)
    
    # Para dataset de tweets
    #tipo = row.get('tipo', 'tweet')
    
    # Construcción de la narrativa semántica
    # NOTA: Repetimos palabras clave como "tema", "sentimiento" y "contenido" 
    # para reforzar la asociación en el espacio vectorial.
    narrativa = (
        f"## Registro Tweets - ID: {row.get('id', 'N/A') + 200}\n"
        f"Fecha {fecha}, Usuario:'{usuario}' "
        f"Tema **{tema}**.\n"
        f"Sentimiento detectado: **{sentimiento}**.\n\n"
        #f"Contenido {tipo}:\n"
        f"\"{texto}\"\n\n"
        f"Generó {likes} reacciones (likes) "
        f"compartida (repost) {repost} veces.\n"
        f"---" 
    )
    return narrativa

def main():
    print(f"🔄 Leyendo archivo: {INPUT_FILE}...")
    
    try:
        # Leemos el CSV (usamos encoding utf-8 para tildes y emojis)
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
        
        # Opcional: Si tu CSV usa ';' en lugar de ',' cambia a: sep=';'
        
        print(f"✅ Se cargaron {len(df)} registros.")
        print("🔄 Procesando y transformando datos a narrativa...")

        # Aplicamos la función fila por fila
        narrativas = df.apply(crear_narrativa, axis=1)

        # Guardamos todo en un solo archivo de texto grande
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # Escribimos una cabecera general para darle contexto al LLM
            f.write("# GEN Z, TECNOLOGÍA Y FILOSOFÍA\n")
            f.write("Este documento contiene registros de redes sociales para análisis sociológico.\n\n")
            
            # Unimos todas las narrativas separadas por saltos de línea
            f.write('\n\n'.join(narrativas))
            
        print(f"🚀 ¡Éxito! Archivo generado: {OUTPUT_FILE}")
        print("   Ahora puedes subir este archivo a tu Workspace en AnythingLLM.")

    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo '{INPUT_FILE}'. Verifica el nombre.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()