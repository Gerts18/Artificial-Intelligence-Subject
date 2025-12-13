import pygame
from queue import PriorityQueue
import math

pygame.init()

info_pantalla = pygame.display.Info()
ANCHO_PANTALLA = info_pantalla.current_w
ALTO_PANTALLA = info_pantalla.current_h

ANCHO_VENTANA = min(int(ANCHO_PANTALLA * 0.8), 1200)  
ALTO_VENTANA = min(int(ALTO_PANTALLA * 0.8), 900)    
PANEL_LATERAL = int(ANCHO_VENTANA * 0.2)  

VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
pygame.display.set_caption("Algoritmo A* - Búsqueda de Caminos")

# Fuentes mejoradas
FUENTE_TITULO = pygame.font.Font(None, 28)
FUENTE = pygame.font.Font(None, 22)
FUENTE_PEQUEÑA = pygame.font.Font(None, 18)
FUENTE_NODO = pygame.font.Font(None, 16)

# Paleta de colores moderna
BLANCO = (250, 250, 252)  
NEGRO = (45, 45, 55)      
GRIS = (200, 200, 210)    
VERDE = (76, 175, 80)     
ROJO = (244, 67, 54)      
NARANJA = (255, 152, 0)   
PURPURA = (156, 39, 176) 
AZUL = (33, 150, 243)     
AMARILLO = (255, 235, 59)  
GRIS_CLARO = (240, 240, 245)
TEXTO = (33, 33, 33)
TEXTO_CLARO = (100, 100, 110)

class Nodo:
    def __init__(self, fila, col, ancho, total_filas):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.total_filas = total_filas

    def get_pos(self):
        return self.fila, self.col

    def es_pared(self):
        return self.color == NEGRO

    def es_inicio(self):
        return self.color == NARANJA

    def es_fin(self):
        return self.color == PURPURA

    def restablecer(self):
        self.color = BLANCO

    def hacer_inicio(self):
        self.color = NARANJA

    def hacer_pared(self):
        self.color = NEGRO

    def hacer_fin(self):
        self.color = PURPURA

    def hacer_camino(self):
        self.color = VERDE

    def hacer_visitado(self):
        self.color = ROJO

    def hacer_alternativo(self):
        self.color = AZUL

    def hacer_abierto(self):
        self.color = AMARILLO

    def dibujar(self, ventana):
        # Dibuja el nodo con bordes redondeados
        pygame.draw.rect(ventana, self.color, (self.x + 1, self.y + 1, self.ancho - 2, self.ancho - 2), border_radius=4)
        
        # Si el nodo está siendo evaluado (amarillo o rojo), mostrar los costos
        if self.color in [AMARILLO, ROJO, VERDE] and hasattr(self, 'g_cost') and hasattr(self, 'h_cost') and self.ancho > 40:
            # Fondo semi-transparente para mejorar legibilidad
            s = pygame.Surface((self.ancho - 4, self.ancho - 4))
            s.set_alpha(180)
            s.fill(BLANCO)
            ventana.blit(s, (self.x + 2, self.y + 2))
            
            # Textos de costos
            g_texto = FUENTE_NODO.render(f"g:{self.g_cost:.1f}", True, TEXTO)
            h_texto = FUENTE_NODO.render(f"h:{self.h_cost:.1f}", True, TEXTO)
            f_valor = self.g_cost + self.h_cost
            f_texto = FUENTE_NODO.render(f"f:{f_valor:.1f}", True, AZUL)
            
            # Posicionar textos verticalmente
            ventana.blit(g_texto, (self.x + 5, self.y + 5))
            ventana.blit(h_texto, (self.x + 5, self.y + self.ancho // 2 - 4))
            ventana.blit(f_texto, (self.x + 5, self.y + self.ancho - 18))

    def actualizar_vecinos(self, grid):
        self.vecinos = []
        # Movimientos: arriba, abajo, izquierda, derecha, y 4 diagonales
        # Formato: (delta_fila, delta_col, costo)
        movimientos = [
            (-1, 0, 1),   # Arriba
            (1, 0, 1),    # Abajo
            (0, -1, 1),   # Izquierda
            (0, 1, 1),    # Derecha
            (-1, -1, 1.414), # Diagonal arriba-izquierda
            (-1, 1, 1.414),  # Diagonal arriba-derecha
            (1, -1, 1.414),  # Diagonal abajo-izquierda
            (1, 1, 1.414)    # Diagonal abajo-derecha
        ]
        
        for delta_f, delta_c, costo in movimientos:
            nueva_fila = self.fila + delta_f
            nueva_col = self.col + delta_c
            
            # Verificar que esté dentro de los límites
            if 0 <= nueva_fila < self.total_filas and 0 <= nueva_col < self.total_filas:
                vecino = grid[nueva_fila][nueva_col]
                if not vecino.es_pared():
                    # Para diagonales, verificar que no haya paredes bloqueando el paso
                    if abs(delta_f) == 1 and abs(delta_c) == 1:
                        # Verificar que no haya paredes en los lados adyacentes
                        if not grid[self.fila + delta_f][self.col].es_pared() and \
                           not grid[self.fila][self.col + delta_c].es_pared():
                            self.vecinos.append((vecino, costo))
                    else:
                        self.vecinos.append((vecino, costo))

def h(p1, p2):
    """Heurística Octile: óptima para movimiento en 8 direcciones"""
    x1, y1 = p1
    x2, y2 = p2
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    # Octile distance: combina movimientos diagonales y ortogonales
    # D = 1 (costo ortogonal), D2 = 1.414 (costo diagonal)
    return 1.414 * min(dx, dy) + 1 * abs(dx - dy)

def reconstruir_camino(vino_de, actual, inicio, dibujar_fn):
    camino = []
    pasos_reconstruccion = 0
    nodo_temp = actual
    while nodo_temp in vino_de:
        nodo_temp = vino_de[nodo_temp]
        if nodo_temp != inicio:
            nodo_temp.hacer_camino()
            pasos_reconstruccion += 1
        camino.append(nodo_temp)
        dibujar_fn()
        pygame.time.delay(50)  # Pequeña pausa para visualizar la reconstrucción
    return camino

def algoritmo_a_estrella(dibujar_fn, grid, inicio, fin):
    cuenta = 0
    conjunto_abierto = PriorityQueue()
    conjunto_abierto.put((0, cuenta, inicio))
    vino_de = {}
    g_score = {nodo: float("inf") for fila in grid for nodo in fila}
    g_score[inicio] = 0
    f_score = {nodo: float("inf") for fila in grid for nodo in fila}
    # Peso para la heurística (epsilon): valores > 1 hacen la búsqueda más rápida pero menos exploratoria
    epsilon = 1.2  # Weighted A* para reducir exploración
    f_score[inicio] = epsilon * h(inicio.get_pos(), fin.get_pos())
    
    # Info para mostrar en la interfaz
    info = []
    pasos = 0

    conjunto_abierto_hash = {inicio}
    caminos_alternativos = []

    while not conjunto_abierto.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        actual = conjunto_abierto.get()[2]
        conjunto_abierto_hash.remove(actual)

        if actual == fin:
            info.append(f"Reconstruyendo camino óptimo...")
            camino = reconstruir_camino(vino_de, actual, inicio, lambda: dibujar_fn(info))
            fin.hacer_fin()
            inicio.hacer_inicio()
            
            # Calcular el costo total del camino óptimo
            costo_total = round(g_score[fin], 2)
            
            # Construir lista de nodos del camino con sus valores H
            nodos_camino = [inicio]
            temp = fin
            camino_completo = []
            while temp in vino_de:
                temp = vino_de[temp]
                camino_completo.insert(0, temp)
            camino_completo.append(fin)
            
            # Crear lista de información de nodos
            info = [
                f"¡Camino encontrado!",
                f"Longitud: {len(camino)} nodos",
                f"Costo total: {costo_total}",
                f"Nodos explorados: {pasos}",
                "",
                "Camino óptimo (fila,col | h):"
            ]
            
            # Mostrar TODOS los nodos del camino
            for i, nodo in enumerate(camino_completo):
                h_valor = round(h(nodo.get_pos(), fin.get_pos()), 1)
                info.append(f"{i+1}. ({nodo.fila},{nodo.col}) | h={h_valor}")
            
            dibujar_fn(info)
            return True, [], info, g_score[fin]

        pasos += 1
        for vecino_info in actual.vecinos:
            vecino, costo_movimiento = vecino_info
            temp_g_score = g_score[actual] + costo_movimiento

            if temp_g_score < g_score[vecino]:
                vino_de[vecino] = actual
                g_score[vecino] = temp_g_score
                h_cost = h(vecino.get_pos(), fin.get_pos())
                # Aplicar peso epsilon a la heurística para búsqueda más directa
                epsilon = 1.2
                f_score[vecino] = temp_g_score + epsilon * h_cost
                
                # Guardar los costos en el nodo para visualización
                vecino.g_cost = round(temp_g_score, 1)
                vecino.h_cost = round(h_cost, 1)
                
                if vecino not in conjunto_abierto_hash:
                    # Poda suave: permitir más flexibilidad para rodear obstáculos
                    vx, vy = vecino.get_pos()
                    fx, fy = fin.get_pos()
                    ax, ay = actual.get_pos()
                    
                    # Vector hacia el objetivo desde el nodo actual
                    dir_objetivo_x = fx - ax
                    dir_objetivo_y = fy - ay
                    
                    # Vector hacia el vecino desde el nodo actual  
                    dir_vecino_x = vx - ax
                    dir_vecino_y = vy - ay
                    
                    # Solo agregar si el vecino está en dirección general hacia el objetivo
                    # (producto punto positivo indica ángulo < 90 grados)
                    producto_punto = dir_objetivo_x * dir_vecino_x + dir_objetivo_y * dir_vecino_y
                    
                    # Permitir gran tolerancia para rodear obstáculos complejos
                    # -2 permite hasta ~135 grados de desviación
                    if producto_punto >= -3 or f_score[vecino] < temp_g_score + h_cost * 1.5:
                        cuenta += 1
                        conjunto_abierto.put((f_score[vecino], cuenta, vecino))
                        conjunto_abierto_hash.add(vecino)
                        vecino.hacer_abierto()
                    
                    # Actualizar información solo cada ciertos pasos
                    if pasos % 3 == 0:  # Actualizar cada 3 pasos para mejor rendimiento
                        info = [
                            f"Explorando nodo: ({vecino.fila}, {vecino.col})",
                            f"g(n) = {round(temp_g_score, 1)}",
                            f"h(n) = {round(h_cost, 1)}",
                            f"f(n) = {round(f_score[vecino], 1)}",
                            f"Nodos visitados: {pasos}"
                        ]
                        dibujar_fn(info)

        if actual != inicio:
            actual.hacer_visitado()
            # Solo actualizar visualización cada ciertos pasos
            if pasos % 5 == 0:
                info = [
                    f"Nodo actual: ({actual.fila}, {actual.col})",
                    f"Nodos explorados: {pasos}",
                    "Buscando camino..."
                ]
                dibujar_fn(info)

    info = ["No se encontró un camino posible"]
    dibujar_fn(info)
    return False, [], info, 0

def crear_grid(filas, ancho):
    grid = []
    ancho_nodo = ancho // filas
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo, filas)
            grid[i].append(nodo)
    return grid

def dibujar_grid(ventana, filas, ancho):
    ancho_nodo = ancho // filas
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_nodo), (ancho, i * ancho_nodo), 1)
        for j in range(filas):
            pygame.draw.line(ventana, GRIS, (j * ancho_nodo, 0), (j * ancho_nodo, ancho), 1)

def mostrar_info_lateral(ventana, info, ancho_ventana, alto_ventana, panel_lateral, scroll_offset=0):
    # Área lateral para información
    x_panel = ancho_ventana - panel_lateral
    pygame.draw.rect(ventana, GRIS_CLARO, (x_panel, 0, panel_lateral, alto_ventana))
    pygame.draw.line(ventana, GRIS, (x_panel, 0), (x_panel, alto_ventana), 2)
    
    y = 20
    
    # Título
    titulo = FUENTE_TITULO.render("A* Pathfinding", True, AZUL)
    ventana.blit(titulo, (x_panel + 15, y))
    y += 50
    
    # Controles - Título
    controles_titulo = FUENTE.render("CONTROLES", True, TEXTO)
    ventana.blit(controles_titulo, (x_panel + 15, y))
    y += 30
    
    controles = [
        "Click Izq: Colocar",
        "Click Der: Borrar",
        "ENTER: Iniciar",
        "G: Limpiar todo",
        "R: Reiniciar ventana",
    ]
    
    for linea in controles:
        texto = FUENTE_PEQUEÑA.render(linea, True, TEXTO_CLARO)
        ventana.blit(texto, (x_panel + 15, y))
        y += 22
    
    y += 15
    pygame.draw.line(ventana, GRIS, (x_panel + 15, y), (x_panel + panel_lateral - 15, y), 1)
    y += 20
    
    # Leyenda de colores
    leyenda_titulo = FUENTE.render("LEYENDA", True, TEXTO)
    ventana.blit(leyenda_titulo, (x_panel + 15, y))
    y += 30
    
    leyenda = [
        ("Inicio", NARANJA),
        ("Final", PURPURA),
        ("Pared", NEGRO),
        ("Frontera", AMARILLO),
        ("Visitado", ROJO),
        ("Camino", VERDE),
    ]
    
    for texto, color in leyenda:
        pygame.draw.rect(ventana, color, (x_panel + 15, y, 20, 20), border_radius=3)
        superficie = FUENTE_PEQUEÑA.render(texto, True, TEXTO_CLARO)
        ventana.blit(superficie, (x_panel + 45, y + 2))
        y += 28
    
    # Info del estado
    if info:
        y += 20
        pygame.draw.line(ventana, GRIS, (x_panel + 15, y), (x_panel + panel_lateral - 15, y), 1)
        y += 20
        
        estado_titulo = FUENTE.render("ESTADO", True, TEXTO)
        ventana.blit(estado_titulo, (x_panel + 15, y))
        y += 30
        
        # Calcular altura total del contenido
        y_inicio = y
        linea_altura = 22
        contenido_altura = len(info) * linea_altura
        area_visible = alto_ventana - y_inicio - 20
        
        # Calcular máximo scroll
        max_scroll = max(0, contenido_altura - area_visible)
        
        # Mostrar información con scroll
        for i, linea in enumerate(info):
            y_real = y_inicio + i * linea_altura - scroll_offset
            # Solo dibujar si está visible
            if y_inicio <= y_real < alto_ventana - 10:
                texto = FUENTE_PEQUEÑA.render(str(linea), True, TEXTO_CLARO)
                ventana.blit(texto, (x_panel + 15, y_real))
        
        # Dibujar barra de scroll si es necesario
        if max_scroll > 0:
            scroll_ancho = 8
            scroll_x = ancho_ventana - scroll_ancho - 5
            scroll_altura_total = area_visible
            
            # Fondo de la barra
            pygame.draw.rect(ventana, GRIS, (scroll_x, y_inicio, scroll_ancho, scroll_altura_total))
            
            # Calcular posición y tamaño del thumb
            thumb_altura = max(20, int(scroll_altura_total * (area_visible / contenido_altura)))
            thumb_y = y_inicio + int((scroll_offset / max_scroll) * (scroll_altura_total - thumb_altura))
            
            # Dibujar thumb
            pygame.draw.rect(ventana, AZUL, (scroll_x, thumb_y, scroll_ancho, thumb_altura), border_radius=4)
        
        return max_scroll
    
    return 0

def dibujar(ventana, grid, filas, ancho_ventana, alto_ventana, panel_lateral, info=None, scroll_offset=0):
    ventana.fill(BLANCO)
    
    # Calcular el tamaño del área de juego (excluyendo el panel lateral)
    ancho_juego = ancho_ventana - panel_lateral
    alto_juego = alto_ventana
    ancho_nodo = min(ancho_juego, alto_juego) // filas
    
    # Centrar el grid
    offset_x = (ancho_juego - (ancho_nodo * filas)) // 2
    offset_y = (alto_juego - (ancho_nodo * filas)) // 2
    
    # Actualizar las posiciones de los nodos
    for i, fila in enumerate(grid):
        for j, nodo in enumerate(fila):
            nodo.x = offset_x + (j * ancho_nodo)
            nodo.y = offset_y + (i * ancho_nodo)
            nodo.ancho = ancho_nodo
            nodo.dibujar(ventana)

    # Dibujar el grid
    for i in range(filas + 1):
        pygame.draw.line(ventana, GRIS, 
                        (offset_x + i * ancho_nodo, offset_y),
                        (offset_x + i * ancho_nodo, offset_y + filas * ancho_nodo), 1)
        pygame.draw.line(ventana, GRIS,
                        (offset_x, offset_y + i * ancho_nodo),
                        (offset_x + filas * ancho_nodo, offset_y + i * ancho_nodo), 1)
    
    # Mostrar panel lateral
    max_scroll = mostrar_info_lateral(ventana, info, ancho_ventana, alto_ventana, panel_lateral, scroll_offset)
    
    pygame.display.update()
    return max_scroll

def obtener_click_pos(pos, filas, offset_x, offset_y, ancho_juego):
    x, y = pos
    x = x - offset_x
    y = y - offset_y
    if x <= 0 or y <= 0:
        return None, None
    
    ancho_nodo = ancho_juego // filas
    fila = y // ancho_nodo
    col = x // ancho_nodo
    
    if fila >= filas or col >= filas:
        return None, None
        
    return fila, col

def main(ventana, ancho_ventana):
    FILAS = 11  # Número de filas por defecto
    alto_ventana = ALTO_VENTANA
    panel_lateral = PANEL_LATERAL
    grid = crear_grid(FILAS, ancho_ventana - panel_lateral)

    inicio = None
    fin = None
    corriendo = True
    info_resultado = None  # Guardar la información del resultado
    scroll_offset = 0  # Desplazamiento del scroll
    max_scroll = 0  # Máximo desplazamiento posible

    while corriendo:
        # Calcular dimensiones actuales
        ancho_juego = ancho_ventana - panel_lateral
        ancho_nodo = min(ancho_juego, alto_ventana) // FILAS
        offset_x = (ancho_juego - (ancho_nodo * FILAS)) // 2
        offset_y = (alto_ventana - (ancho_nodo * FILAS)) // 2

        max_scroll = dibujar(ventana, grid, FILAS, ancho_ventana, alto_ventana, panel_lateral, info_resultado, scroll_offset)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if event.type == pygame.VIDEORESIZE:
                ancho_ventana = event.w
                alto_ventana = event.h
                ventana = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)
                panel_lateral = int(ancho_ventana * 0.2)  # Ajustar panel lateral
            
            # Manejar scroll con la rueda del mouse
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * 20  # Ajustar velocidad de scroll
                scroll_offset = max(0, min(scroll_offset, max_scroll))  # Limitar scroll

            if pygame.mouse.get_pressed()[0]:  # Click izquierdo
                pos = pygame.mouse.get_pos()
                resultado = obtener_click_pos(pos, FILAS, offset_x, offset_y, min(ancho_juego, alto_ventana))
                if resultado[0] is not None:
                    fila, col = resultado
                    nodo = grid[fila][col]
                    if not inicio and nodo != fin:
                        inicio = nodo
                        inicio.hacer_inicio()
                    elif not fin and nodo != inicio:
                        fin = nodo
                        fin.hacer_fin()
                    elif nodo != fin and nodo != inicio:
                        nodo.hacer_pared()

            elif pygame.mouse.get_pressed()[2]:  # Click derecho
                pos = pygame.mouse.get_pos()
                resultado = obtener_click_pos(pos, FILAS, offset_x, offset_y, min(ancho_juego, alto_ventana))
                if resultado[0] is not None:
                    fila, col = resultado
                    nodo = grid[fila][col]
                    nodo.restablecer()
                    if nodo == inicio:
                        inicio = None
                    elif nodo == fin:
                        fin = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and inicio and fin:  # Cambiar SPACE por ENTER
                    for fila in grid:
                        for nodo in fila:
                            nodo.actualizar_vecinos(grid)

                    encontrado, caminos_alt, info_final, costo_optimo = algoritmo_a_estrella(
                        lambda info: dibujar(ventana, grid, FILAS, ancho_ventana, alto_ventana, panel_lateral, info),
                        grid, inicio, fin)
                    
                    if encontrado:
                        # Guardar la información del resultado para que persista
                        info_resultado = info_final
                    else:
                        info_resultado = ["No se encontró un camino!"]
                        print("\nNo se encontró un camino!")

                if event.key == pygame.K_g:  # Cambiar C por G
                    inicio = None
                    fin = None
                    info_resultado = None  # Limpiar la información también
                    scroll_offset = 0  # Resetear scroll
                    grid = crear_grid(FILAS, ancho_ventana - panel_lateral)
                
                if event.key == pygame.K_r:
                    # Restablecer dimensiones de la ventana
                    ancho_ventana = ANCHO_VENTANA
                    alto_ventana = ALTO_VENTANA
                    panel_lateral = PANEL_LATERAL
                    ventana = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)
                    grid = crear_grid(FILAS, ancho_ventana - panel_lateral)
                    inicio = None
                    fin = None
                    info_resultado = None  # Limpiar la información también
                    scroll_offset = 0  # Resetear scroll

    pygame.quit()

main(VENTANA, ANCHO_VENTANA)