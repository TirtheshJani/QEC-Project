"""Tests for the Shor [[9,1,3]] code helper (Phase 2.2)."""

from __future__ import annotations

import itertools

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from qiskit.quantum_info import Statevector

from qec_project.codes.shor9 import (
    Shor9Code,
    pauli_commute,
    pauli_string_to_matrix,
)


def _qiskit_to_bigendian(data: np.ndarray, n_qubits: int) -> np.ndarray:
    """Reverse Qiskit little-endian basis ordering to numpy.kron big-endian."""
    return (
        data.reshape([2] * n_qubits)
        .transpose(*range(n_qubits - 1, -1, -1))
        .reshape(-1)
    )


# ---------- stabilizer-string sanity ----------


def test_stabilizers_have_correct_count_and_length() -> None:
    code = Shor9Code()
    stabs = code.stabilizers()
    assert len(stabs) == 8
    assert all(isinstance(s, str) and len(s) == 9 for s in stabs)
    assert all(set(s) <= {"I", "X", "Y", "Z"} for s in stabs)


def test_stabilizers_pairwise_commute() -> None:
    code = Shor9Code()
    stabs = code.stabilizers()
    for a, b in itertools.combinations(stabs, 2):
        assert pauli_commute(a, b), f"{a} and {b} do not commute"


def test_logical_x_anticommutes_with_logical_z() -> None:
    code = Shor9Code()
    ops = code.logical_operators()
    assert not pauli_commute(ops["X"], ops["Z"])


def test_logical_operators_commute_with_all_stabilizers() -> None:
    code = Shor9Code()
    for name, logical in code.logical_operators().items():
        for stab in code.stabilizers():
            assert pauli_commute(logical, stab), (
                f"logical {name}={logical} does not commute with stabilizer {stab}"
            )


def test_logical_operators_have_minimum_weight_three() -> None:
    code = Shor9Code()
    for name, logical in code.logical_operators().items():
        weight = sum(1 for c in logical if c != "I")
        assert weight == code.d, f"{name} weight {weight} != distance {code.d}"


# ---------- Pauli-string utilities ----------


def test_pauli_commute_rejects_mismatched_length() -> None:
    with pytest.raises(ValueError):
        pauli_commute("XX", "XYZ")


def test_pauli_commute_rejects_empty() -> None:
    with pytest.raises(ValueError):
        pauli_commute("", "")


def test_pauli_commute_rejects_unknown_character() -> None:
    with pytest.raises(ValueError):
        pauli_commute("XQ", "XX")


def test_pauli_string_to_matrix_single_qubit() -> None:
    from qec_project.linalg import PAULI_X

    assert np.allclose(pauli_string_to_matrix("X"), PAULI_X)


def test_pauli_string_to_matrix_two_qubit_ZZ() -> None:
    # Z ⊗ Z has +1 on |00> and |11>, -1 on |01> and |10>.
    M = pauli_string_to_matrix("ZZ")
    expected = np.diag([1, -1, -1, 1]).astype(np.complex128)
    assert np.allclose(M, expected)


def test_pauli_string_to_matrix_rejects_empty() -> None:
    with pytest.raises(ValueError):
        pauli_string_to_matrix("")


def test_pauli_string_to_matrix_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        pauli_string_to_matrix("XQ")


# ---------- encoding circuit ----------


def test_encoded_zero_is_plus1_eigenstate_of_every_stabilizer() -> None:
    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=0)
    sv = _qiskit_to_bigendian(Statevector(qc).data, n_qubits=9)
    for stab in code.stabilizers():
        M = pauli_string_to_matrix(stab)
        overlap = complex(np.vdot(sv, M @ sv))
        assert abs(overlap - 1.0) < 1e-9, f"stab {stab}: <psi|S|psi> = {overlap}"


def test_encoded_one_is_plus1_eigenstate_of_every_stabilizer() -> None:
    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=1)
    sv = _qiskit_to_bigendian(Statevector(qc).data, n_qubits=9)
    for stab in code.stabilizers():
        M = pauli_string_to_matrix(stab)
        overlap = complex(np.vdot(sv, M @ sv))
        assert abs(overlap - 1.0) < 1e-9, f"stab {stab}: <psi|S|psi> = {overlap}"


def test_encoded_one_is_minus1_eigenstate_of_logical_z() -> None:
    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=1)
    sv = _qiskit_to_bigendian(Statevector(qc).data, n_qubits=9)
    Z_L = pauli_string_to_matrix(code.logical_operators()["Z"])
    overlap = complex(np.vdot(sv, Z_L @ sv))
    assert abs(overlap - (-1.0)) < 1e-9, f"<1_L|Z_L|1_L> = {overlap}"


def test_encode_circuit_rejects_invalid_logical_bit() -> None:
    code = Shor9Code()
    with pytest.raises(ValueError):
        code.encode_circuit(logical_bit=2)


def test_encoded_zero_matches_algebraic_form() -> None:
    """|0_L> = ((|000> + |111>) / sqrt(2))^{⊗3} under big-endian ordering."""
    code = Shor9Code()
    sv = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(0)).data, n_qubits=9
    )
    ket_000 = np.zeros(8, dtype=np.complex128)
    ket_000[0] = 1.0
    ket_111 = np.zeros(8, dtype=np.complex128)
    ket_111[7] = 1.0
    block_plus = (ket_000 + ket_111) / np.sqrt(2.0)
    algebraic = np.kron(np.kron(block_plus, block_plus), block_plus)
    assert abs(np.vdot(sv, algebraic)) > 1 - 1e-9


def test_encoded_one_matches_algebraic_form() -> None:
    """|1_L> = ((|000> - |111>) / sqrt(2))^{⊗3} under big-endian ordering."""
    code = Shor9Code()
    sv = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(1)).data, n_qubits=9
    )
    ket_000 = np.zeros(8, dtype=np.complex128)
    ket_000[0] = 1.0
    ket_111 = np.zeros(8, dtype=np.complex128)
    ket_111[7] = 1.0
    block_minus = (ket_000 - ket_111) / np.sqrt(2.0)
    algebraic = np.kron(np.kron(block_minus, block_minus), block_minus)
    assert abs(np.vdot(sv, algebraic)) > 1 - 1e-9


# ---------- syndrome / recovery API shape ----------


def test_syndrome_of_identity_is_all_zero() -> None:
    code = Shor9Code()
    assert code.syndrome_of("I" * 9) == tuple([0] * 8)


def test_syndrome_of_rejects_wrong_length() -> None:
    code = Shor9Code()
    with pytest.raises(ValueError):
        code.syndrome_of("XX")


def test_recovery_rejects_wrong_length_syndrome() -> None:
    code = Shor9Code()
    with pytest.raises(ValueError):
        code.recovery((0, 0, 0))


def test_recovery_of_zero_syndrome_is_identity() -> None:
    code = Shor9Code()
    assert code.recovery(tuple([0] * 8)) == "I" * 9


def test_recovery_returns_pauli_string_for_each_single_qubit_error() -> None:
    code = Shor9Code()
    for q, p in itertools.product(range(9), ("X", "Y", "Z")):
        err = ["I"] * 9
        err[q] = p
        err_string = "".join(err)
        syndrome = code.syndrome_of(err_string)
        recovery_string = code.recovery(syndrome)
        assert isinstance(recovery_string, str) and len(recovery_string) == 9
        assert set(recovery_string) <= {"I", "X", "Y", "Z"}


# ---------- exhaustive 27-error correction ----------


def _exhaustive_correction(code: Shor9Code, logical_bit: int) -> list[str]:
    """Return a list of failure descriptions; empty if all 27 errors corrected."""
    encoded = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(logical_bit)).data, n_qubits=9
    )
    failures: list[str] = []
    for q, p in itertools.product(range(9), ("X", "Y", "Z")):
        err = ["I"] * 9
        err[q] = p
        err_string = "".join(err)
        E = pauli_string_to_matrix(err_string)
        corrupted = E @ encoded
        syndrome = code.syndrome_of(err_string)
        recovery_string = code.recovery(syndrome)
        R = pauli_string_to_matrix(recovery_string)
        restored = R @ corrupted
        overlap = abs(np.vdot(encoded, restored))
        if not overlap > 1 - 1e-9:
            failures.append(
                f"|{logical_bit}_L> err={err_string} "
                f"syn={syndrome} rec={recovery_string} "
                f"|<psi|psi'>|={overlap:.6f}"
            )
    return failures


def test_corrects_every_single_qubit_pauli_error_on_logical_zero() -> None:
    code = Shor9Code()
    failures = _exhaustive_correction(code, logical_bit=0)
    assert not failures, "\n".join(failures)


def test_corrects_every_single_qubit_pauli_error_on_logical_one() -> None:
    code = Shor9Code()
    failures = _exhaustive_correction(code, logical_bit=1)
    assert not failures, "\n".join(failures)


# ---------- hypothesis property test on arbitrary logical superpositions ----------


@settings(deadline=None, max_examples=20)
@given(
    theta=st.floats(
        min_value=0.0,
        max_value=float(np.pi),
        allow_nan=False,
        allow_infinity=False,
    ),
    phi=st.floats(
        min_value=0.0,
        max_value=float(2 * np.pi),
        allow_nan=False,
        allow_infinity=False,
    ),
    qubit=st.integers(min_value=0, max_value=8),
    pauli=st.sampled_from(("X", "Y", "Z")),
)
def test_recovery_preserves_arbitrary_logical_superposition(
    theta: float, phi: float, qubit: int, pauli: str
) -> None:
    """For a random one-qubit state encoded into Shor's code, any
    single-qubit Pauli error is corrected by syndrome + recovery.
    """
    code = Shor9Code()
    alpha = np.cos(theta / 2.0)
    beta = np.exp(1j * phi) * np.sin(theta / 2.0)
    enc0 = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(0)).data, n_qubits=9
    )
    enc1 = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(1)).data, n_qubits=9
    )
    encoded = alpha * enc0 + beta * enc1
    norm = np.linalg.norm(encoded)
    if norm < 1e-12:
        return  # degenerate; skip
    encoded = encoded / norm

    err = ["I"] * 9
    err[qubit] = pauli
    err_string = "".join(err)
    E = pauli_string_to_matrix(err_string)
    corrupted = E @ encoded
    syndrome = code.syndrome_of(err_string)
    R = pauli_string_to_matrix(code.recovery(syndrome))
    restored = R @ corrupted
    overlap = abs(np.vdot(encoded, restored))
    assert overlap > 1 - 1e-9, f"fidelity {overlap} for err {err_string}"
