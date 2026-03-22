import heapq
from search_methods.node import TreeNode
from typing import List
from search_methods.utils import get_priority
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
        self._snapshot = board.get_snapshot()
        #nodo raiz
        self.root = TreeNode(init_state, board, 0, init_state.is_solved(),0,None,None)
        self.known_states: dict[tuple[tuple[int, int], frozenset[tuple[int, int]]], int] = {}

        # lista de nodos frontera (min-heap de (prioridad, nodo))
        self.frontLineNodes: list[tuple[int | tuple[int, int], TreeNode]] = []
        # lista de nodos explorados.
        # TODO: maybe esto puede ser un Set
        self.exploredNodes : List[TreeNode] = []
        self.solution_path : List[Direction] = []

    # def calculate_heuristic(self, state:BoardState) -> int:
    #     return self.root.search_method.calculate_heuristic(state)


    def start_searching(self)->List[Direction]|None:
        self.known_states = {self.root.state.key(): self.root.cost}
        self.frontLineNodes = []
        heapq.heappush(
            self.frontLineNodes,
            (get_priority(self.root, self._snapshot), self.root),
        )
        while len(self.frontLineNodes) > 0:
            _priority, node = heapq.heappop(self.frontLineNodes)

            # Esto permite de vuelta, evitar estar en el mismo estado con mayor costo.
            if node.cost > self.known_states.get(node.state.key(), float("inf")):
                continue

            if node.get_is_goal():
                return list(reversed(get_solution_path(node)))

            self.exploredNodes.append(node)
            list_node = node.expand()
            # Con esto podes evitar hijos con el mismo estado con mayor costo.
            for child in list_node:
                k = child.state.key()
                if k not in self.known_states or child.cost < self.known_states[k]:
                    self.known_states[k] = child.cost
                    heapq.heappush(
                        self.frontLineNodes,
                        (get_priority(child, self._snapshot), child),
                    )

        # Si llega aca, es porque no existe una solucion alcanzable.
        return None
