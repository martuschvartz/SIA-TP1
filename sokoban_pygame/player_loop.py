"""Interactive pygame loop: human plays with WASD."""

from __future__ import annotations

from copy import deepcopy

import pygame

from sokoban_engine import Board, Direction, MoveResult

from sokoban_pygame.visualizer import (
    HUD_HEIGHT,
    TILE_SIZE,
    FPS,
    _board_size,
    draw_static_frame,
)


def run_player(board: Board) -> None:
    pygame.init()
    pygame.display.set_caption("Sokoban — Player mode")

    snapshot = board.get_snapshot()
    bw, bh_tiles = _board_size(snapshot)
    board_width_px = bw * TILE_SIZE
    board_height_px = bh_tiles * TILE_SIZE
    screen = pygame.display.set_mode((board_width_px, board_height_px + HUD_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    key_to_direction = {
        pygame.K_w: Direction.UP,
        pygame.K_s: Direction.DOWN,
        pygame.K_a: Direction.LEFT,
        pygame.K_d: Direction.RIGHT,
    }

    state = deepcopy(board.initial_state)
    status_msg = "WASD move | R reset | Esc quit"

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_r:
                        state = deepcopy(board.initial_state)
                        status_msg = "Reset"
                    elif event.key in key_to_direction:
                        if board.is_in_deadlock(state):
                            status_msg = "Deadlock"
                            continue
                        result = board.move(key_to_direction[event.key], state)
                        if result == MoveResult.WIN:
                            status_msg = "You won!"
                        elif result == MoveResult.ILLEGAL:
                            status_msg = "Illegal move"
                        else:
                            boxes_done = len(snapshot.boxes_on_goals(state))
                            total_goals = len(snapshot.goals)
                            status_msg = f"Boxes on goals: {boxes_done}/{total_goals}"

            line2 = ""
            if board.is_in_deadlock(state):
                line2 = "Deadlock — press R to reset"

            draw_static_frame(screen, snapshot, state, font, board_height_px, status_msg, line2)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
