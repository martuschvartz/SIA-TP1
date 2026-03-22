"""Runtime search settings: loaded from config.json, overridable via CLI before search runs."""

from __future__ import annotations

import importlib
import json
from pathlib import Path


class _Settings:
    def __init__(self) -> None:
        self._search_method: str = "a*"
        self._max_tree_depth: int = 10_000
        self._heuristic: str = "nearest_goal_per_box"

    def load(self, path: Path | None = None) -> None:
        config_path = path or Path(__file__).with_name("config.json")
        with config_path.open(encoding="utf-8") as f:
            data = json.load(f)
        self._search_method = str(data["search_method"])
        self._max_tree_depth = int(data["max_tree_depth"])
        self._heuristic = str(data.get("heuristic", "nearest_goal_per_box"))
        heuristics_mod = importlib.import_module("search_methods.heuristics")
        heuristics_mod.validate_heuristic_name(self._heuristic)

    def override(
        self,
        *,
        search_method: str | None = None,
        heuristic: str | None = None,
    ) -> None:
        if search_method is not None:
            self._search_method = search_method
        if heuristic is not None:
            heuristics_mod = importlib.import_module("search_methods.heuristics")
            heuristics_mod.validate_heuristic_name(heuristic)
            self._heuristic = heuristic

    def get_search_method(self) -> str:
        return self._search_method

    def get_heuristic(self) -> str:
        return self._heuristic

    def get_max_tree_depth(self) -> int:
        return self._max_tree_depth


Settings = _Settings()
Settings.load()
