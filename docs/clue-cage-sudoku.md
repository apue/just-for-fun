Numbered Rooms + Killer Cages Sudoku Solver Spec

1. Problem Definition

We solve a 9×9 Sudoku variant with three constraint families:
	1.	Sudoku base rules
Each row, column, and 3×3 box contains digits 1..9 without repetition.
	2.	Numbered Rooms (Pointer) clues on the border
Each border clue applies to one row/column and enforces a pointer constraint.
	3.	Cage (Killer) sum rules
Each dashed cage is a set of cells whose digits sum to a given total.

Indexing
	•	Use 1-based indexing throughout: rows r = 1..9, cols c = 1..9.
	•	A cell is rXcY meaning (row=X, col=Y).

Important note about cages
	•	The user statement only says “sum equals target”.
	•	Do NOT assume cage digits are all-different unless explicitly required.
Implement it as a configuration flag cage_all_different: bool = False (default false).
If turned on, apply AllDifferent within each cage.

⸻

2. Input Data (from user)

2.1 Border clues

Represent each clue as (side, index, d):
	•	side ∈ {"L","R","T","B"} for Left/Right/Top/Bottom
	•	index is row number for L/R clues, column number for T/B clues
	•	d is the clue digit (1..9)

Given clues:

Left side (row clues):
	•	(L, 2, 3)
	•	(L, 4, 5)
	•	(L, 5, 5)
	•	(L, 6, 5)

Top side (column clues):
	•	(T, 2, 3)
	•	(T, 4, 2)
	•	(T, 5, 2)
	•	(T, 6, 2)

Right side (row clues):
	•	(R, 6, 2)
	•	(R, 8, 8)

Bottom side (column clues):
	•	(B, 6, 5)

2.2 Cages

Each cage is (sum_target, cells[]).

Cages provided:
	•	18: [r1c4, r1c5, r1c6]
	•	9:  [r2c2, r2c3, r3c2]
	•	12: [r2c7, r2c8]
	•	17: [r4c1, r5c1, r6c1]
	•	31: [r4c6, r5c6, r6c4, r6c5, r6c6]
	•	15: [r4c8, r4c9, r5c8, r5c9]
	•	12: [r7c2, r8c2]
	•	15: [r8c4, r8c5, r9c4, r9c5]
	•	14: [r8c8, r8c9, r9c8]

No other givens are specified (grid starts empty unless more provided later).

⸻

3. Constraint Formalization

Let decision variables be:
	•	x[r][c] ∈ {1..9} for r,c in 1..9

3.1 Sudoku constraints
	•	For each row r: AllDifferent({ x[r][1..9] })
	•	For each col c: AllDifferent({ x[1..9][c] })
	•	For each box (br, bc) in 0..2:
AllDifferent({ x[3br+i][3bc+j] for i,j in 1..3 })

3.2 Cage sum constraints

For each cage k with target sum S and cell list Ck:
	•	sum( x[cell] for cell in Ck ) == S
	•	If cage_all_different == True: AllDifferent( x[cell] for cell in Ck )

3.3 Numbered Rooms (Pointer) constraint

For each clue (side, index, d):

Define an ordered line L[1..9] of cells starting from the clue side moving inward:
	•	If side == “L” (row = index), order is:
L[1] = x[index][1], L[2]=x[index][2], …, L[9]=x[index][9]
	•	If side == “R” (row = index), order is:
L[1] = x[index][9], L[2]=x[index][8], …, L[9]=x[index][1]
	•	If side == “T” (col = index), order is:
L[1] = x[1][index], L[2]=x[2][index], …, L[9]=x[9][index]
	•	If side == “B” (col = index), order is:
L[1] = x[9][index], L[2]=x[8][index], …, L[9]=x[1][index]

Rule meaning:
	•	Let N = value of the first cell: N = L[1]
	•	Then the clue digit must appear at the N-th position:
L[N] == d

Because this is an “index-by-variable” constraint, implement it via implications:

For each n in 1..9:
	•	(L[1] == n) ⇒ (L[n] == d)

Also note immediate impossibility:
	•	If n==1 then (L[1]==1 ⇒ L[1]==d). That forces d=1 to allow n=1, otherwise n=1 is impossible.

⸻

4. Solver Approach

Use a classic CSP solver:

4.1 Data structures
	•	Maintain for each cell a domain Dom[r][c] ⊆ {1..9} (initially full set).
	•	Maintain constraint objects:
	•	row/col/box AllDifferent
	•	cages (sum and optional AllDifferent)
	•	pointer clues (implication constraints)

4.2 Constraint propagation (must-have pruning)

Run propagation repeatedly until fixpoint:

A) Sudoku elimination
	•	If a cell is assigned value v, remove v from domains of peers in same row/col/box.

B) Cage pruning
For each cage:
	•	Let assigned cells contribute sum_assigned.
	•	Let unassigned cells be U with domains.
	•	Compute feasible combinations for U that can reach target:
	•	Basic bounds pruning:
	•	min_possible = sum(min(Dom[u]) for u in U)
	•	max_possible = sum(max(Dom[u]) for u in U)
	•	Require: sum_assigned + min_possible ≤ S ≤ sum_assigned + max_possible
	•	If violated: contradiction.
	•	Stronger pruning (recommended):
	•	Enumerate all tuples for U consistent with domains (and optionally all-different) whose sum == (S - sum_assigned).
	•	Replace each Dom[u] by the set of values that appear in any feasible tuple at that position.

Because cages sizes here are small (2–5), enumeration is tractable.

C) Pointer clue pruning
For each pointer clue with line L and clue digit d:
	•	Domain filter for the first cell:
	•	For each candidate n in Dom(L[1]):
	•	If d ∉ Dom(L[n]) then remove n from Dom(L[1])
	•	If n == 1 and d != 1 then remove n from Dom(L[1])
	•	If Dom(L[1]) becomes singleton {n}, enforce L[n]=d.
	•	Additionally, if L[n] is assigned ≠ d, then n cannot be in Dom(L[1]).

These simple rules often produce strong pruning without special-case human deductions.

4.3 Search (backtracking)

If propagation stalls and puzzle not solved:
	•	Choose next cell using MRV heuristic (smallest domain size > 1).
	•	Tie-break by highest degree (most constraints: in cage + touched by pointer lines + peers).
	•	Try values in domain (optionally LCV).
	•	Recurse with propagation; backtrack on contradiction.

This approach should be fast for 9×9 even with pointer constraints.

4.4 Optional: use a CP/SAT engine

If implementing from scratch is long, AIDE can model with:
	•	OR-Tools CP-SAT, or Z3
But if using pure Python, the above propagation+MRV is usually enough.

⸻

5. Parsing / Output Requirements

5.1 APIs

Implement at least:
	•	solve(puzzle) -> grid
	•	Returns 9×9 int matrix or dict {(r,c): val}
	•	If multiple solutions, either return one or raise unless uniqueness required.
	•	verify(puzzle, grid) -> (ok: bool, errors: list[str])
	•	Check all three constraint families.
	•	Errors should include details:
	•	row/col/box duplicates
	•	cage sum mismatch (expected vs got, which cage)
	•	pointer clue violation: show side/index/d, computed N, and found L[N]

5.2 Debug output (recommended)
	•	A function to print grid
	•	Optional: print domains of a row/col for debugging
	•	Ability to run with a --trace flag to log propagation steps

⸻

6. Worked Example for Pointer Validation (for verify())

Given a clue (R, 8, 8):
	•	Line is row 8 from right to left:
L[1]=r8c9, L[2]=r8c8, …, L[9]=r8c1
	•	Let N = value at r8c9
	•	Check that value at L[N] equals 8

⸻

7. Provided Puzzle Instance (ready-to-code)
	•	Size: 9×9
	•	Border clues: as listed in 2.1
	•	Cages: as listed in 2.2
	•	No givens (unless added later)
