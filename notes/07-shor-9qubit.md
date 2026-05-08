# 07 — The Shor [[9, 1, 3]] code

The first true quantum error-correcting code, due to Peter Shor (1995). The smallest QEC code that handles **arbitrary single-qubit Pauli errors** (X, Y, or Z), at the cost of nine physical qubits per logical qubit and a fixed-parity decoder.

## The construction in one sentence

**Concatenate** the 3-qubit phase-flip code with the 3-qubit bit-flip code: encode a logical qubit into a phase-flip code, then encode each of the resulting three qubits separately into a bit-flip code.

That description hides what is really happening. Let's unpack.

## Why concatenation works

The two repetition codes (note 06) each correct one type of error and ignore the other:
- **Bit-flip code** corrects X, ignores Z.
- **Phase-flip code** corrects Z, ignores X.

If we feed the *output* of the phase-flip code into the input of the bit-flip code on each block — i.e. encode each "logical" qubit of the phase-flip code as three physical qubits in the bit-flip code — then within each block, X errors are corrected. Across blocks, Z errors are corrected by the phase-flip code (whose "physical qubits" are now whole bit-flip blocks).

What about Y errors? Y = iXZ (up to a phase), so a Y error on a single physical qubit is a combined X and Z error. The X part is detected and corrected by the inner code; the Z part propagates to the outer code (via the encoded-block representation) and is corrected there. Either way, single-qubit errors of any type are corrected.

## Logical states explicit

The encoded basis states are
```
|0_L> =  ((|000> + |111>) (|000> + |111>) (|000> + |111>)) / (2 sqrt(2))
|1_L> =  ((|000> - |111>) (|000> - |111>) (|000> - |111>)) / (2 sqrt(2))
```
Each of the three "blocks" of three qubits is in a `|+>_3 := (|000> + |111>)/sqrt(2)` or `|->_3 := (|000> - |111>)/sqrt(2)` state, and these three blocks are themselves in a phase-flip pattern (`|+>+_3 |+>_3 |+>_3` for `|0_L>`, all `|->_3` for `|1_L>`).

If you stare at this long enough you'll see that it really is two codes glued together — but it is much faster to read off the **stabilizer generators** and trust that they encode the same information.

## Stabilizer generators

Eight generators on nine qubits → one logical qubit:

**Six Z-type stabilizers (handle X errors within each block):**
```
Z_0 Z_1 ,  Z_1 Z_2          ← block 0 = qubits {0, 1, 2}
Z_3 Z_4 ,  Z_4 Z_5          ← block 1 = qubits {3, 4, 5}
Z_6 Z_7 ,  Z_7 Z_8          ← block 2 = qubits {6, 7, 8}
```
Within each block these are exactly the bit-flip code's stabilizers (note 06). They detect any X error inside the block.

**Two X-type stabilizers (handle Z errors via the phase-flip-code structure):**
```
X_0 X_1 X_2 X_3 X_4 X_5     ← parity of blocks 0, 1
X_3 X_4 X_5 X_6 X_7 X_8     ← parity of blocks 1, 2
```
A Z error on any qubit in block `b` looks identical (modulo the inner-code stabilizer group) to a single Z on, say, qubit `3b`. The two X-type generators measure the parity of phase-flip-code logical states across blocks, just as the two Z-stabilizers of the inner repetition code measure bit-flip parity.

The logical operators are
```
logical Z = X_0 X_1 X_2 X_3 X_4 X_5 X_6 X_7 X_8
logical X = Z_0 Z_3 Z_6        (one Z per block)
```

## Decoding: divide and conquer

Decoding is two passes:

**Inner pass.** Within each block, look at the two Z-stabilizer outcomes and apply the bit-flip code's recovery: a single X on the qubit pointed at by the syndrome (note 06's table). This handles all X parts of any Pauli error in the block.

**Outer pass.** Look at the two X-stabilizer outcomes. Three syndromes are possible (other than no-error), each pointing to one block; apply Z to one canonical qubit of that block (the first, by convention). This handles the Z part of any Pauli error.

After both passes, every weight-1 input error has been mapped to identity (modulo the stabilizer group). Verified exhaustively in `qec/codes/shor.py::all_weight1_errors_corrected()` and `tests/test_codes.py::test_shor_corrects_every_weight_1_error`.

## Distance

Shor's code has **distance d = 3**: the minimum-weight non-stabilizer logical operator has weight 3 (e.g. `Z_0 Z_3 Z_6` = logical X). So it corrects up to `(d-1)/2 = 1` error and detects up to `d - 1 = 2`.

## Y errors are handled "for free"

If you write Y = i X Z and apply it to a single qubit, the X part flips two Z-stabilizers (the inner-code recovery fires), and the Z part flips two X-stabilizers (the outer-code recovery fires). Since the two passes are independent (X-stabilizers only detect Z components, Z-stabilizers only detect X components), they don't interfere. **CSS structure**, in essence — see Phase 6 (`notes/09`).

(Y has a phase factor of `i` that gets absorbed into the residual, but residuals only matter modulo the stabilizer group, not their phase.)

## Logical error rate

Approximately. For independent Pauli noise at rate `p` per qubit (each error randomly from {X, Y, Z}), the leading-order logical error rate is
```
P_L(p)  ≈  C  ·  p^2 ,
```
with `C` a code-dependent constant (roughly the number of weight-2 errors that the decoder gets wrong, divided by 9-choose-2 = 36). For Shor, `C` is of order ~30 — empirically `P_L(0.05) ≈ 0.03–0.04` from the Monte-Carlo runs in the demo.

The crossover where the code starts to *help* (`P_L < p`) is near `p ≈ 0.03`, much below the repetition code's degenerate `1/2`. This is the price of correcting both error types: weight-2 errors are more common because there are more "bad" weight-2 patterns.

## When you'd actually use it

You wouldn't, in practice. The Shor code is **historically** important and **conceptually** clean (concatenation as a generic recipe, two-pass decoding), but for real fault-tolerance work it has been completely supplanted by:
- **Steane** [[7, 1, 3]] (note 08), with one fewer physical qubit and *transversal* logical Cliffords.
- **Surface code** (note 11), with 2D-locality and a much higher threshold.

But it remains the cleanest demonstration that QEC works at all. If somebody asks "show me a quantum code that corrects errors", Shor is what to draw on the napkin.

## Demo

`demos/05_shor_code.ipynb`:
- Print the stabilizer generators and logical operators; verify they pairwise commute and form a valid 1-logical-qubit stabilizer code.
- Inject every weight-1 Pauli error in turn; verify each is corrected exactly.
- Inject a representative weight-2 error and observe the logical failure.
- Plot Monte-Carlo logical error rate vs `p` for `p ∈ [0, 0.05]`, on log-log axes, and confirm the slope is approximately 2 (i.e. `P_L ∝ p^2`).
