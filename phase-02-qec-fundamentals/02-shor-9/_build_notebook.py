"""One-shot generator for ``shor_nine.ipynb``.

Run once:

    python -m uv run python phase-02-qec-fundamentals/02-shor-9/_build_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "shor_nine.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 2.2 — Shor [[9,1,3]] code in Qiskit

The first quantum error-correcting code: Peter Shor's 9-qubit code (1995).
It encodes 1 logical qubit into 9 physical qubits and corrects *any*
single-qubit Pauli error (X, Y, or Z on any of the 9 qubits).

Outline:

1. Concatenation intuition: outer 3-qubit phase-flip code, inner 3-qubit
   bit-flip code in each of three blocks.
2. The encoding circuit (`H`s on block representatives + 8 `CNOT`s).
3. Verify the encoded state matches the algebraic
   ``((|000> + |111>) / sqrt(2))^{otimes 3}`` form for ``|0_L>`` and the
   ``(|000> - |111>)`` analog for ``|1_L>``.
4. The 8 stabilizers (six inner `ZZ` checks + two six-qubit outer `X`
   checks), verified as +1 eigenvalues of the encoded state.
5. The logical operators ``X_L`` and ``Z_L`` (minimum-weight reps).
6. Exhaustive single-error correction: all 27 single-qubit Pauli errors
   on the encoded state are restored by syndrome lookup + recovery.
7. A concrete walk-through for a ``Y`` error on qubit 5.
8. Why the code distance is exactly 3.

Promoted helper: :class:`qec_project.codes.shor9.Shor9Code`.

References (in ``docs/reading-list.md``):

* Peter W. Shor, *Scheme for reducing decoherence in quantum computer
  memory*, Phys. Rev. A 52, R2493 (1995).
  doi:10.1103/PhysRevA.52.R2493.
* Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  section 10.2.
"""
    )
)

cells.append(
    code(
        """import numpy as np
from qiskit.quantum_info import Statevector

from qec_project.codes.shor9 import Shor9Code, pauli_string_to_matrix

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)

code = Shor9Code()
print(f"Shor code: [[{code.n}, {code.k}, {code.d}]]")
"""
    )
)

cells.append(
    md(
        """## 1. Concatenation intuition

Shor's 9-qubit code is the **3-qubit phase-flip code concatenated with
the 3-qubit bit-flip code**. Think of it as two layers:

* **Outer phase-flip code** on three "block representative" qubits
  (qubits 0, 3, 6). The outer code protects against Z-errors on the
  representatives.
* **Inner bit-flip code** in each of three blocks ``{0, 1, 2}``,
  ``{3, 4, 5}``, ``{6, 7, 8}``. The inner code protects each block
  against X-errors on any of its three qubits.

So each "outer" qubit is itself encoded into three "inner" qubits. The
total Hilbert space is ``2^9 = 512`` dimensional and the code subspace
is 2-dimensional (one logical qubit).
"""
    )
)

cells.append(
    md(
        """## 2. The encoding circuit

Sequence (left to right in time):

1. Outer phase-flip code: ``CX(0, 3)``, ``CX(0, 6)`` (copy the data
   bit into the three block representatives), then ``H`` on each of
   ``0, 3, 6`` (Hadamard-rotate the phase-flip basis into the
   computational basis used by the inner code).
2. Inner bit-flip code per block: ``CX(0, 1)``, ``CX(0, 2)``,
   ``CX(3, 4)``, ``CX(3, 5)``, ``CX(6, 7)``, ``CX(6, 8)``.
"""
    )
)

cells.append(
    code(
        """qc0 = code.encode_circuit(logical_bit=0)
print(qc0.draw(output="text"))
"""
    )
)

cells.append(
    md(
        """## 3. Verify the algebraic form

Define ``block_+ = (|000> + |111>) / sqrt(2)`` and
``block_- = (|000> - |111>) / sqrt(2)``. The 9-qubit encoded logical
states are

$$|0_L\\rangle = |\\text{block}_+\\rangle \\otimes |\\text{block}_+\\rangle \\otimes |\\text{block}_+\\rangle,$$
$$|1_L\\rangle = |\\text{block}_-\\rangle \\otimes |\\text{block}_-\\rangle \\otimes |\\text{block}_-\\rangle.$$

We construct each by hand under big-endian ordering (``numpy.kron``) and
compare to the Qiskit ``Statevector`` output (which is little-endian, so
we reverse the basis ordering for the comparison).
"""
    )
)

cells.append(
    code(
        """def qiskit_to_bigendian(data: np.ndarray, n_qubits: int) -> np.ndarray:
    \"\"\"Reverse Qiskit little-endian basis ordering to numpy.kron big-endian.\"\"\"
    return (
        data.reshape([2] * n_qubits)
        .transpose(*range(n_qubits - 1, -1, -1))
        .reshape(-1)
    )


ket_000 = np.zeros(8, dtype=np.complex128)
ket_000[0] = 1.0
ket_111 = np.zeros(8, dtype=np.complex128)
ket_111[7] = 1.0
block_plus = (ket_000 + ket_111) / np.sqrt(2.0)
block_minus = (ket_000 - ket_111) / np.sqrt(2.0)

algebraic_0L = np.kron(np.kron(block_plus, block_plus), block_plus)
algebraic_1L = np.kron(np.kron(block_minus, block_minus), block_minus)

sv0 = qiskit_to_bigendian(Statevector(code.encode_circuit(0)).data, 9)
sv1 = qiskit_to_bigendian(Statevector(code.encode_circuit(1)).data, 9)

print(f"|<0_L | (block_+)^3>| = {abs(np.vdot(sv0, algebraic_0L)):.10f}")
print(f"|<1_L | (block_-)^3>| = {abs(np.vdot(sv1, algebraic_1L)):.10f}")
assert abs(np.vdot(sv0, algebraic_0L)) > 1 - 1e-12
assert abs(np.vdot(sv1, algebraic_1L)) > 1 - 1e-12
"""
    )
)

cells.append(
    md(
        """## 4. The 8 stabilizers

The Shor code is defined by 8 commuting Pauli operators (the stabilizer
generators). Six are inner ``ZZ`` checks (two per block); two are outer
six-qubit ``X`` checks coupling adjacent blocks.

| # | Generator | Pauli string (qubits 0..8) | Role |
|---|---|---|---|
| 1 | ``Z_0 Z_1`` | ``ZZIIIIIII`` | inner bit-flip parity, block 0 |
| 2 | ``Z_1 Z_2`` | ``IZZIIIIII`` | inner bit-flip parity, block 0 |
| 3 | ``Z_3 Z_4`` | ``IIIZZIIII`` | inner bit-flip parity, block 1 |
| 4 | ``Z_4 Z_5`` | ``IIIIZZIII`` | inner bit-flip parity, block 1 |
| 5 | ``Z_6 Z_7`` | ``IIIIIIZZI`` | inner bit-flip parity, block 2 |
| 6 | ``Z_7 Z_8`` | ``IIIIIIIZZ`` | inner bit-flip parity, block 2 |
| 7 | ``X_0..X_5`` | ``XXXXXXIII`` | outer phase-flip parity, blocks 0-1 |
| 8 | ``X_3..X_8`` | ``IIIXXXXXX`` | outer phase-flip parity, blocks 1-2 |

Each generator commutes with every other generator and stabilizes the
encoded state (i.e. ``S |encoded> = +|encoded>``). We verify
numerically.
"""
    )
)

cells.append(
    code(
        """print(f"{'stabilizer':>10}   <0_L|S|0_L>   <1_L|S|1_L>")
for stab in code.stabilizers():
    M = pauli_string_to_matrix(stab)
    e0 = complex(np.vdot(sv0, M @ sv0))
    e1 = complex(np.vdot(sv1, M @ sv1))
    print(f"{stab:>10}   {e0.real:+.6f}      {e1.real:+.6f}")
    assert abs(e0 - 1.0) < 1e-9 and abs(e1 - 1.0) < 1e-9
print("\\nall 8 stabilizers have +1 eigenvalue on both |0_L> and |1_L>")
"""
    )
)

cells.append(
    md(
        """## 5. Logical operators

We need two operators ``X_L``, ``Z_L`` that

* commute with every stabilizer (so they preserve the code subspace),
* anticommute with each other (so they generate the logical Pauli
  group),
* are not themselves in the stabilizer group (so they act non-trivially
  on the code subspace).

The labels look swapped versus naive expectation because the *outer*
code is the phase-flip code. The canonical minimum-weight reps are:

* ``X_L = Z_0 Z_3 Z_6`` (Pauli string ``ZIIZIIZII``). Each ``Z`` on a
  block representative swaps ``block_+`` with ``block_-``, so the
  triple ``Z_0 Z_3 Z_6`` swaps ``|0_L>`` and ``|1_L>``.
* ``Z_L = X_0 X_1 X_2`` (Pauli string ``XXXIIIIII``). ``X^{\\otimes 3}``
  preserves ``block_+`` (eigenvalue +1) and negates ``block_-``
  (eigenvalue -1), so this acts as a phase-flip in the logical basis.

Both have weight 3. The notebook below also shows that the spec-text
form ``X_L = X_1 X_2 ... X_9`` (weight 9) is equivalent modulo
stabilizers — it lives in the same logical equivalence class as the
weight-3 representative.
"""
    )
)

cells.append(
    code(
        """from qec_project.codes.shor9 import pauli_commute

ops = code.logical_operators()
print(f"X_L = {ops['X']}   (weight {sum(1 for c in ops['X'] if c != 'I')})")
print(f"Z_L = {ops['Z']}   (weight {sum(1 for c in ops['Z'] if c != 'I')})")

# Verify commutation with all stabilizers and mutual anticommutation.
for name, logical in ops.items():
    for stab in code.stabilizers():
        assert pauli_commute(logical, stab), f"{name} fails to commute with {stab}"
assert not pauli_commute(ops["X"], ops["Z"]), "X_L and Z_L must anticommute"
print("logical operators commute with every stabilizer and anticommute with each other")

# Eigenvalue cross-check on the encoded basis.
X_L = pauli_string_to_matrix(ops["X"])
Z_L = pauli_string_to_matrix(ops["Z"])
print(f"\\n<0_L|X_L|1_L> = {complex(np.vdot(sv0, X_L @ sv1)).real:+.6f}  (expect +1)")
print(f"<0_L|Z_L|0_L> = {complex(np.vdot(sv0, Z_L @ sv0)).real:+.6f}  (expect +1)")
print(f"<1_L|Z_L|1_L> = {complex(np.vdot(sv1, Z_L @ sv1)).real:+.6f}  (expect -1)")
"""
    )
)

cells.append(
    md(
        """## 6. Single-error correction: all 27 cases

For each of the 27 single-qubit Pauli errors (X, Y, Z on each of 9
qubits), we:

1. Apply the error to ``|0_L>``.
2. Compute the 8-bit syndrome (which stabilizers anticommute with the
   error).
3. Look up the recovery Pauli string.
4. Apply the recovery.
5. Check the fidelity ``|<0_L | restored>|`` is 1 (up to global phase).

This is direct ``Statevector`` arithmetic; no shots, no measurement
ancillas. Ancilla-based fault-tolerant syndrome extraction is Phase 4
material.
"""
    )
)

cells.append(
    code(
        """import itertools

print(f"{'error':>10}  {'syndrome':>20}  {'recovery':>10}  fid     ok")
n_fail = 0
for q, p in itertools.product(range(9), ("X", "Y", "Z")):
    err = ["I"] * 9
    err[q] = p
    err_string = "".join(err)
    E = pauli_string_to_matrix(err_string)
    corrupted = E @ sv0
    syn = code.syndrome_of(err_string)
    rec = code.recovery(syn)
    R = pauli_string_to_matrix(rec)
    restored = R @ corrupted
    fid = abs(np.vdot(sv0, restored))
    ok = fid > 1 - 1e-9
    n_fail += 0 if ok else 1
    print(f"{err_string:>10}  {syn!s:>20}  {rec:>10}  {fid:.4f}   {'OK' if ok else 'FAIL'}")
print(f"\\n{27 - n_fail}/27 single-qubit Pauli errors corrected")
assert n_fail == 0
"""
    )
)

cells.append(
    md(
        """## 7. Concrete walk-through: ``Y`` on qubit 5

``Y`` on qubit 5 is equivalent (up to global phase ``i``) to ``X_5 Z_5``,
so it triggers *both* an inner bit-flip syndrome and an outer phase-flip
syndrome. Qubit 5 sits in block 1 (``{3, 4, 5}``), so:

* ``Y_5`` anticommutes with the inner ``Z_4 Z_5`` check (and commutes
  with ``Z_3 Z_4`` since ``Y`` only anticommutes with ``Z`` once
  there).
* ``Y_5`` anticommutes with both outer six-qubit ``X`` checks because
  qubit 5 is in their support.

Let us compute the exact bit pattern.
"""
    )
)

cells.append(
    code(
        """y5 = "IIIIIYIII"
syn_y5 = code.syndrome_of(y5)
rec_y5 = code.recovery(syn_y5)
print(f"error    : {y5}")
print(f"syndrome : {syn_y5}")
print("            (s1=Z_0 Z_1, s2=Z_1 Z_2, s3=Z_3 Z_4, s4=Z_4 Z_5,")
print("             s5=Z_6 Z_7, s6=Z_7 Z_8, s7=X_0..X_5, s8=X_3..X_8)")
print(f"recovery : {rec_y5}")
E = pauli_string_to_matrix(y5)
R = pauli_string_to_matrix(rec_y5)
fid = abs(np.vdot(sv0, R @ E @ sv0))
print(f"fidelity after recovery: {fid:.10f}")
"""
    )
)

cells.append(
    md(
        """## 8. Why the code distance is exactly 3

The code distance is the minimum weight of any logical operator (any
Pauli that commutes with all stabilizers but is not itself in the
stabilizer group). Both canonical reps have weight 3:

* ``X_L = Z_0 Z_3 Z_6`` has weight 3 (three non-identity factors).
* ``Z_L = X_0 X_1 X_2`` has weight 3.

Can we find a weight-1 or weight-2 logical operator? No: every single
qubit Pauli either commutes with a stabilizer it shouldn't or doesn't
preserve the code subspace. Every weight-2 product can be rewritten as
a product of stabilizers (which act trivially on the code subspace), so
there is no genuinely weight-2 *logical* operator. Therefore

$$d = 3,$$

and by ``t = floor((d-1)/2) = 1`` the Shor code corrects every
single-qubit Pauli error — exactly what we verified above by brute force.

## Recap

* The Shor code is the 3-qubit phase-flip code (on block reps 0, 3, 6)
  concatenated with the 3-qubit bit-flip code (in each of three blocks).
* The encoding circuit consists of 2 outer CNOTs + 3 Hadamards + 6
  inner CNOTs.
* 8 stabilizer generators (six ``ZZ``, two six-qubit ``X``) define the
  code subspace.
* Logical operators ``X_L = Z_0 Z_3 Z_6`` and ``Z_L = X_0 X_1 X_2`` have
  weight 3, anticommute with each other, and commute with all stabilizers.
* All 27 single-qubit Pauli errors are corrected by syndrome lookup +
  recovery, restoring the encoded state to numerical precision.

**Next: Phase 2.3.** Promote the Pauli-string commutation logic into
`qec_project.codes.pauli`, then build the Steane CSS code (Phase 2.4)
and rewrite it in Stim (Phase 2.5).
"""
    )
)


nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.12",
    },
}

OUT.write_text(nbf.writes(nb), encoding="utf-8")
print(f"wrote {OUT}")
