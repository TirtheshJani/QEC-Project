# Plan: Phase 0.3 — Classical error correction (repetition + Hamming(7,4))

Authored: 2026-05-14. Methodology: Superpowers `writing-plans` (in
spirit; plugin not yet installed). Followed by
`test-driven-development` for any code promoted into
`src/qec_project/`.

## Goal

Deliver the third and final content notebook of Phase 0,
`phase-00-foundations/03-classical-ec/classical_ec.ipynb`, covering
exactly Phase 0 README learning goal 3: implement a repetition(3,1)
code and a Hamming(7,4) code from scratch, both with explicit
generator matrix `G` and parity-check matrix `H`, send their codewords
through `qec_project.noise.classical.bsc_flip`, decode by majority
vote (repetition) and syndrome lookup (Hamming), and plot the logical
error rate vs physical flip probability for the two codes against the
uncoded `y = x` baseline. The notebook runs top-to-bottom with seeds
set. Reusable helpers (`RepetitionCode`, `Hamming74` classes with
`encode` / `decode` methods, plus their fixed `G` and `H` matrices) go
to a new `src/qec_project/codes/classical.py` with tests, because
Phase 2 (Steane = quantum CSS built from Hamming(7,4)) reuses them.

The plot shape produced here (codes help below a crossover, hurt
above it) is the same shape that returns in Phase 3 for the surface
code, where the crossover is the **threshold**. The notebook calls
this out explicitly so the reader recognises it later.

## Scope

### In scope

- Linear codes primer: codeword, code rate `k/n`, minimum distance,
  the `(n, k, d)` tuple. Define `G` (k by n) and `H` ((n-k) by n)
  over GF(2). State without proof: a linear code corrects up to
  `floor((d-1)/2)` errors.
- Repetition code `(3, 1, 3)`: encode 1 bit to 3, decode by majority
  vote. Closed-form logical error rate
  `p_L = 3 p^2 (1 - p) + p^3 = 3 p^2 - 2 p^3` for the bit-flip
  channel (two or three flips out of three is unrecoverable).
  Simulate over BSC(p) for
  `p in {0.01, 0.05, 0.1, 0.2, 0.3, 0.4}` with `N = 10000` trials,
  plot empirical vs nominal, overlay closed-form curve, mark the
  `p = 1/2` break-even.
- Hamming(7,4): explicit `G` (4 by 7) and `H` (3 by 7) in standard
  form. Encode 4-bit messages. Syndrome decode: `s = H y^T mod 2`,
  zero syndrome -> no error, nonzero syndrome -> exact column of
  `H` matches the single-bit error pattern (so flip that bit).
  Extract data bits from the corrected codeword.
- Full simulation: send `N = 10000` random 4-bit messages through
  BSC(p) at the same p sweep, decode, compute logical
  bit-error rate (BER over the 4 data bits). Overlay
  uncoded / repetition / Hamming on one log-log plot. Closed-form
  Hamming logical block-error rate is the probability of two or more
  flips in seven bits: `1 - (1-p)^7 - 7 p (1-p)^6`, overlaid as a
  reference.
- Connect to Phase 3 in one markdown sentence: "the same plot shape
  returns for the surface code, where the crossover is called the
  threshold."

### Out of scope (deferred)

- Any quantum content (CSS codes, stabilizers, Pauli noise) -> Phase
  2+.
- Larger linear codes (Reed-Muller, BCH, Reed-Solomon).
- Soft-decision decoding, LLR-based decoding, list decoding.
- Belief propagation, MWPM, neural decoders -> Phase 5.
- Burst-error / non-iid noise channels.
- Multi-error-correcting codes beyond Hamming(7,4)'s single-error
  correction.

## File-by-file changes

| Path | Action | Notes |
| ---- | ------ | ----- |
| `plans/phase-00-03-classical-ec.md` | create | this plan |
| `phase-00-foundations/03-classical-ec/classical_ec.ipynb` | create | the notebook |
| `phase-00-foundations/03-classical-ec/_build_notebook.py` | create | nbformat script that generates the .ipynb (matches Phase 0.1 / 0.2 pattern) |
| `phase-00-foundations/03-classical-ec/README.md` | create | one-pager: what / how / outcomes |
| `src/qec_project/codes/classical.py` | create | `RepetitionCode(n)` and `Hamming74` with `G`, `H`, `encode`, `decode` |
| `tests/test_classical_codes.py` | create | unit + hypothesis property tests |
| `docs/reading-list.md` | edit | add Hamming 1950 with DOI 10.1002/j.1538-7305.1950.tb00463.x |
| `CHANGELOG.md` | edit | append Phase 0.3 milestone; update Current status to "Phase 0 complete; Phase 1 in flight" |

Not modifying: `pyproject.toml`, `tests/test_smoke.py`,
`src/qec_project/linalg.py`, `src/qec_project/info.py`,
`src/qec_project/noise/classical.py`, or
`phase-00-foundations/README.md`.

### Promoted helpers — justification

- `RepetitionCode(n)` with `encode(msg) -> codewords`,
  `decode(received) -> (decoded, syndromes)`: the repetition code is
  the canonical worked example for both the classical and quantum
  bit-flip codes; the 3-qubit and 9-qubit Shor codes in Phase 2 are
  built on top of it.
- `Hamming74` with fixed `G` (4 by 7), `H` (3 by 7), syndrome table,
  `encode`, `decode`, and `extract_message`: Phase 2's Steane code
  is the quantum CSS code built from Hamming(7,4)'s `H` and its
  dual. Promotion now means Phase 2 imports rather than re-derives.

### Public signatures (with type hints)

```python
# src/qec_project/codes/classical.py
class RepetitionCode:
    n: int
    G: np.ndarray   # (1, n) over GF(2)
    H: np.ndarray   # (n-1, n) over GF(2)
    def __init__(self, n: int) -> None: ...
    def encode(self, messages: np.ndarray) -> np.ndarray: ...
    def decode(
        self, received: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]: ...

class Hamming74:
    n: int           # 7
    k: int           # 4
    G: np.ndarray    # (4, 7) over GF(2)
    H: np.ndarray    # (3, 7) over GF(2)
    syndrome_table: np.ndarray  # (8, 7) error patterns indexed by int(syndrome)
    def encode(self, messages: np.ndarray) -> np.ndarray: ...
    def syndrome(self, received: np.ndarray) -> np.ndarray: ...
    def decode(
        self, received: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]: ...
    def extract_message(self, codewords: np.ndarray) -> np.ndarray: ...
```

All inputs and outputs are `numpy.ndarray` of `uint8`. Batches of
messages / codewords are shape `(batch, k)` / `(batch, n)`. Both
classes accept either a 1D single-codeword input or a 2D batch.

## Tests added — `tests/test_classical_codes.py`

Repetition(3,1):

1. `test_rep3_G_and_H_orthogonal_mod2` — `H @ G.T mod 2 == 0`.
2. `test_rep3_encode_zero_msg_is_zero_codeword`.
3. `test_rep3_encode_one_msg_is_all_ones_codeword`.
4. `test_rep3_decode_noiseless_round_trip` — encode then decode
   recovers every 1-bit message.
5. `test_rep3_decode_corrects_every_single_bit_flip` — for each of
   the 3 positions, flipping that bit then decoding recovers the
   message.
6. `test_rep3_decode_fails_on_two_bit_flips` — two flips inverts the
   majority vote, so decoding returns the wrong message (sanity).

Hamming(7,4):

7. `test_hamming74_G_and_H_orthogonal_mod2` — `H @ G.T mod 2 == 0`.
8. `test_hamming74_encode_zero_msg_is_zero_codeword`.
9. `test_hamming74_codeword_dimensions` — `encode` returns shape
   `(batch, 7)`.
10. `test_hamming74_round_trip_noiseless` — for all 16 messages,
    encode then `extract_message(decode(encode(m)))` returns `m`.
11. `test_hamming74_corrects_every_single_bit_error` — for each of
    the 7 positions and each of the 16 messages (16 * 7 = 112
    cases), flipping that bit and decoding recovers the original
    message.
12. `test_hamming74_syndrome_zero_for_codeword` — syndrome of a
    clean codeword is `(0, 0, 0)`.
13. `test_hamming74_syndrome_matches_H_column_for_single_error` —
    flipping bit `j` yields syndrome equal to column `j` of `H`.

Properties (hypothesis):

14. `test_rep3_logical_error_rate_monotone_in_p` — for random
    `p1 < p2` in `[0.01, 0.4]` with fixed `N = 4000`, the
    empirical logical error rate at `p2` is at least as high as at
    `p1` (within Monte Carlo slack of `5/sqrt(N)`).
15. `test_hamming74_logical_error_rate_monotone_in_p` — same for
    Hamming.

## Acceptance criteria

- `python -m uv run pytest` returns 0; total tests >= 35 (existing) +
  >= 15 new = 50 or more.
- `python -m uv run ruff check .` returns 0 findings.
- `python -m uv run jupyter nbconvert --to notebook --execute
  phase-00-foundations/03-classical-ec/classical_ec.ipynb --output
  _check.ipynb` runs to completion without error, then `_check.ipynb`
  is removed.
- `python scripts/verify_reading_list.py` exits 0 after the Hamming
  1950 entry is added.
- Notebook sets `np.random.default_rng(0)` in its first code cell and
  uses no other ad-hoc seeds.
- Notebook contains, in order: linear codes primer, repetition code
  encode/decode, repetition simulation + plot, Hamming(7,4) `G` and
  `H`, syndrome decode walk-through on a worked example, full
  simulation + log-log plot of all three curves, one-sentence
  Phase 3 foreshadowing.
- `CHANGELOG.md` `## Completed milestones` has a new 2026-05-14
  Phase 0.3 entry; `## Current status` is updated to reflect that
  Phase 0 is complete and Phase 1 is in flight in a parallel
  worktree.

## Tasks (2-5 minute units, ordered)

1. Write `src/qec_project/codes/classical.py` with `RepetitionCode`
   and `Hamming74` and their syndrome tables.
2. Write `tests/test_classical_codes.py`. Run
   `python -m uv run pytest tests/test_classical_codes.py -x`;
   iterate until green.
3. Run `python -m uv run pytest -x` to confirm no regressions on the
   prior 35 tests.
4. `python -m uv run ruff check src tests` and fix any findings.
5. Add Hamming 1950 entry to `docs/reading-list.md`; run
   `python scripts/verify_reading_list.py`.
6. Write `_build_notebook.py` for Phase 0.3; run it once to emit
   `classical_ec.ipynb`.
7. Execute the notebook end-to-end via `nbconvert --execute`; iterate
   until clean; delete `_check.ipynb`.
8. Write `phase-00-foundations/03-classical-ec/README.md`.
9. Final sweep: `pytest`, `ruff`, `verify_reading_list.py`.
10. Append CHANGELOG milestone via `scripts/update_changelog.py`;
    update Current status.
11. Commit with `Phase 0.3: Hamming(7,4) + repetition code over BSC`.

## Out-of-band notes

- `uv` is not on PATH; `python -m uv run ...` is the invocation.
- Hamming's 1950 paper has DOI `10.1002/j.1538-7305.1950.tb00463.x`
  (Bell System Technical Journal). Adding it satisfies the integrity
  rule for the `(7, 4)` code construction.
- Phase 1 is being built in parallel in a sibling worktree; current
  status text must phrase Phase 0 completion without depending on
  whether Phase 1 has landed yet.
- The em-dash ban from the *stellar-mk-audit* CLAUDE.md does not
  apply to this project. Normal punctuation allowed.
