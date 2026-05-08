"""Quantum noise channels in Kraus-operator form.

A quantum channel is a completely-positive trace-preserving (CPTP) map
    rho -> sum_k K_k rho K_k^dagger
where the Kraus operators satisfy sum_k K_k^dagger K_k = I.

This module gives the Kraus operators for the channels we need in Phase 2:
bit-flip, phase-flip, bit-and-phase-flip, depolarizing, amplitude-damping,
and a generic Pauli channel. Everything operates on density matrices stored
as numpy arrays of shape (2**n, 2**n).

For applying a 1-qubit channel to a single qubit of an n-qubit density matrix,
we use the same axis-reshape trick as in qec.statevec, but on both the row and
column tensor axes of rho.
"""

from __future__ import annotations

import numpy as np

from qec.statevec import I as _I
from qec.statevec import X as _X
from qec.statevec import Y as _Y
from qec.statevec import Z as _Z

# A Kraus channel is just a list of 2^k x 2^k matrices.
Kraus = list[np.ndarray]


# ---------------------------------------------------------------------------
# 1-qubit channels
# ---------------------------------------------------------------------------
def bit_flip(p: float) -> Kraus:
    """Bit-flip channel: applies X with probability p, identity with probability 1-p."""
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1]")
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _X]


def phase_flip(p: float) -> Kraus:
    """Phase-flip channel: applies Z with probability p."""
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1]")
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _Z]


def bit_phase_flip(p: float) -> Kraus:
    """Y-channel: applies Y with probability p."""
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1]")
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _Y]


def depolarizing(p: float) -> Kraus:
    """Depolarizing channel.

    Convention used here: with probability p the qubit is replaced by the
    maximally mixed state I/2; with probability 1-p it is left alone. In
    Kraus form:
        rho -> (1 - 3p/4) rho + (p/4)(X rho X + Y rho Y + Z rho Z)
    so the Kraus operators are
        K_I = sqrt(1 - 3p/4) I,  K_X = sqrt(p/4) X,  K_Y = sqrt(p/4) Y,  K_Z = sqrt(p/4) Z.

    At p = 0 this is the identity; at p = 1 it sends every state to I/2.
    """
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1]")
    a = np.sqrt(1 - 3 * p / 4)
    b = np.sqrt(p / 4)
    return [a * _I, b * _X, b * _Y, b * _Z]


def amplitude_damping(gamma: float) -> Kraus:
    """Amplitude-damping channel (T1 relaxation).

    Models energy loss to the environment: |1> decays to |0> with probability
    gamma. This is the canonical *non-unital* channel — I/2 is not a fixed
    point — so it cannot be written as a probabilistic mixture of Paulis.
    """
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must be in [0, 1]")
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    return [K0, K1]


def pauli_channel(px: float, py: float, pz: float) -> Kraus:
    """General Pauli channel: apply X / Y / Z with probabilities px, py, pz."""
    pi = 1 - px - py - pz
    if pi < -1e-12 or min(px, py, pz) < 0:
        raise ValueError(f"invalid Pauli channel probabilities {(px, py, pz)}")
    pi = max(pi, 0.0)
    return [
        np.sqrt(pi) * _I,
        np.sqrt(px) * _X,
        np.sqrt(py) * _Y,
        np.sqrt(pz) * _Z,
    ]


# ---------------------------------------------------------------------------
# Applying channels to density matrices
# ---------------------------------------------------------------------------
def apply_channel_full(rho: np.ndarray, kraus: Kraus) -> np.ndarray:
    """Apply a channel whose Kraus operators have the same dimension as rho."""
    out = np.zeros_like(rho)
    for K in kraus:
        out = out + K @ rho @ K.conj().T
    return out


def apply_1q_channel(rho: np.ndarray, kraus: Kraus, q: int) -> np.ndarray:
    """Apply a single-qubit Kraus channel to qubit `q` of an n-qubit density matrix.

    Strategy: each Kraus K_k is a 2x2 matrix. Build the operator
    M_k = I ⊗ ... ⊗ K_k ⊗ ... ⊗ I via axis-reshape contraction, then
    sum_k M_k rho M_k^dagger.

    For an n-qubit density matrix this is an O(4^n) operation, which is fine
    for the small systems (n <= 9) we touch in Phases 2-5.
    """
    dim = rho.shape[0]
    n = int(np.log2(dim))
    if 2**n != dim or rho.shape != (dim, dim):
        raise ValueError("rho must be a 2^n x 2^n density matrix")
    if not 0 <= q < n:
        raise ValueError(f"qubit index {q} out of range for {n} qubits")

    ax = n - 1 - q  # qubit 0 is the LSB axis (Qiskit convention)

    out = np.zeros_like(rho)
    for K in kraus:
        # apply K to the row axes of rho
        t = rho.reshape((2,) * (2 * n))      # row axes 0..n-1, col axes n..2n-1
        t = np.moveaxis(t, ax, 0)
        t = np.tensordot(K, t, axes=([1], [0]))
        t = np.moveaxis(t, 0, ax)
        # apply K^* to the column axes (so the dagger acts on the right)
        col_ax = n + ax
        t = np.moveaxis(t, col_ax, 0)
        t = np.tensordot(K.conj(), t, axes=([1], [0]))
        t = np.moveaxis(t, 0, col_ax)
        out = out + t.reshape(dim, dim)
    return out


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def density_from_state(psi: np.ndarray) -> np.ndarray:
    """|psi><psi|."""
    psi = np.asarray(psi, dtype=complex).reshape(-1)
    return np.outer(psi, psi.conj())


def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Uhlmann fidelity F(rho, sigma) = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2.

    Fast path: when either argument is pure (Tr(rho^2) ~ 1), F reduces to
    Tr(rho sigma) — bit-exact and avoids the eigendecomposition that
    otherwise costs ~1e-8 of precision at intermediate parameter values.
    """
    rho = np.asarray(rho, dtype=complex)
    sigma = np.asarray(sigma, dtype=complex)

    # Fast path: one argument pure -> F = Tr(rho sigma).
    pure_tol = 1e-10
    if abs(np.trace(rho @ rho).real - 1.0) < pure_tol:
        return float(np.real(np.trace(rho @ sigma)))
    if abs(np.trace(sigma @ sigma).real - 1.0) < pure_tol:
        return float(np.real(np.trace(rho @ sigma)))

    w, V = np.linalg.eigh(rho)
    w = np.clip(w.real, 0, None)
    sqrt_rho = (V * np.sqrt(w)) @ V.conj().T
    M = sqrt_rho @ sigma @ sqrt_rho
    eigs = np.linalg.eigvalsh((M + M.conj().T) / 2)
    eigs = np.clip(eigs.real, 0, None)
    return float(np.sum(np.sqrt(eigs)) ** 2)


def is_cptp(kraus: Kraus, atol: float = 1e-10) -> bool:
    """Check sum_k K_k^dagger K_k == I (trace-preserving) within tolerance."""
    if not kraus:
        return False
    dim = kraus[0].shape[0]
    s = sum(K.conj().T @ K for K in kraus)
    return bool(np.allclose(s, np.eye(dim), atol=atol))
