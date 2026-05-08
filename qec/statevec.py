"""A tiny NumPy state-vector simulator.

The goal is pedagogical, not performance: every operation is written so a reader
can map it directly back to the math. Qubit ordering follows the Qiskit
convention so cross-checks line up: qubit 0 is the *least-significant* bit of
the basis-state index, i.e. the state vector for n qubits is indexed by
    idx = q_{n-1} q_{n-2} ... q_1 q_0   (binary)
which means qubit q lives in axis (n - 1 - q) of the (2,)*n tensor reshape.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Single-qubit gate library (column vectors are |0>, |1>).
# ---------------------------------------------------------------------------
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)


def rx(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]],
        dtype=complex,
    )


# ---------------------------------------------------------------------------
# State construction
# ---------------------------------------------------------------------------
def zero_state(n: int) -> np.ndarray:
    """|0...0> on n qubits, returned as a length-2^n complex vector."""
    psi = np.zeros(2**n, dtype=complex)
    psi[0] = 1.0
    return psi


def basis_state(n: int, k: int) -> np.ndarray:
    """Computational basis state |k> on n qubits."""
    if not 0 <= k < 2**n:
        raise ValueError(f"basis index {k} out of range for {n} qubits")
    psi = np.zeros(2**n, dtype=complex)
    psi[k] = 1.0
    return psi


# ---------------------------------------------------------------------------
# Gate application via tensor reshape.
#
# We reshape psi from shape (2^n,) to (2,)*n, then move the target axis to
# position 0, contract the 2x2 gate against it, and move it back. This is the
# standard trick: applying a 1-qubit gate is O(2^n) and never builds the full
# 2^n x 2^n matrix.
# ---------------------------------------------------------------------------
def _axis_for_qubit(n: int, q: int) -> int:
    if not 0 <= q < n:
        raise ValueError(f"qubit index {q} out of range for {n} qubits")
    return n - 1 - q  # qubit 0 is the last (least-significant) tensor axis


def apply_1q(psi: np.ndarray, gate: np.ndarray, q: int) -> np.ndarray:
    """Apply a 2x2 gate to qubit q of an n-qubit state vector."""
    n = int(np.log2(psi.size))
    if 2**n != psi.size:
        raise ValueError("state vector length must be a power of 2")
    ax = _axis_for_qubit(n, q)
    t = psi.reshape((2,) * n)
    t = np.moveaxis(t, ax, 0)
    t = np.tensordot(gate, t, axes=([1], [0]))
    t = np.moveaxis(t, 0, ax)
    return t.reshape(2**n)


def apply_2q(psi: np.ndarray, gate: np.ndarray, q0: int, q1: int) -> np.ndarray:
    """Apply a 4x4 gate to qubits (q0, q1) of an n-qubit state vector.

    The gate matrix is interpreted with q0 as the most-significant of the two
    indices: rows/cols are ordered |q0 q1> = |00>, |01>, |10>, |11>.
    """
    if q0 == q1:
        raise ValueError("apply_2q requires two distinct qubits")
    n = int(np.log2(psi.size))
    if 2**n != psi.size:
        raise ValueError("state vector length must be a power of 2")
    ax0, ax1 = _axis_for_qubit(n, q0), _axis_for_qubit(n, q1)
    t = psi.reshape((2,) * n)
    # Move the two target axes to the front (ax0 then ax1 -> positions 0, 1).
    t = np.moveaxis(t, [ax0, ax1], [0, 1])
    g = gate.reshape(2, 2, 2, 2)  # [out0, out1, in0, in1]
    t = np.tensordot(g, t, axes=([2, 3], [0, 1]))
    # tensordot put the new (out0, out1) at the front; move them back.
    t = np.moveaxis(t, [0, 1], [ax0, ax1])
    return t.reshape(2**n)


# Canonical 2-qubit gates (q0 = control / first index, q1 = target / second).
CNOT = np.array(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
    dtype=complex,
)
CZ = np.diag([1, 1, 1, -1]).astype(complex)
SWAP = np.array(
    [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]],
    dtype=complex,
)


def cnot(psi: np.ndarray, control: int, target: int) -> np.ndarray:
    return apply_2q(psi, CNOT, control, target)


def cz(psi: np.ndarray, q0: int, q1: int) -> np.ndarray:
    return apply_2q(psi, CZ, q0, q1)


def swap(psi: np.ndarray, q0: int, q1: int) -> np.ndarray:
    return apply_2q(psi, SWAP, q0, q1)


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------
def probabilities(psi: np.ndarray) -> np.ndarray:
    """Probability of each computational-basis outcome."""
    return np.abs(psi) ** 2


def sample(psi: np.ndarray, shots: int = 1, rng: np.random.Generator | None = None) -> np.ndarray:
    """Draw `shots` Z-basis measurement outcomes (as integer indices)."""
    rng = rng or np.random.default_rng()
    p = probabilities(psi)
    p = p / p.sum()  # guard against tiny floating-point drift
    return rng.choice(p.size, size=shots, p=p)


def measure_qubit(
    psi: np.ndarray, q: int, rng: np.random.Generator | None = None
) -> tuple[int, np.ndarray]:
    """Project qubit q onto a Z-basis outcome; return (outcome, post-measurement state)."""
    rng = rng or np.random.default_rng()
    n = int(np.log2(psi.size))
    ax = _axis_for_qubit(n, q)
    t = psi.reshape((2,) * n)

    # Probability of outcome 0 = sum of |amp|^2 over the slice with axis ax = 0.
    p0 = np.sum(np.abs(np.take(t, 0, axis=ax)) ** 2)
    p0 = float(np.clip(p0, 0.0, 1.0))
    outcome = 0 if rng.random() < p0 else 1
    p_outcome = p0 if outcome == 0 else 1.0 - p0
    if p_outcome <= 0:
        raise RuntimeError("measured an outcome with zero probability — numerical bug")

    # Project: zero out the orthogonal slice, then renormalise.
    other = 1 - outcome
    t_proj = t.copy()
    sl = [slice(None)] * n
    sl[ax] = other
    t_proj[tuple(sl)] = 0.0
    t_proj = t_proj / np.sqrt(p_outcome)
    return outcome, t_proj.reshape(2**n)
