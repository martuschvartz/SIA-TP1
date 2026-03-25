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
        self._corner_deadlocks = self._compute_corner_deadlocks()

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

    def _compute_corner_deadlocks(self) -> set[tuple[int, int]]:
        """
            Pre-computes corner deadlocks once. A tile is a corner deadlock if it is not a goal,
            and it is blocked on two adjacent sides (e.g., Up AND Left) by walls.
        """
        deadlocks = set()

        # Find the boundaries of the board
        all_positions = list(self._walls) + list(self._goals) + [self._player.position] + [b.position for b in self._boxes]
        max_x = max(x for x, y in all_positions) if all_positions else 0
        max_y = max(y for x, y in all_positions) if all_positions else 0

        for y in range(max_y + 1):
            for x in range(max_x + 1):
                pos = (x, y)
                if pos in self._walls or pos in self._goals:
                    continue

                # Check adjacent walls
                wall_up = (x, y - 1) in self._walls
                wall_down = (x, y + 1) in self._walls
                wall_left = (x - 1, y) in self._walls
                wall_right = (x + 1, y) in self._walls

                # If blocked vertically and horizontally, it's a corner deadlock
                if (wall_up or wall_down) and (wall_left or wall_right):
                    deadlocks.add(pos)

        return deadlocks

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

    def is_box_frozen(self, box_pos: tuple[int, int], state: BoardState, visited: set) -> bool:
        """
        Recursively checks if a specific box is frozen.
        A box is frozen if it is blocked on BOTH the horizontal and vertical axes.
        """
        # Boxes on goal do not cause freeze or deadlock
        if box_pos in self._goals:
            return False

        visited.add(box_pos)
        x, y = box_pos

        # Check horizontal axis
        left_pos = (x - 1, y)
        right_pos = (x + 1, y)

        # Blocked if it's a wall, a corner or another frozen box
        blocked_left = (left_pos in self._walls or
                        left_pos in self._corner_deadlocks or
                        (Board.get_box_at(left_pos, state) and left_pos not in visited and self.is_box_frozen(left_pos, state, visited)))

        blocked_right = (right_pos in self._walls or
                         right_pos in self._corner_deadlocks or
                         (Board.get_box_at(right_pos, state) and right_pos not in visited and self.is_box_frozen(right_pos, state, visited)))

        is_horizontally_blocked = blocked_left or blocked_right

        # Check vertical axis
        up_pos = (x, y - 1)
        down_pos = (x, y + 1)

        blocked_up = (up_pos in self._walls or
                      up_pos in self._corner_deadlocks or
                      (Board.get_box_at(up_pos, state) and up_pos not in visited and self.is_box_frozen(up_pos, state, visited)))

        blocked_down = (down_pos in self._walls or
                        down_pos in self._corner_deadlocks or
                        (Board.get_box_at(down_pos, state) and down_pos not in visited and self.is_box_frozen(down_pos, state, visited)))

        is_vertically_blocked = blocked_up or blocked_down

        # The box is frozen if it is blocked in BOTH axes
        return is_horizontally_blocked and is_vertically_blocked

    def is_in_deadlock(self, state: BoardState, pushed_box_pos: tuple[int, int] = None) -> bool:
        """
        Checks for deadlocks efficiently by only inspecting the box that just moved.
        """
        for box in state.boxes:
            if not box.on_goal and box.position in self._corner_deadlocks:
                return True

        if pushed_box_pos:
            box = Board.get_box_at(pushed_box_pos, state)
            if box and not box.on_goal:
                if self.is_box_frozen(pushed_box_pos, state, set()):
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

        return BoardSnapshot(
            walls=frozenset(self._walls),
            goals=frozenset(self._goals),
            min_x=min(self._walls) if self._walls else 0,
            min_y=min(self._walls) if self._walls else 0,
            max_x=max(self._walls) if self._walls else 0,
            max_y=max(self._walls) if self._walls else 0,
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


