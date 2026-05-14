"""Classical noise channels.

This module starts with the binary symmetric channel because Phase 0.2
needs to simulate it and Phase 0.3 needs to send Hamming codewords
through it. Quantum noise channels live in sibling modules built out
during Phase 1+ (bit-flip / phase-flip / depolarizing on single qubits;
circuit-level depolarizing for surface-code threshold sims in Phase 3+).

References (in ``docs/reading-list.md``):

* C. E. Shannon, *A Mathematical Theory of Communication.* Bell System
  Technical Journal, 27, 1948. doi:10.1002/j.1538-7305.1948.tb01338.x.
* MacKay, *Information Theory, Inference, and Learning Algorithms*,
  chapter 9 (noisy-channel coding theorem; BSC).
"""

from __future__ import annotations

import numpy as np


def bsc_flip(
    bits: np.ndarray,
    p: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Pass ``bits`` through a binary symmetric channel with flip probability ``p``.

    Each input bit is independently flipped with probability ``p``. The
    return value has the same shape and dtype as ``bits``; the input is
    not modified. The XOR with a Bernoulli(p) mask makes the flip
    pattern independent of the input values, which is the textbook
    definition of the BSC and is what the property test verifies.

    Parameters
    ----------
    bits:
        Array of 0/1 values. Any integer dtype is accepted; the output
        matches the input dtype.
    p:
        Flip probability, in ``[0, 1]``.
    rng:
        ``numpy.random.Generator``. The caller owns seeding so that the
        full notebook / experiment is deterministic.

    Raises
    ------
    ValueError
        If ``p`` is outside ``[0, 1]``.
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"flip probability must lie in [0, 1]; got p={p}")
    arr = np.asarray(bits)
    mask = (rng.random(arr.shape) < p).astype(arr.dtype)
    return arr ^ mask
