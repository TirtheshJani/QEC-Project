# 08 — The Steane [[7, 1, 3]] code

The smallest CSS code, due to Andrew Steane (1996). Encodes one logical qubit into seven physical qubits and corrects any single-qubit Pauli error. Distance 3, like Shor — but with two fewer qubits, a much cleaner mathematical structure (built directly from the classical [7, 4] Hamming code), and **transversal Clifford gates**, which is what makes Steane the natural starting point for fault-tolerance discussions (Phase 7).

## The classical [7, 4] Hamming code

The [7, 4] Hamming code is a classical linear code that encodes 4 data bits into 7 codeword bits with parity-check matrix
```
H = | 0 0 0 1 1 1 1 |
    | 0 1 1 0 0 1 1 |
    | 1 0 1 0 1 0 1 |
```
Three rows, three parity checks. Column `q` of `H` is the binary representation of `q + 1`, so a single bit error on bit `q` produces a unique non-zero syndrome (bits read as a binary number) that *is* `q + 1`. Decoding: read the syndrome as an integer, that's the bad bit. This is the cleanest possible classical decoder.

## The CSS construction (Steane)

Take one classical code and use its parity-check matrix `H` to define **both** X-type and Z-type stabilizer generators:
```
X-stabilizers (3): IIIXXXX,  IXXIIXX,  XIXIXIX     (rows of H, X in non-zero columns)
Z-stabilizers (3): IIIZZZZ,  IZZIIZZ,  ZIZIZIZ     (same rows, Z in non-zero columns)
```
Six generators on seven qubits → one logical qubit.

Why this is a valid stabilizer code: each X-stabilizer commutes with each Z-stabilizer iff the corresponding rows of `H` and `H` have an even symplectic inner product, i.e. iff `H · H^T = 0 (mod 2)`. For the [7, 4] Hamming code this is true (the dual code contains the code, a property called **self-orthogonality**, and Steane is built specifically to satisfy it).

This pattern — same matrix on X and Z sides, requiring `H · H^T = 0` — is the **CSS construction** in its simplest form. We'll cover it more generally in note 09.

## Logical operators

```
logical X  =  X X X X X X X        (X on all 7 qubits)
logical Z  =  Z Z Z Z Z Z Z
```
You can verify: each commutes with every stabilizer (sums of rows of `H` and the all-1s vector intersect in even positions), and they anticommute with each other (the all-1s row has odd inner product with itself in seven positions).

## Why decoding is trivial

When a Pauli error `E` hits the encoded state, each stabilizer generator either commutes (`+1` outcome on measurement) or anticommutes (`-1`) with `E`. Anticommutation is determined by symplectic inner products: the X-stabilizers detect the **Z-component** of the error (they are X operators, so they anticommute with Z), and vice versa.

For a Z-component on qubit `q`, the X-stabilizer syndrome is exactly column `q + 1` of `H` — by construction. So:
```
sx (read as binary integer)  =  the qubit (1-indexed) with a Z-error
sz (read as binary integer)  =  the qubit (1-indexed) with an X-error
```
The decoder is "decode sx as a Hamming syndrome to find the X-error qubit, decode sz to find the Z-error qubit, apply the corrections". A Y error produces both a non-zero `sx` and a non-zero `sz`, and the decoder recovers it as `X` + `Z` (correctly, modulo the stabilizer phase).

This is the punchline of CSS codes: **classical decoding ports straight into quantum decoding, twice**. Every classical decoding algorithm becomes a QEC decoding algorithm.

`qec/codes/steane.py::correct(error)` implements exactly this.

## Distance and capacity

[[7, 1, 3]]: 7 physical qubits, 1 logical, distance 3. Corrects any weight-1 Pauli, fails on some weight-2 errors. Same theoretical capacity as Shor [[9, 1, 3]] but with two fewer qubits.

## Transversal Clifford gates

A logical gate is **transversal** if it can be implemented by applying the same single-qubit gate to every physical qubit (or pairwise, qubit-by-qubit, for two-qubit gates). Transversal gates are nice because:
- They cannot spread an error from one qubit to multiple qubits within a code block (the gate touches each qubit independently).
- They are therefore *automatically* fault-tolerant in the simplest sense.

For Steane, the Hadamard, S, and CNOT (between two Steane blocks) are all transversal:
```
H_L  =  H_0 H_1 H_2 H_3 H_4 H_5 H_6
S_L  =  S_0^dagger S_1^dagger ... (the daggers come from how S maps the code's Z-stabilizers)
CNOT_L  =  CNOT(0, 0') CNOT(1, 1') ... CNOT(6, 6')   (between two encoded blocks)
```
**The full Clifford group on a logical qubit can be implemented transversally on Steane.** This is rare and powerful: the only "missing" gate for universality is `T`, which by **Eastin–Knill** cannot be implemented transversally on any code (note 10) and must be supplied by some non-transversal mechanism — e.g. magic state distillation.

## Threshold and beating the unencoded qubit

For independent Pauli noise at rate `p`:
```
P_L(p) ≈ C · p^2   for small p,
```
with `C` empirically of order ~20 (each Steane code can be hit by 7 · 3 = 21 single Paulis, and weight-2 failures are a sub-fraction of (21 choose 2)). The crossover `P_L < p` happens near `p ≈ 0.05` — better than Shor and conventional bit-flip in any honest comparison.

## Why Steane is the gateway to fault tolerance

Three reasons we'll keep coming back to it in Phase 7:

1. **CSS structure**: X and Z corrections are independent, which simplifies fault-tolerant syndrome extraction (you can use Steane-style or Knill-style ancilla preparation).
2. **Transversal Clifford set**: every Clifford acts on the logical qubit by simply applying the same gate to all 7 physical qubits — minimal opportunity for noise to cascade.
3. **Concatenation friendly**: take a Steane-encoded qubit and Steane-encode each of its 7 physical qubits. The concatenated code has distance `3 · 3 = 9` against arbitrary Pauli noise. Iterate to drive logical error rates to arbitrarily small values, given a sufficiently small physical error rate. This is the **threshold theorem** in concrete form (note 10).

## Demo

`demos/06_steane_code.ipynb`:
- Print the stabilizer generators (rows of the Hamming `H`) and verify their commutation.
- Inject every weight-1 Pauli; confirm exact correction (the residual has weight 0).
- Show explicitly that the syndrome `sz` (read as binary) indexes the bad-X qubit; same for `sx` and Z.
- Find a weight-2 error pattern that the decoder fails on (proving distance 3, not 5).
- Plot `P_L(p)` for `p ∈ [0, 0.05]` log-log; confirm slope ≈ 2.

## See also

- Steane (1996), https://royalsocietypublishing.org/doi/10.1098/rspa.1996.0136 — the original.
- Calderbank-Shor (1996), https://arxiv.org/abs/quant-ph/9512032 — the general CSS construction.
- N&C §10.4.2 has a clean walk-through of the decoder.
