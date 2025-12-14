from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

Cell = Tuple[int, int]  # (r, c) with 1-based indexing


@dataclass
class Cage:
    sum: int
    cells: List[Cell]


@dataclass
class BorderClue:
    side: str  # "L", "R", "T", "B"
    index: int  # row or col number (1-based)
    digit: int


@dataclass
class Rules:
    sudoku: bool = True
    cage_sum: bool = True
    cage_all_different: bool = False
    numbered_rooms: bool = True


@dataclass
class Puzzle:
    size: int
    rules: Rules
    border_clues: List[BorderClue]
    cages: List[Cage]


@dataclass
class Domains:
    size: int
    dom: Dict[Cell, Set[int]] = field(default_factory=dict)

    @classmethod
    def full(cls, size: int) -> "Domains":
        d = cls(size=size)
        for r in range(1, size + 1):
            for c in range(1, size + 1):
                d.dom[(r, c)] = set(range(1, size + 1))
        return d

    def copy(self) -> "Domains":
        nd = Domains(size=self.size)
        nd.dom = {k: set(v) for k, v in self.dom.items()}
        return nd

    def assign(self, cell: Cell, val: int) -> bool:
        cur = self.dom[cell]
        if cur == {val}:
            return False
        self.dom[cell] = {val}
        return True

    def remove(self, cell: Cell, val: int) -> bool:
        s = self.dom[cell]
        if val in s:
            s.remove(val)
            return True
        return False

    def set_values(self, cell: Cell, values: Set[int]) -> bool:
        cur = self.dom[cell]
        if values == cur:
            return False
        self.dom[cell] = set(values)
        return True

    def is_singleton(self, cell: Cell) -> bool:
        return len(self.dom[cell]) == 1

    def get_singleton(self, cell: Cell) -> Optional[int]:
        d = self.dom[cell]
        if len(d) == 1:
            return next(iter(d))
        return None

    def snapshot_grid(self) -> List[List[int]]:
        grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for (r, c), s in self.dom.items():
            if len(s) == 1:
                grid[r - 1][c - 1] = next(iter(s))
        return grid

