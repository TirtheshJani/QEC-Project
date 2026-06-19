# Phase 3.2 — Syndrome extraction & detectors

**Goal.** Understand the detector stream a decoder actually sees: inter-round
stabilizer parities. Verify the noiseless circuit fires no detectors, then show how
detection density and the undecoded logical-flip rate scale with the physical error
rate.

**Notebook.** [`syndrome_extraction.ipynb`](syndrome_extraction.ipynb) — built from
`_build_notebook.py`; uses `qec_project.codes.surface.RotatedSurfaceCode`.

**Run.**
```bash
uv run python phase-03-topological-codes/02-syndrome-extraction/_build_notebook.py
uv run jupyter nbconvert --to notebook --execute --inplace \
    phase-03-topological-codes/02-syndrome-extraction/syndrome_extraction.ipynb
```

**References** (`docs/reading-list.md`): Fowler et al. 2012 (arXiv:1208.0928);
Gidney, *Stim* (doi:10.22331/q-2021-07-06-497).
