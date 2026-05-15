"""The Steane [[7,1,3]] CSS code.

Steane is the CSS code obtained from the classical Hamming [7,4,3] code
used for both bit-flip and phase-flip protection. The standard parity-check
matrix

        1 0 1 0 1 0 1
    H = 0 1 1 0 0 1 1
        0 0 0 1 1 1 1

gives three X-type and three Z-type stabilizers. The logical X and Z are
any row of the (dual) generator matrix; the all-ones operator is a common
choice but weight 3 is the minimum, so we pick a weight-3 representative
in the same coset. We use ``X_L = X_4 X_5 X_6 X_7`` truncated against
``H``: in fact ``X X X X I I I`` and ``Z Z Z Z I I I`` (positions 0..3)
both commute with every stabilizer and anti-commute with each other -
but those are weight-4. The standard weight-3 logical representatives
``X_L = X_2 X_4 X_6`` (positions 1, 3, 5 in 0-indexed) and
``Z_L = Z_2 Z_4 Z_6`` are used here.

References: Nielsen & Chuang sec. 10.4.2; Gottesman thesis sec. 3.4.
"""

from __future__ import annotations

from qec_project.codes.pauli import Pauli, commutes_with_set, stabilizer_group_commutes


def _pauli_at(positions: tuple[int, ...], letter: str, n: int = 7) -> Pauli:
    body = ["I"] * n
    for p in positions:
        body[p] = letter
    return Pauli.from_string("".join(body))


# Hamming(7,4) parity-check matrix rows (0-indexed columns). Each row
# touches the columns whose 1-indexed position has the corresponding bit
# set in binary: this is the canonical Hamming construction.
_HAMMING_ROWS: tuple[tuple[int, ...], ...] = (
    (0, 2, 4, 6),  # columns whose 1-indexed position has bit 0 set: 1,3,5,7
    (1, 2, 5, 6),  # bit 1 set: 2,3,6,7
    (3, 4, 5, 6),  # bit 2 set: 4,5,6,7
)


def steane_stabilizers() -> list[Pauli]:
    """Return the six Steane stabilizers: three X-type then three Z-type."""

    x_stabs = [_pauli_at(row, "X") for row in _HAMMING_ROWS]
    z_stabs = [_pauli_at(row, "Z") for row in _HAMMING_ROWS]
    return x_stabs + z_stabs


def steane_logical_x() -> Pauli:
    # Weight-3 representative: the support {0, 1, 2} is *not* used because it
    # equals the first X-stabilizer truncated; instead we pick {4, 5, 6}
    # which is in the same coset as the all-X operator modulo the X
    # stabilizers, and which commutes with every Z-stabilizer (each Z-stab
    # row above contains an even number of elements of {4, 5, 6}: rows
    # touch {4, 6}, {5, 6}, and {4, 5, 6} -> sizes 2, 2, 3. Row 3 has
    # odd overlap, so {4,5,6} does NOT commute with the third Z stabilizer.
    # We therefore use the textbook representative on qubits {0, 1, 6}? No -
    # cleanest is the row of the dual generator; equivalently the support
    # of the all-1s codeword reduced modulo a stabilizer. Concretely the
    # all-X operator ``XXXXXXX`` is logical and has weight 7; multiplying
    # by the first X-stabilizer (support {0,2,4,6}) gives the weight-3
    # operator on positions {1, 3, 5}. That is our canonical choice.
    return _pauli_at((1, 3, 5), "X")


def steane_logical_z() -> Pauli:
    return _pauli_at((1, 3, 5), "Z")


def verify_steane() -> bool:
    """Check the defining algebraic properties of the Steane code."""

    stabs = steane_stabilizers()
    if not stabilizer_group_commutes(stabs):
        return False
    lx = steane_logical_x()
    lz = steane_logical_z()
    if not commutes_with_set(lx, stabs):
        return False
    if not commutes_with_set(lz, stabs):
        return False
    # Logical X and Z must anti-commute for a single encoded qubit.
    return not lx.commutes_with(lz)
