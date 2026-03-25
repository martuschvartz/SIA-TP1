from typing import TYPE_CHECKING

from search_methods.heuristics import Heuristics
from search_methods.settings import Settings
from sokoban_engine import BoardSnapshot

if TYPE_CHECKING:
    from search_methods.node import TreeNode


def get_priority(node: "TreeNode", snapshot: BoardSnapshot) -> tuple[int, int]:
    """Priority tuple for the min-heap (A* and greedy only).

    A*:     (f, h)      — primary: f = g + h; tiebreaker: h (prefer node closer to goal).
    Greedy: (h, level)  — primary: h;          tiebreaker: level (prefer shallower node).
    If the full tuple ties, TreeNode.__lt__ (cost) is the last-resort tiebreaker.
    """
    search_method = Settings.get_search_method()

    if search_method == "a*":
        h = Heuristics.apply_heuristic(node.state, snapshot)
        return (node.cost + h, h)

    if search_method == "greedy":
        return (
            Heuristics.apply_heuristic(node.state, snapshot),
            node.level,
        )

    raise ValueError(
        f"[ERROR]: '{search_method}' no es un metodo de busqueda valido. Use: bfs, dfs, greedy o a*"
    )


# Kept for compatibility; not used by TreeNode in current code.
max_tree_depth = Settings.get_max_tree_depth()
