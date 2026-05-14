"""Tests for :mod:`qec_project.analysis.density` (Phase 1.3 promoted helpers)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.analysis.density import is_density_matrix, partial_trace
from qec_project.linalg import tensor

ATOL = 1e-10


def _ket_to_rho(psi: np.ndarray) -> np.ndarray:
    return psi @ psi.conj().T


KET_0 = np.array([[1.0], [0.0]], dtype=np.complex128)
KET_1 = np.array([[0.0], [1.0]], dtype=np.complex128)
RHO_0 = _ket_to_rho(KET_0)
RHO_1 = _ket_to_rho(KET_1)
RHO_MIXED = 0.5 * np.eye(2, dtype=np.complex128)

# Bell states.
BELL_PHI_PLUS = (tensor(KET_0, KET_0) + tensor(KET_1, KET_1)) / np.sqrt(2.0)
BELL_PHI_MINUS = (tensor(KET_0, KET_0) - tensor(KET_1, KET_1)) / np.sqrt(2.0)
BELL_PSI_PLUS = (tensor(KET_0, KET_1) + tensor(KET_1, KET_0)) / np.sqrt(2.0)
BELL_PSI_MINUS = (tensor(KET_0, KET_1) - tensor(KET_1, KET_0)) / np.sqrt(2.0)


def test_is_density_matrix_accepts_pure_state() -> None:
    assert is_density_matrix(RHO_0)
    assert is_density_matrix(RHO_1)
    assert is_density_matrix(RHO_MIXED)


def test_is_density_matrix_rejects_non_hermitian() -> None:
    bogus = np.array([[0.5, 0.5], [-0.5, 0.5]], dtype=np.complex128)
    assert not is_density_matrix(bogus)


def test_is_density_matrix_rejects_wrong_trace() -> None:
    assert not is_density_matrix(2.0 * RHO_0)


def test_is_density_matrix_rejects_non_psd() -> None:
    # Hermitian, trace 1, but with a negative eigenvalue.
    bogus = np.array([[1.5, 0.0], [0.0, -0.5]], dtype=np.complex128)
    assert not is_density_matrix(bogus)


def test_is_density_matrix_rejects_non_square() -> None:
    assert not is_density_matrix(np.zeros((2, 3), dtype=np.complex128))


def test_partial_trace_bell_phi_plus_gives_max_mixed() -> None:
    rho_bell = _ket_to_rho(BELL_PHI_PLUS)
    # Tracing out either qubit of a Bell state leaves I/2.
    rho_A = partial_trace(rho_bell, keep=0, dims=(2, 2))
    rho_B = partial_trace(rho_bell, keep=1, dims=(2, 2))
    assert np.allclose(rho_A, RHO_MIXED, atol=ATOL)
    assert np.allclose(rho_B, RHO_MIXED, atol=ATOL)


def test_partial_trace_all_four_bell_states() -> None:
    for ket in (BELL_PHI_PLUS, BELL_PHI_MINUS, BELL_PSI_PLUS, BELL_PSI_MINUS):
        rho = _ket_to_rho(ket)
        assert np.allclose(partial_trace(rho, keep=0, dims=(2, 2)), RHO_MIXED, atol=ATOL)
        assert np.allclose(partial_trace(rho, keep=1, dims=(2, 2)), RHO_MIXED, atol=ATOL)


def test_partial_trace_product_state_is_local() -> None:
    # |0> tensor |+> -> tracing out qubit 1 gives |0><0|; tracing out qubit 0
    # gives |+><+|.
    ket_plus = (KET_0 + KET_1) / np.sqrt(2.0)
    rho_plus = _ket_to_rho(ket_plus)
    joint = tensor(KET_0, ket_plus)
    rho_joint = joint @ joint.conj().T
    assert np.allclose(partial_trace(rho_joint, keep=0, dims=(2, 2)), RHO_0, atol=ATOL)
    assert np.allclose(partial_trace(rho_joint, keep=1, dims=(2, 2)), rho_plus, atol=ATOL)


def test_partial_trace_preserves_trace() -> None:
    rho_bell = _ket_to_rho(BELL_PHI_PLUS)
    reduced = partial_trace(rho_bell, keep=0, dims=(2, 2))
    assert abs(np.trace(reduced).real - 1.0) < ATOL


def test_partial_trace_three_qubit_keep_subset() -> None:
    # |0> tensor |1> tensor |+>; trace out the middle qubit -> |0><0| tensor |+><+|.
    ket_plus = (KET_0 + KET_1) / np.sqrt(2.0)
    rho_plus = _ket_to_rho(ket_plus)
    psi = tensor(KET_0, KET_1, ket_plus)
    rho = psi @ psi.conj().T
    reduced = partial_trace(rho, keep=[0, 2], dims=(2, 2, 2))
    expected = tensor(RHO_0, rho_plus)
    assert np.allclose(reduced, expected, atol=ATOL)


def test_partial_trace_rejects_bad_dims() -> None:
    rho = _ket_to_rho(BELL_PHI_PLUS)
    with pytest.raises(ValueError):
        partial_trace(rho, keep=0, dims=(3, 2))


def test_partial_trace_rejects_out_of_range_keep() -> None:
    rho = _ket_to_rho(BELL_PHI_PLUS)
    with pytest.raises(ValueError):
        partial_trace(rho, keep=5, dims=(2, 2))


def _random_density(rng: np.random.Generator, dim: int) -> np.ndarray:
    a = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    rho = a @ a.conj().T
    return (rho / np.trace(rho).real).astype(np.complex128)


@given(seed=st.integers(min_value=0, max_value=2**32 - 1))
@settings(max_examples=20, deadline=None)
def test_partial_trace_random_two_qubit_state(seed: int) -> None:
    """For a random 4x4 density, partial traces should still be valid densities."""
    rng = np.random.default_rng(seed)
    rho = _random_density(rng, 4)
    rho_A = partial_trace(rho, keep=0, dims=(2, 2))
    rho_B = partial_trace(rho, keep=1, dims=(2, 2))
    assert is_density_matrix(rho_A)
    assert is_density_matrix(rho_B)
