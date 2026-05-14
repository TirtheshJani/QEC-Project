# Phase 1.1 — Qubits, single-qubit gates, Bloch sphere

The first content notebook of Phase 1. Builds the single-qubit fluency
that every QEC paper assumes: state vectors in `C^2`, the Bloch sphere,
the single-qubit Clifford gates, and the `H Z H = X` identity that we
rely on every time a basis-changing Hadamard sits before a Z-basis
measurement.

## What it covers

1. The single-qubit state space `C^2` and the six cardinal states
   `|0>, |1>, |+>, |->, |+i>, |-i>`.
2. Global vs relative phase: a numerical demonstration that
   `e^{i theta} |psi>` is observationally identical to `|psi>` in every
   basis, while different relative phases give wildly different X-basis
   statistics.
3. The Bloch sphere: cardinal states plotted on a wireframe sphere
   (matplotlib only, no qutip).
4. The single-qubit Clifford gates `H, S, X, Y, Z`. Unitarity verified
   via `qec_project.linalg.is_unitary`.
5. `H Z H = X` worked through by hand in markdown, then checked
   numerically with `np.allclose`.
6. A small table showing how `H, S, X, Y, Z` permute the six cardinal
   states.

The notebook reuses `qec_project.linalg` from Phase 0.1 for Pauli
matrices and the unitarity check; no new helpers were promoted in this
sub-deliverable.

## How to run

From the repo root:

```bash
uv sync --extra dev
uv run jupyter lab phase-01-quantum-basics/01-qubits-gates/qubits_gates.ipynb
```

Or non-interactively:

```bash
uv run jupyter nbconvert --to notebook --execute \
    phase-01-quantum-basics/01-qubits-gates/qubits_gates.ipynb \
    --output _check.ipynb
```

A fixed seed (`np.random.default_rng(0)`) is set in the first code cell;
the notebook is deterministic across runs.

`_build_notebook.py` in this directory is the source from which the
notebook is generated. Edit it (not the `.ipynb` directly) when the
notebook structure needs to change, then re-run it.

## After reading this you should be able to

- Write any of the six cardinal single-qubit states as a column vector.
- Compute the Bloch vector `(<X>, <Y>, <Z>)` for an arbitrary pure state
  and locate it on the sphere.
- Distinguish a global from a relative phase by listing the
  observable consequences of each.
- Apply `H, S, X, Y, Z` to a state vector and predict where it lands on
  the Bloch sphere.
- Reproduce `H Z H = X` either algebraically or numerically.

## References

In `docs/reading-list.md`:

- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  10th anniversary ed., Cambridge, 2010 — chapter 1 (qubits, Bloch
  sphere) and section 4.1 (single-qubit gates).
