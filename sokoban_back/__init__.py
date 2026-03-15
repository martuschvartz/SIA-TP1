"""
Sokoban Engine — Game logic and board management.

Modular structure: each class lives in its own file.
"""

from sokoban_back.board import Board
from sokoban_back.board_state import BoardState
from sokoban_back.box import Box
from sokoban_back.direction import Direction
from sokoban_back.goal import Goal
from sokoban_back.move_result import MoveResult
from sokoban_back.player import Player
from sokoban_back.wall import Wall

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
