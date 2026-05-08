# 09 — CSS codes and general QEC theory

A consolidation note. We have built three QEC codes from scratch (repetition, Shor, Steane). This note pulls back to the general framework: the CSS construction, the Knill–Laflamme error-correction conditions, parameter bounds, and concatenation. The point is to recognise what these codes have in common and where the theoretical limits lie.

## CSS codes (Calderbank–Shor–Steane)

A **CSS code** is a stabilizer code whose generators are partitioned into two sets:
- **X-type generators**: each consisting only of `I` and `X` factors.
- **Z-type generators**: each consisting only of `I` and `Z` factors.

CSS codes are special because:
1. **X errors and Z errors are detected independently.** X-stabilizers anticommute only with Z-component errors, and vice versa. So syndrome decoding splits into two independent classical decoding problems.
2. **They come from pairs of classical codes.** Given two classical linear codes `C_1, C_2 ⊆ F_2^n` with `C_2^⊥ ⊆ C_1`, a CSS code is built by:
   - X-type generators: rows of the parity-check matrix of `C_1` (one X per non-zero entry).
   - Z-type generators: rows of the parity-check matrix of `C_2`.
   - The condition `C_2^⊥ ⊆ C_1` (equivalently: every X-stabilizer commutes with every Z-stabilizer because their bit-wise inner product is even) is **the** CSS condition.

The number of logical qubits is `k = k_1 + k_2 - n` where `k_i = dim(C_i)`. The distance is at least the minimum distance of the two classical codes, ignoring stabilizer-equivalent codewords.

### Steane = Hamming on both sides

Steane's [[7, 1, 3]] code is the simplest CSS code: `C_1 = C_2 = ` the [7, 4] Hamming code. Hamming is **self-dual containing**: its dual `[7, 3, 4]` code is contained in itself, so the CSS condition `C^⊥ ⊆ C` is satisfied. The X- and Z-stabilizers are literally the same matrix on different sides.

### Shor = (3, 1, 3) ⊗ (3, 1, 3)

Shor's [[9, 1, 3]] is also CSS, with X-stabilizers from the (block-internal) bit-flip code and Z-stabilizers from the (block-spanning) phase-flip code. It is a **concatenation**, which is a special case of CSS that we'll see again below.

### Why CSS is dominant

CSS structure makes fault-tolerant syndrome extraction much easier (you can build "Steane-style" or "Knill-style" ancilla blocks that correct X and Z errors in separate rounds), and almost every code people care about — Steane, surface code, qLDPC codes — is CSS.

## Knill–Laflamme conditions

**The** general criterion for a code to correct a set of errors `{E_a}`. A code `C` (with codespace projector `P`) corrects `{E_a}` iff
```
P E_a^dagger E_b P = c_{ab} P
```
for some matrix of complex numbers `c_{ab}`. In words:

- The product `E_a^dagger E_b`, projected onto the codespace, must be a multiple of the codespace projector — i.e. all error pairs `(a, b)` must look identical on the code (up to a complex scalar).

If `c_{ab} = 0` for `a ≠ b`, the errors are **distinguishable** ("non-degenerate" code). If some non-zero off-diagonals exist, the code is **degenerate** — different errors can have the same effect on the codespace, but still be correctable.

For an `[[n, k, d]]` stabilizer code, the KL conditions are equivalent to: every Pauli `P` of weight `< d` either lies in the stabilizer group (degenerate case) or anticommutes with at least one stabilizer generator (so it's detected). The proof is short and elegant — see N&C §10.3.1.

We **don't** need the general formalism to verify Steane: the simpler statement "every weight-1 Pauli error has a unique non-zero syndrome" already implies KL with a `c_{ab}` matrix that is the identity on weight-1 errors. The demo (`demos/07_css_klc.ipynb`) verifies KL numerically on Steane by checking that `P E_a^dagger E_b P` is proportional to `P` for every pair of weight-1 errors.

## Parameter bounds

The fundamental inequality you'll see quoted: the **quantum Singleton bound**
```
n - k ≥ 2(d - 1).
```
For an `[[n, k, d]]` code, the number of "redundant" physical qubits is at least `2(d − 1)`. Codes that saturate this are called **MDS** (maximum-distance separable). Steane (`[[7, 1, 3]]`) saturates it: `7 - 1 = 6 = 2 · 2`. Shor (`[[9, 1, 3]]`) does not (`9 - 1 = 8 > 4`), which is why Steane is preferred whenever you have a choice.

Other bounds you'll meet:
- **Quantum Hamming bound** for non-degenerate codes (combinatorial counting of correctable error patterns; tight for some codes).
- **Quantum Singleton-Plotkin bound**, refinements thereof.

The surface code (Phase 8) has parameters `[[n = O(d^2), k = 1, d]]` — far from saturating the Singleton bound, but its merit is geometric locality, not parameter efficiency.

## Concatenation

Take a code `C_1` of parameters `[[n_1, 1, d_1]]` and a code `C_2` of parameters `[[n_2, 1, d_2]]`. Replace each physical qubit of a `C_1`-encoded logical qubit with a `C_2`-encoded block. The result is a code with parameters `[[n_1 · n_2, 1, ≥ d_1 · d_2]]`.

Shor [[9, 1, 3]] is exactly the concatenation of two 3-qubit repetition codes (each contributing distance 3 against its preferred error type), giving distance 3 against *arbitrary* Pauli noise.

The threshold theorem (note 10) is fundamentally about iterated concatenation: as long as the physical error rate is below some threshold `p_th`, concatenating a code with itself drives the logical error rate doubly-exponentially toward zero.

## Why we won't go beyond CSS

CSS codes cover essentially everything we'll meet in this repo and most of what's done in practice. **Non-CSS** stabilizer codes (where stabilizers can mix X and Z factors freely) exist and are sometimes useful, but they trade away the "decode X and Z independently" property, which complicates everything.

The 5-qubit code `[[5, 1, 3]]` is the smallest stabilizer code that corrects an arbitrary single-qubit error, beating Steane's qubit count by 2. It is **not** CSS — its stabilizers all mix X and Z. This is what trading away CSS structure buys you (two qubits), and what it costs (uglier decoders, no transversal Cliffords).

## Verification on Steane

`demos/07_css_klc.ipynb` confirms the CSS structure and the KL conditions on the Steane code:

1. Compute `H_X · H_Z^T mod 2` and verify it's zero (CSS condition).
2. For each pair of weight-1 errors `(E_a, E_b)`, compute the codespace projector `P_C` and verify `P_C E_a^dagger E_b P_C` is proportional to `P_C` (Knill–Laflamme).
3. Print the `c_{ab}` matrix; confirm it is 21x21 and equal (up to phase) to a permutation × identity (Steane is non-degenerate on weight-1 errors).

This is the rigorous-correctness gate for the codes we built in Phase 5: not just "every weight-1 error has a unique syndrome" but "the deeper KL condition holds, which is what guarantees a recovery operator exists at all".

## See also

- Calderbank & Shor (1996), https://arxiv.org/abs/quant-ph/9512032 — original CSS construction.
- Knill & Laflamme (1997), https://arxiv.org/abs/quant-ph/9604034 — the KL conditions.
- N&C §10.3 (KL), §10.4 (CSS), §10.5 (Shor / Steane / 5-qubit).
- Gottesman, *Surviving as a Quantum Computer in a Classical World*, lecture notes — concise and well-paced.
