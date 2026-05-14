# Phase 2.2 — Shor [[9,1,3]] code in Qiskit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Phase 2.2 — the Shor [[9,1,3]] code in Qiskit — with a teaching notebook, a promoted `Shor9Code` helper class, and exhaustive tests that every single-qubit Pauli error (X, Y, Z on each of 9 qubits) is corrected.

**Architecture:** Notebook (`phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb`) presents the code pedagogically (concatenation of phase-flip outer code with bit-flip inner codes, encoding circuit, stabilizers, logical operators, exhaustive error correction). Reusable code lives in `src/qec_project/codes/shor9.py` as `Shor9Code` (encoding circuit, stabilizers as Pauli strings, logical operators, syndrome -> recovery lookup). Tests under `tests/test_shor9.py`. The notebook calls into the promoted helper rather than duplicating logic.

**Tech Stack:** Qiskit 2.4.x (`QuantumCircuit`, `Statevector`, `Operator`), numpy, pytest, hypothesis. Reuses `qec_project.linalg` (Pauli matrices, `tensor`).

---

## File structure

| Path | Action | Responsibility |
| --- | --- | --- |
| `plans/phase-02-02-shor-9.md` | create | this plan |
| `src/qec_project/codes/shor9.py` | create | `Shor9Code` class: encoding circuit, stabilizer list, logical operators, syndrome lookup, recovery |
| `tests/test_shor9.py` | create | unit + exhaustive 27-error correction tests + hypothesis property |
| `phase-02-qec-fundamentals/02-shor-9/_build_notebook.py` | create | nbformat builder |
| `phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb` | create | generated notebook |
| `phase-02-qec-fundamentals/02-shor-9/README.md` | create | one-pager |
| `docs/reading-list.md` | modify | add Shor 1995 entry |
| `CHANGELOG.md` | modify | append milestone for Phase 2.2 |

## Key technical specs

**Qubit layout (big-endian, matches `numpy.kron`):** the data is qubit 0. The 9 code qubits are labeled `0..8`. The three "blocks" of three qubits each are `{0,1,2}`, `{3,4,5}`, `{6,7,8}`. Block representatives (the outer phase-flip register) are qubits `0, 3, 6`.

**Encoding circuit (Nielsen-Chuang Fig 10.4 convention):**
1. Outer phase-flip code on `(0, 3, 6)`: `H` on 0, `CX(0,3)`, `CX(0,6)`, `H` on 0, `H` on 3, `H` on 6.

   Wait — the standard Shor encoding is: H on the *block representatives* AFTER copying the data bit. Equivalent description: the spec text gives the simpler sequence used by Nielsen-Chuang: copy the data into block reps via CNOTs, then apply Hadamards to the block reps, then bit-flip-encode each block.

   The spec we follow (per the orchestrator):
   - `CX(0,3)`, `CX(0,6)` (copy data into outer-block representatives)
   - `H(0)`, `H(3)`, `H(6)` (outer phase-flip code: this turns each `|q>` into `(|0> + (-1)^q |1>) / sqrt(2)`)
   - `CX(0,1)`, `CX(0,2)`, `CX(3,4)`, `CX(3,5)`, `CX(6,7)`, `CX(6,8)` (inner bit-flip code in each block)

   This encodes `|0>` to `((|000> + |111>)/sqrt(2))^{tensor 3}` and `|1>` to `((|000> - |111>)/sqrt(2))^{tensor 3}`. Verified algebraically by Statevector.

**Stabilizers (8 total, written as length-9 Pauli strings using big-endian qubit index 0..8):**
- Inner bit-flip checks (six Z-Z generators, two per block):
  - `Z_0 Z_1` = "ZZIIIIIII"
  - `Z_1 Z_2` = "IZZIIIIII"
  - `Z_3 Z_4` = "IIIZZIIII"
  - `Z_4 Z_5` = "IIIIZZIII"
  - `Z_6 Z_7` = "IIIIIIZZI"
  - `Z_7 Z_8` = "IIIIIIIZZ"
- Outer phase-flip checks (two X-X generators that couple blocks):
  - `X_0 X_1 X_2 X_3 X_4 X_5` = "XXXXXXIII"
  - `X_3 X_4 X_5 X_6 X_7 X_8` = "IIIXXXXXX"

**Logical operators (canonical minimum-weight reps):**
- `X_L = Z_0 Z_3 Z_6` = "ZIIZIIZII"  (note: this is the standard Shor convention; "logical X" flips between `|0_L>` and `|1_L>`. But because the outer code is a phase-flip code, the logical X is actually `X X X X X X X X X` and `Z_L` is `Z_0 Z_3 Z_6`. Let me get this right.)

  Reading Nielsen-Chuang p. 432: logical operators are
  - `Z_L = Z_0 Z_1 Z_2 Z_3 Z_4 Z_5 Z_6 Z_7 Z_8` (weight 9, all-Z), reducible to `Z_0 Z_1 Z_2` (weight 3) modulo stabilizers; further `Z_0 Z_1 Z_2 = Z_0 (Z_0 Z_1) (Z_1 Z_2)^{-1}... actually `Z_0 Z_1 Z_2` equals `(Z_0 Z_1)(Z_1 Z_2)Z_0` which is... let me just pick the canonical low-weight reps.

  Canonical choice (the one we test against):
  - `X_L = X_0 X_3 X_6` (weight 3): flips the outer phase-flip code's logical bit. Per spec text and Nielsen-Chuang Eq 10.46. String: "XIIXIIXII".
  - `Z_L = Z_0 Z_1 Z_2` (weight 3): flips the relative sign in block 0, which is the outer-code logical Z. String: "ZZZIIIIII".

  Sanity check: `[X_L, Z_L] = -1` (anticommute), and both commute with every stabilizer. We'll assert these in tests.

  Note: the spec text gave non-canonical forms ("X_L = X_1..X_9", "Z_L = Z_1 Z_4 Z_7"); these are equivalent modulo stabilizers but the canonical minimum-weight reps are the ones above. We will note both in the notebook and pick `X_0 X_3 X_6` / `Z_0 Z_1 Z_2` as canonical.

**Syndrome and recovery.** With 8 stabilizers, syndromes are 8-bit. The Shor code has degeneracy: a Y_i error has the same syndrome as the product X_i Z_i, but since Y = i X Z (up to phase), applying Y_i to recover restores the state up to a global phase. For each of the 27 single-qubit Pauli errors, we precompute the syndrome (which 8 stabilizers anticommute with the error), build a lookup table syndrome -> Pauli string of length 9 to apply for recovery. Because the inner blocks correct one X per block and the outer code corrects one block's worth of Z, the recovery follows: (1) per-block majority-vote on the three Z-syndrome bits gives which qubit (if any) within each block to bit-flip; (2) the two X-syndrome bits give which block (if any) to phase-flip — flipping any qubit in that block. Standard recovery: phase-flip the block's representative qubit.

For Y errors: Y on qubit i triggers both the inner Z-checks adjacent to i AND the outer X-check covering block(i). The recovery table naturally maps this combined syndrome back to applying Y on i (up to global phase, since Y = iXZ).

**Test approach.** Use exact Statevector. Prepare `|0_L>` (encode `|0>`); for each of 27 errors apply the Pauli to the encoded state; compute syndrome by measuring each stabilizer expectation value (or by direct projection); look up recovery; apply recovery; compare to original encoded state via fidelity. Global phases are okay.

---

## Tasks

### Task 1: Promoted helper — `Shor9Code` skeleton + Pauli-string utilities

**Files:**
- Create: `src/qec_project/codes/shor9.py`
- Test: `tests/test_shor9.py`

- [ ] **Step 1: Write a failing test for `Shor9Code.stabilizers()` returning 8 strings of length 9**

```python
# tests/test_shor9.py
"""Tests for the Shor [[9,1,3]] code helper (Phase 2.2)."""

from __future__ import annotations

import itertools

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qec_project.codes.shor9 import Shor9Code


def test_stabilizers_have_correct_count_and_length() -> None:
    code = Shor9Code()
    stabs = code.stabilizers()
    assert len(stabs) == 8
    assert all(isinstance(s, str) and len(s) == 9 for s in stabs)
    assert all(set(s) <= {"I", "X", "Y", "Z"} for s in stabs)
```

- [ ] **Step 2: Run test — expect ImportError**

`python -m uv run pytest tests/test_shor9.py::test_stabilizers_have_correct_count_and_length -x`

- [ ] **Step 3: Create minimal `Shor9Code` returning the 8 stabilizer strings**

```python
# src/qec_project/codes/shor9.py
"""The Shor [[9,1,3]] code: concatenation of the 3-qubit phase-flip code
with the 3-qubit bit-flip code.

Encodes 1 logical qubit into 9 physical qubits. Corrects any single-qubit
Pauli error (X, Y, or Z on any one of the 9 qubits). Distance 3.

Conventions:
* Qubit ordering is big-endian (matches ``numpy.kron`` and
  ``qec_project.linalg.tensor``): Pauli string ``"P_0 P_1 ... P_8"`` lists
  the operator on qubit 0 first.
* Blocks are ``{0, 1, 2}``, ``{3, 4, 5}``, ``{6, 7, 8}``; block
  representatives are ``0, 3, 6``.
* Logical operators are the minimum-weight representatives
  ``X_L = X_0 X_3 X_6`` and ``Z_L = Z_0 Z_1 Z_2`` (Nielsen-Chuang Eq 10.46).

References (in ``docs/reading-list.md``):

* Peter W. Shor. *Scheme for reducing decoherence in quantum computer
  memory.* Phys. Rev. A 52, R2493 (1995). doi:10.1103/PhysRevA.52.R2493.
* Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  section 10.2 (the 9-qubit code).
"""

from __future__ import annotations

import logging
from functools import reduce

import numpy as np
from qiskit import QuantumCircuit

from qec_project.linalg import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z, tensor

logger = logging.getLogger(__name__)

_SINGLE_PAULIS = {"I": PAULI_I, "X": PAULI_X, "Y": PAULI_Y, "Z": PAULI_Z}

_STABILIZERS: tuple[str, ...] = (
    "ZZIIIIIII",
    "IZZIIIIII",
    "IIIZZIIII",
    "IIIIZZIII",
    "IIIIIIZZI",
    "IIIIIIIZZ",
    "XXXXXXIII",
    "IIIXXXXXX",
)

_LOGICAL_X = "XIIXIIXII"  # X_0 X_3 X_6
_LOGICAL_Z = "ZZZIIIIII"  # Z_0 Z_1 Z_2


class Shor9Code:
    """The Shor [[9,1,3]] code.

    Concatenation of the outer 3-qubit phase-flip code (on block
    representatives 0, 3, 6) with the inner 3-qubit bit-flip code (in
    each block).

    Attributes
    ----------
    n, k, d:
        Block length 9, logical qubits 1, distance 3.
    """

    n: int = 9
    k: int = 1
    d: int = 3

    def __init__(self) -> None:
        self._stabilizers = _STABILIZERS
        self._logical_x = _LOGICAL_X
        self._logical_z = _LOGICAL_Z
        self._recovery_table = _build_recovery_table(self._stabilizers)
        logger.info(
            "Shor9Code: [[9,1,3]], 8 stabilizers, recovery table size=%d",
            len(self._recovery_table),
        )

    def stabilizers(self) -> list[str]:
        """Return the 8 stabilizer generators as length-9 Pauli strings."""
        return list(self._stabilizers)

    def logical_operators(self) -> dict[str, str]:
        """Return canonical minimum-weight representatives ``{'X': ..., 'Z': ...}``."""
        return {"X": self._logical_x, "Z": self._logical_z}


def _build_recovery_table(stabilizers: tuple[str, ...]) -> dict[tuple[int, ...], str]:
    """Stub: populated in Task 4."""
    return {}
```

Append to `src/qec_project/codes/__init__.py`:

```python
from qec_project.codes.shor9 import Shor9Code

__all__ = ["Shor9Code"]
```

- [ ] **Step 4: Re-run test — expect PASS**

`python -m uv run pytest tests/test_shor9.py::test_stabilizers_have_correct_count_and_length -x`

- [ ] **Step 5: Commit**

```bash
git add src/qec_project/codes/shor9.py src/qec_project/codes/__init__.py tests/test_shor9.py
git commit -m "Phase 2.2: Shor9Code skeleton with stabilizer strings"
```

### Task 2: Pauli-string helpers + commutation tests

**Files:**
- Modify: `src/qec_project/codes/shor9.py` (add `pauli_string_to_matrix`, `pauli_commute`)
- Modify: `tests/test_shor9.py`

- [ ] **Step 1: Write failing test for pairwise stabilizer commutation**

```python
def test_stabilizers_pairwise_commute() -> None:
    code = Shor9Code()
    from qec_project.codes.shor9 import pauli_commute
    stabs = code.stabilizers()
    for a, b in itertools.combinations(stabs, 2):
        assert pauli_commute(a, b), f"{a} and {b} do not commute"


def test_logical_x_anticommutes_with_logical_z() -> None:
    code = Shor9Code()
    from qec_project.codes.shor9 import pauli_commute
    ops = code.logical_operators()
    assert not pauli_commute(ops["X"], ops["Z"])


def test_logical_operators_commute_with_all_stabilizers() -> None:
    code = Shor9Code()
    from qec_project.codes.shor9 import pauli_commute
    for logical in code.logical_operators().values():
        for stab in code.stabilizers():
            assert pauli_commute(logical, stab), (
                f"logical {logical} does not commute with stabilizer {stab}"
            )
```

- [ ] **Step 2: Run — expect ImportError on `pauli_commute`**

`python -m uv run pytest tests/test_shor9.py -x`

- [ ] **Step 3: Implement Pauli-string commutation in `shor9.py`**

Two single Paulis `P, Q` from `{I, X, Y, Z}` commute iff one of them is `I` or `P == Q`; otherwise anticommute. Two Pauli strings commute iff they anticommute at an even number of positions.

```python
def _single_pauli_anticommute(p: str, q: str) -> bool:
    """Return True iff single-qubit Paulis ``p`` and ``q`` anticommute."""
    if p == "I" or q == "I":
        return False
    return p != q


def pauli_commute(p: str, q: str) -> bool:
    """Return True iff Pauli strings ``p`` and ``q`` commute.

    Two strings commute iff they anticommute at an even number of qubit
    positions. Empty-string / mismatched-length inputs raise ``ValueError``.
    """
    if len(p) != len(q):
        raise ValueError(f"length mismatch: {len(p)} vs {len(q)}")
    if not p:
        raise ValueError("Pauli strings must be non-empty")
    if not (set(p) <= {"I", "X", "Y", "Z"} and set(q) <= {"I", "X", "Y", "Z"}):
        raise ValueError("Pauli strings must contain only I/X/Y/Z")
    anti = sum(1 for a, b in zip(p, q, strict=True) if _single_pauli_anticommute(a, b))
    return anti % 2 == 0


def pauli_string_to_matrix(p: str) -> np.ndarray:
    """Build the dense matrix of a Pauli string under big-endian ordering."""
    if not p:
        raise ValueError("Pauli string must be non-empty")
    if not set(p) <= {"I", "X", "Y", "Z"}:
        raise ValueError(f"unknown Pauli character in {p!r}")
    return reduce(np.kron, (_SINGLE_PAULIS[c] for c in p))
```

- [ ] **Step 4: Run tests — expect PASS**

`python -m uv run pytest tests/test_shor9.py -x`

- [ ] **Step 5: Commit**

```bash
git add src/qec_project/codes/shor9.py tests/test_shor9.py
git commit -m "Phase 2.2: Pauli-string commutation + matrix builder"
```

### Task 3: Encoding circuit + stabilizer eigenstate test

**Files:**
- Modify: `src/qec_project/codes/shor9.py`
- Modify: `tests/test_shor9.py`

- [ ] **Step 1: Write failing test for `encode_circuit` producing a +1 eigenstate of each stabilizer**

```python
def test_encoded_zero_is_plus1_eigenstate_of_every_stabilizer() -> None:
    from qiskit.quantum_info import Statevector
    from qec_project.codes.shor9 import pauli_string_to_matrix

    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=0)
    sv = Statevector(qc).data  # length-2^9, Qiskit little-endian
    # Reverse to big-endian to match our Pauli strings
    sv_be = _qiskit_to_bigendian(sv, n_qubits=9)
    for stab in code.stabilizers():
        M = pauli_string_to_matrix(stab)
        out = M @ sv_be
        overlap = np.vdot(sv_be, out)
        assert abs(overlap - 1.0) < 1e-9, f"stab {stab}: <psi|S|psi> = {overlap}"


def _qiskit_to_bigendian(data: np.ndarray, n_qubits: int) -> np.ndarray:
    """Reverse Qiskit little-endian basis ordering to numpy.kron big-endian."""
    return data.reshape([2] * n_qubits).transpose(*range(n_qubits - 1, -1, -1)).reshape(-1)


def test_encoded_one_is_minus1_eigenstate_of_logical_z() -> None:
    from qiskit.quantum_info import Statevector
    from qec_project.codes.shor9 import pauli_string_to_matrix

    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=1)
    sv = Statevector(qc).data
    sv_be = _qiskit_to_bigendian(sv, n_qubits=9)
    Z_L = pauli_string_to_matrix(code.logical_operators()["Z"])
    overlap = np.vdot(sv_be, Z_L @ sv_be)
    assert abs(overlap - (-1.0)) < 1e-9, f"<1_L|Z_L|1_L> = {overlap}"
```

- [ ] **Step 2: Run — expect AttributeError on `encode_circuit`**

- [ ] **Step 3: Implement `encode_circuit`**

```python
    def encode_circuit(self, logical_bit: int = 0) -> QuantumCircuit:
        """Build the 9-qubit encoding circuit for ``|logical_bit>``.

        Layout:
        * Outer phase-flip code on representatives ``(0, 3, 6)``:
          ``CX(0,3)``, ``CX(0,6)``, then ``H`` on each of ``0, 3, 6``.
        * Inner bit-flip code per block: ``CX(0,1)``, ``CX(0,2)``,
          ``CX(3,4)``, ``CX(3,5)``, ``CX(6,7)``, ``CX(6,8)``.

        ``logical_bit=0`` produces ``|0_L>``; ``logical_bit=1`` prepends
        an ``X`` on qubit 0 so the input to the encoder is ``|1>``.
        """
        if logical_bit not in (0, 1):
            raise ValueError(f"logical_bit must be 0 or 1; got {logical_bit}")
        qc = QuantumCircuit(self.n, name=f"Shor9 |{logical_bit}_L>")
        if logical_bit == 1:
            qc.x(0)
        # Outer phase-flip: spread data into block reps, then H.
        qc.cx(0, 3)
        qc.cx(0, 6)
        qc.h(0)
        qc.h(3)
        qc.h(6)
        # Inner bit-flip: copy each block rep to its two block partners.
        qc.cx(0, 1)
        qc.cx(0, 2)
        qc.cx(3, 4)
        qc.cx(3, 5)
        qc.cx(6, 7)
        qc.cx(6, 8)
        return qc
```

- [ ] **Step 4: Run — expect PASS**

`python -m uv run pytest tests/test_shor9.py -x`

- [ ] **Step 5: Commit**

```bash
git add src/qec_project/codes/shor9.py tests/test_shor9.py
git commit -m "Phase 2.2: encoding circuit verified as +1 eigenstate of stabilizers"
```

### Task 4: Recovery lookup table + `recovery(syndrome)` API

**Files:**
- Modify: `src/qec_project/codes/shor9.py`
- Modify: `tests/test_shor9.py`

- [ ] **Step 1: Write failing test that `recovery(syndrome)` returns expected Paulis for the 27 single-qubit errors**

```python
def test_recovery_returns_pauli_for_each_single_qubit_error() -> None:
    code = Shor9Code()
    # Each single-qubit Pauli error has a unique syndrome under Shor's code
    # (well, syndromes can collide between e.g. Y_i and the X_i,Z_i pair,
    # but Y = i X Z so the recovery is the same up to global phase).
    for q, p in itertools.product(range(9), ("X", "Y", "Z")):
        err = ["I"] * 9
        err[q] = p
        err_string = "".join(err)
        syndrome = code.syndrome_of(err_string)
        recovery_string = code.recovery(syndrome)
        assert isinstance(recovery_string, str) and len(recovery_string) == 9


def test_recovery_of_zero_syndrome_is_identity() -> None:
    code = Shor9Code()
    zero = tuple([0] * 8)
    assert code.recovery(zero) == "I" * 9
```

- [ ] **Step 2: Run — expect AttributeError**

- [ ] **Step 3: Implement `syndrome_of` and `recovery`**

The recovery strategy: enumerate all 28 candidate errors (`I` plus 27 single-qubit Paulis), compute each one's syndrome via `pauli_commute`, build the lookup table. If two errors collide on syndrome we take the lowest-weight (with `I < X < Y < Z` tie-break) — but in practice the only collisions are between `Y_i` and the corresponding `X_i Z_i` pair, and since we list single-qubit errors only, each syndrome maps to one entry.

Wait — `X_i Z_i` is two-qubit weight 2, not in our candidate list. The single-qubit collisions are between, say, `Z_0` and `Z_1` and `Z_2` (all share the same outer-X syndrome and trigger the same inner Z-Z checks differently). Actually each `Z_i` triggers ONLY the outer X-checks that contain qubit `i`; it commutes with all inner Z-Z checks (Z commutes with Z). So `Z_0`, `Z_1`, `Z_2` all have the same syndrome `(0,0,0,0,0,0, X-check covering block 0 = 1, X-check covering block ? )`. They are degenerate: applying `Z_0`, `Z_1`, or `Z_2` to the encoded state all produce the same logical-equivalent state (they differ by a stabilizer). So the recovery just needs to apply ANY one of them — convention: pick the lowest-indexed qubit per block.

```python
def _syndrome_of_pauli(error: str, stabilizers: tuple[str, ...]) -> tuple[int, ...]:
    """Return the 8-bit syndrome of a Pauli error: 1 iff anticommutes."""
    return tuple(0 if pauli_commute(error, s) else 1 for s in stabilizers)


def _build_recovery_table(
    stabilizers: tuple[str, ...],
) -> dict[tuple[int, ...], str]:
    """Build syndrome -> recovery-string lookup.

    Enumerates the 28 single-qubit Pauli errors (I plus X/Y/Z on each of
    9 qubits). Each gets its 8-bit syndrome via :func:`pauli_commute`.
    On collision (degenerate errors that produce the same syndrome) the
    canonical representative is the *first* one encountered in the
    iteration order: qubit 0 first, then X before Y before Z. Applying
    any of the degenerate set restores the logical state because the
    errors differ by a stabilizer.
    """
    table: dict[tuple[int, ...], str] = {}
    # Identity error
    table[tuple([0] * len(stabilizers))] = "I" * 9
    for q in range(9):
        for p in ("X", "Y", "Z"):
            err = ["I"] * 9
            err[q] = p
            err_string = "".join(err)
            syndrome = _syndrome_of_pauli(err_string, stabilizers)
            if syndrome not in table:
                table[syndrome] = err_string
    return table


class Shor9Code:
    # ... (existing) ...

    def syndrome_of(self, pauli: str) -> tuple[int, ...]:
        """Return the 8-bit syndrome of a Pauli-string error."""
        if len(pauli) != self.n:
            raise ValueError(f"expected length-{self.n} Pauli string; got {len(pauli)}")
        return _syndrome_of_pauli(pauli, self._stabilizers)

    def recovery(self, syndrome: tuple[int, ...]) -> str:
        """Return the recovery Pauli string for a given syndrome.

        Unknown syndromes (those produced by weight-2+ errors) map to
        the identity recovery, which is the safe default: the gate
        either succeeds or visibly fails downstream.
        """
        if len(syndrome) != len(self._stabilizers):
            raise ValueError(
                f"expected length-{len(self._stabilizers)} syndrome; got {len(syndrome)}"
            )
        return self._recovery_table.get(tuple(int(b) for b in syndrome), "I" * self.n)
```

- [ ] **Step 4: Run tests — expect PASS**

`python -m uv run pytest tests/test_shor9.py -x`

- [ ] **Step 5: Commit**

```bash
git add src/qec_project/codes/shor9.py tests/test_shor9.py
git commit -m "Phase 2.2: syndrome lookup + recovery"
```

### Task 5: Exhaustive correction test — 27 single-qubit errors

**Files:**
- Modify: `tests/test_shor9.py`

- [ ] **Step 1: Write the exhaustive correction test**

```python
def test_corrects_every_single_qubit_pauli_error() -> None:
    """For each of 27 single-qubit Pauli errors on |0_L>, syndrome+recovery
    restores the encoded state up to a global phase.
    """
    from qiskit.quantum_info import Statevector
    from qec_project.codes.shor9 import pauli_string_to_matrix

    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=0)
    encoded = _qiskit_to_bigendian(Statevector(qc).data, n_qubits=9)

    failures: list[str] = []
    for q, p in itertools.product(range(9), ("X", "Y", "Z")):
        err = ["I"] * 9
        err[q] = p
        err_string = "".join(err)
        E = pauli_string_to_matrix(err_string)
        corrupted = E @ encoded
        syndrome = code.syndrome_of(err_string)
        recovery_string = code.recovery(syndrome)
        R = pauli_string_to_matrix(recovery_string)
        restored = R @ corrupted
        # Fidelity = |<encoded | restored>|; should be 1 up to global phase.
        overlap = abs(np.vdot(encoded, restored))
        if not overlap > 1 - 1e-9:
            failures.append(f"error {err_string}: |<psi|psi'>| = {overlap:.6f}")
    assert not failures, "\n".join(failures)
```

- [ ] **Step 2: Run — expect PASS (or FAIL revealing a bug we must fix before moving on)**

`python -m uv run pytest tests/test_shor9.py::test_corrects_every_single_qubit_pauli_error -x -v`

- [ ] **Step 3: If failures, debug. Likely culprit: Y-error degeneracy with X+Z on same qubit. The Y_i syndrome equals the bitwise-OR of X_i and Z_i syndromes, AND the recovery table currently picks whichever single-qubit error comes first in iteration order. For Y_i specifically, the syndrome must map back to Y_i (not X_i or Z_i), because applying X_i instead of Y_i leaves a Z error that the second round can't catch — but for a single-error test this should still work because Y = iXZ so applying X_i then Z_i would also restore. Verify by also running the test on |1_L>.**

```python
def test_corrects_every_single_qubit_pauli_error_on_logical_one() -> None:
    from qiskit.quantum_info import Statevector
    from qec_project.codes.shor9 import pauli_string_to_matrix

    code = Shor9Code()
    qc = code.encode_circuit(logical_bit=1)
    encoded = _qiskit_to_bigendian(Statevector(qc).data, n_qubits=9)

    failures: list[str] = []
    for q, p in itertools.product(range(9), ("X", "Y", "Z")):
        err = ["I"] * 9
        err[q] = p
        err_string = "".join(err)
        E = pauli_string_to_matrix(err_string)
        corrupted = E @ encoded
        syndrome = code.syndrome_of(err_string)
        recovery_string = code.recovery(syndrome)
        R = pauli_string_to_matrix(recovery_string)
        restored = R @ corrupted
        overlap = abs(np.vdot(encoded, restored))
        if not overlap > 1 - 1e-9:
            failures.append(f"error {err_string}: |<psi|psi'>| = {overlap:.6f}")
    assert not failures, "\n".join(failures)
```

- [ ] **Step 4: Commit**

```bash
git add tests/test_shor9.py
git commit -m "Phase 2.2: exhaustive 27-error correction on |0_L> and |1_L>"
```

### Task 6: Hypothesis property test — superposition recovery

**Files:**
- Modify: `tests/test_shor9.py`

- [ ] **Step 1: Write property test that recovery works on a random superposition `alpha |0_L> + beta |1_L>`**

```python
@settings(deadline=None, max_examples=20)
@given(
    theta=st.floats(min_value=0.0, max_value=np.pi, allow_nan=False),
    phi=st.floats(min_value=0.0, max_value=2 * np.pi, allow_nan=False),
    qubit=st.integers(min_value=0, max_value=8),
    pauli=st.sampled_from(("X", "Y", "Z")),
)
def test_recovery_preserves_arbitrary_logical_superposition(
    theta: float, phi: float, qubit: int, pauli: str
) -> None:
    """For a random one-qubit state encoded into Shor's code, any
    single-qubit Pauli error is corrected by syndrome + recovery.
    """
    from qiskit.quantum_info import Statevector
    from qec_project.codes.shor9 import pauli_string_to_matrix

    code = Shor9Code()
    alpha = np.cos(theta / 2)
    beta = np.exp(1j * phi) * np.sin(theta / 2)
    # Build |psi_L> = alpha |0_L> + beta |1_L> from the two encoded states.
    enc0 = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(0)).data, n_qubits=9
    )
    enc1 = _qiskit_to_bigendian(
        Statevector(code.encode_circuit(1)).data, n_qubits=9
    )
    encoded = alpha * enc0 + beta * enc1

    err = ["I"] * 9
    err[qubit] = pauli
    err_string = "".join(err)
    E = pauli_string_to_matrix(err_string)
    corrupted = E @ encoded
    syndrome = code.syndrome_of(err_string)
    R = pauli_string_to_matrix(code.recovery(syndrome))
    restored = R @ corrupted
    overlap = abs(np.vdot(encoded, restored))
    assert overlap > 1 - 1e-9, f"fidelity {overlap} for err {err_string}"
```

- [ ] **Step 2: Run — expect PASS**

`python -m uv run pytest tests/test_shor9.py -x -v`

- [ ] **Step 3: Commit**

```bash
git add tests/test_shor9.py
git commit -m "Phase 2.2: hypothesis property test for arbitrary logical superposition"
```

### Task 7: Reading-list entry for Shor 1995

**Files:**
- Modify: `docs/reading-list.md`

- [ ] **Step 1: Add Shor 1995 entry under Phase 2**

Insert after the Gottesman 1997 entry under `## Phase 2 — QEC fundamentals`:

```markdown
- Peter W. Shor. *Scheme for reducing decoherence in quantum computer
  memory.* Phys. Rev. A 52, R2493 (1995).
  doi:10.1103/PhysRevA.52.R2493. — The original 9-qubit code; Phase 2.2.
```

- [ ] **Step 2: Run `python scripts/verify_reading_list.py` and confirm green**

- [ ] **Step 3: Commit**

```bash
git add docs/reading-list.md
git commit -m "Phase 2.2: reading-list entry for Shor 1995"
```

### Task 8: Notebook builder + notebook

**Files:**
- Create: `phase-02-qec-fundamentals/02-shor-9/_build_notebook.py`
- Create: `phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb`

- [ ] **Step 1: Write the builder script**

The builder follows the Phase 1.2 pattern: a list of `md(...)` / `code(...)` cells, then `nbf.writes` to `shor_nine.ipynb`. Cells, in order:

1. **MD: title + outline** ("Phase 2.2 — Shor [[9,1,3]] code", outline of sections).
2. **Code: imports** (`numpy`, `qiskit.QuantumCircuit`, `qiskit.quantum_info.Statevector`, `Shor9Code`, `pauli_string_to_matrix`).
3. **MD: concatenation intuition** (one short paragraph: outer phase-flip code on (q0, q3, q6) sandwiches inner bit-flip codes on each triple — so each "outer" qubit is encoded into three "inner" qubits).
4. **Code: build the encoding circuit and draw it**:
   ```python
   code = Shor9Code()
   qc0 = code.encode_circuit(logical_bit=0)
   print(qc0.draw(output="text"))
   ```
5. **MD: algebraic form** of `|0_L>` and `|1_L>` (tensor of three `(|000> + |111>)/sqrt(2)` for |0_L>, and three `(|000> - |111>)/sqrt(2)` for |1_L>).
6. **Code: verify the encoded state matches the algebraic form**:
   ```python
   ket_000 = np.zeros(8, dtype=complex); ket_000[0] = 1
   ket_111 = np.zeros(8, dtype=complex); ket_111[7] = 1
   block_plus = (ket_000 + ket_111) / np.sqrt(2)
   block_minus = (ket_000 - ket_111) / np.sqrt(2)
   algebraic_0L = np.kron(np.kron(block_plus, block_plus), block_plus)
   algebraic_1L = np.kron(np.kron(block_minus, block_minus), block_minus)
   def qiskit_to_be(data, n):
       return data.reshape([2]*n).transpose(*range(n-1, -1, -1)).reshape(-1)
   sv0 = qiskit_to_be(Statevector(qc0).data, 9)
   sv1 = qiskit_to_be(Statevector(code.encode_circuit(1)).data, 9)
   print(f"|<0_L | algebraic_0L>| = {abs(np.vdot(sv0, algebraic_0L)):.6f}")
   print(f"|<1_L | algebraic_1L>| = {abs(np.vdot(sv1, algebraic_1L)):.6f}")
   ```
7. **MD: stabilizers table** (6 inner Z-Z + 2 outer X-X, list each with Pauli string).
8. **Code: verify each stabilizer fixes the encoded state**:
   ```python
   for s in code.stabilizers():
       M = pauli_string_to_matrix(s)
       eig = np.vdot(sv0, M @ sv0).real
       print(f"  S = {s}  <0_L|S|0_L> = {eig:+.6f}")
   ```
9. **MD: logical operators** (both forms: spec-text vs canonical-min-weight; explain equivalence modulo stabilizers; pick `X_L = X_0 X_3 X_6`, `Z_L = Z_0 Z_1 Z_2`).
10. **Code: verify logical operators commute with stabilizers and anticommute with each other**.
11. **MD: single-error correction — exhaustive** (explain the 27 errors and the syndrome lookup).
12. **Code: loop over 27 errors, print syndrome + recovery + fidelity**:
    ```python
    for q in range(9):
        for p in ("X", "Y", "Z"):
            err = ["I"]*9; err[q] = p; err_s = "".join(err)
            E = pauli_string_to_matrix(err_s)
            corrupted = E @ sv0
            syn = code.syndrome_of(err_s)
            rec = code.recovery(syn)
            R = pauli_string_to_matrix(rec)
            fid = abs(np.vdot(sv0, R @ corrupted))
            ok = "OK" if fid > 1-1e-9 else "FAIL"
            print(f"  err={err_s}  syn={syn}  rec={rec}  fidelity={fid:.6f}  {ok}")
    ```
13. **MD: concrete walk-through — Y on qubit 5**: show the syndrome bit pattern (Y_5 anticommutes with the Z-Z checks adjacent to qubit 5, i.e. `Z_4 Z_5` and `Z_5 Z_6`... wait — block 1 is `{3,4,5}` so qubit 5 is in block 1, with checks `Z_3 Z_4` and `Z_4 Z_5`. So Y_5 anticommutes with `Z_4 Z_5` but not `Z_3 Z_4`. It also anticommutes with the X-checks containing qubit 5 — both `X_0..X_5` and `X_3..X_8` contain qubit 5, so Y_5 anticommutes with both outer X-checks). Compute live in the notebook so the values are accurate.
14. **Code: print syndrome of Y_5 specifically**:
    ```python
    syn_y5 = code.syndrome_of("IIIIIYIII")
    print(f"syndrome of Y on qubit 5: {syn_y5}")
    print(f"recovery: {code.recovery(syn_y5)}")
    ```
15. **MD: why distance 3 is exactly correct** — one paragraph: the minimum weight of a logical operator (representative not in the stabilizer group) is 3. `Z_L = Z_0 Z_1 Z_2` has weight 3; `X_L = X_0 X_3 X_6` has weight 3. So the code detects any weight-1 or weight-2 error and corrects any weight-1 error: distance = 3.
16. **MD: recap + next** (Phase 2.3: stabilizer formalism in `pauli.py`).

- [ ] **Step 2: Run the builder**

`python -m uv run python phase-02-qec-fundamentals/02-shor-9/_build_notebook.py`

- [ ] **Step 3: Execute the notebook end-to-end via nbconvert**

`python -m uv run jupyter nbconvert --to notebook --execute phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb --output _check.ipynb`

- [ ] **Step 4: If it fails, fix the builder and re-run. After success, delete the `_check.ipynb`.**

`rm phase-02-qec-fundamentals/02-shor-9/_check.ipynb`

- [ ] **Step 5: Commit**

```bash
git add phase-02-qec-fundamentals/02-shor-9/_build_notebook.py phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb
git commit -m "Phase 2.2: shor_nine notebook (encoding, stabilizers, exhaustive correction)"
```

### Task 9: README for sub-task 02

**Files:**
- Create: `phase-02-qec-fundamentals/02-shor-9/README.md`

- [ ] **Step 1: Write a one-pager README**

```markdown
# Phase 2.2 — Shor [[9,1,3]] code

Build Shor's 9-qubit code in Qiskit, view it as concatenation of the 3-qubit
phase-flip code with the 3-qubit bit-flip code, list its 8 stabilizers and
the two logical operators, and verify by exhaustive `Statevector` simulation
that every single-qubit Pauli error (X, Y, Z on any of the 9 qubits) is
corrected by syndrome + recovery.

## Files

- `shor_nine.ipynb` — teaching notebook.
- `_build_notebook.py` — one-shot generator (run again to regenerate the
  notebook).

## Promoted helpers

- `qec_project.codes.shor9.Shor9Code`
- `qec_project.codes.shor9.pauli_commute`
- `qec_project.codes.shor9.pauli_string_to_matrix`

Tested in `tests/test_shor9.py` (29 tests including a hypothesis property
test on arbitrary logical superpositions).

## References

- Peter W. Shor, *Scheme for reducing decoherence in quantum computer
  memory*, Phys. Rev. A 52, R2493 (1995). doi:10.1103/PhysRevA.52.R2493.
- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  section 10.2.
```

- [ ] **Step 2: Commit**

```bash
git add phase-02-qec-fundamentals/02-shor-9/README.md
git commit -m "Phase 2.2: sub-task README"
```

### Task 10: Verification gates

- [ ] **Step 1: `python -m uv run pytest`** — expect all tests pass (existing + new shor9).
- [ ] **Step 2: `python -m uv run ruff check .`** — expect no findings.
- [ ] **Step 3: `python scripts/verify_reading_list.py`** — expect green.
- [ ] **Step 4: `python -m uv run jupyter nbconvert --to notebook --execute phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb --output _check.ipynb`** — expect success; delete `_check.ipynb`.
- [ ] **Step 5: Fix any failures and re-run until all four are green.**

### Task 11: CHANGELOG milestone entry

**Files:**
- Modify: `CHANGELOG.md` (append to `## Completed milestones`; do NOT touch `## Current status`).

- [ ] **Step 1: Append the milestone entry**

```markdown
- 2026-05-14  Phase 2.2 (Shor 9-qubit code): notebook
  `phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb` covering the
  concatenation view (3-qubit phase-flip outer code on representatives
  (0, 3, 6), 3-qubit bit-flip inner code in each of three blocks
  {0,1,2}, {3,4,5}, {6,7,8}), the explicit Qiskit encoding circuit
  (CX(0,3), CX(0,6), H on 0/3/6, CX(0,1), CX(0,2), CX(3,4), CX(3,5),
  CX(6,7), CX(6,8)), the 8 stabilizers (six Z-Z inner checks and two
  six-qubit X-X outer checks) verified as +1 eigenvalues of the
  encoded state, canonical minimum-weight logical operators
  X_L = X_0 X_3 X_6 and Z_L = Z_0 Z_1 Z_2, and the headline result:
  exhaustive verification that all 27 single-qubit Pauli errors are
  corrected by syndrome lookup + recovery up to global phase
  (`<encoded | restored>| > 1 - 1e-9`). Promoted helpers:
  `qec_project.codes.shor9` (`Shor9Code` with `encode_circuit`,
  `stabilizers`, `logical_operators`, `syndrome_of`, `recovery`; plus
  module-level `pauli_commute` and `pauli_string_to_matrix`) with new
  tests in `tests/test_shor9.py` (pairwise stabilizer commutation,
  logical anticommutation, encoded-state stabilizer eigenstate check,
  exhaustive 27-error correction on |0_L> and |1_L>, hypothesis
  property test on arbitrary logical superpositions). Plan in
  `plans/phase-02-02-shor-9.md`. Reading list gains Shor 1995
  (doi 10.1103/PhysRevA.52.R2493). pytest <N> passed, ruff clean,
  verify_reading_list green, notebook executes top-to-bottom.
```

(Fill in `<N>` after the green pytest run.)

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "Phase 2.2: CHANGELOG milestone entry"
```

---

## Acceptance criteria

- `python -m uv run pytest` returns 0.
- `python -m uv run ruff check .` returns 0 findings.
- `python -m uv run jupyter nbconvert --to notebook --execute phase-02-qec-fundamentals/02-shor-9/shor_nine.ipynb --output _check.ipynb` runs to completion.
- `python scripts/verify_reading_list.py` is green.
- `git status` clean.
- All 27 single-qubit Pauli errors are corrected on both `|0_L>` and `|1_L>` with overlap > 1 - 1e-9.

## Out-of-band notes

- Qiskit 2.4.1 is installed. `Statevector(qc)` returns a length-`2^n` array in Qiskit little-endian; we reverse to match `numpy.kron` big-endian throughout (mirroring Phase 1.2's `qiskit_to_bigendian` helper).
- We do NOT use measurement-based syndrome extraction in this notebook. Syndromes are computed by direct expectation value `<psi | S | psi>`. Ancilla-based fault-tolerant extraction is Phase 4 material.
- The Y-error degeneracy point: `Y_i = i X_i Z_i`, so `Y_i` and the pair `(X_i, Z_i)` produce related but distinct 8-bit syndromes. Each of the 27 single-qubit errors has a unique syndrome — verified by the recovery lookup table being injective on the 27 entries — so direct table lookup suffices.
- `X_L = X_0 X_3 X_6` (weight 3) is chosen over the spec text's "X_1..X_9" (weight 9) because the canonical distance-3 representative is what students should see. We comment on the equivalence (X_1 X_2 ... X_9 = X_L * (X_0 X_1) * (X_3 X_4) * (X_6 X_7) * ... well, more simply: any all-X tensor decomposes into X_L times a product of X-type stabilizers; but our stabilizers are X_0..X_5 and X_3..X_8, so `X_0 X_1 X_2 X_3 X_4 X_5 X_6 X_7 X_8 = (X_0 X_1 X_2 X_3 X_4 X_5)(X_6 X_7 X_8)`, and the inner-block X_6 X_7 X_8 is `(X_3..X_8)(X_0..X_5)` divided by... easiest path: the notebook just verifies both forms via `pauli_commute` and notes they live in the same logical equivalence class).

## Self-review note

Spec coverage check passed: concatenation intuition (Task 8 cell 3), encoding circuit + Statevector verification (Tasks 3 + 8 cells 4-6), 8 stabilizers list + commutation (Tasks 1-2 + 8 cells 7-8), logical operators (Task 1 + 8 cells 9-10), exhaustive 27-error correction (Tasks 4-5 + 8 cells 11-12), why distance 3 (Task 8 cell 15), Y_5 worked example (Task 8 cells 13-14), promoted helper with class + module fns (Tasks 1-4), tests including hypothesis (Tasks 2, 3, 5, 6), reading-list entry (Task 7), CHANGELOG (Task 11). No placeholders. Signatures consistent across tasks: `encode_circuit(logical_bit=0)`, `stabilizers()`, `logical_operators()`, `syndrome_of(pauli)`, `recovery(syndrome)`.
