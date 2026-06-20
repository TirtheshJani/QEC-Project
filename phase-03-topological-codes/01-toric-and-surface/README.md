# Phase 3.1 — The rotated surface code

**Goal.** Construct the rotated surface code $[[d^2,1,d]]$ programmatically at
$d \in \{3,5,7\}$, inspect its memory circuit, visualise the check lattice, and
build the decomposed detector error model (DEM) that every decoder consumes.

**Notebook.** [`toric_and_surface.ipynb`](toric_and_surface.ipynb) — built from
`_build_notebook.py`; uses `qec_project.codes.surface.RotatedSurfaceCode`.

**Run.**
```bash
uv run python phase-03-topological-codes/01-toric-and-surface/_build_notebook.py
uv run jupyter nbconvert --to notebook --execute --inplace \
    phase-03-topological-codes/01-toric-and-surface/toric_and_surface.ipynb
```

**References** (`docs/reading-list.md`): Fowler et al. 2012 (arXiv:1208.0928);
Gidney, *Stim* (doi:10.22331/q-2021-07-06-497).
