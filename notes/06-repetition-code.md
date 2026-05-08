# 06 — The 3-qubit repetition code

The "hello world" of QEC. It is *not* a proper distance-3 quantum code — it cannot correct an arbitrary single-qubit error — but it is the smallest possible non-trivial example, and it makes every concept (encoder, stabilizers, syndrome, recovery, logical error rate) concrete on three qubits.

The two variants — **bit-flip** and **phase-flip** — are essentially the same code in different bases. Concatenating them gives Shor's [[9,1,3]] code (Phase 5).

## The classical idea, why it doesn't quite carry over, and what does

Classical 3-bit repetition: send `0 -> 000`, `1 -> 111`. The receiver majority-votes; this corrects any single bit-flip.

Quantum problem: you can't *copy* a qubit (no-cloning), so encoding `alpha|0> + beta|1>` as `(alpha|0> + beta|1>)^{⊗3}` is forbidden. What you can do is **entangle**:
```
|0_L> = |000>,
|1_L> = |111>,
alpha|0_L> + beta|1_L> = alpha|000> + beta|111>.
```
This is a 1-dimensional encoding of a 1-dim logical qubit into a 3-qubit state space. The encoder is `CNOT(0->1); CNOT(0->2)` applied to `(alpha|0> + beta|1>) ⊗ |00>`.

Quantum problem 2: you can't *measure* the qubits to majority-vote, because that destroys the superposition. What you can do is measure **stabilizers**:
```
S_1 = Z_0 Z_1,    S_2 = Z_1 Z_2.
```
Both have eigenvalue `+1` on the codespace `span{|000>, |111>}`. Measuring them tells you parities, not bit values, so the encoded superposition survives.

## Stabilizers and the syndrome

The 3-qubit repetition code is the [[3,1,1]] stabilizer code with generators `Z_0 Z_1` and `Z_1 Z_2`. (Distance 1 against arbitrary Pauli noise — a single `Z` is undetected. Distance 3 against pure X noise.)

When an X error hits qubit `q`, it anticommutes with any stabilizer that has `Z_q` and commutes with the rest. The syndrome bits flip accordingly:

| X pattern | `Z_0 Z_1` | `Z_1 Z_2` | syndrome (s_0, s_1) |
|---|---|---|---|
| no error | `+1` | `+1` | (0, 0) |
| `X_0`    | `-1` | `+1` | (1, 0) |
| `X_1`    | `-1` | `-1` | (1, 1) |
| `X_2`    | `+1` | `-1` | (0, 1) |
| `X_0 X_1 X_2` (= logical X) | `+1` | `+1` | (0, 0) |

**Three weight-1 errors → three distinct non-zero syndromes.** That's exactly the meaning of "this code corrects a single X error". The fourth row says: a weight-3 error looks identical to no error — it has been mapped to a logical X, undetectably.

## Decoding: minimum-weight recovery

The syndrome table is the lookup decoder. It pairs each non-zero syndrome with the smallest-weight Pauli that produces it: a single X on the unique qubit that flips both syndrome bits as observed.

This decoder fails when the actual error is weight ≥ 2: e.g. `X_0 X_1` produces syndrome `(0, 1)`, the same as `X_2` alone. The decoder applies `X_2`, leaving `X_0 X_1 X_2` = logical X. **Logical error.**

## Logical error rate vs physical

For independent bit-flip errors at rate `p` per qubit, the post-decode logical error probability is the probability of weight ≥ 2:
```
P_L(p) = 3 p^2 (1 - p)  +  p^3  =  3 p^2 - 2 p^3.
```
At small `p`, `P_L ≈ 3 p^2` — quadratic suppression. The code starts to *help* (i.e. `P_L < p`) below
```
3 p^2 - 2 p^3  <  p   <=>   p < 0.5.
```
So the **pseudo-threshold** is exactly `1/2`, the trivial point where bit-flip noise is uninformative. (For real codes with realistic, non-zero-cost syndrome extraction, the threshold is far below 1/2; the repetition code's "infinity" threshold is an artefact of assuming syndrome extraction is free.)

We verify the formula `P_L = 3 p^2 - 2 p^3` numerically by Pauli sampling. See `qec/codes/repetition.py::monte_carlo_logical_error` and the demo notebook.

## Phase-flip code: same code, rotated basis

The 3-qubit *phase-flip* code stabilises the codespace
```
|0_L> = |+++>,    |1_L> = |--->,
```
with stabilizers `X_0 X_1` and `X_1 X_2`. Construction: encode bit-flip-style, then apply `H` to every qubit. It corrects any single Z error and is helpless against X errors.

Why both variants? Real noise has both X and Z components, and **the bit-flip code is helpless against Z, the phase-flip code is helpless against X**. Neither fixes general noise. Shor (Phase 5) glues them: encode each phase-flip "qubit" into a bit-flip code, getting [[9,1,3]] which corrects any single-qubit Pauli.

## Two ways to simulate

Throughout this repo we have two simulators, both useful for the repetition code:

1. **State-vector simulation (`qec.statevec`).** Build the encoded state, apply `X` operators, measure stabilizers explicitly. Slow per shot but exact. Use it for unit tests (verify that round-trip with weight ≤ 1 errors leaves the state unchanged, with weight 2 errors flips it).

2. **Pauli sampling (closed form).** Since the noise channel is Pauli (bit-flip is a probabilistic mixture of `I` and `X`), the syndrome and recovery commute with everything else, and we never actually need to track the state vector — just the bit pattern of injected errors. `monte_carlo_logical_error` is 50000 shots in milliseconds.

Method 2 is what stabilizer simulators do at scale. The repetition code is small enough that we can afford method 1 for sanity, but the Monte-Carlo plot in the demo uses method 2 because it's so much faster.

## Why this code is *not* a real QEC code

Strict QEC requires distance ≥ 3 against arbitrary single-qubit errors (X, Y, Z). The 3-qubit repetition code has distance 3 only against the *one* error type it was designed for. A single Z error on any qubit is invisible to the syndrome (the stabilizers `Z_0 Z_1`, `Z_1 Z_2` commute with all `Z`s), and Z does affect the encoded superposition: `Z_0 (alpha|000> + beta|111>) = alpha|000> - beta|111>`, which is logical Z applied. So this code "corrects bit flips and ignores phase flips", which is a fiction in any real noise environment.

Take it as a stepping stone, not a destination. The Steane and Shor codes (Phase 5) are the smallest *real* QEC codes.

## Demo

`demos/04_repetition_code.ipynb`:
- Build the encoder; verify it produces `alpha|000> + beta|111>` directly.
- Inject every weight-1 X error and confirm the syndrome table recovers the original state exactly.
- Inject a weight-2 error and observe the logical flip.
- Plot Monte-Carlo logical-error rate vs `p` for `p ∈ [0, 0.5]` against the analytic `3 p^2 - 2 p^3` curve, plus a comparison line `y = p` to see the crossover.

`qiskit_demos/repetition_qiskit.ipynb` does the same experiment on `qiskit-aer.AerSimulator` with a depolarising noise model on each qubit, so you can sanity-check that "real" syndrome circuits in Qiskit behave the same way as our hand-rolled simulation.

## See also

- Nielsen & Chuang Ch. 10.1 — the cleanest written treatment.
- Shor (1995), https://journals.aps.org/pra/abstract/10.1103/PhysRevA.52.R2493 — concatenates two repetition codes to get the first true QEC code.
- Qiskit Textbook, *Introduction to Quantum Error Correction* — runnable Qiskit notebooks for the same experiment.
