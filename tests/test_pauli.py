"""Tests for qec/pauli.py.

The Pauli class is the foundation of Phase 3 (stabilizer formalism), so these
tests are deliberately exhaustive: every pair of single-qubit Paulis is
multiplied symbolically and compared against the matrix product, every Clifford
conjugation rule (H, S, CNOT) is verified against G @ P @ G^dagger, and a
batch of multi-qubit Paulis are round-tripped through string parsing.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import pytest

from qec import statevec as sv
from qec.pauli import (
    Pauli,
    conjugate_cnot,
    conjugate_h,
    conjugate_s,
)


SINGLES = ["I", "X", "Y", "Z"]


# ---------------------------------------------------------------------------
# Parsing / repr round-trip
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("s", ["+I", "X", "Y", "Z", "+iX", "-X", "-iY", "+IXYZ", "-XXZZ"])
def test_string_round_trip(s):
    P = Pauli.from_string(s)
    # repr should produce a canonical form parseable back to the same Pauli.
    P2 = Pauli.from_string(repr(P))
    assert P == P2


def test_y_string_means_standard_y():
    """Pauli.from_string('Y').matrix() must equal the standard Y matrix."""
    Y_std = np.array([[0, -1j], [1j, 0]], dtype=complex)
    assert np.allclose(Pauli.from_string("Y").matrix(), Y_std)


def test_repr_signs():
    assert repr(Pauli.from_string("X")) == "+X"
    assert repr(Pauli.from_string("-X")) == "-X"
    assert repr(Pauli.from_string("+iZ")) == "+iZ"
    assert repr(Pauli.from_string("-iY")) == "-iY"


# ---------------------------------------------------------------------------
# Single-qubit multiplication: every pair vs explicit matrix product
# ---------------------------------------------------------------------------
def test_single_qubit_products_match_matrices():
    for a, b in product(SINGLES, repeat=2):
        Pa, Pb = Pauli.from_string(a), Pauli.from_string(b)
        out = Pa * Pb
        ref = Pa.matrix() @ Pb.matrix()
        assert np.allclose(out.matrix(), ref, atol=1e-12), f"{a} * {b}"


def test_pauli_squares_are_identity():
    for a in ("X", "Y", "Z"):
        P = Pauli.from_string(a)
        assert (P * P).matrix().shape == (2, 2)
        assert np.allclose((P * P).matrix(), np.eye(2), atol=1e-12)


def test_anticommutators():
    """Distinct non-identity Paulis anticommute; identical ones commute."""
    for a, b in product("XYZ", repeat=2):
        Pa, Pb = Pauli.from_string(a), Pauli.from_string(b)
        if a == b:
            assert Pa.commutes_with(Pb)
        else:
            assert not Pa.commutes_with(Pb)


# ---------------------------------------------------------------------------
# Multi-qubit multiplication and commutation
# ---------------------------------------------------------------------------
def test_two_qubit_product_against_matrices():
    rng = np.random.default_rng(0)
    for _ in range(20):
        s1 = "".join(rng.choice(list("IXYZ"), size=3))
        s2 = "".join(rng.choice(list("IXYZ"), size=3))
        P1, P2 = Pauli.from_string(s1), Pauli.from_string(s2)
        out = (P1 * P2).matrix()
        ref = P1.matrix() @ P2.matrix()
        assert np.allclose(out, ref, atol=1e-12), f"{s1} * {s2}"


def test_commutes_with_matches_matrix_check():
    rng = np.random.default_rng(1)
    for _ in range(20):
        s1 = "".join(rng.choice(list("IXYZ"), size=4))
        s2 = "".join(rng.choice(list("IXYZ"), size=4))
        P1, P2 = Pauli.from_string(s1), Pauli.from_string(s2)
        from_bits = P1.commutes_with(P2)
        M1, M2 = P1.matrix(), P2.matrix()
        from_matrix = np.allclose(M1 @ M2, M2 @ M1, atol=1e-12)
        assert from_bits == from_matrix, f"{s1}, {s2}"


def test_weight_counts_non_identity_qubits():
    assert Pauli.from_string("IXYZ").weight() == 3
    assert Pauli.from_string("IIII").weight() == 0
    assert Pauli.from_string("XXXX").weight() == 4
    assert Pauli.identity(5).weight() == 0


# ---------------------------------------------------------------------------
# Clifford conjugation rules: G @ P @ G^dagger
# ---------------------------------------------------------------------------
def _gate_matrix_on_qubit(gate: np.ndarray, q: int, n: int) -> np.ndarray:
    """Build I ⊗ ... ⊗ gate ⊗ ... ⊗ I in qec.statevec / Qiskit ordering."""
    ops = [np.eye(2, dtype=complex)] * n
    ops[n - 1 - q] = gate  # qubit 0 = LSB axis
    M = ops[0]
    for op in ops[1:]:
        M = np.kron(M, op)
    return M


def _two_qubit_matrix_on(gate4x4: np.ndarray, q0: int, q1: int, n: int) -> np.ndarray:
    """Build the n-qubit operator that applies gate4x4 with q0 as the
    most-significant of the two indices (matching qec.statevec.apply_2q)."""
    psi_basis = np.eye(2**n, dtype=complex)
    out = np.empty_like(psi_basis)
    from qec.statevec import apply_2q

    for k in range(2**n):
        out[:, k] = apply_2q(psi_basis[:, k], gate4x4, q0, q1)
    return out


@pytest.mark.parametrize("p_str", ["X", "Y", "Z", "I", "+iX", "-Y"])
def test_conjugate_h_matches_matrix(p_str):
    n = 1
    P = Pauli.from_string(p_str)
    Hmat = _gate_matrix_on_qubit(sv.H, 0, n)
    expected = Hmat @ P.matrix() @ Hmat.conj().T
    got = conjugate_h(P, 0).matrix()
    assert np.allclose(got, expected, atol=1e-12)


@pytest.mark.parametrize("p_str", ["X", "Y", "Z", "I", "+iX", "-Y"])
def test_conjugate_s_matches_matrix(p_str):
    n = 1
    P = Pauli.from_string(p_str)
    Smat = _gate_matrix_on_qubit(sv.S, 0, n)
    expected = Smat @ P.matrix() @ Smat.conj().T
    got = conjugate_s(P, 0).matrix()
    assert np.allclose(got, expected, atol=1e-12)


def test_conjugate_h_on_qubit_in_multi_qubit_pauli():
    P = Pauli.from_string("XYZ")  # 3 qubits: qubit 0 = X, qubit 1 = Y, qubit 2 = Z
    n = 3
    for q in range(n):
        Hmat = _gate_matrix_on_qubit(sv.H, q, n)
        expected = Hmat @ P.matrix() @ Hmat.conj().T
        got = conjugate_h(P, q).matrix()
        assert np.allclose(got, expected, atol=1e-12), f"H on q={q}"


def test_conjugate_cnot_matches_matrix():
    # qec.statevec.CNOT has q0 as control, q1 as target.
    n = 2
    CNOTm = _two_qubit_matrix_on(sv.CNOT, 0, 1, n)
    for s in ("II", "XI", "IX", "ZI", "IZ", "YI", "IY", "XX", "ZZ", "YY", "XZ", "YZ", "ZY"):
        P = Pauli.from_string(s)
        expected = CNOTm @ P.matrix() @ CNOTm.conj().T
        got = conjugate_cnot(P, 0, 1).matrix()
        assert np.allclose(got, expected, atol=1e-12), s


def test_conjugate_cnot_propagation_rules():
    """The four canonical CNOT propagation identities (note 02)."""
    XI = Pauli.from_string("XI")
    IX = Pauli.from_string("IX")
    ZI = Pauli.from_string("ZI")
    IZ = Pauli.from_string("IZ")
    XX = Pauli.from_string("XX")
    ZZ = Pauli.from_string("ZZ")

    # qec.pauli lists qubit 0 as the LEFTMOST character. CNOT(control=0,
    # target=1) means: X on q0 propagates to q1; Z on q1 propagates to q0.
    assert conjugate_cnot(XI, 0, 1) == XX
    assert conjugate_cnot(IX, 0, 1) == IX
    assert conjugate_cnot(ZI, 0, 1) == ZI
    assert conjugate_cnot(IZ, 0, 1) == ZZ
