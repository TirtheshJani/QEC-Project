"""Single-qubit Kraus noise channels.

Phase 1 promotion of the bit-flip, phase-flip and depolarizing channels.
All channels are returned as tuples of Kraus operators so callers can
both apply them via :func:`apply_channel` and inspect the structure.

Convention. The depolarizing channel uses the "p/3 per Pauli" form:

    K0 = sqrt(1 - p) I,    K_{X,Y,Z} = sqrt(p / 3) {X, Y, Z}.

By the identity ``X rho X + Y rho Y + Z rho Z = 2 I - rho`` this is
equivalent to the mixture ``(1 - 4p/3) rho + (4p/3) (I/2)``. The
maximally mixed fixed point is reached at ``p = 3/4`` (Nielsen & Chuang,
sec. 8.3.4).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

__all__ = [
    "I",
    "X",
    "Y",
    "Z",
    "apply_channel",
    "bit_flip_kraus",
    "composed_depolarizing_probabilities",
    "depolarizing_kraus",
    "is_trace_preserving",
    "phase_flip_kraus",
]


# Pauli matrices in the computational basis. The single-letter names match
# the physics literature; ruff E741 is silenced because `I` is the standard
# symbol for the identity Pauli throughout QEC papers.
I: np.ndarray = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128)  # noqa: E741
X: np.ndarray = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
Y: np.ndarray = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
Z: np.ndarray = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def _check_prob(p: float) -> None:
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"probability must lie in [0, 1]; got {p}")


def bit_flip_kraus(p: float) -> tuple[np.ndarray, np.ndarray]:
    """Return Kraus operators for the bit-flip channel with flip probability ``p``."""
    _check_prob(p)
    k0 = np.sqrt(1.0 - p) * I
    k1 = np.sqrt(p) * X
    return k0, k1


def phase_flip_kraus(p: float) -> tuple[np.ndarray, np.ndarray]:
    """Return Kraus operators for the phase-flip channel with flip probability ``p``."""
    _check_prob(p)
    k0 = np.sqrt(1.0 - p) * I
    k1 = np.sqrt(p) * Z
    return k0, k1


def depolarizing_kraus(
    p: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Kraus operators for the depolarizing channel.

    Uses the standard four-operator form with weight ``sqrt(p / 3)`` on
    each Pauli and ``sqrt(1 - p)`` on the identity.
    """
    _check_prob(p)
    k0 = np.sqrt(1.0 - p) * I
    s = np.sqrt(p / 3.0)
    return k0, s * X, s * Y, s * Z


def apply_channel(rho: np.ndarray, kraus_ops: Sequence[np.ndarray]) -> np.ndarray:
    """Apply ``sum_i K_i rho K_i^dagger`` to the density matrix ``rho``."""
    rho_c = np.asarray(rho, dtype=np.complex128)
    out = np.zeros_like(rho_c)
    for k in kraus_ops:
        kc = np.asarray(k, dtype=np.complex128)
        out = out + kc @ rho_c @ kc.conj().T
    return out


def is_trace_preserving(kraus_ops: Sequence[np.ndarray], atol: float = 1e-10) -> bool:
    """Return True iff ``sum_i K_i^dagger K_i`` equals the identity within ``atol``."""
    kraus_ops = list(kraus_ops)
    if not kraus_ops:
        return False
    dim = kraus_ops[0].shape[0]
    acc = np.zeros((dim, dim), dtype=np.complex128)
    for k in kraus_ops:
        kc = np.asarray(k, dtype=np.complex128)
        acc = acc + kc.conj().T @ kc
    return bool(np.allclose(acc, np.eye(dim, dtype=np.complex128), atol=atol))


def composed_depolarizing_probabilities(p: float) -> dict[str, float]:
    """Marginal Pauli outcome probabilities for the depolarizing channel.

    Each Kraus operator can be interpreted as applying a Pauli with the
    indicated probability; this is the convention used by Stim's
    ``DEPOLARIZE1`` instruction once translated to its standard Pauli
    decomposition. Useful as a sanity-check fixture in tests.
    """
    _check_prob(p)
    return {"I": 1.0 - p, "X": p / 3.0, "Y": p / 3.0, "Z": p / 3.0}
