# Phase 2.1 - 3-qubit repetition code

**Sub-task duration:** 1 day. **Prereq:** Phase 1 (density matrices, channels).

The first real QEC code. It is too weak to be useful - it cannot correct
phase errors - but the encoding, stabilizer measurement, decoding-by-syndrome
loop are the universal template you will reuse for Shor 9 (Phase 2.2), Steane
(Phase 2.4), and the surface code (Phase 3).

## Goals

1. Define the [[3, 1, 1]] bit-flip code: encoding, stabilizers `Z_1 Z_2`
   and `Z_2 Z_3`, logical operators `X_L = XXX`, `Z_L = ZZZ`.
2. Apply single-qubit depolarizing noise to each physical qubit
   independently in the density-matrix picture.
3. Extract the two-bit syndrome by sampling from the Z-basis diagonal of
   the noisy state. Foreshadow that Phase 2.2 replaces this with an
   ancilla circuit in Qiskit.
4. Apply the maximum-likelihood single-qubit X recovery.
5. Sweep physical error rate p, plot logical error rate vs p alongside
   the uncoded baseline and the exact curves, and show that under
   depolarizing noise the code is worse than an uncoded qubit at every
   0 < p < 1: it corrects X errors but triples the exposure to Z errors.

## Deliverables

- `three_qubit_repetition.ipynb` - generated from `_build_notebook.py`.
- `src/qec_project/codes/repetition3.py` - `ThreeQubitBitFlipCode` class
  (reused by Phase 2.2 Shor 9).
- `src/qec_project/noise/quantum.py` - Pauli matrices and Kraus channels
  (reused throughout Phase 2).
- `tests/test_quantum_noise.py`, `tests/test_repetition3.py`.

## What this code does NOT correct

Phase errors. A single Z on any one of the three qubits commutes with both
stabilizers (because the stabilizers are products of Z's), so the syndrome
is `(0, 0)` - indistinguishable from "no error". `Z_L` flips the logical
phase and is undetectable. The phase-flip code is the same construction in
the Hadamard-rotated basis (encoding `|+> -> |+++>`, `|-> -> |--->`,
stabilizers `X_1 X_2` and `X_2 X_3`). Shor 9 (Phase 2.2) concatenates the
two and corrects every single-qubit Pauli error.

## References

- Nielsen and Chuang, *Quantum Computation and Quantum Information* 10th
  anniversary ed., Ch. 10.1.
- Gottesman, *Stabilizer Codes and Quantum Error Correction* (PhD thesis),
  arXiv:quant-ph/9705052, Ch. 3.

## Workflow hints

- Superpowers `test-driven-development` was applied: tests for every public
  method in `repetition3.py` were written first.
- Re-run the notebook from the builder rather than editing it in-place:
  `python phase-02-qec-fundamentals/01-3qubit-repetition/_build_notebook.py`.
- All numerical comparisons use seeded RNGs; the plot is reproducible from
  `seed=42`.
