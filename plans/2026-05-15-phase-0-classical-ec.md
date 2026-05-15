# Plan: Phase 0 — Classical error correction promotion

Date: 2026-05-15. Branch: `claude/deploy-multiple-agents-915lI`.

Scope: promote Hamming(7,4) + 3-repetition code from notebook prototype to
tested `src/qec_project/codes/classical.py`, plus an executed notebook
showing BSC logical error-rate curves.

## Tasks

- [ ] Write `tests/test_classical.py` (RED): matrix algebra identities,
      encode/decode round-trip, exhaustive single-bit correction, 2-bit
      sanity, BSC simulator bounds + loose monotonicity (hypothesis).
- [ ] Implement `src/qec_project/codes/classical.py` with `hamming74_*`
      helpers, `encode`, `syndrome`, `decode`, `simulate_bsc`, and a
      `RepetitionCode` helper class (n=3 majority decode + BSC sim).
- [ ] Lint + test: `uv run ruff check` and `uv run pytest` green.
- [ ] Build `phase-00-foundations/03-classical-ec/hamming_bsc.ipynb`
      programmatically via `nbformat` + `nbclient.execute()`, sweep
      `p_flip` over 10 points in [0.01, 0.3] with n_shots=50_000 and
      seed=12345, plot lin-lin + log-log, print table.
- [ ] Run the full test suite to confirm no regressions; report
      crossing point between Hamming(7,4) and 3-rep curves.

## Notes

- Standard Hamming(7,4) systematic form: parity bits at positions 5,6,7
  (1-indexed) with `H` matching `G H^T = 0 (mod 2)`.
- Block (logical) error = any decoded bit differs from original message.
- Repetition code BSC: probability of >=2 bit flips out of 3 yields a
  logical error after majority vote.
