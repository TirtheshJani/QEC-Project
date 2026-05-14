"""One-shot generator for ``linear_algebra.ipynb``.

Run once:

    python -m uv run python phase-00-foundations/01-linear-algebra/_build_notebook.py

The notebook is committed; this script exists so the source of truth for
the notebook structure is reviewable in git diff form. It is safe to
re-run: it overwrites the .ipynb file with the regenerated version.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "linear_algebra.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 0.1 — Linear algebra for QEC

This is the first content notebook in the curriculum spine. It builds the
linear-algebra muscle that every QEC paper assumes you already have:

1. Complex vectors, inner products, and norms.
2. Matrices, the conjugate transpose, and the unitarity check we will
   reuse for every quantum gate.
3. Eigendecomposition of the four Pauli matrices `I, X, Y, Z`.
4. Tensor (Kronecker) products: by hand, then numerically, then for two
   one-qubit states combining into a two-qubit state — with an explicit
   note on basis ordering.

Why these four topics and nothing else? Because Phase 0.2 is probability
and Phase 0.3 is classical error correction. Density matrices, partial
trace, and the Bloch sphere wait for Phase 1. Stabilizers wait for
Phase 2. Doing too much here is the failure mode.

**Helpers used.** Pauli constants and the `tensor`, `is_unitary`,
`eigendecompose` helpers live in `qec_project.linalg`. They are imported
below; their tests are in `tests/test_linalg.py`.

**References.** Nielsen and Chuang, *Quantum Computation and Quantum
Information*, chapter 2 (linear algebra primer). MacKay, *Information
Theory, Inference, and Learning Algorithms*, chapters 1 and 2 (free
online). Both are entries in `docs/reading-list.md`.
"""
    )
)

cells.append(
    code(
        """import numpy as np

from qec_project.linalg import (
    PAULI_I,
    PAULI_X,
    PAULI_Z,
    PAULIS,
    eigendecompose,
    is_unitary,
    tensor,
)

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)
"""
    )
)

cells.append(
    md(
        """## 1. Complex vectors, inner products, norms

A quantum state on a single qubit is a unit vector in $\\mathbb{C}^2$.
We write a column vector $|\\psi\\rangle = (\\alpha, \\beta)^T$ with
$\\alpha, \\beta \\in \\mathbb{C}$ and $|\\alpha|^2 + |\\beta|^2 = 1$.
The inner product is

$$\\langle\\phi|\\psi\\rangle = \\sum_i \\overline{\\phi_i}\\, \\psi_i,$$

i.e. the first vector is **conjugated** before the dot product. In numpy
that is `np.vdot(phi, psi)`.
"""
    )
)

cells.append(
    code(
        """ket_zero = np.array([1, 0], dtype=np.complex128)
ket_one = np.array([0, 1], dtype=np.complex128)
ket_plus = (ket_zero + ket_one) / np.sqrt(2)
ket_minus = (ket_zero - ket_one) / np.sqrt(2)

for name, v in [("|0>", ket_zero), ("|1>", ket_one), ("|+>", ket_plus), ("|->", ket_minus)]:
    print(f"{name}: vec={v}, norm={np.linalg.norm(v):.4f}")

print()
print("<+|->  =", np.vdot(ket_plus, ket_minus))
print("<+|0>  =", np.vdot(ket_plus, ket_zero))
"""
    )
)

cells.append(
    md(
        """`<+|->` is exactly zero: the X-basis states are orthogonal, just like
`|0>` and `|1>` are orthogonal in the Z basis. `<+|0> = 1/sqrt(2)` is
the overlap that controls the measurement probability when we measure
`|+>` in the Z basis (this is foreshadowing Phase 1; we will not derive
it here).
"""
    )
)

cells.append(
    md(
        """## 2. Matrices, conjugate transpose, unitarity

The conjugate transpose of a matrix $A$ is written $A^\\dagger$. A
matrix $U$ is **unitary** if $U U^\\dagger = I$, equivalently if its
columns form an orthonormal basis. Every quantum gate is unitary.

Below we verify that all four Paulis are unitary, that each Pauli is
Hermitian (equal to its conjugate transpose, so it is also a valid
*observable*), and that `X, Y, Z` each square to the identity.
"""
    )
)

cells.append(
    code(
        """for name, P in PAULIS.items():
    hermitian = np.allclose(P, P.conj().T)
    unitary = is_unitary(P)
    print(f"Pauli {name}: hermitian={hermitian}, unitary={unitary}")

print()
for name in ("X", "Y", "Z"):
    P = PAULIS[name]
    print(f"{name} @ {name} == I:", np.allclose(P @ P, PAULI_I))
"""
    )
)

cells.append(
    md(
        """The anticommutation relations $\\{X, Y\\} = \\{X, Z\\} = \\{Y, Z\\} = 0$
are the algebraic backbone of the stabilizer formalism in Phase 2.
Verify them numerically so we see the zero matrix appear:
"""
    )
)

cells.append(
    code(
        """def anticommutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b + b @ a

for left, right in [("X", "Y"), ("X", "Z"), ("Y", "Z")]:
    A = anticommutator(PAULIS[left], PAULIS[right])
    print(f"{{{left}, {right}}} =")
    print(A)
    print(f"   is zero matrix: {np.allclose(A, 0)}")
"""
    )
)

cells.append(
    md(
        """## 3. Eigendecomposition of the Paulis

For a diagonalizable matrix $A$ with eigenvalues $\\lambda_i$ and
eigenvectors $v_i$, we can write

$$A = V D V^{-1},$$

where the columns of $V$ are the $v_i$ and $D$ is diagonal with the
$\\lambda_i$. For Hermitian matrices the eigenvectors are orthogonal,
so $V^{-1} = V^\\dagger$ and the decomposition becomes

$$A = V D V^\\dagger.$$

This is exactly the spectral form used in quantum measurement: every
Hermitian observable decomposes into projectors onto its eigenspaces,
and the eigenvalues are the possible measurement outcomes. We will not
formalize that yet — but the numbers we are about to compute are the
numbers that show up in Phase 1.
"""
    )
)

cells.append(
    code(
        """for name, P in PAULIS.items():
    values, vectors = eigendecompose(P)
    reconstructed = vectors @ np.diag(values) @ vectors.conj().T
    ok = np.allclose(reconstructed, P, atol=1e-10)
    print(f"Pauli {name}: eigenvalues = {np.round(values.real, 6).tolist()}, "
          f"V D V^H == P : {ok}")
"""
    )
)

cells.append(
    md(
        """Each of `X, Y, Z` has eigenvalues `+1` and `-1`. Those `+/-1` values
are exactly the outcomes a Pauli measurement reports in the lab — and
the same `+/-1` values we will read off the syndrome bits of a
stabilizer code in Phase 2. The eigenvector columns of `V` are the
eigenstates corresponding to each outcome; e.g. for `Z` they are
`|0>` (eigenvalue `+1`) and `|1>` (eigenvalue `-1`).
"""
    )
)

cells.append(
    md(
        """## 4. Tensor (Kronecker) products — by hand

Two qubits live in $\\mathbb{C}^2 \\otimes \\mathbb{C}^2 = \\mathbb{C}^4$.
The Kronecker product gives the matrix representation. For
$2 \\times 2$ matrices

$$A = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}, \\qquad
B = \\begin{pmatrix} e & f \\\\ g & h \\end{pmatrix},$$

the definition is

$$A \\otimes B = \\begin{pmatrix} aB & bB \\\\ cB & dB \\end{pmatrix}
= \\begin{pmatrix}
a e & a f & b e & b f \\\\
a g & a h & b g & b h \\\\
c e & c f & d e & d f \\\\
c g & c h & d g & d h
\\end{pmatrix}.$$

Concrete example: let $A = X$ (off-diagonal ones) and $B = Z$
(diagonal `+1, -1`). Then $a = 0, b = 1, c = 1, d = 0$ and
$e = 1, f = 0, g = 0, h = -1$, so by hand

$$X \\otimes Z = \\begin{pmatrix}
0 \\cdot 1 & 0 \\cdot 0 & 1 \\cdot 1 & 1 \\cdot 0 \\\\
0 \\cdot 0 & 0 \\cdot (-1) & 1 \\cdot 0 & 1 \\cdot (-1) \\\\
1 \\cdot 1 & 1 \\cdot 0 & 0 \\cdot 1 & 0 \\cdot 0 \\\\
1 \\cdot 0 & 1 \\cdot (-1) & 0 \\cdot 0 & 0 \\cdot (-1)
\\end{pmatrix}
= \\begin{pmatrix}
0 & 0 & 1 & 0 \\\\
0 & 0 & 0 & -1 \\\\
1 & 0 & 0 & 0 \\\\
0 & -1 & 0 & 0
\\end{pmatrix}.$$

Verify numerically.
"""
    )
)

cells.append(
    code(
        """by_hand = np.array(
    [
        [0, 0, 1, 0],
        [0, 0, 0, -1],
        [1, 0, 0, 0],
        [0, -1, 0, 0],
    ],
    dtype=np.complex128,
)

via_numpy = np.kron(PAULI_X, PAULI_Z)
via_helper = tensor(PAULI_X, PAULI_Z)

print("X (x) Z via numpy.kron:")
print(via_numpy.real)
print()
print("X (x) Z by hand matches numpy.kron:", np.allclose(by_hand, via_numpy))
print("tensor() helper matches numpy.kron:", np.allclose(via_helper, via_numpy))
"""
    )
)

cells.append(
    md(
        """### Basis-ordering convention

`numpy.kron(A, B)` uses **Kronecker / big-endian** ordering: when we
form `tensor(|psi>, |phi>)` for two single-qubit states, the four
computational-basis entries of the result are indexed by the two-bit
string `psi-bit phi-bit`, i.e. the **first factor is the
most-significant qubit**. So `tensor(|0>, |1>)` lands at index
$2 \\cdot 0 + 1 = 1$ in the length-4 vector. The same convention is
what Qiskit's `Statevector(...).data` reports when you write tensor
products as `|psi> tensor |phi>`. (Aside: Qiskit's *circuit qubit
labelling* uses the opposite reading order in some places, which is a
common source of off-by-one confusion later in the curriculum. We pin
the convention here and stick to it.)
"""
    )
)

cells.append(
    code(
        """state = tensor(ket_zero, ket_one)
print("|0> (x) |1> =", state)
print("index of the single non-zero entry:", int(np.argmax(np.abs(state))))
print("expected index (big-endian 0 1 = 01 = 1):", 0b01)
print()

state_plus_zero = tensor(ket_plus, ket_zero)
print("|+> (x) |0> =", np.round(state_plus_zero, 4))
print("  non-zero indices:", np.flatnonzero(np.abs(state_plus_zero) > 1e-12).tolist())
print("  expected: indices 0 (= '00') and 2 (= '10'),")
print("  i.e. the first qubit is in |+>, the second in |0>.")
"""
    )
)

cells.append(
    md(
        """A quick property check: the tensor of two unitaries is unitary. This
is what lets us build multi-qubit gates by composing single-qubit gates
in parallel.
"""
    )
)

cells.append(
    code(
        """def haar_ish_unitary(rng: np.random.Generator, dim: int = 2) -> np.ndarray:
    a = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    q, r = np.linalg.qr(a)
    phases = np.diag(r) / np.abs(np.diag(r))
    return q * phases


u = haar_ish_unitary(rng)
v = haar_ish_unitary(rng)
print("is_unitary(U):", is_unitary(u))
print("is_unitary(V):", is_unitary(v))
print("is_unitary(U (x) V):", is_unitary(tensor(u, v)))
"""
    )
)

cells.append(
    md(
        """## Recap and next steps

What we now have in hand:

* The four Paulis and a unitarity check, imported from
  `qec_project.linalg` and tested in `tests/test_linalg.py`.
* A worked spectral decomposition for each Pauli, with eigenvalues
  `+/-1`. Those are the measurement outcomes we will use in Phase 1
  and the syndrome bits in Phase 2.
* A by-hand and numerical Kronecker product, with an explicit
  basis-ordering convention (Kronecker / big-endian: the first factor
  is the most-significant qubit).

**Next deliverable:** Phase 0.2 — discrete probability and the binary
symmetric channel (`phase-00-foundations/02-probability/`).
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
