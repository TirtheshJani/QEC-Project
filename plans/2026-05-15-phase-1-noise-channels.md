# Plan: Phase 1 — Single-qubit noise channels

Date: 2026-05-15. Branch: `claude/deploy-multiple-agents-915lI`.

Scope: implement single-qubit Kraus channels (bit-flip, phase-flip,
depolarizing) in `src/qec_project/noise/channels.py`, test-driven, and
build an executed notebook showing Bloch-vector contraction.

## Tasks

- [ ] Write `tests/test_channels.py` (RED): trace preservation across
      p in {0, 0.1, 0.5, 1.0}; bit-flip extremes on |0><0|; depolarizing
      p=1 -> I/2 for sampled pure states; Kraus sum == mixture form for
      depolarizing; hypothesis-style property with seeded RNG that
      apply_channel preserves trace and Hermiticity on random density
      matrices (runtime < 2 s).
- [ ] Implement `src/qec_project/noise/channels.py`: Pauli matrices,
      `bit_flip_kraus`, `phase_flip_kraus`, `depolarizing_kraus`,
      `apply_channel`, `is_trace_preserving`,
      `composed_depolarizing_probabilities`. Strict type hints, no
      emojis, comments only where the *why* is non-obvious.
- [ ] `uv run ruff check` + `uv run pytest tests/test_channels.py`
      green.
- [ ] Build `phase-01-quantum-basics/03-density-matrices-noise/kraus_channels.ipynb`
      programmatically via `nbformat` + `nbclient.execute()` (seed
      RNG=20260515). Three subplots of Bloch-vector length r(p) for
      p in [0, 1] starting from |+>; final cell prints the trace
      distance between the depolarizing output at p=1 and I/2.
- [ ] Run full `uv run pytest` to confirm no regressions.

## Notes

- Standard depolarizing channel: K0 = sqrt(1-p) I, K_{X,Y,Z} = sqrt(p/3) P.
  This contracts the Bloch vector by factor (1 - 4p/3) (see Nielsen &
  Chuang Ch. 8.3); r=0 at p=3/4 and the channel maps everything to I/2
  at that point. Note our convention: p in [0, 1] with p=1 placing full
  weight 1/3 on each Pauli — at p=1 the output of |+> is
  (1/3)(I + (1 - 4/3) X) which still has r = |1 - 4/3| = 1/3, not 0.
  The "maps to I/2 at p=1" requirement therefore must be tested using
  the *mixture* convention `(1-p) rho + p I/2`, and we cross-check
  the Kraus form matches that mixture form at p=3/4 only. We'll test
  the Kraus channel against the equivalent mixture form
  `(1 - 4p/3) rho + (4p/3) I/2` to handle this cleanly.
</content>
</invoke>