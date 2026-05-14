# Phase 0.2 — Discrete probability and the binary symmetric channel

The second content notebook of the curriculum. Builds the probability +
information-theory vocabulary that QEC papers assume and lands at the
binary symmetric channel (BSC), the simplest classical noise model. The
BSC is exactly what Phase 0.3 will send Hamming(7,4) codewords through;
recognising the same picture later in Phase 3 for the surface code under
bit-flip noise is the point of doing this now.

## What it covers

1. Discrete probability primer: random variable, PMF, expectation,
   variance — verified by sampling a biased coin.
2. Conditional probability and Bayes' rule — a single-bit noisy-channel
   example computing `P(X | Y)` from `P(Y | X)` and the prior.
3. Mutual information `I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)` computed
   three ways from one toy joint distribution, all agreeing — and
   shown to equal `1 - H_2(p)` for the BSC-with-uniform-prior example.
4. Two-state Markov chain: stationary distribution found by iteration
   and as a left eigenvector of `P` with eigenvalue 1. Used as a
   vocabulary bridge to memoryful channel models.
5. Binary symmetric channel BSC(p): Shannon capacity
   `C(p) = 1 - H_2(p)` plotted across `p ∈ [0, 1]`. Spot-checks confirm
   `C(0) = 1`, `C(0.5) = 0`.
6. Monte Carlo simulation: `N = 10000` bits sent through BSC(p) for
   `p ∈ {0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5}`. Empirical flip rates
   land inside the `+/- 1/sqrt(N)` band.

The notebook reuses two small helpers promoted to `src/qec_project/`:

- `qec_project.info.binary_entropy(p)` and `qec_project.info.bsc_capacity(p)`
- `qec_project.noise.classical.bsc_flip(bits, p, rng)`

Their tests are in `tests/test_info.py` and `tests/test_classical_noise.py`.

## How to run

From the repo root:

```bash
uv sync --extra dev
uv run jupyter lab phase-00-foundations/02-probability/probability.ipynb
```

Or non-interactively:

```bash
uv run jupyter nbconvert --to notebook --execute \
    phase-00-foundations/02-probability/probability.ipynb \
    --output _check.ipynb
```

A fixed seed (`np.random.default_rng(0)`) is set in the first code cell;
the notebook is deterministic across runs.

`_build_notebook.py` in this directory is the source from which the
notebook is generated. Edit it (not the `.ipynb` directly) when the
notebook structure needs to change, then re-run it.

## After reading this you should be able to

- Compute the expectation and variance of a discrete random variable
  from its PMF and verify by sampling.
- Apply Bayes' rule to invert a single-bit noisy channel.
- Compute `H(X)`, `H(X|Y)`, `H(Y|X)`, and `I(X;Y)` from a joint
  distribution, and recognise the equivalent formulations.
- Find the stationary distribution of a two-state Markov chain two
  different ways and explain why they agree.
- State the BSC capacity formula `C(p) = 1 - H_2(p)`, predict its
  behaviour at `p = 0`, `p = 1/2`, `p = 1`, and produce a Monte Carlo
  estimate of the empirical flip rate.

## References

Both are in `docs/reading-list.md`:

- MacKay, *Information Theory, Inference, and Learning Algorithms*,
  Cambridge, 2003 — chapters 1-2 (probability primer) and chapter 9
  (BSC; noisy-channel coding theorem statement).
- C. E. Shannon. *A Mathematical Theory of Communication.* Bell System
  Technical Journal 27 (1948).
  doi:`10.1002/j.1538-7305.1948.tb01338.x`. The original capacity paper.
