from __future__ import annotations

from sokoban_engine import BoardState


def single_manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def zero(_state: BoardState, _goals: frozenset[tuple[int, int]]) -> int:
    return 0


def manhattan(state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    if not goals:
        return 0
    total = 0
    # Como hay varios goals, para cada caja se calcula la distancia contra todos los goals
    # pero solo se queda uno con la más cercana
    for box_pos in state.get_boxes_positions():
        if box_pos in goals:
            continue
        total += min(single_manhattan(box_pos, g) for g in goals)
    return total
