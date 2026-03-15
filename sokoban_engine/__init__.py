"""
Sokoban Engine — Game logic and board management.

Modular structure: enums/, entities/, board/, constants/
"""

from sokoban_engine.board.board import Board
from sokoban_engine.board.board_state import BoardState
from sokoban_engine.entities.box import Box
from sokoban_engine.entities.goal import Goal
from sokoban_engine.entities.player import Player
from sokoban_engine.entities.wall import Wall
from sokoban_engine.enums.direction import Direction
from sokoban_engine.enums.move_result import MoveResult

__all__ = [
    "Board",
    "BoardState",
    "Box",
    "Direction",
    "Goal",
    "MoveResult",
    "Player",
    "Wall",
]
