"""Tests for :mod:`qec_project.linalg` (Phase 0.1 promoted helpers)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.linalg import (
    PAULI_I,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    PAULIS,
    eigendecompose,
    is_unitary,
    tensor,
)

ATOL = 1e-12


def test_pauli_shapes_and_dtype() -> None:
    for name, p in PAULIS.items():
        assert p.shape == (2, 2), name
        assert p.dtype == np.complex128, name


def test_pauli_hermitian() -> None:
    for name, p in PAULIS.items():
        assert np.allclose(p, p.conj().T, atol=ATOL), name


def test_pauli_unitary() -> None:
    for name, p in PAULIS.items():
        assert is_unitary(p), name


def test_pauli_squares_to_identity() -> None:
    for name in ("X", "Y", "Z"):
        p = PAULIS[name]
        assert np.allclose(p @ p, PAULI_I, atol=ATOL), name


def test_pauli_anticommutation() -> None:
    pairs = [(PAULI_X, PAULI_Y), (PAULI_X, PAULI_Z), (PAULI_Y, PAULI_Z)]
    zero = np.zeros((2, 2), dtype=np.complex128)
    for a, b in pairs:
        assert np.allclose(a @ b + b @ a, zero, atol=ATOL)


def test_is_unitary_rejects_non_unitary() -> None:
    rng = np.random.default_rng(0)
    not_unitary = rng.standard_normal((2, 2)) + 1j * rng.standard_normal((2, 2))
    assert not is_unitary(not_unitary)


def test_is_unitary_rejects_non_square() -> None:
    assert not is_unitary(np.eye(2, 3, dtype=np.complex128))


def test_tensor_matches_numpy_kron() -> None:
    assert np.allclose(tensor(PAULI_X, PAULI_Y), np.kron(PAULI_X, PAULI_Y), atol=ATOL)


def test_tensor_variadic_three_factors() -> None:
    expected = np.kron(np.kron(PAULI_X, PAULI_Y), PAULI_Z)
    assert np.allclose(tensor(PAULI_X, PAULI_Y, PAULI_Z), expected, atol=ATOL)


def test_tensor_empty_returns_scalar_identity() -> None:
    result = tensor()
    assert result.shape == (1, 1)
    assert result[0, 0] == 1.0 + 0j


def test_eigendecompose_reconstructs_pauli_z() -> None:
    values, vectors = eigendecompose(PAULI_Z)
    reconstructed = vectors @ np.diag(values) @ vectors.conj().T
    assert np.allclose(reconstructed, PAULI_Z, atol=1e-10)


def test_eigendecompose_eigenvalues_pauli_z() -> None:
    values, _ = eigendecompose(PAULI_Z)
    assert set(np.round(values.real).astype(int).tolist()) == {1, -1}


def test_eigendecompose_rejects_non_square() -> None:
    with pytest.raises(ValueError):
        eigendecompose(np.zeros((2, 3), dtype=np.complex128))


def _random_unitary(rng: np.random.Generator, dim: int = 2) -> np.ndarray:
    """Haar-ish random unitary via QR of a complex Gaussian matrix.

    Sufficient for property tests; not a calibrated Haar measure.
    """
    a = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    q, r = np.linalg.qr(a)
    phases = np.diag(r) / np.abs(np.diag(r))
    return q * phases


@given(seed=st.integers(min_value=0, max_value=2**32 - 1))
@settings(max_examples=25, deadline=None)
def test_unitary_tensor_is_unitary(seed: int) -> None:
    rng = np.random.default_rng(seed)
    u = _random_unitary(rng)
    v = _random_unitary(rng)
    assert is_unitary(u)
    assert is_unitary(v)
    assert is_unitary(tensor(u, v))
