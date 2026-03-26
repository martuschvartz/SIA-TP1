from search_methods.heuristics import manhattan, hungarian
from sokoban_engine import BoardState

def mixed (state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    return max(hungarian(state,goals), manhattan(state, goals))
