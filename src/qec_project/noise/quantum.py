"""Single-qubit quantum noise channels in Kraus-operator form.

A quantum channel ``E`` is a completely-positive trace-preserving (CPTP)
map on density operators. It can always be written as

    E(rho) = sum_k K_k rho K_k^dagger,

with the Kraus completeness relation ``sum_k K_k^dagger K_k = I``. The
three single-qubit channels introduced in Phase 1.3 and reused from
Phase 2 onward are:

* **Bit-flip** ``X`` with probability ``p``: ``K_0 = sqrt(1-p) I``,
  ``K_1 = sqrt(p) X``.
* **Phase-flip** ``Z`` with probability ``p``: ``K_0 = sqrt(1-p) I``,
  ``K_1 = sqrt(p) Z``.
* **Depolarizing** (Nielsen-Chuang Eq. 8.102): with probability ``p`` the
  qubit becomes maximally mixed ``I/2``; equivalently each Pauli error
  ``X, Y, Z`` occurs with probability ``p/4``. Kraus set
  ``K_0 = sqrt(1 - 3p/4) I``, ``K_1 = sqrt(p/4) X``,
  ``K_2 = sqrt(p/4) Y``, ``K_3 = sqrt(p/4) Z``.

The depolarizing parametrisation here matches Nielsen & Chuang's
``rho -> (1 - p) rho + p I/2`` form, which is the convention every QEC
threshold paper uses. (Some texts use a different ``p`` that gives Kraus
weights ``1 - p, p/3, p/3, p/3``; we do not.)

References (in ``docs/reading-list.md``):

* Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  10th anniversary ed., chapter 8 (operator-sum representation).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from qec_project.linalg import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z

_KRAUS_TOL = 1e-10


def _check_prob(p: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"probability must lie in [0, 1]; got p={p}")
    return float(p)


def _as_density(rho: np.ndarray) -> np.ndarray:
    arr = np.asarray(rho, dtype=np.complex128)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(f"expected a square matrix, got shape {arr.shape}")
    return arr


def apply_channel(rho: np.ndarray, kraus: Sequence[np.ndarray]) -> np.ndarray:
    """Apply a Kraus channel ``E(rho) = sum_k K_k rho K_k^dagger``.

    The caller is responsible for the Kraus set being CPTP; use
    :func:`is_trace_preserving` to verify. Returns a new density matrix
    of the same shape as ``rho``.
    """
    out = np.zeros_like(_as_density(rho))
    for k in kraus:
        kk = np.asarray(k, dtype=np.complex128)
        out = out + kk @ rho @ kk.conj().T
    return out


def is_trace_preserving(kraus: Sequence[np.ndarray], atol: float = _KRAUS_TOL) -> bool:
    """Return True iff ``sum_k K_k^dagger K_k == I`` within ``atol``."""
    arrs = [np.asarray(k, dtype=np.complex128) for k in kraus]
    if not arrs:
        return False
    dim = arrs[0].shape[0]
    identity = np.eye(dim, dtype=np.complex128)
    total = sum(k.conj().T @ k for k in arrs)
    return bool(np.allclose(total, identity, atol=atol))


def bit_flip_kraus(p: float) -> tuple[np.ndarray, np.ndarray]:
    """Kraus operators for the bit-flip channel with error probability ``p``.

    Returns ``(K_0, K_1) = (sqrt(1-p) I, sqrt(p) X)``.
    """
    p = _check_prob(p)
    return (np.sqrt(1.0 - p) * PAULI_I, np.sqrt(p) * PAULI_X)


def phase_flip_kraus(p: float) -> tuple[np.ndarray, np.ndarray]:
    """Kraus operators for the phase-flip channel with error probability ``p``.

    Returns ``(K_0, K_1) = (sqrt(1-p) I, sqrt(p) Z)``.
    """
    p = _check_prob(p)
    return (np.sqrt(1.0 - p) * PAULI_I, np.sqrt(p) * PAULI_Z)


def depolarizing_kraus(
    p: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Kraus operators for the depolarizing channel with parameter ``p``.

    The channel sends ``rho -> (1 - p) rho + p I/2``. Equivalently each
    of ``X``, ``Y``, ``Z`` occurs with probability ``p / 4``. Kraus set:

        K_0 = sqrt(1 - 3p/4) I,
        K_1 = sqrt(p/4) X,
        K_2 = sqrt(p/4) Y,
        K_3 = sqrt(p/4) Z.
    """
    p = _check_prob(p)
    a = np.sqrt(1.0 - 3.0 * p / 4.0)
    b = np.sqrt(p / 4.0)
    return (a * PAULI_I, b * PAULI_X, b * PAULI_Y, b * PAULI_Z)


def bit_flip_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """Apply the bit-flip channel ``E(rho) = (1-p) rho + p X rho X``."""
    return apply_channel(rho, bit_flip_kraus(p))


def phase_flip_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """Apply the phase-flip channel ``E(rho) = (1-p) rho + p Z rho Z``."""
    return apply_channel(rho, phase_flip_kraus(p))


def depolarizing_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """Apply the depolarizing channel ``E(rho) = (1-p) rho + p I/2``.

    Implemented via the four-Kraus operator-sum form so the routine works
    on any single-qubit ``rho``; the closed-form ``(1-p) rho + p I/2`` is
    equivalent and falls out as a sanity check.
    """
    return apply_channel(rho, depolarizing_kraus(p))
