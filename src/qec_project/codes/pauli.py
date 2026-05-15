"""Symplectic Pauli-group representation.

Each Pauli on ``n`` qubits is stored as two boolean vectors ``x`` and ``z``
of length ``n`` plus a global phase in ``{+1, -1, +i, -i}``. The mapping is
the standard one: position ``j`` carries

    (x_j, z_j) = (0, 0) -> I
                 (1, 0) -> X
                 (0, 1) -> Z
                 (1, 1) -> Y    (= i * X * Z conventionally; see below).

Multiplication is bitwise XOR on (x, z), and the phase is tracked
position-by-position using the standard rule. Commutation of two Paulis
P and Q on ``n`` qubits is decided by the symplectic inner product

    omega(P, Q) = (x_P . z_Q) + (z_P . x_Q)   (mod 2),

which is 0 iff P and Q commute. References: Nielsen & Chuang, sec. 10.5;
Gottesman, *Stabilizer Codes and Quantum Error Correction*, ch. 3.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

# Phase of a single-qubit Pauli "XZ" relative to the symplectic letter Y.
# We adopt the convention Y = i X Z, so when multiplying we accumulate
# a factor of i for every qubit where the left operand has a Z that meets
# the right operand's X. The tables below enumerate the exact phases
# letter-by-letter under that convention.

# Single-qubit symbol -> (x_bit, z_bit).
_LETTER_TO_BITS: dict[str, tuple[bool, bool]] = {
    "I": (False, False),
    "X": (True, False),
    "Z": (False, True),
    "Y": (True, True),
}

_BITS_TO_LETTER: dict[tuple[bool, bool], str] = {v: k for k, v in _LETTER_TO_BITS.items()}

_VALID_PHASES: tuple[complex, ...] = (1 + 0j, -1 + 0j, 1j, -1j)


def _bits_for_letter(letter: str) -> tuple[bool, bool]:
    try:
        return _LETTER_TO_BITS[letter]
    except KeyError as exc:
        raise ValueError(f"Invalid Pauli letter {letter!r}") from exc


def _phase_for_pair(left: str, right: str) -> complex:
    """Return the scalar phase produced by multiplying two single-qubit Paulis.

    The phase tables follow directly from the convention Y = i X Z and the
    standard Pauli algebra. Concretely:

        X * Y = + i Z       Y * X = - i Z
        Y * Z = + i X       Z * Y = - i X
        Z * X = + i Y       X * Z = - i Y

    All other products are real with phase +1.
    """

    if left == "I" or right == "I" or left == right:
        return 1 + 0j
    pos = {("X", "Y"), ("Y", "Z"), ("Z", "X")}
    return 1j if (left, right) in pos else -1j


@dataclass
class Pauli:
    """A signed Pauli operator on ``n`` qubits in symplectic form."""

    n: int
    x: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=bool))
    z: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=bool))
    phase: complex = 1 + 0j

    def __post_init__(self) -> None:
        if self.x.dtype != np.bool_:
            self.x = self.x.astype(bool)
        if self.z.dtype != np.bool_:
            self.z = self.z.astype(bool)
        if self.x.shape != (self.n,) or self.z.shape != (self.n,):
            raise ValueError(
                f"x/z must have shape ({self.n},); got {self.x.shape} and {self.z.shape}"
            )
        if self.phase not in _VALID_PHASES:
            raise ValueError(f"phase must be in {_VALID_PHASES}; got {self.phase}")

    @classmethod
    def from_string(cls, s: str) -> Pauli:
        """Parse ``"IXYZ"`` or ``"+IXYZ"``/``"-IXYZ"``/``"iIXYZ"``/``"-iIXYZ"``."""

        phase: complex = 1 + 0j
        body = s
        if body.startswith("-i"):
            phase = -1j
            body = body[2:]
        elif body.startswith("+i"):
            phase = 1j
            body = body[2:]
        elif body.startswith("i"):
            phase = 1j
            body = body[1:]
        elif body.startswith("+"):
            body = body[1:]
        elif body.startswith("-"):
            phase = -1 + 0j
            body = body[1:]
        n = len(body)
        x = np.zeros(n, dtype=bool)
        z = np.zeros(n, dtype=bool)
        for j, letter in enumerate(body):
            bx, bz = _bits_for_letter(letter)
            x[j] = bx
            z[j] = bz
        return cls(n=n, x=x, z=z, phase=phase)

    def to_string(self) -> str:
        letters = "".join(_BITS_TO_LETTER[(bool(self.x[j]), bool(self.z[j]))] for j in range(self.n))
        if self.phase == 1 + 0j:
            return f"+{letters}"
        if self.phase == -1 + 0j:
            return f"-{letters}"
        if self.phase == 1j:
            return f"+i{letters}"
        return f"-i{letters}"

    def weight(self) -> int:
        # A Pauli letter is "non-identity" iff at least one of (x, z) is set.
        return int(np.count_nonzero(self.x | self.z))

    def copy(self) -> Pauli:
        return Pauli(n=self.n, x=self.x.copy(), z=self.z.copy(), phase=self.phase)

    def commutes_with(self, other: Pauli) -> bool:
        if other.n != self.n:
            raise ValueError(f"Cannot compare Paulis on {self.n} and {other.n} qubits")
        # Symplectic inner product modulo 2.
        sym = int(np.sum(self.x & other.z) + np.sum(self.z & other.x)) & 1
        return sym == 0

    def __mul__(self, other: Pauli) -> Pauli:
        if other.n != self.n:
            raise ValueError(f"Cannot multiply Paulis on {self.n} and {other.n} qubits")
        new_x = self.x ^ other.x
        new_z = self.z ^ other.z
        # Accumulate phase contribution letter-by-letter. This is the
        # simplest correct approach; for our scale (n <= 7 most of the
        # time) it is plenty fast and avoids subtle symplectic-cocycle bugs.
        accumulated: complex = self.phase * other.phase
        for j in range(self.n):
            left = _BITS_TO_LETTER[(bool(self.x[j]), bool(self.z[j]))]
            right = _BITS_TO_LETTER[(bool(other.x[j]), bool(other.z[j]))]
            accumulated *= _phase_for_pair(left, right)
        return Pauli(n=self.n, x=new_x, z=new_z, phase=accumulated)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pauli):
            return NotImplemented
        return (
            self.n == other.n
            and np.array_equal(self.x, other.x)
            and np.array_equal(self.z, other.z)
            and self.phase == other.phase
        )

    def __hash__(self) -> int:
        return hash((self.n, self.x.tobytes(), self.z.tobytes(), self.phase))

    def __repr__(self) -> str:
        return f"Pauli({self.to_string()})"


def commutes_with_set(p: Pauli, stabilizers: Sequence[Pauli]) -> bool:
    """Return True iff ``p`` commutes with every element of ``stabilizers``."""

    return all(p.commutes_with(s) for s in stabilizers)


def stabilizer_group_commutes(stabs: Sequence[Pauli]) -> bool:
    """Return True iff every pair of operators in ``stabs`` commutes."""

    for i, a in enumerate(stabs):
        for b in stabs[i + 1:]:
            if not a.commutes_with(b):
                return False
    return True
