from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List

from .model import Domains


@dataclass
class Stats:
    start_ts: float
    nodes: int = 0
    assignments: int = 0
    pruned: int = 0

    # propagator counters
    hidden_single_hits: int = 0
    pointer_fires: int = 0
    cage_recomps: int = 0

    def elapsed(self) -> float:
        return time.monotonic() - self.start_ts


def grid_to_str(grid: List[List[int]]) -> str:
    lines: List[str] = []
    for r in range(len(grid)):
        row = grid[r]
        parts = []
        for c in range(len(row)):
            v = row[c]
            parts.append(str(v) if v else ".")
            if c % 3 == 2 and c != len(row) - 1:
                parts.append("|")
        line = " ".join(parts)
        lines.append(line)
        if r % 3 == 2 and r != len(grid) - 1:
            lines.append("------+-------+------")
    return "\n".join(lines)


def domains_histogram(dom: Domains) -> Dict[int, int]:
    # Include 0 bucket to reflect temporary contradictions during search branches
    hist: Dict[int, int] = {i: 0 for i in range(0, dom.size + 1)}
    for s in dom.dom.values():
        l = len(s)
        if l not in hist:
            hist[l] = 0
        hist[l] += 1
    return hist


def heartbeat(stats: Stats, dom: Domains) -> str:
    hist = domains_histogram(dom)
    hist_str = ", ".join(f"{k}:{v}" for k, v in sorted(hist.items()))
    return (
        f"[{stats.elapsed():.1f}s] nodes={stats.nodes} assign={stats.assignments} "
        f"pruned={stats.pruned} dom{{{hist_str}}} "
        f"cages{{recomp={stats.cage_recomps}}} pointer{{fires={stats.pointer_fires}}} "
        f"hidden_single={stats.hidden_single_hits}"
    )
