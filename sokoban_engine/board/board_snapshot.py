"""
BoardSnapshot — immutable full description of a level's static properties.

Created once at game start. Contains everything that never changes:
walls, goals, and board bounds. Provides helpers that work on top of
a lightweight BoardState without needing the full Board object.
"""

from __future__ import annotations

from dataclasses import dataclass

from sokoban_engine.board.board_state import BoardState


@dataclass(frozen=True)
class BoardSnapshot:
    """
    Full static description of a Sokoban level.

    Unlike BoardState (which tracks only what changes), BoardSnapshot captures
    the fixed layout: walls, goal positions, and board bounds. Create it once
    at game start via Board.get_snapshot() and reuse it throughout the game or
    AI search.
    """

    walls: frozenset[tuple[int, int]]
    goals: frozenset[tuple[int, int]]
    min_x: int
    min_y: int
    max_x: int
    max_y: int

    def boxes_on_goals(self, state: BoardState) -> frozenset[tuple[int, int]]:
        """Returns the positions of boxes currently resting on a goal."""
        return state.get_boxes_positions() & self.goals

    def boxes_off_goals(self, state: BoardState) -> frozenset[tuple[int, int]]:
        """Returns the positions of boxes NOT on any goal."""
        return state.get_boxes_positions() - self.goals

    def is_solved(self, state: BoardState) -> bool:
        """Returns True if every box in state is on a goal tile."""
        return state.boxes <= self.goals

    def goals_without_box(self, state: BoardState) -> frozenset[tuple[int, int]]:
        """Returns goal positions that still have no box on them."""
        return self.goals - state.get_boxes_positions()
