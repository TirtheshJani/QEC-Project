"""Tests for the Steane [[7,1,3]] CSS code.

Distance check is by exhaustive enumeration over weight-1 and weight-2
Pauli errors on 7 qubits, which is small and fast (~ 9000 patterns).
"""

from __future__ import annotations

import itertools

from qec_project.codes.pauli import Pauli, commutes_with_set
from qec_project.codes.steane import (
    steane_logical_x,
    steane_logical_z,
    steane_stabilizers,
    verify_steane,
)


def test_verify_steane_true() -> None:
    assert verify_steane()


def test_six_stabilizers_on_seven_qubits() -> None:
    stabs = steane_stabilizers()
    assert len(stabs) == 6
    for s in stabs:
        assert s.n == 7
        # Steane stabilizers are weight 4.
        assert s.weight() == 4


def test_logicals_have_weight_three_or_more() -> None:
    lx = steane_logical_x()
    lz = steane_logical_z()
    # Standard choice has weight 3 (a row of the Hamming generator).
    assert lx.weight() == 3
    assert lz.weight() == 3
    # And they belong to the right Pauli type (X-only / Z-only).
    assert not lx.z.any()
    assert not lz.x.any()


def test_logical_x_anticommutes_with_logical_z() -> None:
    assert not steane_logical_x().commutes_with(steane_logical_z())


def test_logicals_commute_with_all_stabilizers() -> None:
    stabs = steane_stabilizers()
    assert commutes_with_set(steane_logical_x(), stabs)
    assert commutes_with_set(steane_logical_z(), stabs)


def _all_low_weight_paulis(n: int, max_weight: int) -> list[Pauli]:
    """Enumerate every Pauli on ``n`` qubits with weight in [1, max_weight]."""

    out: list[Pauli] = []
    letters = ("X", "Y", "Z")
    for w in range(1, max_weight + 1):
        for positions in itertools.combinations(range(n), w):
            for choice in itertools.product(letters, repeat=w):
                body = ["I"] * n
                for pos, letter in zip(positions, choice, strict=True):
                    body[pos] = letter
                out.append(Pauli.from_string("".join(body)))
    return out


def test_distance_at_least_three() -> None:
    """No weight <= 2 error is an undetectable non-trivial logical operator.

    "Undetectable" = commutes with every stabilizer. To rule out distance 1
    or 2, we require every weight-1 or weight-2 Pauli to anti-commute with
    at least one stabilizer (i.e., produce a non-zero syndrome). The logical
    operators themselves have weight 3, so this is the textbook distance-3
    proof.
    """

    stabs = steane_stabilizers()
    errors = _all_low_weight_paulis(7, 2)
    # 7*3 = 21 weight-1, C(7,2)*9 = 189 weight-2, total 210.
    assert len(errors) == 21 + 189
    for err in errors:
        # Every low-weight error must trigger at least one syndrome bit.
        assert not commutes_with_set(err, stabs), (
            f"weight-{err.weight()} error {err.to_string()} is undetected"
        )


def test_weight_three_logical_x_is_undetectable() -> None:
    # Sanity-check the other direction: at weight 3 we *do* have an
    # undetectable error (the logical X itself).
    stabs = steane_stabilizers()
    assert commutes_with_set(steane_logical_x(), stabs)
    assert steane_logical_x().weight() == 3
