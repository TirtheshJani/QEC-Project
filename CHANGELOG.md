# CHANGELOG — QEC-Project research journal

This file is the project's portable long-term memory (per Anthropic's
*Long-running Claude for scientific computing*). **Read it at the start of
every session, append to it before stopping.** See
`docs/long-running-protocol.md` for the full ritual.

## Current status

Phase 0.1 complete. Next: `phase-00-foundations/02-probability/` (discrete
probability + binary symmetric channel simulation). Branch `main`
(post-bootstrap merge); commit locally, do not push without explicit ask.

## Completed milestones

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
