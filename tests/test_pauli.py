"""Tests for the symplectic Pauli representation.

The hardest property — that our symplectic commutation predicate agrees
with the literal commutator of the 2^n x 2^n matrices — is the
ground-truth property test required by CLAUDE.md.
"""

from __future__ import annotations

import itertools
from typing import cast

import numpy as np
import pytest

from qec_project.codes.pauli import (
    Pauli,
    commutes_with_set,
    stabilizer_group_commutes,
)

# Single-qubit Pauli matrices (computational basis).
I_MAT = np.array([[1, 0], [0, 1]], dtype=complex)
X_MAT = np.array([[0, 1], [1, 0]], dtype=complex)
Y_MAT = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z_MAT = np.array([[1, 0], [0, -1]], dtype=complex)

_LETTER_TO_MAT = {"I": I_MAT, "X": X_MAT, "Y": Y_MAT, "Z": Z_MAT}


def pauli_to_matrix(p: Pauli) -> np.ndarray:
    """Build the 2^n x 2^n complex matrix for a Pauli operator (with phase)."""
    s = p.to_string()
    # Strip leading sign / phase tokens that to_string may emit.
    body = s
    for prefix in ("+i", "-i", "+", "-"):
        if body.startswith(prefix):
            body = body[len(prefix):]
            break
    mat = np.array([[1.0 + 0.0j]])
    for letter in body:
        mat = np.kron(mat, _LETTER_TO_MAT[letter])
    return p.phase * mat


def random_pauli(n: int, rng: np.random.Generator) -> Pauli:
    letters = "".join(rng.choice(list("IXYZ"), size=n))
    return Pauli.from_string(letters)


def test_from_string_roundtrip_random() -> None:
    rng = np.random.default_rng(20260515)
    for _ in range(50):
        n = int(rng.integers(1, 8))
        letters = "".join(rng.choice(list("IXYZ"), size=n))
        p = Pauli.from_string(letters)
        assert p.to_string().lstrip("+") == letters
        assert p.n == n


def test_from_string_with_sign_prefix() -> None:
    for prefix, expected_phase in (("+", 1 + 0j), ("-", -1 + 0j), ("i", 1j), ("-i", -1j)):
        p = Pauli.from_string(f"{prefix}XYZ")
        assert p.phase == expected_phase
        assert p.n == 3


def test_pauli_squared_is_identity_up_to_phase() -> None:
    rng = np.random.default_rng(0xC0FFEE)
    for _ in range(30):
        p = random_pauli(int(rng.integers(1, 6)), rng)
        sq = p * p
        assert not sq.x.any()
        assert not sq.z.any()
        # For real (unsigned) I, X, Y, Z, the square is +I exactly.
        assert sq.phase == 1 + 0j


def test_single_qubit_multiplication_table() -> None:
    # Reference: standard Pauli algebra. X*Y = iZ, Y*X = -iZ, etc.
    table: dict[tuple[str, str], tuple[str, complex]] = {
        ("I", "I"): ("I", 1 + 0j),
        ("I", "X"): ("X", 1 + 0j),
        ("I", "Y"): ("Y", 1 + 0j),
        ("I", "Z"): ("Z", 1 + 0j),
        ("X", "I"): ("X", 1 + 0j),
        ("X", "X"): ("I", 1 + 0j),
        ("X", "Y"): ("Z", 1j),
        ("X", "Z"): ("Y", -1j),
        ("Y", "I"): ("Y", 1 + 0j),
        ("Y", "X"): ("Z", -1j),
        ("Y", "Y"): ("I", 1 + 0j),
        ("Y", "Z"): ("X", 1j),
        ("Z", "I"): ("Z", 1 + 0j),
        ("Z", "X"): ("Y", 1j),
        ("Z", "Y"): ("X", -1j),
        ("Z", "Z"): ("I", 1 + 0j),
    }
    for (a, b), (letter, phase) in table.items():
        result = Pauli.from_string(a) * Pauli.from_string(b)
        expected = Pauli.from_string(letter)
        expected.phase = phase
        assert result.x.tolist() == expected.x.tolist()
        assert result.z.tolist() == expected.z.tolist()
        assert result.phase == phase, f"{a}*{b}: phase {result.phase} != {phase}"


def test_weight_counts_non_identity_positions() -> None:
    assert Pauli.from_string("IIII").weight() == 0
    assert Pauli.from_string("IXIY").weight() == 2
    assert Pauli.from_string("XYZX").weight() == 4
    assert Pauli.from_string("ZIIZ").weight() == 2


def matrices_commute(a: np.ndarray, b: np.ndarray) -> bool:
    return np.allclose(a @ b, b @ a, atol=1e-10)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_symplectic_commutation_matches_matrix_truth(n: int) -> None:
    # Exhaustive over all 4^n unsigned Pauli pairs for n in {1, 2, 3}.
    rng = np.random.default_rng(2026_05_15 + n)
    letters_iter = itertools.product("IXYZ", repeat=n)
    paulis = [Pauli.from_string("".join(t)) for t in letters_iter]
    # n=3 -> 64 elements -> 64^2 = 4096 pairs; still fast.
    for p, q in itertools.product(paulis, repeat=2):
        sym_commute = p.commutes_with(q)
        mat_commute = matrices_commute(pauli_to_matrix(p), pauli_to_matrix(q))
        assert sym_commute == mat_commute, (
            f"n={n}: {p.to_string()} vs {q.to_string()} "
            f"symplectic={sym_commute} matrix={mat_commute}"
        )
    # Also random signed/imag-phased Paulis; phase must not change commutation.
    for _ in range(20):
        p = random_pauli(n, rng)
        q = random_pauli(n, rng)
        p.phase = cast(complex, rng.choice([1 + 0j, -1 + 0j, 1j, -1j]))
        q.phase = cast(complex, rng.choice([1 + 0j, -1 + 0j, 1j, -1j]))
        assert p.commutes_with(q) == matrices_commute(pauli_to_matrix(p), pauli_to_matrix(q))


def test_pauli_multiplication_matches_matrix_truth_two_qubits() -> None:
    rng = np.random.default_rng(42)
    for _ in range(40):
        a = random_pauli(2, rng)
        b = random_pauli(2, rng)
        prod = a * b
        lhs = pauli_to_matrix(prod)
        rhs = pauli_to_matrix(a) @ pauli_to_matrix(b)
        assert np.allclose(lhs, rhs, atol=1e-10)


def test_commutes_with_set_helper() -> None:
    stabs = [Pauli.from_string("XX"), Pauli.from_string("ZZ")]
    assert commutes_with_set(Pauli.from_string("YY"), stabs)
    assert not commutes_with_set(Pauli.from_string("XI"), stabs)


def test_stabilizer_group_commutes_helper() -> None:
    good = [Pauli.from_string("XX"), Pauli.from_string("ZZ")]
    bad = [Pauli.from_string("XI"), Pauli.from_string("ZZ")]
    assert stabilizer_group_commutes(good)
    assert not stabilizer_group_commutes(bad)


def test_mul_raises_on_size_mismatch() -> None:
    with pytest.raises(ValueError):
        _ = Pauli.from_string("XX") * Pauli.from_string("XXX")
