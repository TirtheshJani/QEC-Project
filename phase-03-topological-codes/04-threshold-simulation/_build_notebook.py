"""One-shot generator for ``threshold_simulation.ipynb`` (Phase 3.4).

Run:  uv run python phase-03-topological-codes/04-threshold-simulation/_build_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "threshold_simulation.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = [
    md(
        """# Phase 3.4 — Threshold simulation & the decoder benchmark

This is where Phase 3 becomes the capstone. We load the production sweeps written by
`scripts/run_threshold_sweep.py` (in `capstone/experiments/`), reproduce the
**threshold-crossing plot**, extract the threshold $p_\\mathrm{th}$ and the
sub-threshold suppression factor $\\Lambda = p_L(d)/p_L(d+2)$, and put **MWPM vs
BP+OSD** head to head on accuracy *and* latency.

Everything here uses the promoted analysis helpers in
:mod:`qec_project.analysis.threshold`; the numbers match `CHANGELOG.md`'s accuracy
table and `capstone/figures/summary.json` (same seed, same commit)."""
    ),
    code(
        """from pathlib import Path

import matplotlib.pyplot as plt

from qec_project.analysis.threshold import (
    estimate_threshold,
    filter_points,
    fit_critical,
    lambda_ratios,
    load_points,
)

repo = Path.cwd()
while not (repo / "capstone").exists() and repo.parent != repo:
    repo = repo.parent
exp = repo / "capstone" / "experiments"
pm_csv = sorted(exp.glob("*pymatching*depolarizing*/stats.csv"))[-1]
bp_csv = sorted(exp.glob("*bp-osd*depolarizing*/stats.csv"))[-1]
points = load_points(pm_csv, bp_csv)
print(f"loaded {len(points)} points from\\n  {pm_csv.parent.name}\\n  {bp_csv.parent.name}")"""
    ),
    md(
        """## The threshold crossing (MWPM)

Below threshold, larger distance $\\Rightarrow$ lower logical error; the curves
fan out. Above threshold the ordering inverts. They cross at $p_\\mathrm{th}$."""
    ),
    code(
        """def plot_crossing(points, title):
    by_d = {}
    for p in points:
        by_d.setdefault(p.distance, []).append(p)
    plt.figure(figsize=(6, 4.4))
    for d in sorted(by_d):
        g = sorted(by_d[d], key=lambda q: q.p_phys)
        xs = [q.p_phys for q in g]
        ys = [q.p_log for q in g]
        yerr = [[max(q.p_log - q.p_log_low, 0) for q in g], [max(q.p_log_high - q.p_log, 0) for q in g]]
        plt.errorbar(xs, ys, yerr=yerr, marker="o", capsize=2, label=f"d = {d}")
    pth = estimate_threshold(points)
    plt.axvline(pth, ls="--", color="0.4", label=fr"$p_{{th}}\\approx{pth:.4f}$")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("physical error rate $p$")
    plt.ylabel("logical error rate per round $p_L$")
    plt.title(title)
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.show()

pm = filter_points(points, decoder="pymatching")
plot_crossing(pm, "Rotated surface code — MWPM (PyMatching)")"""
    ),
    md(
        """## Threshold & suppression for both decoders

`estimate_threshold` finds the curve crossing; `fit_critical` independently fits the
finite-size form $p_L = A\\,(p/p_\\mathrm{th})^{(d+1)/2}$. They agree to within the
fit error — a good consistency check. $\\Lambda > 1$ confirms error suppression."""
    ),
    code(
        """for dec in ("pymatching", "bp-osd"):
    pts = filter_points(points, decoder=dec)
    cross = estimate_threshold(pts)
    fit = fit_critical(pts)
    lam = {f"{a}->{b}": round(v, 2) for (a, b), v in lambda_ratios(pts).items()}
    print(f"{dec:>11}: crossing p_th = {cross:.4f} | fit p_th = {fit.p_th:.4f} "
          f"± {fit.p_th_stderr:.4f} | Λ = {lam}")"""
    ),
    md(
        """## Head to head: accuracy vs latency

BP+OSD exploits the full hyperedge structure of the DEM, so it is **more accurate**
(higher threshold, stronger suppression) than graph-based MWPM. But it is **far
slower** — and the cost gap grows steeply with distance. For the *Decoding algorithm
optimization* objective (real-time signal recovery), that latency scaling is the
crux."""
    ),
    code(
        """import csv
from collections import defaultdict


def throughput(csv_path):
    agg = defaultdict(lambda: [0, 0.0])
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            agg[int(r["distance"])][0] += int(r["shots"])
            agg[int(r["distance"])][1] += float(r["seconds"])
    return {d: (s / max(t, 1e-12)) for d, (s, t) in agg.items()}  # shots/sec

pm_tp, bp_tp = throughput(pm_csv), throughput(bp_csv)
print(f"{'d':>3} {'MWPM us/shot':>14} {'BP+OSD us/shot':>16} {'slowdown':>10}")
for d in sorted(set(pm_tp) & set(bp_tp)):
    pm_us, bp_us = 1e6 / pm_tp[d], 1e6 / bp_tp[d]
    print(f"{d:>3} {pm_us:>14.2f} {bp_us:>16.2f} {bp_us / pm_us:>9.0f}x")

# accuracy at a representative sub-threshold point
for dec, pts in (("MWPM", pm), ("BP+OSD", filter_points(points, decoder="bp-osd"))):
    q = next(x for x in pts if x.distance == 5 and abs(x.p_phys - 0.005) < 1e-9)
    print(f"{dec:>7} d=5 @ p=0.005: p_L = {q.p_log:.2e}")"""
    ),
    md(
        """## Result

* **Threshold (uniform depolarizing).** MWPM $p_\\mathrm{th}\\approx 0.0119$;
  BP+OSD $p_\\mathrm{th}\\approx 0.0132$ — BP+OSD's higher threshold and larger
  $\\Lambda$ make it the more accurate decoder on this model.
* **Latency.** BP+OSD is ~60$\\times$ slower than MWPM at $d=3$ and ~600$\\times$
  at $d=5$ on identical hardware; the gap widens with distance.
* **Takeaway for the capstone.** Accuracy and real-time feasibility pull in opposite
  directions. Quantifying that frontier under realistic noise is exactly the NRC
  *Decoding algorithm optimization* question — see `capstone/`.

> Noise model: `depolarizing` = all four Stim circuit-noise knobs set to $p$. The
> threshold is specific to this model and is **not** a published circuit-level
> (e.g. SI1000) number; it is an identical baseline for the decoder *comparison*."""
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
