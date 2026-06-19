"""Surface-code threshold sweep harness (rotated surface code, Phase 3).

Samples the rotated-surface-code memory experiment over a grid of distances and
physical error rates, decodes with the chosen decoder, and writes a resumable
CSV of logical-error counts under ``capstone/experiments/<run-id>/``.

Sampling runs **in-process** via :func:`qec_project.decoders.harness.sample_cell`
(Stim sampling + PyMatching / ldpc BP+OSD), not ``sinter.collect`` — the latter
asserts ``isinstance(errors, int)`` and breaks under NumPy 2.x's
``np.count_nonzero`` (see CHANGELOG "Failed approaches"). Cells run concurrently
across CPU workers; each Stim sampler is explicitly seeded so results are
reproducible regardless of scheduling.

Resumability: re-running an identical command reads the existing ``stats.csv``
and tops each cell up to ``--shots`` (already-met cells are skipped).

Usage:
    python scripts/run_threshold_sweep.py \\
        --decoder pymatching --noise depolarizing --distances 3 5 7 \\
        --p-phys 0.002 0.003 0.005 0.007 0.01 --shots 20000 --seed 42 --changelog
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from qec_project.analysis.threshold import point_from_counts
from qec_project.decoders.harness import sample_cell

REPO = Path(__file__).resolve().parent.parent
EXPERIMENTS = REPO / "capstone" / "experiments"
SCRIPTS = REPO / "scripts"
CSV_FIELDS = [
    "decoder", "noise", "distance", "rounds", "p_phys",
    "shots", "errors", "seconds", "seed", "commit",
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "unknown"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--decoder", choices=["pymatching", "union-find", "bp-osd", "neural"], default="pymatching")
    p.add_argument("--noise", choices=["depolarizing", "biased", "SI1000", "leakage"], default="depolarizing")
    p.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    p.add_argument("--p-phys", type=float, nargs="+", default=[0.002, 0.003, 0.005, 0.007, 0.01])
    p.add_argument("--shots", type=int, default=20_000)
    p.add_argument("--max-errors", type=int, default=None, help="Early-stop a cell after this many logical errors.")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    p.add_argument("--run-id", default=None, help="Override the derived run id / output directory name.")
    p.add_argument("--changelog", action="store_true", help="Append accuracy-table rows to CHANGELOG.md.")
    p.add_argument("--remote", action="store_true", help="Run on Modal instead of locally (roadmap).")
    return p.parse_args(argv)


def _read_existing(csv_path: Path, decoder: str, noise: str) -> dict[tuple[int, float], tuple[int, int, float]]:
    """Return {(distance, p_phys): (shots, errors, seconds)} for matching rows."""
    if not csv_path.exists():
        return {}
    out: dict[tuple[int, float], tuple[int, int, float]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["decoder"] != decoder or row["noise"] != noise:
                continue
            key = (int(row["distance"]), round(float(row["p_phys"]), 12))
            out[key] = (int(row["shots"]), int(row["errors"]), float(row["seconds"]))
    return out


def _write_csv(csv_path: Path, rows: list[dict[str, object]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _rows(
    merged: dict[tuple[int, float], tuple[int, int, float]],
    args: argparse.Namespace,
    commit: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for d in args.distances:
        for p in args.p_phys:
            shots, errors, seconds = merged[(d, round(p, 12))]
            rows.append({
                "decoder": args.decoder, "noise": args.noise, "distance": d, "rounds": d,
                "p_phys": repr(p), "shots": shots, "errors": errors,
                "seconds": round(seconds, 4), "seed": args.seed, "commit": commit,
            })
    return rows


def _append_changelog(run_id: str, rows: list[dict[str, object]]) -> None:
    """Append one accuracy-table row per distance (well-sampled representative near p=0.005)."""
    ref = 0.005
    by_distance: dict[int, dict[str, object]] = {}
    for row in rows:
        d = int(row["distance"])
        cur = by_distance.get(d)
        if cur is None or abs(float(row["p_phys"]) - ref) < abs(float(cur["p_phys"]) - ref):
            by_distance[d] = row
    for d in sorted(by_distance):
        row = by_distance[d]
        point = point_from_counts(
            decoder=str(row["decoder"]), distance=d, p_phys=float(row["p_phys"]),
            rounds=int(row["rounds"]), shots=int(row["shots"]), errors=int(row["errors"]),
        )
        subprocess.run(
            [sys.executable, str(SCRIPTS / "update_changelog.py"), "--kind", "accuracy",
             "--run-id", run_id, "--code", "rotated-surface", "--distance", str(d),
             "--decoder", str(row["decoder"]), "--noise", str(row["noise"]),
             "--p-phys", repr(float(row["p_phys"])), "--p-log", repr(point.p_log),
             "--shots", str(row["shots"]), "--seed", str(row["seed"]),
             "--notes", "in-process harness, local CPU, per-round p_log"],
            cwd=REPO, check=True,
        )


def run_sweep(args: argparse.Namespace) -> int:
    if args.remote:
        raise SystemExit("Modal --remote path is Phase-4 roadmap; run locally for now.")
    if args.decoder == "neural":
        raise SystemExit("The neural decoder is Phase-5 roadmap; choose pymatching / bp-osd / union-find.")

    run_id = args.run_id or f"sweep-{_dt.date.today().isoformat()}-{args.decoder}-{args.noise}"
    out_dir = EXPERIMENTS / run_id
    csv_path = out_dir / "stats.csv"
    commit = _git_sha()
    existing = _read_existing(csv_path, args.decoder, args.noise)

    # Decide per-cell work (resumability: top up to --shots).
    merged: dict[tuple[int, float], tuple[int, int, float]] = {}
    work: list[tuple[int, float, int, int]] = []
    for d in args.distances:
        for p in args.p_phys:
            key = (d, round(p, 12))
            ex_shots, ex_errors, ex_seconds = existing.get(key, (0, 0, 0.0))
            need = args.shots - ex_shots
            need_errors = (args.max_errors - ex_errors) if args.max_errors is not None else need
            if need <= 0 or need_errors <= 0:
                merged[key] = (ex_shots, ex_errors, ex_seconds)
            else:
                merged[key] = (ex_shots, ex_errors, ex_seconds)
                work.append((d, p, need, need_errors))

    print(f"[{run_id}] {args.decoder}/{args.noise}: {len(work)} cells to run "
          f"({len(merged) - len(work)} already complete), workers={args.workers}")

    # Build picklable kwargs for the top-level sample_cell (closures can't be sent to workers).
    tasks: list[tuple[int, float, dict[str, object]]] = []
    for d, p, need, need_errors in work:
        tasks.append((d, p, {
            "decoder": args.decoder, "distance": d, "p_phys": p, "noise": args.noise,
            "shots": need, "max_errors": need_errors, "seed": args.seed,
            "shot_offset": merged[(d, round(p, 12))][0],
        }))

    def _merge(d: int, p: float, res: object) -> None:
        key = (d, round(p, 12))
        ex_s, ex_e, ex_t = merged[key]
        merged[key] = (ex_s + res.shots, ex_e + res.errors, ex_t + res.seconds)  # type: ignore[attr-defined]
        print(f"  d={d} p={p:<7g} shots={merged[key][0]} errors={merged[key][1]} "
              f"p_shot={merged[key][1] / max(merged[key][0], 1):.4g}", flush=True)
        _write_csv(csv_path, _rows(merged, args, commit))  # incremental flush -> crash-safe/resumable

    if tasks and args.workers > 1 and len(tasks) > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(sample_cell, **kw): (d, p) for (d, p, kw) in tasks}
            for fut in as_completed(futs):
                d, p = futs[fut]
                _merge(d, p, fut.result())
    else:
        for d, p, kw in tasks:
            _merge(d, p, sample_cell(**kw))

    rows = _rows(merged, args, commit)
    _write_csv(csv_path, rows)

    manifest = {
        "run_id": run_id, "argv": sys.argv[1:], "decoder": args.decoder, "noise": args.noise,
        "distances": args.distances, "p_phys": args.p_phys, "shots": args.shots,
        "seed": args.seed, "commit": commit, "timestamp": _dt.datetime.now().isoformat(),
        "versions": _versions(),
    }
    (out_dir / "run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{run_id}] wrote {csv_path} ({len(rows)} cells) and run.json")

    if args.changelog:
        _append_changelog(run_id, rows)
        print(f"[{run_id}] appended accuracy rows to CHANGELOG.md")
    return 0


def _versions() -> dict[str, str]:
    import numpy
    import pymatching
    import sinter
    import stim
    return {
        "numpy": numpy.__version__, "stim": stim.__version__,
        "pymatching": pymatching.__version__, "sinter": sinter.__version__,
    }


def main(argv: list[str] | None = None) -> int:
    return run_sweep(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
