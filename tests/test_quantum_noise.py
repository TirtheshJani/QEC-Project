"""Tests for :mod:`qec_project.noise.quantum` (Phase 1.3 promoted helpers)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.linalg import PAULI_X, PAULI_Y
from qec_project.noise.quantum import (
    apply_channel,
    bit_flip_channel,
    bit_flip_kraus,
    depolarizing_channel,
    depolarizing_kraus,
    is_trace_preserving,
    phase_flip_channel,
    phase_flip_kraus,
)

ATOL = 1e-10

# A few useful states for testing.
KET_0 = np.array([[1.0], [0.0]], dtype=np.complex128)
KET_1 = np.array([[0.0], [1.0]], dtype=np.complex128)
KET_PLUS = np.array([[1.0], [1.0]], dtype=np.complex128) / np.sqrt(2.0)
KET_MINUS = np.array([[1.0], [-1.0]], dtype=np.complex128) / np.sqrt(2.0)

RHO_0 = KET_0 @ KET_0.conj().T
RHO_1 = KET_1 @ KET_1.conj().T
RHO_PLUS = KET_PLUS @ KET_PLUS.conj().T
RHO_MINUS = KET_MINUS @ KET_MINUS.conj().T
RHO_MIXED = 0.5 * np.eye(2, dtype=np.complex128)


def test_bit_flip_kraus_completeness() -> None:
    for p in (0.0, 0.05, 0.25, 0.5, 0.9, 1.0):
        assert is_trace_preserving(bit_flip_kraus(p))


def test_phase_flip_kraus_completeness() -> None:
    for p in (0.0, 0.05, 0.25, 0.5, 0.9, 1.0):
        assert is_trace_preserving(phase_flip_kraus(p))


def test_depolarizing_kraus_completeness() -> None:
    for p in (0.0, 0.05, 0.25, 0.5, 0.9, 1.0):
        assert is_trace_preserving(depolarizing_kraus(p))


def test_bit_flip_p_zero_is_identity() -> None:
    out = bit_flip_channel(RHO_PLUS, 0.0)
    assert np.allclose(out, RHO_PLUS, atol=ATOL)


def test_bit_flip_p_one_acts_as_X() -> None:
    # With p=1 the only Kraus operator is X, so the channel is rho -> X rho X.
    out = bit_flip_channel(RHO_0, 1.0)
    expected = PAULI_X @ RHO_0 @ PAULI_X
    assert np.allclose(out, expected, atol=ATOL)
    # |0><0| under X becomes |1><1|.
    assert np.allclose(out, RHO_1, atol=ATOL)


def test_bit_flip_on_zero_matches_analytic_form() -> None:
    # rho_0 under bit flip: (1-p) |0><0| + p |1><1|, a classical mixture.
    p = 0.3
    out = bit_flip_channel(RHO_0, p)
    expected = (1.0 - p) * RHO_0 + p * RHO_1
    assert np.allclose(out, expected, atol=ATOL)


def test_phase_flip_on_plus_matches_analytic_form() -> None:
    # rho_+ under phase flip: (1-p) |+><+| + p |-><-|.
    p = 0.25
    out = phase_flip_channel(RHO_PLUS, p)
    expected = (1.0 - p) * RHO_PLUS + p * RHO_MINUS
    assert np.allclose(out, expected, atol=ATOL)


def test_phase_flip_on_zero_is_identity() -> None:
    # Z |0> = |0>, so |0><0| is a fixed point of the phase-flip channel.
    out = phase_flip_channel(RHO_0, 0.4)
    assert np.allclose(out, RHO_0, atol=ATOL)


def test_depolarizing_on_pure_matches_closed_form() -> None:
    # E(rho) = (1 - p) rho + p I/2.
    p = 0.3
    for rho in (RHO_0, RHO_PLUS, RHO_MINUS):
        out = depolarizing_channel(rho, p)
        expected = (1.0 - p) * rho + p * RHO_MIXED
        assert np.allclose(out, expected, atol=ATOL)


def test_depolarizing_p_one_sends_everything_to_max_mixed() -> None:
    for rho in (RHO_0, RHO_1, RHO_PLUS, RHO_MINUS):
        out = depolarizing_channel(rho, 1.0)
        assert np.allclose(out, RHO_MIXED, atol=ATOL)


def test_max_mixed_is_fixed_point_of_all_three() -> None:
    # rho = I/2 is a fixed point of each channel because [P, I] = 0 for any P.
    for p in (0.0, 0.1, 0.5, 0.9, 1.0):
        assert np.allclose(bit_flip_channel(RHO_MIXED, p), RHO_MIXED, atol=ATOL)
        assert np.allclose(phase_flip_channel(RHO_MIXED, p), RHO_MIXED, atol=ATOL)
        assert np.allclose(depolarizing_channel(RHO_MIXED, p), RHO_MIXED, atol=ATOL)


def test_apply_channel_preserves_trace() -> None:
    p = 0.2
    out = apply_channel(RHO_PLUS, bit_flip_kraus(p))
    assert abs(np.trace(out).real - 1.0) < ATOL


def test_channels_reject_out_of_range_p() -> None:
    with pytest.raises(ValueError):
        bit_flip_channel(RHO_0, -0.01)
    with pytest.raises(ValueError):
        phase_flip_channel(RHO_0, 1.01)
    with pytest.raises(ValueError):
        depolarizing_channel(RHO_0, -0.1)


def test_is_trace_preserving_rejects_empty() -> None:
    assert not is_trace_preserving([])


def test_is_trace_preserving_rejects_non_kraus() -> None:
    bogus = [PAULI_X, PAULI_Y]  # X^T X + Y^T Y = 2 I, not I.
    assert not is_trace_preserving(bogus)


def _random_density(rng: np.random.Generator, dim: int = 2) -> np.ndarray:
    """Random density matrix as A A^dagger / tr(A A^dagger) for a random A."""
    a = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    rho = a @ a.conj().T
    rho = rho / np.trace(rho).real
    return rho.astype(np.complex128)


@given(
    p=st.floats(min_value=0.0, max_value=1.0),
    seed=st.integers(min_value=0, max_value=2**32 - 1),
    channel=st.sampled_from(["bit_flip", "phase_flip", "depolarizing"]),
)
@settings(max_examples=40, deadline=None)
def test_random_density_stays_valid_under_channel(
    p: float, seed: int, channel: str
) -> None:
    rng = np.random.default_rng(seed)
    rho = _random_density(rng)
    if channel == "bit_flip":
        out = bit_flip_channel(rho, p)
    elif channel == "phase_flip":
        out = phase_flip_channel(rho, p)
    else:
        out = depolarizing_channel(rho, p)
    # Hermitian.
    assert np.allclose(out, out.conj().T, atol=1e-9)
    # Trace 1.
    assert abs(np.trace(out).real - 1.0) < 1e-9
    assert abs(np.trace(out).imag) < 1e-9
    # PSD: min eigenvalue of the Hermitised matrix is >= -1e-9.
    eigvals = np.linalg.eigvalsh((out + out.conj().T) / 2.0)
    assert eigvals.min() >= -1e-9
