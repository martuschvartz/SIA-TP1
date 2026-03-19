"""
Sokoban — modo prueba en terminal.
w/a/s/d = mover, r = reset, q = salir. Presioná Enter después de cada tecla.
"""
from copy import copy, deepcopy

from sokoban_engine import Board, BoardSnapshot, BoardState, Direction, MoveResult

LEVEL = """
    ######
    #    #
    #.$$.#
  ###  $ ###
  #   $@$  #
  ###  $ ###
    #.$$.#
    #    #
    ######
"""
# LEVEL = """
#     ###########
#    # . $ @  $. #
#     ###########
# """


def render(snapshot: BoardSnapshot, state: BoardState) -> str:
    """Renders the board from a static snapshot and a dynamic state."""
    walls = snapshot.walls
    goals = snapshot.goals
    player_pos = state.player.position
    box_positions = state.get_boxes_positions()

    lines = []
    for y in range(snapshot.min_y, snapshot.max_y + 1):
        row = []
        for x in range(snapshot.min_x, snapshot.max_x + 1):
            pos = (x, y)
            if pos in walls:
                row.append("#")
            elif pos == player_pos:
                row.append("+" if pos in goals else "@")
            elif pos in box_positions:
                row.append("*" if pos in goals else "$")
            elif pos in goals:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines)


def main() -> None:
    board = Board(LEVEL)
    snapshot = board.get_snapshot()
    key_to_direction = {
        "w": Direction.UP,
        "s": Direction.DOWN,
        "a": Direction.LEFT,
        "d": Direction.RIGHT,
    }

    print("Sokoban — Prueba del motor")
    print("w/a/s/d = mover | r = reset | q = salir")
    print()

    direction_to_key = {d: k for k, d in key_to_direction.items()}

    state = deepcopy(board.initial_state)
    while True:
        print(render(snapshot, state))
        legal = board.get_legal_moves(state)
        legal_str = ", ".join(direction_to_key[d].upper() for d in legal) or "ninguno"
        boxes_done = len(snapshot.boxes_on_goals(state))
        total_goals = len(snapshot.goals)
        print(f"Legal moves: {legal_str}   Boxes on goals: {boxes_done}/{total_goals}")
        print()

        cmd = input("> ").strip().lower()
        if not cmd:
            continue
        key = cmd[0]

        if key == "q":
            print("Chau!")
            break

        if key == "r":
            state = deepcopy(board.initial_state)
            print("Reset.\n")
            continue

        if key in key_to_direction:
            result = board.move(key_to_direction[key],state)
            if result == MoveResult.WIN:
                print(render(snapshot, state))
                print("\n¡Ganaste!")
                break
            elif result == MoveResult.ILLEGAL:
                print("Movimiento ilegal.\n")
        else:
            print("Tecla no válida. Usá w/a/s/d, r o q.\n")


if __name__ == "__main__":
    main()