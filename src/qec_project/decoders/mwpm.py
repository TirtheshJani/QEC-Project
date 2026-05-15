"""MWPM decoder wrapping PyMatching.

This is the capstone's primary baseline. The implementation is a thin
wrapper: any cleverness lives upstream (Stim's DEM construction with
``decompose_errors=True``) or downstream (PyMatching's blossom-based
matching). The wrapper exists so that every experiment in the benchmark
talks to a decoder through the same `Decoder` protocol.
"""

from __future__ import annotations

import numpy as np
import pymatching
import stim


class MwpmDecoder:
    """Minimum-weight perfect-matching decoder backed by PyMatching."""

    def __init__(self, dem: stim.DetectorErrorModel) -> None:
        self._dem = dem
        self._matching = pymatching.Matching.from_detector_error_model(dem)
        self._num_detectors = dem.num_detectors
        self._num_observables = dem.num_observables

    @classmethod
    def from_circuit(cls, circuit: stim.Circuit) -> MwpmDecoder:
        """Build a decoder from a Stim circuit by extracting its DEM."""
        dem = circuit.detector_error_model(decompose_errors=True)
        return cls(dem)

    @property
    def num_detectors(self) -> int:
        return self._num_detectors

    @property
    def num_observables(self) -> int:
        return self._num_observables

    def decode_batch(self, detection_events: np.ndarray) -> np.ndarray:
        """Decode a batch of shots; returns ``(shots, n_observables)`` uint8."""
        if detection_events.ndim != 2:
            raise ValueError(
                f"detection_events must be 2D (shots, n_detectors); got shape {detection_events.shape}"
            )
        if detection_events.shape[1] != self._num_detectors:
            raise ValueError(
                f"expected {self._num_detectors} detectors per shot, got {detection_events.shape[1]}"
            )
        # PyMatching accepts bool or uint8; normalize for safety.
        if detection_events.dtype != np.uint8 and detection_events.dtype != np.bool_:
            detection_events = detection_events.astype(np.uint8)
        predictions = self._matching.decode_batch(detection_events)
        return np.asarray(predictions, dtype=np.uint8)
