"""Tests for threshold analysis (Phase 3). Pure-math; no Monte-Carlo."""

from __future__ import annotations

import math

import pytest

from qec_project.analysis.threshold import (
    LogicalErrorPoint,
    estimate_threshold,
    fit_critical,
    lambda_ratios,
    load_points,
    point_from_counts,
)


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
