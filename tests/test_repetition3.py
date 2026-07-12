"""Unit + property tests for the 3-qubit bit-flip repetition code."""

from __future__ import annotations

import itertools

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.codes.repetition3 import ThreeQubitBitFlipCode


def test_encode_logical_zero() -> None:
    code = ThreeQubitBitFlipCode()
    one_qubit_zero = np.array([1.0, 0.0], dtype=complex)
    psi = code.encode(one_qubit_zero)
    expected = np.zeros(8, dtype=complex)
    expected[0] = 1.0  # |000>
    np.testing.assert_allclose(psi, expected, atol=1e-12)


def test_encode_logical_one() -> None:
    code = ThreeQubitBitFlipCode()
    one_qubit_one = np.array([0.0, 1.0], dtype=complex)
    psi = code.encode(one_qubit_one)
    expected = np.zeros(8, dtype=complex)
    expected[7] = 1.0  # |111>
    np.testing.assert_allclose(psi, expected, atol=1e-12)


def test_encode_logical_plus() -> None:
    code = ThreeQubitBitFlipCode()
    plus = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
    psi = code.encode(plus)
    expected = np.zeros(8, dtype=complex)
    expected[0] = 1.0 / np.sqrt(2)
    expected[7] = 1.0 / np.sqrt(2)
    np.testing.assert_allclose(psi, expected, atol=1e-12)


def test_stabilizers_commute_with_logical_z() -> None:
    code = ThreeQubitBitFlipCode()
    S0, S1 = code.stabilizers()
    Z_L = code.logical_z()
    np.testing.assert_allclose(S0 @ Z_L - Z_L @ S0, 0, atol=1e-12)
    np.testing.assert_allclose(S1 @ Z_L - Z_L @ S1, 0, atol=1e-12)


def test_logical_zero_is_plus1_eigenstate_of_stabilizers() -> None:
    code = ThreeQubitBitFlipCode()
    psi_0L = code.encode(np.array([1.0, 0.0], dtype=complex))
    S0, S1 = code.stabilizers()
    np.testing.assert_allclose(S0 @ psi_0L, psi_0L, atol=1e-12)
    np.testing.assert_allclose(S1 @ psi_0L, psi_0L, atol=1e-12)


def test_logical_one_is_plus1_eigenstate_of_stabilizers() -> None:
    code = ThreeQubitBitFlipCode()
    psi_1L = code.encode(np.array([0.0, 1.0], dtype=complex))
    S0, S1 = code.stabilizers()
    np.testing.assert_allclose(S0 @ psi_1L, psi_1L, atol=1e-12)
    np.testing.assert_allclose(S1 @ psi_1L, psi_1L, atol=1e-12)


def test_syndrome_for_no_error_is_zero() -> None:
    code = ThreeQubitBitFlipCode()
    psi = code.encode(np.array([1.0, 0.0], dtype=complex))
    rho = np.outer(psi, psi.conj())
    rng = np.random.default_rng(seed=0)
    s0, s1 = code.syndrome_extract(rho, rng)
    assert (s0, s1) == (0, 0)


def test_syndrome_for_x_on_each_qubit() -> None:
    from qec_project.noise.quantum import PAULI_I, PAULI_X

    code = ThreeQubitBitFlipCode()
    psi = code.encode(np.array([1.0, 0.0], dtype=complex))
    rng = np.random.default_rng(seed=0)

    X0 = np.kron(np.kron(PAULI_X, PAULI_I), PAULI_I)
    X1 = np.kron(np.kron(PAULI_I, PAULI_X), PAULI_I)
    X2 = np.kron(np.kron(PAULI_I, PAULI_I), PAULI_X)

    psi_e0 = X0 @ psi
    psi_e1 = X1 @ psi
    psi_e2 = X2 @ psi

    rho_e0 = np.outer(psi_e0, psi_e0.conj())
    rho_e1 = np.outer(psi_e1, psi_e1.conj())
    rho_e2 = np.outer(psi_e2, psi_e2.conj())

    assert code.syndrome_extract(rho_e0, rng) == (1, 0)
    assert code.syndrome_extract(rho_e1, rng) == (1, 1)
    assert code.syndrome_extract(rho_e2, rng) == (0, 1)


def test_decode_no_error_returns_input_logical_state() -> None:
    code = ThreeQubitBitFlipCode()
    psi = code.encode(np.array([1.0, 0.0], dtype=complex))
    rho = np.outer(psi, psi.conj())
    rho_corrected = code.decode(rho, syndrome=(0, 0))
    np.testing.assert_allclose(rho_corrected, rho, atol=1e-12)


def test_decode_corrects_single_x_errors() -> None:
    from qec_project.noise.quantum import PAULI_I, PAULI_X

    code = ThreeQubitBitFlipCode()
    psi = code.encode(np.array([1.0, 0.0], dtype=complex))

    X0 = np.kron(np.kron(PAULI_X, PAULI_I), PAULI_I)
    X1 = np.kron(np.kron(PAULI_I, PAULI_X), PAULI_I)
    X2 = np.kron(np.kron(PAULI_I, PAULI_I), PAULI_X)

    for X, syn in [(X0, (1, 0)), (X1, (1, 1)), (X2, (0, 1))]:
        psi_err = X @ psi
        rho_err = np.outer(psi_err, psi_err.conj())
        rho_corrected = code.decode(rho_err, syndrome=syn)
        np.testing.assert_allclose(
            rho_corrected, np.outer(psi, psi.conj()), atol=1e-12
        )


def test_apply_noise_p_zero_is_identity() -> None:
    code = ThreeQubitBitFlipCode()
    psi = code.encode(np.array([1.0, 0.0], dtype=complex))
    rho = np.outer(psi, psi.conj())
    rng = np.random.default_rng(seed=0)
    rho_out = code.apply_noise(rho, p=0.0, rng=rng)
    np.testing.assert_allclose(rho_out, rho, atol=1e-12)


def test_apply_noise_preserves_trace_and_hermiticity() -> None:
    code = ThreeQubitBitFlipCode()
    psi = code.encode(np.array([1.0 / np.sqrt(2), 1.0 / np.sqrt(2)], dtype=complex))
    rho = np.outer(psi, psi.conj())
    rng = np.random.default_rng(seed=42)
    rho_out = code.apply_noise(rho, p=0.2, rng=rng)
    np.testing.assert_allclose(np.trace(rho_out).real, 1.0, atol=1e-12)
    np.testing.assert_allclose(rho_out, rho_out.conj().T, atol=1e-12)


def test_simulate_logical_error_rate_is_zero_at_p_zero() -> None:
    code = ThreeQubitBitFlipCode()
    rng = np.random.default_rng(seed=0)
    err = code.simulate_logical_error_rate(p=0.0, n_trials=64, rng=rng)
    assert err == 0.0


def test_simulate_logical_error_rate_is_finite_and_bounded() -> None:
    code = ThreeQubitBitFlipCode()
    rng = np.random.default_rng(seed=0)
    err = code.simulate_logical_error_rate(p=0.2, n_trials=128, rng=rng)
    assert 0.0 <= err <= 1.0


@settings(max_examples=5, deadline=None)
@given(
    ps=st.lists(
        st.floats(min_value=0.0, max_value=0.5, allow_nan=False),
        min_size=2,
        max_size=3,
        unique=True,
    )
)
def test_logical_error_rate_is_monotone_non_decreasing_in_p(ps: list[float]) -> None:
    code = ThreeQubitBitFlipCode()
    ps_sorted = sorted(ps)
    n_trials = 200
    errs: list[float] = []
    for p in ps_sorted:
        rng = np.random.default_rng(seed=123)  # matched trials across p
        errs.append(code.simulate_logical_error_rate(p=p, n_trials=n_trials, rng=rng))
    # Allow Monte-Carlo wiggle: tolerate up to 5% backward step.
    tolerance = 0.05
    for a, b in itertools.pairwise(errs):
        assert b + tolerance >= a, f"not monotone: {errs} for {ps_sorted}"
