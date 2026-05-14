# Phase 0 — Foundations

**Duration:** ~3 weeks @ 20+ hrs/week.

You are a true beginner. Before any qubits, build the math + classical-EC
muscles every QEC paper assumes you already have. Every notebook here is a
prerequisite for everything that follows — do not skip.

## Learning goals

1. Read and write linear algebra on finite-dimensional complex vector spaces
   without slowing down: vectors, matrices, eigendecomposition, **tensor
   products** (the operation that lets us write multi-qubit states).
2. Be fluent with discrete probability and the language of channels: random
   variables, conditional probability, Markov chains, mutual information.
3. Understand classical error correction end-to-end: repetition codes, parity,
   the Hamming(7,4) code, linear codes as parity-check / generator matrices,
   syndrome decoding. This is the literal scaffold QEC stabilizer formalism
   sits on top of.

## Deliverables

- [ ] `01-linear-algebra/` notebook: tensor products by hand; numerical check
      via `numpy.kron`. Eigendecomposition of Pauli matrices.
- [ ] `02-probability/` notebook: discrete channel capacity for the binary
      symmetric channel; simulate it.
- [ ] `03-classical-ec/` notebook: implement Hamming(7,4) encoder + syndrome
      decoder from scratch; simulate over a binary symmetric channel and plot
      the logical error curve. The same plot shape returns in Phase 3 for the
      surface code — recognizing it then is the point of doing it now.
- [ ] All notebooks rerun cleanly with seeds set.
- [ ] Phase entry in `CHANGELOG.md` `## Completed milestones`.

## Workflow hints

- **Stuck on the math?** Invoke ARS `/ars-socratic` — it produces a guided
  explanation instead of an answer.
- **Promoting code from notebook → `src/qec_project/`?** Use Superpowers'
  `test-driven-development` skill. Write the test first.

## References

Seed entries — extend in `docs/reading-list.md` as you read.

- Nielsen & Chuang, *Quantum Computation and Quantum Information*, Ch. 2
  (linear algebra) and §10.1 (classical error correction).
- MacKay, *Information Theory, Inference, and Learning Algorithms* (free PDF),
  Chs. 1–2.
- 3Blue1Brown's "Essence of Linear Algebra" YouTube series, for intuition.
