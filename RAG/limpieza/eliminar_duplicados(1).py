"""
Script para eliminar filas duplicadas del dataset
Opciones: duplicados exactos, duplicados de texto, duplicados normalizados
"""

import pandas as pd
import re


def normalizar_para_comparacion(texto: str) -> str:
    """
    Normaliza texto para comparación de duplicados
    (minúsculas, sin espacios extras, sin puntuación)
    """
    if not isinstance(texto, str):
        return ""
    
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def eliminar_duplicados(archivo_entrada: str,
                       archivo_salida: str = "dataset_sin_duplicados.csv",
                       modo: str = "texto",
                       columna_texto: str = "texto",
                       mantener: str = "first") -> pd.DataFrame:
    """
    Elimina filas duplicadas del dataset
    
    Args:
        archivo_entrada: Ruta al archivo CSV de entrada
        archivo_salida: Ruta al archivo CSV de salida
        modo: Modo de detección de duplicados:
            - "exacto": Duplicados en todas las columnas
            - "texto": Duplicados en la columna de texto (case-sensitive)
            - "normalizado": Duplicados de texto normalizado (case-insensitive)
        columna_texto: Nombre de la columna con el texto
        mantener: 'first' (mantener primera ocurrencia) o 'last' (mantener última)
        
    Returns:
        DataFrame sin duplicados
    """
    print(f"📂 Cargando datos desde: {archivo_entrada}")
    df = pd.read_csv(archivo_entrada)
    
    total_inicial = len(df)
    print(f"📊 Total de registros inicial: {total_inicial}")
    
    # Identificar duplicados según el modo
    if modo == "exacto":
        print("\n🔍 Buscando duplicados exactos (todas las columnas)...")
        df_limpio = df.drop_duplicates(keep=mantener)
        
    elif modo == "texto":
        print(f"\n🔍 Buscando duplicados en columna '{columna_texto}' (exactos)...")
        if columna_texto not in df.columns:
            raise ValueError(f"La columna '{columna_texto}' no existe en el dataset")
        df_limpio = df.drop_duplicates(subset=[columna_texto], keep=mantener)
        
    elif modo == "normalizado":
        print(f"\n🔍 Buscando duplicados de texto normalizado...")
        if columna_texto not in df.columns:
            raise ValueError(f"La columna '{columna_texto}' no existe en el dataset")
        
        # Crear columna temporal con texto normalizado
        df['_texto_normalizado_temp'] = df[columna_texto].apply(normalizar_para_comparacion)
        
        # Eliminar duplicados basados en texto normalizado
        df_limpio = df.drop_duplicates(subset=['_texto_normalizado_temp'], keep=mantener)
        
        # Eliminar columna temporal
        df_limpio = df_limpio.drop(columns=['_texto_normalizado_temp'])
        
    else:
        raise ValueError(f"Modo '{modo}' no válido. Usa: 'exacto', 'texto' o 'normalizado'")
    
    total_final = len(df_limpio)
    duplicados_eliminados = total_inicial - total_final
    porcentaje = (duplicados_eliminados / total_inicial * 100) if total_inicial > 0 else 0
    
    # Estadísticas
    print("\n📈 Resultados:")
    print(f"  ✅ Registros originales:     {total_inicial}")
    print(f"  ❌ Duplicados eliminados:    {duplicados_eliminados}")
    print(f"  ✅ Registros únicos:         {total_final}")
    print(f"  📊 Porcentaje eliminado:     {porcentaje:.2f}%")
    
    # Guardar resultado
    if archivo_salida:
        print(f"\n💾 Guardando dataset limpio en: {archivo_salida}")
        df_limpio.to_csv(archivo_salida, index=False, encoding='utf-8')
        print("✅ Archivo guardado exitosamente")
    
    return df_limpio


def mostrar_ejemplos_duplicados(archivo_entrada: str, 
                                columna_texto: str = "texto",
                                n: int = 5):
    """
    Muestra ejemplos de textos duplicados encontrados
    
    Args:
        archivo_entrada: Ruta al archivo CSV
        columna_texto: Nombre de la columna con el texto
        n: Número de ejemplos a mostrar
    """
    print(f"\n📋 Analizando duplicados en: {archivo_entrada}\n")
    print("=" * 100)
    
    df = pd.read_csv(archivo_entrada)
    
    if columna_texto not in df.columns:
        print(f"❌ La columna '{columna_texto}' no existe")
        return
    
    # Encontrar duplicados exactos
    duplicados_exactos = df[df.duplicated(subset=[columna_texto], keep=False)]
    
    if len(duplicados_exactos) == 0:
        print("✅ No se encontraron duplicados exactos")
    else:
        print(f"🔍 Duplicados exactos encontrados: {len(duplicados_exactos)} filas")
        print(f"\nMostrando hasta {n} grupos de duplicados:\n")
        
        # Agrupar por texto duplicado
        grupos = duplicados_exactos.groupby(columna_texto)
        
        for i, (texto, grupo) in enumerate(grupos):
            if i >= n:
                break
            
            print(f"Grupo {i+1}: {len(grupo)} repeticiones")
            print(f"Texto: {texto[:150]}...")
            print(f"IDs: {list(grupo['id'].values) if 'id' in grupo.columns else 'N/A'}")
            print("-" * 100)
    
    # Encontrar duplicados normalizados
    df['_texto_norm'] = df[columna_texto].apply(normalizar_para_comparacion)
    duplicados_norm = df[df.duplicated(subset=['_texto_norm'], keep=False)]
    duplicados_solo_norm = duplicados_norm[~duplicados_norm.duplicated(subset=[columna_texto], keep=False)]
    
    if len(duplicados_solo_norm) > 0:
        print(f"\n🔍 Duplicados normalizados (diferentes en mayúsculas/puntuación): {len(duplicados_solo_norm)} filas")


def analisis_completo(archivo_entrada: str, columna_texto: str = "texto"):
    """
    Realiza un análisis completo de duplicados en el dataset
    """
    print("\n" + "="*100)
    print("📊 ANÁLISIS COMPLETO DE DUPLICADOS")
    print("="*100)
    
    df = pd.read_csv(archivo_entrada)
    total = len(df)
    
    # Duplicados exactos (todas las columnas)
    dup_exactos = df.duplicated(keep=False).sum()
    print(f"\n1️⃣ Duplicados exactos (todas las columnas): {dup_exactos} ({dup_exactos/total*100:.2f}%)")
    
    # Duplicados de texto
    dup_texto = df.duplicated(subset=[columna_texto], keep=False).sum()
    print(f"2️⃣ Duplicados de texto (columna '{columna_texto}'): {dup_texto} ({dup_texto/total*100:.2f}%)")
    
    # Duplicados normalizados
    df['_texto_norm'] = df[columna_texto].apply(normalizar_para_comparacion)
    dup_norm = df.duplicated(subset=['_texto_norm'], keep=False).sum()
    print(f"3️⃣ Duplicados normalizados (case-insensitive): {dup_norm} ({dup_norm/total*100:.2f}%)")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    # Configuración
    ARCHIVO_ENTRADA = "RAG//dataset_sintetico_5000_ampliado.csv"
    ARCHIVO_SALIDA = "dataset_sin_duplicados.csv"
    
    # Modo de eliminación:
    # "exacto"      - Elimina filas 100% idénticas en todas las columnas
    # "texto"       - Elimina filas con texto idéntico (case-sensitive)
    # "normalizado" - Elimina filas con texto similar (ignora mayúsculas/puntuación)
    MODO = "normalizado"
    
    # Columna que contiene el texto
    COLUMNA_TEXTO = "texto"
    
    # Qué ocurrencia mantener: "first" (primera) o "last" (última)
    MANTENER = "first"
    
    try:
        # Análisis completo de duplicados
        analisis_completo(ARCHIVO_ENTRADA, COLUMNA_TEXTO)
        
        # Mostrar ejemplos de duplicados
        mostrar_ejemplos_duplicados(ARCHIVO_ENTRADA, COLUMNA_TEXTO, n=3)
        
        # Eliminar duplicados
        print("\n" + "="*100)
        print("🧹 ELIMINANDO DUPLICADOS")
        print("="*100)
        
        df_limpio = eliminar_duplicados(
            archivo_entrada=ARCHIVO_ENTRADA,
            archivo_salida=ARCHIVO_SALIDA,
            modo=MODO,
            columna_texto=COLUMNA_TEXTO,
            mantener=MANTENER
        )
        
        print("\n✨ ¡Proceso completado exitosamente!")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{ARCHIVO_ENTRADA}'")
        print("   Verifica la ruta del archivo")
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
