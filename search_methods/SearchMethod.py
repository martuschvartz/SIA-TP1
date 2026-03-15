from sokoban_engine import Board, BoardSnapshot, BoardState
from sokoban_engine.board import Board
from abc import ABC, abstractmethod


class SearchMethod(ABC):

    board : BoardSnapshot
    def __init__(self, state: BoardState):
        self.state = state


    @staticmethod
    def set_board(new_board: BoardSnapshot):
        board = new_board

    @staticmethod
    def get_board() -> BoardSnapshot:
        return SearchMethod.board


    # frontier_nodes : List[Node]


    @abstractmethod
    def calculate_heuristic(self, state:BoardState) -> int:






    #    def get_next_move(self) -> BoardState:
    #     Board.get_box_at((0,0), self.state)


