from __future__ import annotations

from typing import List, Tuple

from .constraints import pointer_line_cells
from .model import Puzzle


def verify(puzzle: Puzzle, grid: List[List[int]]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    N = puzzle.size

    def in_bounds(v: int) -> bool:
        return 1 <= v <= N

    # Check rows/cols/boxes (Sudoku)
    if puzzle.rules.sudoku:
        for r in range(1, N + 1):
            seen = set()
            for c in range(1, N + 1):
                v = grid[r - 1][c - 1]
                if v == 0:
                    continue
                if not in_bounds(v):
                    errors.append(f"Out-of-range at r{r}c{c}: {v}")
                if v in seen:
                    errors.append(f"Row {r} duplicate value {v}")
                seen.add(v)
        for c in range(1, N + 1):
            seen = set()
            for r in range(1, N + 1):
                v = grid[r - 1][c - 1]
                if v == 0:
                    continue
                if v in seen:
                    errors.append(f"Col {c} duplicate value {v}")
                seen.add(v)
        for br in range(0, 3):
            for bc in range(0, 3):
                seen = set()
                for i in range(1, 4):
                    for j in range(1, 4):
                        r = 3 * br + i
                        c = 3 * bc + j
                        v = grid[r - 1][c - 1]
                        if v == 0:
                            continue
                        if v in seen:
                            errors.append(f"Box ({br+1},{bc+1}) duplicate value {v}")
                        seen.add(v)

    # Cages
    if puzzle.rules.cage_sum:
        for idx, cage in enumerate(puzzle.cages):
            vs = [grid[r - 1][c - 1] for (r, c) in cage.cells]
            if all(v != 0 for v in vs):
                s = sum(vs)
                if s != cage.sum:
                    errors.append(
                        f"Cage#{idx} sum mismatch: expected {cage.sum}, got {s}, cells={cage.cells}"
                    )

    # Pointer lines
    if puzzle.rules.numbered_rooms:
        for clue in puzzle.border_clues:
            line = pointer_line_cells(puzzle, clue)
            L1 = grid[line[0][0] - 1][line[0][1] - 1]
            if L1 == 0:
                continue
            n = L1
            if not (1 <= n <= N):
                errors.append(f"Pointer {clue.side},{clue.index},{clue.digit}: L1 out of range {n}")
                continue
            target = line[n - 1]
            val = grid[target[0] - 1][target[1] - 1]
            if val != 0 and val != clue.digit:
                errors.append(
                    f"Pointer {clue.side},{clue.index},{clue.digit} violated: N={n}, L[N]={val}"
                )

    return (len(errors) == 0, errors)

