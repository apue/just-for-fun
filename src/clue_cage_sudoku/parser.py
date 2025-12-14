from __future__ import annotations

import json
from typing import Any, Dict

from .model import BorderClue, Cage, Puzzle, Rules


def load_puzzle(path: str) -> Puzzle:
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)

    size = int(data["size"])  # 9
    rules = data.get("rules", {})
    rules_obj = Rules(
        sudoku=bool(rules.get("sudoku", True)),
        cage_sum=bool(rules.get("cage_sum", True)),
        cage_all_different=bool(rules.get("cage_all_different", False)),
        numbered_rooms=bool(rules.get("numbered_rooms", True)),
    )

    clues = [
        BorderClue(side=c["side"], index=int(c["index"]), digit=int(c["digit"]))
        for c in data.get("border_clues", [])
    ]

    cages = []
    for cg in data.get("cages", []):
        cells = [(int(r), int(c)) for r, c in cg["cells"]]
        cages.append(Cage(sum=int(cg["sum"]), cells=cells))

    return Puzzle(size=size, rules=rules_obj, border_clues=clues, cages=cages)

