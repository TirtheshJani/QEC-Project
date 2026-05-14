"""Tests for :mod:`qec_project.info` (Phase 0.2 promoted helpers)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.info import binary_entropy, bsc_capacity

ATOL = 1e-12


def test_binary_entropy_at_zero_and_one_is_zero() -> None:
    assert binary_entropy(0.0) == 0.0
    assert binary_entropy(1.0) == 0.0


def test_binary_entropy_at_half_is_one() -> None:
    assert abs(binary_entropy(0.5) - 1.0) < ATOL


def test_binary_entropy_symmetric() -> None:
    for p in (0.01, 0.1, 0.25, 0.4, 0.49):
        assert abs(binary_entropy(p) - binary_entropy(1.0 - p)) < ATOL


def test_binary_entropy_vectorised() -> None:
    ps = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    hs = binary_entropy(ps)
    assert isinstance(hs, np.ndarray)
    assert hs.shape == ps.shape
    expected = np.array([0.0, 0.8112781244591328, 1.0, 0.8112781244591328, 0.0])
    assert np.allclose(hs, expected, atol=1e-12)


def test_bsc_capacity_at_zero_is_one() -> None:
    assert abs(bsc_capacity(0.0) - 1.0) < ATOL


def test_bsc_capacity_at_half_is_zero() -> None:
    assert abs(bsc_capacity(0.5) - 0.0) < ATOL


def test_bsc_capacity_at_one_is_one() -> None:
    assert abs(bsc_capacity(1.0) - 1.0) < ATOL


def test_bsc_capacity_vectorised() -> None:
    ps = np.array([0.0, 0.1, 0.5, 0.9, 1.0])
    cs = bsc_capacity(ps)
    assert isinstance(cs, np.ndarray)
    assert cs.shape == ps.shape
    assert abs(cs[0] - 1.0) < ATOL
    assert abs(cs[2] - 0.0) < ATOL
    assert abs(cs[4] - 1.0) < ATOL


def test_entropy_rejects_out_of_range_p() -> None:
    with pytest.raises(ValueError):
        binary_entropy(-0.01)
    with pytest.raises(ValueError):
        binary_entropy(1.01)


def test_capacity_rejects_out_of_range_p() -> None:
    with pytest.raises(ValueError):
        bsc_capacity(np.array([0.5, 1.5]))


@given(p=st.floats(min_value=0.0, max_value=1.0))
@settings(max_examples=50, deadline=None)
def test_entropy_in_zero_one(p: float) -> None:
    h = binary_entropy(p)
    assert isinstance(h, float)
    assert -1e-12 <= h <= 1.0 + 1e-12
