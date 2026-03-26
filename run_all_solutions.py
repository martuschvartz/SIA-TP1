from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from time import perf_counter

SEARCH_METHODS = ("bfs", "dfs", "greedy", "a*")
HEURISTICS = ("manhattan", "hungarian")
INFORMED_METHODS = {"greedy", "a*"}


def discover_levels(maps_dir: Path) -> list[Path]:
    levels = sorted(p for p in maps_dir.glob("*.txt") if p.is_file())
    if not levels:
        raise FileNotFoundError(f"No .txt levels found in: {maps_dir}")
    return levels


def build_command(
    python_exec: str,
    main_py: Path,
    level_path: Path,
    search_method: str,
    heuristic: str | None,
    replay: bool,
) -> list[str]:
    cmd = [
        python_exec,
        str(main_py),
        "--mode",
        "ai",
        "--search-method",
        search_method,
        "--map",
        str(level_path),
    ]
    if heuristic is not None:
        cmd.extend(["--heuristic", heuristic])
    if replay:
        cmd.append("--replay")
    return cmd


def run_all(
    project_root: Path,
    replay: bool,
    continue_on_error: bool,
) -> int:
    main_py = project_root / "main.py"
    maps_dir = project_root / "resources" / "maps"

    if not main_py.is_file():
        print(f"[ERROR] main.py not found at: {main_py}")
        return 2

    try:
        levels = discover_levels(maps_dir)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 2

    combos: list[tuple[str, str | None, Path]] = []
    for level in levels:
        for method in SEARCH_METHODS:
            if method in INFORMED_METHODS:
                for heuristic in HEURISTICS:
                    combos.append((method, heuristic, level))
            else:
                combos.append((method, None, level))

    print(f"Levels found: {len(levels)}")
    print(f"Total runs: {len(combos)}")

    failures = 0
    total_executions = 0
    combo_duration_seconds = 120.0

    for i, (method, heuristic, level) in enumerate(combos, start=1):
        h_text = heuristic if heuristic is not None else "N/A"
        print(
            f"[{i}/{len(combos)}] level={level.name} method={method} heuristic={h_text}"
        )

        combo_start = perf_counter()
        run = 0

        while perf_counter() - combo_start < combo_duration_seconds and run < 20:
            run += 1
            total_executions += 1
            elapsed = perf_counter() - combo_start
            print(
                f"  -> Executing #{run} (elapsed {elapsed:.2f}/{combo_duration_seconds:.0f}s)"
            )

            cmd = build_command(
                python_exec=sys.executable,
                main_py=main_py,
                level_path=level,
                search_method=method,
                heuristic=heuristic,
                replay=replay,
            )

            result = subprocess.run(cmd, cwd=project_root)
            if result.returncode != 0:
                failures += 1
                print(f"  -> failed with exit code {result.returncode}")
                if not continue_on_error:
                    print("Stopping at first failure. Use --continue-on-error to keep going.")
                    return result.returncode

    print("\nDone.")
    print(f"Total executions: {total_executions}")
    print(f"Successful executions: {total_executions - failures}")
    print(f"Failed executions: {failures}")
    return 0 if failures == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all combinations of search_method, heuristic (if applicable), and level."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Project root directory (default: directory of this script).",
    )
    parser.add_argument(
        "--replay",
        action="store_true",
        help="Pass --replay to main.py runs (disabled by default).",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue remaining combinations even if one run fails.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        run_all(
            project_root=args.project_root.resolve(),
            replay=args.replay,
            continue_on_error=args.continue_on_error,
        )
    )
