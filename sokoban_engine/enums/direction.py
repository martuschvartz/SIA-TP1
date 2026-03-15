"""
Direction enum — movement deltas for the Sokoban game.
"""

from enum import Enum


class Direction(Enum):
    """Represents the four possible movement directions. Each value is a (dx, dy) delta tuple."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self) -> tuple[int, int]:
        """Returns the (dx, dy) offset for this direction."""
        return self.value
