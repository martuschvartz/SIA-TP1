"""
MoveResult enum — outcome of Board.move().
"""

from enum import Enum


class MoveResult(Enum):
    """Returned by Board.move() to describe the outcome of an attempted move."""

    SUCCESS = "success"  # Move was legal and applied; game continues.
    WIN = "win"  # Move was legal, applied, and all boxes are on goals.
    ILLEGAL = "illegal"  # Move was blocked; board state is unchanged.
