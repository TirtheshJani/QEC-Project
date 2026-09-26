"""Tests for scripts/make_figures.py (loaded from its file; scripts/ is not a package)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "make_figures.py"
_HEADER = "decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit\n"
_ROWS = (
    "pymatching,depolarizing,3,3,0.005,10000,120,0.1,42,abc1234\n"
    "pymatching,depolarizing,5,5,0.005,10000,30,0.2,42,abc1234\n"
    "pymatching,depolarizing,3,3,0.01,10000,500,0.1,42,abc1234\n"
    "pymatching,depolarizing,5,5,0.01,10000,300,0.2,42,abc1234\n"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("make_figures", _SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_make_figures_warns_when_two_csvs_share_a_cell(tmp_path, capsys):
    old = tmp_path / "old" / "stats.csv"
    new = tmp_path / "new" / "stats.csv"
    for path in (old, new):
        path.parent.mkdir()
        path.write_text(_HEADER + _ROWS)
    rc = _load_script().main([str(old), str(new), "--out-dir", str(tmp_path / "figs")])
    assert rc == 0
    err = capsys.readouterr().err
    assert "WARNING" in err
    assert "4 cells" in err
    assert "pymatching d=3 p=0.005" in err
    assert str(old) in err and str(new) in err


def test_make_figures_silent_without_duplicates(tmp_path, capsys):
    csv = tmp_path / "stats.csv"
    csv.write_text(_HEADER + _ROWS)
    rc = _load_script().main([str(csv), "--out-dir", str(tmp_path / "figs")])
    assert rc == 0
    assert "WARNING" not in capsys.readouterr().err
