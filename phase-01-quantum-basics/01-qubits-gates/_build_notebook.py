"""One-shot generator for ``qubits_gates.ipynb``.

Run once:

    python -m uv run python phase-01-quantum-basics/01-qubits-gates/_build_notebook.py

The notebook is committed; this script exists so the source of truth
for the notebook structure is reviewable in git diff form. It is safe
to re-run: it overwrites the .ipynb file.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "qubits_gates.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 1.1 — Qubits, single-qubit gates, Bloch sphere

First content notebook of Phase 1. Goal: become comfortable enough with
single-qubit states and gates that the rest of Phase 1 (entanglement,
density matrices) and Phase 2 (stabilizer formalism) feel like
notation rather than concepts.

Outline:

1. The single-qubit state space: column vectors in `C^2`.
2. Global vs relative phase: which one is physical, which one is not.
3. The Bloch sphere: the six cardinal states, plotted.
4. The single-qubit Clifford gates `H, S, X, Y, Z`. Unitarity check
   via `qec_project.linalg.is_unitary`.
5. `H Z H = X` by hand and numerically.
6. How `H, S, X` move the cardinal states around the Bloch sphere.

We reuse `qec_project.linalg` (`PAULI_I/X/Y/Z`, `PAULIS`, `is_unitary`,
`eigendecompose`) from Phase 0.1.

References (in `docs/reading-list.md`):
- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  chapter 1 (qubits, Bloch sphere) and chapter 4.1 (single-qubit gates).
"""
    )
)

cells.append(
    code(
        """import matplotlib.pyplot as plt
import numpy as np

from qec_project.linalg import PAULI_X, PAULI_Y, PAULI_Z, PAULIS, is_unitary

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)
"""
    )
)

cells.append(
    md(
        """## 1. The single-qubit state space

A qubit is a unit vector in `C^2`. In the computational basis,

$$|0\\rangle = \\begin{pmatrix} 1 \\\\ 0 \\end{pmatrix}, \\qquad
|1\\rangle = \\begin{pmatrix} 0 \\\\ 1 \\end{pmatrix}.$$

A general single-qubit state is `|psi> = alpha |0> + beta |1>` with
`|alpha|^2 + |beta|^2 = 1`. The four standard non-computational states
are the eigenvectors of `X` and `Y`:

$$|+\\rangle = \\tfrac{1}{\\sqrt{2}} (|0\\rangle + |1\\rangle), \\qquad
|-\\rangle = \\tfrac{1}{\\sqrt{2}} (|0\\rangle - |1\\rangle),$$
$$|+i\\rangle = \\tfrac{1}{\\sqrt{2}} (|0\\rangle + i |1\\rangle), \\qquad
|-i\\rangle = \\tfrac{1}{\\sqrt{2}} (|0\\rangle - i |1\\rangle).$$

`{|+>, |->}` is the eigenbasis of `X`; `{|+i>, |-i>}` is the eigenbasis
of `Y`. We will reuse this when we read off measurement outcomes.
"""
    )
)

cells.append(
    code(
        """ket_0 = np.array([[1.0], [0.0]], dtype=np.complex128)
ket_1 = np.array([[0.0], [1.0]], dtype=np.complex128)
ket_plus = (ket_0 + ket_1) / np.sqrt(2.0)
ket_minus = (ket_0 - ket_1) / np.sqrt(2.0)
ket_plus_i = (ket_0 + 1j * ket_1) / np.sqrt(2.0)
ket_minus_i = (ket_0 - 1j * ket_1) / np.sqrt(2.0)

cardinal = {
    "|0>": ket_0,
    "|1>": ket_1,
    "|+>": ket_plus,
    "|->": ket_minus,
    "|+i>": ket_plus_i,
    "|-i>": ket_minus_i,
}

for name, psi in cardinal.items():
    norm = float(np.sqrt((psi.conj().T @ psi).real.item()))
    print(f"{name:>5}  norm = {norm:.6f}")
"""
    )
)

cells.append(
    md(
        """All six cardinal states have norm 1, as required for a physical state.

## 2. Global vs relative phase

A **global phase** `e^{i theta}` multiplying the entire state is
*unphysical*: it does not change `|psi><psi|` and therefore cannot
change any measurement statistic. A **relative phase**, on the other
hand, changes the state's representation on the Bloch sphere and is
fully physical.

Concrete experiment: compare the X-basis measurement probabilities of

* `|psi_0> = (|0> + |1>) / sqrt(2) = |+>`
* `|psi_1> = (|0> + i |1>) / sqrt(2) = |+i>`
* `|psi_2> = (|0> - |1>) / sqrt(2) = |->`

These three states are *all* `(|0> + e^{i phi} |1>) / sqrt(2)` with
`phi in {0, pi/2, pi}`. They have *identical* Z-basis probabilities
(50/50) but very different X-basis probabilities (100% +,
50/50, 100% -).

Now compare to `e^{i theta} |psi_0>` for some non-zero `theta`. Its
projectors `|psi><psi|` are identical to the un-rotated version, so
every measurement probability matches `|psi_0>` exactly.
"""
    )
)

cells.append(
    code(
        """def prob_in_basis(psi: np.ndarray, basis: tuple[np.ndarray, np.ndarray]) -> tuple[float, float]:
    \"\"\"Return Born-rule probabilities for the two outcomes of a 2-state basis.\"\"\"
    p_plus = abs(complex((basis[0].conj().T @ psi).item())) ** 2
    p_minus = abs(complex((basis[1].conj().T @ psi).item())) ** 2
    return float(p_plus), float(p_minus)


z_basis = (ket_0, ket_1)
x_basis = (ket_plus, ket_minus)
y_basis = (ket_plus_i, ket_minus_i)

relative_phase_states = {
    "phi=0    (|+>)": ket_plus,
    "phi=pi/2 (|+i>)": ket_plus_i,
    "phi=pi   (|->)": ket_minus,
}
print("relative phase: Z- and X-basis outcome probabilities")
print(f"{'state':>16}  {'P(|0>)':>8} {'P(|1>)':>8}  {'P(|+>)':>8} {'P(|->)':>8}")
for name, psi in relative_phase_states.items():
    pz0, pz1 = prob_in_basis(psi, z_basis)
    px0, px1 = prob_in_basis(psi, x_basis)
    print(f"{name:>16}  {pz0:>8.4f} {pz1:>8.4f}  {px0:>8.4f} {px1:>8.4f}")

print()
print("global phase: rotate |+> by e^{i pi/3} and verify all probabilities match")
theta = np.pi / 3.0
psi_glob = np.exp(1j * theta) * ket_plus
for basis_name, basis in (("Z", z_basis), ("X", x_basis), ("Y", y_basis)):
    p_a, p_b = prob_in_basis(ket_plus, basis)
    q_a, q_b = prob_in_basis(psi_glob, basis)
    print(f"  basis {basis_name}: ({p_a:.4f}, {p_b:.4f}) vs ({q_a:.4f}, {q_b:.4f})"
          f"  match = {np.allclose([p_a, p_b], [q_a, q_b])}")
"""
    )
)

cells.append(
    md(
        """The two takeaways:

* Z-basis probabilities are 50/50 for all three relative-phase states,
  but X-basis probabilities are wildly different (`P(|+>) = 1, 0.5, 0`
  across the three). Relative phase is **physical**.
* Multiplying `|+>` by `e^{i pi/3}` leaves every Born-rule probability
  invariant in every basis. Global phase is **unphysical** and never
  appears in a measurement record.

This is why the Bloch sphere is a *sphere* and not a higher-dimensional
object: the unphysical global phase has been quotiented out.

## 3. The Bloch sphere

Up to a global phase, every single-qubit state can be written

$$|\\psi(\\theta, \\phi)\\rangle = \\cos(\\theta/2) |0\\rangle
+ e^{i\\phi} \\sin(\\theta/2) |1\\rangle,$$

with `theta in [0, pi]` and `phi in [0, 2 pi)`. The point
`(sin theta cos phi, sin theta sin phi, cos theta)` is the **Bloch
vector** `(<X>, <Y>, <Z>)` for `|psi>`. The six cardinal states sit at
the +/- axes.

The Bloch vector of any density matrix `rho` is
`r = (Tr(X rho), Tr(Y rho), Tr(Z rho))`. For a pure state the length is
1; for a mixed state it is < 1 and `rho = I/2` sits at the origin.
"""
    )
)

cells.append(
    code(
        """def bloch_vector(psi: np.ndarray) -> tuple[float, float, float]:
    \"\"\"Bloch vector (<X>, <Y>, <Z>) for a pure-state column vector.\"\"\"
    rho = psi @ psi.conj().T
    rx = float(np.trace(PAULI_X @ rho).real)
    ry = float(np.trace(PAULI_Y @ rho).real)
    rz = float(np.trace(PAULI_Z @ rho).real)
    return rx, ry, rz


print(f"{'state':>5}  {'<X>':>8} {'<Y>':>8} {'<Z>':>8}")
bloch_points: dict[str, tuple[float, float, float]] = {}
for name, psi in cardinal.items():
    rx, ry, rz = bloch_vector(psi)
    bloch_points[name] = (rx, ry, rz)
    print(f"{name:>5}  {rx:>8.4f} {ry:>8.4f} {rz:>8.4f}")
"""
    )
)

cells.append(
    code(
        """fig = plt.figure(figsize=(6.0, 6.0))
ax = fig.add_subplot(111, projection="3d")

# Wireframe sphere.
u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 15)
sx = np.outer(np.cos(u), np.sin(v))
sy = np.outer(np.sin(u), np.sin(v))
sz = np.outer(np.ones_like(u), np.cos(v))
ax.plot_wireframe(sx, sy, sz, color="lightgray", linewidth=0.4, alpha=0.7)

# Coordinate axes.
ax.plot([-1.1, 1.1], [0, 0], [0, 0], color="black", linewidth=0.5)
ax.plot([0, 0], [-1.1, 1.1], [0, 0], color="black", linewidth=0.5)
ax.plot([0, 0], [0, 0], [-1.1, 1.1], color="black", linewidth=0.5)

# Cardinal states.
colors = {"|0>": "tab:blue", "|1>": "tab:blue",
          "|+>": "tab:orange", "|->": "tab:orange",
          "|+i>": "tab:green", "|-i>": "tab:green"}
for name, (rx, ry, rz) in bloch_points.items():
    ax.scatter([rx], [ry], [rz], color=colors[name], s=60, zorder=5)
    ax.text(rx * 1.18, ry * 1.18, rz * 1.18, name, fontsize=10, ha="center")

ax.set_xlabel("<X>")
ax.set_ylabel("<Y>")
ax.set_zlabel("<Z>")
ax.set_title("Bloch sphere: six cardinal single-qubit states")
ax.set_box_aspect((1, 1, 1))
plt.tight_layout()
plt.show()
"""
    )
)

cells.append(
    md(
        """`|0>` and `|1>` sit at the north and south poles (`<Z> = +/- 1`);
`|+>` and `|->` on the +x and -x axes; `|+i>` and `|-i>` on the +y and
-y axes. Antipodal points are orthogonal *as quantum states*
(`<0|1> = <+|-> = <+i|-i> = 0`) but separated by 180 degrees on the
sphere because the sphere is the projective space of `C^2`.

## 4. Single-qubit Clifford gates

Every unitary `U` on a qubit is in the (single-qubit) **Clifford
group** iff it sends every Pauli to a Pauli (up to a sign). The
generators we need today are the Hadamard `H` and the phase gate `S`,
plus the three Paulis `X, Y, Z` (already imported from
`qec_project.linalg`):

$$H = \\frac{1}{\\sqrt{2}}\\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix},
\\qquad
S = \\begin{pmatrix} 1 & 0 \\\\ 0 & i \\end{pmatrix}.$$

`is_unitary` from `qec_project.linalg` confirms each one.
"""
    )
)

cells.append(
    code(
        """H = (1.0 / np.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=np.complex128)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)

single_qubit_gates = {"H": H, "S": S, "X": PAULIS["X"], "Y": PAULIS["Y"], "Z": PAULIS["Z"]}
for name, U in single_qubit_gates.items():
    print(f"{name}: unitary = {is_unitary(U)}")
"""
    )
)

cells.append(
    md(
        """## 5. `H Z H = X` — by hand and numerically

**Algebra.** Write `H` and `Z`:

$$H = \\tfrac{1}{\\sqrt{2}} \\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix}, \\qquad
Z = \\begin{pmatrix} 1 & 0 \\\\ 0 & -1 \\end{pmatrix}.$$

Then

$$Z H = \\tfrac{1}{\\sqrt{2}} \\begin{pmatrix} 1 & 0 \\\\ 0 & -1 \\end{pmatrix}
\\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix} =
\\tfrac{1}{\\sqrt{2}} \\begin{pmatrix} 1 & 1 \\\\ -1 & 1 \\end{pmatrix},$$

$$H Z H = \\tfrac{1}{2} \\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix}
\\begin{pmatrix} 1 & 1 \\\\ -1 & 1 \\end{pmatrix} =
\\tfrac{1}{2} \\begin{pmatrix} 0 & 2 \\\\ 2 & 0 \\end{pmatrix} =
\\begin{pmatrix} 0 & 1 \\\\ 1 & 0 \\end{pmatrix} = X.$$

This identity is the reason `H` is the universal Z-to-X basis change:
measuring `Z` after applying `H` is the same as measuring `X` directly.
We will rely on this when we cross-check Bell state circuits against
hand-computed state vectors in Phase 1.2 (Hadamard followed by
Z-basis measurement implements an X-basis measurement).

Numerical check:
"""
    )
)

cells.append(
    code(
        """HZH = H @ PAULIS["Z"] @ H
print("H Z H =")
print(HZH)
print("X =")
print(PAULIS["X"])
assert np.allclose(HZH, PAULIS["X"], atol=1e-12), "H Z H != X"
print("\\nnumerical check: H Z H == X (to 1e-12)")
"""
    )
)

cells.append(
    md(
        """## 6. Gates on the Bloch sphere

`H, S, X` permute the six cardinal states. The map below verifies the
standard table:

* `H` swaps the Z and X axes: `|0> -> |+>`, `|+> -> |0>`, `|1> -> |->`,
  `|-> -> |1>`. It leaves `|+i> -> |-i>` (sign on the y-axis).
* `S` rotates the X-Y equator by 90 degrees: `|+> -> |+i>`,
  `|+i> -> |->`, `|-> -> |-i>`, `|-i> -> |+>`. Leaves Z fixed.
* `X` swaps |0> and |1>; `Z` flips the sign of |1>; `Y` does both.

These are deterministic permutations of the cardinal points because
the single-qubit Cliffords are exactly the rotations of the Bloch
sphere by multiples of 90 degrees around the X, Y, Z axes.
"""
    )
)

cells.append(
    code(
        """def closest_cardinal(psi: np.ndarray, tol: float = 1e-6) -> str:
    \"\"\"Return the cardinal label whose Bloch vector matches psi (up to global phase).\"\"\"
    target = bloch_vector(psi)
    for name, point in bloch_points.items():
        if all(abs(target[i] - point[i]) < tol for i in range(3)):
            return name
    return "???"


actions = {"H": H, "S": S, "X": PAULIS["X"], "Y": PAULIS["Y"], "Z": PAULIS["Z"]}
print(f"{'state':>5} | " + " | ".join(f"{g:>4}" for g in actions))
print("-" * (8 + 7 * len(actions)))
for name, psi in cardinal.items():
    row = [name]
    for U in actions.values():
        out = U @ psi
        row.append(closest_cardinal(out))
    print(f"{row[0]:>5} | " + " | ".join(f"{x:>4}" for x in row[1:]))
"""
    )
)

cells.append(
    md(
        """## Recap

* A single qubit is a unit vector in `C^2`. Six cardinal states sit at
  the +/- axes of the Bloch sphere.
* Global phase is unphysical (every Born-rule probability is
  invariant); relative phase is physical and changes X/Y measurement
  outcomes.
* The single-qubit Cliffords `H, S, X, Y, Z` are unitaries that permute
  the cardinal points. We verified `H Z H = X` by hand and to 1e-12
  numerically.

**Next: Phase 1.2.** Two qubits, tensor products, Bell states,
superdense coding, teleportation. The basis-ordering note from Phase
0.1 (`numpy.kron` is big-endian) comes back, and Qiskit enters the
curriculum.
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
