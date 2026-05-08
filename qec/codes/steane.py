"""The Steane [[7, 1, 3]] code.

A CSS code derived from the classical [7, 4] Hamming code: both the X-type
and Z-type stabilizer matrices are the [7, 4] Hamming parity-check matrix.
This gives:
- 6 stabilizer generators (3 X-type, 3 Z-type) on 7 qubits.
- 1 logical qubit.
- distance 3: corrects any single-qubit Pauli error.

The Steane code is the smallest CSS code, and the cleanest example of how
classical coding theory ports straight into QEC. Logical Clifford gates are
*transversal* (apply the same single-qubit gate to all 7 physical qubits),
which is why Steane appears in fault-tolerance discussions (Phase 7).

This module provides:
- The stabilizer generators (as Pauli strings).
- The Hamming parity-check matrix and its inverse for syndrome decoding.
- A Pauli-sampling correction routine: given an injected Pauli error, return
  whether the syndrome-table decoder leaves a logical Pauli on the qubit.
- Exhaustive verification: every single-qubit Pauli error is correctable.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable

import numpy as np

from qec.pauli import Pauli

# ---------------------------------------------------------------------------
# Hamming [7,4] parity-check matrix.
# Columns 1..7 are the binary representations of 1..7. Three rows = three
# parity checks. Any non-zero column is unique, so a single bit error gives a
# unique non-zero syndrome (= the column index of the bad bit).
# ---------------------------------------------------------------------------
HAMMING_H = np.array(
    [
        [0, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 0, 1, 1],
        [1, 0, 1, 0, 1, 0, 1],
    ],
    dtype=np.int8,
)

# Map syndrome (s2, s1, s0) read as integer 1..7 to the qubit it points at.
# qubit q (0-indexed) corresponds to column q+1 of HAMMING_H, since column 0
# would be the all-zero (no-error) syndrome.
_SYNDROME_TO_QUBIT: dict[int, int] = {
    int(np.dot([4, 2, 1], HAMMING_H[:, q])): q for q in range(7)
}
assert _SYNDROME_TO_QUBIT == {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}


def _stabilizer_strings() -> tuple[list[str], list[str]]:
    """Return (X-type generator strings, Z-type generator strings).

    Each string is 7 characters in {I, X, Z}. The X-type generators are
    rows of the Hamming parity-check matrix written as X / I patterns; same
    for Z-type.
    """
    x_gens = []
    z_gens = []
    for row in HAMMING_H:
        x_gens.append("".join("X" if b else "I" for b in row))
        z_gens.append("".join("Z" if b else "I" for b in row))
    return x_gens, z_gens


X_STABILIZERS_STR, Z_STABILIZERS_STR = _stabilizer_strings()
X_STABILIZERS: list[Pauli] = [Pauli.from_string(s) for s in X_STABILIZERS_STR]
Z_STABILIZERS: list[Pauli] = [Pauli.from_string(s) for s in Z_STABILIZERS_STR]
ALL_STABILIZERS: list[Pauli] = X_STABILIZERS + Z_STABILIZERS

# Logical operators: any odd-weight all-X (resp. all-Z) string that
# anticommutes with the corresponding non-trivial cosets. The simplest
# choice (and the one most commonly cited): logical X = X on all 7 qubits,
# logical Z = Z on all 7 qubits.
LOGICAL_X = Pauli.from_string("XXXXXXX")
LOGICAL_Z = Pauli.from_string("ZZZZZZZ")


# ---------------------------------------------------------------------------
# Stabilizer-group sanity (asserted at import time)
# ---------------------------------------------------------------------------
def _assert_valid_stabilizer_code() -> None:
    """All stabilizers must pairwise commute, and logical X / Z must commute
    with every stabilizer (so they preserve the codespace) but anticommute
    with each other (so they form a logical Pauli pair)."""
    for a, b in itertools.combinations(ALL_STABILIZERS, 2):
        if not a.commutes_with(b):
            raise AssertionError(f"non-commuting stabilizers: {a!r}, {b!r}")
    for s in ALL_STABILIZERS:
        if not LOGICAL_X.commutes_with(s):
            raise AssertionError(f"logical X anticommutes with {s!r}")
        if not LOGICAL_Z.commutes_with(s):
            raise AssertionError(f"logical Z anticommutes with {s!r}")
    if LOGICAL_X.commutes_with(LOGICAL_Z):
        raise AssertionError("logical X and Z must anticommute")


_assert_valid_stabilizer_code()


# ---------------------------------------------------------------------------
# Syndrome extraction (symbolic / Pauli-sampling)
# ---------------------------------------------------------------------------
def syndrome_for_error(error: Pauli) -> tuple[int, int]:
    """Return (sx, sz), each a 3-bit integer 0..7, packing the X-type and
    Z-type syndromes.

    sx[k] = 1 iff X-stabilizer k anticommutes with `error` (i.e. iff the
    error has a non-trivial Z component on the qubits stabilizer k touches).
    Conversely sz[k] reads the X part of the error.

    Encoded so that sx interpreted as an integer in [1, 7] *is* the qubit
    index (0-based, +1) of the unique single-Z error producing it; same for sz
    and single-X errors.
    """
    if error.n != 7:
        raise ValueError("Steane errors must be 7-qubit Paulis")
    # Z-part of the error = error.z; X-stabilizers anticommute with Z-errors.
    # Hamming row k anticommutes with the error iff sum_q (HAMMING_H[k, q] * error.z[q]) is odd.
    sx_bits = (HAMMING_H @ error.z) % 2  # length-3 array
    sz_bits = (HAMMING_H @ error.x) % 2
    sx = int(4 * sx_bits[0] + 2 * sx_bits[1] + sx_bits[2])
    sz = int(4 * sz_bits[0] + 2 * sz_bits[1] + sz_bits[2])
    return sx, sz


def _recovery_pauli(sx: int, sz: int) -> Pauli:
    """Build the Pauli the decoder applies given a (sx, sz) syndrome.

    Uses the standard CSS minimum-weight decoder: each non-zero sx points to
    the unique qubit where a single Z error would have produced it; same for
    sz and X. (sx=0, sz=0) → identity. This decoder is optimal against
    weight-1 Pauli noise.
    """
    x = np.zeros(7, dtype=np.int8)
    z = np.zeros(7, dtype=np.int8)
    if sz != 0:
        x[_SYNDROME_TO_QUBIT[sz]] = 1
    if sx != 0:
        z[_SYNDROME_TO_QUBIT[sx]] = 1
    return Pauli(x, z, 0)


def correct(error: Pauli) -> Pauli:
    """Apply the syndrome-table decoder to an error: return error * recovery.

    If the result is in the stabilizer group (modulo phase), the decoder
    succeeded: the codespace is unchanged. If the result is a logical
    operator (anticommutes with logical X or logical Z), the decoder failed:
    the encoded qubit has been flipped.

    For weight-1 input errors the result is always trivial (identity in
    symplectic form), confirming distance 3.
    """
    sx, sz = syndrome_for_error(error)
    rec = _recovery_pauli(sx, sz)
    return error * rec


def is_logical_failure(residual: Pauli) -> tuple[bool, bool]:
    """For a residual Pauli (post-recovery), return (logical_x, logical_z):
    whether logical X or logical Z (or both) has been applied.

    The residual is in the normaliser of the stabilizer group; the four cosets
    correspond to the four logical Paulis I_L / X_L / Z_L / Y_L. We detect by
    commutation with the *logical* operators (which act trivially on the
    stabilizer group, so this gives a clean coset label).
    """
    return (
        not residual.commutes_with(LOGICAL_Z),  # X_L anticommutes with Z_L
        not residual.commutes_with(LOGICAL_X),  # Z_L anticommutes with X_L
    )


# ---------------------------------------------------------------------------
# Exhaustive verification / Monte-Carlo
# ---------------------------------------------------------------------------
def _enumerate_paulis(weight: int) -> Iterable[Pauli]:
    """Yield every Pauli on 7 qubits with given non-trivial weight."""
    n = 7
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
                else:  # "Y"
                    x[q] = z[q] = 1
                    phase = (phase + 1) & 3
            yield Pauli(x, z, phase)


def all_weight1_errors_corrected() -> bool:
    """Smoke test: every weight-1 Pauli error is corrected to identity."""
    for E in _enumerate_paulis(1):
        residual = correct(E)
        # In symplectic form residual must be the identity (its x and z are
        # all zero); the phase may be ±1 / ±i but acts trivially on states.
        if residual.weight() != 0:
            return False
    return True


def monte_carlo_logical_error(
    p: float, shots: int, rng: np.random.Generator | None = None
) -> float:
    """Sample independent depolarising errors at rate `p` per qubit and
    estimate the logical-failure rate after recovery.

    'Logical failure' means the residual lands in any non-identity coset
    (X_L, Z_L, or Y_L). For small p this scales as O(p^2).

    Convention: rate `p` means "with probability p, replace the qubit with
    one of {X, Y, Z} uniformly" — i.e. with probability p/3 each, matching
    the IBM / Aer "depolarizing_error" convention.
    """
    rng = rng or np.random.default_rng()
    fails = 0
    for _ in range(shots):
        # Sample a Pauli error per qubit.
        x = np.zeros(7, dtype=np.int8)
        z = np.zeros(7, dtype=np.int8)
        phase = 0
        for q in range(7):
            r = rng.random()
            if r < 1 - p:
                continue
            r2 = rng.integers(0, 3)
            if r2 == 0:
                x[q] = 1
            elif r2 == 1:
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
