from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from sokoban_engine import BoardSnapshot, BoardState

from search_methods.heuristics.Hungarian import hungarian
from search_methods.heuristics.Manhattan import nearest_goal_per_box, zero

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
with CONFIG_PATH.open() as f:
    _config = json.load(f)

_HEURISTIC_REGISTRY: dict[str, Callable[[BoardState, frozenset[tuple[int, int]]], int]] = {
    "zero": zero,
    "nearest_goal_per_box": nearest_goal_per_box,
    "manhattan": nearest_goal_per_box,
    "hungarian": hungarian,
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
