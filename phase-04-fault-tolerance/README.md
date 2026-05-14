# Phase 4 — Fault tolerance

**Duration:** ~3 weeks. **Prereq:** Phase 3.

Error correction by itself is not enough — the gates and measurements that
extract syndromes must also be FT. This phase covers what the NRC call
specifically calls "efficient fault-tolerant logical operations".

## Learning goals

1. Fault-tolerant syndrome extraction: Shor / Steane / Knill schemes. Flag
   qubits and why they exist.
2. Transversal gates: which Clifford gates are transversal on Steane and
   the surface code; why a transversal universal gate set is forbidden
   (Eastin–Knill).
3. **Magic state distillation** as the standard workaround. Implement the
   15-to-1 protocol and measure the output fidelity.
4. Lattice surgery on the surface code: merge / split for logical CNOT.
   Counting qubit-cycles for a useful FT operation.

## Deliverables

- [ ] `01-ft-syndrome-extraction/`: simulate Steane-method extraction with
      a flag qubit; verify error propagation stays bounded.
- [ ] `02-magic-state-distillation/`: 15-to-1 distillation; plot output
      infidelity vs input infidelity.
- [ ] `03-lattice-surgery/`: schematic + Stim circuit for a logical CNOT
      via merge/split.
- [ ] Phase entry in `CHANGELOG.md`. ~10 references in
      `docs/reading-list.md`.

## Workflow hints

- Pressure-test any overhead estimate with the `devils_advocate_agent`
  (cribbed from ARS) — distillation overhead is the single most-fudged
  number in the QEC literature.
- Use `/ars-fact-check` for every numerical claim about overhead /
  thresholds you copy from a paper.

## References

- Bryan Eastin, Emanuel Knill, *Restrictions on Transversal Encoded
  Quantum Gate Sets.* Phys. Rev. Lett. 102, 110502 (2009). arXiv:0811.4262.
- Sergey Bravyi, Alexei Kitaev, *Universal Quantum Computation with Ideal
  Clifford Gates and Noisy Ancillas.* Phys. Rev. A 71, 022316 (2005).
  arXiv:quant-ph/0403025.
- Clare Horsman, Austin G. Fowler, Simon Devitt, Rodney Van Meter,
  *Surface code quantum computing by lattice surgery.* New J. Phys. 14,
  123011 (2012). arXiv:1111.4022.
