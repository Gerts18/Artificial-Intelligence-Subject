import json
from pathlib import Path

def json_to_txt(json_file_path, output_file_path=None):
    """
    Convierte un archivo JSON de posts de Facebook a formato TXT legible.
    
    Args:
        json_file_path: Ruta al archivo JSON de entrada
        output_file_path: Ruta al archivo TXT de salida (opcional)
    """
    # Cargar el archivo JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Si no se especifica archivo de salida, usar el mismo nombre con extensión .txt
    if output_file_path is None:
        output_file_path = Path(json_file_path).with_suffix('.txt')
    
    # Escribir el archivo TXT
    with open(output_file_path, 'w', encoding='utf-8') as f:
        # Encabezado
        f.write("=" * 80 + "\n")
        f.write(f"DATOS DE POSTS DE FACEBOOK\n")
        f.write(f"Total de posts: {data['total_posts']}\n")
        f.write(f"Fecha de extracción: {data['fecha_extraccion']}\n")
        f.write(f"Última actualización: {data['fecha_ultima_actualizacion']}\n")
        f.write("=" * 80 + "\n\n")
        
        # Recorrer cada post
        for i, post in enumerate(data['posts'], 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"POST #{i}\n")
            f.write(f"{'=' * 80}\n\n")
            
            f.write(f"URL: {post['url']}\n")
            f.write(f"Página: {post['nombre_pagina']}\n")
            f.write(f"Fecha: {post['fecha']}\n\n")
            
            # Descripción
            if post['descripcion']:
                f.write(f"DESCRIPCIÓN:\n")
                f.write(f"{'-' * 80}\n")
                f.write(f"{post['descripcion']}\n\n")
            
            # Comentarios
            f.write(f"COMENTARIOS ({len(post['comentarios'])}):\n")
            f.write(f"{'-' * 80}\n")
            
            if post['comentarios']:
                for j, comentario in enumerate(post['comentarios'], 1):
                    f.write(f"\n[Comentario {j}]\n")
                    f.write(f"{comentario['texto']}\n")
            else:
                f.write("No hay comentarios\n")
            
            f.write("\n")
    
    print(f"✓ Archivo convertido exitosamente: {output_file_path}")
    return output_file_path


if __name__ == "__main__":
    # Ejemplo de uso
    json_file = r"OLLAMA//scraping//posts_data_fb.json"
    
    # Convertir el archivo
    output_file = json_to_txt(json_file)
    
    print(f"\nArchivo de salida: {output_file}")
