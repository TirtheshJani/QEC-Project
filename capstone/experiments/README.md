# Capstone experiments — rotated surface code decoder benchmark

Each `sweep-<date>-<decoder>-<noise>/` directory is one reproducible Monte-Carlo
sweep written by `scripts/run_threshold_sweep.py`:

- `stats.csv` — one row per `(distance, p_phys)` cell:
  `decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit`.
- `run.json` — provenance manifest (argv, seed, commit SHA, library versions, timestamp).

The committed data is `sweep-2026-06-19-*`. The two `rerun-2026-09-26-*` directories
hold a rerun of the two commands below at 1218c55 (with `--workers 2` and `--run-id`),
kept for comparison. The README commands and the Phase 3.4 notebook name the
`sweep-2026-06-19-*` directories, so they do not pick up the rerun.

Sampling is **in-process** (Stim → PyMatching / ldpc BP+OSD), explicitly seeded per
cell, and resumable: re-running an identical command tops each cell up to `--shots`.
(`sinter.collect` is bypassed — it is incompatible with NumPy 2.x in the locked
environment; see `CHANGELOG.md` → "Failed approaches".)

Seeding: until 2026-09-26 the per-cell Stim seed mixed in Python's `hash(decoder)`,
which changes from process to process, so the committed 2026-06-19 `stats.csv` files
cannot be regenerated bit for bit. The seed now uses a CRC32 of the decoder name, so
rerunning a command below gives identical counts (Stim guarantees this for the same
Stim version on machines with the same SIMD width). The committed rerun agrees with the
committed counts within binomial error. The committed counts do come from this harness:
with the per-process salts recovered by brute force, it regenerates all 27 MWPM cells
and the 10 BP+OSD cells at $p \le 0.01$ exactly. Each committed `stats.csv` was
written by two invocations (the $p \le 0.01$ grid, then $p \ge 0.013$) from the
uncommitted tree that became 725c700, but its `run.json` records only the last
invocation: one full-grid command stamped 678ee59, a commit that has no harness yet.
See the 2026-09-26 entries in `CHANGELOG.md`.

## Reproduce

```bash
uv sync --extra dev

# Each run writes capstone/experiments/sweep-<today>-<decoder>-<noise>/. --changelog
# appends accuracy rows to CHANGELOG.md; drop it when you are only checking.

# MWPM (PyMatching) — fast; full distance set
uv run python scripts/run_threshold_sweep.py \
    --decoder pymatching --noise depolarizing \
    --distances 3 5 7 \
    --p-phys 0.002 0.003 0.005 0.007 0.01 0.013 0.016 0.02 0.025 \
    --shots 20000 --max-errors 2000 --seed 42 --changelog

# BP+OSD (ldpc) — ~590x the time per shot of MWPM at d=5; d <= 5 for tractable local CPU runtime
uv run python scripts/run_threshold_sweep.py \
    --decoder bp-osd --noise depolarizing \
    --distances 3 5 \
    --p-phys 0.002 0.003 0.005 0.007 0.01 0.013 0.016 0.02 0.025 \
    --shots 20000 --max-errors 2000 --seed 42 --changelog

# Figures + summary.json (estimated threshold, fit p_th, Λ ratios) from the committed
# sweeps. To plot a rerun, pass its stats.csv files instead; make_figures.py warns if
# two inputs contain the same (decoder, distance, p) cell.
uv run python scripts/make_figures.py \
    capstone/experiments/sweep-2026-06-19-*/stats.csv --noise depolarizing
```

Figures land in `capstone/figures/`; headline numbers in `capstone/figures/summary.json`
and `CHANGELOG.md`'s accuracy table. The `lambda` in `summary.json` is taken at the
lowest $p$ both distances share, which is the lowest swept $p$ (0.002) here, and
`lambda_p_phys` records it. Those cells hold few logical errors (5 to 49). The $\Lambda$
values in the top-level README come from `scripts/lambda_interval.py` at $p = 0.005$.

## Noise model

`depolarizing` sets all four `stim.Circuit.generated` knobs equal to `p`
(`after_clifford_depolarization`, `after_reset_flip_probability`,
`before_measure_flip_probability`, `before_round_data_depolarization`) — a uniform
circuit-level depolarizing model. The measured threshold is specific to this model
and is **not** directly comparable to published asymmetric circuit-level (e.g. SI1000)
thresholds; it is a controlled, identical baseline for the decoder *comparison*.
