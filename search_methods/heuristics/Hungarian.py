from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment
from sokoban_engine import BoardState


def hungarian(state: BoardState, goals: frozenset[tuple[int, int]]) -> int:
    # Boxes on goals have distance 0 to that goal column; matcher pairs them at no cost.
    if not goals:
        return 0
    boxes = state.get_boxes_positions()
    if not boxes:
        return 0
    b = np.array(list(boxes), dtype=np.int64)   # (n, 2)
    g = np.array(list(goals), dtype=np.int64)    # (m, 2)
    cost = np.abs(b[:, None, :] - g[None, :, :]).sum(axis=2)  # (n, m), no Python loop
    # retorna la combinación de índices que encontró para la solución
    row_ind, col_ind = linear_sum_assignment(cost)
    return int(cost[row_ind, col_ind].sum())
