"""Small linear-algebra utilities reused across the curriculum.

These helpers are introduced in Phase 0.1 (`linear_algebra.ipynb`) and
relied upon from Phase 0.3 onward (parity-check matrices), Phase 1
(single-qubit unitaries, measurement), and Phase 2+ (Pauli operators on
multi-qubit registers, stabilizer formalism).

The convention is:

* Eigenvectors are returned as the columns of a matrix (matches
  ``numpy.linalg.eig``).
* Tensor / Kronecker products use Kronecker / big-endian ordering. For
  states this means ``tensor(|psi>, |phi>)`` places ``|psi>`` on the
  most-significant qubit; the basis indices read ``psi-bit, phi-bit``.
* All complex arrays use ``complex128``.
"""

from __future__ import annotations

from functools import reduce
from typing import Final

import numpy as np

PAULI_I: Final[np.ndarray] = np.array([[1, 0], [0, 1]], dtype=np.complex128)
PAULI_X: Final[np.ndarray] = np.array([[0, 1], [1, 0]], dtype=np.complex128)
PAULI_Y: Final[np.ndarray] = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
PAULI_Z: Final[np.ndarray] = np.array([[1, 0], [0, -1]], dtype=np.complex128)

PAULIS: Final[dict[str, np.ndarray]] = {
    "I": PAULI_I,
    "X": PAULI_X,
    "Y": PAULI_Y,
    "Z": PAULI_Z,
}


def is_unitary(matrix: np.ndarray, atol: float = 1e-10) -> bool:
    """Return True iff ``matrix`` is a square unitary within ``atol``.

    A matrix ``U`` is unitary when ``U @ U.conj().T == I``. Equivalently
    its columns form an orthonormal basis of the ambient complex space.
    """
    arr = np.asarray(matrix)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        return False
    identity = np.eye(arr.shape[0], dtype=np.complex128)
    return bool(np.allclose(arr @ arr.conj().T, identity, atol=atol))


def tensor(*matrices: np.ndarray) -> np.ndarray:
    """Variadic Kronecker product.

    ``tensor(A, B, C)`` is ``numpy.kron(numpy.kron(A, B), C)``. With no
    arguments a 1x1 identity is returned so that ``tensor()`` is a
    well-defined neutral element. The result dtype is ``complex128`` to
    avoid surprises when mixing real and complex inputs (e.g. a real
    state with a complex Pauli operator).
    """
    if not matrices:
        return np.array([[1.0 + 0j]], dtype=np.complex128)
    arrays = [np.asarray(m, dtype=np.complex128) for m in matrices]
    return reduce(np.kron, arrays)


def eigendecompose(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(eigenvalues, eigenvectors)`` for a square matrix.

    Eigenvectors are columns of the second return value, matching
    ``numpy.linalg.eig``. For the Hermitian Paulis ``X, Y, Z`` (and
    later, stabilizers) the eigenvalues come out real and equal to
    ``+/- 1``, but this helper stays general because we will reuse it
    for non-Hermitian operators downstream.
    """
    arr = np.asarray(matrix, dtype=np.complex128)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(f"expected a square matrix, got shape {arr.shape}")
    values, vectors = np.linalg.eig(arr)
    return values, vectors
