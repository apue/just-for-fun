from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .debug import grid_to_str, heartbeat, Stats
from .parser import load_puzzle
from .solver import SolveOptions, solve
from .verify import verify


def parse_args(argv):
    p = argparse.ArgumentParser(description="Clue-Cage Sudoku CLI")
    p.add_argument("--puzzle", default="docs/clue-cage-sudoku-data.json", help="Puzzle JSON path")
    p.add_argument("--propagate-only", action="store_true", help="Only run propagation, no search")
    p.add_argument("--max-seconds", type=float, default=None)
    p.add_argument("--max-nodes", type=int, default=None)
    p.add_argument("--trace", action="store_true")
    p.add_argument("--trace-interval", type=float, default=10.0)
    p.add_argument("--stats", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    # Resolve puzzle path: try CWD first, then project root (two levels up from src/)
    raw = Path(args.puzzle)
    if raw.exists():
        puzzle_path = raw
    else:
        # project root inferred from this file: src/clue_cage_sudoku/main.py -> repo_root = parents[2]
        repo_root = Path(__file__).resolve().parents[2]
        candidate = (repo_root / raw).resolve()
        if candidate.exists():
            puzzle_path = candidate
        else:
            # also try repo_root/docs/<filename> if not already under docs/
            if raw.parent.name != "docs":
                alt = (repo_root / "docs" / raw.name).resolve()
                if alt.exists():
                    puzzle_path = alt
                else:
                    raise FileNotFoundError(f"Puzzle JSON not found: {raw} (also tried {candidate} and {alt})")
            else:
                raise FileNotFoundError(f"Puzzle JSON not found: {raw} (also tried {candidate})")

    puzzle = load_puzzle(str(puzzle_path))
    opts = SolveOptions(
        propagate_only=args.propagate_only,
        max_seconds=args.max_seconds,
        max_nodes=args.max_nodes,
        trace=args.trace,
        trace_interval=args.trace_interval,
    )
    start = time.monotonic()
    grid = solve(puzzle, options=opts)
    elapsed = time.monotonic() - start
    print(grid_to_str(grid))
    ok, errors = verify(puzzle, grid)
    print(f"\nverify: {'OK' if ok else 'FAIL'}")
    if not ok:
        for e in errors:
            print(f"- {e}")
    if args.stats:
        # On-demand: run a short propagate-only to report heartbeat-like stats
        # (We do not capture internal stats from the solve call for simplicity here.)
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
