"""
Box — pushable game object.
"""

from dataclasses import dataclass


@dataclass
class Box:
    """Represents a pushable box."""

    position: tuple[int, int]
    on_goal: bool = False


    def __hash__(self):
        return hash(self.position)