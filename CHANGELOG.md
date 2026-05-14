# CHANGELOG — QEC-Project research journal

This file is the project's portable long-term memory (per Anthropic's
*Long-running Claude for scientific computing*). **Read it at the start of
every session, append to it before stopping.** See
`docs/long-running-protocol.md` for the full ritual.

## Current status

Phase 0 and Phase 1 both complete. Phase 0 (foundations: linear algebra, probability + BSC, classical EC with Hamming(7,4) over BSC) and Phase 1 (quantum basics: qubits + Cliffords, Bell/superdense/teleportation in Qiskit, density matrices + Kraus channels) were built in parallel worktrees on 2026-05-14 and merged together. Next: `phase-02-qec-fundamentals/` (stabilizer formalism, Pauli group machinery; Steane will reuse `qec_project.codes.classical.Hamming74`, the stabilizer simulator will reuse `qec_project.noise.quantum` Kraus channels). Branch `main`; commit locally, do not push without explicit ask.

## Completed milestones

- 2026-05-14  Phase 1 (quantum basics): three notebooks under `phase-01-quantum-basics/`. 1.1 `01-qubits-gates/qubits_gates.ipynb` covers single-qubit state space, global vs relative phase (Born-rule probabilities cross-checked), the six cardinal Bloch-sphere states plotted on a matplotlib wireframe (no qutip dependency), the single-qubit Cliffords `H, S, X, Y, Z` with unitarity check via `qec_project.linalg.is_unitary`, and the `H Z H = X` identity verified algebraically (markdown) and numerically. 1.2 `02-multi-qubit-entanglement/multi_qubit.ipynb` brings Qiskit + qiskit-aer into the curriculum: basis-ordering reconciliation (`numpy.kron` big-endian vs Qiskit little-endian), all four Bell states constructed two ways with Statevector cross-check, superdense coding with 1000 shots per message decoding correctly for all four 2-bit messages, and standard 3-qubit teleportation with `if_test` classical feed-forward verified to fidelity 1.0. 1.3 `03-density-matrices-noise/density_kraus.ipynb` covers density operators (pure/mixed/purity), partial trace (Bell-state marginals = I/2), and the three single-qubit Kraus channels (bit-flip, phase-flip, depolarizing with Nielsen-Chuang Eq. 8.102 form) with trace-preservation checks and analytic-form verification. Promoted helpers in 1.3: `qec_project.noise.quantum` (Kraus constructors + channel functions + `is_trace_preserving`) and `qec_project.analysis.density` (`is_density_matrix`, `partial_trace`), 29 new tests in `tests/test_quantum_noise.py` and `tests/test_density.py` (hypothesis property tests for random-density validity under each channel and for partial-trace of random 4x4 densities). Plans in `plans/phase-01-0{1,2,3}-*.md`. No new reading-list entries (Nielsen-Chuang already present). pytest 64 passed, ruff clean, all three notebooks execute top-to-bottom.

- 2026-05-14  Phase 0.3 (classical error correction): notebook `phase-00-foundations/03-classical-ec/classical_ec.ipynb` covering linear codes (generator G, parity-check H, the (n, k, d) tuple), the repetition (3, 1, 3) code with majority-vote decoding and closed-form logical error rate `3 p^2 - 2 p^3` verified by Monte Carlo, and the Hamming (7, 4, 3) code with explicit systematic G (4 by 7) and H (3 by 7), syndrome-table decoding exhaustively verified against all 16 messages times 7 single-bit errors (112 cases). Headline log-log plot of logical error rate vs physical flip probability for uncoded / rep(3,1) / Hamming(7,4) over BSC(p) at p in {0.01, 0.05, 0.1, 0.2, 0.3, 0.4} with N=10000 trials each; closed-form Hamming block-error curve `1 - (1-p)^7 - 7 p (1-p)^6` overlaid. Plot shape foreshadows Phase 3 threshold picture. Promoted helpers: `qec_project.codes.classical` with RepetitionCode(n) and Hamming74 (encode / syndrome / decode / extract_message / syndrome_table) with 20 tests in tests/test_classical_codes.py (hypothesis property tests for monotonicity of logical error rate in p). Plan in plans/phase-00-03-classical-ec.md. Reading list gains Hamming 1950 (doi 10.1002/j.1538-7305.1950.tb00463.x). pytest 55 passed, ruff clean, verify_reading_list green, notebook executes top-to-bottom.

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
