"""
BoardState — hashable snapshot for AI state deduplication.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardState:
    """
    A lightweight, hashable snapshot of the board.
    Used by AI agents for state deduplication (e.g. visited sets in BFS/A*).
    """

    player_pos: tuple[int, int]
    box_positions: frozenset[tuple[int, int]]
