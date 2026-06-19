"""Decoder wrappers behind a common interface.

The capstone benchmark study lives or dies by whether decoders are comparable
under identical Stim DEMs. All decoders here expose:

    decode(detector_data: np.ndarray) -> np.ndarray  # logical-flip predictions

Implementations wrap PyMatching, the `ldpc` library (BP+OSD), a Union-Find
decoder, and a small neural decoder (Phase 5).
"""

from qec_project.decoders.harness import CellResult, sample_cell
from qec_project.decoders.pymatching_decoder import decode_shots, matching_from_dem
from qec_project.decoders.registry import (
    DECODERS,
    builtin_decoder_names,
    custom_decoders,
)

__all__ = [
    "DECODERS",
    "CellResult",
    "builtin_decoder_names",
    "custom_decoders",
    "decode_shots",
    "matching_from_dem",
    "sample_cell",
]
