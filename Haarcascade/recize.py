import os
import cv2
import glob

def resize_images_in_folder(folder_path, target_size=(224, 224)):
    """
    Redimensiona todas las imágenes en una carpeta al tamaño especificado
    El script tiene que ejecutarse dentro de la carpeta donde se encuentran las imagenes que se van a redimencionar 
    """
    # Extensiones de imagen soportadas
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    
    if not os.path.exists(folder_path):
        print(f"La carpeta {folder_path} no existe")
        return
    
    image_count = 0
    
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
                
                # Guardar la imagen redimensionada
                cv2.imwrite(image_path, resized_img)
                image_count += 1
                
                print(f"Redimensionada: {os.path.basename(image_path)}")
                
            except Exception as e:
                print(f"Error procesando {image_path}: {str(e)}")
    
    print(f"Total de imágenes procesadas en {folder_path}: {image_count}")

def main():
    # Obtener el directorio actual donde está el script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definir las carpetas a procesar
    folders = ['happy', 'sad', 'angry']
    
    # Tamaño objetivo (ancho, alto) - puedes cambiar estos valores
    target_size = (100, 100)
    
    print(f"Iniciando redimensionamiento de imágenes a {target_size[0]}x{target_size[1]} píxeles...")
    
    for folder in folders:
        folder_path = os.path.join(current_dir, folder)
        print(f"\nProcesando carpeta: {folder}")
        resize_images_in_folder(folder_path, target_size)
    
    print("\n¡Redimensionamiento completado!")

if __name__ == "__main__":
    main()
