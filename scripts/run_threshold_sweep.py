"""Surface-code threshold sweep harness (skeleton).

Real implementation lands during Phase 3 (`phase-03-topological-codes/`). This
module exists from day one so:

  * `from qec_project.codes import ...` style imports have a stable home
  * the CLI shape is fixed early
  * `scripts/update_changelog.py --kind accuracy ...` calls in CI artifacts
    can reference a stable filename

Usage (target):
    python scripts/run_threshold_sweep.py \\
        --decoder pymatching --noise SI1000 --distances 3 5 7 \\
        --p-phys 5e-4 1e-3 2e-3 --shots 1000000 --seed 42
    python scripts/run_threshold_sweep.py ... --remote   # bursts to Modal
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--decoder", choices=["pymatching", "union-find", "bp-osd", "neural"], required=False)
    p.add_argument("--noise", choices=["depolarizing", "biased", "SI1000", "leakage"], required=False)
    p.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    p.add_argument("--p-phys", type=float, nargs="+", default=[1e-3])
    p.add_argument("--shots", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--remote", action="store_true", help="Run on Modal instead of locally.")
    args = p.parse_args(argv)

    print(
        "Threshold sweep harness is not yet implemented — this is a Phase-3 deliverable.\n"
        f"Requested: decoder={args.decoder} noise={args.noise} distances={args.distances} "
        f"p_phys={args.p_phys} shots={args.shots} seed={args.seed} remote={args.remote}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
