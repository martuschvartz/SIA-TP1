"""
Player — read-only position holder for the game avatar.
"""

from dataclasses import dataclass


@dataclass
class Player:
    """Represents the player's position on the board. Read-only outside of Board."""

    position: tuple[int, int]

    def __hash__(self):
        return hash(self.position)
