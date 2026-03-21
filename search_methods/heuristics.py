from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from sokoban_engine import BoardSnapshot, BoardState

CONFIG_PATH = Path(__file__).with_name("config.json")
with CONFIG_PATH.open() as f:
    _config = json.load(f)


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _zero(_state: BoardState, _goals: frozenset[tuple[int, int]]) -> int:
    return 0


def _nearest_goal_per_box(state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    if not goals:
        return 0
    total = 0
    for box_pos in state.get_boxes_positions():
        if box_pos in goals:
            continue
        total += min(_manhattan(box_pos, g) for g in goals)
    return total


_HEURISTIC_REGISTRY: dict[str, Callable[[BoardState, frozenset[tuple[int, int]]], int]] = {
    "zero": _zero,
    "nearest_goal_per_box": _nearest_goal_per_box,
}

_HEURISTIC_KEY: str = _config.get("heuristic", "nearest_goal_per_box")
if _HEURISTIC_KEY not in _HEURISTIC_REGISTRY:
    _valid_names = sorted(_HEURISTIC_REGISTRY)
    if len(_valid_names) == 1:
        _use_suffix = _valid_names[0]
    else:
        _use_suffix = ", ".join(_valid_names[:-1]) + " o " + _valid_names[-1]
    raise ValueError(
        f"[ERROR]: '{_HEURISTIC_KEY}' no es un heuristico valido. Use: {_use_suffix}"
    )


class Heuristics:
    @staticmethod
    def apply_heuristic(state: BoardState, snapshot: BoardSnapshot) -> int:
        goals = snapshot.goals
        fn = _HEURISTIC_REGISTRY[_HEURISTIC_KEY]
        return fn(state, goals)
