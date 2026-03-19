"""
BoardState — hashable snapshot for AI state deduplication.
"""

from dataclasses import dataclass
from typing import Set

from sokoban_engine.entities.box import Box
from sokoban_engine.entities.player import Player



@dataclass()
class BoardState:
    """
    A lightweight, hashable snapshot of the board.
    Used by AI agents for state deduplication (e.g. visited sets in BFS/A*).
    """

    _player: Player
    _boxes: set[Box]

    def __init__(self, player: Player, boxes: set[Box]) -> None:
        self._player = player
        self._boxes = boxes
        self._boxes_positions = frozenset(b.position for b in self.boxes)

    def is_solved(self) -> bool:
        for box in self._boxes:
            if not box.on_goal:
                return False
        return True

    def get_boxes_positions(self) -> frozenset[tuple[int, int]]:
        return frozenset(b.position for b in self.boxes)

    @property
    def player(self) -> Player:
        return self._player

    @property
    def boxes(self) -> set[Box]:
        return self._boxes

