from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from time import perf_counter

SEARCH_METHODS = ("bfs", "dfs", "greedy", "a*")
HEURISTICS = ("manhattan", "hungarian", "mixed")
INFORMED_METHODS = {"greedy", "a*"}
RUNS_PER_COMBO = 10

W = 60  # box width


# ── ASCII helpers ──────────────────────────────────────────

def _bar(char: str = "─") -> str:
    return char * W


def _header(title: str) -> str:
    pad = W - 2 - len(title)
    left = pad // 2
    right = pad - left
    return f"┌{'─' * (W - 2)}┐\n│{' ' * left}{title}{' ' * right}│\n└{'─' * (W - 2)}┘"


def _section(label: str) -> str:
    inner = f"  {label}  "
    dash = (W - len(inner)) // 2
    return f"{'─' * dash}{inner}{'─' * (W - dash - len(inner))}"


def _combo_banner(idx: int, total: int, level: str, method: str, heuristic: str | None) -> str:
    h_text = heuristic if heuristic else "—"
    tag = f"[{idx}/{total}]"
    info = f"{level}  ·  {method}  ·  {h_text}"
    lines = [
        _bar("─"),
        f"  {tag:<8} {info}",
        _bar("─"),
    ]
    return "\n".join(lines)


def _run_line(run: int, total: int, ok: bool, elapsed: float) -> str:
    status = "ok " if ok else "ERR"
    return f"    ▶  run {run:>{len(str(total))}}/{total}  ·  {status}  ({elapsed:.3f}s)"


def _combo_summary(passed: int, total: int) -> str:
    if passed == total:
        return f"  ✓  {passed}/{total} passed\n"
    return f"  ✗  {passed}/{total} passed  ({total - passed} failed)\n"


def _final_banner(total: int, failures: int) -> str:
    passed = total - failures
    status = "ALL PASSED" if failures == 0 else f"{failures} FAILED"
    lines = [
        "",
        _bar("═"),
        f"  DONE  ·  {total} runs  ·  {passed} ok  ·  {status}",
        _bar("═"),
    ]
    return "\n".join(lines)


# ── core logic ─────────────────────────────────────────────

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
        "--mode", "ai",
        "--search-method", search_method,
        "--map", str(level_path),
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
    runs_per_combo: int = RUNS_PER_COMBO,
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

    total_runs = len(combos) * runs_per_combo

    print(_header("SIA-TP1  ·  BULK SOLVER"))
    print()
    print(f"  Levels       : {len(levels)}")
    print(f"  Combos       : {len(combos)}")
    print(f"  Runs / combo : {runs_per_combo}")
    print(f"  Total runs   : {total_runs}")
    print()

    failures = 0
    total_executions = 0

    for i, (method, heuristic, level) in enumerate(combos, start=1):
        print(_combo_banner(i, len(combos), level.name, method, heuristic))

        combo_failures = 0
        for run in range(1, runs_per_combo + 1):
            total_executions += 1
            cmd = build_command(
                python_exec=sys.executable,
                main_py=main_py,
                level_path=level,
                search_method=method,
                heuristic=heuristic,
                replay=replay,
            )
            t0 = perf_counter()
            result = subprocess.run(cmd, cwd=project_root)
            elapsed = perf_counter() - t0
            ok = result.returncode == 0

            print(_run_line(run, runs_per_combo, ok, elapsed))

            if not ok:
                failures += 1
                combo_failures += 1
                if not continue_on_error:
                    print()
                    print("  Stopping at first failure. Use --continue-on-error to keep going.")
                    print(_final_banner(total_executions, failures))
                    return result.returncode

        print(_combo_summary(runs_per_combo - combo_failures, runs_per_combo))

    print(_final_banner(total_executions, failures))
    return 0 if failures == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all combinations of search_method × heuristic × level, N times each."
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
    parser.add_argument(
        "--runs",
        type=int,
        default=RUNS_PER_COMBO,
        metavar="N",
        help=f"Number of runs per combo (default: {RUNS_PER_COMBO}).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        run_all(
            project_root=args.project_root.resolve(),
            replay=args.replay,
            continue_on_error=args.continue_on_error,
            runs_per_combo=args.runs,
        )
    )
