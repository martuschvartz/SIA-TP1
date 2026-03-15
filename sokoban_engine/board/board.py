"""
Board — central game engine. Owns all game objects and enforces rules.
"""

from __future__ import annotations

import copy

from sokoban_engine.board.board_state import BoardState
from sokoban_engine.constants import (
    BOX_CHAR,
    BOX_ON_GOAL_CHAR,
    GOAL_CHAR,
    PLAYER_CHAR,
    PLAYER_ON_GOAL_CHAR,
    WALL_CHAR,
)
from sokoban_engine.entities.box import Box
from sokoban_engine.entities.player import Player
from sokoban_engine.enums.direction import Direction
from sokoban_engine.enums.move_result import MoveResult


class Board:
    """
    The central game engine. Owns all game objects and enforces all rules.
    All game interactions go through this class.
    """

    def __init__(self, level: str) -> None:
        """
        Initialize the board from a level string.

        Args:
            level: Multi-line string encoding the level. See Level Format in the API spec.
        """
        self._walls: set[tuple[int, int]] = set()
        self._goals: set[tuple[int, int]] = set()
        self._player: Player = Player((0, 0))
        self._boxes: list[Box] = []
        self._initial_state: tuple[tuple[int, int], frozenset[tuple[int, int]]] | None = None
        self._parse_level(level)

    def _parse_level(self, level: str) -> None:
        """Parse the level string and populate the board."""
        lines = level.splitlines()
        player_pos: tuple[int, int] | None = None
        box_positions: list[tuple[int, int]] = []

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                pos = (x, y)
                if char == WALL_CHAR:
                    self._walls.add(pos)
                elif char == GOAL_CHAR:
                    self._goals.add(pos)
                elif char == PLAYER_CHAR:
                    player_pos = pos
                elif char == PLAYER_ON_GOAL_CHAR:
                    player_pos = pos
                    self._goals.add(pos)
                elif char == BOX_CHAR:
                    box_positions.append(pos)
                elif char == BOX_ON_GOAL_CHAR:
                    box_positions.append(pos)
                    self._goals.add(pos)

        if player_pos is None:
            raise ValueError("Level must contain a player (@ or +)")

        self._player = Player(player_pos)
        self._boxes = [Box(pos, pos in self._goals) for pos in box_positions]
        self._initial_state = (player_pos, frozenset(box_positions))

    @property
    def player(self) -> Player:
        """The player object (read-only)."""
        return self._player

    @property
    def boxes(self) -> list[Box]:
        """List of box objects (read-only)."""
        return self._boxes

    @property
    def walls(self) -> set[tuple[int, int]]:
        """Set of wall positions (read-only)."""
        return self._walls

    @property
    def goals(self) -> set[tuple[int, int]]:
        """Set of goal positions (read-only)."""
        return self._goals

    def _get_box_at(self, pos: tuple[int, int]) -> Box | None:
        """Return the box at the given position, or None."""
        for box in self._boxes:
            if box.position == pos:
                return box
        return None

    def get_legal_moves(self) -> list[Direction]:
        """
        Returns all directions the player can legally move in the current state.
        A move is legal if the target is not a wall, and if pushing a box,
        the cell behind it is free of walls and other boxes.
        """
        legal: list[Direction] = []
        px, py = self._player.position

        for direction in Direction:
            dx, dy = direction.delta
            new_player_pos = (px + dx, py + dy)

            if new_player_pos in self._walls:
                continue

            box = self._get_box_at(new_player_pos)
            if box is not None:
                new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
                if new_box_pos in self._walls:
                    continue
                if self._get_box_at(new_box_pos) is not None:
                    continue

            legal.append(direction)

        return legal

    def move(self, direction: Direction) -> MoveResult:
        """
        Attempts to move the player in the given direction.
        Returns MoveResult.SUCCESS, MoveResult.WIN, or MoveResult.ILLEGAL.
        """
        px, py = self._player.position
        dx, dy = direction.delta
        new_player_pos = (px + dx, py + dy)

        if new_player_pos in self._walls:
            return MoveResult.ILLEGAL

        box = self._get_box_at(new_player_pos)
        if box is not None:
            new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
            if new_box_pos in self._walls:
                return MoveResult.ILLEGAL
            if self._get_box_at(new_box_pos) is not None:
                return MoveResult.ILLEGAL
            box.position = new_box_pos
            box.on_goal = new_box_pos in self._goals

        self._player.position = new_player_pos

        return MoveResult.WIN if self.is_solved() else MoveResult.SUCCESS

    def get_state(self) -> BoardState:
        """Returns an immutable, hashable snapshot of the current board state."""
        return BoardState(
            player_pos=self._player.position,
            box_positions=frozenset(b.position for b in self._boxes),
        )

    def is_solved(self) -> bool:
        """Returns True if every Box is positioned on a Goal tile."""
        return all(b.on_goal for b in self._boxes)

    def clone(self) -> Board:
        """Returns a deep copy of the board. Mutations do not affect the original."""
        return copy.deepcopy(self)

    def reset(self) -> None:
        """Restores the board to the initial state of the level."""
        if self._initial_state is None:
            return
        player_pos, box_positions = self._initial_state
        self._player.position = player_pos
        for box, pos in zip(self._boxes, box_positions):
            box.position = pos
            box.on_goal = pos in self._goals
