from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from .model import BorderClue, Cell, Puzzle


def peers_of(size: int, cell: Cell) -> Set[Cell]:
    r, c = cell
    cells: Set[Cell] = set()
    # row
    for cc in range(1, size + 1):
        if cc != c:
            cells.add((r, cc))
    # col
    for rr in range(1, size + 1):
        if rr != r:
            cells.add((rr, c))
    # box (3x3)
    br = (r - 1) // 3
    bc = (c - 1) // 3
    for i in range(1, 4):
        for j in range(1, 4):
            rr = 3 * br + i
            cc = 3 * bc + j
            if rr == r and cc == c:
                continue
            cells.add((rr, cc))
    return cells


def all_units(size: int) -> List[List[Cell]]:
    units: List[List[Cell]] = []
    # rows
    for r in range(1, size + 1):
        units.append([(r, c) for c in range(1, size + 1)])
    # cols
    for c in range(1, size + 1):
        units.append([(r, c) for r in range(1, size + 1)])
    # boxes
    for br in range(0, 3):
        for bc in range(0, 3):
            unit: List[Cell] = []
            for i in range(1, 4):
                for j in range(1, 4):
                    unit.append((3 * br + i, 3 * bc + j))
            units.append(unit)
    return units


def pointer_line_cells(puzzle: Puzzle, clue: BorderClue) -> List[Cell]:
    N = puzzle.size
    s = clue.side.upper()
    idx = clue.index
    line: List[Cell] = []
    if s == "L":
        r = idx
        line = [(r, c) for c in range(1, N + 1)]
    elif s == "R":
        r = idx
        line = [(r, c) for c in range(N, 0, -1)]
    elif s == "T":
        c = idx
        line = [(r, c) for r in range(1, N + 1)]
    elif s == "B":
        c = idx
        line = [(r, c) for r in range(N, 0, -1)]
    else:
        raise ValueError(f"Unknown side: {clue.side}")
    return line

