"""Classical error-correcting codes promoted from Phase 0 notebooks.

Two codes are exposed:

* Hamming(7,4): a length-7, dimension-4 linear binary code that corrects any
  single-bit error. Used as the canonical worked example before stabilizer
  codes are introduced in Phase 2.
* `RepetitionCode`: an n-bit repetition code with majority-vote decoding.

All arithmetic is performed over GF(2) using ``numpy`` ``uint8`` arrays. The
parity-check / generator matrices are stored in *systematic* form so the
first ``k`` bits of each codeword equal the message bits, which keeps the
decoder's bookkeeping trivial.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = [
    "RepetitionCode",
    "decode",
    "encode",
    "hamming74_generator",
    "hamming74_parity_check",
    "simulate_bsc",
    "syndrome",
]


# Systematic Hamming(7,4): codeword bits 1..4 are the message, bits 5..7 are
# parity. The parity submatrix `P` below is the standard textbook choice
# (Nielsen & Chuang §10.1; MacKay §1.2).
_P: NDArray[np.uint8] = np.array(
    [
        [1, 1, 0],
        [0, 1, 1],
        [1, 1, 1],
        [1, 0, 1],
    ],
    dtype=np.uint8,
)


def hamming74_generator() -> NDArray[np.uint8]:
    """Return the 4x7 generator matrix of Hamming(7,4) in systematic form."""
    return np.hstack([np.eye(4, dtype=np.uint8), _P])


def hamming74_parity_check() -> NDArray[np.uint8]:
    """Return the 3x7 parity-check matrix corresponding to ``hamming74_generator``."""
    return np.hstack([_P.T, np.eye(3, dtype=np.uint8)])


def _as_bits(arr: NDArray[np.integer]) -> NDArray[np.uint8]:
    return np.asarray(arr, dtype=np.uint8) & 1


def encode(message: NDArray[np.integer]) -> NDArray[np.uint8]:
    """Encode a length-4 binary message into a length-7 Hamming codeword."""
    msg = _as_bits(message)
    if msg.shape != (4,):
        raise ValueError(f"message must have shape (4,), got {msg.shape}")
    G = hamming74_generator()
    return (msg @ G) % 2


def syndrome(received: NDArray[np.integer], H: NDArray[np.integer]) -> NDArray[np.uint8]:
    """Compute the syndrome ``H r^T (mod 2)`` for a received vector."""
    r = _as_bits(received)
    H_bits = _as_bits(H)
    if r.shape[-1] != H_bits.shape[1]:
        raise ValueError(
            f"received length {r.shape[-1]} incompatible with H shape {H_bits.shape}"
        )
    return (H_bits @ r) % 2


# Precompute syndrome -> error-bit lookup. With our `H` the syndrome equals
# the column of `H` indexed by the flipped bit, so we tabulate each column
# read as a 3-bit integer.
def _build_syndrome_table() -> dict[int, int]:
    H = hamming74_parity_check()
    table: dict[int, int] = {0: -1}  # syndrome 0 means "no error"
    for j in range(7):
        col = H[:, j]
        key = int(col[0]) << 2 | int(col[1]) << 1 | int(col[2])
        table[key] = j
    return table


_SYNDROME_TABLE: dict[int, int] = _build_syndrome_table()


def decode(received: NDArray[np.integer]) -> NDArray[np.uint8]:
    """Decode a length-7 Hamming(7,4) received vector to its 4-bit message.

    Corrects any single-bit error. Two-bit errors are silently mis-decoded;
    that limit is the point of the test suite's ``test_two_bit_errors`` case.
    """
    r = _as_bits(received).copy()
    if r.shape != (7,):
        raise ValueError(f"received must have shape (7,), got {r.shape}")
    H = hamming74_parity_check()
    s = syndrome(r, H)
    key = int(s[0]) << 2 | int(s[1]) << 1 | int(s[2])
    err_idx = _SYNDROME_TABLE[key]
    if err_idx >= 0:
        r[err_idx] ^= 1
    # Systematic encoding: first 4 bits of the (corrected) codeword are the message.
    return r[:4]


def simulate_bsc(n_shots: int, p_flip: float, rng: np.random.Generator) -> float:
    """Monte-Carlo estimate of the Hamming(7,4) block error rate over a BSC.

    A "block error" is any decoded message bit that differs from the
    transmitted message. Each shot draws a fresh random 4-bit message,
    encodes it, applies independent bit flips with probability ``p_flip``,
    and decodes.
    """
    if n_shots <= 0:
        raise ValueError("n_shots must be positive")
    if not 0.0 <= p_flip <= 1.0:
        raise ValueError("p_flip must be in [0, 1]")

    messages = rng.integers(0, 2, size=(n_shots, 4), dtype=np.uint8)
    G = hamming74_generator()
    codewords = (messages @ G) % 2
    flips = (rng.random(size=codewords.shape) < p_flip).astype(np.uint8)
    received = (codewords ^ flips).astype(np.uint8)

    H = hamming74_parity_check()
    syndromes = (received @ H.T) % 2  # (n_shots, 3)
    keys = (syndromes[:, 0] << 2) | (syndromes[:, 1] << 1) | syndromes[:, 2]

    corrected = received.copy()
    for key, err_idx in _SYNDROME_TABLE.items():
        if err_idx < 0:
            continue
        mask = keys == key
        corrected[mask, err_idx] ^= 1

    decoded = corrected[:, :4]
    block_errors = np.any(decoded != messages, axis=1)
    return float(block_errors.mean())


class RepetitionCode:
    """n-bit repetition code with majority-vote decoding.

    Useful as a *classical* baseline curve in the Phase 0 BSC plot, and as
    a warm-up for the quantum 3-qubit repetition code in Phase 2.
    """

    def __init__(self, n: int = 3) -> None:
        if n < 1 or n % 2 == 0:
            raise ValueError("n must be a positive odd integer")
        self.n = n

    def encode(self, bit: int) -> NDArray[np.uint8]:
        if bit not in (0, 1):
            raise ValueError("bit must be 0 or 1")
        return np.full(self.n, bit, dtype=np.uint8)

    def decode(self, received: NDArray[np.integer]) -> int:
        r = _as_bits(received)
        if r.shape != (self.n,):
            raise ValueError(f"received must have shape ({self.n},), got {r.shape}")
        # Majority vote: bit equals 1 if more than half the entries are 1.
        return int(r.sum() > self.n // 2)

    def simulate_bsc(
        self, n_shots: int, p_flip: float, rng: np.random.Generator
    ) -> float:
        """Monte-Carlo BSC logical error rate under majority decoding."""
        if n_shots <= 0:
            raise ValueError("n_shots must be positive")
        if not 0.0 <= p_flip <= 1.0:
            raise ValueError("p_flip must be in [0, 1]")

        bits = rng.integers(0, 2, size=n_shots, dtype=np.uint8)
        codewords = np.repeat(bits[:, None], self.n, axis=1)
        flips = (rng.random(size=codewords.shape) < p_flip).astype(np.uint8)
        received = (codewords ^ flips).astype(np.uint8)
        # Majority vote per row.
        decoded = (received.sum(axis=1) > self.n // 2).astype(np.uint8)
        return float((decoded != bits).mean())
