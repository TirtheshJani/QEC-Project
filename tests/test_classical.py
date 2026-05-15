"""Tests for classical error-correcting codes (Phase 0 promotion).

Property tests cover:
- Hamming(7,4) algebraic identities (`G H^T = 0` over GF(2)).
- Encode/decode round-trip on random messages with no channel errors.
- Exhaustive single-bit error correction (all 7 error positions).
- Sanity: two-bit errors are not guaranteed to be corrected.
- BSC simulator returns a valid probability and is loosely monotone in p.
- 3-repetition code: majority decode + BSC simulator behaviour.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from qec_project.codes.classical import (
    RepetitionCode,
    decode,
    encode,
    hamming74_generator,
    hamming74_parity_check,
    simulate_bsc,
    syndrome,
)


def test_generator_parity_orthogonality() -> None:
    G = hamming74_generator()
    H = hamming74_parity_check()
    assert G.shape == (4, 7)
    assert H.shape == (3, 7)
    product = (G @ H.T) % 2
    assert np.array_equal(product, np.zeros((4, 3), dtype=int))


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_encode_then_decode_no_error(seed: int) -> None:
    rng = np.random.default_rng(seed)
    for _ in range(16):
        msg = rng.integers(0, 2, size=4).astype(np.uint8)
        codeword = encode(msg)
        recovered = decode(codeword)
        assert np.array_equal(recovered, msg)


def test_decode_corrects_every_single_bit_error() -> None:
    H = hamming74_parity_check()
    # All 16 messages, all 7 single-bit error positions.
    for m in range(16):
        msg = np.array([(m >> i) & 1 for i in range(4)], dtype=np.uint8)
        codeword = encode(msg)
        for pos in range(7):
            received = codeword.copy()
            received[pos] ^= 1
            # Syndrome should be non-zero for a non-zero error.
            s = syndrome(received, H)
            assert np.any(s != 0)
            recovered = decode(received)
            assert np.array_equal(recovered, msg), (
                f"failed on msg={msg.tolist()} pos={pos}"
            )


def test_two_bit_errors_are_not_always_corrected() -> None:
    # Hamming(7,4) has distance 3; it cannot correct >=2 errors in general.
    msg = np.array([1, 0, 1, 1], dtype=np.uint8)
    codeword = encode(msg)
    mismatches = 0
    for i in range(7):
        for j in range(i + 1, 7):
            received = codeword.copy()
            received[i] ^= 1
            received[j] ^= 1
            recovered = decode(received)
            if not np.array_equal(recovered, msg):
                mismatches += 1
    assert mismatches > 0


def test_simulate_bsc_returns_probability() -> None:
    rng = np.random.default_rng(42)
    p_log = simulate_bsc(n_shots=2_000, p_flip=0.05, rng=rng)
    assert 0.0 <= p_log <= 1.0


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    p_low=st.floats(min_value=0.005, max_value=0.05),
    gap=st.floats(min_value=0.05, max_value=0.15),
)
def test_simulate_bsc_loose_monotonicity(p_low: float, gap: float) -> None:
    # Use a fixed seed inside the test so hypothesis shrinking is reproducible.
    rng_lo = np.random.default_rng(20260515)
    rng_hi = np.random.default_rng(20260515)
    p_high = p_low + gap
    p_log_low = simulate_bsc(n_shots=20_000, p_flip=p_low, rng=rng_lo)
    p_log_high = simulate_bsc(n_shots=20_000, p_flip=p_high, rng=rng_hi)
    # Allow Monte-Carlo slack: smaller p should not produce a *much* higher
    # logical error rate than larger p.
    assert p_log_low <= p_log_high + 0.02


def test_repetition_code_decode_corrects_single_errors() -> None:
    code = RepetitionCode(n=3)
    for bit in (0, 1):
        codeword = code.encode(bit)
        assert codeword.shape == (3,)
        for pos in range(3):
            received = codeword.copy()
            received[pos] ^= 1
            assert code.decode(received) == bit


def test_repetition_code_bsc_probability_in_range() -> None:
    code = RepetitionCode(n=3)
    rng = np.random.default_rng(123)
    p_log = code.simulate_bsc(n_shots=2_000, p_flip=0.1, rng=rng)
    assert 0.0 <= p_log <= 1.0
