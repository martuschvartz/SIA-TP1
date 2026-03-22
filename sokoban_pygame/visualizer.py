from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable

import pygame

from sokoban_engine import Board, BoardSnapshot, BoardState, MoveResult

TILE_SIZE = 56
HUD_HEIGHT = 72
FPS = 60
MOVE_DURATION_MS = 180

BACKGROUND_COLOR = (20, 20, 24)
FLOOR_COLOR = (46, 46, 56)
GRID_COLOR = (58, 58, 70)
WALL_COLOR = (87, 103, 155)
GOAL_COLOR = (232, 196, 77)
BOX_COLOR = (183, 122, 58)
BOX_ON_GOAL_COLOR = (102, 186, 98)
PLAYER_COLOR = (86, 193, 255)
TEXT_COLOR = (238, 238, 238)


@dataclass(frozen=True)
class AnimationFrame:
    player_from: tuple[int, int]
    player_to: tuple[int, int]
    box_from: tuple[int, int] | None
    box_to: tuple[int, int] | None


def _board_size(snapshot: BoardSnapshot) -> tuple[int, int]:
    width = snapshot.max_x - snapshot.min_x + 1
    height = snapshot.max_y - snapshot.min_y + 1
    return width, height


def _tile_rect(snapshot: BoardSnapshot, pos: tuple[int, int]) -> pygame.Rect:
    x, y = pos
    screen_x = (x - snapshot.min_x) * TILE_SIZE
    screen_y = (y - snapshot.min_y) * TILE_SIZE
    return pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)


def _lerp(start: float, end: float, progress: float) -> float:
    return start + (end - start) * progress


def _lerp_pos(
    snapshot: BoardSnapshot,
    start: tuple[int, int],
    end: tuple[int, int],
    progress: float,
) -> tuple[float, float]:
    start_rect = _tile_rect(snapshot, start)
    end_rect = _tile_rect(snapshot, end)
    return (
        _lerp(start_rect.centerx, end_rect.centerx, progress),
        _lerp(start_rect.centery, end_rect.centery, progress),
    )


def _build_animation(previous_state: BoardState, current_state: BoardState) -> AnimationFrame:
    previous_boxes = previous_state.get_boxes_positions()
    current_boxes = current_state.get_boxes_positions()
    moved_from = previous_boxes - current_boxes
    moved_to = current_boxes - previous_boxes
    return AnimationFrame(
        player_from=previous_state.player.position,
        player_to=current_state.player.position,
        box_from=next(iter(moved_from), None),
        box_to=next(iter(moved_to), None),
    )


def _draw_board(screen: pygame.Surface, snapshot: BoardSnapshot) -> None:
    width, height = _board_size(snapshot)
    for row in range(height):
        for col in range(width):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, FLOOR_COLOR, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    for wall in snapshot.walls:
        rect = _tile_rect(snapshot, wall)
        pygame.draw.rect(screen, WALL_COLOR, rect, border_radius=6)
        inset = rect.inflate(-12, -12)
        pygame.draw.rect(screen, (120, 137, 194), inset, border_radius=4)

    for goal in snapshot.goals:
        rect = _tile_rect(snapshot, goal)
        center = rect.center
        pygame.draw.circle(screen, GOAL_COLOR, center, TILE_SIZE // 6)
        pygame.draw.circle(screen, (248, 224, 138), center, TILE_SIZE // 10)


def _draw_box(
    screen: pygame.Surface,
    center: tuple[float, float],
    on_goal: bool,
) -> None:
    size = TILE_SIZE * 0.62
    rect = pygame.Rect(0, 0, size, size)
    rect.center = (round(center[0]), round(center[1]))
    color = BOX_ON_GOAL_COLOR if on_goal else BOX_COLOR
    highlight = (176, 225, 161) if on_goal else (219, 164, 98)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, highlight, rect.inflate(-16, -16), border_radius=4)


def _draw_player(screen: pygame.Surface, center: tuple[float, float]) -> None:
    pygame.draw.circle(
        screen,
        PLAYER_COLOR,
        (round(center[0]), round(center[1])),
        TILE_SIZE // 3,
    )
    pygame.draw.circle(
        screen,
        (212, 242, 255),
        (round(center[0]), round(center[1] - TILE_SIZE * 0.08)),
        TILE_SIZE // 8,
    )


def _draw_entities(
    screen: pygame.Surface,
    snapshot: BoardSnapshot,
    state: BoardState,
    animation: AnimationFrame | None,
    progress: float,
) -> None:
    animated_box_from = animation.box_from if animation else None
    animated_box_to = animation.box_to if animation else None

    for box_pos in state.get_boxes_positions():
        if box_pos == animated_box_to and animated_box_from is not None:
            continue

        center = _tile_rect(snapshot, box_pos).center
        _draw_box(screen, center, box_pos in snapshot.goals)

    if animation and animated_box_from is not None and animated_box_to is not None:
        center = _lerp_pos(snapshot, animated_box_from, animated_box_to, progress)
        _draw_box(screen, center, animated_box_to in snapshot.goals)

    if animation:
        player_center = _lerp_pos(snapshot, animation.player_from, animation.player_to, progress)
    else:
        player_center = _tile_rect(snapshot, state.player.position).center

    _draw_player(screen, player_center)


def _draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    solved_font: pygame.font.Font,
    board_height_px: int,
    current_step: int,
    total_steps: int,
    is_paused: bool,
    is_solved: bool,
) -> None:
    hud_rect = pygame.Rect(0, board_height_px, screen.get_width(), HUD_HEIGHT)
    pygame.draw.rect(screen, (28, 28, 36), hud_rect)

    status_text = f"Step {current_step}/{total_steps}    Space: pause/resume    Esc: close"
    status_surface = font.render(status_text, True, TEXT_COLOR)
    screen.blit(status_surface, (16, board_height_px + 14))

    if is_solved:
        solved_surface = solved_font.render("Solved!", True, (126, 231, 135))
        screen.blit(solved_surface, (16, board_height_px + 38))
    elif is_paused:
        paused_surface = solved_font.render("Paused", True, GOAL_COLOR)
        screen.blit(paused_surface, (16, board_height_px + 38))


def draw_static_frame(
    screen: pygame.Surface,
    snapshot: BoardSnapshot,
    state: BoardState,
    font: pygame.font.Font,
    board_height_px: int,
    hud_line_1: str,
    hud_line_2: str = "",
) -> None:
    """Draw one frame for interactive player mode (no move animation)."""
    screen.fill(BACKGROUND_COLOR)
    _draw_board(screen, snapshot)
    _draw_entities(screen, snapshot, state, None, 1.0)
    hud_rect = pygame.Rect(0, board_height_px, screen.get_width(), HUD_HEIGHT)
    pygame.draw.rect(screen, (28, 28, 36), hud_rect)
    y = board_height_px + 10
    screen.blit(font.render(hud_line_1, True, TEXT_COLOR), (16, y))
    if hud_line_2:
        screen.blit(font.render(hud_line_2, True, TEXT_COLOR), (16, y + 22))


def replay_solution(
    board: Board,
    solution: Iterable,
    move_duration_ms: int = MOVE_DURATION_MS,
) -> None:
    pygame.init()
    pygame.display.set_caption("Sokoban — AI replay")

    snapshot = board.get_snapshot()
    board_width, board_height = _board_size(snapshot)
    board_width_px = board_width * TILE_SIZE
    board_height_px = board_height * TILE_SIZE
    screen = pygame.display.set_mode((board_width_px, board_height_px + HUD_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    solved_font = pygame.font.SysFont("consolas", 24, bold=True)

    solution = list(solution)
    state = deepcopy(board.initial_state)
    animation: AnimationFrame | None = None
    animation_start_ms = 0
    move_index = 0
    is_paused = False
    is_solved = False

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        is_paused = not is_paused

            now = pygame.time.get_ticks()
            progress = 1.0

            if animation is not None:
                elapsed = now - animation_start_ms
                progress = min(1.0, elapsed / move_duration_ms)
                if progress >= 1.0:
                    animation = None

            elif not is_paused and move_index < len(solution):
                previous_state = deepcopy(state)
                result = board.move(solution[move_index], state)
                if result == MoveResult.ILLEGAL:
                    raise RuntimeError(
                        f"Illegal move during pygame replay at step {move_index + 1}: {solution[move_index]}"
                    )

                animation = _build_animation(previous_state, state)
                animation_start_ms = now
                move_index += 1
                is_solved = result == MoveResult.WIN
                progress = 0.0

            screen.fill(BACKGROUND_COLOR)
            _draw_board(screen, snapshot)
            _draw_entities(screen, snapshot, state, animation, progress)
            _draw_hud(
                screen,
                font,
                solved_font,
                board_height_px,
                move_index,
                len(solution),
                is_paused,
                is_solved,
            )
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
