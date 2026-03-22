from typing import TYPE_CHECKING

from search_methods.heuristics import Heuristics
from search_methods.settings import Settings
from sokoban_engine import BoardSnapshot

if TYPE_CHECKING:
    from search_methods.node import TreeNode


def get_priority(node: "TreeNode", snapshot: BoardSnapshot) -> int | tuple[int, int]:
    search_method = Settings.get_search_method()
    if search_method == "dfs":
        return -node.level

    if search_method == "bfs":
        return node.level

    if search_method == "a*":
        return (
            node.cost + Heuristics.apply_heuristic(node.state, snapshot),
            node.level,
        )

    if search_method == "greedy":
        return (Heuristics.apply_heuristic(node.state, snapshot), node.level)

    raise ValueError(
        f"[ERROR]: '{search_method}' no es un metodo de busqueda valido. Use: bfs, dfs, greedy o a*"
    )


# Kept for compatibility; not used by TreeNode in current code.
max_tree_depth = Settings.get_max_tree_depth()
