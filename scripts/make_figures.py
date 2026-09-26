"""Generate capstone threshold figures + a summary from sweep CSVs.

Reads one or more ``stats.csv`` files produced by
``scripts/run_threshold_sweep.py``, then writes, into ``capstone/figures/``:

* ``threshold_<noise>_<decoder>.png`` / ``.svg`` — the logical-vs-physical
  error-rate crossing plot, one curve per distance, per decoder.
* ``decoder_comparison_d<d>_<noise>.png`` / ``.svg`` — MWPM vs BP+OSD at a fixed
  distance (when >= 2 decoders are present).
* ``summary.json`` — the reproduced headline numbers (estimated threshold,
  finite-size fit ``p_th`` ± stderr, and Λ suppression ratios) per decoder, so
  the README / EOI can cite exact values without re-deriving them.

Usage:
    python scripts/make_figures.py capstone/experiments/*/stats.csv --noise depolarizing
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from qec_project.analysis.threshold import (
    duplicate_cells,
    estimate_threshold,
    filter_points,
    fit_critical,
    lambda_ratios,
    load_points,
    plot_decoder_comparison,
    plot_threshold_crossing,
)

REPO = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csvs", nargs="+", help="stats.csv files from run_threshold_sweep.py")
    ap.add_argument("--noise", default="depolarizing")
    ap.add_argument("--out-dir", default=str(REPO / "capstone" / "figures"))
    ap.add_argument("--compare-distance", type=int, default=5)
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dups = duplicate_cells(*args.csvs)
    if dups:
        lines = [
            f"WARNING: {len(dups)} cells appear in more than one input CSV. Each copy is fitted "
            "as a separate point, which shifts the fit and shrinks its error bar. Pass one "
            "stats.csv per decoder (the committed data is capstone/experiments/sweep-2026-06-19-*).",
        ]
        for (dec, noise, d, p), paths in sorted(dups.items()):
            lines.append(f"  {dec} d={d} p={p} ({noise}): " + ", ".join(map(str, paths)))
        print("\n".join(lines), file=sys.stderr)

    points = filter_points(load_points(*args.csvs), noise=args.noise)
    if not points:
        raise SystemExit(f"no points for noise={args.noise!r} in {args.csvs}")
    decoders = sorted({p.decoder for p in points})

    summary: dict[str, object] = {"noise": args.noise, "decoders": {}}
    by_decoder = {}
    for decoder in decoders:
        pts = filter_points(points, decoder=decoder)
        by_decoder[decoder] = pts
        fig = out_dir / f"threshold_{args.noise}_{decoder}.png"
        plot_threshold_crossing(
            pts, out_path=fig,
            title=f"Rotated surface code — {decoder} under {args.noise} noise",
        )
        crossing = estimate_threshold(pts)
        try:
            fit = fit_critical(pts)
            fit_info = {"p_th": fit.p_th, "p_th_stderr": fit.p_th_stderr,
                        "amplitude": fit.amplitude, "log_rmse": fit.log_rmse}
        except ValueError:
            fit_info = None
        lam = {f"{a}->{b}": v for (a, b), v in lambda_ratios(pts).items()}
        summary["decoders"][decoder] = {  # type: ignore[index]
            "crossing_estimate": None if math.isnan(crossing) else crossing,
            "fit": fit_info,
            "lambda": lam,
            "points": [
                {"distance": p.distance, "p_phys": p.p_phys, "shots": p.shots,
                 "errors": p.errors, "p_log": p.p_log,
                 "p_log_low": p.p_log_low, "p_log_high": p.p_log_high}
                for p in sorted(pts, key=lambda q: (q.distance, q.p_phys))
            ],
        }
        cstr = "nan" if math.isnan(crossing) else f"{crossing:.4f}"
        fstr = "n/a" if fit_info is None else f"{fit_info['p_th']:.4f}±{fit_info['p_th_stderr']:.4f}"
        print(f"{decoder:>11}: crossing≈{cstr}  fit p_th={fstr}  Λ={lam}")
        print(f"             wrote {fig.name} (+ .svg)")

    if len(decoders) >= 2:
        cmp_fig = out_dir / f"decoder_comparison_d{args.compare_distance}_{args.noise}.png"
        plot_decoder_comparison(
            by_decoder, distance=args.compare_distance, out_path=cmp_fig,
            title=f"MWPM vs BP+OSD at d={args.compare_distance} ({args.noise} noise)",
        )
        print(f"  comparison: wrote {cmp_fig.name} (+ .svg)")

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {out_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
