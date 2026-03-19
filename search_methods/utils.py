from pathlib import Path
import json
from typing import List
from search_methods.node import TreeNode

CONFIG_PATH = Path(__file__).with_name("config.json")
with CONFIG_PATH.open() as f:
    config = json.load(f)

search_method = config["search_method"]

def sort_method(node_list: List[TreeNode]) -> List[TreeNode]:

    if search_method == "dfs":
        return sorted(node_list, key=lambda node: node.level, reverse=True)

    elif search_method == "bfs":
        return sorted(node_list, key=lambda node: node.level)

    #TODO
    elif search_method == "a*":
        return None

    elif search_method == "greedy":
        return None

    return None


