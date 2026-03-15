# SIA-TP1

## Estructura del proyecto

- **search_methods**: donde van los métodos de búsqueda
- **sokoban_back**: motor del Sokoban (backend). El "front" iría aparte para la interfaz visual.

### Estructura modular de `sokoban_back/`

Cada clase en su propio archivo para máxima modularidad:

```
sokoban_back/
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

El motor del Sokoban está en `sokoban_back/`. Todas las interacciones del juego pasan por la clase `Board`, que es la única fuente de verdad y el único punto de entrada legal para los movimientos.

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
- `move(direction)` → `MoveResult`: intenta mover al jugador; actualiza el tablero.
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
from sokoban_back import Board, Direction, MoveResult

level = """
#####
#@$.#
#####
"""
board = Board(level)

for direction in board.get_legal_moves():
    future = board.clone()
    result = future.move(direction)
    if result == MoveResult.WIN:
        print("¡Ganaste!")
```