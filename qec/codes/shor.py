"""The Shor [[9, 1, 3]] code: the first true QEC code (Shor 1995).

Construction: concatenate the 3-qubit phase-flip code (outer) with the
3-qubit bit-flip code (inner). Each of the three "blocks" is a bit-flip
code; the blocks are then combined in the X basis (by writing the
phase-flip-code logical states `|+>_L` and `|->_L` in terms of the
encoded blocks).

Logical states:
    |0_L> = (|000> + |111>)(|000> + |111>)(|000> + |111>) / (2 sqrt(2))
    |1_L> = (|000> - |111>)(|000> - |111>)(|000> - |111>) / (2 sqrt(2))

There are 8 stabilizer generators on 9 qubits → 1 logical qubit. The code
has distance 3: it corrects any single-qubit Pauli error.

Stabilizers:
    Z-type, two per block (handling X errors within a block):
        Z_0 Z_1, Z_1 Z_2,    Z_3 Z_4, Z_4 Z_5,    Z_6 Z_7, Z_7 Z_8
    X-type, two between blocks (handling Z errors anywhere in a block):
        X_0 X_1 X_2 X_3 X_4 X_5,  X_3 X_4 X_5 X_6 X_7 X_8
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable

import numpy as np

from qec.pauli import Pauli

# ---------------------------------------------------------------------------
# Stabilizer generators
# ---------------------------------------------------------------------------
_Z_PAIR_STR = (
    "ZZIIIIIII",  # Z_0 Z_1
    "IZZIIIIII",  # Z_1 Z_2
    "IIIZZIIII",  # Z_3 Z_4
    "IIIIZZIII",  # Z_4 Z_5
    "IIIIIIZZI",  # Z_6 Z_7
    "IIIIIIIZZ",  # Z_7 Z_8
)
_X_BLOCK_STR = (
    "XXXXXXIII",  # X_0..X_5
    "IIIXXXXXX",  # X_3..X_8
)

Z_STABILIZERS = [Pauli.from_string(s) for s in _Z_PAIR_STR]
X_STABILIZERS = [Pauli.from_string(s) for s in _X_BLOCK_STR]
ALL_STABILIZERS = Z_STABILIZERS + X_STABILIZERS

# Logical operators. Standard choice (see Nielsen & Chuang §10.5):
#   logical Z = X_0 X_1 ... X_8 (or any odd-weight all-X column)
#   logical X = Z_0 Z_3 Z_6 (one Z per block)
LOGICAL_Z = Pauli.from_string("XXXXXXXXX")
LOGICAL_X = Pauli.from_string("ZIIZIIZII")


def _assert_valid() -> None:
    for a, b in itertools.combinations(ALL_STABILIZERS, 2):
        if not a.commutes_with(b):
            raise AssertionError(f"non-commuting stabilizers: {a!r}, {b!r}")
    for s in ALL_STABILIZERS:
        if not LOGICAL_X.commutes_with(s):
            raise AssertionError(f"logical X anticommutes with stabilizer {s!r}")
        if not LOGICAL_Z.commutes_with(s):
            raise AssertionError(f"logical Z anticommutes with stabilizer {s!r}")
    if LOGICAL_X.commutes_with(LOGICAL_Z):
        raise AssertionError("logical X and Z must anticommute")


_assert_valid()


# ---------------------------------------------------------------------------
# Syndrome extraction and minimum-weight decoding
# ---------------------------------------------------------------------------
def syndrome_for_error(error: Pauli) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return ((z_syndrome bits), (x_syndrome bits)) for an injected Pauli error.

    The Z-type generators detect X-component errors; the X-type generators
    detect Z-component errors. Each bit is `1` iff the corresponding generator
    anticommutes with the error.
    """
    if error.n != 9:
        raise ValueError("Shor errors must be 9-qubit Paulis")
    z_syn = tuple(0 if g.commutes_with(error) else 1 for g in Z_STABILIZERS)
    x_syn = tuple(0 if g.commutes_with(error) else 1 for g in X_STABILIZERS)
    return z_syn, x_syn


# Minimum-weight decoder, derived per block. Within block b ∈ {0, 1, 2}:
# the two Z_iZ_{i+1} generators detect X errors via the same syndrome table
# as the 3-qubit repetition code (note 06):
#     (s0, s1) = (0, 0) -> no X correction
#     (1, 0) -> X on qubit 0 of the block
#     (1, 1) -> X on qubit 1 of the block
#     (0, 1) -> X on qubit 2 of the block
# The two X-type generators X_0..X_5 and X_3..X_8 give a 2-bit syndrome that
# tells us which *block* a Z error lives in (we apply Z to one qubit of that
# block — by convention, the first):
#     (0, 0) -> no Z correction
#     (1, 0) -> Z on a qubit of block 0  (Z_0 by convention)
#     (1, 1) -> Z on a qubit of block 1  (Z_3)
#     (0, 1) -> Z on a qubit of block 2  (Z_6)
def _x_recovery_for_block(s0: int, s1: int) -> int | None:
    return {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}[(s0, s1)]


def _z_recovery_qubit_for_block(x_syn: tuple[int, int]) -> int | None:
    return {(0, 0): None, (1, 0): 0, (1, 1): 3, (0, 1): 6}[x_syn]


def _recovery_pauli(z_syn: tuple[int, ...], x_syn: tuple[int, ...]) -> Pauli:
    x = np.zeros(9, dtype=np.int8)
    z = np.zeros(9, dtype=np.int8)
    # Block-by-block X recovery from Z-type syndromes.
    for b, (s0, s1) in enumerate(((z_syn[0], z_syn[1]), (z_syn[2], z_syn[3]), (z_syn[4], z_syn[5]))):
        which = _x_recovery_for_block(s0, s1)
        if which is not None:
            x[3 * b + which] = 1
    # Z recovery from X-type syndromes.
    qubit = _z_recovery_qubit_for_block((x_syn[0], x_syn[1]))
    if qubit is not None:
        z[qubit] = 1
    return Pauli(x, z, 0)


def correct(error: Pauli) -> Pauli:
    """Apply the syndrome-table decoder. Return error * recovery."""
    z_syn, x_syn = syndrome_for_error(error)
    rec = _recovery_pauli(z_syn, x_syn)
    return error * rec


def is_logical_failure(residual: Pauli) -> tuple[bool, bool]:
    """Return (logical_x, logical_z) for the residual."""
    return (
        not residual.commutes_with(LOGICAL_Z),
        not residual.commutes_with(LOGICAL_X),
    )


# ---------------------------------------------------------------------------
# Verification / Monte-Carlo
# ---------------------------------------------------------------------------
def _enumerate_paulis(weight: int) -> Iterable[Pauli]:
    n = 9
    for positions in itertools.combinations(range(n), weight):
        for letters in itertools.product("XYZ", repeat=weight):
            x = np.zeros(n, dtype=np.int8)
            z = np.zeros(n, dtype=np.int8)
            phase = 0
            for q, ltr in zip(positions, letters):
                if ltr == "X":
                    x[q] = 1
                elif ltr == "Z":
                    z[q] = 1
                else:
                    x[q] = z[q] = 1
                    phase = (phase + 1) & 3
            yield Pauli(x, z, phase)


def all_weight1_errors_corrected() -> bool:
    for E in _enumerate_paulis(1):
        residual = correct(E)
        lx, lz = is_logical_failure(residual)
        if lx or lz:
            return False
    return True


def monte_carlo_logical_error(
    p: float, shots: int, rng: np.random.Generator | None = None
) -> float:
    """Sample depolarising errors at rate p / qubit (Pauli replaced by one
    of {X, Y, Z} uniformly) and estimate logical failure rate."""
    rng = rng or np.random.default_rng()
    fails = 0
    for _ in range(shots):
        x = np.zeros(9, dtype=np.int8)
        z = np.zeros(9, dtype=np.int8)
        phase = 0
        for q in range(9):
            if rng.random() < 1 - p:
                continue
            kind = rng.integers(0, 3)
            if kind == 0:
                x[q] = 1
            elif kind == 1:
                z[q] = 1
            else:
                x[q] = z[q] = 1
                phase = (phase + 1) & 3
        E = Pauli(x, z, phase)
        residual = correct(E)
        lx, lz = is_logical_failure(residual)
        if lx or lz:
            fails += 1
    return fails / shots
