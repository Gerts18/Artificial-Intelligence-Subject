import pygame
import math
from queue import PriorityQueue
from enum import Enum

# ==================== CONFIGURACIÓN INICIAL ====================

pygame.init()

# Configuración de pantalla adaptable
info_pantalla = pygame.display.Info()
ANCHO_BASE = min(int(info_pantalla.current_w * 0.85), 1400)
ALTO_BASE = min(int(info_pantalla.current_h * 0.85), 1000)
PANEL_INFO = 300  # Panel lateral fijo

VENTANA = pygame.display.set_mode((ANCHO_BASE, ALTO_BASE), pygame.RESIZABLE)
pygame.display.set_caption("A* Pathfinding Visualizer - Versión Optimizada")

# Fuentes
FUENTE_TITULO = pygame.font.Font(None, 28)
FUENTE_NORMAL = pygame.font.Font(None, 22)
FUENTE_PEQUEÑA = pygame.font.Font(None, 18)
FUENTE_NODO = pygame.font.Font(None, 16)

# Paleta de colores moderna
COLORES = {
    'fondo': (250, 250, 252),
    'grid': (200, 200, 210),
    'pared': (45, 45, 55),
    'inicio': (255, 152, 0),
    'fin': (156, 39, 176),
    'camino': (76, 175, 80),
    'visitado': (244, 67, 54),
    'frontera': (255, 235, 59),
    'panel': (240, 240, 245),
    'texto': (33, 33, 33),
    'texto_claro': (100, 100, 110),
    'acento': (33, 150, 243)
}

# Modos de heurística
class MetodoHeuristica(Enum):
    MANHATTAN = "Manhattan"
    EUCLIDIANA = "Euclidiana"

# ==================== CLASE NODO ====================

class Nodo:
    def __init__(self, fila, col, ancho, total_filas):
        self.fila = fila
        self.col = col
        self.x = 0
        self.y = 0
        self.ancho = ancho
        self.total_filas = total_filas
        self.color = COLORES['fondo']
        self.vecinos = []
        
        # Costos para A*
        self.costo_g = float('inf')
        self.costo_h = 0
        self.costo_f = float('inf')
        self.nodo_padre = None

    def obtener_posicion(self):
        return self.fila, self.col

    def es_pared(self):
        return self.color == COLORES['pared']

    def es_inicio(self):
        return self.color == COLORES['inicio']

    def es_fin(self):
        return self.color == COLORES['fin']

    def resetear_nodo(self):
        self.color = COLORES['fondo']
        self.costo_g = float('inf')
        self.costo_h = 0
        self.costo_f = float('inf')
        self.nodo_padre = None

    def establecer_inicio(self):
        self.color = COLORES['inicio']

    def establecer_pared(self):
        self.color = COLORES['pared']

    def establecer_fin(self):
        self.color = COLORES['fin']

    def establecer_camino(self):
        self.color = COLORES['camino']

    def establecer_visitado(self):
        self.color = COLORES['visitado']

    def establecer_frontera(self):
        self.color = COLORES['frontera']

    def renderizar(self, ventana, mostrar_costos=False):
        # Dibujar nodo con bordes redondeados
        pygame.draw.rect(ventana, self.color, 
                        (self.x + 1, self.y + 1, self.ancho - 2, self.ancho - 2), 
                        border_radius=4)
        
        # Mostrar costos si está en frontera o visitado y el modo está activo
        if mostrar_costos and self.ancho > 40 and \
           self.color in [COLORES['frontera'], COLORES['visitado'], COLORES['camino']]:
            if self.costo_g != float('inf') and self.costo_h > 0:
                # Fondo semi-transparente
                s = pygame.Surface((self.ancho - 4, self.ancho - 4))
                s.set_alpha(180)
                s.fill(COLORES['fondo'])
                ventana.blit(s, (self.x + 2, self.y + 2))
                
                # Textos de costos
                g_texto = FUENTE_NODO.render(f"g:{self.costo_g:.1f}", True, COLORES['texto'])
                h_texto = FUENTE_NODO.render(f"h:{self.costo_h:.1f}", True, COLORES['texto'])
                f_texto = FUENTE_NODO.render(f"f:{self.costo_f:.1f}", True, COLORES['acento'])
                
                ventana.blit(g_texto, (self.x + 5, self.y + 5))
                ventana.blit(h_texto, (self.x + 5, self.y + self.ancho // 2 - 4))
                ventana.blit(f_texto, (self.x + 5, self.y + self.ancho - 18))

    def calcular_vecinos(self, grid):
        self.vecinos = []
        movimientos = [
            (-1, 0, 1.0),    # Arriba
            (1, 0, 1.0),     # Abajo
            (0, -1, 1.0),    # Izquierda
            (0, 1, 1.0),     # Derecha
            (-1, -1, math.sqrt(2)),  # Diagonal superior izquierda
            (-1, 1, math.sqrt(2)),   # Diagonal superior derecha
            (1, -1, math.sqrt(2)),   # Diagonal inferior izquierda
            (1, 1, math.sqrt(2))     # Diagonal inferior derecha
        ]
        
        for df, dc, costo in movimientos:
            nf, nc = self.fila + df, self.col + dc
            
            if 0 <= nf < self.total_filas and 0 <= nc < self.total_filas:
                vecino = grid[nf][nc]
                if not vecino.es_pared():
                    # Para diagonales, verificar que no haya paredes bloqueando
                    if abs(df) == 1 and abs(dc) == 1:
                        if not grid[self.fila + df][self.col].es_pared() and \
                           not grid[self.fila][self.col + dc].es_pared():
                            self.vecinos.append((vecino, costo))
                    else:
                        self.vecinos.append((vecino, costo))

    def __lt__(self, other):
        return self.costo_f < other.costo_f

# ==================== FUNCIONES DE HEURÍSTICA ====================

def obtener_distancia_heuristica(p1, p2, metodo=MetodoHeuristica.EUCLIDIANA):
    x1, y1 = p1
    x2, y2 = p2
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    
    if metodo == MetodoHeuristica.MANHATTAN:
        return dx + dy
    elif metodo == MetodoHeuristica.EUCLIDIANA:
        return math.sqrt(dx**2 + dy**2)
    
    return dx + dy  # Default: Manhattan

# ==================== ALGORITMO A* ====================

def buscar_camino_a_estrella(grid, inicio, fin, funcion_dibujar, metodo_heuristica, epsilon=1.0, 
                        mostrar_costos=False, velocidad=1):
    """
    Implementación optimizada de A* con múltiples heurísticas
    epsilon > 1.0 = Weighted A* (más rápido, menos óptimo)
    epsilon = 1.0 = A* clásico (óptimo)
    """
    contador = 0
    cola_abierta = PriorityQueue()
    
    # Inicializar nodo inicio
    inicio.costo_g = 0
    inicio.costo_h = obtener_distancia_heuristica(inicio.obtener_posicion(), fin.obtener_posicion(), metodo_heuristica)
    inicio.costo_f = epsilon * inicio.costo_h
    
    cola_abierta.put((inicio.costo_f, contador, inicio))
    conjunto_abierto = {inicio}
    
    nodos_explorados = 0
    info_actual = []

    while not cola_abierta.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

        nodo_actual = cola_abierta.get()[2]
        conjunto_abierto.remove(nodo_actual)
        nodos_explorados += 1

        # ¿Encontramos el destino?
        if nodo_actual == fin:
            camino = construir_ruta(inicio, fin, funcion_dibujar)
            fin.establecer_fin()
            inicio.establecer_inicio()
            
            info_final = [
                "═══ CAMINO ENCONTRADO ═══",
                f"Longitud: {len(camino)} nodos",
                f"Costo total: {fin.costo_g:.2f}",
                f"Nodos explorados: {nodos_explorados}",
                f"Heurística: {metodo_heuristica.value}",
                f"Epsilon: {epsilon}",
                "",
                "═══ NODOS DEL CAMINO ═══"
            ]
            
            for i, nodo in enumerate(camino):
                info_final.append(
                    f"{i+1}. ({nodo.fila},{nodo.col}) | "
                    f"g={nodo.costo_g:.1f} h={nodo.costo_h:.1f}"
                )
            
            return info_final

        # Explorar vecinos
        for vecino, costo_movimiento in nodo_actual.vecinos:
            temp_g = nodo_actual.costo_g + costo_movimiento
            
            if temp_g < vecino.costo_g:
                vecino.nodo_padre = nodo_actual
                vecino.costo_g = temp_g
                vecino.costo_h = obtener_distancia_heuristica(vecino.obtener_posicion(), fin.obtener_posicion(), metodo_heuristica)
                vecino.costo_f = temp_g + epsilon * vecino.costo_h
                
                if vecino not in conjunto_abierto:
                    contador += 1
                    cola_abierta.put((vecino.costo_f, contador, vecino))
                    conjunto_abierto.add(vecino)
                    vecino.establecer_frontera()
                    
                    # Actualizar info cada N nodos según velocidad
                    if nodos_explorados % velocidad == 0:
                        info_actual = [
                            f"Explorando: ({vecino.fila},{vecino.col})",
                            f"g={temp_g:.1f} h={vecino.costo_h:.1f} f={vecino.costo_f:.1f}",
                            f"Nodos: {nodos_explorados}",
                            f"En frontera: {len(conjunto_abierto)}"
                        ]
                        funcion_dibujar(info_actual, mostrar_costos)

        if nodo_actual != inicio:
            nodo_actual.establecer_visitado()
        
        if nodos_explorados % velocidad == 0:
            funcion_dibujar(info_actual, mostrar_costos)

    return ["✗ No se encontró camino", f"Nodos explorados: {nodos_explorados}"]

def construir_ruta(inicio, fin, funcion_dibujar):
    camino = []
    nodo_actual = fin
    
    while nodo_actual != inicio:
        if nodo_actual.nodo_padre is None:
            break
        nodo_actual = nodo_actual.nodo_padre
        if nodo_actual != inicio:
            nodo_actual.establecer_camino()
            camino.insert(0, nodo_actual)
        pygame.time.delay(30)
        funcion_dibujar([], False)
    
    return [inicio] + camino + [fin]

# ==================== FUNCIONES DE INTERFAZ ====================

def inicializar_grilla(filas, ancho_disponible):
    grid = []
    ancho_nodo = ancho_disponible // filas
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo, filas)
            grid[i].append(nodo)
    return grid

def renderizar_lineas_grilla(ventana, grid, filas, offset_x, offset_y, ancho_nodo):
    # Dibujar líneas del grid
    for i in range(filas + 1):
        pygame.draw.line(ventana, COLORES['grid'],
                        (offset_x, offset_y + i * ancho_nodo),
                        (offset_x + filas * ancho_nodo, offset_y + i * ancho_nodo), 1)
        pygame.draw.line(ventana, COLORES['grid'],
                        (offset_x + i * ancho_nodo, offset_y),
                        (offset_x + i * ancho_nodo, offset_y + filas * ancho_nodo), 1)

def mostrar_panel_lateral(ventana, ancho_ventana, alto_ventana, info_estado, scroll, 
                       metodo_heuristica, epsilon, velocidad):
    x_panel = ancho_ventana - PANEL_INFO
    pygame.draw.rect(ventana, COLORES['panel'], (x_panel, 0, PANEL_INFO, alto_ventana))
    pygame.draw.line(ventana, COLORES['grid'], (x_panel, 0), (x_panel, alto_ventana), 2)
    
    y = 20
    
    # Título
    titulo = FUENTE_TITULO.render("A* Pathfinding", True, COLORES['acento'])
    ventana.blit(titulo, (x_panel + 15, y))
    y += 50
    
    # Controles
    controles = [
        ("CONTROLES", FUENTE_NORMAL, COLORES['texto']),
        ("Click Izq: Colocar", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("Click Der: Borrar", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("ESPACIO: Iniciar A*", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("C: Limpiar grid", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("V: Mostrar costos", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("H: Cambiar heurística", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("↑/↓: Velocidad", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        ("+/-: Epsilon", FUENTE_PEQUEÑA, COLORES['texto_claro']),
    ]
    
    for texto, fuente, color in controles:
        superficie = fuente.render(texto, True, color)
        ventana.blit(superficie, (x_panel + 15, y))
        y += 25 if fuente == FUENTE_NORMAL else 20
    
    y += 10
    
    # Configuración actual
    pygame.draw.line(ventana, COLORES['grid'], (x_panel + 15, y), (x_panel + PANEL_INFO - 15, y), 1)
    y += 15
    
    config = [
        ("CONFIGURACIÓN", FUENTE_NORMAL, COLORES['texto']),
        (f"Heurística: {metodo_heuristica.value}", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        (f"Epsilon: {epsilon:.1f}", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        (f"Velocidad: {velocidad}x", FUENTE_PEQUEÑA, COLORES['texto_claro']),
        (f"Diagonales: Activas", FUENTE_PEQUEÑA, COLORES['texto_claro']),
    ]
    
    for texto, fuente, color in config:
        superficie = fuente.render(texto, True, color)
        ventana.blit(superficie, (x_panel + 15, y))
        y += 25 if fuente == FUENTE_NORMAL else 20
    
    y += 10
    
    # Leyenda de colores
    pygame.draw.line(ventana, COLORES['grid'], (x_panel + 15, y), (x_panel + PANEL_INFO - 15, y), 1)
    y += 15
    
    leyenda_texto = FUENTE_NORMAL.render("LEYENDA", True, COLORES['texto'])
    ventana.blit(leyenda_texto, (x_panel + 15, y))
    y += 30
    
    leyenda = [
        ("Inicio", COLORES['inicio']),
        ("Final", COLORES['fin']),
        ("Pared", COLORES['pared']),
        ("Frontera", COLORES['frontera']),
        ("Visitado", COLORES['visitado']),
        ("Camino", COLORES['camino']),
    ]
    
    for texto, color in leyenda:
        pygame.draw.rect(ventana, color, (x_panel + 15, y, 20, 20), border_radius=3)
        superficie = FUENTE_PEQUEÑA.render(texto, True, COLORES['texto_claro'])
        ventana.blit(superficie, (x_panel + 45, y + 2))
        y += 28
    
    # Info del estado actual
    if info_estado:
        y += 20
        pygame.draw.line(ventana, COLORES['grid'], (x_panel + 15, y), (x_panel + PANEL_INFO - 15, y), 1)
        y += 15
        
        estado_texto = FUENTE_NORMAL.render("ESTADO", True, COLORES['texto'])
        ventana.blit(estado_texto, (x_panel + 15, y))
        y += 30
        
        # Área scrolleable para info
        y_inicio = y
        area_scroll = alto_ventana - y_inicio - 20
        
        for i, linea in enumerate(info_estado):
            y_linea = y_inicio + (i * 22) - scroll
            if y_inicio <= y_linea < alto_ventana - 20:
                texto_linea = FUENTE_PEQUEÑA.render(str(linea), True, COLORES['texto_claro'])
                ventana.blit(texto_linea, (x_panel + 15, y_linea))
        
        # Barra de scroll si es necesaria
        contenido_altura = len(info_estado) * 22
        if contenido_altura > area_scroll:
            scroll_max = contenido_altura - area_scroll
            thumb_altura = max(30, int((area_scroll / contenido_altura) * area_scroll))
            thumb_y = y_inicio + int((scroll / scroll_max) * (area_scroll - thumb_altura))
            
            pygame.draw.rect(ventana, COLORES['grid'], 
                           (x_panel + PANEL_INFO - 25, y_inicio, 8, area_scroll))
            pygame.draw.rect(ventana, COLORES['acento'], 
                           (x_panel + PANEL_INFO - 25, thumb_y, 8, thumb_altura), 
                           border_radius=4)
            
            return scroll_max
    
    return 0

def actualizar_ventana(ventana, grid, filas, ancho_ventana, alto_ventana, info_estado, scroll, 
           metodo_heuristica, epsilon, velocidad, mostrar_costos):
    ventana.fill(COLORES['fondo'])
    
    # Calcular área de juego
    ancho_juego = ancho_ventana - PANEL_INFO
    ancho_nodo = min(ancho_juego, alto_ventana) // filas
    
    offset_x = (ancho_juego - (ancho_nodo * filas)) // 2
    offset_y = (alto_ventana - (ancho_nodo * filas)) // 2
    
    # Actualizar y dibujar nodos
    for i, fila in enumerate(grid):
        for j, nodo in enumerate(fila):
            nodo.x = offset_x + j * ancho_nodo
            nodo.y = offset_y + i * ancho_nodo
            nodo.ancho = ancho_nodo
            nodo.renderizar(ventana, mostrar_costos)
    
    # Dibujar grid
    renderizar_lineas_grilla(ventana, grid, filas, offset_x, offset_y, ancho_nodo)
    
    # Dibujar panel
    scroll_max = mostrar_panel_lateral(ventana, ancho_ventana, alto_ventana, info_estado, 
                                     scroll, metodo_heuristica, epsilon, velocidad)
    
    pygame.display.update()
    return offset_x, offset_y, ancho_nodo, scroll_max

def convertir_click_a_posicion(pos, filas, offset_x, offset_y, ancho_nodo):
    x, y = pos
    x -= offset_x
    y -= offset_y
    
    if x < 0 or y < 0:
        return None, None
    
    col = x // ancho_nodo
    fila = y // ancho_nodo
    
    if fila >= filas or col >= filas:
        return None, None
    
    return fila, col

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    FILAS = 15
    grid = inicializar_grilla(FILAS, ANCHO_BASE - PANEL_INFO)
    
    inicio = None
    fin = None
    info_estado = None
    scroll = 0
    
    # Configuración
    metodo_heuristica = MetodoHeuristica.EUCLIDIANA
    epsilon = 1.0
    velocidad = 5
    mostrar_costos = False
    
    ancho_ventana = ANCHO_BASE
    alto_ventana = ALTO_BASE
    
    corriendo = True
    clock = pygame.time.Clock()

    while corriendo:
        clock.tick(60)  # 60 FPS
        
        offset_x, offset_y, ancho_nodo, scroll_max = actualizar_ventana(
            VENTANA, grid, FILAS, ancho_ventana, alto_ventana, 
            info_estado, scroll, metodo_heuristica, epsilon, velocidad, 
            mostrar_costos
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
            
            if event.type == pygame.VIDEORESIZE:
                ancho_ventana = event.w
                alto_ventana = event.h
            
            if event.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(scroll - event.y * 20, scroll_max))
            
            # Click izquierdo
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] < ancho_ventana - PANEL_INFO:  # No clickear en panel
                    fila, col = convertir_click_a_posicion(pos, FILAS, offset_x, offset_y, ancho_nodo)
                    if fila is not None:
                        nodo = grid[fila][col]
                        if not inicio and nodo != fin:
                            inicio = nodo
                            inicio.establecer_inicio()
                        elif not fin and nodo != inicio:
                            fin = nodo
                            fin.establecer_fin()
                        elif nodo != inicio and nodo != fin:
                            nodo.establecer_pared()
            
            # Click derecho
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] < ancho_ventana - PANEL_INFO:
                    fila, col = convertir_click_a_posicion(pos, FILAS, offset_x, offset_y, ancho_nodo)
                    if fila is not None:
                        nodo = grid[fila][col]
                        nodo.resetear_nodo()
                        if nodo == inicio:
                            inicio = None
                        elif nodo == fin:
                            fin = None
            
            # Teclas
            if event.type == pygame.KEYDOWN:
                # Iniciar A*
                if event.key == pygame.K_SPACE and inicio and fin:
                    for fila in grid:
                        for nodo in fila:
                            if not nodo.es_inicio() and not nodo.es_fin() and not nodo.es_pared():
                                nodo.resetear_nodo()
                            nodo.calcular_vecinos(grid)
                    
                    def wrapper_dibujar(info, costos):
                        nonlocal info_estado
                        info_estado = info
                        actualizar_ventana(VENTANA, grid, FILAS, ancho_ventana, alto_ventana, 
                               info_estado, scroll, metodo_heuristica, epsilon, velocidad, 
                               costos)
                    
                    resultado = buscar_camino_a_estrella(grid, inicio, fin, wrapper_dibujar, 
                                                    metodo_heuristica, epsilon, mostrar_costos, 
                                                    velocidad)
                    if resultado:
                        info_estado = resultado
                
                # Limpiar
                elif event.key == pygame.K_c:
                    grid = inicializar_grilla(FILAS, ancho_ventana - PANEL_INFO)
                    inicio = None
                    fin = None
                    info_estado = None
                    scroll = 0
                
                # Cambiar heurística
                elif event.key == pygame.K_h:
                    heuristicas = list(MetodoHeuristica)
                    idx_actual = heuristicas.index(metodo_heuristica)
                    metodo_heuristica = heuristicas[(idx_actual + 1) % len(heuristicas)]
                
                # Velocidad
                elif event.key == pygame.K_UP:
                    velocidad = min(velocidad + 1, 20)
                elif event.key == pygame.K_DOWN:
                    velocidad = max(velocidad - 1, 1)
                
                # Epsilon
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    epsilon = min(epsilon + 0.1, 3.0)
                elif event.key == pygame.K_MINUS:
                    epsilon = max(epsilon - 0.1, 1.0)
                
                # Mostrar costos
                elif event.key == pygame.K_v:
                    mostrar_costos = not mostrar_costos

    pygame.quit()

if __name__ == '__main__':
    main()
