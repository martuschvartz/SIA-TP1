from search_methods.heuristics import nearest_goal_per_box, hungarian
from sokoban_engine import BoardState

def mixed (state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    return max(hungarian(state,goals), nearest_goal_per_box(state,goals))
