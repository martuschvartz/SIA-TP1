from pathlib import Path
import json
from typing import List, TYPE_CHECKING

from search_methods.heuristics import Heuristics
from sokoban_engine import BoardSnapshot

if TYPE_CHECKING:
    from search_methods.node import TreeNode


CONFIG_PATH = Path(__file__).with_name("config.json")
with CONFIG_PATH.open() as f:
    config = json.load(f)

search_method = config["search_method"]
max_tree_depth = config["max_tree_depth"]


def sort_method(node_list: List["TreeNode"], snapshot: BoardSnapshot) -> List["TreeNode"]:
    #Programación defensiva B)
    if not node_list:
        return node_list

    if search_method == "dfs":
        return sorted(node_list, key=lambda node: node.level, reverse=True)

    elif search_method == "bfs":
        return sorted(node_list, key=lambda node: node.level)

    elif search_method == "a*":
        return sorted(
            node_list,
            key=lambda n: (n.cost + Heuristics.apply_heuristic(n.state, snapshot), n.level),
        )

    elif search_method == "greedy":
        return sorted(
            node_list,
            key=lambda n: (Heuristics.apply_heuristic(n.state, snapshot), n.level),
        )

    raise ValueError(
        f"[ERROR]: '{search_method}' no es un metodo de busqueda valido. Use: bfs, dfs, greedy o a*"
    )
