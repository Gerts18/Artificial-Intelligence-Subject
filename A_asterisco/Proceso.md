# Documentación del Algoritmo A* con Pygame

## Descripción General
Este script implementa una visualización interactiva del algoritmo de búsqueda de caminos **A*** (A-Star) utilizando Pygame. Permite crear obstáculos, definir puntos de inicio y fin, y visualizar en tiempo real cómo el algoritmo encuentra el camino óptimo.

## Características Principales

### 1. Movimiento en 8 Direcciones
- **Movimientos ortogonales** (arriba, abajo, izquierda, derecha): Costo 1.0
- **Movimientos diagonales**: Costo 1.414 (√2)
- Validación de diagonales para evitar atravesar esquinas de obstáculos

### 2. Heurística Octile
```python
def h(p1, p2):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return 1.414 * min(dx, dy) + 1 * abs(dx - dy)
```
Esta heurística es **admisible y consistente** para grids con movimiento en 8 direcciones, garantizando optimalidad.

### 3. Weighted A* (ε = 1.2)
- Se aplica un peso de 1.2 a la heurística: `f(n) = g(n) + 1.2 * h(n)`
- Reduce la exploración excesiva, priorizando velocidad sobre exploración completa
- Aún encuentra caminos muy cercanos al óptimo

### 4. Visualización de Costos
Cuando los nodos son suficientemente grandes (>40px), se muestran:
- **g(n)**: Costo acumulado desde el inicio
- **h(n)**: Estimación heurística al objetivo
- **f(n)**: Costo total (g + h)

## Estructura del Código

### Clase `Nodo`
Representa cada celda del grid con:
- **Posición**: fila, columna, coordenadas x,y en píxeles
- **Color**: Estado visual (inicio, fin, pared, visitado, etc.)
- **Vecinos**: Lista de nodos adyacentes con sus costos de movimiento
- **Métodos**:
  - `dibujar()`: Renderiza el nodo con bordes redondeados y costos
  - `actualizar_vecinos()`: Calcula vecinos válidos considerando diagonales

### Función `algoritmo_a_estrella()`
Implementación completa del algoritmo:

1. **Inicialización**:
   - Cola de prioridad (PriorityQueue) para nodos abiertos
   - Diccionarios para g_score, f_score y vino_de (reconstrucción)
   
2. **Bucle principal**:
   ```
   Mientras conjunto_abierto no esté vacío:
       1. Extraer nodo con menor f(n)
       2. Si es el objetivo → reconstruir camino
       3. Para cada vecino válido:
          - Calcular nuevo g_score
          - Si es mejor que el anterior:
            * Actualizar scores
            * Agregar a conjunto abierto
       4. Marcar nodo como visitado
   ```

3. **Poda direccional**:
   - Utiliza producto punto para favorecer movimientos hacia el objetivo
   - Permite desviaciones de hasta ~135° para rodear obstáculos complejos

4. **Reconstrucción del camino**:
   - Sigue el diccionario `vino_de` desde el fin hasta el inicio
   - Visualiza el camino con animación

### Funciones de Interfaz

#### `dibujar()`
- Renderiza el grid centrado en el área de juego
- Actualiza visualización de todos los nodos
- Muestra panel lateral con información

#### `mostrar_info_lateral()`
Panel informativo con:
- **Controles**: Instrucciones de uso
- **Leyenda**: Significado de colores
- **Estado**: Información del algoritmo en ejecución
- **Scroll**: Para listas largas (camino completo)

#### `main()`
Bucle principal del juego:
- Maneja eventos del mouse y teclado
- Actualiza dimensiones en redimensionamiento
- Coordina la ejecución del algoritmo

## Controles

| Tecla/Acción | Función |
|--------------|---------|
| **Click Izquierdo** | Colocar inicio (1º), fin (2º), paredes (resto) |
| **Click Derecho** | Borrar nodo |
| **ENTER** | Iniciar búsqueda del algoritmo A* |
| **G** | Limpiar toda la cuadrícula |
| **R** | Reiniciar ventana al tamaño original |
| **Rueda del Mouse** | Scroll en panel de información |

## Paleta de Colores

```python
NARANJA = (255, 152, 0)    # Nodo de inicio
PURPURA = (156, 39, 176)   # Nodo final
NEGRO = (45, 45, 55)       # Paredes/obstáculos
AMARILLO = (255, 235, 59)  # Nodos en frontera (abiertos)
ROJO = (244, 67, 54)       # Nodos visitados
VERDE = (76, 175, 80)      # Camino óptimo encontrado
```

## Configuración de Ventana

```python
ANCHO_VENTANA = min(int(ANCHO_PANTALLA * 0.8), 1200)
ALTO_VENTANA = min(int(ALTO_PANTALLA * 0.8), 900)
PANEL_LATERAL = 20% del ancho
FILAS = 11 (grid de 11x11)
```

## Detalles Técnicos

### Validación de Movimientos Diagonales
Para moverse diagonalmente, se verifica que no haya paredes bloqueando en los lados adyacentes:
```python
if abs(delta_f) == 1 and abs(delta_c) == 1:
    if not grid[self.fila + delta_f][self.col].es_pared() and \
       not grid[self.fila][self.col + delta_c].es_pared():
        self.vecinos.append((vecino, costo))
```

### Optimizaciones de Rendimiento
1. **Actualización visual selectiva**: Cada 3-5 pasos en lugar de cada uno
2. **Poda direccional**: Evita explorar nodos muy alejados del objetivo
3. **Weighted A***: Reduce exploración innecesaria
4. **Epsilon = 1.2**: Balance entre velocidad y optimalidad

### Información del Resultado
Al encontrar un camino, se muestra:
- Longitud del camino (número de nodos)
- Costo total acumulado
- Número de nodos explorados
- Lista completa de nodos del camino con coordenadas y valores h(n)

## Ejemplo de Flujo de Ejecución

1. Usuario hace click izquierdo → Coloca nodo de **inicio** (naranja)
2. Segundo click izquierdo → Coloca nodo **final** (púrpura)
3. Clicks adicionales → Crea **paredes** (negro)
4. Presiona **ENTER** → Inicia algoritmo A*
5. Algoritmo explora:
   - Nodos en **frontera** se marcan en amarillo
   - Nodos **visitados** se marcan en rojo
   - Muestra costos g, h, f en cada nodo
6. Al encontrar camino:
   - **Reconstruye** el camino óptimo
   - Marca el camino en **verde**
   - Muestra estadísticas completas en panel lateral

## Ventajas de esta Implementación

✅ **Visualización en tiempo real** de la exploración del algoritmo  
✅ **Movimiento en 8 direcciones** más realista  
✅ **Heurística óptima** (Octile distance)  
✅ **Interfaz intuitiva** con leyendas y controles claros  
✅ **Información detallada** de costos en cada nodo  
✅ **Responsive** - Se adapta al tamaño de ventana  
✅ **Scroll** para caminos largos  
✅ **Validación de diagonales** - No atraviesa esquinas
