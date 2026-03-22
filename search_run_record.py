# search_methods/search_run_logger.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd


@dataclass
class SearchRunRecord:
    search_method: str
    heuristic: str # Heuristic name or "None" for uninformed method
    level_name: str
    result: str  # "success" or "failure"
    solution_cost: int | str
    expanded_nodes: int # counts total expanded nodes
    frontier_nodes_pending: int #counts nodes inserted into the frontier, not yet expanded when the solution was found
    frontier_nodes_inserted: int #counts total nodes inserted into the frontier (included non-expanded ones)
    solution_path: str
    processing_time_seconds: float


class SearchRunLogger:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.columns = [
            "search_method",
            "heuristic",
            "level_name",
            "result",
            "solution_cost",
            "expanded_nodes",
            "frontier_nodes_pending",
            "frontier_nodes_inserted",
            "solution_path",
            "processing_time_seconds",
        ]

    def append(self, record: SearchRunRecord) -> None:
        row_df = pd.DataFrame([asdict(record)], columns=self.columns)

        if self.file_path.exists():
            # Append mode: write only row, no header
            row_df.to_csv(self.file_path, mode="a", header=False, index=False)
        else:
            # First write: include header
            row_df.to_csv(self.file_path, mode="w", header=True, index=False)
