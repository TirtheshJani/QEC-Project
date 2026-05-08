"""Tests for qec/channels.py.

Acceptance gates for Phase 2:
- All channels are CPTP (sum K^dag K = I).
- Depolarizing(p=0) is identity; depolarizing(p=1) sends every state to I/2.
- Bit-flip / phase-flip on the appropriate eigenstates are no-ops.
- apply_1q_channel matches the explicit Kronecker construction on small systems.
- Fidelity is sane: F(rho, rho) = Tr(rho^2) for pure rho, and F(I/2, I/2) = 1.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import pytest

from qec import channels as ch
from qec import statevec as sv

ATOL = 1e-12


# ---------------------------------------------------------------------------
def _kron_apply(rho: np.ndarray, kraus_1q: ch.Kraus, q: int, n: int) -> np.ndarray:
    """Reference implementation: build I ⊗ ... ⊗ K ⊗ ... ⊗ I explicitly."""
    out = np.zeros_like(rho)
    for K in kraus_1q:
        ops = [np.eye(2, dtype=complex)] * n
        ops[n - 1 - q] = K  # qubit 0 = LSB axis
        M = ops[0]
        for op in ops[1:]:
            M = np.kron(M, op)
        out = out + M @ rho @ M.conj().T
    return out


# ---------------------------------------------------------------------------
# CPTP checks
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 0.9, 1.0])
def test_bit_flip_is_cptp(p):
    assert ch.is_cptp(ch.bit_flip(p))


@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 0.9, 1.0])
def test_phase_flip_is_cptp(p):
    assert ch.is_cptp(ch.phase_flip(p))


@pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 0.9, 1.0])
def test_depolarizing_is_cptp(p):
    assert ch.is_cptp(ch.depolarizing(p))


@pytest.mark.parametrize("g", [0.0, 0.2, 0.7, 1.0])
def test_amplitude_damping_is_cptp(g):
    assert ch.is_cptp(ch.amplitude_damping(g))


def test_pauli_channel_is_cptp():
    assert ch.is_cptp(ch.pauli_channel(0.1, 0.05, 0.2))


# ---------------------------------------------------------------------------
# Sanity behaviour
# ---------------------------------------------------------------------------
def test_depolarizing_p_zero_is_identity():
    rho = ch.density_from_state(sv.apply_1q(sv.zero_state(1), sv.H, 0))
    out = ch.apply_channel_full(rho, ch.depolarizing(0.0))
    assert np.allclose(out, rho, atol=ATOL)


def test_depolarizing_p_one_is_maximally_mixed():
    """At p=1 every input state must end up at I/2."""
    rng = np.random.default_rng(0)
    target = np.eye(2, dtype=complex) / 2
    for _ in range(5):
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        psi /= np.linalg.norm(psi)
        rho = ch.density_from_state(psi)
        out = ch.apply_channel_full(rho, ch.depolarizing(1.0))
        assert np.allclose(out, target, atol=ATOL)


def test_bit_flip_on_z_eigenstates_is_a_mixture():
    """X|0> = |1>, so bit-flip on |0><0| gives (1-p)|0><0| + p|1><1|."""
    rho0 = ch.density_from_state(np.array([1, 0], dtype=complex))
    rho1 = ch.density_from_state(np.array([0, 1], dtype=complex))
    p = 0.3
    out = ch.apply_channel_full(rho0, ch.bit_flip(p))
    expected = (1 - p) * rho0 + p * rho1
    assert np.allclose(out, expected, atol=ATOL)


def test_phase_flip_on_x_eigenstates_is_a_mixture():
    """Z|+> = |->, so phase-flip on |+><+| gives (1-p)|+><+| + p|-><-|."""
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    minus = np.array([1, -1], dtype=complex) / np.sqrt(2)
    rho_p = ch.density_from_state(plus)
    rho_m = ch.density_from_state(minus)
    p = 0.4
    out = ch.apply_channel_full(rho_p, ch.phase_flip(p))
    expected = (1 - p) * rho_p + p * rho_m
    assert np.allclose(out, expected, atol=ATOL)


def test_amplitude_damping_drains_excited_state():
    """For pure |1>, T1 decay leaves population (1-gamma) in |1> and gamma in |0>."""
    rho1 = ch.density_from_state(np.array([0, 1], dtype=complex))
    g = 0.3
    out = ch.apply_channel_full(rho1, ch.amplitude_damping(g))
    expected = np.array([[g, 0], [0, 1 - g]], dtype=complex)
    assert np.allclose(out, expected, atol=ATOL)


# ---------------------------------------------------------------------------
# apply_1q_channel matches Kronecker reference
# ---------------------------------------------------------------------------
def test_apply_1q_matches_kron_reference():
    """For every channel and every target qubit on a 3-qubit GHZ, the reshape
    implementation must agree with the explicit-Kronecker reference."""
    n = 3
    psi = sv.zero_state(n)
    psi = sv.apply_1q(psi, sv.H, 0)
    for q in range(1, n):
        psi = sv.cnot(psi, control=0, target=q)
    rho = ch.density_from_state(psi)

    channels = {
        "bit_flip(0.2)": ch.bit_flip(0.2),
        "phase_flip(0.3)": ch.phase_flip(0.3),
        "depolarizing(0.4)": ch.depolarizing(0.4),
        "amplitude_damping(0.25)": ch.amplitude_damping(0.25),
    }
    for q, (name, K) in product(range(n), channels.items()):
        out = ch.apply_1q_channel(rho, K, q)
        ref = _kron_apply(rho, K, q, n)
        assert np.allclose(out, ref, atol=ATOL), f"mismatch on {name}, q={q}"


# ---------------------------------------------------------------------------
# Fidelity
# ---------------------------------------------------------------------------
def test_fidelity_self_is_one():
    psi = sv.apply_1q(sv.zero_state(1), sv.H, 0)
    rho = ch.density_from_state(psi)
    assert np.isclose(ch.fidelity(rho, rho), 1.0, atol=1e-10)


def test_fidelity_orthogonal_pure_states_is_zero():
    rho0 = ch.density_from_state(np.array([1, 0], dtype=complex))
    rho1 = ch.density_from_state(np.array([0, 1], dtype=complex))
    assert np.isclose(ch.fidelity(rho0, rho1), 0.0, atol=1e-10)


def test_fidelity_max_mixed_with_self():
    Iover2 = np.eye(2, dtype=complex) / 2
    assert np.isclose(ch.fidelity(Iover2, Iover2), 1.0, atol=1e-10)


def test_depolarizing_fidelity_with_input_pure():
    """For pure input |+>, F(rho_out, |+><+|) = 1 - p/2 (standard textbook result)."""
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho_in = ch.density_from_state(plus)
    for p in [0.0, 0.1, 0.4, 1.0]:
        rho_out = ch.apply_channel_full(rho_in, ch.depolarizing(p))
        F = ch.fidelity(rho_out, rho_in)
        assert np.isclose(F, 1 - p / 2, atol=1e-10), f"p={p}: F={F}"


# ---------------------------------------------------------------------------
# Qiskit cross-check
# ---------------------------------------------------------------------------
def test_depolarizing_matches_qiskit():
    pytest.importorskip("qiskit_aer")
    from qiskit.quantum_info import Kraus
    from qiskit_aer.noise import depolarizing_error

    p = 0.25
    err = depolarizing_error(p, 1)
    qiskit_kraus = [np.asarray(K, dtype=complex) for K in Kraus(err).data]

    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho_in = ch.density_from_state(plus)
    ours = ch.apply_channel_full(rho_in, ch.depolarizing(p))
    theirs = sum(K @ rho_in @ K.conj().T for K in qiskit_kraus)
    assert np.allclose(ours, theirs, atol=1e-10)
