from __future__ import annotations

from time import perf_counter
from typing import List

from search_methods.node import TreeNode
from search_methods.settings import Settings
from search_methods.strategies import SearchStrategy, build_strategy
from sokoban_engine import Board, BoardState, Direction


def get_solution_path(goal_node: TreeNode) -> List[Direction]:
    path: List[Direction] = []
    node = goal_node
    while node.parent_node is not None:
        path.append(node.action_direction)
        node = node.parent_node
    return path


class Tree:
    """Orchestrates the search loop.

    All algorithm-specific logic (frontier structure, dedup, priority, lazy deletion)
    lives in the SearchStrategy subclasses. This class only drives the generic loop.
    """

    def __init__(self, board: Board, init_state: BoardState) -> None:
        self._snapshot = board.get_snapshot()
        self.root = TreeNode(init_state, board, 0, init_state.is_solved(), 0, None, None)

        self.solution_path: List[Direction] = []
        self.solution_cost: int | None = None
        self.result_success: bool = False
        self.timed_out: bool = False

        self.expanded_nodes_count: int = 0
        self.frontier_nodes_count: int = 0
        self.frontier_nodes_remaining: int = 0
        self.max_frontier_nodes_count: int = 0

        # Held during search so main.py can call _frontier.clear() on MemoryError.
        self._frontier: SearchStrategy | None = None

    def start_searching(self) -> List[Direction] | None:
        self.solution_path = []
        self.solution_cost = None
        self.result_success = False
        self.timed_out = False
        self.expanded_nodes_count = 0
        self.frontier_nodes_count = 0
        self.frontier_nodes_remaining = 0
        self.max_frontier_nodes_count = 0

        strategy = build_strategy(Settings.get_search_method(), self._snapshot)
        self._frontier = strategy

        # Seed the frontier with the root node.
        strategy.should_visit(self.root)
        strategy.push(self.root)
        self.frontier_nodes_count = 1
        self.max_frontier_nodes_count = 1

        max_depth = Settings.get_max_tree_depth()
        timeout_seconds = Settings.get_search_timeout_seconds()
        start_time = perf_counter()

        try:
            while strategy:
                if perf_counter() - start_time >= timeout_seconds:
                    self.timed_out = True
                    self.frontier_nodes_remaining = len(strategy)
                    return None

                node = strategy.pop()

                if not strategy.should_expand(node):
                    continue

                if node.get_is_goal():
                    self.solution_path = list(reversed(get_solution_path(node)))
                    self.solution_cost = node.cost
                    self.result_success = True
                    self.frontier_nodes_remaining = len(strategy)
                    return self.solution_path

                if node.level >= max_depth:
                    continue

                self.expanded_nodes_count += 1
                for child in node.expand():
                    if strategy.should_visit(child):
                        strategy.push(child)
                        self.frontier_nodes_count += 1

                self.max_frontier_nodes_count = max(
                    self.max_frontier_nodes_count,
                    len(strategy),
                )

            self.frontier_nodes_remaining = len(strategy)
            return None
        finally:
            self._frontier = None
