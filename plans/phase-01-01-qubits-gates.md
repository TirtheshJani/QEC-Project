# Plan: Phase 1.1 — Qubits, single-qubit gates, Bloch sphere

Authored: 2026-05-14. Methodology: Superpowers `writing-plans` (in spirit;
plugin not yet installed). Followed by `test-driven-development` for any
code promoted into `src/qec_project/`.

## Goal

Deliver the first Phase 1 content notebook,
`phase-01-quantum-basics/01-qubits-gates/qubits_gates.ipynb`, covering
exactly Phase 1 README learning goal 1: qubits as unit vectors in C^2,
the Bloch sphere parametrisation, the single-qubit Clifford gates
(`H, S, X, Y, Z`), and the identity `H Z H = X` verified both
algebraically (markdown) and numerically. The notebook runs top-to-bottom
with seeds set and produces a single matplotlib Bloch-sphere figure
(wireframe + scatter, no qutip). All Pauli definitions are pulled from
`qec_project.linalg` rather than redefined.

## Scope

### In scope

- The single-qubit state space C^2: column-vector representations of
  `|0>, |1>, |+>, |->, |+i>, |-i>` with explicit `complex128` dtype.
- Global vs relative phase. Show that `e^{i theta} |psi>` and `|psi>`
  produce identical measurement statistics in any basis (global phase
  unphysical), but `(|0> + e^{i phi} |1>) / sqrt(2)` for `phi in
  {0, pi/2, pi}` produces distinguishable X-basis statistics
  (relative phase physical).
- Bloch sphere parametrisation
  `|psi> = cos(theta/2) |0> + e^{i phi} sin(theta/2) |1>`. Compute the
  Bloch vector `(<X>, <Y>, <Z>)` for the six cardinal states and plot
  them on a wireframe sphere with labels.
- Single-qubit Clifford gates `H, S, X, Y, Z` (matrices defined or
  imported from `qec_project.linalg.PAULIS`). Show their unitarity via
  `is_unitary` from `qec_project.linalg`.
- `H Z H = X` by hand in markdown (one paragraph of `2x2` matrix
  multiplication) plus a numerical check using `np.allclose`.
- Action on Bloch sphere: a small table showing where `H, S, X` send
  each cardinal state.

### Out of scope (deferred)

- Multi-qubit gates -> Phase 1.2.
- Mixed states / density matrices / channels -> Phase 1.3.
- Stabilizer formalism, codes -> Phase 2+.
- Hardware-specific gates (sqrt(X), Rzx, etc.) and arbitrary rotations.
- Any 3D rotation animation (a static scatter + wireframe is enough).

## File-by-file changes

| Path | Action | Notes |
| ---- | ------ | ----- |
| `plans/phase-01-01-qubits-gates.md` | create | this plan |
| `phase-01-quantum-basics/01-qubits-gates/qubits_gates.ipynb` | create | the notebook |
| `phase-01-quantum-basics/01-qubits-gates/_build_notebook.py` | create | nbformat builder (matches Phase 0 pattern) |
| `phase-01-quantum-basics/01-qubits-gates/README.md` | create | one-pager |

No `src/qec_project/` changes for this sub-deliverable; Pauli matrices
and the unitarity check live in `qec_project.linalg` already (Phase 0.1).

### Promoted helpers — justification

None. Single-qubit Cliffords are reused so often that they will live as
constants in the eventual `qec_project.codes` package, but this notebook
is pedagogical; promoting `H`, `S` here would be premature when the
Phase 2 stabilizer module will own them anyway. Define them inline.

## Tests added

None new for this sub-deliverable. `qec_project.linalg` already has its
tests (Phase 0.1, `tests/test_linalg.py`). The numerical `H Z H = X`
check inside the notebook is a self-test; if it fails, the notebook
fails.

## Acceptance criteria

- `python -m uv run pytest` continues to return 0 (no new tests added).
- `python -m uv run ruff check .` returns 0 findings.
- `python -m uv run jupyter nbconvert --to notebook --execute
  phase-01-quantum-basics/01-qubits-gates/qubits_gates.ipynb --output
  _check.ipynb` runs to completion.
- Notebook sets `np.random.default_rng(0)` in its first code cell.
- Notebook contains: a global-vs-relative phase code cell, a Bloch-sphere
  figure with six cardinal states labelled, a single-qubit Clifford gate
  matrix block, the `H Z H = X` algebraic + numerical verification.

## Tasks (2-5 minute units, ordered)

1. Scaffold `_build_notebook.py` with headings + empty code cells.
2. Fill in the state definitions and the global-vs-relative phase
   discussion.
3. Add the Bloch sphere section: helper function `bloch_vector(psi)`
   inline, scatter + wireframe matplotlib figure.
4. Add the Clifford gate section: define `H, S`, import Paulis, table
   showing where they send cardinal states.
5. Add the `H Z H = X` block: markdown derivation, then a numerical
   check with `np.allclose`.
6. Run `python phase-01-quantum-basics/01-qubits-gates/_build_notebook.py`
   to emit the .ipynb.
7. Execute the notebook end-to-end via `nbconvert --execute`. Iterate
   until clean.
8. Write the sub-deliverable README.

## Out-of-band notes

- `qiskit` is not strictly needed in this notebook (Phase 1.1 is
  state-vector arithmetic). Defer the first Qiskit usage to Phase 1.2.
- The Bloch-sphere figure is static; no animation, no qutip dependency.
