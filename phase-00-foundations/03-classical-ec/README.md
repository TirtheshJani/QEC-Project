# Phase 0.3 — Classical error correction over a BSC

The third and final content notebook of Phase 0. Builds two classical
linear codes from scratch, sends their codewords through the binary
symmetric channel from Phase 0.2, and plots the logical error rate vs
physical flip probability. The plot shape (codes help below a
crossover, hurt above it) is the same shape that returns in Phase 3
for the surface code, where the crossover is called the **threshold**.
Recognising it then is the point of doing it now.

## What it covers

1. Linear codes primer: code rate `R = k / n`, minimum distance `d`,
   the `(n, k, d)` tuple. Generator matrix `G` and parity-check
   matrix `H` over GF(2), with the relation `H G^T mod 2 == 0`.
2. Repetition (3, 1, 3) code: encode 1 bit to 3 bits, decode by
   majority vote. Closed-form logical error rate
   `p_L(p) = 3 p^2 - 2 p^3` verified by Monte Carlo at
   `p ∈ {0.01, 0.05, 0.1, 0.2, 0.3, 0.4}` with `N = 10000` trials.
3. Hamming (7, 4, 3) code: explicit systematic
   `G = [I_4 | A]` and `H = [A^T | I_3]`. Syndrome decoding via a
   precomputed lookup table over the 8 possible 3-bit syndromes.
   Exhaustive verification on all 16 messages × 7 single-bit errors.
4. Headline log-log plot of logical error rate vs physical flip
   probability for the uncoded baseline, repetition(3,1), and
   Hamming(7,4). Closed-form curves overlaid on Monte Carlo points.
5. One-sentence Phase 3 foreshadowing: the same plot returns for the
   surface code, where the crossover is the threshold.

The notebook reuses three small helpers promoted to `src/qec_project/`:

- `qec_project.codes.classical.RepetitionCode(n)` — the (n, 1, n)
  repetition code with majority-vote decoding.
- `qec_project.codes.classical.Hamming74` — the (7, 4, 3) Hamming
  code with `G`, `H`, syndrome table, encode, syndrome, decode,
  extract_message.
- `qec_project.noise.classical.bsc_flip(bits, p, rng)` — the BSC
  simulator promoted in Phase 0.2.

Their tests are in `tests/test_classical_codes.py`.

## How to run

From the repo root:

```bash
uv sync --extra dev
uv run jupyter lab phase-00-foundations/03-classical-ec/classical_ec.ipynb
```

Or non-interactively:

```bash
uv run jupyter nbconvert --to notebook --execute \
    phase-00-foundations/03-classical-ec/classical_ec.ipynb \
    --output _check.ipynb
```

A fixed seed (`np.random.default_rng(0)`) is set in the first code
cell; the notebook is deterministic across runs.

`_build_notebook.py` in this directory is the source from which the
notebook is generated. Edit it (not the `.ipynb` directly) when the
notebook structure needs to change, then re-run it.

## After reading this you should be able to

- Write down a generator matrix `G` and parity-check matrix `H` for a
  small linear code over GF(2) and verify `H G^T mod 2 == 0`.
- Encode a message, decode a received word by majority vote (for
  repetition codes) or syndrome lookup (for Hamming(7,4)).
- Predict that a (7, 4, 3) code has leading-order logical error rate
  `~ p^2` at small `p` because it corrects up to one bit-flip.
- Explain why every error-correcting code has a crossover above which
  it makes things worse than not coding.
- Recognise the threshold picture in Phase 3 as the same plot with
  one extra knob (the code distance `d`).

## References

Both are in `docs/reading-list.md`:

- David J. C. MacKay. *Information Theory, Inference, and Learning
  Algorithms.* Cambridge, 2003 — chapter 1 (the Hamming(7,4) example).
- Richard W. Hamming. *Error Detecting and Error Correcting Codes.*
  Bell System Technical Journal 29 (2): 147–160 (1950).
  doi:`10.1002/j.1538-7305.1950.tb00463.x`. The original paper.
