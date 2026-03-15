from search_methods.node import TreeNode
from typing import List
from queue import Queue

from sokoban_engine import BoardState, Board


# Searching Tree

class Tree:
    #dfs
    #bfs
    #def __init__(self, root: TreeNode, func(BoardState , int ) orderMethod:
    def __init__(self, board: Board, init_state: BoardState,  ):
        #nodo raiz
        self.root = TreeNode(init_state, board, 0, False)

        # lista de nodos frontera
        self.frontLineNodes:Queue = Queue(0)
        # lista de nodos explorados. TODO: maybe esto puede ser un Set
        self.exploredNodes : List[TreeNode] = []

    def calculate_heuristic(self, state:BoardState) -> int:
        return self.root.search_method.calculate_heuristic(state)


    def start_searching(self):
        self.frontLineNodes.put(self.root)
        while self.frontLineNodes.qsize() > 0:
            node = self.frontLineNodes.get()
            # retornar la solucion. somehow
            if node.get_is_goal:
                return None
            self.exploredNodes.append(node)
            # TODO: ver si sortear el orden dependiendo del metodo
            ListNode = node.expand().sortBy(orderMethod)

            for child in ListNode:
                # todos los nodos ya tienen sus hijos guardados.
                self.frontLineNodes.put(child)





        return None
