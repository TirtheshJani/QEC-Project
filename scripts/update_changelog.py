"""Append a templated entry to CHANGELOG.md.

The long-running-Claude pattern: every session updates the project journal.
Three entry kinds map to the three sections in CHANGELOG.md.

Usage:
    python scripts/update_changelog.py --kind milestone --text "Phase 0.1 landed"
    python scripts/update_changelog.py --kind failed    --text "MWPM on NetworkX too slow at d=7; use PyMatching.decode_batch"
    python scripts/update_changelog.py --kind accuracy \\
        --run-id sweep-2026-05-14-a --code rotated-surface --distance 5 \\
        --decoder pymatching --noise SI1000 --p-phys 1e-3 --p-log 1.2e-5 \\
        --shots 1000000 --seed 42 --notes "first threshold sweep, local CPU"

The --kind status form rewrites the "Current status" paragraph instead of
appending.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"

SECTION_HEADERS = {
    "milestone": "## Completed milestones",
    "failed": "## Failed approaches & why",
    "accuracy": "## Decoder accuracy tables (capstone)",
    "limitation": "## Known limitations",
}


def short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "unknown"


def append_under(text: str, header: str, line: str) -> str:
    pattern = re.compile(rf"({re.escape(header)}\n)", re.MULTILINE)
    if not pattern.search(text):
        return text.rstrip() + f"\n\n{header}\n\n{line}\n"
    return pattern.sub(rf"\1\n{line}\n", text, count=1)


def append_accuracy_row(text: str, row: str) -> str:
    """Insert a row immediately below the markdown table separator
    (`| --- | --- | ...`) under the accuracy section. Falls back to
    appending if the section/table doesn't exist yet."""
    header = SECTION_HEADERS["accuracy"]
    sep_pattern = re.compile(
        rf"({re.escape(header)}\n.*?\n\| -+ \|[^\n]*\n)", re.DOTALL
    )
    m = sep_pattern.search(text)
    if not m:
        return append_under(text, header, row)
    return text[: m.end()] + row + "\n" + text[m.end() :]


def rewrite_status(text: str, paragraph: str) -> str:
    pat = re.compile(r"(## Current status\n)(.*?)(\n## )", re.DOTALL)
    if pat.search(text):
        return pat.sub(rf"\1{paragraph}\n\3", text)
    return text.rstrip() + f"\n\n## Current status\n{paragraph}\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--kind",
        required=True,
        choices=["milestone", "failed", "accuracy", "limitation", "status"],
    )
    p.add_argument("--text", help="Free-form text for milestone/failed/limitation/status entries.")
    # accuracy fields
    p.add_argument("--run-id")
    p.add_argument("--code")
    p.add_argument("--distance", type=int)
    p.add_argument("--decoder")
    p.add_argument("--noise")
    p.add_argument("--p-phys", type=float)
    p.add_argument("--p-log", type=float)
    p.add_argument("--shots", type=int)
    p.add_argument("--seed", type=int)
    p.add_argument("--notes", default="")
    args = p.parse_args()

    date = _dt.date.today().isoformat()
    text = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""

    if args.kind == "status":
        if not args.text:
            raise SystemExit("--text is required for status")
        new = rewrite_status(text, args.text.strip())
    elif args.kind == "accuracy":
        required = [
            "run_id",
            "code",
            "distance",
            "decoder",
            "noise",
            "p_phys",
            "p_log",
            "shots",
            "seed",
        ]
        missing = [k for k in required if getattr(args, k) in (None, "")]
        if missing:
            raise SystemExit(f"accuracy entry missing required fields: {missing}")
        row = (
            f"| {args.run_id} | {args.code} | {args.distance} | {args.decoder} | {args.noise} "
            f"| {args.p_phys:.3e} | {args.p_log:.3e} | {args.shots} | {args.seed} "
            f"| {short_sha()} | {args.notes} |"
        )
        new = append_accuracy_row(text, row)
    else:
        if not args.text:
            raise SystemExit(f"--text is required for {args.kind}")
        line = f"- {date}  {args.text.strip()}"
        new = append_under(text, SECTION_HEADERS[args.kind], line)

    CHANGELOG.write_text(new, encoding="utf-8")
    print(f"Updated {CHANGELOG} ({args.kind}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
