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
        # Tertiary heap tiebreaker (fires only when the full priority tuple is equal).
        # A*: primary=f, secondary=h — both encoded in the heap tuple by get_priority().
        # Greedy: primary=h, secondary=level — also encoded in the heap tuple.
        # cost is the semantically correct fallback for A* (cost == level for unit-step costs).
        return self.cost < other.cost

    def expand(self) -> List['TreeNode']:
        if  self.board.is_in_deadlock(self.state):
            return self.children

        for direction in self.possible_actions:
            new_state = self.state.copy()
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
