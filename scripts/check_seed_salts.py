"""Check that today's harness regenerates the committed 2026-06-19 counts exactly.

Until f5a48b3 the per-cell Stim seed in ``qec_project.decoders.harness._cell_seed``
mixed in ``hash(decoder) & 0xFFFF``, which Python salts per process, so the committed
``sweep-2026-06-19-*/stats.csv`` files cannot be regenerated from the documented
commands. The salts those files used were recovered by brute force (CHANGELOG.md,
Failed approaches, 2026-09-26). Each file was written by two invocations:

* MWPM (pymatching): salt 39723 for p <= 0.01, salt 17237 for p >= 0.013.
* BP+OSD (bp-osd): salt 44539 for p <= 0.01; the p >= 0.013 salt was not recovered.

This script reruns every cell with a known salt through today's
``harness.sample_cell``, with the salt put back in place of the CRC32 term, using the
committed command's settings (20000 shots, --max-errors 2000, seed 42), and compares
shots and errors with the committed stats.csv. The five BP+OSD d = 5 cells take
several minutes, so they run only with ``--all``.

Usage:
    python scripts/check_seed_salts.py                 # 27 MWPM + 5 BP+OSD d=3 cells
    python scripts/check_seed_salts.py --all --workers 2   # also the 5 BP+OSD d=5 cells
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from qec_project.analysis.threshold import load_points
from qec_project.decoders import harness

REPO = Path(__file__).resolve().parent.parent
COMMITTED = [
    REPO / "capstone" / "experiments" / f"sweep-2026-06-19-{dec}-depolarizing" / "stats.csv"
    for dec in ("pymatching", "bp-osd")
]
# The committed run.json argv: --shots 20000 --max-errors 2000 --seed 42.
SHOTS, MAX_ERRORS, SEED = 20000, 2000, 42


def recovered_salt(decoder: str, p_phys: float) -> int | None:
    """The ``hash(decoder) & 0xFFFF`` value the committed cell was sampled with, if known."""
    if decoder == "pymatching":
        return 39723 if p_phys <= 0.01 else 17237
    if decoder == "bp-osd":
        return 44539 if p_phys <= 0.01 else None
    return None


def salted_cell_seed(salt: int) -> Callable[[int, str, int, float, int], int]:
    """``harness._cell_seed`` as it was before f5a48b3, with ``hash(decoder) & 0xFFFF`` = ``salt``."""

    def _seed(seed: int, decoder: str, distance: int, p_phys: float, offset: int) -> int:
        h = (int(seed) & 0x7FFFFFFF) * 1_000_003
        h += distance * 100_003
        h += round(p_phys * 1e9) * 101
        h += (salt & 0xFFFF) * 31
        h += offset
        return h % (2**31 - 1)

    return _seed


def regenerate(
    decoder: str,
    distance: int,
    p_phys: float,
    salt: int,
    noise: str,
    shots: int = SHOTS,
    max_errors: int = MAX_ERRORS,
) -> tuple[int, int]:
    """Run one cell through ``harness.sample_cell`` with the given salt; return (shots, errors)."""
    original = harness._cell_seed
    harness._cell_seed = salted_cell_seed(salt)  # type: ignore[assignment]
    try:
        res = harness.sample_cell(
            decoder=decoder, distance=distance, p_phys=p_phys, noise=noise,
            shots=shots, max_errors=max_errors, seed=SEED,
        )
    finally:
        harness._cell_seed = original  # type: ignore[assignment]
    return res.shots, res.errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("csvs", nargs="*", default=[str(p) for p in COMMITTED],
                    help="stats.csv files (default: the committed sweep-2026-06-19-*)")
    ap.add_argument("--all", action="store_true", help="also run the slow BP+OSD d=5 cells")
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args(argv)

    todo = []
    skipped: dict[str, int] = {}
    for q in sorted(load_points(*args.csvs), key=lambda q: (q.decoder, q.distance, q.p_phys)):
        salt = recovered_salt(q.decoder, q.p_phys)
        if salt is None:
            print(f"{q.decoder:>11} d={q.distance} p={q.p_phys:<6g} skipped: salt not recovered")
        elif q.decoder == "bp-osd" and q.distance >= 5 and not args.all:
            print(f"{q.decoder:>11} d={q.distance} p={q.p_phys:<6g} skipped: slow (use --all)")
        else:
            todo.append((q, salt))
            continue
        skipped[q.decoder] = skipped.get(q.decoder, 0) + 1

    jobs = [(q.decoder, q.distance, q.p_phys, salt, q.noise) for q, salt in todo]
    if args.workers > 1 and jobs:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(regenerate, *zip(*jobs, strict=True)))
    else:
        results = [regenerate(*job) for job in jobs]

    matched: dict[str, list[bool]] = {}
    for (q, salt), (shots, errors) in zip(todo, results, strict=True):
        ok = (shots, errors) == (q.shots, q.errors)
        matched.setdefault(q.decoder, []).append(ok)
        print(
            f"{q.decoder:>11} d={q.distance} p={q.p_phys:<6g} salt={salt}: committed "
            f"{q.errors}/{q.shots}, regenerated {errors}/{shots} {'match' if ok else 'MISMATCH'}"
        )
    for decoder in sorted(set(matched) | set(skipped)):
        oks = matched.get(decoder, [])
        print(f"{decoder}: {sum(oks)}/{len(oks)} checked cells match exactly "
              f"({skipped.get(decoder, 0)} skipped)")
    return 0 if all(all(v) for v in matched.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
