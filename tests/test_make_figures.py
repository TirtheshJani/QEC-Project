"""Tests for scripts/make_figures.py (loaded from its file; scripts/ is not a package)."""

from __future__ import annotations

import importlib.util
import json
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


def test_summary_records_the_p_of_each_lambda(tmp_path):
    csv = tmp_path / "stats.csv"
    csv.write_text(_HEADER + _ROWS)
    figs = tmp_path / "figs"
    assert _load_script().main([str(csv), "--out-dir", str(figs)]) == 0
    entry = json.loads((figs / "summary.json").read_text())["decoders"]["pymatching"]
    assert entry["lambda_p_phys"] == {"3->5": 0.005}  # the lowest p both distances share
    assert set(entry["lambda"]) == set(entry["lambda_p_phys"])


_WINDOW_ROWS = _ROWS + (
    "pymatching,depolarizing,3,3,0.003,10000,50,0.1,42,abc1234\n"
    "pymatching,depolarizing,5,5,0.003,10000,8,0.2,42,abc1234\n"
    "pymatching,depolarizing,3,3,0.02,10000,1500,0.1,42,abc1234\n"
    "pymatching,depolarizing,5,5,0.02,10000,1900,0.2,42,abc1234\n"
)


def test_p_max_prints_a_post_hoc_windowed_fit_and_leaves_the_files_unchanged(tmp_path, capsys):
    from qec_project.analysis.threshold import filter_points, fit_critical, load_points

    csv = tmp_path / "stats.csv"
    csv.write_text(_HEADER + _WINDOW_ROWS)
    mod = _load_script()
    assert mod.main([str(csv), "--out-dir", str(tmp_path / "full")]) == 0
    capsys.readouterr()
    assert mod.main([str(csv), "--out-dir", str(tmp_path / "win"), "--p-max", "0.01"]) == 0
    out = capsys.readouterr().out

    pts = filter_points(load_points(csv), decoder="pymatching")
    full = fit_critical(pts)
    window = fit_critical([q for q in pts if q.p_phys <= 0.01])
    assert f"{window.p_th:.4f}" != f"{full.p_th:.4f}"  # the window changes the fit
    line = next(ln for ln in out.splitlines() if "p <= 0.01" in ln)
    assert "post-hoc" in line
    assert f"p_th={window.p_th:.4f}±{window.p_th_stderr:.4f}" in line
    assert "6 points" in line
    # The windowed fit is printed only: summary.json keeps the whole-grid fit.
    assert (tmp_path / "win" / "summary.json").read_bytes() == (
        tmp_path / "full" / "summary.json"
    ).read_bytes()


def test_p_max_reports_n_a_when_the_window_is_too_small_to_fit(tmp_path, capsys):
    csv = tmp_path / "stats.csv"
    csv.write_text(_HEADER + _WINDOW_ROWS)
    assert _load_script().main(
        [str(csv), "--out-dir", str(tmp_path / "figs"), "--p-max", "0.003"]
    ) == 0
    line = next(ln for ln in capsys.readouterr().out.splitlines() if "p <= 0.003" in ln)
    assert "p_th=n/a" in line
