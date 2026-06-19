# Phase 3.4 — Threshold simulation & the decoder benchmark

**Goal.** Turn Phase 3 into the capstone: load the production sweeps, reproduce the
threshold-crossing plot, extract $p_\mathrm{th}$ and $\Lambda$, and put **MWPM vs
BP+OSD** head to head on accuracy *and* latency.

**Notebook.** [`threshold_simulation.ipynb`](threshold_simulation.ipynb) — built from
`_build_notebook.py`; uses `qec_project.analysis.threshold` and the CSVs in
`capstone/experiments/`.

**Headline result** (uniform depolarizing noise, seed 42; see
`capstone/figures/summary.json` and `CHANGELOG.md`):

| Decoder | $p_\mathrm{th}$ (fit) | $\Lambda_{3\to5}$ | latency @ d=5 | accuracy @ d=5, p=0.005 |
| --- | --- | --- | --- | --- |
| MWPM (PyMatching) | $0.0122 \pm 0.0013$ | 5.8 | ~9 µs/shot | $p_L = 3.0\times10^{-3}$ |
| BP+OSD (ldpc) | $0.0134 \pm 0.0015$ | 6.3 | ~5400 µs/shot | $p_L = 1.9\times10^{-3}$ |

BP+OSD is the more accurate decoder (higher threshold, ~35% lower $p_L$) but ~600×
slower at $d=5$ — the accuracy/latency frontier the capstone studies.

**Run.**
```bash
# produce the sweeps + figures first (see capstone/experiments/README.md), then:
uv run python phase-03-topological-codes/04-threshold-simulation/_build_notebook.py
uv run jupyter nbconvert --to notebook --execute --inplace \
    phase-03-topological-codes/04-threshold-simulation/threshold_simulation.ipynb
```

**References** (`docs/reading-list.md`): Fowler et al. 2012 (arXiv:1208.0928);
Higgott & Gidney (arXiv:2303.15933); Roffe et al. 2020
(doi:10.1103/PhysRevResearch.2.043423).
