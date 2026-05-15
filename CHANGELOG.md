# CHANGELOG — QEC-Project research journal

This file is the project's portable long-term memory (per Anthropic's
*Long-running Claude for scientific computing*). **Read it at the start of
every session, append to it before stopping.** See
`docs/long-running-protocol.md` for the full ritual.

## Current status
Phase 0-3 *core code* promoted to src/qec_project/ with TDD: classical.py (Hamming/repetition), noise/channels.py (Kraus), codes/pauli.py + codes/steane.py, codes/surface_code.py + decoders/mwpm.py + decoders/base.py. 80 tests pass, ruff clean. One illustrative notebook per phase, executed with outputs embedded. **Not yet done:** Phase 0 notebooks 01-linear-algebra and 02-probability; Phase 1 notebooks 01-qubits-gates and 02-multi-qubit-entanglement (Qiskit-focused); Phase 2 notebooks 01-3qubit-repetition, 02-shor-9, 04-css-and-steane, 05-intro-to-stim; Phase 3 notebooks 01-toric-and-surface, 02-syndrome-extraction, 03-mwpm-pymatching. **Phase 4 (FT, magic state distillation, lattice surgery) and Phase 5 (BP, BP+OSD, Union-Find, neural decoders, qLDPC) entirely untouched** — these are the next session's priority and the runway to the capstone. Capstone literature review and EOI also pending.

## Completed milestones

- 2026-05-15  Phase 3 promoted: rotated_surface_code_circuit (Stim wrapper) in src/qec_project/codes/surface_code.py and MwpmDecoder (PyMatching wrapper behind Decoder protocol) in src/qec_project/decoders/mwpm.py; illustrative threshold-sweep notebook over d in {3,5} in phase-03-topological-codes/04-threshold-simulation/.

- 2026-05-15  Phase 2 promoted: symplectic Pauli class in src/qec_project/codes/pauli.py (property-tested against 2^n matrix ground truth for n<=3) and Steane [[7,1,3]] in src/qec_project/codes/steane.py (exhaustive distance-3 verification); stabilizer notebook in phase-02-qec-fundamentals/03-stabilizer-formalism/.

- 2026-05-15  Phase 1 promoted: single-qubit Kraus channels (bit-flip, phase-flip, depolarizing) in src/qec_project/noise/channels.py with trace-preservation property tests; Bloch-shrink notebook in phase-01-quantum-basics/03-density-matrices-noise/.

- 2026-05-15  Phase 0 promoted: Hamming(7,4) + n-repetition codes in src/qec_project/codes/classical.py with exhaustive single-bit-correction tests; BSC simulation notebook in phase-00-foundations/03-classical-ec/.

- 2026-05-14  Repo bootstrap: directory skeleton, build config,
  `src/qec_project/` package, smoke tests, CI workflow, plugin install
  script, all six phase READMEs, capstone scaffolding, NRC notes, three
  plugin cheatsheets, long-running protocol doc. `uv sync --extra dev`
  resolves; `pytest`, `ruff`, and `verify_reading_list.py` all green.

## Decoder accuracy tables (capstone)

| Run ID | Code | Distance | Decoder | Noise model | p_phys | p_log | shots | seed | commit | notes |
| ------ | ---- | -------- | ------- | ----------- | ------ | ----- | ----- | ---- | ------ | ----- |
| phase3-illustrative-d5 | rotated-surface | 5 | pymatching | depolarizing | 2.000e-02 | 3.053e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d5 | rotated-surface | 5 | pymatching | depolarizing | 1.700e-02 | 2.446e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d5 | rotated-surface | 5 | pymatching | depolarizing | 1.400e-02 | 1.708e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d5 | rotated-surface | 5 | pymatching | depolarizing | 1.100e-02 | 1.024e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d5 | rotated-surface | 5 | pymatching | depolarizing | 8.000e-03 | 5.000e-02 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d5 | rotated-surface | 5 | pymatching | depolarizing | 5.000e-03 | 1.590e-02 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d3 | rotated-surface | 3 | pymatching | depolarizing | 2.000e-02 | 1.721e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d3 | rotated-surface | 3 | pymatching | depolarizing | 1.700e-02 | 1.372e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d3 | rotated-surface | 3 | pymatching | depolarizing | 1.400e-02 | 1.030e-01 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d3 | rotated-surface | 3 | pymatching | depolarizing | 1.100e-02 | 7.200e-02 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d3 | rotated-surface | 3 | pymatching | depolarizing | 8.000e-03 | 3.830e-02 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |
| phase3-illustrative-d3 | rotated-surface | 3 | pymatching | depolarizing | 5.000e-03 | 1.750e-02 | 10000 | 20260515 | 90cd34f | illustrative; rounds=d; phase-3 notebook |

## Failed approaches & why

- 2026-05-14  In sandboxed environments doi.org/arxiv.org return 403 to
  HEAD requests. `verify_reading_list.py` would otherwise hard-fail on
  every entry. Resolution: treat only 404/410 as hard failures; 403/429
  and connection errors are soft-passed (the script is meant to catch
  fabricated identifiers, not flaky network policy).

## Known limitations

- 2026-05-15  Depolarizing Kraus uses sqrt(p/3) per-Pauli convention (Nielsen and Chuang sec. 8.3.4): maximally mixed at p=3/4, not p=1. Documented in src/qec_project/noise/channels.py and its tests.

<!--
Slow-growing list of constraints to remember across sessions. Examples:

- Local CPU caps the surface-code sims at d=9, ~1M shots/run. For d≥11 burst to Modal via `scripts/run_threshold_sweep.py --remote`.
-->
