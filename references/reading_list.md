# Reading list

The "background" stack of textbooks, papers, and lecture notes that backs each phase. Add to as needed; don't feel obliged to read everything before starting code.

## Textbooks

- **Nielsen & Chuang, _Quantum Computation and Quantum Information_** — the standard reference. Ch. 2 (linear algebra), Ch. 4 (gates), Ch. 8 (channels), Ch. 10 (QEC).
- **Preskill, _Quantum Information_ Lecture Notes (Ph229)** — http://theory.caltech.edu/~preskill/ph229/. Free, very thorough; Ch. 7 is the QEC + fault tolerance bible.
- **Gottesman, _Stabilizer Codes and Quantum Error Correction_** (PhD thesis, 1997) — https://arxiv.org/abs/quant-ph/9705052. The original treatment of the stabilizer formalism, still the clearest.

## Lecture notes & courses

- **Qiskit Textbook** — https://qiskit.org/textbook (and the new Qiskit Learning platform). Approachable QC intro with runnable code; QEC chapter is short but useful.
- **Gottesman, _Quantum Error Correction_** (Perimeter Scholars Lectures, 2009) — talks on YouTube; concise overview of stabilizer codes and FT.

## Papers (per phase)

### Phase 3 — stabilizer formalism
- Aaronson & Gottesman, *Improved Simulation of Stabilizer Circuits* (2004), https://arxiv.org/abs/quant-ph/0406196 — the tableau algorithm we'll implement.

### Phase 4 — repetition code
- Standard textbook coverage (N&C §10.1, Preskill Ch. 7).

### Phase 5 — Shor & Steane
- Shor, *Scheme for reducing decoherence in quantum computer memory* (1995), Phys. Rev. A 52, R2493 — the original 9-qubit code.
- Steane, *Multiple-particle interference and quantum error correction* (1996), Proc. R. Soc. A 452, 2551 — the 7-qubit Hamming-derived code.
- Calderbank & Shor, *Good quantum error-correcting codes exist* (1996), https://arxiv.org/abs/quant-ph/9512032 — the CSS construction.

### Phase 7 — fault tolerance
- Aliferis, Gottesman, Preskill, *Quantum accuracy threshold for concatenated distance-3 codes* (2006), https://arxiv.org/abs/quant-ph/0504218 — rigorous threshold theorem.
- Eastin & Knill, *Restrictions on transversal encoded quantum gate sets* (2009), https://arxiv.org/abs/0811.4262.

### Phase 8 — surface code
- Kitaev, *Fault-tolerant quantum computation by anyons* (2003), https://arxiv.org/abs/quant-ph/9707021 — the toric code.
- Dennis, Kitaev, Landahl, Preskill, *Topological quantum memory* (2002), https://arxiv.org/abs/quant-ph/0110143.
- Fowler, Mariantoni, Martinis, Cleland, *Surface codes: Towards practical large-scale quantum computation* (2012), https://arxiv.org/abs/1208.0928 — the practical-engineering reference.

## Tools / docs

- **Qiskit** — https://docs.quantum.ibm.com/api/qiskit
- **Qiskit Aer** — https://qiskit.github.io/qiskit-aer/
- **Stim** (Gidney) — https://github.com/quantumlib/Stim — out-of-scope here, but the standard for serious surface-code research.
- **PyMatching** — https://pymatching.readthedocs.io — MWPM decoder; potential follow-on once Phase 8 is done.

## Updating

When a phase's notes cite a specific paper, add it under the corresponding section above so this file stays the single source of truth for "what should I read".
