from __future__ import annotations

import itertools
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .constraints import all_units, peers_of, pointer_line_cells
from .debug import Stats
from .model import Cage, Cell, Domains, Puzzle


class PropagationError(Exception):
    pass


def basic_eliminate(puzzle: Puzzle, dom: Domains) -> int:
    size = puzzle.size
    removed = 0
    # Eliminate peers of singletons
    singles = [(cell, next(iter(vals))) for cell, vals in dom.dom.items() if len(vals) == 1]
    for cell, v in singles:
        for peer in peers_of(size, cell):
            if v in dom.dom[peer]:
                dom.dom[peer].remove(v)
                removed += 1
                if len(dom.dom[peer]) == 0:
                    raise PropagationError(f"Domain wipeout at {peer}")
    return removed


def hidden_singles(puzzle: Puzzle, dom: Domains, stats: Optional[Stats] = None) -> int:
    changed = 0
    for unit in all_units(puzzle.size):
        # Map digit -> cells that can take it
        locations: Dict[int, List[Cell]] = {d: [] for d in range(1, puzzle.size + 1)}
        for cell in unit:
            for v in dom.dom[cell]:
                locations[v].append(cell)
        for v, cells in locations.items():
            if len(cells) == 1:
                cell = cells[0]
                if len(dom.dom[cell]) != 1:
                    dom.assign(cell, v)
                    changed += 1
                    if stats:
                        stats.hidden_single_hits += 1
    if changed:
        # After assigning, eliminate peers
        changed += basic_eliminate(puzzle, dom)
    return changed


def cage_feasible_values(
    puzzle: Puzzle, dom: Domains, cage: Cage
) -> Dict[Cell, Set[int]]:
    # Enumerate feasible tuples given current domains
    cells = cage.cells
    k = len(cells)
    targets = cage.sum
    alldiff = puzzle.rules.cage_all_different

    # Prepare domain lists in fixed order
    dom_lists: List[List[int]] = [sorted(dom.dom[cell]) for cell in cells]

    # Quick bounds check
    min_sum = sum(min(d) for d in dom_lists)
    max_sum = sum(max(d) for d in dom_lists)
    if not (min_sum <= targets <= max_sum):
        # No feasible combination
        return {cell: set() for cell in cells}

    supports: List[Set[int]] = [set() for _ in range(k)]

    def backtrack(i: int, partial_sum: int, used: Set[int], chosen: List[int]):
        if i == k:
            if partial_sum == targets:
                for idx, val in enumerate(chosen):
                    supports[idx].add(val)
            return
        remaining_min = partial_sum + sum(min(d) for d in dom_lists[i:])
        remaining_max = partial_sum + sum(max(d) for d in dom_lists[i:])
        if targets < remaining_min or targets > remaining_max:
            return
        for v in dom_lists[i]:
            if alldiff and v in used:
                continue
            chosen.append(v)
            used_added = False
            if alldiff:
                used.add(v)
                used_added = True
            backtrack(i + 1, partial_sum + v, used, chosen)
            if used_added:
                used.remove(v)
            chosen.pop()

    backtrack(0, 0, set(), [])

    return {cells[i]: supports[i] for i in range(k)}


def prune_cages(puzzle: Puzzle, dom: Domains, stats: Optional[Stats] = None) -> int:
    pruned = 0
    for cage in puzzle.cages:
        feasible = cage_feasible_values(puzzle, dom, cage)
        if stats:
            stats.cage_recomps += 1
        for cell, support in feasible.items():
            if not support:
                # No feasible value for this position under cage constraints
                raise PropagationError(f"Cage infeasible at {cell}")
            before = set(dom.dom[cell])
            dom.dom[cell].intersection_update(support)
            pruned += len(before) - len(dom.dom[cell])
            if len(dom.dom[cell]) == 0:
                raise PropagationError(f"Domain wipeout by cage at {cell}")
    return pruned


def prune_pointers(puzzle: Puzzle, dom: Domains, stats: Optional[Stats] = None) -> int:
    pruned = 0
    for clue in puzzle.border_clues:
        line = pointer_line_cells(puzzle, clue)
        d = clue.digit
        first = line[0]
        # Filter Dom(L[1])
        to_remove: Set[int] = set()
        for n in list(dom.dom[first]):
            if n < 1 or n > puzzle.size:
                to_remove.add(n)
                continue
            target_cell = line[n - 1]
            target_dom = dom.dom[target_cell]
            if d not in target_dom:
                to_remove.add(n)
                continue
            if n == 1 and d != 1:
                to_remove.add(n)
                continue
            if dom.is_singleton(target_cell):
                tv = dom.get_singleton(target_cell)
                if tv is not None and tv != d:
                    to_remove.add(n)
        if to_remove:
            before = len(dom.dom[first])
            dom.dom[first].difference_update(to_remove)
            pruned += before - len(dom.dom[first])
            if stats:
                stats.pointer_fires += 1
            if len(dom.dom[first]) == 0:
                raise PropagationError(f"Pointer wiped L[1] at {first}")
        # If L[1] is singleton {n}, enforce L[n] == d
        if dom.is_singleton(first):
            n = dom.get_singleton(first)
            if n is not None:
                target_cell = line[n - 1]
                if d not in dom.dom[target_cell]:
                    raise PropagationError(
                        f"Pointer contradiction at {clue.side}{clue.index}: L[{n}] cannot be {d}"
                    )
                before = set(dom.dom[target_cell])
                dom.assign(target_cell, d)
                pruned += len(before) - 1
        # Reverse support: if L[k] cannot be d at all, then k cannot be in Dom(L[1])
        for k, cell in enumerate(line, start=1):
            if d not in dom.dom[cell]:
                if k in dom.dom[first]:
                    dom.dom[first].discard(k)
                    pruned += 1
                    if stats:
                        stats.pointer_fires += 1
                    if len(dom.dom[first]) == 0:
                        raise PropagationError(f"Pointer wiped L[1] at {first}")
            # If L[k] is assigned d, force k ∈ Dom(L[1]) and reduce others that contradict
            if dom.is_singleton(cell) and dom.get_singleton(cell) == d:
                # Keep only k in Dom(L[1])
                to_remove2 = {n for n in dom.dom[first] if n != k}
                if to_remove2:
                    dom.dom[first].difference_update(to_remove2)
                    pruned += len(to_remove2)
                    if stats:
                        stats.pointer_fires += 1
                if len(dom.dom[first]) == 0:
                    raise PropagationError(f"Pointer wiped L[1] at {first}")
    return pruned


def propagate_fixpoint(puzzle: Puzzle, dom: Domains, stats: Optional[Stats] = None) -> None:
    while True:
        changed = 0
        changed += basic_eliminate(puzzle, dom)
        changed += hidden_singles(puzzle, dom, stats=stats)
        changed += prune_cages(puzzle, dom, stats=stats)
        changed += prune_pointers(puzzle, dom, stats=stats)
        if stats:
            stats.pruned += changed
        if changed == 0:
            break
