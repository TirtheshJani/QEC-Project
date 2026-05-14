# Phase 2.2 — Shor [[9,1,3]] code

Build Peter Shor's 9-qubit code in Qiskit, view it as concatenation of the
3-qubit phase-flip code (on block representatives 0, 3, 6) with the 3-qubit
bit-flip code (in each of three blocks {0,1,2}, {3,4,5}, {6,7,8}), list its
8 stabilizers and the two logical operators, and verify by exhaustive
`Statevector` simulation that every single-qubit Pauli error (X, Y, or Z on
any of the 9 qubits) is corrected by syndrome lookup + recovery up to
global phase.

## Goals

1. **Encoding circuit.** ``CX(0,3)``, ``CX(0,6)``, ``H`` on each of 0/3/6,
   then ``CX(0,1)``, ``CX(0,2)``, ``CX(3,4)``, ``CX(3,5)``, ``CX(6,7)``,
   ``CX(6,8)``. Verified against the algebraic
   ``((|000> +/- |111>)/sqrt(2))^{otimes 3}`` form.
2. **Stabilizers.** 6 inner ``Z_i Z_{i+1}`` checks + 2 six-qubit outer
   ``X``-checks. Each verified as a +1 eigenvalue of ``|0_L>`` and
   ``|1_L>``.
3. **Logical operators.** Canonical minimum-weight reps
   ``X_L = Z_0 Z_3 Z_6`` and ``Z_L = X_0 X_1 X_2`` (the swap reflects the
   outer code being phase-flip, not bit-flip).
4. **27-error exhaustive correction.** All single-qubit X / Y / Z on each
   of 9 qubits, on both ``|0_L>`` and ``|1_L>``, restored to
   ``|<encoded | restored>| > 1 - 1e-9``.
5. **Distance 3.** Both logical reps have weight 3; no weight-1 or
   weight-2 logical exists; ``t = floor((d-1)/2) = 1``.

## Deliverables

| Path | Purpose |
| --- | --- |
| `shor_nine.ipynb` | Teaching notebook. |
| `_build_notebook.py` | One-shot generator (idempotent; re-run to regenerate). |
| `../../src/qec_project/codes/shor9.py` | `Shor9Code` (`encode_circuit`, `stabilizers`, `logical_operators`, `syndrome_of`, `recovery`) + module-level `pauli_commute`, `pauli_string_to_matrix`. |
| `../../tests/test_shor9.py` | 26 tests including hypothesis property test on arbitrary logical superpositions. |

## Hints

* **Engineering workflow.** Superpowers `writing-plans` -> `executing-plans`.
  Plan in `plans/phase-02-02-shor-9.md`.
* **Basis ordering.** ``numpy.kron`` is big-endian (Phase 0.1
  convention); Qiskit ``Statevector`` is little-endian. The notebook
  reverses Qiskit output via ``qiskit_to_bigendian`` before comparing to
  hand-built tensors.
* **Syndrome via expectation value.** No ancilla circuits in this
  notebook; syndromes are read off the encoded state algebraically via
  ``<psi | S | psi>``. Ancilla-based fault-tolerant extraction is Phase 4
  material.

## References

- Peter W. Shor, *Scheme for reducing decoherence in quantum computer
  memory*, Phys. Rev. A 52, R2493 (1995). doi:10.1103/PhysRevA.52.R2493.
- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  section 10.2.
