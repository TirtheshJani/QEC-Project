# 12 — Capstone summary

A one-page recap. If everything else got compressed away, this should still tell the story end-to-end.

## What QEC is for

Quantum hardware is noisy. A real qubit decoheres in microseconds; a real gate fails one time in a hundred. **Quantum error correction** encodes a single *logical* qubit's state across many *physical* qubits in such a way that the encoded state survives errors that would have destroyed an unencoded qubit. The goal is to push the *logical* error rate arbitrarily small using physical qubits whose error rate is below some threshold.

## What we built (and why)

Each phase produced something concrete that builds on the previous:

| # | What | The reason it had to come first |
|---|---|---|
| 0 | Repo + env | so the rest is reproducible |
| 1 | NumPy state-vector simulator (`qec/statevec.py`) | a ground-truth oracle for everything else |
| 2 | Kraus channels + density-matrix tools (`qec/channels.py`) | needed before "noise" means anything precise |
| 3 | Pauli class + AG tableau simulator (`qec/pauli.py`, `qec/stabilizer.py`) | the formalism every QEC code is written in |
| 4 | 3-qubit repetition code (`qec/codes/repetition.py`) | the smallest non-trivial code; classical-coding analogue |
| 5 | Shor [[9,1,3]] + Steane [[7,1,3]] (`qec/codes/shor.py`, `steane.py`) | the first true QEC codes, distance 3 |
| 6 | CSS construction + Knill–Laflamme (`notes/09`, `demos/07`) | the rigorous correctness gate |
| 7 | Fault tolerance basics (`notes/10`) | why we need codes that don't break their own promises |
| 8 | Surface code intro (`qec/codes/surface.py`, `notes/11`, `demos/08`) | the leading practical candidate |

## The key insights

1. **Encoding via entanglement, not copies.** No-cloning forbids `|psi> -> |psi>^{⊗3}`. Encoding works by entangling with ancillas (`|0_L> = |000>, |1_L> = |111>`), so `alpha|0_L> + beta|1_L> = alpha|000> + beta|111>` is a 1-dim subspace of a 3-dim Hilbert space.

2. **Reading errors via stabilizers, not data.** Measuring data destroys superpositions. Stabilizers are operators that have eigenvalue `+1` on the codespace; measuring them tells you about *errors* without revealing logical information.

3. **Error discretization.** Continuous quantum errors don't ruin QEC: any single-qubit error decomposes into `I, X, Y, Z`, and a code that corrects this discrete set automatically corrects every linear combination. This is why we can build finite syndrome tables at all.

4. **The stabilizer formalism reduces QEC to bit arithmetic.** A Pauli is two bits per qubit (x, z) plus a phase; multiplication is XOR; commutation is a single bit (the symplectic inner product). Every code's encoder, syndrome, and decoder reduce to GF(2) linear algebra.

5. **CSS = classical decoding, twice.** The X- and Z-side decoders are independent classical decoders. Steane is literally the [7,4] Hamming code applied on both sides.

6. **Distance 3 corrects 1 error; threshold theorem extends this to "correct everything".** Concatenated distance-3 codes with fault-tolerant syndrome extraction drive `P_L → 0` doubly exponentially below threshold.

7. **Surface code wins on locality + threshold.** All stabilizers are 4-local on a 2D grid; threshold ≈ 1% under realistic circuit-level noise. Logical error rate scales as `(p / p_th)^{(d+1)/2}`.

## The numbers we trust

From the demos and tests:
- Repetition code: `P_L = 3 p^2 - 2 p^3` exactly, verified by Monte Carlo to 4σ at 50k shots.
- Shor + Steane: every one of the 27 (Shor) / 21 (Steane) weight-1 Pauli errors corrected to identity. `P_L ∝ p^2` log-log slope ~ 2.
- Tableau simulator agrees with state-vector simulator to 1e-10 (up to global phase) on random 60-gate Clifford circuits, and runs 50k Clifford gates on 50 qubits in seconds.
- KL conditions hold to 1e-10 for every pair of weight-1 Pauli errors on Steane.
- Surface code at d=3 and d=5: `d^2` data qubits, `d^2 - 1` stabilizers (auto-derived logicals of weight `d`).

## What we deliberately skipped

The project was scoped theory-first, with small demos. We skipped:

- A real fault-tolerant syndrome-extraction circuit (Shor- or Steane-style ancillas).
- Magic state distillation.
- An MWPM decoder for the surface code (PyMatching).
- A real circuit-level threshold plot (Stim).
- Running anything on real hardware.

Each of these is a substantial follow-up project on its own and is parked under "out of scope" in the original plan. The conceptual foundation here should make any of them tractable to pick up later.

## How to use this repo as a reference

Six months from now:

- **"How does the X stabilizer commute with Y?"** → `qec/pauli.py::Pauli.commutes_with` plus `notes/05`.
- **"Show me the Steane decoder."** → `qec/codes/steane.py::correct` plus `notes/08`.
- **"What's the analytic bit-flip-code logical error rate?"** → `notes/06::"Logical error rate vs physical"` plus `qec/codes/repetition.py::analytic_logical_error_rate`.
- **"Is my Pauli implementation correct?"** → run `pytest`.

The notes are designed to be readable cold; the code has a `tests/` directory that can be run as documentation in itself. Either way, the answer should be a single file lookup.
