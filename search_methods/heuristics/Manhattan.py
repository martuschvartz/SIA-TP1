from __future__ import annotations

from sokoban_engine import BoardState


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def zero(_state: BoardState, _goals: frozenset[tuple[int, int]]) -> int:
    return 0


def nearest_goal_per_box(state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    if not goals:
        return 0
    total = 0
    for box_pos in state.get_boxes_positions():
        if box_pos in goals:
            continue
        total += min(manhattan(box_pos, g) for g in goals)
    return total
