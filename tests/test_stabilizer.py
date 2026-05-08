"""Tests for qec/stabilizer.py.

Phase 3 acceptance gate: the tableau simulator must agree with the
qec.statevec state-vector simulator (and Qiskit, where available) on
arbitrary Clifford circuits up to global phase, and on measurement statistics
in the long-shot limit.
"""

from __future__ import annotations

import numpy as np
import pytest

from qec import statevec as sv
from qec.pauli import Pauli
from qec.stabilizer import StabilizerState

ATOL = 1e-10


def _states_equal_up_to_phase(psi1: np.ndarray, psi2: np.ndarray, atol: float = ATOL) -> bool:
    """True iff psi1 and psi2 differ only by a global phase."""
    psi1 = np.asarray(psi1, dtype=complex).reshape(-1)
    psi2 = np.asarray(psi2, dtype=complex).reshape(-1)
    if psi1.shape != psi2.shape:
        return False
    overlap = abs(np.vdot(psi1, psi2))
    return bool(np.isclose(overlap, 1.0, atol=atol))


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------
def test_initial_state_is_all_zeros():
    n = 4
    st = StabilizerState(n)
    psi = st.to_statevector()
    expected = sv.zero_state(n)
    assert _states_equal_up_to_phase(psi, expected)


def test_initial_stabilizers_are_z_on_each_qubit():
    """For |0...0>, the stabilizers are Z_0, Z_1, ..., Z_{n-1}."""
    n = 3
    st = StabilizerState(n)
    gens = st.stabilizer_generators()
    expected_strs = ["ZII", "IZI", "IIZ"]
    for g, s in zip(gens, expected_strs):
        assert g == Pauli.from_string(s), f"{g!r} != {s}"


# ---------------------------------------------------------------------------
# Single-gate sanity
# ---------------------------------------------------------------------------
def test_h_creates_plus_state():
    """H |0> should be stabilised by +X."""
    st = StabilizerState(1)
    st.h(0)
    gens = st.stabilizer_generators()
    assert gens == [Pauli.from_string("X")]
    psi = st.to_statevector()
    expected = sv.apply_1q(sv.zero_state(1), sv.H, 0)
    assert _states_equal_up_to_phase(psi, expected)


def test_x_flips_z_eigenstate():
    """X |0> = |1> should be stabilised by -Z."""
    st = StabilizerState(1)
    st.x(0)
    gens = st.stabilizer_generators()
    assert gens == [Pauli.from_string("-Z")]


def test_s_takes_plus_to_plus_i():
    """S H |0> = (|0> + i|1>)/sqrt(2) should be stabilised by +Y."""
    st = StabilizerState(1)
    st.h(0)
    st.s(0)
    gens = st.stabilizer_generators()
    assert gens == [Pauli.from_string("Y")]


# ---------------------------------------------------------------------------
# Bell / GHZ
# ---------------------------------------------------------------------------
def test_bell_state_via_stabilizer():
    """H q0 then CNOT(0->1) gives |Phi+>, stabilised by XX and ZZ."""
    n = 2
    st = StabilizerState(n)
    st.h(0)
    st.cnot(0, 1)
    gens = st.stabilizer_generators()
    assert gens == [Pauli.from_string("XX"), Pauli.from_string("ZZ")]
    psi = st.to_statevector()
    expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    assert _states_equal_up_to_phase(psi, expected)


def test_ghz_state():
    n = 4
    st = StabilizerState(n)
    st.h(0)
    for q in range(1, n):
        st.cnot(0, q)
    psi = st.to_statevector()
    expected = np.zeros(2**n, dtype=complex)
    expected[0] = expected[-1] = 1 / np.sqrt(2)
    assert _states_equal_up_to_phase(psi, expected)


# ---------------------------------------------------------------------------
# Random Clifford agreement with qec.statevec
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("seed", [0, 1, 7, 42])
def test_random_clifford_matches_statevec(seed):
    """A 60-gate random Clifford on n=4 must produce the same state vector
    (up to global phase) in qec.stabilizer and qec.statevec."""
    n, depth = 4, 60
    rng = np.random.default_rng(seed)

    st = StabilizerState(n)
    psi = sv.zero_state(n)

    for _ in range(depth):
        kind = rng.integers(0, 4)
        q = int(rng.integers(0, n))
        if kind == 0:
            st.h(q)
            psi = sv.apply_1q(psi, sv.H, q)
        elif kind == 1:
            st.s(q)
            psi = sv.apply_1q(psi, sv.S, q)
        elif kind == 2:
            st.x(q)
            psi = sv.apply_1q(psi, sv.X, q)
        else:
            q2 = int(rng.integers(0, n))
            while q2 == q:
                q2 = int(rng.integers(0, n))
            st.cnot(q, q2)
            psi = sv.cnot(psi, q, q2)

    psi_stab = st.to_statevector()
    assert _states_equal_up_to_phase(psi_stab, psi), f"seed {seed}"


# ---------------------------------------------------------------------------
# Stabilizer generators are consistent with the underlying state vector
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("seed", [0, 7])
def test_stabilizer_generators_stabilise_the_state(seed):
    """For the state psi reconstructed from the tableau, every stabilizer
    generator g must satisfy g psi = +psi (eigenvalue +1)."""
    n, depth = 3, 40
    rng = np.random.default_rng(seed)
    st = StabilizerState(n)
    for _ in range(depth):
        kind = rng.integers(0, 3)
        q = int(rng.integers(0, n))
        if kind == 0:
            st.h(q)
        elif kind == 1:
            st.s(q)
        else:
            q2 = int(rng.integers(0, n))
            while q2 == q:
                q2 = int(rng.integers(0, n))
            st.cnot(q, q2)
    psi = st.to_statevector()
    for g in st.stabilizer_generators():
        out = g.matrix() @ psi
        assert np.allclose(out, psi, atol=ATOL), f"{g!r} is not a stabilizer of psi"


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------
def test_measure_zero_state_is_deterministic():
    n = 3
    st = StabilizerState(n)
    rng = np.random.default_rng(0)
    for q in range(n):
        assert st.measure(q, rng=rng) == 0


def test_measure_after_x_is_deterministic_one():
    st = StabilizerState(1)
    st.x(0)
    rng = np.random.default_rng(0)
    assert st.measure(0, rng=rng) == 1


def test_measure_plus_state_is_random():
    """|+> in the Z basis: 50/50 outcomes."""
    st_template = StabilizerState(1)
    st_template.h(0)
    rng = np.random.default_rng(2026)
    shots = 4000
    ones = 0
    for _ in range(shots):
        st = st_template.copy()
        ones += st.measure(0, rng=rng)
    p1 = ones / shots
    assert 0.45 < p1 < 0.55, f"got p(1) = {p1}"


def test_bell_measurement_correlates():
    """Measuring both qubits of |Phi+> always gives 00 or 11."""
    rng = np.random.default_rng(42)
    template = StabilizerState(2)
    template.h(0)
    template.cnot(0, 1)
    bad = 0
    for _ in range(2000):
        st = template.copy()
        m0 = st.measure(0, rng=rng)
        m1 = st.measure(1, rng=rng)
        if m0 != m1:
            bad += 1
    assert bad == 0


def test_sample_returns_correct_shape():
    n = 3
    st = StabilizerState(n)
    st.h(0)
    st.cnot(0, 1)
    st.cnot(0, 2)
    rng = np.random.default_rng(0)
    out = st.sample(shots=128, rng=rng)
    assert out.shape == (128, n)
    # GHZ: every shot must be all-0 or all-1.
    for row in out:
        assert all(b == row[0] for b in row), f"non-GHZ sample {row}"


# ---------------------------------------------------------------------------
# Qiskit cross-check (skipped if absent)
# ---------------------------------------------------------------------------
def test_random_clifford_matches_qiskit():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    n, depth = 3, 40
    rng = np.random.default_rng(99)
    qc = QuantumCircuit(n)
    st = StabilizerState(n)
    for _ in range(depth):
        kind = rng.integers(0, 4)
        q = int(rng.integers(0, n))
        if kind == 0:
            qc.h(q); st.h(q)
        elif kind == 1:
            qc.s(q); st.s(q)
        elif kind == 2:
            qc.x(q); st.x(q)
        else:
            q2 = int(rng.integers(0, n))
            while q2 == q:
                q2 = int(rng.integers(0, n))
            qc.cx(q, q2); st.cnot(q, q2)

    expected = np.asarray(Statevector.from_instruction(qc).data, dtype=complex)
    psi = st.to_statevector()
    assert _states_equal_up_to_phase(psi, expected)
