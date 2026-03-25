"""
Board — central game engine. Owns all game objects and enforces rules.
"""

from __future__ import annotations

import copy

from sokoban_engine.board.board_snapshot import BoardSnapshot
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

    @staticmethod
    def get_box_at(pos: tuple[int, int], state: BoardState) -> Box | None:
        """Return the box at the given position, or None."""
        for box in state.boxes:
            if box.position == pos:
                return box
        return None

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
        self._initial_state: BoardState
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
        self._initial_state = BoardState(Player(player_pos), set(self._boxes))

    # @property
    # def player(self) -> Player:
    #     """The player object (read-only)."""
    #     return self._player
    #
    # @property
    # def boxes(self) -> list[Box]:
    #     """List of box objects (read-only)."""
    #     return self._boxes

    @property
    def initial_state(self) -> BoardState:
        return self._initial_state

    @property
    def walls(self) -> set[tuple[int, int]]:
        """Set of wall positions (read-only)."""
        return self._walls

    @property
    def goals(self) -> set[tuple[int, int]]:
        """Set of goal positions (read-only)."""
        return self._goals

    def get_legal_moves(self, state: BoardState) -> list[Direction]:
        """
        Returns all directions the player can legally move in the current state.
        A move is legal if the target is not a wall, and if pushing a box,
        the cell behind it is free of walls and other boxes.
        """
        legal: list[Direction] = []
        px, py = state.player.position

        for direction in Direction:
            dx, dy = direction.delta
            new_player_pos = (px + dx, py + dy)

            if new_player_pos in self._walls:
                continue

            box = Board.get_box_at(new_player_pos, state)
            if box is not None:
                new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
                if new_box_pos in self._walls:
                    continue
                if Board.get_box_at(new_box_pos, state) is not None:
                    continue

            legal.append(direction)

        return legal

    def legal_directions(self, position: tuple[int,int]) -> list[Direction]:
        """
        returns possible box movements given a current position.
        used to determine whether a box can be moved in a given direction, which is useful
        to check for unsolvable cases.
        """
        legal: list[Direction] = []
        px,py = position
        for direction in Direction:
            dx, dy = direction.delta
            new_pos = (px + dx, py + dy)

            if new_pos in self._walls:
                continue
            legal.append(direction)
        return legal

    def is_in_deadlock(self, state: BoardState) -> bool:
        for box in state.boxes:
            legal_directions = self.legal_directions(box.position)
            if box.on_goal:
                continue
            if len(legal_directions) < 2:
                return True
            if len(legal_directions) == 2 and not Direction.can_move_box(legal_directions[0], legal_directions[1]):
                return True
        return False

    def move(self, direction: Direction, state: BoardState) -> MoveResult:
        """
        Attempts to move the player in the given direction.
        Returns MoveResult.SUCCESS, MoveResult.WIN, or MoveResult.ILLEGAL.
        """
        px, py = state.player.position
        dx, dy = direction.delta
        new_player_pos = (px + dx, py + dy)

        if new_player_pos in self._walls:
            return MoveResult.ILLEGAL

        box = Board.get_box_at(new_player_pos, state)
        if box is not None:
            new_box_pos = (new_player_pos[0] + dx, new_player_pos[1] + dy)
            if new_box_pos in self._walls:
                return MoveResult.ILLEGAL
            if Board.get_box_at(new_box_pos, state) is not None:
                return MoveResult.ILLEGAL
            box.position = new_box_pos
            box.on_goal = new_box_pos in self._goals

        state.player.position = new_player_pos

        return MoveResult.WIN if state.is_solved() else MoveResult.SUCCESS

    def get_snapshot(self) -> BoardSnapshot:
        """
        Returns the static description of the level: walls, goals, and bounds.
        Call once at game start and reuse throughout the game or AI search.
        """
        all_positions = list(self._walls) + list(self._goals)
        xs = [x for x, _ in all_positions]
        ys = [y for _, y in all_positions]
        return BoardSnapshot(
            walls=frozenset(self._walls),
            goals=frozenset(self._goals),
            min_x=min(xs) if xs else 0,
            min_y=min(ys) if ys else 0,
            max_x=max(xs) if xs else 0,
            max_y=max(ys) if ys else 0,
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


