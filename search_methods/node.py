from typing import List, Optional

from sokoban_engine import BoardState, Board, Direction, MoveResult


class TreeNode:
    def __init__(self, state: BoardState, board: Board, cost: int, is_goal: bool, level: int, action_direction:Optional[Direction],
                 parent_node : Optional['TreeNode']) -> None:
        self.state = state
        self.board = board
        self.cost = cost
        self.possible_actions = board.get_legal_moves(state)
        self.children: List[TreeNode] = []
        self.parent_node = parent_node
        #profundidad de un nodo
        self.level = level
        self.is_goal = is_goal
        self.action_direction = action_direction

    def __lt__(self, other: "TreeNode") -> bool:
        return self.level < other.level

    def expand(self) -> List['TreeNode']:
        for direction in self.possible_actions:
            new_state = self.state.copy()

            # 1. Let the engine handle all the math and movement
            move_result = self.board.move(direction, new_state)

            # 2. Find out which box moved using pure Set difference! (No math required)
            moved_boxes = new_state.get_boxes_positions() - self.state.get_boxes_positions()

            # next(iter(...)) gets the single item from the set, or None if the set is empty
            pushed_box_pos = next(iter(moved_boxes), None)

            # 3. Check for deadlock efficiently!
            if not self.board.is_in_deadlock(new_state, pushed_box_pos):
                is_win = (move_result == MoveResult.WIN)
                new_node = TreeNode(new_state, self.board, self.cost + 1, is_win, self.level + 1, direction, self)
                self.children.append(new_node)

        return self.children


    def get_children(self) -> List['TreeNode']:
        return self.children

    def get_cost(self) -> int:
        return self.cost


    def get_state(self) -> BoardState:
        return self.state

    def get_is_goal(self) -> bool:
        return self.is_goal

    def get_level(self) -> int:
        return self.level
