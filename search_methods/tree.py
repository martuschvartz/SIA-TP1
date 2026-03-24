import heapq
from collections import deque
from time import perf_counter
from typing import Deque, List

from search_methods.node import TreeNode
from search_methods.settings import Settings
from search_methods.utils import get_priority
from sokoban_engine import Board, BoardState, Direction

# Frontier during search: heap-backed list, DFS stack, or BFS queue
_Frontier = list[tuple[int | tuple[int, int], TreeNode]] | list[TreeNode] | Deque[TreeNode]

_StateKey = tuple[tuple[int, int], frozenset[tuple[int, int]]]


def get_solution_path(goal_node: TreeNode) -> List[Direction]:
    current_node = goal_node
    to_return: List[Direction] = []
    while current_node.parent_node is not None:
        to_return.append(current_node.action_direction)
        current_node = current_node.parent_node
    return to_return


class Tree:
    def __init__(self, board: Board, init_state: BoardState):
        self._snapshot = board.get_snapshot()
        self.root = TreeNode(init_state, board, 0, init_state.is_solved(), 0, None, None)
        self.known_states: dict[_StateKey, int] = {}

        self.solution_path: List[Direction] = []
        self.solution_cost: int | None = None
        self.result_success: bool = False
        self.timed_out: bool = False

        self.expanded_nodes_count: int = 0
        self.frontier_nodes_count: int = 0
        self.frontier_nodes_remaining: int = 0
        self.max_frontier_nodes_count: int = 0

        # Set during start_searching only; used by main.py on MemoryError to clear frontier.
        self._frontier: _Frontier | None = None

    def _make_frontier(self, is_informed: bool, search_method: str, root: TreeNode) -> _Frontier:
        """Build the frontier with root already inside."""
        if is_informed:
            f: list[tuple[int | tuple[int, int], TreeNode]] = []
            heapq.heappush(f, (get_priority(root, self._snapshot), root))
            return f
        if search_method == "dfs":
            return [root]
        return deque([root])

    def _frontier_pop(self, frontier: _Frontier, is_informed: bool, search_method: str) -> TreeNode:
        """Pop the next node according to the search strategy."""
        if is_informed:
            _priority, node = heapq.heappop(frontier)  # type: ignore[arg-type]
            return node
        if search_method == "dfs":
            return frontier.pop()  # type: ignore[union-attr]
        return frontier.popleft()  # type: ignore[union-attr]

    def _frontier_push(self, frontier: _Frontier, child: TreeNode, is_informed: bool) -> None:
        """Push a child onto the frontier."""
        if is_informed:
            heapq.heappush(frontier, (get_priority(child, self._snapshot), child))  # type: ignore[arg-type]
        else:
            frontier.append(child)  # type: ignore[union-attr]

    def _should_visit(self, child: TreeNode, is_informed: bool, visited: set[_StateKey]) -> bool:
        k = child.state.key()
        if not is_informed:
            if k in visited:
                return False
            visited.add(k)
            return True
        if k not in self.known_states or child.cost < self.known_states[k]:
            self.known_states[k] = child.cost
            return True
        return False

    def start_searching(self) -> List[Direction] | None:
        self.solution_path = []
        self.solution_cost = None
        self.result_success = False
        self.timed_out = False
        self.expanded_nodes_count = 0
        self.frontier_nodes_count = 0
        self.frontier_nodes_remaining = 0
        self.max_frontier_nodes_count = 0

        search_method = Settings.get_search_method()
        is_informed = search_method in ("a*", "greedy")

        visited: set[_StateKey] = set()
        self.known_states = {}
        root_key = self.root.state.key()
        if is_informed:
            self.known_states[root_key] = self.root.cost
        else:
            visited.add(root_key)

        max_depth = Settings.get_max_tree_depth()
        timeout_seconds = Settings.get_search_timeout_seconds()
        start_time = perf_counter()

        frontier = self._make_frontier(is_informed, search_method, self.root)
        self._frontier = frontier
        self.frontier_nodes_count = 1
        self.max_frontier_nodes_count = 1

        try:
            while frontier:
                if perf_counter() - start_time >= timeout_seconds:
                    self.timed_out = True
                    self.frontier_nodes_remaining = len(frontier)
                    return None

                node = self._frontier_pop(frontier, is_informed, search_method)

                if is_informed and node.cost > self.known_states.get(node.state.key(), float("inf")):
                    continue

                if node.get_is_goal():
                    self.solution_path = list(reversed(get_solution_path(node)))
                    self.solution_cost = node.cost
                    self.result_success = True
                    self.frontier_nodes_remaining = len(frontier)
                    return self.solution_path

                if node.level >= max_depth:
                    continue

                self.expanded_nodes_count += 1
                for child in node.expand():
                    if self._should_visit(child, is_informed, visited):
                        self._frontier_push(frontier, child, is_informed)
                        self.frontier_nodes_count += 1

                self.max_frontier_nodes_count = max(
                    self.max_frontier_nodes_count,
                    len(frontier),
                )

            self.frontier_nodes_remaining = len(frontier)
            return None
        finally:
            self._frontier = None
