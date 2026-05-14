"""Tiny information-theoretic helpers used from Phase 0.2 onward.

These functions are introduced in Phase 0.2 (`probability.ipynb`) and
reused whenever a noise channel needs a Shannon-limit reference point:
Phase 0.3 (Hamming code over a BSC), Phase 3+ (surface-code logical
error rate vs the classical capacity bound for the same physical error
rate).

Conventions:

* Probabilities are real scalars or numpy arrays in ``[0, 1]``.
* Entropy is in bits (``log2``).
* The standard convention ``0 * log2(0) = 0`` is used so that
  ``binary_entropy(0) == binary_entropy(1) == 0``.

References (in ``docs/reading-list.md``):

* C. E. Shannon, *A Mathematical Theory of Communication.* Bell System
  Technical Journal, 27, 1948. doi:10.1002/j.1538-7305.1948.tb01338.x.
* MacKay, *Information Theory, Inference, and Learning Algorithms*,
  chapters 1-2.
"""

from __future__ import annotations

import numpy as np


def _check_prob(p: float | np.ndarray) -> np.ndarray:
    arr = np.asarray(p, dtype=np.float64)
    if np.any(arr < 0.0) or np.any(arr > 1.0):
        raise ValueError(f"probabilities must lie in [0, 1]; got min={arr.min()}, max={arr.max()}")
    return arr


def binary_entropy(p: float | np.ndarray) -> float | np.ndarray:
    """Binary entropy ``H_2(p) = -p log2(p) - (1-p) log2(1-p)`` in bits.

    Uses the ``0 log 0 = 0`` convention so the function is continuous at
    the endpoints: ``binary_entropy(0) == binary_entropy(1) == 0``.

    Accepts a scalar or an array; returns the same shape.
    """
    arr = _check_prob(p)
    safe_p = np.where((arr == 0.0) | (arr == 1.0), 0.5, arr)
    h = -safe_p * np.log2(safe_p) - (1.0 - safe_p) * np.log2(1.0 - safe_p)
    h = np.where((arr == 0.0) | (arr == 1.0), 0.0, h)
    if np.ndim(p) == 0:
        return float(h)
    return h


def bsc_capacity(p: float | np.ndarray) -> float | np.ndarray:
    """Shannon capacity of the binary symmetric channel: ``C = 1 - H_2(p)``.

    Units: bits per channel use. ``C(0) = 1`` (a noiseless binary channel
    carries one bit per use); ``C(0.5) = 0`` (a fair-coin channel carries
    no information). The capacity is symmetric about ``p = 0.5`` and
    rises back to 1 at ``p = 1`` because deterministically flipping
    every bit is just a relabelling.
    """
    h = binary_entropy(p)
    if isinstance(h, float):
        return 1.0 - h
    return 1.0 - h
