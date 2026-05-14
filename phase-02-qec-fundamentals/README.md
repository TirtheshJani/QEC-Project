# Phase 2 — QEC fundamentals

**Duration:** ~4 weeks. **Prereq:** Phases 0–1.

The phase where you stop being a quantum-curious person and start being a QEC
person. By the end you can read Gottesman's thesis and most stabilizer-code
papers.

## Learning goals

1. The 3-qubit repetition codes (bit-flip and phase-flip). Syndrome
   measurement without measuring the data qubits.
2. Concatenation intuition via Shor's 9-qubit code.
3. The **stabilizer formalism**: Pauli group, normalizer, stabilizer states,
   Gottesman–Knill. This is *the* abstraction QEC sits on.
4. CSS construction. Steane $[[7,1,3]]$ code: stabilizers, logical
   operators, distance proof.
5. Knill–Laflamme conditions — what makes a code "correct $t$ errors"
   precisely.
6. **Stim** as your everyday tool: build a stabilizer circuit programmatically,
   sample shots, generate a detector-error-model (DEM).

## Deliverables

- [ ] `01-3qubit-repetition/`: bit-flip code simulation under depolarizing
      noise; logical-error vs physical-error plot.
- [ ] `02-shor-9/`: build it in Qiskit; verify it corrects any single-qubit
      error.
- [ ] `03-stabilizer-formalism/`: implement Pauli-group multiplication and
      commutation checking in `src/qec_project/codes/pauli.py` (with tests).
- [ ] `04-css-and-steane/`: construct Steane explicitly; verify K-L
      conditions numerically.
- [ ] `05-intro-to-stim/`: rewrite the Steane code as a `stim.Circuit`;
      sample 100k shots; produce the DEM.
- [ ] Phase entry in `CHANGELOG.md`. Add 8–12 references to
      `docs/reading-list.md`.

## Workflow hints

- The first piece of `src/qec_project/codes/` code lives here. Apply
  Superpowers `writing-plans` + `test-driven-development` rigorously — you
  will be reusing this Pauli code for years.
- Every claim you write down ("the Steane code has distance 3 because…")
  passes through `/ars-fact-check` before it ships to a notebook conclusion
  cell.

## References

- Daniel Gottesman, *Stabilizer Codes and Quantum Error Correction* (PhD
  thesis, 1997). arXiv:quant-ph/9705052.
- Nielsen & Chuang, Ch. 10.
- Craig Gidney, *Stim: a fast stabilizer circuit simulator.* Quantum 5, 497
  (2021). arXiv:2103.02202. — read the Stim docs alongside this.
