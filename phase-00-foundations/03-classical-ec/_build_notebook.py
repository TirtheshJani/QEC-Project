"""One-shot generator for ``classical_ec.ipynb``.

Run once:

    python -m uv run python phase-00-foundations/03-classical-ec/_build_notebook.py

The notebook is committed; this script exists so the source of truth for
the notebook structure is reviewable in git diff form. It is safe to
re-run: it overwrites the .ipynb file with the regenerated version.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "classical_ec.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 0.3 — Classical error correction over a BSC

Third and final content notebook of Phase 0. Phase 0.1 built the linear
algebra; Phase 0.2 built the binary symmetric channel BSC(p) and its
Shannon capacity `C(p) = 1 - H_2(p)`. This notebook does the simplest
non-trivial thing you can do with a noisy channel: **encode** a message
into a longer codeword, send the codeword through the channel, and
**decode** what comes out. Two codes:

1. The **repetition code (3, 1, 3)**: send each bit three times, vote.
2. The **Hamming (7, 4, 3) code**: the smallest single-error-correcting
   linear code, decoded by syndrome lookup.

The plot at the end shows logical error rate vs physical flip
probability for both codes against the uncoded `y = x` baseline. Two
features of that plot are the entire point of the exercise:

* Coding helps below a crossover and *hurts* above it. There is no
  free lunch.
* The plot shape returns in Phase 3 for the surface code, where the
  crossover is called the **threshold**. Recognising it then is why
  we are drawing it now.

**Helpers used.** `qec_project.codes.classical.RepetitionCode`,
`qec_project.codes.classical.Hamming74`, and
`qec_project.noise.classical.bsc_flip` (the BSC simulator from Phase
0.2). Tests live in `tests/test_classical_codes.py`.

**References.** MacKay, *Information Theory, Inference, and Learning
Algorithms*, chapter 1 (the Hamming(7,4) example); Hamming (1950), the
original (7, 4) paper. Both are in `docs/reading-list.md`.
"""
    )
)

cells.append(
    code(
        """import itertools

import matplotlib.pyplot as plt
import numpy as np

from qec_project.codes.classical import Hamming74, RepetitionCode
from qec_project.noise.classical import bsc_flip

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)
"""
    )
)

cells.append(
    md(
        """## 1. Linear codes in 90 seconds

A **block code** maps each `k`-bit message to an `n`-bit codeword
(`n > k`). The **code rate** is `R = k / n`. A code is **linear** if
the set of codewords is closed under bitwise XOR; equivalently, the
codewords form a vector subspace of `GF(2)^n`. Two matrices specify a
linear code:

* The **generator matrix** `G` is `(k, n)` over GF(2); each message
  `m` (a length-`k` row vector) is encoded as `c = m G mod 2`.
* The **parity-check matrix** `H` is `(n - k, n)` over GF(2); a vector
  `y` is a codeword iff `H y^T mod 2 == 0`. Equivalently
  `H G^T mod 2 == 0`.

For a received word `y = c + e` (with error `e`), the **syndrome**

$$s = H y^T = H (c + e)^T = H e^T \\pmod{2}$$

depends only on the error, not on the transmitted codeword. That is
the whole reason syndrome decoding works.

The **minimum distance** `d` is the smallest Hamming weight of any
nonzero codeword. A linear code with minimum distance `d` can detect
up to `d - 1` errors and correct up to `floor((d - 1) / 2)` errors.
The repetition code below has `d = 3` (one nonzero codeword,
`(1, 1, 1)`, weight 3); the Hamming(7,4) code also has `d = 3`. Both
correct exactly one bit-flip per block.
"""
    )
)

cells.append(
    md(
        """## 2. The repetition code (3, 1, 3)

Encode 0 -> `(0, 0, 0)`, 1 -> `(1, 1, 1)`. Decode by majority vote. In
matrix form the generator is

$$G = \\begin{pmatrix} 1 & 1 & 1 \\end{pmatrix}, \\qquad
H = \\begin{pmatrix} 1 & 1 & 0 \\\\ 1 & 0 & 1 \\end{pmatrix},$$

i.e. each parity check asserts `bit_0 == bit_i` for `i = 1, 2`. The
syndrome is therefore the pair `(bit_0 XOR bit_1, bit_0 XOR bit_2)`.
"""
    )
)

cells.append(
    code(
        """rep = RepetitionCode(3)
print("G =", rep.G.tolist())
print("H =")
print(rep.H)
print()
print("H G^T mod 2 =", ((rep.H @ rep.G.T) % 2).tolist())
print("encode([0]) =", rep.encode(np.array([0], dtype=np.uint8))[0].tolist())
print("encode([1]) =", rep.encode(np.array([1], dtype=np.uint8))[0].tolist())
"""
    )
)

cells.append(
    md(
        """`H G^T mod 2` is the zero matrix, confirming that every codeword has
zero syndrome. Now decode a received word with one bit flipped.
"""
    )
)

cells.append(
    code(
        """codeword = rep.encode(np.array([1], dtype=np.uint8))
print("clean codeword:   ", codeword[0].tolist())

received = codeword.copy()
received[0, 1] ^= 1
print("with bit 1 flipped:", received[0].tolist())

decoded, syndromes = rep.decode(received)
print("syndrome:         ", syndromes[0].tolist())
print("majority-vote decode:", int(decoded[0, 0]))
"""
    )
)

cells.append(
    md(
        """Closed form for the logical error rate. The 3-bit repetition code
fails iff two or three of the three bits are flipped, so

$$p_L(p) = 3 p^2 (1 - p) + p^3 = 3 p^2 - 2 p^3.$$

At small `p`, `p_L ~ 3 p^2` (quadratic suppression). At `p = 0.5`,
`p_L = 0.5` (chance level). The crossover with the uncoded baseline
`p_L = p` is at `p = 0.5`: above it, repeating is worse than not
repeating.

Verify by Monte Carlo on the same `p` sweep we used in Phase 0.2.
"""
    )
)

cells.append(
    code(
        """nominal_ps = np.array([0.01, 0.05, 0.1, 0.2, 0.3, 0.4])
n_trials = 10_000

rep_empirical = np.empty_like(nominal_ps)
for i, p in enumerate(nominal_ps):
    msgs = rng.integers(0, 2, size=(n_trials, 1), dtype=np.uint8)
    codewords = rep.encode(msgs)
    received = bsc_flip(codewords, float(p), rng)
    decoded, _ = rep.decode(received)
    rep_empirical[i] = float(np.mean(decoded != msgs))

p_grid = np.linspace(0.0, 0.5, 201)
rep_closed_form = 3 * p_grid**2 * (1 - p_grid) + p_grid**3

print(f"{'p_nominal':>10} {'p_logical_emp':>14} {'p_logical_thy':>14}")
for p, emp in zip(nominal_ps, rep_empirical, strict=True):
    thy = 3 * p**2 * (1 - p) + p**3
    print(f"{p:>10.4f} {emp:>14.4f} {thy:>14.4f}")
"""
    )
)

cells.append(
    code(
        """fig, ax = plt.subplots(figsize=(6.0, 4.0))
ax.plot(p_grid, p_grid, color="gray", linestyle="--", label="uncoded (y = p)")
ax.plot(p_grid, rep_closed_form, color="C0",
        label="repetition(3,1) closed form: 3 p^2 - 2 p^3")
ax.scatter(nominal_ps, rep_empirical, color="C0", zorder=3,
           label="repetition(3,1) empirical")
ax.axvline(0.5, color="black", linewidth=0.5, linestyle=":")
ax.set_xlabel("physical flip probability p")
ax.set_ylabel("logical error rate")
ax.set_title("Repetition(3,1) vs uncoded over BSC(p)")
ax.legend(loc="upper left")
ax.set_xlim(0.0, 0.5)
ax.set_ylim(0.0, 0.5)
fig.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        """The empirical dots sit on the closed-form curve. The curve crosses
the uncoded diagonal at `p = 0.5`: above that, the repetition code
makes things worse, because the majority vote concentrates whatever
errors the channel introduces. This crossover is the simplest
possible example of the more general fact we will see in Phase 3:
an error-correcting code only helps when the channel is below the
code's threshold.
"""
    )
)

cells.append(
    md(
        """## 3. The Hamming(7, 4, 3) code

Encodes 4 message bits to 7 codeword bits. Corrects any single-bit
error in the 7-bit block. Code rate is `4 / 7 ~ 0.571`, much better
than `1 / 3` for repetition. Discovered by R. W. Hamming in 1950
(see `docs/reading-list.md`).

In **systematic form**, the codeword is `(d0, d1, d2, d3, p0, p1, p2)`
with parity bits `p_i` defined to make each parity check vanish:

* `p0 = d0 + d1 + d3 mod 2`
* `p1 = d0 + d2 + d3 mod 2`
* `p2 = d1 + d2 + d3 mod 2`

Equivalently `G = [I_4 | A]` and `H = [A^T | I_3]` where `A` is the
4-by-3 matrix encoding those three parity equations.
"""
    )
)

cells.append(
    code(
        """ham = Hamming74()
print("G (4 by 7) =")
print(ham.G)
print()
print("H (3 by 7) =")
print(ham.H)
print()
print("H G^T mod 2 (should be zero):")
print((ham.H @ ham.G.T) % 2)
"""
    )
)

cells.append(
    md(
        """The parity-check rows are the three triples of bit positions that
must XOR to zero in every codeword. There are seven distinct nonzero
3-bit syndromes, and each one matches a column of `H` (the syndrome
of a single error at position `j` is the `j`-th column of `H` by
construction). The syndrome table maps each integer-encoded syndrome
back to its error pattern.
"""
    )
)

cells.append(
    code(
        """print("Hamming(7,4) syndrome table:")
print("  syndrome (b0 b1 b2)  ->  error pattern (positions 0..6)")
for s_int in range(8):
    pattern = ham.syndrome_table[s_int]
    bits = ((s_int >> 2) & 1, (s_int >> 1) & 1, s_int & 1)
    flipped = int(np.argmax(pattern)) if pattern.sum() else -1
    desc = "no error" if flipped < 0 else f"flip bit {flipped}"
    print(f"  ({bits[0]} {bits[1]} {bits[2]})              ->  {pattern.tolist()}   ({desc})")
"""
    )
)

cells.append(
    md(
        """Walked example. Encode `m = (1, 0, 1, 1)`, flip bit 2, recover.
"""
    )
)

cells.append(
    code(
        """msg = np.array([1, 0, 1, 1], dtype=np.uint8)
codeword = ham.encode(msg)
print("message m         =", msg.tolist())
print("codeword c = m G  =", codeword.tolist())

received = codeword.copy()
received[2] ^= 1
print("received (bit 2 flipped) =", received.tolist())

s = ham.syndrome(received)
print(f"syndrome s = H y^T = {s.tolist()} -> int {int(s[0]) * 4 + int(s[1]) * 2 + int(s[2])}")

corrected, _ = ham.decode(received)
recovered = ham.extract_message(corrected)
print("corrected codeword       =", corrected.tolist())
print("recovered message        =", recovered.tolist())
assert np.array_equal(recovered, msg)
"""
    )
)

cells.append(
    md(
        """Exhaustive single-error test: for every one of the 16 messages and
every one of the 7 error positions, the decoder must recover the
original message. That gives `16 * 7 = 112` cases.
"""
    )
)

cells.append(
    code(
        """all_msgs = np.array(list(itertools.product([0, 1], repeat=4)), dtype=np.uint8)
all_cw = ham.encode(all_msgs)

n_correct = 0
n_total = 0
for pos in range(7):
    flipped = all_cw.copy()
    flipped[:, pos] ^= 1
    corrected, _ = ham.decode(flipped)
    recovered = ham.extract_message(corrected)
    n_correct += int(np.all(recovered == all_msgs))
    n_total += 1

print(f"all single-bit errors corrected: {n_correct}/{n_total} positions")
assert n_correct == n_total
"""
    )
)

cells.append(
    md(
        """## 4. The headline plot: uncoded vs repetition(3,1) vs Hamming(7,4)

Same simulation framework for both codes. For each nominal `p` in the
sweep:

1. Draw `N = 10000` random length-`k` messages.
2. Encode each one to length `n`.
3. Pass every bit through BSC(p) via `bsc_flip`.
4. Decode each block.
5. Compare data bits before encoding vs after decoding; report
   logical bit-error rate.

Closed-form references for sanity:

* Repetition(3,1) logical error rate: `3 p^2 - 2 p^3`.
* Hamming(7,4) logical *block* error rate (probability that two or
  more of seven bits flipped, since the code corrects one error per
  block):
  `P_block = 1 - (1 - p)^7 - 7 p (1 - p)^6`.

The Hamming closed form is a block-error rate; the simulated curve
is a per-data-bit error rate (averaged over 4 bits), so the two
should match in shape but not in absolute value. Both are plotted.
"""
    )
)

cells.append(
    code(
        """ham_empirical = np.empty_like(nominal_ps)
for i, p in enumerate(nominal_ps):
    msgs = rng.integers(0, 2, size=(n_trials, 4), dtype=np.uint8)
    codewords = ham.encode(msgs)
    received = bsc_flip(codewords, float(p), rng)
    corrected, _ = ham.decode(received)
    recovered = ham.extract_message(corrected)
    ham_empirical[i] = float(np.mean(recovered != msgs))

ham_block_closed_form = (
    1.0 - (1 - p_grid) ** 7 - 7 * p_grid * (1 - p_grid) ** 6
)

print(f"{'p':>8} {'uncoded':>10} {'rep(3,1)':>10} {'ham(7,4) bit':>14} {'ham block':>12}")
for p, r, h in zip(nominal_ps, rep_empirical, ham_empirical, strict=True):
    block = 1 - (1 - p) ** 7 - 7 * p * (1 - p) ** 6
    print(f"{p:>8.3f} {p:>10.4f} {r:>10.4f} {h:>14.4f} {block:>12.4f}")
"""
    )
)

cells.append(
    code(
        """fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.loglog(p_grid[1:], p_grid[1:], color="gray", linestyle="--",
          label="uncoded (y = p)")
ax.loglog(p_grid[1:], rep_closed_form[1:], color="C0",
          label="rep(3,1) closed form")
ax.loglog(p_grid[1:], ham_block_closed_form[1:], color="C1",
          label="Hamming(7,4) block-error closed form")
ax.loglog(nominal_ps, rep_empirical, "o", color="C0",
          label="rep(3,1) empirical")
ax.loglog(nominal_ps, ham_empirical, "s", color="C1",
          label="Hamming(7,4) empirical (per data bit)")
ax.set_xlabel("physical flip probability p")
ax.set_ylabel("logical error rate")
ax.set_title("Logical vs physical error rate: rep(3,1) and Hamming(7,4) over BSC(p)")
ax.legend(loc="lower right", fontsize=9)
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        """The picture in three observations:

1. At small `p` both codes lie **below** the uncoded diagonal: they
   correct most errors. The logical error rate scales like `p^2` for
   both (each code corrects up to one error, so the leading-order
   failure mode is two simultaneous errors).
2. There is a **crossover** somewhere in `(0, 0.5)` where each
   code's curve crosses the uncoded diagonal. Above the crossover,
   coding makes things worse: encoding `k` bits into `n > k` bits
   gives the channel `n - k` more chances to introduce errors, and
   above the crossover the decoder cannot keep up.
3. The Hamming(7,4) curve is below the repetition curve at small
   `p` despite a higher code rate (4/7 vs 1/3). This is the first
   hint that *better codes* exist (lower logical error rate at the
   same physical rate, or the same logical error rate at higher
   physical rate). The full story is the noisy-channel coding
   theorem (MacKay chapter 10).

## Foreshadowing Phase 3

In Phase 3 we will see the same plot for the rotated surface code,
with one extra knob: the **code distance** `d`. Each `d` gives a
different logical-error-rate curve, and all the curves cross at the
same point. That crossover is called the **threshold** of the code.
Recognising this plot then is the entire point of drawing it now.
"""
    )
)

cells.append(
    md(
        """## Recap and what is next

What we now have in hand:

* Generator and parity-check matrices `G`, `H` for two block codes;
  the relation `H G^T mod 2 == 0` verified explicitly.
* A working encoder + majority-vote decoder for the repetition code,
  with closed-form logical error rate agreeing with simulation.
* A working encoder + syndrome-table decoder for Hamming(7,4),
  exhaustively verified against every single-bit error.
* A log-log plot of logical error rate vs physical error rate for
  uncoded / rep(3,1) / Hamming(7,4) that previews the threshold
  picture from Phase 3.

**Phase 0 is complete.** The next deliverable is Phase 1 (quantum
basics: states, gates, measurement, density matrices, the Bloch
sphere). Phase 2 then introduces stabilizer codes; the Hamming(7,4)
code we just built reappears there as half of the Steane code, the
smallest non-trivial CSS code.
"""
    )
)


nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.12",
    },
}

OUT.write_text(nbf.writes(nb), encoding="utf-8")
print(f"wrote {OUT}")
