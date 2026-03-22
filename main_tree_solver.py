from copy import deepcopy
from pathlib import Path
from time import perf_counter, sleep

from main import LEVEL, render
from search_methods.tree import Tree
from sokoban_engine import Board, MoveResult


def replay_solution(board, state, solution, delay_seconds=1.5):
    snapshot = board.get_snapshot()
    print("Initial state:")
    print(render(snapshot, state))
    print()

    for i, move in enumerate(solution, start=1):
        result = board.move(move, state)
        print(f"Step {i}: {move.name}")
        print(render(snapshot, state))
        print()

        if result == MoveResult.ILLEGAL:
            raise RuntimeError(f"Illegal move during replay at step {i}: {move}")
        if result == MoveResult.WIN:
            print("Solved!")
            return

        sleep(delay_seconds)

    print("Replay finished.")


def main():
    board = Board(LEVEL)
    initial_state = deepcopy(board.initial_state)

    tree = Tree(board, initial_state)
    start_time = perf_counter()
    solution = tree.start_searching()
    elapsed_seconds = perf_counter() - start_time

    success = solution is not None
    result_str = "success" if success else "failure"
    solution_cost = tree.solution_cost if success else "N/A"
    solution_path = " -> ".join(move.name for move in solution) if success else "Not found"

    stats_lines = [
        "=== Search statistics ===",
        f"Result: {result_str}",
        f"Solution cost: {solution_cost}",
        f"Expanded nodes: {tree.expanded_nodes_count}",
        (
            "Frontier nodes: "
            f"{tree.frontier_nodes_remaining} pending, {tree.frontier_nodes_count} inserted"
        ),
        f"Solution path: {solution_path}",
        f"Processing time: {elapsed_seconds:.6f} seconds",
    ]

    output_file = Path(__file__).resolve().parent / "output.txt"
    output_file.write_text("\n".join(stats_lines) + "\n", encoding="utf-8")

    if solution is None:
        print("No reachable solution found.")
        return

    print(f"Solution found with {len(solution)} moves.")
    replay_state = deepcopy(board.initial_state)
    replay_solution(board, replay_state, solution, delay_seconds=1)


if __name__ == "__main__":
    main()
