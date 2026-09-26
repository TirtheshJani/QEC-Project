"""Tests for threshold analysis (Phase 3). Pure-math; no Monte-Carlo."""

from __future__ import annotations

import math

import pytest

from qec_project.analysis.threshold import (
    LogicalErrorPoint,
    duplicate_cells,
    estimate_threshold,
    fit_critical,
    lambda_ratios,
    lambda_ratios_with_p,
    load_points,
    plot_decoder_comparison,
    plot_threshold_crossing,
    point_from_counts,
)

_HEADER = "decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit\n"


def _synthetic(p_th=0.006, amp=0.4, distances=(3, 5, 7), ps=(0.001, 0.002, 0.003, 0.004)):
    """Points lying exactly on p_L = amp * (p / p_th) ** ((d + 1) / 2)."""
    return [
        LogicalErrorPoint(
            decoder="x", distance=d, p_phys=p, p_log=amp * (p / p_th) ** ((d + 1) / 2), rounds=d
        )
        for d in distances
        for p in ps
    ]


def test_fit_recovers_known_threshold():
    fit = fit_critical(_synthetic(p_th=0.0062))
    assert fit.p_th == pytest.approx(0.0062, rel=1e-3)
    assert fit.log_rmse < 1e-6


def test_estimate_threshold_finds_crossing():
    pts = _synthetic(p_th=0.005, ps=(0.002, 0.004, 0.006, 0.008, 0.01))
    assert estimate_threshold(pts) == pytest.approx(0.005, rel=0.1)


def test_estimate_threshold_nan_when_no_crossing():
    pts = _synthetic(p_th=0.05, ps=(0.001, 0.002, 0.003))  # all sub-threshold, never cross
    assert math.isnan(estimate_threshold(pts))


def test_lambda_ratio_above_one_below_threshold():
    ratios = lambda_ratios(_synthetic(p_th=0.01, ps=(0.001, 0.002)))
    assert (3, 5) in ratios and (5, 7) in ratios
    assert all(v > 1 for v in ratios.values())


def test_lambda_ratios_with_p_reports_the_p_used_per_pair():
    pts = _synthetic(p_th=0.01, ps=(0.001, 0.002))
    # No errors at d=7, p=0.001: that cell has p_log = 0, so 5->7 falls back to p=0.002.
    pts = [q for q in pts if not (q.distance == 7 and q.p_phys == 0.001)] + [
        LogicalErrorPoint(decoder="x", distance=7, p_phys=0.001, p_log=0.0, rounds=7)
    ]
    with_p = lambda_ratios_with_p(pts)
    assert {k: p for k, (p, _) in with_p.items()} == {(3, 5): 0.001, (5, 7): 0.002}
    assert {k: lam for k, (_, lam) in with_p.items()} == lambda_ratios(pts)


def test_load_points_roundtrip(tmp_path):
    csv = tmp_path / "stats.csv"
    csv.write_text(
        "decoder,noise,distance,rounds,p_phys,shots,errors,seconds,seed,commit\n"
        "pymatching,depolarizing,3,3,0.005,10000,120,0.1,42,abc1234\n"
        "pymatching,depolarizing,5,5,0.005,10000,30,0.2,42,abc1234\n"
    )
    pts = load_points(csv)
    assert len(pts) == 2
    p3 = next(p for p in pts if p.distance == 3)
    assert p3.shots == 10000 and p3.errors == 120
    assert 0.0 < p3.p_log < 1.0
    assert p3.p_log_low <= p3.p_log <= p3.p_log_high


def test_point_from_counts_zero_errors():
    p = point_from_counts(decoder="x", distance=3, p_phys=1e-4, rounds=3, shots=10000, errors=0)
    assert p.p_log == 0.0


def test_fit_critical_needs_enough_points():
    with pytest.raises(ValueError):
        fit_critical([LogicalErrorPoint(decoder="x", distance=3, p_phys=0.001, p_log=0.01)])


def test_duplicate_cells_flags_a_cell_present_in_two_csvs(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    a.write_text(
        _HEADER
        + "pymatching,depolarizing,3,3,0.005,10000,120,0.1,42,abc1234\n"
        + "pymatching,depolarizing,5,5,0.005,10000,30,0.2,42,abc1234\n"
    )
    b.write_text(_HEADER + "pymatching,depolarizing,3,3,0.005,20000,250,0.1,42,def5678\n")
    assert duplicate_cells(a, b) == {("pymatching", "depolarizing", 3, 0.005): [a, b]}


def test_duplicate_cells_empty_for_disjoint_csvs(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    a.write_text(_HEADER + "pymatching,depolarizing,3,3,0.005,10000,120,0.1,42,abc1234\n")
    b.write_text(_HEADER + "bp-osd,depolarizing,3,3,0.005,10000,90,5.0,42,abc1234\n")
    assert duplicate_cells(a, b) == {}


@pytest.mark.parametrize("which", ["crossing", "comparison"])
def test_svg_output_is_byte_identical_across_saves(tmp_path, which):
    pts = _synthetic(p_th=0.005, ps=(0.002, 0.004, 0.006, 0.008))
    for name in ("a", "b"):
        out = tmp_path / f"{name}.png"
        if which == "crossing":
            plot_threshold_crossing(pts, out_path=out)
        else:
            plot_decoder_comparison({"x": pts}, distance=5, out_path=out)
    assert (tmp_path / "a.svg").read_bytes() == (tmp_path / "b.svg").read_bytes()
