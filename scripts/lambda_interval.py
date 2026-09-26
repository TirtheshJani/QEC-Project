"""Sub-threshold suppression Λ = p_L(d) / p_L(d+2) at one physical error rate, with an interval.

Reads ``stats.csv`` files from ``scripts/run_threshold_sweep.py``, takes the per-round
logical error rate of each (decoder, distance) cell at ``--p``, and gives a percentile
interval for Λ from a seeded parametric bootstrap: each cell's error count is redrawn
from Binomial(shots, errors / shots) and Λ is recomputed.

Usage:
    python scripts/lambda_interval.py capstone/experiments/sweep-2026-06-19-*/stats.csv --p 0.005
"""

from __future__ import annotations

import argparse

import numpy as np

from qec_project.analysis.threshold import LogicalErrorPoint, filter_points, load_points


def _per_round(shot_rate: np.ndarray, rounds: int) -> np.ndarray:
    """Per-shot to per-round rate, as ``sinter.shot_error_rate_to_piece_error_rate`` (rate < 0.5)."""
    return 0.5 * (1.0 - (1.0 - 2.0 * shot_rate) ** (1.0 / rounds))


def _draws(cell: LogicalErrorPoint, reps: int, rng: np.random.Generator) -> np.ndarray:
    errors = rng.binomial(cell.shots, cell.errors / cell.shots, size=reps)
    return _per_round(errors / cell.shots, cell.rounds)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("csvs", nargs="+", help="stats.csv files from run_threshold_sweep.py")
    ap.add_argument("--p", type=float, default=0.005, help="physical error rate")
    ap.add_argument("--noise", default="depolarizing")
    ap.add_argument("--reps", type=int, default=10_000, help="bootstrap replicates")
    ap.add_argument("--level", type=float, default=0.95, help="interval coverage")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    points = [
        q
        for q in filter_points(load_points(*args.csvs), noise=args.noise)
        if abs(q.p_phys - args.p) < 1e-12
    ]
    tail = (1.0 - args.level) / 2.0
    for decoder in sorted({q.decoder for q in points}):
        cells = {q.distance: q for q in points if q.decoder == decoder}
        for d in sorted(cells):
            if d + 2 not in cells:
                continue
            lo, hi = cells[d], cells[d + 2]
            if hi.errors == 0:
                print(f"{decoder:>11} Λ({d}->{d + 2}) at p={args.p}: undefined (0 errors at d={d + 2})")
                continue
            with np.errstate(divide="ignore"):  # a draw with 0 errors at d+2 gives inf
                ratio = _draws(lo, args.reps, rng) / _draws(hi, args.reps, rng)
            q_lo, q_hi = np.quantile(ratio, [tail, 1.0 - tail])
            print(
                f"{decoder:>11} Λ({d}->{d + 2}) at p={args.p}: {lo.p_log / hi.p_log:.2f}, "
                f"{args.level:.0%} interval [{q_lo:.2f}, {q_hi:.2f}] "
                f"(errors {lo.errors}/{lo.shots} at d={d}, {hi.errors}/{hi.shots} at d={d + 2})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
