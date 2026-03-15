"""
Goal — target tile for boxes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Goal:
    """A target tile a box must occupy to count toward the win condition."""

    position: tuple[int, int]
