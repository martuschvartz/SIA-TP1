from copy import deepcopy
from time import sleep

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
    solution = tree.start_searching()

    if not solution:
        print("No reachable solution found.")
        return

    print(f"Solution found with {len(solution)} moves.")
    replay_state = deepcopy(board.initial_state)
    replay_solution(board, replay_state, solution, delay_seconds=1)


if __name__ == "__main__":
    main()
