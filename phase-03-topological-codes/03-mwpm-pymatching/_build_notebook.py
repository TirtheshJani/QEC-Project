"""One-shot generator for ``mwpm_pymatching.ipynb`` (Phase 3.3).

Run:  uv run python phase-03-topological-codes/03-mwpm-pymatching/_build_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "mwpm_pymatching.ipynb"


def md(cell_id: str, text: str) -> nbf.NotebookNode:
    # Fixed ids (the committed ones) keep a rebuild from rewriting every cell id.
    return nbf.v4.new_markdown_cell(text, id=cell_id)


def code(cell_id: str, text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text, id=cell_id)


cells: list[nbf.NotebookNode] = [
    md(
        "e06a54f6",
        """# Phase 3.3 — MWPM decoding with PyMatching

Minimum-weight perfect matching (MWPM) is the baseline surface-code decoder. Given
the graphlike detector error model, PyMatching (Sparse Blossom) finds the
lowest-weight set of error edges consistent with the observed detectors and predicts
the logical-observable flips.

The pipeline is **Stim circuit → DEM → `pymatching.Matching` → `decode_batch` →
logical error rate**, wrapped by the promoted helpers
:func:`qec_project.decoders.pymatching_decoder.matching_from_dem` /
:func:`~qec_project.decoders.pymatching_decoder.decode_shots` and the Monte-Carlo
driver :func:`qec_project.decoders.harness.sample_cell`.

References (`docs/reading-list.md`): Higgott & Gidney, *Sparse Blossom*
(arXiv:2303.15933)."""
    ),
    code(
        "6cdd9399",
        """import matplotlib.pyplot as plt
import numpy as np

from qec_project.codes.surface import RotatedSurfaceCode
from qec_project.decoders.pymatching_decoder import decode_shots, matching_from_dem
from qec_project.noise.circuit import depolarizing

code = RotatedSurfaceCode.memory(5)
noise = depolarizing(0.005)
circuit = code.circuit(noise)
dem = code.detector_error_model(noise)
matching = matching_from_dem(dem)
print("Matching built from DEM:", matching)"""
    ),
    md(
        "5eaea3d1",
        """## One batch, end to end

Sample detection events + the true observable flips from the circuit, decode, and
compare. The logical error rate is the fraction of shots where the prediction
disagrees with the truth."""
    ),
    code(
        "790e2b3e",
        """import time

rng_seed = 42
det, obs = circuit.compile_detector_sampler(seed=rng_seed).sample(
    50_000, separate_observables=True)
t0 = time.perf_counter()
pred = decode_shots(matching, det)
decode_s = time.perf_counter() - t0
errors = int(np.count_nonzero(np.any(pred != obs, axis=1)))
print(f"shots = {det.shape[0]:,}, logical errors = {errors}, "
      f"p_L (per shot) = {errors / det.shape[0]:.4f}")
print(f"decode only: {1e6 * decode_s / det.shape[0]:.2f} us/shot "
      f"({det.shape[0] / decode_s:,.0f} shots/s, one core)")

# A 'do nothing' decoder (predict no flip) is the baseline MWPM must beat:
trivial = int(np.count_nonzero(np.any(obs != 0, axis=1)))
print(f"trivial decoder errors = {trivial}  ->  MWPM is {trivial / max(errors,1):.1f}x better")"""
    ),
    md(
        "7fb2da27",
        """## A mini threshold sweep

`sample_cell` wraps the whole loop (seeded, with early-stop). Sweeping a few
physical error rates at $d = 3, 5$ already shows the surface-code signature:
**below threshold, increasing $d$ lowers the logical error rate.** The full
$d \\in \\{3,5,7\\}$ production sweep lives in `capstone/experiments/` (Phase 3.4)."""
    ),
    code(
        "cffcf14a",
        """from qec_project.decoders.harness import sample_cell

ps = [0.003, 0.005, 0.007, 0.01]
plt.figure(figsize=(5.2, 4))
for d in (3, 5):
    ys = [sample_cell(decoder="pymatching", distance=d, p_phys=p, shots=20_000, seed=42).shot_error_rate
          for p in ps]
    plt.plot(ps, ys, "o-", label=f"d = {d}")
    print(f"d={d}: " + "  ".join(f"p={p}:{y:.4f}" for p, y in zip(ps, ys, strict=False)))
plt.xscale("log")
plt.yscale("log")
plt.xlabel("physical error rate $p$")
plt.ylabel("logical error rate (per shot)")
plt.title("MWPM mini-sweep — larger d wins below threshold")
plt.legend()
plt.grid(True, which="both", alpha=0.3)
plt.show()"""
    ),
    md(
        "803a0c1a",
        """## Recap

* PyMatching turns a Stim DEM into an MWPM decoder in one call. `decode_batch`
  decoded the $d=5$, $p=0.005$ shots above in about 3 µs each (the rate printed
  above, a few hundred thousand shots per second on one core). The time per shot
  grows with $d$: each shot holds $d$ rounds of a $d \\times d$ patch.
* MWPM beats the trivial decoder by a wide margin below threshold.
* The $d=3$ vs $d=5$ curves already separate sub-threshold — the full crossing and
  threshold estimate are produced in Phase 3.4 / the capstone sweep."""
    ),
]

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
}
OUT.write_text(nbf.writes(nb), encoding="utf-8")
print(f"wrote {OUT}")
