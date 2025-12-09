import os
import cv2
import glob

def resize_images_in_folder(folder_path, target_size=(64, 64)):
    """
    Redimensiona todas las imágenes en una carpeta al tamaño especificado
    y las renombra con numeración secuencial
    """
    # Extensiones de imagen soportadas
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    
    if not os.path.exists(folder_path):
        print(f"La carpeta {folder_path} no existe")
        return
    
    # Obtener el nombre de la carpeta para usar en el renombrado
    folder_name = os.path.basename(folder_path)
    image_count = 0
    counter = 1
    
    # Buscar todas las imágenes en la carpeta
    for extension in image_extensions:
        pattern = os.path.join(folder_path, extension)
        images = glob.glob(pattern)
        
        for image_path in images:
            try:
                # Leer la imagen
                img = cv2.imread(image_path)
                
                if img is None:
                    print(f"No se pudo leer: {image_path}")
                    continue
                
                # Redimensionar la imagen
                resized_img = cv2.resize(img, target_size)
                
                # Obtener la extensión original
                _, ext = os.path.splitext(image_path)
                
                # Crear el nuevo nombre de archivo
                new_filename = f"{folder_name}_{counter}{ext}"
                new_path = os.path.join(folder_path, new_filename)
                
                # Guardar la imagen redimensionada con el nuevo nombre
                cv2.imwrite(new_path, resized_img)
                
                # Si el archivo original tiene un nombre diferente, eliminarlo
                if image_path != new_path:
                    os.remove(image_path)
                
                image_count += 1
                counter += 1
                
                print(f"Redimensionada y renombrada: {new_filename}")
                
            except Exception as e:
                print(f"Error procesando {image_path}: {str(e)}")
    
    print(f"Total de imágenes procesadas en {folder_path}: {image_count}")

def main():
    # Obtener el directorio actual donde está el script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definir las carpetas a procesar
    folders = ['catarina', 'gato', 'hormiga','perro', 'tortuga']
    
    # Tamaño objetivo (ancho, alto) - puedes cambiar estos valores
    target_size = (64, 64)
    
    print(f"Iniciando redimensionamiento de imágenes a {target_size[0]}x{target_size[1]} píxeles...")
    
    for folder in folders:
        folder_path = os.path.join(current_dir, folder)
        print(f"\nProcesando carpeta: {folder}")
        resize_images_in_folder(folder_path, target_size)
    
    print("\n¡Redimensionamiento completado!")

if __name__ == "__main__":
    main()
