# Phase 3.3 — MWPM decoding with PyMatching

**Goal.** Run the full decode pipeline — Stim circuit → DEM → `pymatching.Matching`
→ `decode_batch` → logical error rate — show MWPM beats the trivial decoder by a
wide margin, and confirm that $d=5$ beats $d=3$ below threshold with a mini-sweep.

**Notebook.** [`mwpm_pymatching.ipynb`](mwpm_pymatching.ipynb) — built from
`_build_notebook.py`; uses `qec_project.decoders.pymatching_decoder` and
`qec_project.decoders.harness.sample_cell`.

**Run.**
```bash
uv run python phase-03-topological-codes/03-mwpm-pymatching/_build_notebook.py
uv run jupyter nbconvert --to notebook --execute --inplace \
    phase-03-topological-codes/03-mwpm-pymatching/mwpm_pymatching.ipynb
```

**References** (`docs/reading-list.md`): Higgott & Gidney, *Sparse Blossom*
(arXiv:2303.15933).
