"""Tests for the rotated surface code factory (Phase 3)."""

from __future__ import annotations

import pytest

from qec_project.codes.surface import RotatedSurfaceCode
from qec_project.noise.circuit import CircuitNoise, depolarizing


def test_memory_defaults_rounds_to_distance():
    code = RotatedSurfaceCode.memory(5)
    assert code.rounds == 5
    assert code.basis == "Z"
    assert code.num_data_qubits == 25


@pytest.mark.parametrize("d", [-3, 0, 1, 2, 4, 6])
def test_rejects_even_or_too_small_distance(d):
    with pytest.raises(ValueError):
        RotatedSurfaceCode.memory(d)


def test_rejects_bad_basis_and_rounds():
    with pytest.raises(ValueError):
        RotatedSurfaceCode(distance=3, rounds=3, basis="Y")
    with pytest.raises(ValueError):
        RotatedSurfaceCode(distance=3, rounds=0)


def test_circuit_detector_and_observable_counts():
    circuit = RotatedSurfaceCode.memory(3).circuit(depolarizing(0.005))
    assert circuit.num_observables == 1
    assert circuit.num_detectors > 0


@pytest.mark.parametrize("d", [3, 5, 7])
def test_detectors_grow_with_distance(d):
    n3 = RotatedSurfaceCode.memory(3).circuit(depolarizing(0.005)).num_detectors
    nd = RotatedSurfaceCode.memory(d).circuit(depolarizing(0.005)).num_detectors
    assert nd >= n3


def test_dem_is_deterministic():
    code = RotatedSurfaceCode.memory(3)
    a = code.detector_error_model(depolarizing(0.004))
    b = code.detector_error_model(depolarizing(0.004))
    assert str(a) == str(b)


def test_memory_x_basis_builds():
    circuit = RotatedSurfaceCode.memory(3, basis="X").circuit(depolarizing(0.005))
    assert circuit.num_observables == 1


@pytest.mark.parametrize("d", [3, 5, 7])
def test_dem_decomposes_for_matching(d):
    dem = RotatedSurfaceCode.memory(d).detector_error_model(depolarizing(0.005))
    assert dem.num_errors > 0


def test_zero_noise_has_no_error_mechanisms():
    dem = RotatedSurfaceCode.memory(3).detector_error_model(CircuitNoise(0.0, 0.0, 0.0, 0.0))
    assert dem.num_errors == 0


@pytest.mark.slow
def test_logical_error_decreases_with_distance():
    from qec_project.decoders.harness import sample_cell

    p = 0.002
    r3 = sample_cell(decoder="pymatching", distance=3, p_phys=p, shots=40000, seed=1)
    r5 = sample_cell(decoder="pymatching", distance=5, p_phys=p, shots=40000, seed=1)
    assert r5.shot_error_rate < r3.shot_error_rate
