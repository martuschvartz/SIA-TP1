# SIA-TP1

## Cómo ejecutar

Instalá dependencias:

```bash
pip install -r requirements.txt
```

El punto de entrada es **`main.py`** (interfaz **pygame**). No hay más replay por consola.

| Comando (ejemplo) | Descripción |
|-------------------|-------------|
| `python main.py` | Modo **AI** (default): lee `search_methods/config.json`, busca solución, escribe `output.txt` y reproduce la solución en una ventana. |
| `python main.py --mode player` | Modo **jugador**: WASD para mover, **R** reset, **Esc** o **Q** salir. |
| `python main.py --mode ai --search-method bfs` | Sobrescribe solo el método de búsqueda; el resto sigue el JSON. |
| `python main.py --heuristic hungarian --search-method a*` | Heurística y método explícitos (la heurística aplica a `a*` y `greedy`). |
| `python main.py --map resources/maps/default.txt` | Nivel desde archivo `.txt` (cualquier ruta válida). |

### Argumentos de línea de comandos

Los valores por defecto salen de **`search_methods/config.json`**. Si pasás un flag, **solo ese campo** se reemplaza; el resto sigue el archivo.

| Flag | Efecto |
|------|--------|
| `-m` / `--mode` | `player` o `ai` (default: `ai`). |
| `--search-method` | `bfs`, `dfs`, `a*`, `greedy`. |
| `--heuristic` | `zero`, `manhattan`, `nearest_goal_per_box`, `hungarian` (debe ser válido para `a*` / `greedy`; en `bfs`/`dfs` no se usa en la prioridad). |
| `--map` / `--level` | Ruta al archivo de nivel. Si no se pasa, se usa `resources/maps/default.txt`. |
| `--config` | Ruta a un JSON con la misma forma que `config.json` (reemplaza la carga inicial por defecto de ese archivo). |

### Mapas (`resources/maps/`)

- Los niveles son archivos **`.txt`** en texto plano, multilínea, con el mismo formato de caracteres que la tabla de más abajo.
- Para agregar un mapa: creá un `.txt` en `resources/maps/` (o en cualquier carpeta) y pasá `--map ruta/al/archivo.txt`.

### Estructura de carpetas (resumen)

- **`sokoban_engine/`** — Motor del juego (`Board`, `BoardState`, etc.).
- **`search_methods/`** — Búsqueda en árbol, heurísticas y `config.json`; **`settings.py`** concentra la configuración en runtime (sobrescribible por CLI).
- **`sokoban_pygame/`** — Ventana pygame: modo jugador y replay de la IA.
- **`resources/maps/`** — Archivos de nivel.

### Scripts viejos

`main_tree_solver.py` y `main_pygame_solver.py` fueron reemplazados por **`python main.py`** (`--mode ai` o `--mode player`). El módulo suelto `pygame_visualizer.py` pasó a vivir dentro de **`sokoban_pygame/`**.

---

## Estructura del proyecto

- **search_methods**: métodos de búsqueda y configuración.
- **sokoban_engine**: motor del Sokoban (backend).
- **sokoban_pygame**: interfaz visual (pygame).
- **resources/maps**: niveles en `.txt`.

### Estructura modular de `sokoban_engine/`

Cada clase en su propio archivo para máxima modularidad:

```
sokoban_engine/
├── __init__.py      # Re-exporta todas las clases públicas
├── board.py         # Board — motor central del juego
├── board_state.py   # BoardState — snapshot hashable
├── box.py           # Box — caja empujable
├── constants.py     # Caracteres del formato de nivel
├── direction.py     # Direction — enum de direcciones
├── goal.py          # Goal — casilla meta
├── move_result.py   # MoveResult — resultado del movimiento
├── player.py        # Player — posición del jugador
└── wall.py          # Wall — casilla impasable
```

---

## Sokoban Engine — Clases y API

El motor del Sokoban está en `sokoban_engine/`. Todas las interacciones del juego pasan por la clase `Board`, que es la única fuente de verdad y el único punto de entrada legal para los movimientos.

### Enums

#### `Direction`
Representa las cuatro direcciones posibles de movimiento. Cada valor es una tupla `(dx, dy)`:
- `UP` = (0, -1)
- `DOWN` = (0, 1)
- `LEFT` = (-1, 0)
- `RIGHT` = (1, 0)

Tiene la propiedad `delta` que devuelve la tupla de desplazamiento.

#### `MoveResult`
Devuelto por `Board.move()` para describir el resultado del movimiento:
- `SUCCESS`: el movimiento fue legal y se aplicó; el juego continúa.
- `WIN`: el movimiento fue legal, se aplicó, y todas las cajas están en las metas.
- `ILLEGAL`: el movimiento fue bloqueado; el estado del tablero **no cambia**.

> **Nota para IA:** `get_legal_moves()` garantiza que llamar a `move(d)` para cualquier `d` en la lista devuelta **nunca** retornará `ILLEGAL`.

### Data Classes

#### `BoardState`
Snapshot ligero y **hashable** del tablero. Usado por agentes de IA para deduplicación de estados (ej. conjuntos de visitados en BFS/A*).
- `player_pos`: tupla `(x, y)` del jugador.
- `box_positions`: `frozenset` con las posiciones de todas las cajas.

Es inmutable y hashable — seguro como clave de diccionario o miembro de set.

### Clases principales

#### `Board`
El motor central del juego. Posee todos los objetos y aplica las reglas.

**Constructor:** `Board(level: str)` — recibe un string multilínea con el nivel.

**Métodos:**
- `get_legal_moves()` → `list[Direction]`: devuelve todas las direcciones legales.
- `move(direction, state)` → `MoveResult`: intenta mover al jugador en `state`; actualiza el estado.
- `get_state()` → `BoardState`: snapshot inmutable del estado actual.
- `is_solved()` → `bool`: `True` si todas las cajas están en metas.
- `clone()` → `Board`: copia profunda independiente (para búsqueda en árbol).
- `reset()`: restaura el tablero al estado inicial.

#### `Player`
Representa la posición del jugador. **Solo lectura** fuera de `Board`.
- `position`: tupla `(x, y)` actual.

> No modificar ni mover directamente. Todo el movimiento lo maneja `Board.move()`.

#### `Box`
Representa una caja empujable.
- `position`: tupla `(x, y)` actual.
- `on_goal`: `True` si la caja está sobre una meta.

`on_goal` se deriva y actualiza por `Board` después de cada movimiento.

#### `Wall`
Casilla impasable. Inmutable tras la inicialización.
- `position`: tupla `(x, y)` fija.

#### `Goal`
Casilla objetivo que una caja debe ocupar para ganar. Inmutable.
- `position`: tupla `(x, y)` fija.

### Formato de nivel

| Carácter | Significado        |
|----------|--------------------|
| `#`      | Pared              |
| `@`      | Posición del jugador |
| `$`      | Caja               |
| `.`      | Meta               |
| `*`      | Caja en meta       |
| `+`      | Jugador en meta    |
| ` `      | Suelo vacío        |

### Uso básico

```python
from copy import deepcopy

from sokoban_engine import Board, Direction, MoveResult

level = """
#####
#@$.#
#####
"""
board = Board(level)
state = deepcopy(board.initial_state)

for direction in board.get_legal_moves(state):
    trial = deepcopy(state)
    result = board.move(direction, trial)
    if result == MoveResult.WIN:
        print("¡Ganaste!")
```