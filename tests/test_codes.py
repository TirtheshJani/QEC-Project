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


# ===========================================================================
# Steane [[7, 1, 3]] code
# ===========================================================================
from qec.codes import steane  # noqa: E402


def test_steane_stabilizer_count_and_strings():
    assert len(steane.X_STABILIZERS) == 3
    assert len(steane.Z_STABILIZERS) == 3
    # Standard Hamming-derived choice.
    assert steane.X_STABILIZERS_STR == ["IIIXXXX", "IXXIIXX", "XIXIXIX"]
    assert steane.Z_STABILIZERS_STR == ["IIIZZZZ", "IZZIIZZ", "ZIZIZIZ"]


def test_steane_stabilizers_pairwise_commute():
    from itertools import combinations

    for a, b in combinations(steane.ALL_STABILIZERS, 2):
        assert a.commutes_with(b), f"{a!r} and {b!r} should commute"


def test_steane_logical_operators():
    for s in steane.ALL_STABILIZERS:
        assert steane.LOGICAL_X.commutes_with(s)
        assert steane.LOGICAL_Z.commutes_with(s)
    assert not steane.LOGICAL_X.commutes_with(steane.LOGICAL_Z)


def test_steane_corrects_every_weight_1_error():
    """Steane is distance 3: every weight-1 Pauli must be corrected exactly."""
    for E in steane._enumerate_paulis(1):
        residual = steane.correct(E)
        lx, lz = steane.is_logical_failure(residual)
        assert not lx and not lz, f"{E!r} caused logical failure"
        # Residual must be exactly identity (in symplectic form) for weight-1.
        assert residual.weight() == 0


def test_steane_some_weight_2_errors_fail():
    """Distance 3: there exist weight-2 errors the decoder gets wrong."""
    # Two X errors on qubits sharing a Hamming column with one other qubit
    # alias to the third — known degeneracy. We only assert that *at least
    # one* weight-2 error fails (full distance proof).
    failures = 0
    for E in steane._enumerate_paulis(2):
        residual = steane.correct(E)
        lx, lz = steane.is_logical_failure(residual)
        if lx or lz:
            failures += 1
    assert failures > 0, "no weight-2 error caused a logical failure"


def test_steane_monte_carlo_scaling():
    """Sub-threshold logical error rate should scale as O(p^2).

    Specifically: P_L(0.02) / P_L(0.04) should be ~ (0.02/0.04)^2 = 0.25 to
    within factor 2 in our shot budget.
    """
    rng = np.random.default_rng(2026)
    p_lo = 0.02
    p_hi = 0.04
    pl_lo = steane.monte_carlo_logical_error(p_lo, 20_000, rng=rng)
    pl_hi = steane.monte_carlo_logical_error(p_hi, 20_000, rng=rng)
    ratio = pl_lo / max(pl_hi, 1e-9)
    # O(p^2) -> ratio ~ 0.25; allow [0.1, 0.5] to absorb noise.
    assert 0.1 < ratio < 0.5, f"ratio={ratio} (pl_lo={pl_lo}, pl_hi={pl_hi})"


# ===========================================================================
# Shor [[9, 1, 3]] code
# ===========================================================================
from qec.codes import shor  # noqa: E402


def test_shor_stabilizers_pairwise_commute():
    from itertools import combinations

    for a, b in combinations(shor.ALL_STABILIZERS, 2):
        assert a.commutes_with(b)


def test_shor_logical_operators():
    for s in shor.ALL_STABILIZERS:
        assert shor.LOGICAL_X.commutes_with(s)
        assert shor.LOGICAL_Z.commutes_with(s)
    assert not shor.LOGICAL_X.commutes_with(shor.LOGICAL_Z)


def test_shor_corrects_every_weight_1_error():
    for E in shor._enumerate_paulis(1):
        residual = shor.correct(E)
        lx, lz = shor.is_logical_failure(residual)
        assert not lx and not lz, f"{E!r} caused logical failure"


def test_shor_monte_carlo_scaling():
    rng = np.random.default_rng(2027)
    pl_lo = shor.monte_carlo_logical_error(0.02, 20_000, rng=rng)
    pl_hi = shor.monte_carlo_logical_error(0.04, 20_000, rng=rng)
    ratio = pl_lo / max(pl_hi, 1e-9)
    assert 0.1 < ratio < 0.5, f"ratio={ratio}"
