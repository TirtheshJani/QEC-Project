# Capstone experiments — rotated surface code decoder benchmark

Each `sweep-<date>-<decoder>-<noise>/` directory is one reproducible Monte-Carlo
sweep written by `scripts/run_threshold_sweep.py`:

- `stats.csv` — one row per `(distance, p_phys)` cell:
  `decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit`.
- `run.json` — provenance manifest (argv, seed, commit SHA, library versions, timestamp).

Sampling is **in-process** (Stim → PyMatching / ldpc BP+OSD), explicitly seeded per
cell, and resumable: re-running an identical command tops each cell up to `--shots`.
(`sinter.collect` is bypassed — it is incompatible with NumPy 2.x in the locked
environment; see `CHANGELOG.md` → "Failed approaches".)

## Reproduce

```bash
uv sync --extra dev

# MWPM (PyMatching) — fast; full distance set
uv run python scripts/run_threshold_sweep.py \
    --decoder pymatching --noise depolarizing \
    --distances 3 5 7 \
    --p-phys 0.002 0.003 0.005 0.007 0.01 0.013 0.016 0.02 0.025 \
    --shots 20000 --max-errors 2000 --seed 42 --changelog

# BP+OSD (ldpc) — ~10^3x slower per shot; d <= 5 for tractable local CPU runtime
uv run python scripts/run_threshold_sweep.py \
    --decoder bp-osd --noise depolarizing \
    --distances 3 5 \
    --p-phys 0.002 0.003 0.005 0.007 0.01 0.013 0.016 0.02 0.025 \
    --shots 20000 --max-errors 2000 --seed 42 --changelog

# Figures + summary.json (estimated threshold, fit p_th, Λ ratios)
uv run python scripts/make_figures.py \
    capstone/experiments/*/stats.csv --noise depolarizing
```

Figures land in `capstone/figures/`; headline numbers in `capstone/figures/summary.json`
and `CHANGELOG.md`'s accuracy table.

## Noise model

`depolarizing` sets all four `stim.Circuit.generated` knobs equal to `p`
(`after_clifford_depolarization`, `after_reset_flip_probability`,
`before_measure_flip_probability`, `before_round_data_depolarization`) — a uniform
circuit-level depolarizing model. The measured threshold is specific to this model
and is **not** directly comparable to published asymmetric circuit-level (e.g. SI1000)
thresholds; it is a controlled, identical baseline for the decoder *comparison*.
