"""
Script para obtener datos de post de Twitter/X
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import os
import pandas as pd
from datetime import datetime
import pickle

class TwitterScraper:
    def __init__(self):
        """Inicializa el navegador con opciones configuradas"""
        options = uc.ChromeOptions()
        
        # Opciones para evitar detección
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--start-maximized')
        
        # User agent realista
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Usa undetected-chromedriver para evitar detección
        self.driver = uc.Chrome(
            options=options,
            version_main=None  # Detecta automáticamente la versión de Chrome
        )
        
        # Configuraciones adicionales anti-detección
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        self.cookies_file = 'RAG//recoleccion//twitter_cookies.pkl'
    
    def save_cookies(self):
        """Guarda las cookies de la sesión actual"""
        try:
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            print("✅ Cookies guardadas exitosamente")
        except Exception as e:
            print(f"❌ Error al guardar cookies: {e}")
    
    def load_cookies(self):
        """Carga las cookies guardadas"""
        try:
            if os.path.exists(self.cookies_file):
                # Primero navega a Twitter para establecer el dominio
                self.driver.get('https://x.com')
                time.sleep(2)
                
                # Luego carga las cookies
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        # Selenium 4 requiere que algunas propiedades sean eliminadas
                        if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                            cookie['sameSite'] = 'None'
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as e:
                            continue
                
                print("✅ Cookies cargadas exitosamente")
                # Recarga la página para aplicar las cookies
                self.driver.refresh()
                time.sleep(3)
                return True
            else:
                print("⚠️ No se encontraron cookies guardadas")
                return False
        except Exception as e:
            print(f"❌ Error al cargar cookies: {e}")
            return False
    
    def is_logged_in(self):
        """Verifica si el usuario está logueado en Twitter"""
        try:
            # Busca elementos que solo aparecen cuando estás logueado
            self.driver.find_element(By.XPATH, "//a[@aria-label='Profile' or @data-testid='AppTabBar_Profile_Link']")
            return True
        except:
            return False
    
    def scroll_gradual_para_cargar_respuestas(self, num_scrolls=15, respuestas_dict=None):
        """Hace scroll gradual y extrae respuestas/replies en el proceso"""
        print(f"Haciendo scroll gradual en respuestas ({num_scrolls} veces)...")
        
        if respuestas_dict is None:
            respuestas_dict = {}
        
        try:
            sin_cambios = 0
            
            for i in range(num_scrolls):
                # Busca los artículos que contienen los tweets/replies
                # En Twitter, cada tweet/reply está dentro de un article element
                respuestas_actuales = self.driver.find_elements(
                    By.XPATH, 
                    "//article[@data-testid='tweet']"
                )
                
                # Guarda las respuestas visibles en este momento
                respuestas_nuevas = 0
                for respuesta_elem in respuestas_actuales:
                    try:
                        # Extrae el texto del tweet/reply
                        texto_elem = respuesta_elem.find_elements(
                            By.XPATH, 
                            ".//div[@data-testid='tweetText']"
                        )
                        
                        if texto_elem:
                            texto_completo = texto_elem[0].text.strip()
                            
                            # Filtra textos vacíos o muy cortos
                            if texto_completo and len(texto_completo) > 0:
                                # Si no está guardado, lo agrega
                                if texto_completo not in respuestas_dict:
                                    # Extrae autor
                                    autor = ""
                                    try:
                                        # Busca el nombre de usuario
                                        autor_elem = respuesta_elem.find_element(
                                            By.XPATH, 
                                            ".//div[@data-testid='User-Name']//span"
                                        )
                                        autor = autor_elem.text.strip()
                                    except:
                                        try:
                                            # Intenta con otro selector
                                            autor_elem = respuesta_elem.find_element(
                                                By.XPATH,
                                                ".//a[contains(@href, '/')]//span"
                                            )
                                            autor = autor_elem.text.strip()
                                        except:
                                            pass
                                    
                                    # Extrae fecha/tiempo
                                    fecha = ""
                                    try:
                                        fecha_elem = respuesta_elem.find_element(
                                            By.XPATH,
                                            ".//time"
                                        )
                                        fecha = fecha_elem.get_attribute('datetime')
                                    except:
                                        pass
                                    
                                    respuestas_dict[texto_completo] = {
                                        "autor": autor,
                                        "texto": texto_completo,
                                        "fecha": fecha
                                    }
                                    respuestas_nuevas += 1
                    except Exception as e:
                        continue
                
                print(f"Scroll {i+1}/{num_scrolls} - Total únicos: {len(respuestas_dict)} (+{respuestas_nuevas} nuevos)")
                
                # Hace scroll hacia abajo
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Verifica si se están cargando nuevas respuestas
                if respuestas_nuevas == 0:
                    sin_cambios += 1
                    if sin_cambios >= 3:
                        print("No se cargan más respuestas nuevas")
                        break
                else:
                    sin_cambios = 0
            
            print(f"Scroll completado - Total respuestas únicas: {len(respuestas_dict)}")
            return respuestas_dict
            
        except Exception as e:
            print(f"Error en scroll gradual: {e}")
            return respuestas_dict
    
    def extract_tweet_data(self, tweet_url):
        """Extrae todos los datos de un tweet específico"""
        print(f"Accediendo al tweet: {tweet_url}")
        self.driver.get(tweet_url)
        time.sleep(5)
        
        tweet_data = {
            "url": tweet_url,
            "autor": "",
            "usuario": "",
            "fecha": "",
            "contenido": "",
            "likes": "",
            "retweets": "",
            "respuestas": []
        }
        
        try:
            # Busca el tweet principal (primer article)
            tweet_principal = self.driver.find_element(
                By.XPATH,
                "//article[@data-testid='tweet'][1]"
            )
            
            # Extraer autor
            try:
                autor_elem = tweet_principal.find_element(
                    By.XPATH,
                    ".//div[@data-testid='User-Name']//span"
                )
                tweet_data["autor"] = autor_elem.text
                
                # Extrae el handle/usuario
                usuario_elem = tweet_principal.find_element(
                    By.XPATH,
                    ".//div[@data-testid='User-Name']//a[contains(@href, '/')]"
                )
                tweet_data["usuario"] = usuario_elem.get_attribute('href').split('/')[-1]
            except Exception as e:
                print(f"No se pudo extraer el autor: {e}")
            
            # Extraer fecha
            try:
                fecha_elem = tweet_principal.find_element(
                    By.XPATH,
                    ".//time"
                )
                tweet_data["fecha"] = fecha_elem.get_attribute('datetime')
            except Exception as e:
                print(f"No se pudo extraer la fecha: {e}")
            
            # Extraer contenido del tweet
            try:
                contenido_elem = tweet_principal.find_element(
                    By.XPATH,
                    ".//div[@data-testid='tweetText']"
                )
                tweet_data["contenido"] = contenido_elem.text
            except Exception as e:
                print(f"No se pudo extraer el contenido: {e}")
            
            # Extraer métricas (likes, retweets, etc)
            try:
                # Busca los botones de interacción
                metricas = tweet_principal.find_elements(
                    By.XPATH,
                    ".//div[@role='group']//button"
                )
                
                for metrica in metricas:
                    aria_label = metrica.get_attribute('aria-label')
                    if aria_label:
                        if 'like' in aria_label.lower():
                            tweet_data["likes"] = aria_label
                        elif 'retweet' in aria_label.lower() or 'repost' in aria_label.lower():
                            tweet_data["retweets"] = aria_label
            except Exception as e:
                print(f"No se pudieron extraer las métricas: {e}")
            
            # Cargar más respuestas
            print("Cargando respuestas...")
            
            # Hace scroll gradual Y EXTRAE respuestas durante el proceso
            respuestas_dict = {}
            respuestas_dict = self.scroll_gradual_para_cargar_respuestas(num_scrolls=20, respuestas_dict=respuestas_dict)
            
            # Convierte el diccionario a lista y elimina el tweet principal
            all_respuestas = list(respuestas_dict.values())
            
            # Filtra el tweet principal de las respuestas
            tweet_data["respuestas"] = [
                r for r in all_respuestas 
                if r.get('texto', '') != tweet_data.get('contenido', '')
            ]
            
            print(f"Se extrajeron {len(tweet_data['respuestas'])} respuestas únicas")
        
        except Exception as e:
            print(f"Error al extraer datos del tweet: {e}")
        
        return tweet_data
    
    def extract_multiple_tweets(self, tweet_urls):
        """Extrae datos de múltiples tweets"""
        all_tweets_data = []
        total_tweets = len(tweet_urls)
        
        for idx, tweet_url in enumerate(tweet_urls, 1):
            print(f"\n{'='*60}")
            print(f"Procesando tweet {idx}/{total_tweets}")
            print(f"{'='*60}")
            
            try:
                tweet_data = self.extract_tweet_data(tweet_url)
                all_tweets_data.append(tweet_data)
                
                # Espera un poco entre tweets para no sobrecargar
                if idx < total_tweets:
                    print(f"\nEsperando antes del siguiente tweet...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Error al procesar el tweet {tweet_url}: {e}")
                # Agrega un tweet con error para mantener el registro
                all_tweets_data.append({
                    "url": tweet_url,
                    "error": str(e),
                    "autor": "",
                    "usuario": "",
                    "fecha": "",
                    "contenido": "",
                    "likes": "",
                    "retweets": "",
                    "respuestas": []
                })
        
        return all_tweets_data
    
    def save_multiple_tweets_to_json(self, tweets_data, filename='posts_data_x.json'):
        """Guarda múltiples tweets en un archivo JSON (agrega a los existentes)"""
        filepath = f'RAG//recoleccion//{filename}'
        
        # Intenta cargar datos existentes
        existing_data = {
            "total_tweets": 0,
            "fecha_ultima_actualizacion": "",
            "tweets": []
        }
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"Se encontraron {len(existing_data['tweets'])} tweets existentes")
            except Exception as e:
                print(f"No se pudo leer el archivo existente: {e}")
        
        # Agrega los nuevos tweets a los existentes
        existing_data['tweets'].extend(tweets_data)
        existing_data['total_tweets'] = len(existing_data['tweets'])
        existing_data['fecha_ultima_actualizacion'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Guarda todo de nuevo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
        print(f"\n{'='*60}")
        print(f"Datos guardados en: {filepath}")
        print(f"Tweets nuevos agregados: {len(tweets_data)}")
        print(f"Total de tweets en el archivo: {existing_data['total_tweets']}")
        
        # Muestra resumen de respuestas por tweet nuevo
        for idx, tweet in enumerate(tweets_data, 1):
            num_respuestas = len(tweet.get('respuestas', []))
            print(f"Nuevo tweet {idx}: {num_respuestas} respuestas")
        print(f"{'='*60}")
    
    def json_to_excel(self, json_file='posts_data_x.json', excel_file='respuestas_twitter.csv'):
        """
        Convierte el JSON de tweets a un archivo Excel/CSV con todas las respuestas
        Formato compatible con el script de limpieza
        """
        filepath_json = f'RAG//recoleccion//{json_file}'
        filepath_excel = f'RAG//recoleccion//{excel_file}'
        
        print(f"\n{'='*60}")
        print("Convirtiendo JSON a Excel...")
        print(f"{'='*60}")
        
        try:
            # Carga el JSON
            with open(filepath_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Lista para almacenar todas las respuestas
            respuestas_lista = []
            
            # Recorre todos los tweets
            for tweet in data.get('tweets', []):
                url_tweet = tweet.get('url', '')
                autor_tweet = tweet.get('autor', '')
                usuario_tweet = tweet.get('usuario', '')
                fecha_tweet = tweet.get('fecha', '')
                contenido_tweet = tweet.get('contenido', '')
                likes_tweet = tweet.get('likes', '')
                retweets_tweet = tweet.get('retweets', '')
                
                # Recorre todas las respuestas del tweet
                for respuesta in tweet.get('respuestas', []):
                    respuestas_lista.append({
                        'texto': respuesta.get('texto', ''),
                        'autor_respuesta': respuesta.get('autor', ''),
                        'fecha_respuesta': respuesta.get('fecha', ''),
                        'autor_tweet': autor_tweet,
                        'usuario_tweet': usuario_tweet,
                        'fecha_tweet': fecha_tweet,
                        'url_tweet': url_tweet,
                        'contenido_tweet': contenido_tweet[:200] + '...' if len(contenido_tweet) > 200 else contenido_tweet,
                        'likes': likes_tweet,
                        'retweets': retweets_tweet,
                        'fecha_extraccion': data.get('fecha_ultima_actualizacion', '')
                    })
            
            # Crea DataFrame
            df = pd.DataFrame(respuestas_lista)
            
            # Agrega columna de ID
            df.insert(0, 'id', range(1, len(df) + 1))
            
            # Guarda en CSV (compatible con Excel)
            df.to_csv(filepath_excel, index=False, encoding='utf-8-sig')
            
            print(f"✅ Excel generado: {filepath_excel}")
            print(f"📊 Total de respuestas: {len(df)}")
            print(f"📝 Columnas: {list(df.columns)}")
            print(f"\n{'='*60}")
            
            # Muestra estadísticas
            print("\n📈 Estadísticas:")
            print(f"  - Respuestas totales: {len(df)}")
            print(f"  - Tweets procesados: {len(data.get('tweets', []))}")
            print(f"  - Autores de tweets únicos: {df['autor_tweet'].nunique()}")
            print(f"  - Autores de respuestas únicos: {df['autor_respuesta'].nunique()}")
            
            # Muestra ejemplo de las primeras respuestas
            print(f"\n📋 Primeras 3 respuestas:")
            for i in range(min(3, len(df))):
                print(f"\n{i+1}. {df.iloc[i]['texto'][:100]}...")
                print(f"   Autor: {df.iloc[i]['autor_respuesta']}")
                print(f"   Tweet original: @{df.iloc[i]['usuario_tweet']}")
            
            return df
            
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {filepath_json}")
            return None
        except Exception as e:
            print(f"❌ Error al convertir JSON a Excel: {e}")
            return None
    
    def close(self):
        """Cierra el navegador"""
        self.driver.quit()


def main():
    """Función principal"""
    scraper = TwitterScraper()
    
    try:
        # CONFIGURACIÓN - Lista de URLs de tweets a scrapear
        TWEET_URLS = [
            'https://x.com/pitiklinov/status/1970145986317025595',
            'https://x.com/JoseMarioMX/status/1997355040219021443',
            'https://x.com/JoseMarioMX/status/1992423599018266913',
            'https://x.com/bitacorabeagle/status/1931457470427488477'
        ]
        
        print(f"Se procesarán {len(TWEET_URLS)} tweets")
        print("\n⚠️  IMPORTANTE: Sistema de cookies para mantener sesión")
        print("⚠️  Solo necesitas iniciar sesión una vez\n")
        
        # Intenta cargar cookies existentes
        print("Intentando cargar sesión guardada...")
        cookies_loaded = scraper.load_cookies()
        
        if cookies_loaded:
            print("\n✅ Sesión cargada desde cookies")
            # Verifica si realmente está logueado
            scraper.driver.get('https://x.com/home')
            time.sleep(3)
            
            if scraper.is_logged_in():
                print("✅ Sesión activa confirmada")
            else:
                print("⚠️ Las cookies expiraron, necesitas iniciar sesión de nuevo")
                cookies_loaded = False
        
        if not cookies_loaded:
            # Si no hay cookies o expiraron, pide login manual
            print("\n📝 INSTRUCCIONES PARA INICIAR SESIÓN:")
            print("   1. Se abrirá Twitter/X en el navegador")
            print("   2. Inicia sesión MANUALMENTE (no uses modo rápido)")
            print("   3. Si pide verificación, complétala")
            print("   4. Espera a ver tu timeline/inicio")
            print("   5. Regresa aquí y presiona Enter\n")
            
            scraper.driver.get('https://x.com/login')
            
            input("👉 Presiona Enter SOLO cuando hayas iniciado sesión completamente...")
            
            # Verifica el login
            scraper.driver.get('https://x.com/home')
            time.sleep(3)
            
            if scraper.is_logged_in():
                print("\n✅ Login exitoso! Guardando sesión para futuros usos...")
                scraper.save_cookies()
            else:
                print("\n❌ Parece que no se completó el login correctamente")
                input("   Intenta de nuevo y presiona Enter cuando estés logueado...")
                
                if scraper.is_logged_in():
                    print("\n✅ Login exitoso! Guardando sesión...")
                    scraper.save_cookies()
                else:
                    raise Exception("No se pudo verificar el login en Twitter")
        
        # Extrae datos de todos los tweets
        all_tweets_data = scraper.extract_multiple_tweets(TWEET_URLS)
        
        # Guarda todos los datos en un JSON
        scraper.save_multiple_tweets_to_json(all_tweets_data)
        
        # Convierte el JSON a Excel/CSV
        scraper.json_to_excel()
        
        print("\n=== EXTRACCIÓN COMPLETADA ===")
        print("✅ Archivos generados:")
        print("   - posts_data_x.json (datos completos)")
        print("   - respuestas_twitter.csv (listo para limpieza)")
        
    except Exception as e:
        print(f"Error general: {e}")
    
    finally:
        input("Presiona Enter para cerrar el navegador...")
        scraper.close()


if __name__ == "__main__":
    main()
