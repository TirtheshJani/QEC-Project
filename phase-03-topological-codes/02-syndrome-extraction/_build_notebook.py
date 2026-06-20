"""One-shot generator for ``syndrome_extraction.ipynb`` (Phase 3.2).

Run:  uv run python phase-03-topological-codes/02-syndrome-extraction/_build_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "syndrome_extraction.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = [
    md(
        """# Phase 3.2 — Syndrome extraction & detectors

A surface-code memory runs repeated rounds of stabilizer measurement. Each
measurement is noisy, so we work with **detectors**: a detector is the parity of a
stabilizer between consecutive rounds. In a noiseless run every detector is
deterministically `0`; noise makes some fire. Decoders consume these detection
events, not the raw measurements.

This notebook samples the detector stream from
:class:`qec_project.codes.surface.RotatedSurfaceCode` and sanity-checks its
structure."""
    ),
    code(
        """import matplotlib.pyplot as plt

from qec_project.codes.surface import RotatedSurfaceCode
from qec_project.noise.circuit import CircuitNoise, depolarizing

code = RotatedSurfaceCode.memory(5)          # d = 5, 5 rounds
noisy = code.circuit(depolarizing(0.005))
clean = code.circuit(CircuitNoise(0, 0, 0, 0))
print(f"d=5: {noisy.num_detectors} detectors over {code.rounds} rounds, "
      f"{noisy.num_observables} logical observable")"""
    ),
    md(
        """## Noiseless ⇒ no detections

The defining sanity check: with zero noise, no detector ever fires (and the logical
observable never flips)."""
    ),
    code(
        """det0, obs0 = clean.compile_detector_sampler(seed=0).sample(
    1000, separate_observables=True)
print("clean detections fired:", int(det0.sum()), " logical flips:", int(obs0.sum()))
assert det0.sum() == 0 and obs0.sum() == 0"""
    ),
    md(
        """## The noisy syndrome stream

Under depolarizing noise the detectors fire sparsely and randomly. The mean
detection density per detector is a useful diagnostic; the heat-map shows which
detectors fired across the first few shots."""
    ),
    code(
        """det, obs = noisy.compile_detector_sampler(seed=42).sample(
    20_000, separate_observables=True)
print(f"mean detection density = {det.mean():.4f},  "
      f"logical flip rate (undecoded) = {obs.mean():.4f}")

plt.figure(figsize=(6, 3))
plt.imshow(det[:40], aspect="auto", cmap="Greys", interpolation="nearest")
plt.xlabel("detector index")
plt.ylabel("shot")
plt.title("d=5 detection events (first 40 shots)")
plt.colorbar(label="fired")
plt.show()"""
    ),
    md(
        """## Detection density vs physical error rate

The fraction of detectors that fire scales smoothly with the physical error rate —
the raw signal the decoder must invert in Phase 3.3."""
    ),
    code(
        """ps = [0.001, 0.002, 0.005, 0.01, 0.02]
dens = []
for p in ps:
    d, _ = RotatedSurfaceCode.memory(5).circuit(depolarizing(p)).compile_detector_sampler(
        seed=1).sample(5000, separate_observables=True)
    dens.append(d.mean())
plt.figure(figsize=(5, 3.5))
plt.plot(ps, dens, "o-")
plt.xscale("log")
plt.xlabel("physical error rate $p$")
plt.ylabel("mean detection density")
plt.title("Detector firing rate grows with p")
plt.grid(True, which="both", alpha=0.3)
plt.show()
print(dict(zip(ps, (round(x, 4) for x in dens), strict=False)))"""
    ),
    md(
        """## Recap

* Detectors = inter-round stabilizer parities; noiseless ⇒ all zero (verified).
* Detection density rises smoothly with $p$; the undecoded logical flip rate is
  what MWPM / BP+OSD must suppress.
* **Next (3.3):** feed this detector stream to PyMatching."""
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
