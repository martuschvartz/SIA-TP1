from __future__ import annotations

from search_methods.strategies.base import SearchStrategy
from search_methods.strategies.bfs import BFSStrategy
from search_methods.strategies.dfs import DFSStrategy
from search_methods.strategies.greedy import GreedyStrategy
from search_methods.strategies.a_star import AStarStrategy
from sokoban_engine import BoardSnapshot


def build_strategy(search_method: str, snapshot: BoardSnapshot) -> SearchStrategy:
    """Factory: return the right SearchStrategy for the configured search method."""
    if search_method == "bfs":
        return BFSStrategy()
    if search_method == "dfs":
        return DFSStrategy()
    if search_method == "greedy":
        return GreedyStrategy(snapshot)
    if search_method == "a*":
        return AStarStrategy(snapshot)
    raise ValueError(
        f"[ERROR]: '{search_method}' no es un metodo de busqueda valido. Use: bfs, dfs, greedy o a*"
    )


__all__ = [
    "SearchStrategy",
    "BFSStrategy",
    "DFSStrategy",
    "GreedyStrategy",
    "AStarStrategy",
    "build_strategy",
]
