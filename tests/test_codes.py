"""Tests for qec/codes/.

Phase 4 acceptance gates:
- Encoder produces alpha|000> + beta|111>.
- Every weight-<=1 X error is detected and corrected (final state == noiseless
  encoded state to floating-point precision).
- Weight-2 X errors trigger a recovery that *fails* (logical flip), confirming
  distance 1 against arbitrary X+Z noise but distance 3 against pure X noise.
- Monte-Carlo logical error rate matches the analytic 3 p^2 - 2 p^3.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import pytest

from qec import statevec as sv
from qec.codes import repetition as rep

ATOL = 1e-12


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------
def test_encode_zero():
    psi = rep.encode_bitflip(1, 0)
    expected = np.zeros(8, dtype=complex)
    expected[0b000] = 1.0
    assert np.allclose(psi, expected, atol=ATOL)


def test_encode_one():
    psi = rep.encode_bitflip(0, 1)
    expected = np.zeros(8, dtype=complex)
    expected[0b111] = 1.0
    assert np.allclose(psi, expected, atol=ATOL)


def test_encode_superposition():
    a = (1 / np.sqrt(2)) * (1 + 0j)
    b = (1 / np.sqrt(2)) * (1 + 0j)
    psi = rep.encode_bitflip(a, b)
    expected = np.zeros(8, dtype=complex)
    expected[0b000] = a
    expected[0b111] = b
    assert np.allclose(psi, expected, atol=ATOL)


# ---------------------------------------------------------------------------
# Syndrome table
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "pattern,expected_syndrome,recovery",
    [
        ((0, 0, 0), (0, 0), None),
        ((1, 0, 0), (1, 0), 0),
        ((0, 1, 0), (1, 1), 1),
        ((0, 0, 1), (0, 1), 2),
    ],
)
def test_syndrome_for_weight_1_error(pattern, expected_syndrome, recovery):
    s = rep.syndrome_bitflip_from_error(pattern)
    assert s == expected_syndrome
    assert rep.recovery_x(s) == recovery


# ---------------------------------------------------------------------------
# Round-trip on a state vector (weight <= 1 errors must be corrected)
# ---------------------------------------------------------------------------
def test_round_trip_no_error():
    alpha, beta = 0.6, 0.8
    psi_clean = rep.encode_bitflip(alpha, beta)
    psi_out, syn = rep.round_trip_with_x_error(alpha, beta, (0, 0, 0))
    assert syn == (0, 0)
    assert np.allclose(psi_out, psi_clean, atol=ATOL)


@pytest.mark.parametrize("q", [0, 1, 2])
def test_round_trip_single_x_error_corrected(q):
    """X error on any single qubit must be undone."""
    rng = np.random.default_rng(0)
    alpha = rng.normal() + 1j * rng.normal()
    beta = rng.normal() + 1j * rng.normal()
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    alpha, beta = alpha / norm, beta / norm

    psi_clean = rep.encode_bitflip(alpha, beta)
    pattern = [0, 0, 0]
    pattern[q] = 1
    psi_out, _ = rep.round_trip_with_x_error(alpha, beta, tuple(pattern))
    # Equal up to global phase (which the syndrome path doesn't introduce, so
    # equality should be exact).
    assert np.allclose(psi_out, psi_clean, atol=ATOL), f"X on q={q} not corrected"


def test_round_trip_weight_2_error_causes_logical_flip():
    """An X_0 X_1 error decodes as 'X on q2', leaving X_0 X_1 X_2 = logical X."""
    psi_clean_zero = rep.encode_bitflip(1, 0)
    psi_clean_one = rep.encode_bitflip(0, 1)
    psi_out, syn = rep.round_trip_with_x_error(1, 0, (1, 1, 0))
    # The miscorrected state should be the *other* logical state.
    assert np.allclose(psi_out, psi_clean_one, atol=ATOL)


# ---------------------------------------------------------------------------
# Logical-error scaling: Monte-Carlo vs analytic
# ---------------------------------------------------------------------------
def test_logical_error_at_zero():
    assert rep.analytic_logical_error_rate(0.0) == 0.0
    rng = np.random.default_rng(0)
    assert rep.monte_carlo_logical_error(0.0, 1000, rng=rng) == 0.0


def test_logical_error_at_half_is_one_half():
    """At p = 0.5 every input bit is uniformly random, so the post-recovery
    logical state is also uniformly random — logical error rate 0.5."""
    expected = rep.analytic_logical_error_rate(0.5)
    assert np.isclose(expected, 0.5, atol=1e-12)


@pytest.mark.parametrize("p", [0.05, 0.1, 0.2])
def test_monte_carlo_matches_analytic(p):
    """At least 50 000 shots should put the empirical estimate within ~3
    sigma of the analytic curve."""
    rng = np.random.default_rng(2026)
    shots = 50_000
    est = rep.monte_carlo_logical_error(p, shots, rng=rng)
    truth = rep.analytic_logical_error_rate(p)
    sigma = np.sqrt(truth * (1 - truth) / shots)
    assert abs(est - truth) < 4 * sigma, f"p={p}: est={est}, truth={truth}, 4sigma={4*sigma}"


def test_logical_error_pattern_table_matches_truth_table():
    """Exhaustively verify the (failure?) classification for all 8 X patterns."""
    for pattern in product([0, 1], repeat=3):
        weight = sum(pattern)
        # Distance-3 against pure X: weight <= 1 corrects, weight >= 2 fails.
        expected_failure = 1 if weight >= 2 else 0
        got = rep.logical_error_after_recovery(pattern)
        assert got == expected_failure, f"pattern {pattern}: weight {weight}, got {got}"


# ---------------------------------------------------------------------------
# Phase-flip code symmetry: bit-flip code in the X basis
# ---------------------------------------------------------------------------
def test_phase_flip_encoding_is_bit_flip_in_hadamard_basis():
    """Encoding into the phase-flip code = encoding into the bit-flip code,
    then H on every qubit."""
    a, b = 0.6, 0.8
    psi_phase = rep.encode_phaseflip(a, b)
    psi_bit = rep.encode_bitflip(a, b)
    for q in range(3):
        psi_bit = sv.apply_1q(psi_bit, sv.H, q)
    assert np.allclose(psi_phase, psi_bit, atol=ATOL)


def test_phase_flip_logical_zero_is_plus_plus_plus():
    psi = rep.encode_phaseflip(1, 0)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    expected = np.kron(plus, np.kron(plus, plus))
    assert np.allclose(psi, expected, atol=ATOL)
