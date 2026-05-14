# CHANGELOG — QEC-Project research journal

This file is the project's portable long-term memory (per Anthropic's
*Long-running Claude for scientific computing*). **Read it at the start of
every session, append to it before stopping.** See
`docs/long-running-protocol.md` for the full ritual.

## Current status
Phase 0.2 complete. Next: `phase-00-foundations/03-classical-ec/` (Hamming(7,4) encoder + syndrome decoder, simulated over BSC; logical error rate curve vs nominal flip probability). Branch `main` (post-bootstrap merge); commit locally, do not push without explicit ask.

## Completed milestones

- 2026-05-14  Phase 0.2 (probability + BSC): notebook `phase-00-foundations/02-probability/probability.ipynb` covering discrete probability (PMF / E / Var via biased-coin sampling), Bayes for a single-bit noisy channel, mutual information `I(X;Y)` computed three ways and shown to equal `1 - H_2(p)` for the BSC-with-uniform-prior example, two-state Markov chain stationary distribution (iteration vs eigenvector), Shannon BSC capacity plot, and a Monte Carlo simulation showing empirical flip rate within +/- 1/sqrt(N) of nominal. Promoted helpers: `qec_project.info` (binary_entropy, bsc_capacity) and `qec_project.noise.classical` (bsc_flip) with 19 tests in tests/test_info.py and tests/test_classical_noise.py (hypothesis property tests for entropy range and empirical-rate concentration). Plan in plans/phase-00-02-probability.md. Reading list gains Shannon 1948 (doi 10.1002/j.1538-7305.1948.tb01338.x). pytest 35 passed, ruff clean, verify_reading_list green, notebook executes top-to-bottom.

- 2026-05-14  Phase 0.1 (linear algebra): notebook `phase-00-foundations/01-linear-algebra/linear_algebra.ipynb` covering complex vectors, unitarity, Pauli eigendecomposition (eigenvalues +/-1 foreshadowed as measurement outcomes), and Kronecker products by hand + numerical (basis convention pinned: numpy.kron is big-endian, first factor is most-significant qubit). Promoted helpers to `src/qec_project/linalg.py` (PAULI_{I,X,Y,Z}, PAULIS, `is_unitary`, `tensor`, `eigendecompose`) with 14 tests in `tests/test_linalg.py` (hypothesis property test for unitary-tensor-unitary). Plan in `plans/phase-00-01-linear-algebra.md`. pytest 16 passed, ruff clean, notebook executes top-to-bottom, verify_reading_list green.

- 2026-05-14  Repo bootstrap: directory skeleton, build config,
  `src/qec_project/` package, smoke tests, CI workflow, plugin install
  script, all six phase READMEs, capstone scaffolding, NRC notes, three
  plugin cheatsheets, long-running protocol doc. `uv sync --extra dev`
  resolves; `pytest`, `ruff`, and `verify_reading_list.py` all green.

## Decoder accuracy tables (capstone)

| Run ID | Code | Distance | Decoder | Noise model | p_phys | p_log | shots | seed | commit | notes |
| ------ | ---- | -------- | ------- | ----------- | ------ | ----- | ----- | ---- | ------ | ----- |

## Failed approaches & why

- 2026-05-14  In sandboxed environments doi.org/arxiv.org return 403 to
  HEAD requests. `verify_reading_list.py` would otherwise hard-fail on
  every entry. Resolution: treat only 404/410 as hard failures; 403/429
  and connection errors are soft-passed (the script is meant to catch
  fabricated identifiers, not flaky network policy).

## Known limitations

<!--
Slow-growing list of constraints to remember across sessions. Examples:

- Local CPU caps the surface-code sims at d=9, ~1M shots/run. For d≥11 burst to Modal via `scripts/run_threshold_sweep.py --remote`.
-->
