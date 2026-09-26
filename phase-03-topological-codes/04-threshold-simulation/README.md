# Phase 3.4 — Threshold simulation & the decoder benchmark

**Goal.** Turn Phase 3 into the capstone: load the production sweeps, reproduce the
threshold-crossing plot, extract $p_\mathrm{th}$ and $\Lambda$, and put **MWPM vs
BP+OSD** head to head on accuracy *and* latency.

**Notebook.** [`threshold_simulation.ipynb`](threshold_simulation.ipynb) — built from
`_build_notebook.py`; uses `qec_project.analysis.threshold` and the CSVs in
`capstone/experiments/`.

**Headline result** (uniform depolarizing noise, seed 42; see
`capstone/figures/summary.json` and `CHANGELOG.md`):

| Decoder | $p_\mathrm{th}$ (fit, per round) | time per shot, sampling + decoding @ d=5 | accuracy @ d=5, p=0.005 |
| --- | --- | --- | --- |
| MWPM (PyMatching) | $0.0122 \pm 0.0013$ ($d=3,5,7$) | ~9 µs | $p_L = 3.0\times10^{-3}$ |
| BP+OSD (ldpc) | $0.0134 \pm 0.0015$ ($d=3,5$) | ~5400 µs | $p_L = 1.9\times10^{-3}$ |

The fitted thresholds overlap within fit error. BP+OSD's measured edge is lower $p_L$
at $d=5$: 11 to 35% lower per shot for $p = 0.003$ to $0.01$ (35% at $p = 0.005$;
two-proportion $z > 2$ only for $p = 0.005$ to $0.02$, on unpaired samples), and it
takes about 600× as long per shot at $d=5$ (587× in the committed sweep, 719× in the
committed rerun): the accuracy/latency frontier the capstone studies. See the top-level `README.md` for
$\Lambda$ with intervals and what the timing measures.

**Run.**
```bash
# reads the committed sweeps in capstone/experiments/sweep-2026-06-19-*/
uv run python phase-03-topological-codes/04-threshold-simulation/_build_notebook.py
uv run jupyter nbconvert --to notebook --execute --inplace \
    phase-03-topological-codes/04-threshold-simulation/threshold_simulation.ipynb
```

**References** (`docs/reading-list.md`): Fowler et al. 2012 (arXiv:1208.0928);
Higgott & Gidney (arXiv:2303.15933); Roffe et al. 2020
(doi:10.1103/PhysRevResearch.2.043423).
