"""Pygame front-end: player mode and AI solution replay."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sokoban_engine import Board


def run_player(board: "Board") -> None:
    from sokoban_pygame.player_loop import run_player as _run

    _run(board)


def run_ai_replay(board: "Board", solution: list) -> None:
    from sokoban_pygame.visualizer import replay_solution

    replay_solution(board, solution)
