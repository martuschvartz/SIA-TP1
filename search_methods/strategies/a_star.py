from __future__ import annotations

import heapq

from search_methods.heuristics import Heuristics
from search_methods.node import TreeNode
from search_methods.strategies.base import SearchStrategy, _StateKey
from sokoban_engine import BoardSnapshot


class AStarStrategy(SearchStrategy):
    """A* Search: min-heap ordered by f = g + h, cost-based dedup with lazy deletion.

    Priority tuple: (f, h, node)
      - Primary:    f = g + h — minimize total estimated cost.
      - Tiebreaker: h         — among equal-f nodes, prefer the one closer to the goal
                                (higher g means a more concrete path, so lower h wins).

    Deduplication: a state may be re-queued only when a strictly cheaper path is found.
    Lazy deletion: stale heap entries (superseded by a cheaper path) are discarded in
    should_expand() when popped, keeping the algorithm correct without a decrease-key op.
    """

    def __init__(self, snapshot: BoardSnapshot) -> None:
        self._frontier: list[tuple[int, int, TreeNode]] = []
        self._known: dict[_StateKey, int] = {}

        # Fix 2: resolvemos la función heurística UNA sola vez al construir la estrategia.
        # Antes se resolvía en cada push() con un import + lookup al settings + búsqueda en
        # el registro, lo cual se ejecutaba millones de veces durante la búsqueda.
        self._h_fn = Heuristics.get_heuristic_fn()
        self._goals = snapshot.goals

        # Fix 1: caché de heurística indexada por posiciones de cajas.
        # La heurística solo depende de DÓNDE están las cajas (no del jugador).
        # Si el jugador se mueve sin empujar ninguna caja, el valor es idéntico
        # pero antes se recalculaba desde cero. Con este dict, es O(1) en cache hit.
        self._h_cache: dict[frozenset[tuple[int, int]], int] = {}

    def push(self, node: TreeNode) -> None:
        boxes = node.state.get_boxes_positions()

        # Consultamos el caché antes de calcular; si ya conocemos h para esta
        # configuración de cajas, evitamos toda la computación de la heurística.
        if boxes not in self._h_cache:
            self._h_cache[boxes] = self._h_fn(node.state, self._goals)
        h = self._h_cache[boxes]

        heapq.heappush(self._frontier, (node.cost + h, h, node))

    def pop(self) -> TreeNode:
        _, __, node = heapq.heappop(self._frontier)
        return node

    def should_visit(self, node: TreeNode) -> bool:
        k = node.state.key()
        if k not in self._known or node.cost < self._known[k]:
            self._known[k] = node.cost
            return True
        return False

    def should_expand(self, node: TreeNode) -> bool:
        # Discard stale entries: the heap may hold an old copy of this state that was
        # superseded when a cheaper path was found and re-queued.
        return node.cost <= self._known.get(node.state.key(), float("inf"))

    def __len__(self) -> int:
        return len(self._frontier)

    def clear(self) -> None:
        self._frontier.clear()
        self._known.clear()
