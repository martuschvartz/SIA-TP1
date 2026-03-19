from search_methods.node import TreeNode
from typing import List
from search_methods.utils import sort_method
from sokoban_engine import BoardState, Board, Direction


# Searching Tree
def get_solution_path(goal_node:TreeNode) -> List[Direction]:
    current_node = goal_node
    to_return : List[Direction] = []
    while current_node.parent_node is not None:
        to_return.append(current_node.action_direction)
        current_node = current_node.parent_node

    return to_return


class Tree:
    def __init__(self, board: Board, init_state: BoardState):
        #nodo raiz
        self.root = TreeNode(init_state, board, 0, init_state.is_solved(),0,None,None)

        # lista de nodos frontera
        self.frontLineNodes:List[TreeNode] = []
        # lista de nodos explorados.
        # TODO: maybe esto puede ser un Set
        self.exploredNodes : List[TreeNode] = []
        self.solution_path : List[Direction] = []

    # def calculate_heuristic(self, state:BoardState) -> int:
    #     return self.root.search_method.calculate_heuristic(state)


    def start_searching(self)->List[Direction]|None:
        self.frontLineNodes.append(self.root)
        while len(self.frontLineNodes) > 0:
            node = self.frontLineNodes.pop(0)

            if node.get_is_goal():
                return list(reversed(get_solution_path(node)))

            self.exploredNodes.append(node)
            list_node = node.expand()
            for child in list_node:
                self.frontLineNodes.append(child)
                # todos los nodos ya tienen sus hijos guardados. No hace falta aca.
            self.frontLineNodes = sort_method(self.frontLineNodes)

        # Si llega aca, es porque no existe una solucion alcanzable.
        return None
