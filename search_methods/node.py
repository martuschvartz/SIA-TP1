import copy
from time import sleep
from typing import List, Optional

import search_methods
# from search_methods.SearchMethod import SearchMethod
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


    def expand(self) -> List['TreeNode']:
        for direction in self.possible_actions:
            new_state = copy.deepcopy(self.state)
            move_result = self.board.move(direction, new_state) == MoveResult.WIN
            new_node = TreeNode(new_state, self.board, self.cost + 1, move_result, self.level+1, direction, self)
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
