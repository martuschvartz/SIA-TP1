"""
Box — pushable game object.
"""

from dataclasses import dataclass


@dataclass
class Box:
    """Represents a pushable box."""

    position: tuple[int, int]
    on_goal: bool = False
