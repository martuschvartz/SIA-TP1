from __future__ import annotations

import heapq

from search_methods.heuristics import Heuristics
from search_methods.node import TreeNode
from search_methods.strategies.base import SearchStrategy, _StateKey
from sokoban_engine import BoardSnapshot


class GreedyStrategy(SearchStrategy):
    """Greedy Best-First Search: min-heap ordered by h, simple visited set.

    Priority tuple: (h, level, node)
      - Primary:    h      — always expand the node that looks closest to the goal.
      - Tiebreaker: level  — among equal-h nodes, prefer shallower ones.
    Uses a visited set (not cost-based dedup): each state enters the frontier once.
    """

    def __init__(self, snapshot: BoardSnapshot) -> None:
        self._frontier: list[tuple[int, int, TreeNode]] = []
        self._visited: set[_StateKey] = set()

        # Fix 2: igual que en A*, resolvemos la función heurística una sola vez.
        self._h_fn = Heuristics.get_heuristic_fn()
        self._goals = snapshot.goals

        # Fix 1: mismo caché por configuración de cajas que en A*.
        self._h_cache: dict[frozenset[tuple[int, int]], int] = {}

    def push(self, node: TreeNode) -> None:
        boxes = node.state.get_boxes_positions()

        # Reutilizamos el valor cacheado si ya calculamos h para estas posiciones de cajas.
        if boxes not in self._h_cache:
            self._h_cache[boxes] = self._h_fn(node.state, self._goals)
        h = self._h_cache[boxes]

        heapq.heappush(self._frontier, (h, node.level, node))

    def pop(self) -> TreeNode:
        _, __, node = heapq.heappop(self._frontier)
        return node

    def should_visit(self, node: TreeNode) -> bool:
        k = node.state.key()
        if k in self._visited:
            return False
        self._visited.add(k)
        return True

    def __len__(self) -> int:
        return len(self._frontier)

    def clear(self) -> None:
        self._frontier.clear()
        self._visited.clear()
