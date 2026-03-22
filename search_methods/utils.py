from pathlib import Path
import json
from typing import TYPE_CHECKING

from search_methods.heuristics import Heuristics
from sokoban_engine import BoardSnapshot

if TYPE_CHECKING:
    from search_methods.node import TreeNode


CONFIG_PATH = Path(__file__).with_name("config.json")
with CONFIG_PATH.open() as f:
    config = json.load(f)

search_method = config["search_method"]
max_tree_depth = config["max_tree_depth"]


def get_priority(node: "TreeNode", snapshot: BoardSnapshot) -> int | tuple[int, int]:
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
