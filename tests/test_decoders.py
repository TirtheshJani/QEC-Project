"""Tests for the decoder wrappers, registry, and Monte-Carlo harness (Phase 3)."""

from __future__ import annotations

import numpy as np
import pytest
import sinter

from qec_project.codes.surface import RotatedSurfaceCode
from qec_project.decoders.harness import CellResult, sample_cell
from qec_project.decoders.pymatching_decoder import decode_shots, matching_from_dem
from qec_project.decoders.registry import DECODERS, builtin_decoder_names, custom_decoders
from qec_project.noise.circuit import depolarizing


def _sample(d, p, shots, seed=0):
    code = RotatedSurfaceCode.memory(d)
    circuit = code.circuit(depolarizing(p))
    dem = code.detector_error_model(depolarizing(p))
    det, obs = circuit.compile_detector_sampler(seed=seed).sample(
        shots, separate_observables=True
    )
    return dem, det, obs


def test_matching_decode_shape():
    dem, det, obs = _sample(3, 0.01, 200)
    pred = decode_shots(matching_from_dem(dem), det)
    assert pred.shape == obs.shape


def test_decode_shots_rejects_non_2d():
    dem, det, _ = _sample(3, 0.01, 5)
    with pytest.raises(ValueError):
        decode_shots(matching_from_dem(dem), det[0])


def test_registry_mapping():
    assert "pymatching" in builtin_decoder_names()
    assert custom_decoders("pymatching") == {}
    bp = custom_decoders("bp-osd")
    assert set(bp) == {"bp-osd"}
    assert isinstance(bp["bp-osd"], sinter.Decoder)
    with pytest.raises(ValueError):
        custom_decoders("nope")
    assert {"pymatching", "bp-osd"} <= set(DECODERS)


def test_matching_beats_trivial_decoder():
    dem, det, obs = _sample(3, 0.004, 20000, seed=3)
    pred = decode_shots(matching_from_dem(dem), det)
    mwpm_errors = int(np.count_nonzero(np.any(pred != obs, axis=1)))
    trivial_errors = int(np.count_nonzero(np.any(obs != 0, axis=1)))
    assert mwpm_errors < trivial_errors


def test_sample_cell_basic():
    r = sample_cell(decoder="pymatching", distance=3, p_phys=0.01, shots=1000, seed=5)
    assert isinstance(r, CellResult)
    assert r.shots == 1000
    assert 0 <= r.errors <= r.shots
    assert r.distance == 3 and r.rounds == 3 and r.decoder == "pymatching"


def test_sample_cell_is_reproducible():
    a = sample_cell(decoder="pymatching", distance=3, p_phys=0.005, shots=3000, seed=11)
    b = sample_cell(decoder="pymatching", distance=3, p_phys=0.005, shots=3000, seed=11)
    assert a.errors == b.errors


def test_sample_cell_rejects_bad_shots():
    with pytest.raises(ValueError):
        sample_cell(decoder="pymatching", distance=3, p_phys=0.01, shots=0)


@pytest.mark.slow
def test_bposd_runs_and_is_comparable_to_mwpm():
    pm = sample_cell(decoder="pymatching", distance=3, p_phys=0.006, shots=20000, seed=2)
    bp = sample_cell(decoder="bp-osd", distance=3, p_phys=0.006, shots=20000, seed=2)
    assert bp.shots == 20000
    # Both decode the same code; BP+OSD should be at least competitive with MWPM.
    assert bp.shot_error_rate <= pm.shot_error_rate * 1.5 + 0.01
