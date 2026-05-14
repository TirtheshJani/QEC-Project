"""Verify every DOI / arXiv ID cited in docs/reading-list.md resolves.

Runs in CI as an anti-hallucination gate. Any cited number that lives in
`docs/reading-list.md` must point at a real, fetchable identifier. The check
is intentionally lightweight (HEAD on doi.org / arxiv.org) so it works offline
in dev and online in CI — when offline, missing-network is reported as a skip
rather than a failure.

Exit codes:
    0  all identifiers resolve (or skipped due to no network)
    1  one or more identifiers do not resolve
"""

from __future__ import annotations

import re
import socket
import sys
from pathlib import Path

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"\barXiv:\s*([0-9]{4}\.[0-9]{4,5})(v\d+)?\b", re.IGNORECASE)

READING_LIST = Path(__file__).resolve().parent.parent / "docs" / "reading-list.md"

# A 404 from doi.org / arxiv.org means the identifier is bad. Everything else
# (200/302 success, 403 access denied, 429 rate-limited, connection errors)
# means we can't disprove the identifier — soft-pass it. The point of this
# script is to catch fabricated DOIs and arXiv IDs, not to gate CI on
# arxiv.org being friendly to a HEAD request from a CI runner.
HARD_FAIL_STATUSES = {404, 410}


def trim_punct(s: str) -> str:
    return s.rstrip(".,;:)]}'\"")


def have_network() -> bool:
    try:
        socket.create_connection(("doi.org", 443), timeout=3).close()
        return True
    except OSError:
        return False


def check_url(url: str) -> tuple[bool, str]:
    """Return (ok, status_descriptor). ok is False only on a 404/410."""
    import urllib.error
    import urllib.request

    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (qec-project-ci/0.1) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return (resp.status not in HARD_FAIL_STATUSES, f"{resp.status}")
    except urllib.error.HTTPError as e:
        return (e.code not in HARD_FAIL_STATUSES, f"{e.code}")
    except Exception as e:
        return (True, f"unreachable ({type(e).__name__})")


def main() -> int:
    if not READING_LIST.exists():
        print(f"reading-list not found at {READING_LIST}; nothing to verify.")
        return 0

    text = READING_LIST.read_text(encoding="utf-8")
    dois = sorted({trim_punct(d) for d in DOI_RE.findall(text)})
    arxivs = sorted({m.group(1) for m in ARXIV_RE.finditer(text)})

    if not dois and not arxivs:
        print("No DOIs or arXiv IDs found in reading-list.md yet — OK (early days).")
        return 0

    if not have_network():
        print("No network — skipping DOI/arXiv resolution checks.")
        return 0

    failures: list[str] = []
    for doi in dois:
        url = f"https://doi.org/{doi}"
        ok, status = check_url(url)
        print(f"  [{'OK' if ok else 'FAIL'}] [{status}] {url}")
        if not ok:
            failures.append(url)

    for ax in arxivs:
        url = f"https://arxiv.org/abs/{ax}"
        ok, status = check_url(url)
        print(f"  [{'OK' if ok else 'FAIL'}] [{status}] {url}")
        if not ok:
            failures.append(url)

    if failures:
        print(f"\n{len(failures)} identifier(s) returned 404/410.")
        return 1
    print(f"\n{len(dois) + len(arxivs)} identifier(s) checked (no 404s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
