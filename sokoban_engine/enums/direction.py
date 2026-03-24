"""
Direction enum — movement deltas for the Sokoban game.
"""

from enum import Enum


class Direction(Enum):
    """Represents the four possible movement directions. Each value is a (dx, dy) delta tuple."""

    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)


    @classmethod
    def can_move_box(cls, dir_1 : 'Direction', dir_2 : 'Direction') -> bool:
        dx_1, dy_1 = dir_1.delta
        dx_2, dy_2 = dir_2.delta

        if dx_1 + dx_2 == 0 and dy_1 + dy_2 == 0:
            return True

        return False

    @property
    def delta(self) -> tuple[int, int]:
        """Returns the (dx, dy) offset for this direction."""
        return self.value
