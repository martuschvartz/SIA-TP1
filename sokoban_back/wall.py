"""
Wall — impassable tile.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Wall:
    """An impassable tile. Immutable after board initialization."""

    position: tuple[int, int]
