# Plan: Phase 0.2 — Probability notebook + BSC helpers

Authored: 2026-05-14. Methodology: Superpowers `writing-plans` (in spirit;
plugin not yet installed). Followed by `test-driven-development` for any
code promoted into `src/qec_project/`.

## Goal

Deliver the second content notebook of the curriculum,
`phase-00-foundations/02-probability/probability.ipynb`, covering exactly
Phase 0 README learning goal 2 (discrete probability and the language of
channels: random variables, conditional probability, Markov chains,
mutual information) and landing at the binary symmetric channel (BSC):
its Shannon capacity `C = 1 - H_2(p)` plotted vs `p`, and an empirical
Monte Carlo confirmation that flipping bits independently with
probability `p` produces an empirical flip rate near `p` within
Monte Carlo error. The notebook runs top-to-bottom with seeds set. Two
short helpers with obvious downstream reuse (BSC simulator, binary
entropy / capacity) are promoted to `src/qec_project/noise/classical.py`
and `src/qec_project/info.py` with tests; anything single-use stays in
the notebook.

## Scope

### In scope

- Discrete random variable, sample space, PMF, expectation, variance.
  One worked biased-coin example.
- Conditional probability and Bayes' rule. One worked noisy-channel
  example that sets up the BSC narrative (P(sent=0 | received=1)).
- Joint distribution on a small alphabet; marginals; computation of
  mutual information by hand and numerically. `I(X;Y) = H(X) - H(X|Y) =
  H(Y) - H(Y|X)` verified for one toy joint.
- Two-state Markov chain: transition matrix, one-step / multi-step
  evolution, stationary distribution as the eigenvector of P^T with
  eigenvalue 1. Used as a vocabulary bridge to channel models.
- BSC(p) defined; binary entropy `H_2(p) = -p log2(p) - (1-p) log2(1-p)`;
  Shannon capacity `C(p) = 1 - H_2(p)`. Plot C vs p for `p in [0, 0.5]`.
  Confirm `C(0) = 1` and `C(0.5) = 0`.
- Simulate BSC with fixed seed: `N = 10000` bits sent through BSC(p) for
  `p in {0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5}`. Plot empirical flip rate
  vs nominal p with a `+/- 1/sqrt(N)` band.
- Foreshadow Phase 0.3: one sentence saying the next notebook will
  encode bits before they enter this channel and decode the output; the
  gap between empirical and nominal flip rates becomes the logical
  error rate.

### Out of scope (deferred)

- Any quantum content (states, Pauli channels, decoherence) -> Phase 1+.
- Hamming(7,4) encoding / syndrome decoding -> Phase 0.3.
- Continuous distributions (Gaussian, etc.).
- Information-theoretic results beyond Shannon's BSC capacity (rate
  distortion, channel coding theorem proofs, Fano, joint typicality).

## File-by-file changes

| Path | Action | Notes |
| ---- | ------ | ----- |
| `plans/phase-00-02-probability.md` | create | this plan |
| `phase-00-foundations/02-probability/probability.ipynb` | create | the notebook |
| `phase-00-foundations/02-probability/_build_notebook.py` | create | nbformat script that generates the .ipynb (matches Phase 0.1 pattern) |
| `phase-00-foundations/02-probability/README.md` | create | one-pager: what / how / outcomes |
| `src/qec_project/noise/classical.py` | create | `bsc_flip(bits, p, rng)` |
| `src/qec_project/info.py` | create | `binary_entropy(p)`, `bsc_capacity(p)` |
| `tests/test_classical_noise.py` | create | unit + hypothesis property tests for `bsc_flip` |
| `tests/test_info.py` | create | unit + hypothesis property tests for entropy / capacity |
| `docs/reading-list.md` | edit | add Shannon 1948 with DOI 10.1002/j.1538-7305.1948.tb01338.x |
| `CHANGELOG.md` | edit | append milestone; update Current status to point at Phase 0.3 |

Not modifying: `pyproject.toml`, `tests/test_smoke.py`,
`src/qec_project/linalg.py`, `src/qec_project/__init__.py`, or
`phase-00-foundations/README.md`.

### Promoted helpers — justification

- `bsc_flip(bits, p, rng)`: Phase 0.3 immediately needs to send Hamming
  codewords through a BSC and Phase 3+ needs a classical-channel point
  of comparison for the surface code under bit-flip noise. Two callers
  inside one phase is already enough; promotion now beats copy-paste
  later.
- `binary_entropy(p)` and `bsc_capacity(p)`: the capacity curve recurs
  whenever a noise channel is benchmarked against the Shannon limit.
  Both are tiny and trivially testable.

### Public signatures (with type hints)

```python
# src/qec_project/noise/classical.py
def bsc_flip(
    bits: np.ndarray,
    p: float,
    rng: np.random.Generator,
) -> np.ndarray: ...

# src/qec_project/info.py
def binary_entropy(p: float | np.ndarray) -> float | np.ndarray: ...
def bsc_capacity(p: float | np.ndarray) -> float | np.ndarray: ...
```

`bsc_flip` returns a new array of the same shape/dtype as `bits` with
each bit independently flipped with probability `p`. `binary_entropy(0)`
and `binary_entropy(1)` return 0 by the standard `0 log 0 = 0`
convention. Log base 2 throughout; capacity is in bits per channel use.

## Tests added

### `tests/test_classical_noise.py`

1. `test_bsc_flip_p_zero_returns_unchanged` — `p=0` leaves bits identical.
2. `test_bsc_flip_p_one_returns_complement` — `p=1` flips every bit.
3. `test_bsc_flip_preserves_shape_and_dtype` — output shape and dtype match
   input.
4. `test_bsc_flip_is_deterministic_given_seed` — same `rng` seed yields
   identical output across two calls.
5. `test_bsc_flip_independent_of_input_for_random_p` — flip pattern is
   the same regardless of input bit values (XOR property).
6. `test_bsc_flip_rejects_out_of_range_p` — `p < 0` or `p > 1` raises
   `ValueError`.
7. (hypothesis) `test_bsc_flip_empirical_rate_concentrates_on_p` — for
   `N=20000` bits and `p` drawn from `[0.01, 0.49]`, the empirical flip
   rate is within `5/sqrt(N)` of `p`.

### `tests/test_info.py`

1. `test_binary_entropy_at_zero_and_one_is_zero` — `H_2(0) = H_2(1) = 0`.
2. `test_binary_entropy_at_half_is_one` — `H_2(0.5) = 1.0` exactly to
   tolerance.
3. `test_binary_entropy_symmetric` — `H_2(p) = H_2(1-p)`.
4. `test_bsc_capacity_at_zero_is_one` — `C(0) = 1.0`.
5. `test_bsc_capacity_at_half_is_zero` — `C(0.5) = 0.0` to tolerance.
6. `test_bsc_capacity_vectorised` — `bsc_capacity(np.array([...]))`
   returns the elementwise values.
7. `test_entropy_rejects_out_of_range_p` — `p < 0` or `p > 1` raises
   `ValueError`.
8. (hypothesis) `test_entropy_in_zero_one` — for `p in [0, 1]`, the
   binary entropy lies in `[0, 1]`.

## Acceptance criteria

- `python -m uv run pytest` returns 0; total tests >= 16 (existing) + >= 15
  new = 31 or more.
- `python -m uv run ruff check .` returns 0 findings.
- `python -m uv run jupyter nbconvert --to notebook --execute
  phase-00-foundations/02-probability/probability.ipynb --output _check.ipynb`
  runs to completion without error.
- `python scripts/verify_reading_list.py` exits 0 after the Shannon 1948
  entry is added.
- Notebook sets `np.random.default_rng(0)` in its first code cell and
  uses no other seeds.
- Notebook contains all six required sections: discrete-probability
  primer, conditional + Bayes, mutual information, Markov chains, BSC
  capacity + plot, BSC simulation + plot.
- `CHANGELOG.md` `## Completed milestones` has a new 2026-05-14 Phase
  0.2 entry; `## Current status` points the next session at Phase 0.3.

## Tasks (2-5 minute units, ordered)

1. Write `src/qec_project/info.py` with `binary_entropy` and
   `bsc_capacity`.
2. Write `src/qec_project/noise/classical.py` with `bsc_flip`.
3. Write `tests/test_info.py` and `tests/test_classical_noise.py`. Run
   `python -m uv run pytest tests/test_info.py tests/test_classical_noise.py -x`;
   iterate until green.
4. `python -m uv run ruff check src tests` and fix.
5. Add Shannon 1948 entry to `docs/reading-list.md` and run
   `python scripts/verify_reading_list.py`.
6. Write `_build_notebook.py` for Phase 0.2; run it once to emit
   `probability.ipynb`.
7. Execute the notebook end-to-end via `nbconvert --execute`. Iterate
   until clean.
8. Write `phase-00-foundations/02-probability/README.md`.
9. Final sweep: `pytest`, `ruff`, `verify_reading_list.py`.
10. Append CHANGELOG milestone; update Current status to Phase 0.3.
11. Commit with `Phase 0.2: probability notebook + BSC capacity + simulation`.

## Out-of-band notes

- `uv` is not on PATH on this machine; `python -m uv run ...` is the
  working invocation. Same as Phase 0.1.
- Shannon's 1948 paper has DOI `10.1002/j.1538-7305.1948.tb01338.x`
  (Bell System Technical Journal). Adding it to the reading list
  satisfies the integrity rule for the capacity formula.
- The em-dash ban in the *other* CLAUDE.md (stellar-mk-audit) does
  **not** apply here. Normal punctuation is allowed.
