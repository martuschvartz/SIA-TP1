from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment
from sokoban_engine import BoardState

from search_methods.heuristics.Manhattan import manhattan


def hungarian(state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    # Boxes on goals have distance 0 to that goal column; matcher pairs them at no cost.
    if not goals:
        return 0
    boxes = sorted(state.get_boxes_positions())
    goal_list = sorted(goals)
    if not boxes:
        return 0
    n, m = len(boxes), len(goal_list)
    cost = np.zeros((n, m), dtype=np.int64)
    for i, b in enumerate(boxes):
        for j, g in enumerate(goal_list):
            cost[i, j] = manhattan(b, g)
    row_ind, col_ind = linear_sum_assignment(cost)
    return int(cost[row_ind, col_ind].sum())
