"""
BoardState — hashable snapshot for AI state deduplication.
"""

from dataclasses import dataclass

from sokoban_engine import Box, Player


@dataclass()
class BoardState:
    """
    A lightweight, hashable snapshot of the board.
    Used by AI agents for state deduplication (e.g. visited sets in BFS/A*).
    """

    player: Player
    boxes: set[Box]

    def is_solved(self) -> bool:
        for box in self.boxes:
            if not box.on_goal:
                return False
        return True

