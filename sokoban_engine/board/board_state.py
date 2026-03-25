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

    def copy(self) -> "BoardState":
        """Shallow structural copy: new Player and Box instances (safe before Board.move)."""
        return BoardState(
            Player(self._player.position),
            {Box(b.position, b.on_goal) for b in self._boxes},
        )

    def is_solved(self) -> bool:
        for box in self._boxes:
            if not box.on_goal:
                return False
        return True

    def get_boxes_positions(self) -> frozenset[tuple[int, int]]:
        return self._boxes_positions



    def key(self) -> tuple[tuple[int, int], frozenset[tuple[int, int]]]:
        """
        used for hashing and equal purposes, since using a hash or equals function over mutable
        objects is unsafe
        """
        return self.player.position, self._boxes_positions

    @property
    def player(self) -> Player:
        return self._player

    @property
    def boxes(self) -> set[Box]:
        return self._boxes

