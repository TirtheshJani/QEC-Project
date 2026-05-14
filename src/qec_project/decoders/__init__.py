"""Decoder wrappers behind a common interface.

The capstone benchmark study lives or dies by whether decoders are comparable
under identical Stim DEMs. All decoders here expose:

    decode(detector_data: np.ndarray) -> np.ndarray  # logical-flip predictions

Implementations wrap PyMatching, the `ldpc` library (BP+OSD), a Union-Find
decoder, and a small neural decoder (Phase 5).
"""
