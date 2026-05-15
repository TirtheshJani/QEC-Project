"""Common decoder interface.

Every decoder in the capstone benchmark exposes the same contract so that
swapping decoders under an identical Stim Detector Error Model is a
one-line change in experiment harnesses.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Decoder(Protocol):
    """Decoder protocol for batched syndrome decoding.

    Implementations operate on detector data from a `stim.Circuit` and
    return predicted observable flips.

    Array contract
    --------------
    Input: ``detection_events`` of shape ``(shots, n_detectors)``, dtype
    ``bool`` or ``uint8``. Each row is one shot's detector outcomes.

    Output: predictions of shape ``(shots, n_observables)``, dtype
    ``uint8`` (values in {0, 1}). Each row is the decoder's guess of the
    logical observable flips for that shot.

    The XOR of the prediction and the true observable (also shape
    ``(shots, n_observables)``) is the per-shot logical-error indicator.
    """

    def decode_batch(self, detection_events: np.ndarray) -> np.ndarray:  # pragma: no cover - protocol
        ...
