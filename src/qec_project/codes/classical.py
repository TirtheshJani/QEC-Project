"""Classical linear codes used in Phase 0.3 (and reused later).

Two block codes over GF(2), built from scratch for the classical
error-correction notebook:

* :class:`RepetitionCode` -- the (n, 1, n) repetition code with
  majority-vote decoding. The 3-bit case is the canonical worked
  example for both the classical bit-flip channel and the 3-qubit
  bit-flip code in Phase 2.
* :class:`Hamming74` -- the (7, 4, 3) Hamming code with explicit
  generator matrix ``G`` (4 by 7) and parity-check matrix ``H``
  (3 by 7). Single-bit errors are decoded by looking up the syndrome
  in a precomputed table. Phase 2's Steane code is the CSS quantum
  code built from this same ``H`` and its dual, which is why
  promotion now (rather than letting the notebook own it) pays off.

All arrays are ``numpy.ndarray`` of ``uint8`` over GF(2): values are
0 or 1, addition is XOR, multiplication is AND. Both classes accept
either a single message / codeword as a 1D array or a batch as a 2D
array; batched output preserves the leading dimension.

References (in ``docs/reading-list.md``):

* R. W. Hamming. *Error Detecting and Error Correcting Codes.*
  Bell System Technical Journal 29, 1950.
  doi:10.1002/j.1538-7305.1950.tb00463.x. Source of the (7, 4) code.
* MacKay, *Information Theory, Inference, and Learning Algorithms*,
  chapter 1 (linear codes; the Hamming(7,4) example).
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def _as_batch(arr: np.ndarray, expected_width: int, name: str) -> tuple[np.ndarray, bool]:
    """Promote a 1D row to a (1, width) batch; pass batches through unchanged.

    Returns ``(batch, was_1d)`` so the caller can squeeze the leading
    axis back out on output.
    """
    a = np.asarray(arr, dtype=np.uint8)
    if a.ndim == 1:
        if a.shape[0] != expected_width:
            raise ValueError(
                f"{name} 1D input must have length {expected_width}; got {a.shape[0]}"
            )
        return a.reshape(1, expected_width), True
    if a.ndim == 2:
        if a.shape[1] != expected_width:
            raise ValueError(
                f"{name} 2D input must have shape (batch, {expected_width}); got {a.shape}"
            )
        return a, False
    raise ValueError(f"{name} input must be 1D or 2D; got ndim={a.ndim}")


class RepetitionCode:
    """The classical (n, 1, n) repetition code over GF(2).

    Encodes a single bit ``b`` as ``(b, b, ..., b)`` of length ``n``;
    decodes by majority vote across the ``n`` received bits. The
    canonical generator matrix is the all-ones row vector
    ``G = [1 1 ... 1]`` and a convenient parity-check matrix is

    .. code-block::

        H = [[1, 1, 0, ..., 0],
             [1, 0, 1, 0,..., 0],
             ...
             [1, 0, 0, ..., 1]]   shape (n-1, n)

    i.e. each parity check asserts ``bit_0 == bit_i`` for ``i >= 1``.
    The syndrome is therefore the vector of mismatches between bit 0
    and the other bits.

    Parameters
    ----------
    n:
        Block length. Must be a positive odd integer so that the
        majority vote is unambiguous.
    """

    def __init__(self, n: int) -> None:
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"n must be a positive integer; got {n}")
        if n % 2 == 0:
            raise ValueError(f"n must be odd for unambiguous majority vote; got {n}")
        self.n = n
        self.k = 1
        self.d = n
        self.G: np.ndarray = np.ones((1, n), dtype=np.uint8)
        H = np.zeros((n - 1, n), dtype=np.uint8)
        for i in range(n - 1):
            H[i, 0] = 1
            H[i, i + 1] = 1
        self.H: np.ndarray = H
        logger.info("RepetitionCode(n=%d): rate=%g, d=%d", n, 1.0 / n, n)

    def encode(self, messages: np.ndarray) -> np.ndarray:
        """Encode ``k=1`` bit messages into length-``n`` codewords.

        ``messages`` may be a 1D array of shape ``(batch,)`` or a 2D
        array of shape ``(batch, 1)``. The return is a 2D array of
        shape ``(batch, n)``.
        """
        a = np.asarray(messages, dtype=np.uint8)
        if a.ndim == 1:
            a = a.reshape(-1, 1)
        if a.ndim != 2 or a.shape[1] != 1:
            raise ValueError(
                f"messages must have shape (batch,) or (batch, 1); got {a.shape}"
            )
        return np.tile(a, (1, self.n))

    def decode(self, received: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Majority-vote decode received words.

        Returns ``(decoded, syndromes)`` where ``decoded`` has shape
        ``(batch, 1)`` and ``syndromes`` has shape ``(batch, n - 1)``.
        A nonzero syndrome means at least one bit disagrees with bit
        0; majority vote still produces the correct answer as long as
        fewer than ``ceil(n/2)`` bits were flipped.
        """
        batch, _ = _as_batch(received, self.n, "received")
        votes = batch.sum(axis=1)
        decoded = (votes > (self.n // 2)).astype(np.uint8).reshape(-1, 1)
        syndromes = (self.H @ batch.T) % 2
        return decoded, syndromes.T


def _hamming74_G() -> np.ndarray:
    """Generator matrix for Hamming(7,4) in systematic form: data || parity.

    Layout: codeword = (d0, d1, d2, d3, p0, p1, p2), where
    p0 = d0 + d1 + d3, p1 = d0 + d2 + d3, p2 = d1 + d2 + d3 (mod 2).
    This corresponds to the standard ``[I_4 | A]`` form.
    """
    A = np.array(
        [
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    G = np.hstack([np.eye(4, dtype=np.uint8), A])
    return G


def _hamming74_H() -> np.ndarray:
    """Parity-check matrix matching ``_hamming74_G``.

    With ``G = [I_4 | A]``, the parity-check matrix is
    ``H = [A.T | I_3]``. ``H @ G.T mod 2 == 0`` by construction.
    """
    A = np.array(
        [
            [1, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    H = np.hstack([A.T, np.eye(3, dtype=np.uint8)])
    return H


def _hamming74_syndrome_table(H: np.ndarray) -> np.ndarray:
    """Map an integer-encoded syndrome to its single-bit error pattern.

    There are 2**3 = 8 possible syndromes for Hamming(7,4); the zero
    syndrome maps to the zero error, and each of the 7 nonzero
    syndromes is a column of ``H`` (in some order), uniquely
    identifying which of the 7 bit positions to flip. The returned
    table has shape ``(8, 7)``; row ``s`` is the error pattern to XOR
    into the received word.
    """
    table = np.zeros((8, 7), dtype=np.uint8)
    for j in range(7):
        col = H[:, j]
        idx = int(col[0]) * 4 + int(col[1]) * 2 + int(col[2])
        pattern = np.zeros(7, dtype=np.uint8)
        pattern[j] = 1
        table[idx] = pattern
    return table


class Hamming74:
    """The Hamming (7, 4, 3) code in systematic form.

    Corrects any single-bit error per 7-bit block; detects but cannot
    correct two-bit errors. Code rate is ``k / n = 4 / 7``.

    Attributes
    ----------
    n, k, d:
        Block length 7, message length 4, minimum distance 3.
    G:
        Generator matrix of shape ``(4, 7)``, systematic ``[I_4 | A]``.
    H:
        Parity-check matrix of shape ``(3, 7)``, matching ``[A.T | I_3]``.
    syndrome_table:
        Lookup table of shape ``(8, 7)`` mapping the integer-encoded
        syndrome to the error pattern to XOR into the received word.
    """

    n: int = 7
    k: int = 4
    d: int = 3

    def __init__(self) -> None:
        self.G: np.ndarray = _hamming74_G()
        self.H: np.ndarray = _hamming74_H()
        self.syndrome_table: np.ndarray = _hamming74_syndrome_table(self.H)
        logger.info("Hamming74: rate=4/7, d=3, syndrome table cached")

    def encode(self, messages: np.ndarray) -> np.ndarray:
        """Encode 4-bit messages into 7-bit codewords.

        ``messages`` has shape ``(batch, 4)`` (a 1D ``(4,)`` input is
        promoted to ``(1, 4)``). The return has shape ``(batch, 7)``.
        """
        batch, was_1d = _as_batch(messages, self.k, "messages")
        codewords = (batch @ self.G) % 2
        if was_1d:
            return codewords.reshape(self.n).astype(np.uint8)
        return codewords.astype(np.uint8)

    def syndrome(self, received: np.ndarray) -> np.ndarray:
        """Compute the syndrome ``s = H y^T mod 2``.

        ``received`` has shape ``(batch, 7)``; the return has shape
        ``(batch, 3)``. A 1D input is promoted and the leading axis
        squeezed back out on return.
        """
        batch, was_1d = _as_batch(received, self.n, "received")
        s = (self.H @ batch.T) % 2
        if was_1d:
            return s.T.reshape(self.H.shape[0]).astype(np.uint8)
        return s.T.astype(np.uint8)

    def decode(self, received: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Syndrome-decode received words.

        For each received word, compute the syndrome, look up the
        single-bit error pattern, and XOR it in. Returns
        ``(corrected, syndromes)`` with the leading axis squeezed back
        out for a 1D input.
        """
        batch, was_1d = _as_batch(received, self.n, "received")
        s = (self.H @ batch.T) % 2  # shape (3, batch)
        s_int = s[0] * 4 + s[1] * 2 + s[2]
        patterns = self.syndrome_table[s_int]  # shape (batch, 7)
        corrected = (batch ^ patterns).astype(np.uint8)
        syndromes = s.T.astype(np.uint8)
        if was_1d:
            return corrected.reshape(self.n), syndromes.reshape(self.H.shape[0])
        return corrected, syndromes

    def extract_message(self, codewords: np.ndarray) -> np.ndarray:
        """Pull the 4-bit message out of a (corrected) systematic codeword.

        The systematic form puts the data bits in positions 0..3.
        """
        batch, was_1d = _as_batch(codewords, self.n, "codewords")
        msgs = batch[:, : self.k].astype(np.uint8)
        if was_1d:
            return msgs.reshape(self.k)
        return msgs
