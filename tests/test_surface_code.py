"""Tests for the rotated surface-code circuit factory.

Locks in regression baselines for detector / observable counts at d=3 and
covers input validation. The exact integer baselines are read from a
single Stim construction so the test serves as a stable fingerprint.
"""

from __future__ import annotations

import numpy as np
import pytest

from qec_project.codes.surface_code import (
    code_parameters,
    rotated_surface_code_circuit,
)


def test_d3_r3_detector_and_observable_counts() -> None:
    circuit = rotated_surface_code_circuit(distance=3, rounds=3, p_phys=0.01)
    # Regression baseline: confirmed by direct Stim inspection on stim 1.15.
    assert circuit.num_detectors == 24
    assert circuit.num_observables == 1


def test_zero_noise_yields_zero_clicks() -> None:
    circuit = rotated_surface_code_circuit(distance=3, rounds=3, p_phys=0.0)
    sampler = circuit.compile_detector_sampler(seed=12345)
    dets, obs = sampler.sample(shots=100, separate_observables=True)
    assert dets.dtype == np.bool_
    assert dets.sum() == 0
    assert obs.sum() == 0


@pytest.mark.parametrize("bad_distance", [2, 4, 1, 0, -3])
def test_invalid_distance_raises(bad_distance: int) -> None:
    with pytest.raises(ValueError):
        rotated_surface_code_circuit(distance=bad_distance, rounds=1, p_phys=0.001)


@pytest.mark.parametrize("bad_rounds", [0, -1])
def test_invalid_rounds_raises(bad_rounds: int) -> None:
    with pytest.raises(ValueError):
        rotated_surface_code_circuit(distance=3, rounds=bad_rounds, p_phys=0.001)


@pytest.mark.parametrize("bad_p", [-0.01, 0.6, 1.0])
def test_invalid_p_raises(bad_p: float) -> None:
    with pytest.raises(ValueError):
        rotated_surface_code_circuit(distance=3, rounds=1, p_phys=bad_p)


def test_code_parameters_d3() -> None:
    params = code_parameters(3)
    assert params["distance"] == 3
    assert params["n_data"] == 9
    assert params["n_stabilizers"] == 8
    assert params["n_x_stabilizers"] == 4
    assert params["n_z_stabilizers"] == 4


def test_code_parameters_d5() -> None:
    params = code_parameters(5)
    assert params["distance"] == 5
    assert params["n_data"] == 25
    assert params["n_stabilizers"] == 24
    assert params["n_x_stabilizers"] == 12
    assert params["n_z_stabilizers"] == 12


def test_code_parameters_invalid() -> None:
    with pytest.raises(ValueError):
        code_parameters(4)
    with pytest.raises(ValueError):
        code_parameters(1)
