from search_methods.node import TreeNode
from typing import List
from queue import Queue
from utils import sort_method
from sokoban_engine import BoardState, Board


# Searching Tree
class Tree:
    def __init__(self, board: Board, init_state: BoardState, search_method:str):
        #nodo raiz
        self.root = TreeNode(init_state, board, 0, False,0)

        # lista de nodos frontera
        self.frontLineNodes:Queue = Queue(0)
        # lista de nodos explorados.
        # TODO: maybe esto puede ser un Set
        self.exploredNodes : List[TreeNode] = []
        self.search_method = search_method

    # def calculate_heuristic(self, state:BoardState) -> int:
    #     return self.root.search_method.calculate_heuristic(state)


    def start_searching(self):
        self.frontLineNodes.put(self.root)
        while self.frontLineNodes.qsize() > 0:
            node = self.frontLineNodes.get()

            if node.get_is_goal:
                # TODO: retornar la solucion. somehow
                return None

            self.exploredNodes.append(node)
            list_node = sort_method(node.expand(), self.search_method)
            for child in list_node:
                self.frontLineNodes.put(child)
                # todos los nodos ya tienen sus hijos guardados. No hace falta aca.


        # Si llega aca, es porque no existe una solucion alcanzable.
        return None
