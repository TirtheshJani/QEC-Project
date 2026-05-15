"""Tests for single-qubit Kraus noise channels.

Convention note. The depolarizing channel here uses the "p/3 per Pauli"
Kraus form: K0 = sqrt(1-p) I, K_{X,Y,Z} = sqrt(p/3) P. Using the identity
X rho X + Y rho Y + Z rho Z = 2 I - rho for any single-qubit density
matrix, this channel is equivalent to the mixture

    (1 - 4p/3) rho + (4p/3) * (I/2).

The channel reaches the maximally mixed state I/2 at p = 3/4, not p = 1.
Tests for "depolarizing -> I/2" and the mixture equivalence therefore
use p = 3/4 and the (1 - 4p/3) form respectively. This matches Nielsen
& Chuang sec. 8.3.4.
"""

from __future__ import annotations

import numpy as np
import pytest

from qec_project.noise.channels import (
    I,
    X,
    Y,
    Z,
    apply_channel,
    bit_flip_kraus,
    composed_depolarizing_probabilities,
    depolarizing_kraus,
    is_trace_preserving,
    phase_flip_kraus,
)

ATOL = 1e-10


def _ket_to_density(psi: np.ndarray) -> np.ndarray:
    psi = psi.astype(np.complex128).reshape(2, 1)
    psi = psi / np.linalg.norm(psi)
    return psi @ psi.conj().T


KET_0 = np.array([1.0, 0.0], dtype=np.complex128)
KET_1 = np.array([0.0, 1.0], dtype=np.complex128)
KET_PLUS = (KET_0 + KET_1) / np.sqrt(2)
KET_MINUS = (KET_0 - KET_1) / np.sqrt(2)
KET_IPLUS = (KET_0 + 1j * KET_1) / np.sqrt(2)


def test_pauli_matrices_are_correct() -> None:
    assert np.allclose(I, np.eye(2))
    assert np.allclose(X @ X, I)
    assert np.allclose(Y @ Y, I)
    assert np.allclose(Z @ Z, I)
    assert np.allclose(X @ Y, 1j * Z)


@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 1.0])
def test_bit_flip_trace_preserving(p: float) -> None:
    assert is_trace_preserving(bit_flip_kraus(p), atol=ATOL)


@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 1.0])
def test_phase_flip_trace_preserving(p: float) -> None:
    assert is_trace_preserving(phase_flip_kraus(p), atol=ATOL)


@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 1.0])
def test_depolarizing_trace_preserving(p: float) -> None:
    assert is_trace_preserving(depolarizing_kraus(p), atol=ATOL)


def test_bit_flip_identity_at_p_zero() -> None:
    rho = _ket_to_density(KET_0)
    out = apply_channel(rho, bit_flip_kraus(0.0))
    assert np.allclose(out, rho, atol=ATOL)


def test_bit_flip_full_flip_at_p_one() -> None:
    rho0 = _ket_to_density(KET_0)
    rho1 = _ket_to_density(KET_1)
    out = apply_channel(rho0, bit_flip_kraus(1.0))
    assert np.allclose(out, rho1, atol=ATOL)


def test_phase_flip_preserves_z_eigenstates() -> None:
    for ket in (KET_0, KET_1):
        rho = _ket_to_density(ket)
        out = apply_channel(rho, phase_flip_kraus(0.37))
        assert np.allclose(out, rho, atol=ATOL)


def test_phase_flip_flips_plus_to_minus_at_p_one() -> None:
    rho_plus = _ket_to_density(KET_PLUS)
    rho_minus = _ket_to_density(KET_MINUS)
    out = apply_channel(rho_plus, phase_flip_kraus(1.0))
    assert np.allclose(out, rho_minus, atol=ATOL)


def test_depolarizing_reaches_maximally_mixed_at_p_three_quarters() -> None:
    # With Kraus weights sqrt(1-p) and sqrt(p/3), the fully mixing point is p=3/4.
    target = 0.5 * np.eye(2, dtype=np.complex128)
    for ket in (KET_0, KET_1, KET_PLUS, KET_MINUS, KET_IPLUS):
        rho = _ket_to_density(ket)
        out = apply_channel(rho, depolarizing_kraus(0.75))
        assert np.allclose(out, target, atol=ATOL)


@pytest.mark.parametrize("p", [0.0, 0.1, 0.3, 0.5, 0.75])
def test_depolarizing_matches_mixture_form(p: float) -> None:
    # Kraus form equals (1 - 4p/3) rho + (4p/3) I/2 (Nielsen & Chuang 8.3.4).
    rng = np.random.default_rng(20260515)
    ident_over_2 = 0.5 * np.eye(2, dtype=np.complex128)
    for _ in range(8):
        a, b = rng.standard_normal(2) + 1j * rng.standard_normal(2)
        psi = np.array([a, b], dtype=np.complex128)
        rho = _ket_to_density(psi)
        kraus_out = apply_channel(rho, depolarizing_kraus(p))
        mix_out = (1.0 - 4.0 * p / 3.0) * rho + (4.0 * p / 3.0) * ident_over_2
        assert np.allclose(kraus_out, mix_out, atol=1e-12)


def test_composed_depolarizing_probabilities_sum_to_one() -> None:
    for p in (0.0, 0.1, 0.5, 0.75, 1.0):
        probs = composed_depolarizing_probabilities(p)
        assert set(probs.keys()) == {"I", "X", "Y", "Z"}
        assert abs(sum(probs.values()) - 1.0) < 1e-12
        # All non-negative for p in [0, 1].
        for v in probs.values():
            assert v >= -1e-12


def test_composed_depolarizing_probabilities_specific_values() -> None:
    probs = composed_depolarizing_probabilities(0.3)
    assert abs(probs["I"] - 0.7) < 1e-12
    assert abs(probs["X"] - 0.1) < 1e-12
    assert abs(probs["Y"] - 0.1) < 1e-12
    assert abs(probs["Z"] - 0.1) < 1e-12


def _random_density_matrix(rng: np.random.Generator) -> np.ndarray:
    # Sample a 2x2 density matrix via the Ginibre ensemble: rho = A A^dag / tr.
    a = rng.standard_normal((2, 2)) + 1j * rng.standard_normal((2, 2))
    rho = a @ a.conj().T
    rho = rho / np.trace(rho).real
    return rho


@pytest.mark.parametrize(
    "kraus_factory",
    [
        lambda: bit_flip_kraus(0.2),
        lambda: phase_flip_kraus(0.4),
        lambda: depolarizing_kraus(0.3),
    ],
)
def test_apply_channel_preserves_trace_and_hermiticity(kraus_factory) -> None:  # type: ignore[no-untyped-def]
    # Seeded RNG pool stands in for a hypothesis search; keeps runtime tiny.
    rng = np.random.default_rng(20260515)
    kraus = kraus_factory()
    for _ in range(32):
        rho = _random_density_matrix(rng)
        assert abs(np.trace(rho) - 1.0) < 1e-12
        out = apply_channel(rho, kraus)
        assert abs(np.trace(out) - 1.0) < 1e-10
        assert np.allclose(out, out.conj().T, atol=1e-12)


def test_is_trace_preserving_rejects_bad_set() -> None:
    bad = (np.array([[1.0, 0.0], [0.0, 0.5]], dtype=np.complex128),)
    assert not is_trace_preserving(bad)
