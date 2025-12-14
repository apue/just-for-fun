from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .debug import Stats
from .model import Cell, Domains, Puzzle
from .propagation import PropagationError, propagate_fixpoint


@dataclass
class SolveOptions:
    propagate_only: bool = False
    max_seconds: Optional[float] = None
    max_nodes: Optional[int] = None
    trace: bool = False
    trace_interval: float = 10.0


def solve(puzzle: Puzzle, options: Optional[SolveOptions] = None) -> List[List[int]]:
    if options is None:
        options = SolveOptions()
    stats = Stats(start_ts=time.monotonic())
    dom = Domains.full(puzzle.size)

    last_beat = stats.elapsed()
    try:
        propagate_fixpoint(puzzle, dom, stats=stats)
    except PropagationError:
        return dom.snapshot_grid()

    if options.propagate_only:
        if options.trace:
            print(f"{time.strftime('%H:%M:%S')} {stats.elapsed():.2f}s propagate-only done")
        return dom.snapshot_grid()

    def timed_out() -> bool:
        if options.max_seconds is not None and stats.elapsed() >= options.max_seconds:
            return True
        if options.max_nodes is not None and stats.nodes >= options.max_nodes:
            return True
        return False

    def heartbeat_if_needed(current_dom: Domains):
        nonlocal last_beat
        if options.trace and (stats.elapsed() - last_beat) >= options.trace_interval:
            from .debug import heartbeat

            print(heartbeat(stats, current_dom))
            last_beat = stats.elapsed()

    def pick_var(dom: Domains) -> Optional[Cell]:
        # MRV
        best: Optional[Tuple[int, Cell]] = None
        for cell, s in dom.dom.items():
            if len(s) <= 1:
                continue
            key = (len(s), cell)
            if best is None or key < best:
                best = key
        return None if best is None else best[1]

    def lcv_order(cell: Cell) -> List[int]:
        vals = list(dom.dom[cell])
        # naive LCV: sort by value count of conflicts in peers
        peers = set()
        r, c = cell
        # compute peers inline to avoid import cycle
        for cc in range(1, puzzle.size + 1):
            if cc != c:
                peers.add((r, cc))
        for rr in range(1, puzzle.size + 1):
            if rr != r:
                peers.add((rr, c))
        br = (r - 1) // 3
        bc = (c - 1) // 3
        for i in range(1, 4):
            for j in range(1, 4):
                rr = 3 * br + i
                cc = 3 * bc + j
                if rr == r and cc == c:
                    continue
                peers.add((rr, cc))
        def conflict_score(v: int) -> int:
            score = 0
            for p in peers:
                if v in dom.dom[p]:
                    score += 1
            return score
        vals.sort(key=conflict_score)
        return vals

    # track best partial (most assigned cells)
    best: Tuple[int, Domains] = (sum(1 for s in dom.dom.values() if len(s) == 1), dom.copy())

    def maybe_update_best(d: Domains) -> None:
        nonlocal best
        cnt = sum(1 for s in d.dom.values() if len(s) == 1)
        if cnt > best[0]:
            best = (cnt, d.copy())

    def search(dom: Domains) -> Optional[Domains]:
        if timed_out():
            return None
        # Check completion
        done = all(len(s) == 1 for s in dom.dom.values())
        if done:
            return dom
        maybe_update_best(dom)
        cell = pick_var(dom)
        if cell is None:
            return dom
        for v in lcv_order(cell):
            stats.nodes += 1
            new_dom = dom.copy()
            new_dom.assign(cell, v)
            stats.assignments += 1
            try:
                propagate_fixpoint(puzzle, new_dom, stats=stats)
            except PropagationError:
                heartbeat_if_needed(new_dom)
                continue
            maybe_update_best(new_dom)
            res = search(new_dom)
            if res is not None:
                return res
            heartbeat_if_needed(new_dom)
            if timed_out():
                return None
        return None

    result = search(dom)
    if result is None:
        # return best-so-far partial
        return best[1].snapshot_grid()
    return result.snapshot_grid()
