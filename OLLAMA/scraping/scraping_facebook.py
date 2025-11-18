"""
Script para obtener datos de post de facebook
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import os

class FacebookScraper:
    def __init__(self):
        """Inicializa el navegador con opciones configuradas"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--headless')
        
        # Ruta al chromedriver local
        chromedriver_path = 'OLLAMA//scraping//chromedriver.exe'
        
        self.driver = webdriver.Chrome(
            service=Service(chromedriver_path),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)
    
    def scroll_to_load_comments(self):
        """Hace scroll para cargar más comentarios"""
        try:
            # Primero busca y hace clic en "Más relevantes"
            mas_relevantes_buttons = self.driver.find_elements(
                By.XPATH,
                "//div[@aria-haspopup='menu' and @tabindex='0' and @role='button']"
            )
            
            if mas_relevantes_buttons:
                print('ENCONTRADO - Más Comentarios')
                try:
                    time.sleep(1)
                    mas_relevantes_buttons[0].find_element(By.XPATH, "./ancestor::div[1]").click()
                    time.sleep(2)
                    
                    # Se abre menú y selecciona la tercera opción
                    menu_items = self.driver.find_elements(By.XPATH, "//div[@role='menuitem']//span[contains(text(), 'All comments')]")
                    if menu_items:
                        menu_items[0].click()
                        time.sleep(2)

                    else:
                        print(f"No se encontro el menu")
                except Exception as e:
                    print(f"Error al cambiar orden de comentarios: {e}")
            else:
                print("No se encontró el botón 'Más relevantes'")

        except Exception as e:
            print(f"Error general en scroll_to_load_comments: {e}")
    
    def scroll_gradual_para_cargar_comentarios(self, num_scrolls=10, comentarios_dict=None):
        """Hace scroll gradual y extrae comentarios en el proceso"""
        print(f"Haciendo scroll gradual en comentarios ({num_scrolls} veces)...")
        
        if comentarios_dict is None:
            comentarios_dict = {}
        
        try:
            # Busca el div con role='dialog' que es el contenedor con scroll
            contenedor_comentarios = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            
            if contenedor_comentarios:
                print("Contenedor de comentarios encontrado")
                contenedor = contenedor_comentarios[-1]
                
                sin_cambios = 0
                
                for i in range(num_scrolls):
                    # EXTRAE COMENTARIOS INDIVIDUALES (no el contenedor completo)
                    # Busca divs que tengan la estructura de un comentario individual
                    comentarios_actuales = self.driver.find_elements(
                        By.XPATH, 
                        "//div[@role='article']//div[contains(@class, 'x1lliihq') and contains(@class, 'xjkvuk6')]"
                    )
                    
                    # Guarda los comentarios visibles en este momento
                    comentarios_nuevos = 0
                    for comentario_elem in comentarios_actuales:
                        try:
                            # Extrae solo el texto del comentario, no todo el árbol
                            texto_completo = comentario_elem.text.strip()
                            
                            # Filtra textos muy largos (probablemente sea el contenedor completo)
                            if texto_completo and 10 < len(texto_completo) < 2000:
                                # Si no está guardado, lo agrega
                                if texto_completo not in comentarios_dict:
                                    # Extrae autor - busca el primer enlace dentro del comentario
                                    autor = ""
                                    try:
                                        autor_elem = comentario_elem.find_element(By.XPATH, ".//a[@role='link'][1]")
                                        autor = autor_elem.text.strip()
                                    except:
                                        try:
                                            # Intenta otra forma de encontrar el autor
                                            autor_elem = comentario_elem.find_element(By.XPATH, ".//span//a[1]")
                                            autor = autor_elem.text.strip()
                                        except:
                                            pass
                                    
                                    # Limpia el texto del comentario para quitar información extra
                                    # Elimina cosas como "5d", "Like", "Reply", etc al final
                                    lineas = texto_completo.split('\n')
                                    texto_limpio = '\n'.join([l for l in lineas if l and not l in ['Like', 'Reply', 'View', 'View more']])
                                    
                                    comentarios_dict[texto_completo] = {
                                        "autor": autor,
                                        "texto": texto_limpio
                                    }
                                    comentarios_nuevos += 1
                        except Exception as e:
                            continue
                    
                    print(f"Scroll {i+1}/{num_scrolls} - Total únicos: {len(comentarios_dict)} (+{comentarios_nuevos} nuevos)")
                    
                    # Ahora hace scroll
                    if comentarios_actuales:
                        ultimo_comentario = comentarios_actuales[-1]
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", ultimo_comentario)
                        time.sleep(2)
                    
                    # Verifica si se están cargando nuevos comentarios
                    if comentarios_nuevos == 0:
                        sin_cambios += 1
                        if sin_cambios >= 3:
                            print("No se cargan más comentarios nuevos")
                            break
                    else:
                        sin_cambios = 0
                    
            else:
                print("No se encontró el contenedor con scroll")
            
            print(f"Scroll completado - Total comentarios únicos: {len(comentarios_dict)}")
            return comentarios_dict
            
        except Exception as e:
            print(f"Error en scroll gradual: {e}")
            return comentarios_dict
    
    def extract_post_data(self, post_url):
        """Extrae todos los datos de un post específico"""
        print(f"Accediendo al post: {post_url}")
        self.driver.get(post_url)
        time.sleep(5)
        
        post_data = {
            "url": post_url,
            "nombre_pagina": "",
            "fecha": "",
            "descripcion": "",
            "comentarios": []
        }
        
        try:
            # Extraer nombre de la página/persona
            try:
                nombre_element = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-ad-rendering-role='profile_name']"))
                )
                post_data["nombre_pagina"] = nombre_element.text
            except:
                print("No se pudo extraer el nombre")
            
            # Extraer fecha
            try:
                fecha_elements = self.driver.find_elements(
                    By.XPATH, 
                    "//span[contains(@class, 'x4k7w5x')] | //abbr | //a[contains(@href, 'story_fbid')]//span"
                )
                for elem in fecha_elements:
                    if elem.text and len(elem.text) > 0:
                        post_data["fecha"] = elem.text
                        break
            except:
                print("No se pudo extraer la fecha")
            
            # Extraer descripción del post
            try:
                # Busca el botón "Ver más" y haz clic
                ver_mas_btns = self.driver.find_elements(
                    By.XPATH, 
                    "//div[contains(text(), 'Ver más') or contains(text(), 'See more')]"
                )
                if ver_mas_btns:
                    ver_mas_btns[0].click()
                    time.sleep(1)
                
                # Extrae la descripción
                descripcion_elements = self.driver.find_elements(
                    By.XPATH, 
                    "//div[@data-ad-preview='message'] | //div[contains(@class, 'x11i5rnm')]//span"
                )
                
                for elem in descripcion_elements:
                    text = elem.text.strip()
                    if text and len(text) > 10:
                        post_data["descripcion"] = text
                        break
            except:
                print("No se pudo extraer la descripción")
            
            # Cargar más comentarios
            print("Cargando comentarios...")
            
            # Primero cambia el orden a "Todos los comentarios"
            self.scroll_to_load_comments()
            
            # Luego hace scroll gradual Y EXTRAE comentarios durante el proceso
            comentarios_dict = {}
            comentarios_dict = self.scroll_gradual_para_cargar_comentarios(num_scrolls=20, comentarios_dict=comentarios_dict)
            
            # Convierte el diccionario a lista
            post_data["comentarios"] = list(comentarios_dict.values())
            
            print(f"Se extrajeron {len(post_data['comentarios'])} comentarios únicos")
        
        except Exception as e:
            print(f"Error al extraer datos del post: {e}")
        
        return post_data
    
    def extract_multiple_posts(self, post_urls):
        """Extrae datos de múltiples posts"""
        all_posts_data = []
        total_posts = len(post_urls)
        
        for idx, post_url in enumerate(post_urls, 1):
            print(f"\n{'='*60}")
            print(f"Procesando post {idx}/{total_posts}")
            print(f"{'='*60}")
            
            try:
                post_data = self.extract_post_data(post_url)
                all_posts_data.append(post_data)
                
                # Espera un poco entre posts para no sobrecargar
                if idx < total_posts:
                    print(f"\nEsperando antes del siguiente post...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Error al procesar el post {post_url}: {e}")
                # Agrega un post con error para mantener el registro
                all_posts_data.append({
                    "url": post_url,
                    "error": str(e),
                    "nombre_pagina": "",
                    "fecha": "",
                    "descripcion": "",
                    "comentarios": []
                })
        
        return all_posts_data
    
    def save_to_json(self, data, filename='post_data_fb.json'):
        """Guarda los datos en un archivo JSON"""
        filepath = f'OLLAMA//scraping//{filename}'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Datos guardados en: {filepath}")
    
    def save_multiple_posts_to_json(self, posts_data, filename='post_data_fb.json'):
        """Guarda múltiples posts en un archivo JSON (agrega a los existentes)"""
        filepath = f'OLLAMA//scraping//{filename}'
        
        # Intenta cargar datos existentes
        existing_data = {
            "total_posts": 0,
            "fecha_ultima_actualizacion": "",
            "posts": []
        }
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"Se encontraron {len(existing_data['posts'])} posts existentes")
            except Exception as e:
                print(f"No se pudo leer el archivo existente: {e}")
        
        # Agrega los nuevos posts a los existentes
        existing_data['posts'].extend(posts_data)
        existing_data['total_posts'] = len(existing_data['posts'])
        existing_data['fecha_ultima_actualizacion'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Guarda todo de nuevo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
        print(f"\n{'='*60}")
        print(f"Datos guardados en: {filepath}")
        print(f"Posts nuevos agregados: {len(posts_data)}")
        print(f"Total de posts en el archivo: {existing_data['total_posts']}")
        
        # Muestra resumen de comentarios por post nuevo
        for idx, post in enumerate(posts_data, 1):
            num_comentarios = len(post.get('comentarios', []))
            print(f"Nuevo post {idx}: {num_comentarios} comentarios")
        print(f"{'='*60}")
    
    def close(self):
        """Cierra el navegador"""
        self.driver.quit()


def main():
    """Función principal"""
    scraper = FacebookScraper()
    
    try:
        # CONFIGURACIÓN - Lista de URLs de posts a scrapear
        POST_URLS = [
            'https://www.facebook.com/share/p/17oHjXQoSb/'
            
        ]
        
        print(f"Se procesarán {len(POST_URLS)} posts")
        
        # Extrae datos de todos los posts
        all_posts_data = scraper.extract_multiple_posts(POST_URLS)
        
        # Guarda todos los datos en un JSON
        scraper.save_multiple_posts_to_json(all_posts_data)
        
        print("\n=== EXTRACCIÓN COMPLETADA ===")
        
    except Exception as e:
        print(f"Error general: {e}")
    
    finally:
        input("Presiona Enter para cerrar el navegador...")
        scraper.close()


if __name__ == "__main__":
    main()

