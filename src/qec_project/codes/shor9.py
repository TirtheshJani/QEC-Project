"""The Shor [[9,1,3]] code: concatenation of the 3-qubit phase-flip code
with the 3-qubit bit-flip code.

Encodes 1 logical qubit into 9 physical qubits. Corrects any single-qubit
Pauli error (X, Y, or Z on any one of the 9 qubits). Distance 3.

Conventions:

* Qubit ordering is big-endian (matches ``numpy.kron`` and
  ``qec_project.linalg.tensor``): Pauli string ``"P_0 P_1 ... P_8"`` lists
  the operator on qubit 0 first.
* Blocks are ``{0, 1, 2}``, ``{3, 4, 5}``, ``{6, 7, 8}``; block
  representatives are ``0, 3, 6``.
* Logical operators are the minimum-weight representatives
  ``X_L = Z_0 Z_3 Z_6`` and ``Z_L = X_0 X_1 X_2``. The labels look
  swapped versus naive expectation because the *outer* code is the
  phase-flip code: its logical X is a tensor of Zs on the three block
  representatives (which swaps each block between
  ``(|000>+|111>)/sqrt(2)`` and ``(|000>-|111>)/sqrt(2)``), and its
  logical Z is an X on each qubit of any one block (which contributes
  +1 on ``|0_L>`` and -1 on ``|1_L>``). Both have weight 3, anticommute
  with each other, and commute with all 8 stabilizers; the code
  distance is therefore 3.

References (in ``docs/reading-list.md``):

* Peter W. Shor. *Scheme for reducing decoherence in quantum computer
  memory.* Phys. Rev. A 52, R2493 (1995). doi:10.1103/PhysRevA.52.R2493.
* Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  section 10.2 (the 9-qubit code).
"""

from __future__ import annotations

import logging
from functools import reduce

import numpy as np
from qiskit import QuantumCircuit

from qec_project.linalg import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z

logger = logging.getLogger(__name__)

_SINGLE_PAULIS: dict[str, np.ndarray] = {
    "I": PAULI_I,
    "X": PAULI_X,
    "Y": PAULI_Y,
    "Z": PAULI_Z,
}

_STABILIZERS: tuple[str, ...] = (
    "ZZIIIIIII",
    "IZZIIIIII",
    "IIIZZIIII",
    "IIIIZZIII",
    "IIIIIIZZI",
    "IIIIIIIZZ",
    "XXXXXXIII",
    "IIIXXXXXX",
)

_LOGICAL_X: str = "ZIIZIIZII"  # Z_0 Z_3 Z_6: swaps |0_L> <-> |1_L>
_LOGICAL_Z: str = "XXXIIIIII"  # X_0 X_1 X_2: +1 on |0_L>, -1 on |1_L>


def _single_pauli_anticommute(p: str, q: str) -> bool:
    """Return True iff single-qubit Paulis ``p`` and ``q`` anticommute."""
    if p == "I" or q == "I":
        return False
    return p != q


def pauli_commute(p: str, q: str) -> bool:
    """Return True iff Pauli strings ``p`` and ``q`` commute.

    Two strings commute iff they anticommute at an even number of qubit
    positions. Empty / mismatched-length inputs raise ``ValueError``.
    """
    if len(p) != len(q):
        raise ValueError(f"length mismatch: {len(p)} vs {len(q)}")
    if not p:
        raise ValueError("Pauli strings must be non-empty")
    if not (set(p) <= {"I", "X", "Y", "Z"} and set(q) <= {"I", "X", "Y", "Z"}):
        raise ValueError("Pauli strings must contain only I/X/Y/Z")
    anti = sum(
        1 for a, b in zip(p, q, strict=True) if _single_pauli_anticommute(a, b)
    )
    return anti % 2 == 0


def pauli_string_to_matrix(p: str) -> np.ndarray:
    """Build the dense matrix of a Pauli string under big-endian ordering."""
    if not p:
        raise ValueError("Pauli string must be non-empty")
    if not set(p) <= {"I", "X", "Y", "Z"}:
        raise ValueError(f"unknown Pauli character in {p!r}")
    return reduce(np.kron, (_SINGLE_PAULIS[c] for c in p))


def _syndrome_of_pauli(error: str, stabilizers: tuple[str, ...]) -> tuple[int, ...]:
    """Return the bitwise syndrome of a Pauli error: 1 iff it anticommutes."""
    return tuple(0 if pauli_commute(error, s) else 1 for s in stabilizers)


def _build_recovery_table(
    stabilizers: tuple[str, ...],
) -> dict[tuple[int, ...], str]:
    """Build syndrome -> recovery-string lookup over single-qubit errors.

    Enumerates the 28 single-qubit Pauli errors (``I`` plus ``X/Y/Z`` on
    each of 9 qubits). Each gets its 8-bit syndrome via
    :func:`pauli_commute`. On collision (degenerate errors that produce
    the same syndrome) the first one encountered in iteration order wins:
    qubit 0 first, then ``X`` before ``Y`` before ``Z``. Applying any
    member of the degenerate set restores the logical state because the
    errors differ by a stabilizer.
    """
    table: dict[tuple[int, ...], str] = {}
    table[tuple([0] * len(stabilizers))] = "I" * 9
    for q in range(9):
        for p in ("X", "Y", "Z"):
            err = ["I"] * 9
            err[q] = p
            err_string = "".join(err)
            syndrome = _syndrome_of_pauli(err_string, stabilizers)
            if syndrome not in table:
                table[syndrome] = err_string
    return table


class Shor9Code:
    """The Shor [[9,1,3]] code.

    Concatenation of the outer 3-qubit phase-flip code (on block
    representatives 0, 3, 6) with the inner 3-qubit bit-flip code (in
    each block).

    Attributes
    ----------
    n, k, d:
        Block length 9, logical qubits 1, distance 3.
    """

    n: int = 9
    k: int = 1
    d: int = 3

    def __init__(self) -> None:
        self._stabilizers = _STABILIZERS
        self._logical_x = _LOGICAL_X
        self._logical_z = _LOGICAL_Z
        self._recovery_table = _build_recovery_table(self._stabilizers)
        logger.info(
            "Shor9Code: [[9,1,3]], 8 stabilizers, recovery table size=%d",
            len(self._recovery_table),
        )

    def stabilizers(self) -> list[str]:
        """Return the 8 stabilizer generators as length-9 Pauli strings."""
        return list(self._stabilizers)

    def logical_operators(self) -> dict[str, str]:
        """Return canonical minimum-weight reps ``{'X': ..., 'Z': ...}``."""
        return {"X": self._logical_x, "Z": self._logical_z}

    def encode_circuit(self, logical_bit: int = 0) -> QuantumCircuit:
        """Build the 9-qubit encoding circuit for ``|logical_bit>``.

        Layout:

        * Outer phase-flip code on representatives ``(0, 3, 6)``:
          ``CX(0,3)``, ``CX(0,6)``, then ``H`` on each of ``0, 3, 6``.
        * Inner bit-flip code per block: ``CX(0,1)``, ``CX(0,2)``,
          ``CX(3,4)``, ``CX(3,5)``, ``CX(6,7)``, ``CX(6,8)``.

        ``logical_bit=0`` produces ``|0_L>``; ``logical_bit=1`` prepends
        an ``X`` on qubit 0 so the input to the encoder is ``|1>``.
        """
        if logical_bit not in (0, 1):
            raise ValueError(f"logical_bit must be 0 or 1; got {logical_bit}")
        qc = QuantumCircuit(self.n, name=f"Shor9 |{logical_bit}_L>")
        if logical_bit == 1:
            qc.x(0)
        # Outer phase-flip: spread data into block reps, then H on each rep.
        qc.cx(0, 3)
        qc.cx(0, 6)
        qc.h(0)
        qc.h(3)
        qc.h(6)
        # Inner bit-flip: copy each block rep to its two block partners.
        qc.cx(0, 1)
        qc.cx(0, 2)
        qc.cx(3, 4)
        qc.cx(3, 5)
        qc.cx(6, 7)
        qc.cx(6, 8)
        return qc

    def syndrome_of(self, pauli: str) -> tuple[int, ...]:
        """Return the 8-bit syndrome of a Pauli-string error."""
        if len(pauli) != self.n:
            raise ValueError(
                f"expected length-{self.n} Pauli string; got {len(pauli)}"
            )
        return _syndrome_of_pauli(pauli, self._stabilizers)

    def recovery(self, syndrome: tuple[int, ...]) -> str:
        """Return the recovery Pauli string for a given syndrome.

        Unknown syndromes (those produced by weight-2+ errors not in the
        single-qubit table) map to the identity recovery.
        """
        if len(syndrome) != len(self._stabilizers):
            raise ValueError(
                f"expected length-{len(self._stabilizers)} syndrome; "
                f"got {len(syndrome)}"
            )
        return self._recovery_table.get(
            tuple(int(b) for b in syndrome), "I" * self.n
        )
