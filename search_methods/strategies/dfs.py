from __future__ import annotations

from search_methods.node import TreeNode
from search_methods.strategies.base import SearchStrategy, _StateKey


class DFSStrategy(SearchStrategy):
    """Depth-First Search: LIFO list (stack) frontier, simple visited set."""

    def __init__(self) -> None:
        self._frontier: list[TreeNode] = []
        self._visited: set[_StateKey] = set()

    def push(self, node: TreeNode) -> None:
        self._frontier.append(node)

    def pop(self) -> TreeNode:
        return self._frontier.pop()

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
