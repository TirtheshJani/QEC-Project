"""Sanity tests for qec/statevec.py.

These are the Phase 1 acceptance gate: the NumPy simulator must reproduce
canonical small-circuit outputs to high precision. We avoid a hard Qiskit
dependency in the tests themselves — a separate (skipped if missing) test
cross-checks against `qiskit.quantum_info.Statevector`.
"""

from __future__ import annotations

import numpy as np
import pytest

from qec import statevec as sv

ATOL = 1e-12


def _bell_phi_plus() -> np.ndarray:
    """(|00> + |11>) / sqrt(2)."""
    return np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)


def _ghz(n: int) -> np.ndarray:
    """(|0...0> + |1...1>) / sqrt(2)."""
    psi = np.zeros(2**n, dtype=complex)
    psi[0] = psi[-1] = 1 / np.sqrt(2)
    return psi


# --- 1-qubit gates ---------------------------------------------------------
def test_pauli_squares_to_identity():
    rng = np.random.default_rng(0)
    psi = rng.normal(size=2) + 1j * rng.normal(size=2)
    psi /= np.linalg.norm(psi)
    for G in (sv.X, sv.Y, sv.Z, sv.H):
        out = sv.apply_1q(sv.apply_1q(psi, G, 0), G, 0)
        assert np.allclose(out, psi, atol=ATOL)


def test_hadamard_creates_superposition():
    psi = sv.zero_state(1)
    out = sv.apply_1q(psi, sv.H, 0)
    expected = np.array([1, 1], dtype=complex) / np.sqrt(2)
    assert np.allclose(out, expected, atol=ATOL)


# --- 2-qubit gates ---------------------------------------------------------
def test_bell_state_construction():
    """H on q0 then CNOT(q0 -> q1) yields |Phi+>."""
    psi = sv.zero_state(2)
    psi = sv.apply_1q(psi, sv.H, 0)
    psi = sv.cnot(psi, control=0, target=1)
    assert np.allclose(psi, _bell_phi_plus(), atol=ATOL)


def test_ghz_state_construction():
    """H on q0 then CNOT chain yields a 4-qubit GHZ."""
    n = 4
    psi = sv.zero_state(n)
    psi = sv.apply_1q(psi, sv.H, 0)
    for q in range(1, n):
        psi = sv.cnot(psi, control=0, target=q)
    assert np.allclose(psi, _ghz(n), atol=ATOL)


def test_cnot_only_flips_when_control_is_one():
    psi = sv.basis_state(2, 0b10)  # qubit 1 = 1, qubit 0 = 0
    out = sv.cnot(psi, control=0, target=1)
    # control = qubit 0 = 0, so target unchanged → state unchanged.
    assert np.allclose(out, psi, atol=ATOL)

    psi = sv.basis_state(2, 0b01)  # qubit 0 = 1, qubit 1 = 0
    out = sv.cnot(psi, control=0, target=1)
    # control = 1, so qubit 1 flips: 01 -> 11.
    assert np.allclose(out, sv.basis_state(2, 0b11), atol=ATOL)


def test_swap_exchanges_qubits():
    psi = sv.basis_state(3, 0b001)  # qubit 0 = 1, others 0
    out = sv.swap(psi, 0, 2)
    assert np.allclose(out, sv.basis_state(3, 0b100), atol=ATOL)


# --- Measurement -----------------------------------------------------------
def test_probabilities_sum_to_one():
    rng = np.random.default_rng(42)
    n = 5
    psi = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
    psi /= np.linalg.norm(psi)
    assert np.isclose(sv.probabilities(psi).sum(), 1.0, atol=ATOL)


def test_bell_measurement_correlates():
    """Measuring |Phi+> always gives 00 or 11, never 01/10."""
    psi = _bell_phi_plus()
    rng = np.random.default_rng(1)
    samples = sv.sample(psi, shots=2000, rng=rng)
    bad = np.sum((samples == 0b01) | (samples == 0b10))
    assert bad == 0
    # Roughly equal split.
    p11 = np.mean(samples == 0b11)
    assert 0.4 < p11 < 0.6


def test_measure_qubit_collapses():
    """After measuring qubit 0 of |Phi+>, qubit 1 must equal the same outcome."""
    psi = _bell_phi_plus()
    rng = np.random.default_rng(7)
    out0, post = sv.measure_qubit(psi, 0, rng=rng)
    # Post-measurement state is now deterministic in qubit 1.
    out1, _ = sv.measure_qubit(post, 1, rng=rng)
    assert out0 == out1


# --- Cross-check with Qiskit (skipped if not installed) --------------------
def test_bell_matches_qiskit():
    qi = pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    expected = np.asarray(Statevector.from_instruction(qc).data, dtype=complex)

    psi = sv.zero_state(2)
    psi = sv.apply_1q(psi, sv.H, 0)
    psi = sv.cnot(psi, 0, 1)

    assert np.allclose(psi, expected, atol=ATOL)


def test_random_clifford_matches_qiskit():
    qi = pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    n = 4
    rng = np.random.default_rng(2026)
    qc = QuantumCircuit(n)
    psi = sv.zero_state(n)
    for _ in range(40):
        kind = rng.integers(0, 4)
        q = int(rng.integers(0, n))
        if kind == 0:
            qc.h(q)
            psi = sv.apply_1q(psi, sv.H, q)
        elif kind == 1:
            qc.s(q)
            psi = sv.apply_1q(psi, sv.S, q)
        elif kind == 2:
            qc.x(q)
            psi = sv.apply_1q(psi, sv.X, q)
        else:
            q2 = int(rng.integers(0, n))
            while q2 == q:
                q2 = int(rng.integers(0, n))
            qc.cx(q, q2)
            psi = sv.cnot(psi, q, q2)

    expected = np.asarray(Statevector.from_instruction(qc).data, dtype=complex)
    assert np.allclose(psi, expected, atol=ATOL)
