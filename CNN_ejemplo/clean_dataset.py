import os
from PIL import Image
import shutil
import warnings

dataset_path = os.path.join(os.getcwd(), 'CNN_ejemplo/animals-dataset')
corrupted_folder = os.path.join(os.getcwd(), 'corrupted_images')

# Crear carpeta para imágenes corruptas
os.makedirs(corrupted_folder, exist_ok=True)

# Suprimir warnings de PIL para capturarlos como errores
warnings.filterwarnings('error')

print("Escaneando y limpiando dataset...")
corrupted_count = 0
converted_count = 0
total_count = 0

for class_folder in os.listdir(dataset_path):
    folder_path = os.path.join(dataset_path, class_folder)
    
    if not os.path.isdir(folder_path):
        continue
    
    print(f"\nProcesando carpeta: {class_folder}")
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        total_count += 1
        
        try:
            # Intentar abrir y verificar la imagen
            with Image.open(file_path) as img:
                img.verify()
                
            # Segunda verificación: cargar completamente
            with Image.open(file_path) as img:
                img.load()
                
                # Si es TIFF, PNG con transparencia o tiene problemas, convertir a JPG
                if img.format in ['TIFF', 'TIF'] or img.mode in ['P', 'RGBA', 'LA']:
                    print(f"  ⚠ Convirtiendo {filename} ({img.format}, {img.mode}) -> JPG")
                    
                    # Convertir a RGB
                    rgb_img = img.convert('RGB')
                    
                    # Guardar como JPG en el mismo lugar
                    new_filename = os.path.splitext(filename)[0] + '.jpg'
                    new_path = os.path.join(folder_path, new_filename)
                    rgb_img.save(new_path, 'JPEG', quality=95)
                    
                    # Eliminar original si tiene diferente nombre
                    if new_filename != filename:
                        os.remove(file_path)
                    
                    converted_count += 1
                    
        except Exception as e:
            print(f"  ✗ Corrupta: {filename}")
            print(f"    Error: {str(e)[:100]}")
            
            # Mover archivo corrupto
            dest_path = os.path.join(corrupted_folder, f"{class_folder}_{filename}")
            try:
                shutil.move(file_path, dest_path)
                corrupted_count += 1
            except:
                print(f"    No se pudo mover el archivo")

print(f"\n{'='*60}")
print(f"Limpieza completada:")
print(f"  Total de archivos escaneados: {total_count}")
print(f"  Corruptos movidos: {corrupted_count}")
print(f"  Convertidos a JPG: {converted_count}")
print(f"  Válidos finales: {total_count - corrupted_count}")
if corrupted_count > 0:
    print(f"\n  Archivos corruptos en: {corrupted_folder}")
print(f"{'='*60}")
