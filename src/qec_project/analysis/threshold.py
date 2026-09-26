"""Post-sweep analysis: logical-error rates, threshold extraction, plots.

Phase-3 deliverable. Reads the CSV written by ``scripts/run_threshold_sweep.py``
(schema ``decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit``),
normalises each cell to a per-round logical error rate with a binomial
confidence interval, and offers the standard surface-code threshold tools:

* :func:`estimate_threshold` — the crossing point of the ``p_L`` vs ``p`` curves.
* :func:`lambda_ratios` — the sub-threshold error-suppression factor
  ``Λ = p_L(d) / p_L(d+2)``.
* :func:`fit_critical` — the finite-size fit ``p_L = A * (p / p_th) ** ((d+1)/2)``.
* :func:`plot_threshold_crossing` / :func:`plot_decoder_comparison` — figures.

Threshold numbers are never fabricated: when the curves do not cross in range,
:func:`estimate_threshold` returns ``nan`` and logs a warning.

References (in ``docs/reading-list.md``):

* A. G. Fowler, M. Mariantoni, J. M. Martinis, A. N. Cleland. *Surface codes:
  Towards practical large-scale quantum computation.* Phys. Rev. A 86, 032324
  (2012). doi:10.1103/PhysRevA.86.032324.
"""

from __future__ import annotations

import csv
import itertools
import logging
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import sinter

if TYPE_CHECKING:
    from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

_MAX_LIKELIHOOD_FACTOR = 1000
# Fixed salt for matplotlib's generated SVG element ids; with the date dropped
# from the metadata, re-running make_figures.py on the same data gives
# byte-identical SVGs instead of a diff on every run.
_SVG_HASHSALT = "qec-project"


@dataclass(frozen=True)
class LogicalErrorPoint:
    """One (decoder, distance, p_phys) cell, normalised to a per-round rate."""

    decoder: str
    distance: int
    p_phys: float
    p_log: float
    rounds: int = 0
    shots: int = 0
    errors: int = 0
    p_log_low: float = float("nan")
    p_log_high: float = float("nan")
    noise: str = "depolarizing"


@dataclass(frozen=True)
class ThresholdFit:
    """Result of :func:`fit_critical`."""

    p_th: float
    amplitude: float
    p_th_stderr: float
    log_rmse: float


def _per_round_rate(shot_rate: float, rounds: int) -> float:
    """Convert a per-shot error rate to a per-round rate (clamped to ``[0, 0.5)``)."""
    rounds = max(int(rounds), 1)
    clamped = min(max(shot_rate, 0.0), 0.5 - 1e-12)
    return float(sinter.shot_error_rate_to_piece_error_rate(clamped, pieces=rounds))


def point_from_counts(
    *, decoder: str, distance: int, p_phys: float, rounds: int, shots: int, errors: int,
    noise: str = "depolarizing",
) -> LogicalErrorPoint:
    """Build a :class:`LogicalErrorPoint` from raw shot/error counts."""
    if shots <= 0:
        raise ValueError(f"shots must be positive; got {shots}")
    fit = sinter.fit_binomial(
        num_shots=shots, num_hits=errors, max_likelihood_factor=_MAX_LIKELIHOOD_FACTOR
    )
    return LogicalErrorPoint(
        decoder=decoder,
        distance=int(distance),
        p_phys=float(p_phys),
        p_log=_per_round_rate(fit.best, rounds),
        rounds=int(rounds),
        shots=int(shots),
        errors=int(errors),
        p_log_low=_per_round_rate(fit.low, rounds),
        p_log_high=_per_round_rate(fit.high, rounds),
        noise=noise,
    )


def load_points(*csv_paths: str | Path) -> list[LogicalErrorPoint]:
    """Read one or more sweep CSVs into per-round :class:`LogicalErrorPoint`s."""
    points: list[LogicalErrorPoint] = []
    for path in csv_paths:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                shots = int(row["shots"])
                if shots <= 0:
                    continue
                points.append(
                    point_from_counts(
                        decoder=row["decoder"],
                        distance=int(row["distance"]),
                        p_phys=float(row["p_phys"]),
                        rounds=int(row["rounds"]),
                        shots=shots,
                        errors=int(row["errors"]),
                        noise=row.get("noise", "depolarizing"),
                    )
                )
    return points


def duplicate_cells(
    *csv_paths: str | Path,
) -> dict[tuple[str, str, int, float], list[Path]]:
    """Return the ``(decoder, noise, distance, p_phys)`` cells found in more than one row.

    Each sweep CSV holds one row per cell, so a repeat means two sweeps of the
    same cell were passed together (e.g. a rerun next to the committed data).
    :func:`load_points` would then treat them as independent points. Maps each
    repeated cell to the files it came from, in input order.
    """
    seen: dict[tuple[str, str, int, float], list[Path]] = defaultdict(list)
    for path in csv_paths:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = (
                    row["decoder"],
                    row.get("noise", "depolarizing"),
                    int(row["distance"]),
                    float(row["p_phys"]),
                )
                seen[key].append(Path(path))
    return {k: v for k, v in seen.items() if len(v) > 1}


def filter_points(
    points: Iterable[LogicalErrorPoint], *, decoder: str | None = None, noise: str | None = None
) -> list[LogicalErrorPoint]:
    """Return points matching ``decoder`` and/or ``noise``."""
    return [
        p
        for p in points
        if (decoder is None or p.decoder == decoder) and (noise is None or p.noise == noise)
    ]


def _by_distance(points: Iterable[LogicalErrorPoint]) -> dict[int, dict[float, float]]:
    """Map distance -> {p_phys: p_log} for points with positive p_log."""
    out: dict[int, dict[float, float]] = defaultdict(dict)
    for p in points:
        if p.p_log > 0:
            out[p.distance][p.p_phys] = p.p_log
    return out


def estimate_threshold(points: Sequence[LogicalErrorPoint]) -> float:
    """Estimate the threshold as the crossing of the ``p_L`` vs ``p`` curves.

    For each adjacent distance pair, finds where ``log p_L`` for the larger
    distance crosses the smaller (interpolating in ``log p_L`` vs ``p``) and
    averages the in-range crossings. Returns ``nan`` (with a warning) when no
    pair crosses — never a fabricated value.
    """
    by_d = _by_distance(points)
    distances = sorted(by_d)
    if len(distances) < 2:
        logger.warning("estimate_threshold: need >= 2 distances, got %d", len(distances))
        return float("nan")

    crossings: list[float] = []
    for d_lo, d_hi in itertools.pairwise(distances):
        shared = sorted(set(by_d[d_lo]) & set(by_d[d_hi]))
        for p_a, p_b in itertools.pairwise(shared):
            diff_a = math.log(by_d[d_hi][p_a]) - math.log(by_d[d_lo][p_a])
            diff_b = math.log(by_d[d_hi][p_b]) - math.log(by_d[d_lo][p_b])
            if diff_a == 0.0:
                crossings.append(p_a)
            if diff_a * diff_b < 0:  # sign change brackets a crossing
                t = diff_a / (diff_a - diff_b)
                crossings.append(p_a + t * (p_b - p_a))
    if not crossings:
        logger.warning("estimate_threshold: curves do not cross in range; returning nan")
        return float("nan")
    return float(np.mean(crossings))


def lambda_ratios(points: Sequence[LogicalErrorPoint]) -> dict[tuple[int, int], float]:
    """Error-suppression factor ``Λ = p_L(d) / p_L(d+2)`` at the lowest shared ``p``."""
    by_d = _by_distance(points)
    out: dict[tuple[int, int], float] = {}
    for d in sorted(by_d):
        if d + 2 not in by_d:
            continue
        shared = sorted(set(by_d[d]) & set(by_d[d + 2]))
        if not shared:
            continue
        p = shared[0]
        if by_d[d + 2][p] > 0:
            out[(d, d + 2)] = by_d[d][p] / by_d[d + 2][p]
    return out


def fit_critical(points: Sequence[LogicalErrorPoint]) -> ThresholdFit:
    """Fit ``p_L = A * (p / p_th) ** ((d + 1) / 2)`` (log-linear least squares)."""
    pts = [p for p in points if p.p_log > 0]
    if len({p.distance for p in pts}) < 2 or len(pts) < 3:
        raise ValueError("need >= 3 points spanning >= 2 distances with positive p_log")
    d = np.array([p.distance for p in pts], dtype=float)
    p_phys = np.array([p.p_phys for p in pts], dtype=float)
    y = np.log(np.array([p.p_log for p in pts], dtype=float))
    expo = (d + 1.0) / 2.0
    # y = logA + expo * log(p) - expo * log(p_th)  ->  linear in (logA, log p_th)
    target = y - expo * np.log(p_phys)
    design = np.column_stack([np.ones_like(expo), -expo])
    sol, *_ = np.linalg.lstsq(design, target, rcond=None)
    log_amp, log_pth = sol
    resid = target - design @ sol
    dof = max(len(pts) - 2, 1)
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.inv(design.T @ design)
    p_th = float(np.exp(log_pth))
    return ThresholdFit(
        p_th=p_th,
        amplitude=float(np.exp(log_amp)),
        p_th_stderr=float(p_th * math.sqrt(max(cov[1, 1], 0.0))),
        log_rmse=float(np.sqrt(np.mean(resid**2))),
    )


def _grouped_sorted(
    points: Iterable[LogicalErrorPoint],
) -> dict[int, list[LogicalErrorPoint]]:
    groups: dict[int, list[LogicalErrorPoint]] = defaultdict(list)
    for p in points:
        groups[p.distance].append(p)
    return {d: sorted(groups[d], key=lambda q: q.p_phys) for d in sorted(groups)}


def _yerr(group: Sequence[LogicalErrorPoint]) -> np.ndarray | None:
    lo = [max(p.p_log - p.p_log_low, 0.0) for p in group]
    hi = [max(p.p_log_high - p.p_log, 0.0) for p in group]
    if any(math.isnan(v) for v in lo + hi):
        return None
    return np.array([lo, hi])


def _save_svg(fig: Figure, path: Path) -> None:
    """Save ``fig`` as an SVG that is byte-identical across runs."""
    import matplotlib

    with matplotlib.rc_context({"svg.hashsalt": _SVG_HASHSALT}):
        fig.savefig(path, metadata={"Date": None})


def plot_threshold_crossing(
    points: Sequence[LogicalErrorPoint], *, out_path: str | Path, title: str | None = None
) -> Path:
    """Plot ``p_L`` (per round) vs ``p`` with one curve per distance; save PNG+SVG."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = _grouped_sorted(points)
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    for d, group in groups.items():
        xs = [p.p_phys for p in group]
        ys = [p.p_log for p in group]
        ax.errorbar(xs, ys, yerr=_yerr(group), marker="o", capsize=2, label=f"d = {d}")
    p_th = estimate_threshold(points)
    if math.isfinite(p_th):
        ax.axvline(p_th, ls="--", color="0.4", lw=1, label=rf"$p_\mathrm{{th}}\approx{p_th:.4f}$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"physical error rate $p$")
    ax.set_ylabel(r"logical error rate per round $p_L$")
    ax.set_title(title or "Rotated surface code — threshold crossing")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = Path(out_path)
    fig.savefig(out, dpi=200)
    _save_svg(fig, out.with_suffix(".svg"))
    plt.close(fig)
    return out


def plot_decoder_comparison(
    points_by_decoder: Mapping[str, Sequence[LogicalErrorPoint]],
    *,
    distance: int,
    out_path: str | Path,
    title: str | None = None,
) -> Path:
    """Overlay ``p_L`` vs ``p`` for several decoders at a fixed distance; save PNG+SVG."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    for decoder, pts in points_by_decoder.items():
        group = sorted((p for p in pts if p.distance == distance), key=lambda q: q.p_phys)
        if not group:
            continue
        ax.errorbar(
            [p.p_phys for p in group],
            [p.p_log for p in group],
            yerr=_yerr(group),
            marker="o",
            capsize=2,
            label=decoder,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"physical error rate $p$")
    ax.set_ylabel(r"logical error rate per round $p_L$")
    ax.set_title(title or f"Decoder comparison at d = {distance}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = Path(out_path)
    fig.savefig(out, dpi=200)
    _save_svg(fig, out.with_suffix(".svg"))
    plt.close(fig)
    return out
