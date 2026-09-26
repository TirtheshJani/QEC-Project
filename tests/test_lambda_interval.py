"""Tests for scripts/lambda_interval.py (loaded from its file; scripts/ is not a package)."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from qec_project.analysis.threshold import point_from_counts

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lambda_interval.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("lambda_interval", _SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_per_round_matches_sinter_conversion():
    import numpy as np

    mod = _load_script()
    cell = point_from_counts(
        decoder="x", distance=5, p_phys=0.005, rounds=5, shots=20000, errors=297
    )
    assert mod._per_round(np.array([297 / 20000]), 5)[0] == pytest.approx(cell.p_log, rel=1e-9)


def test_lambda_interval_brackets_point_estimate(tmp_path, capsys):
    csv = tmp_path / "stats.csv"
    csv.write_text(
        "decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit\n"
        "pymatching,depolarizing,3,3,0.005,20000,400,0.1,42,abc1234\n"
        "pymatching,depolarizing,5,5,0.005,20000,200,0.2,42,abc1234\n"
        "pymatching,depolarizing,3,3,0.01,20000,900,0.1,42,abc1234\n"
    )
    assert _load_script().main([str(csv), "--p", "0.005", "--reps", "2000"]) == 0
    out = capsys.readouterr().out
    m = re.search(r"Λ\(3->5\) at p=0.005: ([\d.]+), 95% interval \[([\d.]+), ([\d.]+)\]", out)
    assert m is not None, out
    lam, lo, hi = (float(g) for g in m.groups())
    p3 = point_from_counts(decoder="x", distance=3, p_phys=0.005, rounds=3, shots=20000, errors=400)
    p5 = point_from_counts(decoder="x", distance=5, p_phys=0.005, rounds=5, shots=20000, errors=200)
    assert lam == pytest.approx(p3.p_log / p5.p_log, abs=0.005)
    assert lo < lam < hi
