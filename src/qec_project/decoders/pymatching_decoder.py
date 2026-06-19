"""PyMatching (MWPM) decoding behind the package's common interface.

Phase 3. Minimum-weight perfect matching is the baseline surface-code decoder.
This thin wrapper builds a :class:`pymatching.Matching` from a Stim detector
error model and decodes batches of detection events to logical-flip
predictions, honoring the contract documented in this package's ``__init__``:
``decode(detector_data) -> logical-flip predictions``.

References (in ``docs/reading-list.md``):

* O. Higgott, C. Gidney. *Sparse Blossom: correcting a million errors per core
  second with minimum-weight matching.* arXiv:2303.15933.
"""

from __future__ import annotations

import numpy as np
import pymatching
import stim


def matching_from_dem(dem: stim.DetectorErrorModel) -> pymatching.Matching:
    """Build an MWPM decoder from a (decomposed) detector error model."""
    return pymatching.Matching.from_detector_error_model(dem)


def decode_shots(matching: pymatching.Matching, detection_events: np.ndarray) -> np.ndarray:
    """Decode a batch of detection events to logical-flip predictions.

    Parameters
    ----------
    matching:
        A compiled :class:`pymatching.Matching` (see :func:`matching_from_dem`).
    detection_events:
        Array of shape ``(shots, num_detectors)`` of 0/1 detection events.

    Returns
    -------
    np.ndarray
        Array of shape ``(shots, num_observables)`` — the predicted
        logical-observable flips.
    """
    events = np.asarray(detection_events)
    if events.ndim != 2:
        raise ValueError(f"detection_events must be 2-D (shots, detectors); got {events.shape}")
    return matching.decode_batch(events)
