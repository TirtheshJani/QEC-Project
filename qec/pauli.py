"""The Pauli group on n qubits, in symplectic form.

Every n-qubit Pauli is represented by two binary vectors x, z in Z_2^n and a
phase in {0, 1, 2, 3} corresponding to {+1, +i, -1, -i}, where the operator is

    P = phase_factor * X^{x_0} Z^{z_0}  ⊗  X^{x_1} Z^{z_1}  ⊗  ...  ⊗  X^{x_{n-1}} Z^{z_{n-1}}

and a single-qubit factor X^a Z^b is read as I, X, Z, or Y for (a,b) =
(0,0), (1,0), (0,1), (1,1) respectively (with Y = i X Z).

Why symplectic form: it makes the two operations we use most — multiplication
and commutation — into bit arithmetic over GF(2). Building the 2^n x 2^n
matrix is only ever needed for cross-checking with state-vector simulators.

Qubit-index convention: qubit 0 is the LEFTMOST factor in the tensor product
*here*, which is the OPPOSITE of the Qiskit / qec.statevec little-endian
convention. We pick this ordering because the symplectic / tableau literature
(Aaronson-Gottesman, Gottesman's thesis) reads left-to-right; we explicitly
reverse when calling matrix() so the resulting numpy matrix matches the
statevec convention. See `Pauli.matrix` for the bridge.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qec.statevec import I as _I
from qec.statevec import X as _X
from qec.statevec import Y as _Y
from qec.statevec import Z as _Z

_PHASE_FACTORS = {0: 1 + 0j, 1: 0 + 1j, 2: -1 + 0j, 3: 0 - 1j}
_PHASE_LABELS = {0: "+", 1: "+i", 2: "-", 3: "-i"}
# In the symplectic encoding, the operator is i^phase * X^x * Z^z. So the
# *standard* Y matrix Y = i*X*Z corresponds to (x=1, z=1) plus an implicit
# +1 contribution to the phase per Y. _XZ_FROM_PAULI handles that on parse;
# _PAULI_LETTER_FROM_XZ is used by repr after we've subtracted those Y phases.
_PAULI_LETTER_FROM_XZ = {(0, 0): "I", (1, 0): "X", (0, 1): "Z", (1, 1): "Y"}
# (xz_bits, extra_phase): "Y" carries an extra +i, others carry no extra phase.
_XZ_FROM_PAULI = {
    "I": ((0, 0), 0),
    "X": ((1, 0), 0),
    "Y": ((1, 1), 1),
    "Z": ((0, 1), 0),
}


@dataclass
class Pauli:
    """An n-qubit Pauli operator in (x, z, phase) form.

    Multiplication, commutation, and weight are bit operations. Use
    `from_string`, `matrix`, and `__repr__` to interoperate with the rest of
    the codebase.
    """

    x: np.ndarray  # int8, shape (n,)
    z: np.ndarray  # int8, shape (n,)
    phase: int  # 0..3, meaning phase = i^phase

    def __post_init__(self) -> None:
        self.x = np.asarray(self.x, dtype=np.int8) & 1
        self.z = np.asarray(self.z, dtype=np.int8) & 1
        if self.x.shape != self.z.shape or self.x.ndim != 1:
            raise ValueError("x and z must be 1-D arrays of the same length")
        self.phase = int(self.phase) & 3

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------
    @property
    def n(self) -> int:
        return int(self.x.size)

    @classmethod
    def identity(cls, n: int) -> Pauli:
        return cls(np.zeros(n, dtype=np.int8), np.zeros(n, dtype=np.int8), 0)

    @classmethod
    def from_string(cls, s: str) -> Pauli:
        """Parse a string like '+IXYZ', '-XYZI', '+iXX', '-iY'.

        Whitespace and an optional leading sign / 'i' are accepted; the
        remaining characters must each be one of I/X/Y/Z. Qubit 0 is the
        FIRST listed character (left-to-right).
        """
        s = s.replace(" ", "").replace("_", "")
        if not s:
            raise ValueError("empty Pauli string")
        phase = 0
        if s[0] == "+":
            s = s[1:]
        elif s[0] == "-":
            phase = 2
            s = s[1:]
        if s.startswith("i"):
            phase = (phase + 1) & 3
            s = s[1:]
        elif s.startswith("-i"):
            phase = (phase + 3) & 3
            s = s[2:]
        n = len(s)
        x = np.zeros(n, dtype=np.int8)
        z = np.zeros(n, dtype=np.int8)
        for i, ch in enumerate(s.upper()):
            if ch not in _XZ_FROM_PAULI:
                raise ValueError(f"unknown Pauli character {ch!r} in {s!r}")
            (xi, zi), extra = _XZ_FROM_PAULI[ch]
            x[i], z[i] = xi, zi
            phase = (phase + extra) & 3  # each Y contributes +i to the phase
        return cls(x, z, phase)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        # When we display "Y" we are absorbing one factor of i per qubit
        # whose (x, z) bits are both 1; subtract that from the phase to get
        # the *displayed* sign / i prefix.
        n_y = int(np.sum(self.x & self.z))
        displayed_phase = (self.phase - n_y) & 3
        body = "".join(
            _PAULI_LETTER_FROM_XZ[(int(xi), int(zi))] for xi, zi in zip(self.x, self.z)
        )
        return f"{_PHASE_LABELS[displayed_phase]}{body}"

    # ------------------------------------------------------------------
    # Algebra
    # ------------------------------------------------------------------
    def commutes_with(self, other: Pauli) -> bool:
        """Two Paulis commute iff their symplectic inner product is zero mod 2.

        sigma((x1,z1), (x2,z2)) = x1 . z2 + z1 . x2  (mod 2)
        """
        if self.n != other.n:
            raise ValueError("commutes_with: qubit counts differ")
        s = int(np.dot(self.x, other.z) + np.dot(self.z, other.x)) & 1
        return s == 0

    def __mul__(self, other: Pauli) -> Pauli:
        """Pauli multiplication. Phase tracking is the only subtle part.

        For a single qubit, X^a Z^b * X^c Z^d = (-1)^{b*c} X^{a+c} Z^{b+d},
        so over n qubits the phase picks up an extra (-1)^{sum_i b_i * c_i}
        on top of the two operators' own phases.
        """
        if self.n != other.n:
            raise ValueError("Pauli multiplication: qubit counts differ")
        new_x = (self.x ^ other.x).astype(np.int8)
        new_z = (self.z ^ other.z).astype(np.int8)

        # Per-qubit phase from XZ-anticommutation: each occurrence of
        #   (X^a Z^b)(X^c Z^d) -> i^(2 b c) * X^{a^c} Z^{b^d}
        # is a factor of (-1)^{b*c}, contributing 2*b*c to the phase exponent.
        phase = (self.phase + other.phase + 2 * int(np.dot(self.z, other.x))) & 3
        return Pauli(new_x, new_z, phase)

    def __neg__(self) -> Pauli:
        return Pauli(self.x.copy(), self.z.copy(), (self.phase + 2) & 3)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pauli):
            return NotImplemented
        return (
            self.n == other.n
            and self.phase == other.phase
            and np.array_equal(self.x, other.x)
            and np.array_equal(self.z, other.z)
        )

    def __hash__(self) -> int:
        return hash((self.phase, self.x.tobytes(), self.z.tobytes()))

    def weight(self) -> int:
        """Number of qubits on which this Pauli acts non-trivially."""
        return int(np.sum((self.x | self.z).astype(int)))

    def is_identity(self) -> bool:
        return self.weight() == 0 and self.phase == 0

    # ------------------------------------------------------------------
    # Bridge to dense matrices (for cross-checking only)
    # ------------------------------------------------------------------
    def matrix(self) -> np.ndarray:
        """Build the dense 2^n x 2^n matrix.

        Operator convention: P = i^phase * (kron over qubits of X^x_q @ Z^z_q).
        We compute each per-qubit factor as a small matrix product so that the
        result is consistent with __mul__ (where (x=1,z=1,phase=0) means X*Z
        = -i*Y, not +Y).

        Qubit ordering: this Pauli class lists qubit 0 as the *leftmost*
        factor; qec.statevec / Qiskit make qubit 0 the LSB of the basis-state
        index. We reverse the factor order before kron-ing so the matrix
        matches the statevec convention.
        """
        factors = []
        for xi, zi in zip(self.x, self.z):
            f = _I.copy()
            if int(xi):
                f = _X @ f
            if int(zi):
                f = f @ _Z
            factors.append(f)
        # Build kron with qubit 0 as the LSB factor (innermost / rightmost),
        # matching qec.statevec / Qiskit. With np.kron(A, B), A is the more-
        # significant bit, so we kron each higher-numbered qubit on the left.
        M = factors[0]
        for F in factors[1:]:
            M = np.kron(F, M)
        return _PHASE_FACTORS[self.phase] * M


# ---------------------------------------------------------------------------
# Conjugation under Clifford gates: how a Pauli transforms when sandwiched
# between G and G^dagger. Used both as a sanity reference and by the
# stabilizer simulator (note: the simulator works directly on the tableau and
# does not call these — they exist for tests and pedagogy).
# ---------------------------------------------------------------------------
def conjugate_h(P: Pauli, q: int) -> Pauli:
    """H X H = Z, H Z H = X, H Y H = -Y. So swap x_q <-> z_q; add phase 2 if both were 1."""
    x, z, phase = P.x.copy(), P.z.copy(), P.phase
    if x[q] and z[q]:
        phase = (phase + 2) & 3  # Y -> -Y
    x[q], z[q] = z[q], x[q]
    return Pauli(x, z, phase)


def conjugate_s(P: Pauli, q: int) -> Pauli:
    """S X S^dag = Y, S Z S^dag = Z, S Y S^dag = -X.

    Symplectic action on (x_q, z_q): if x_q = 1, toggle z_q and add +i to the
    phase (this single rule covers both X -> Y and Y -> -X correctly under
    the i^phase * X^x Z^z encoding).
    """
    x, z, phase = P.x.copy(), P.z.copy(), P.phase
    if x[q]:
        z[q] ^= 1
        phase = (phase + 1) & 3
    return Pauli(x, z, phase)


def conjugate_cnot(P: Pauli, control: int, target: int) -> Pauli:
    """CNOT propagation rules:
        I_c X_t -> I_c X_t       (X on target unchanged)
        X_c I_t -> X_c X_t       (X on control propagates to target)
        I_c Z_t -> Z_c Z_t       (Z on target propagates to control)
        Z_c I_t -> Z_c I_t       (Z on control unchanged)
    Y = i X Z so the rules compose; phases cancel because we update both x
    and z simultaneously.
    """
    if control == target:
        raise ValueError("conjugate_cnot: control and target must differ")
    x, z = P.x.copy(), P.z.copy()
    x[target] ^= x[control]
    z[control] ^= z[target]
    return Pauli(x, z, P.phase)
