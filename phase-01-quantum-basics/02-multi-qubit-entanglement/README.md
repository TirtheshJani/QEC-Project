# Phase 1.2 — Multi-qubit states, Bell states, superdense coding, teleportation

The second Phase 1 notebook. Brings Qiskit into the curriculum and
exercises the two famous two-qubit protocols. The basis-ordering note
from Phase 0.1 (`numpy.kron` is big-endian) collides head-on with
Qiskit's little-endian convention here; the reconciliation is spelled
out explicitly.

## What it covers

1. Multi-qubit state vectors and the basis-ordering conventions of
   `numpy.kron` (big-endian) vs Qiskit (little-endian). Reconciled by
   reversing the index ordering when comparing Qiskit `Statevector`
   objects to hand-computed states.
2. The four Bell states `|Phi+/->`, `|Psi+/->` built two ways (by hand
   with `qec_project.linalg.tensor`, then in Qiskit). Statevector
   cross-check passes for all four.
3. Superdense coding: 2 classical bits over 1 qubit + a shared Bell
   pair, implemented in Qiskit and run on `qiskit_aer.AerSimulator`
   with 1000 shots per message. All four 2-bit messages decode with
   100% confidence.
4. Standard 3-qubit teleportation with classical feed-forward via
   `with circuit.if_test`. Prepare a random one-qubit state, teleport
   it, partial-trace down to Bob's qubit, and verify fidelity 1.0.

The notebook reuses `qec_project.linalg.tensor` and `PAULIS` from Phase
0.1. No new helpers were promoted in this sub-deliverable: the Phase 2
stabilizer machinery will subsume the by-hand Bell-state construction.

## How to run

From the repo root:

```bash
uv sync --extra dev
uv run jupyter lab phase-01-quantum-basics/02-multi-qubit-entanglement/multi_qubit.ipynb
```

Or non-interactively:

```bash
uv run jupyter nbconvert --to notebook --execute \
    phase-01-quantum-basics/02-multi-qubit-entanglement/multi_qubit.ipynb \
    --output _check.ipynb
```

A fixed seed (`np.random.default_rng(0)`) is set in the first code
cell; the AerSimulator is seeded with `seed_simulator=0`; the random
one-qubit state is generated with `random_statevector(2, seed=7)`. The
notebook is deterministic across runs.

`_build_notebook.py` is the source from which the notebook is
generated. Edit it (not the `.ipynb`) when the structure needs to
change, then re-run it.

## After reading this you should be able to

- State whether `numpy.kron` or Qiskit's `Statevector` is big-endian or
  little-endian, and convert between them.
- Construct any of the four Bell states two ways (by hand and via a
  Qiskit circuit) and verify the result.
- Implement superdense coding and predict which classical bit lands on
  Alice's measurement vs Bob's.
- Implement teleportation with classical feed-forward via `if_test`,
  and explain why no qubit was physically transferred.

## References

In `docs/reading-list.md`:

- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  sections 1.3 (multi-qubit states), 1.3.7 (superdense coding), 1.3.6
  (teleportation), 4.4 (universality of CNOT + single-qubit gates).
