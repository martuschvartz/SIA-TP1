"""
Sokoban — entrypoint: pygame UI, player or AI mode.

CLI arguments override values from search_methods/config.json when provided.
"""

from __future__ import annotations

import argparse
import sys
from copy import deepcopy
from pathlib import Path
from time import perf_counter

from search_methods.settings import Settings
from search_methods.tree import Tree
from search_run_record import SearchRunLogger, SearchRunRecord
from sokoban_engine import Board

from sokoban_pygame import run_ai_replay, run_player

_REPO_ROOT = Path(__file__).resolve().parent
_DEFAULT_MAP = _REPO_ROOT / "resources" / "maps" / "LEVEL1-Easy.txt"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sokoban with pygame (player or AI).")
    parser.add_argument(
        "-m",
        "--mode",
        choices=("player", "ai"),
        default="ai",
        help="player = human WASD; ai = run search then animate solution (default: ai)",
    )
    parser.add_argument(
        "--replay",
        action="store_true",
        help="In ai mode, animate the solution after search (default: disabled)",
    )
    parser.add_argument(
        "--search-method",
        default=None,
        metavar="METHOD",
        help="Override config: bfs, dfs, a*, greedy",
    )
    parser.add_argument(
        "--heuristic",
        default=None,
        metavar="NAME",
        help="Override config heuristic (a* / greedy): zero, manhattan, nearest_goal_per_box, hungarian, mixed",
    )
    parser.add_argument(
        "--map",
        "--level",
        dest="map_path",
        default=None,
        metavar="PATH",
        help="Path to level .txt (default: resources/maps/default.txt)",
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="Path to search JSON config (default: search_methods/config.json)",
    )
    return parser.parse_args(argv)


def _apply_settings(args: argparse.Namespace) -> None:
    if args.config is not None:
        Settings.load(Path(args.config))
    Settings.override(
        search_method=args.search_method,
        heuristic=args.heuristic,
    )


def _load_level_text(args: argparse.Namespace) -> tuple[str, str]:
    map_path = Path(args.map_path) if args.map_path else _DEFAULT_MAP

    if not map_path.is_file():
        print(f"Map file not found: {map_path}", file=sys.stderr)
        sys.exit(1)
    level_name = map_path.stem
    return map_path.read_text(encoding="utf-8"), level_name


def _run_ai(board: Board, level_name: str, with_replay: bool) -> None:
    initial_state = deepcopy(board.initial_state)
    tree = Tree(board, initial_state)
    is_oom = False
    start_time = perf_counter()
    solution = None

    try:
        solution = tree.start_searching()
    except MemoryError:
        is_oom = True
        tree.frontier_nodes_remaining = len(tree.frontLineNodes)
        tree.frontLineNodes.clear()
        tree.known_states.clear()

    elapsed_seconds = perf_counter() - start_time

    success = solution is not None
    timed_out = tree.timed_out

    solution_cost = tree.solution_cost if success else "N/A"
    if success:
        solution_path = " -> ".join(move.name for move in solution)
        result_str = "success"
    elif timed_out:
        solution_path = "Timeout reached"
        result_str = "timeout"
    elif is_oom:
        solution_path = "OOM reached"
        result_str = "oom"
    else:
        solution_path = "Not found"
        result_str = "failure"

    logger = SearchRunLogger(_REPO_ROOT / "search_runs.csv")
    heuristic_name = Settings.get_heuristic() if Settings.get_search_method() in ("a*", "greedy") else "None"
    logger.append(
        SearchRunRecord(
            search_method=Settings.get_search_method(),
            heuristic=heuristic_name,
            level_name=level_name,
            result=result_str,
            solution_cost=solution_cost,
            expanded_nodes=tree.expanded_nodes_count,
            frontier_nodes_pending=tree.frontier_nodes_remaining,
            frontier_nodes_inserted=tree.frontier_nodes_count,
            solution_path=solution_path,
            processing_time_seconds=round(elapsed_seconds, 6),
        )
    )

    stats_lines = [
        "=== Search statistics ===",
        f"Result: {result_str}",
        f"Timeout limit: {Settings.get_search_timeout_seconds():.0f} seconds",
        f"Solution cost: {solution_cost}",
        f"Expanded nodes: {tree.expanded_nodes_count}",
        (
            "Frontier nodes: "
            f"{tree.frontier_nodes_remaining} pending, {tree.frontier_nodes_count} inserted"
        ),
        f"Solution path: {solution_path}",
        f"Processing time: {elapsed_seconds:.6f} seconds",
    ]

    output_file = _REPO_ROOT / "output.txt"
    output_file.write_text("\n".join(stats_lines) + "\n", encoding="utf-8")

    if solution is None:
        if timed_out:
            print(
                f"Search stopped after timeout ({Settings.get_search_timeout_seconds():.0f} seconds)."
            )
        else:
            print("No reachable solution found.")
        return

    print(f"Solution found with {len(solution)} moves in {elapsed_seconds:.4f} seconds.")
    if with_replay: run_ai_replay(board, solution)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    _apply_settings(args)
    level_text, level_name = _load_level_text(args)

    board = Board(level_text)

    if args.mode == "player":
        run_player(board)
    else:
        _run_ai(board, level_name, args.replay)


if __name__ == "__main__":
    main()
