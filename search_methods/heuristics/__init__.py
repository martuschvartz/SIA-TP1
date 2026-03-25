from __future__ import annotations

from typing import Callable

from sokoban_engine import BoardSnapshot, BoardState

from search_methods.heuristics.Hungarian import hungarian
from search_methods.heuristics.Manhattan import nearest_goal_per_box, zero
from search_methods.heuristics.mixed import mixed

_HEURISTIC_REGISTRY: dict[str, Callable[[BoardState, frozenset[tuple[int, int]]], int]] = {
    "zero": zero,
    "nearest_goal_per_box": nearest_goal_per_box,
    "manhattan": nearest_goal_per_box, # manhattan?
    "hungarian": hungarian,
    "mixed": mixed
}


def validate_heuristic_name(name: str) -> None:
    if name in _HEURISTIC_REGISTRY:
        return
    _valid_names = sorted(_HEURISTIC_REGISTRY)
    if len(_valid_names) == 1:
        _use_suffix = _valid_names[0]
    else:
        _use_suffix = ", ".join(_valid_names[:-1]) + " o " + _valid_names[-1]
    raise ValueError(
        f"[ERROR]: '{name}' no es un heuristico valido. Use: {_use_suffix}"
    )


class Heuristics:
    @staticmethod
    def get_heuristic_fn() -> Callable[[BoardState, frozenset[tuple[int, int]]], int]:
        """
        Devuelve la función heurística configurada, resuelta UNA sola vez.
        Así las estrategias (A*, Greedy) la guardan en __init__ y no repiten
        el import + lookup al settings + búsqueda en el registro en cada push().
        """
        from search_methods.settings import Settings
        return _HEURISTIC_REGISTRY[Settings.get_heuristic()]

    @staticmethod
    def apply_heuristic(state: BoardState, snapshot: BoardSnapshot) -> int:
        from search_methods.settings import Settings

        goals = snapshot.goals
        key = Settings.get_heuristic()
        fn = _HEURISTIC_REGISTRY[key]
        return fn(state, goals)
