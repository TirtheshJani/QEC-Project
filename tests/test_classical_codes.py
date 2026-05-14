"""Tests for :mod:`qec_project.codes.classical` (Phase 0.3 promoted helpers)."""

from __future__ import annotations

import itertools

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.codes.classical import Hamming74, RepetitionCode
from qec_project.noise.classical import bsc_flip

# ---------- repetition(3, 1) ----------


def test_rep3_construction_rejects_even_n() -> None:
    with pytest.raises(ValueError):
        RepetitionCode(4)


def test_rep3_construction_rejects_nonpositive_n() -> None:
    with pytest.raises(ValueError):
        RepetitionCode(0)


def test_rep3_G_and_H_orthogonal_mod2() -> None:
    code = RepetitionCode(3)
    product = (code.H @ code.G.T) % 2
    assert np.array_equal(product, np.zeros_like(product))


def test_rep3_encode_zero_msg_is_zero_codeword() -> None:
    code = RepetitionCode(3)
    out = code.encode(np.array([0], dtype=np.uint8))
    assert np.array_equal(out, np.zeros((1, 3), dtype=np.uint8))


def test_rep3_encode_one_msg_is_all_ones_codeword() -> None:
    code = RepetitionCode(3)
    out = code.encode(np.array([1], dtype=np.uint8))
    assert np.array_equal(out, np.ones((1, 3), dtype=np.uint8))


def test_rep3_decode_noiseless_round_trip() -> None:
    code = RepetitionCode(3)
    msgs = np.array([[0], [1]], dtype=np.uint8)
    codewords = code.encode(msgs)
    decoded, _ = code.decode(codewords)
    assert np.array_equal(decoded, msgs)


def test_rep3_decode_corrects_every_single_bit_flip() -> None:
    code = RepetitionCode(3)
    for m in (0, 1):
        codeword = code.encode(np.array([m], dtype=np.uint8))[0]
        for pos in range(3):
            received = codeword.copy()
            received[pos] ^= 1
            decoded, _ = code.decode(received.reshape(1, 3))
            assert int(decoded[0, 0]) == m


def test_rep3_decode_fails_on_two_bit_flips() -> None:
    """Two flips invert the majority vote: this is a sanity check, not a feature."""
    code = RepetitionCode(3)
    codeword = code.encode(np.array([0], dtype=np.uint8))[0].copy()
    codeword[0] ^= 1
    codeword[1] ^= 1
    decoded, _ = code.decode(codeword.reshape(1, 3))
    assert int(decoded[0, 0]) == 1  # wrong, by design of the (3,1) code


def test_rep3_syndrome_zero_for_codeword() -> None:
    code = RepetitionCode(3)
    codewords = code.encode(np.array([[0], [1]], dtype=np.uint8))
    _, syndromes = code.decode(codewords)
    assert np.array_equal(syndromes, np.zeros((2, 2), dtype=np.uint8))


# ---------- Hamming(7, 4) ----------


def test_hamming74_G_and_H_orthogonal_mod2() -> None:
    code = Hamming74()
    product = (code.H @ code.G.T) % 2
    assert np.array_equal(product, np.zeros_like(product))


def test_hamming74_G_shape_and_H_shape() -> None:
    code = Hamming74()
    assert code.G.shape == (4, 7)
    assert code.H.shape == (3, 7)


def test_hamming74_encode_zero_msg_is_zero_codeword() -> None:
    code = Hamming74()
    out = code.encode(np.zeros((1, 4), dtype=np.uint8))
    assert np.array_equal(out, np.zeros((1, 7), dtype=np.uint8))


def test_hamming74_codeword_dimensions() -> None:
    code = Hamming74()
    msgs = np.array(list(itertools.product([0, 1], repeat=4)), dtype=np.uint8)
    cw = code.encode(msgs)
    assert cw.shape == (16, 7)


def test_hamming74_round_trip_noiseless() -> None:
    code = Hamming74()
    msgs = np.array(list(itertools.product([0, 1], repeat=4)), dtype=np.uint8)
    cw = code.encode(msgs)
    corrected, syndromes = code.decode(cw)
    assert np.array_equal(syndromes, np.zeros((16, 3), dtype=np.uint8))
    assert np.array_equal(code.extract_message(corrected), msgs)


def test_hamming74_corrects_every_single_bit_error() -> None:
    code = Hamming74()
    msgs = np.array(list(itertools.product([0, 1], repeat=4)), dtype=np.uint8)
    cw = code.encode(msgs)
    for pos in range(7):
        flipped = cw.copy()
        flipped[:, pos] ^= 1
        corrected, _ = code.decode(flipped)
        recovered = code.extract_message(corrected)
        assert np.array_equal(recovered, msgs), f"failed to correct flip at position {pos}"


def test_hamming74_syndrome_zero_for_codeword() -> None:
    code = Hamming74()
    msgs = np.array(list(itertools.product([0, 1], repeat=4)), dtype=np.uint8)
    cw = code.encode(msgs)
    s = code.syndrome(cw)
    assert np.array_equal(s, np.zeros((16, 3), dtype=np.uint8))


def test_hamming74_syndrome_matches_H_column_for_single_error() -> None:
    code = Hamming74()
    cw = code.encode(np.zeros((1, 4), dtype=np.uint8))[0]
    for pos in range(7):
        received = cw.copy()
        received[pos] ^= 1
        s = code.syndrome(received)
        assert np.array_equal(s, code.H[:, pos]), f"syndrome wrong for flip at {pos}"


def test_hamming74_1d_input_returns_1d_output() -> None:
    code = Hamming74()
    msg = np.array([1, 0, 1, 1], dtype=np.uint8)
    cw = code.encode(msg)
    assert cw.shape == (7,)
    s = code.syndrome(cw)
    assert s.shape == (3,)
    corrected, syn = code.decode(cw)
    assert corrected.shape == (7,)
    assert syn.shape == (3,)
    assert np.array_equal(code.extract_message(cw), msg)


# ---------- Monte Carlo properties ----------


def _rep3_logical_error_rate(p: float, n_trials: int, rng: np.random.Generator) -> float:
    code = RepetitionCode(3)
    msgs = rng.integers(0, 2, size=(n_trials, 1), dtype=np.uint8)
    cw = code.encode(msgs)
    received = bsc_flip(cw, p, rng)
    decoded, _ = code.decode(received)
    return float(np.mean(decoded != msgs))


def _hamming74_logical_error_rate(p: float, n_trials: int, rng: np.random.Generator) -> float:
    code = Hamming74()
    msgs = rng.integers(0, 2, size=(n_trials, 4), dtype=np.uint8)
    cw = code.encode(msgs)
    received = bsc_flip(cw, p, rng)
    corrected, _ = code.decode(received)
    recovered = code.extract_message(corrected)
    return float(np.mean(recovered != msgs))


@given(
    p1=st.floats(min_value=0.01, max_value=0.2),
    delta=st.floats(min_value=0.05, max_value=0.2),
    seed=st.integers(min_value=0, max_value=2**32 - 1),
)
@settings(max_examples=10, deadline=None)
def test_rep3_logical_error_rate_monotone_in_p(p1: float, delta: float, seed: int) -> None:
    p2 = min(p1 + delta, 0.45)
    n = 4000
    rng = np.random.default_rng(seed)
    r1 = _rep3_logical_error_rate(p1, n, rng)
    r2 = _rep3_logical_error_rate(p2, n, rng)
    slack = 5.0 / np.sqrt(n)
    assert r2 + slack >= r1


@given(
    p1=st.floats(min_value=0.01, max_value=0.15),
    delta=st.floats(min_value=0.05, max_value=0.2),
    seed=st.integers(min_value=0, max_value=2**32 - 1),
)
@settings(max_examples=10, deadline=None)
def test_hamming74_logical_error_rate_monotone_in_p(
    p1: float, delta: float, seed: int
) -> None:
    p2 = min(p1 + delta, 0.4)
    n = 4000
    rng = np.random.default_rng(seed)
    r1 = _hamming74_logical_error_rate(p1, n, rng)
    r2 = _hamming74_logical_error_rate(p2, n, rng)
    slack = 5.0 / np.sqrt(n)
    assert r2 + slack >= r1
