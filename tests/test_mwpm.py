"""Tests for the MWPM decoder wrapper.

PyMatching is treated as ground truth for the algorithm itself; these tests
only verify the wrapper correctly plumbs Stim detector data through
`Matching.decode_batch` and that the output shape contract holds.
"""

from __future__ import annotations

import numpy as np

from qec_project.codes.surface_code import rotated_surface_code_circuit
from qec_project.decoders.mwpm import MwpmDecoder


def _sample(circuit, shots: int, seed: int):
    sampler = circuit.compile_detector_sampler(seed=seed)
    return sampler.sample(shots=shots, separate_observables=True)


def test_zero_noise_zero_logical_errors() -> None:
    circuit = rotated_surface_code_circuit(distance=3, rounds=2, p_phys=0.0)
    decoder = MwpmDecoder.from_circuit(circuit)
    dets, obs = _sample(circuit, shots=200, seed=1)
    predictions = decoder.decode_batch(dets)
    assert predictions.shape == obs.shape
    assert (predictions ^ obs.astype(np.uint8)).sum() == 0


def test_decoder_beats_physical_at_low_p() -> None:
    distance = 3
    rounds = 2
    p_phys = 0.001
    shots = 10_000
    circuit = rotated_surface_code_circuit(distance=distance, rounds=rounds, p_phys=p_phys)
    decoder = MwpmDecoder.from_circuit(circuit)
    dets, obs = _sample(circuit, shots=shots, seed=2026)
    predictions = decoder.decode_batch(dets)
    # XOR of prediction vs truth = logical-flip outcome.
    errors = (predictions ^ obs.astype(np.uint8)).any(axis=1).sum()
    logical_error_rate = errors / shots
    assert logical_error_rate < p_phys, (
        f"logical_error_rate={logical_error_rate} expected < p_phys={p_phys}"
    )


def test_decode_batch_shape_and_dtype() -> None:
    circuit = rotated_surface_code_circuit(distance=3, rounds=2, p_phys=0.005)
    decoder = MwpmDecoder.from_circuit(circuit)
    dets, _ = _sample(circuit, shots=50, seed=7)
    predictions = decoder.decode_batch(dets)
    assert predictions.shape == (50, circuit.num_observables)
    assert predictions.dtype == np.uint8
