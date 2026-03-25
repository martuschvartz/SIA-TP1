from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from search_methods.node import TreeNode

# Canonical state key: (player_pos, frozenset_of_box_positions)
_StateKey = tuple[tuple[int, int], frozenset[tuple[int, int]]]


class SearchStrategy(ABC):
    """Encapsulates the frontier and visited/cost tracking for one search algorithm.

    Tree calls only these methods — no algorithm-specific if-else anywhere else.
    """

    @abstractmethod
    def push(self, node: "TreeNode") -> None:
        """Add a node to the frontier."""

    @abstractmethod
    def pop(self) -> "TreeNode":
        """Remove and return the next node to process."""

    @abstractmethod
    def should_visit(self, node: "TreeNode") -> bool:
        """Return True (and record the state) if node should enter the frontier.
        Called both for the root (seeding) and for each generated child."""

    def should_expand(self, node: "TreeNode") -> bool:
        """Return True if a just-popped node should actually be expanded.
        Default is True. A* overrides this for lazy-deletion of stale heap entries."""
        return True

    @abstractmethod
    def __len__(self) -> int:
        """Number of nodes currently in the frontier."""

    def clear(self) -> None:
        """Free all internal memory (frontier + tracking structures).
        Called by the orchestrator on MemoryError."""
