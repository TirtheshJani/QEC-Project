"""Tests for :mod:`qec_project.noise.classical` (Phase 0.2 promoted helpers)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.noise.classical import bsc_flip


def test_bsc_flip_p_zero_returns_unchanged() -> None:
    rng = np.random.default_rng(0)
    bits = np.array([0, 1, 0, 1, 1, 0, 0, 1], dtype=np.uint8)
    out = bsc_flip(bits, 0.0, rng)
    assert np.array_equal(out, bits)


def test_bsc_flip_p_one_returns_complement() -> None:
    rng = np.random.default_rng(0)
    bits = np.array([0, 1, 0, 1, 1, 0, 0, 1], dtype=np.uint8)
    out = bsc_flip(bits, 1.0, rng)
    assert np.array_equal(out, 1 - bits)


def test_bsc_flip_preserves_shape_and_dtype() -> None:
    rng = np.random.default_rng(0)
    bits = np.zeros((4, 7), dtype=np.uint8)
    out = bsc_flip(bits, 0.3, rng)
    assert out.shape == bits.shape
    assert out.dtype == bits.dtype


def test_bsc_flip_does_not_mutate_input() -> None:
    rng = np.random.default_rng(0)
    bits = np.array([0, 1, 0, 1], dtype=np.uint8)
    snapshot = bits.copy()
    _ = bsc_flip(bits, 0.5, rng)
    assert np.array_equal(bits, snapshot)


def test_bsc_flip_is_deterministic_given_seed() -> None:
    bits = np.array([0, 1, 0, 1, 1, 0, 0, 1], dtype=np.uint8)
    a = bsc_flip(bits, 0.3, np.random.default_rng(42))
    b = bsc_flip(bits, 0.3, np.random.default_rng(42))
    assert np.array_equal(a, b)


def test_bsc_flip_xor_property() -> None:
    """The flip pattern (output XOR input) is independent of input values."""
    rng_a = np.random.default_rng(123)
    rng_b = np.random.default_rng(123)
    zeros = np.zeros(1000, dtype=np.uint8)
    ones = np.ones(1000, dtype=np.uint8)
    flip_pattern_from_zeros = bsc_flip(zeros, 0.25, rng_a) ^ zeros
    flip_pattern_from_ones = bsc_flip(ones, 0.25, rng_b) ^ ones
    assert np.array_equal(flip_pattern_from_zeros, flip_pattern_from_ones)


def test_bsc_flip_rejects_out_of_range_p() -> None:
    rng = np.random.default_rng(0)
    bits = np.array([0, 1], dtype=np.uint8)
    with pytest.raises(ValueError):
        bsc_flip(bits, -0.01, rng)
    with pytest.raises(ValueError):
        bsc_flip(bits, 1.01, rng)


@given(p=st.floats(min_value=0.01, max_value=0.49), seed=st.integers(min_value=0, max_value=2**32 - 1))
@settings(max_examples=20, deadline=None)
def test_bsc_flip_empirical_rate_concentrates_on_p(p: float, seed: int) -> None:
    n = 20000
    rng = np.random.default_rng(seed)
    bits = np.zeros(n, dtype=np.uint8)
    out = bsc_flip(bits, p, rng)
    empirical = float(out.mean())
    # Bernoulli std is sqrt(p(1-p)/n) <= 0.5/sqrt(n); 5 sigma slack gives
    # 2.5/sqrt(n) = ~0.018 at n=20000. Use 5/sqrt(n) for comfortable margin.
    assert abs(empirical - p) < 5.0 / np.sqrt(n)
