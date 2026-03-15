from search_methods.node import TreeNode
from typing import List
from queue import Queue

# Searching Tree

class Tree:
    def __init__(self, root: TreeNode):
        #nodo raiz
        self.root = root
        # lista de nodos frontera
        self.frontLineNodes:Queue = Queue(0)
        # lista de nodos explorados. TODO: maybe esto puede ser un Set
        self.exploredNodes : List[TreeNode] = []


    def start_searching(self):
        self.frontLineNodes.put(self.root)
        while self.frontLineNodes.qsize() > 0:
            node = self.frontLineNodes.get()
            # retornar la solucion. somehow
            if node.get_is_goal:
                return None
            self.exploredNodes.append(node)
            ListNode = node.expand()
            for child in ListNode:
                # TODO: ver si sortear el orden dependiendo del metodo
                # todos los nodos ya tienen sus hijos guardados.
                self.frontLineNodes.put(child)



        return None
