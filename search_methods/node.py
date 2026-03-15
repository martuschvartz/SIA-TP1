import copy
from time import sleep
from typing import List

import search_methods
# from search_methods.SearchMethod import SearchMethod
from sokoban_engine import BoardState, Board, Direction, MoveResult


class TreeNode:
    def __init__(self, state: BoardState, board: Board, cost: int, is_goal: bool, level: int) -> None:
        self.state = state
        self.board = board
        self.cost = cost
        self.directions = board.get_legal_moves(state)
        self.children: List[TreeNode] = []
        #profundidad de un nodo
        self.level = level
        self.is_goal = is_goal

    def expand(self) -> List['TreeNode']:
        for direction in self.directions:
            new_state = copy.deepcopy(self.state)
            move_result = self.board.move(direction, new_state) == MoveResult.WIN
            # new_node = TreeNode(new_state, self.board,  self.cost + 1, move_result)
            new_node = TreeNode(new_state, self.board, self.cost + 1, move_result, self.level+1)
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
