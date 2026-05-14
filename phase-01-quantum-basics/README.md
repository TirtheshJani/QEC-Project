# Phase 1 — Quantum computing basics

**Duration:** ~3 weeks. **Prereq:** Phase 0 complete.

The goal is fluency, not breadth. By the end of this phase you can read any
QEC paper's circuit notation without lookup.

## Learning goals

1. Qubits, single-qubit gates, the Bloch sphere. Why a global phase is
   physical garbage but a relative phase isn't.
2. Multi-qubit states. Tensor products, entanglement, Bell states,
   superdense coding, teleportation.
3. Density matrices and mixed states. Kraus operators. The bit-flip,
   phase-flip, and depolarizing channels as Kraus sets.
4. Qiskit as a tool, not a religion: build, transpile, sample, measure.

## Deliverables

- [ ] `01-qubits-gates/`: Bloch-sphere visualization of all single-qubit
      Cliffords; verify $HZH = X$ both algebraically and numerically.
- [ ] `02-multi-qubit-entanglement/`: Bell-state preparation circuit;
      teleportation; superdense coding. All three in Qiskit + Aer.
- [ ] `03-density-matrices-noise/`: implement the three single-qubit noise
      channels as Kraus operators; sanity-check trace preservation.
- [ ] All notebooks runnable from `uv run jupyter lab`.
- [ ] Phase entry in `CHANGELOG.md`.

## Workflow hints

- For confusing concepts (mixed states, partial trace), reach for ARS
  `/ars-socratic` before plowing through textbook pages.
- `/ars-fact-check` any non-obvious algebraic identity before promoting it
  into `src/qec_project/`.

## References

- Nielsen & Chuang, Chs. 1–2, 4, and §8.3 (operator-sum representation).
- IBM Qiskit textbook (free), Chs. 0–2.
- Mike Nielsen's "Quantum Computing for the Determined" YouTube playlist.
