"""One-shot generator for ``density_kraus.ipynb``.

Run once:

    python -m uv run python phase-01-quantum-basics/03-density-matrices-noise/_build_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "density_kraus.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 1.3 — Density matrices, partial trace, single-qubit Kraus channels

Third Phase 1 notebook. Goal: master the density-operator formalism well
enough to write down any noise channel as a Kraus set, verify it is
trace-preserving, and apply it numerically. This is the last piece of
quantum vocabulary needed before Phase 2's stabilizer formalism.

Outline:

1. Density matrix `rho`: pure / mixed, Hermitian, trace 1, PSD.
2. Partial trace: for a Bell state, tracing out one qubit gives `I/2`
   on the other.
3. The three canonical single-qubit channels in Kraus form:
   bit-flip, phase-flip, depolarizing. Trace-preservation check on each.
   Action on `|0><0|` and `|+><+|` matches the analytic forms.

Promotes two small modules:

* `qec_project.noise.quantum`: Kraus constructors and channel functions.
  Reused in Phase 2 (stabilizer-formalism error models) and Phase 3+
  (circuit-level noise).
* `qec_project.analysis.density`: `is_density_matrix` and
  `partial_trace`. Reused throughout Phase 2-4 (reduced densities on
  logical qubits).

Tests live in `tests/test_quantum_noise.py` and `tests/test_density.py`.

References (in `docs/reading-list.md`):
- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  sections 2.4 (density operator), Box 2.6 (partial trace), and 8.3
  (operator-sum representation; Eq. 8.102 is the depolarizing form we
  use).
"""
    )
)

cells.append(
    code(
        """import numpy as np

from qec_project.analysis.density import is_density_matrix, partial_trace
from qec_project.linalg import tensor
from qec_project.noise.quantum import (
    bit_flip_channel,
    bit_flip_kraus,
    depolarizing_channel,
    depolarizing_kraus,
    is_trace_preserving,
    phase_flip_channel,
    phase_flip_kraus,
)

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)
"""
    )
)

cells.append(
    md(
        """## 1. Density matrices

The pure-state formalism `|psi>` is not closed under partial trace: a
subsystem of an entangled pair is not in a pure state, so we need a
representation that handles mixtures. The **density operator** does this.

For a pure state `|psi>`,

$$\\rho = |\\psi\\rangle\\langle\\psi|.$$

For a statistical mixture `{p_i, |psi_i>}` of pure states with
probabilities `p_i`,

$$\\rho = \\sum_i p_i\\, |\\psi_i\\rangle\\langle\\psi_i|.$$

Any density matrix satisfies:

1. **Hermitian.** `rho^dagger = rho`.
2. **Trace 1.** `Tr rho = 1` (probabilities sum to 1).
3. **Positive semi-definite.** `<phi | rho | phi> >= 0` for every
   `|phi>`.

Mixed states are exactly the ones with `Tr(rho^2) < 1`; pure states
have `Tr(rho^2) = 1`. Verify on `|+><+|` (pure) and the maximally
mixed state `I/2`.
"""
    )
)

cells.append(
    code(
        """ket_0 = np.array([[1.0], [0.0]], dtype=np.complex128)
ket_1 = np.array([[0.0], [1.0]], dtype=np.complex128)
ket_plus = (ket_0 + ket_1) / np.sqrt(2.0)
ket_minus = (ket_0 - ket_1) / np.sqrt(2.0)

rho_plus = ket_plus @ ket_plus.conj().T
rho_mixed = 0.5 * np.eye(2, dtype=np.complex128)

print("|+><+|:")
print(rho_plus)
print(f"  Hermitian: {np.allclose(rho_plus, rho_plus.conj().T)}")
print(f"  trace    : {np.trace(rho_plus).real:.6f}")
print(f"  purity Tr(rho^2): {np.trace(rho_plus @ rho_plus).real:.6f}")
print(f"  is_density_matrix: {is_density_matrix(rho_plus)}")

print()
print("I/2 (maximally mixed):")
print(rho_mixed)
print(f"  Hermitian: {np.allclose(rho_mixed, rho_mixed.conj().T)}")
print(f"  trace    : {np.trace(rho_mixed).real:.6f}")
print(f"  purity Tr(rho^2): {np.trace(rho_mixed @ rho_mixed).real:.6f}")
print(f"  is_density_matrix: {is_density_matrix(rho_mixed)}")
"""
    )
)

cells.append(
    md(
        """`|+><+|` is pure (`Tr(rho^2) = 1`); `I/2` is maximally mixed
(`Tr(rho^2) = 0.5`, the lowest possible value for a single qubit, and
in general `1/d` for a `d`-dimensional system).

`is_density_matrix` (from `qec_project.analysis.density`) bundles the
three checks. It is paranoid in a useful way: a noise channel that
returns a not-quite-PSD matrix from floating-point error gets flagged
immediately. Tests in `tests/test_density.py` cover the rejection
cases (non-Hermitian, wrong trace, negative eigenvalue, non-square).

## 2. Partial trace

The partial trace `Tr_B` over subsystem `B` of a bipartite density
`rho_{AB}` produces the **reduced** density on `A`:

$$\\rho_A = \\mathrm{Tr}_B(\\rho_{AB}).$$

For the Bell state `|Phi+> = (|00> + |11>) / sqrt(2)`,

$$\\rho_{AB} = \\tfrac{1}{2}(|00\\rangle\\langle 00| +
|00\\rangle\\langle 11| + |11\\rangle\\langle 00| +
|11\\rangle\\langle 11|),$$

and tracing out either qubit yields `I / 2`: the maximally entangled
pair has *maximally mixed* marginals. This is the canonical example
of how entanglement looks from a single subsystem's perspective.
"""
    )
)

cells.append(
    code(
        """phi_plus = (tensor(ket_0, ket_0) + tensor(ket_1, ket_1)) / np.sqrt(2.0)
rho_phi_plus = phi_plus @ phi_plus.conj().T

print("rho_{AB} for |Phi+>:")
print(rho_phi_plus)

rho_A = partial_trace(rho_phi_plus, keep=0, dims=(2, 2))
rho_B = partial_trace(rho_phi_plus, keep=1, dims=(2, 2))
print("\\nTr_B(rho_{AB}):")
print(rho_A)
print("\\nTr_A(rho_{AB}):")
print(rho_B)
print(f"\\nrho_A == I/2 : {np.allclose(rho_A, rho_mixed)}")
print(f"rho_B == I/2 : {np.allclose(rho_B, rho_mixed)}")
"""
    )
)

cells.append(
    md(
        """Both marginals come out exactly equal to `I/2`. The
`qec_project.analysis.density.partial_trace` helper uses the Kronecker
/ big-endian ordering pinned in Phase 0.1, so `dims=(2, 2)` and
`keep=0` means "qubit 0 is the most-significant factor; keep it".

For a product state `|0> \\otimes |+>`, the partial traces just return
the local factors:
"""
    )
)

cells.append(
    code(
        """product = tensor(ket_0, ket_plus)
rho_product = product @ product.conj().T
rho_A_prod = partial_trace(rho_product, keep=0, dims=(2, 2))
rho_B_prod = partial_trace(rho_product, keep=1, dims=(2, 2))
print("Tr_B on |0> tensor |+>:")
print(rho_A_prod)
print("Tr_A on |0> tensor |+>:")
print(rho_B_prod)
"""
    )
)

cells.append(
    md(
        """As expected: tracing out the `|+>` factor leaves `|0><0|`, and
vice-versa. Partial trace on a product state factorises trivially; it
is on entangled states (the Bell example above) that it does real work.

## 3. Quantum channels in Kraus form

A **quantum channel** `E` is a completely positive trace-preserving
(CPTP) map on density matrices. Every CPTP map can be written in
**operator-sum** (Kraus) form

$$E(\\rho) = \\sum_k K_k\\, \\rho\\, K_k^\\dagger, \\qquad
\\sum_k K_k^\\dagger K_k = I.$$

The Kraus completeness relation is exactly what makes `E`
trace-preserving (and hence physical).

We define three textbook single-qubit channels (Nielsen-Chuang
sections 8.3.1-8.3.3):

### Bit-flip
With probability `p` the qubit is flipped (apply `X`):

$$E(\\rho) = (1 - p)\\, \\rho + p\\, X \\rho X.$$
$$K_0 = \\sqrt{1-p}\\, I, \\quad K_1 = \\sqrt{p}\\, X.$$

### Phase-flip
With probability `p` apply `Z`:

$$E(\\rho) = (1 - p)\\, \\rho + p\\, Z \\rho Z.$$
$$K_0 = \\sqrt{1-p}\\, I, \\quad K_1 = \\sqrt{p}\\, Z.$$

### Depolarizing (Nielsen-Chuang Eq. 8.102 convention)
With probability `p` the qubit is replaced by the maximally mixed
state `I/2`; equivalently each of `X, Y, Z` is applied independently
with probability `p / 4`:

$$E(\\rho) = (1 - p)\\, \\rho + p\\, \\tfrac{I}{2}.$$
$$K_0 = \\sqrt{1 - 3p/4}\\, I, \\quad
K_1 = \\sqrt{p/4}\\, X, \\quad K_2 = \\sqrt{p/4}\\, Y,
\\quad K_3 = \\sqrt{p/4}\\, Z.$$

(Some textbooks use a different parametrisation,
`rho -> (1 - p) rho + (p/3)(X rho X + Y rho Y + Z rho Z)`, where each
Pauli has weight `p/3`. We use the Nielsen-Chuang form because every
QEC threshold paper relevant to the capstone uses it.)

The three constructors `bit_flip_kraus`, `phase_flip_kraus`,
`depolarizing_kraus` and a generic `apply_channel` live in
`qec_project.noise.quantum`. `is_trace_preserving` checks the Kraus
completeness relation. Tests live in `tests/test_quantum_noise.py`.
"""
    )
)

cells.append(
    code(
        """# Trace-preservation check for each channel at a sweep of p values.
print("trace preservation: sum_k K_k^dagger K_k == I ?")
print(f"{'p':>6}  {'bit-flip':>10}  {'phase-flip':>11}  {'depolarizing':>13}")
for p in (0.0, 0.05, 0.25, 0.5, 0.9, 1.0):
    ok_bf = is_trace_preserving(bit_flip_kraus(p))
    ok_pf = is_trace_preserving(phase_flip_kraus(p))
    ok_dep = is_trace_preserving(depolarizing_kraus(p))
    print(f"{p:>6.2f}  {ok_bf!s:>10}  {ok_pf!s:>11}  {ok_dep!s:>13}")
"""
    )
)

cells.append(
    md(
        """All three channels are trace-preserving at every probability we
checked. Now apply each to `|0><0|` and to `|+><+|` and compare to the
analytic predictions.
"""
    )
)

cells.append(
    code(
        """rho_0 = ket_0 @ ket_0.conj().T
rho_1 = ket_1 @ ket_1.conj().T
rho_plus = ket_plus @ ket_plus.conj().T
rho_minus = ket_minus @ ket_minus.conj().T

p = 0.3

# Bit-flip on |0><0|: (1-p)|0><0| + p|1><1|.
out_bf_0 = bit_flip_channel(rho_0, p)
expected_bf_0 = (1.0 - p) * rho_0 + p * rho_1
assert np.allclose(out_bf_0, expected_bf_0, atol=1e-12)

# Bit-flip on |+><+|: unchanged because X |+> = |+>.
out_bf_plus = bit_flip_channel(rho_plus, p)
assert np.allclose(out_bf_plus, rho_plus, atol=1e-12)

# Phase-flip on |+><+|: (1-p)|+><+| + p|-><-|.
out_pf_plus = phase_flip_channel(rho_plus, p)
expected_pf_plus = (1.0 - p) * rho_plus + p * rho_minus
assert np.allclose(out_pf_plus, expected_pf_plus, atol=1e-12)

# Phase-flip on |0><0|: unchanged because Z |0> = |0>.
out_pf_0 = phase_flip_channel(rho_0, p)
assert np.allclose(out_pf_0, rho_0, atol=1e-12)

# Depolarizing on |0><0|: (1-p) rho_0 + p I/2.
out_dep_0 = depolarizing_channel(rho_0, p)
expected_dep_0 = (1.0 - p) * rho_0 + p * (0.5 * np.eye(2, dtype=np.complex128))
assert np.allclose(out_dep_0, expected_dep_0, atol=1e-12)

print(f"all analytic forms agree to 1e-12 at p = {p}")
print()
print("bit-flip on |0><0|:")
print(out_bf_0)
print("\\nphase-flip on |+><+|:")
print(out_pf_plus)
print("\\ndepolarizing on |0><0|:")
print(out_dep_0)
"""
    )
)

cells.append(
    md(
        """As expected:

* The bit-flip channel is the identity on `|+><+|` because `X |+> = |+>`
  (and on `|-><-|` too, with a sign). It is *not* the identity on
  `|0><0|`: it mixes in some `|1><1|`.
* The phase-flip channel is the identity on `|0><0|` and `|1><1|`
  (since `Z` acts trivially on the computational basis as a density)
  but mixes `|+><+|` with `|-><-|`.
* The depolarizing channel pushes *every* pure state toward `I/2`,
  with rate `p`. At `p = 1` the qubit is replaced by `I/2` exactly,
  independent of the input.

Sanity-check the last claim: depolarizing with `p = 1` on each of the
four states `{|0>, |1>, |+>, |->}` should give `I/2`.
"""
    )
)

cells.append(
    code(
        """rho_mixed_target = 0.5 * np.eye(2, dtype=np.complex128)
for name, rho in {"|0>": rho_0, "|1>": rho_1, "|+>": rho_plus, "|->": rho_minus}.items():
    out = depolarizing_channel(rho, 1.0)
    ok = np.allclose(out, rho_mixed_target, atol=1e-12)
    print(f"depolarizing(1.0) on {name:>3} -> I/2 ?  {ok}")
"""
    )
)

cells.append(
    md(
        """All four pure states collapse to `I/2`, which is the geometric
statement that the depolarizing channel contracts the entire Bloch
ball toward the origin with rate `p` (the ball at the end is a sphere
of radius `1 - p`, and at `p = 1` it is the single point at the
origin).

One more check: `I/2` is a **fixed point** of all three channels (any
Pauli commutes with `I` up to sign, so `P (I/2) P^dagger = I/2`).
"""
    )
)

cells.append(
    code(
        """for p in (0.0, 0.1, 0.5, 0.9, 1.0):
    out_bf = bit_flip_channel(rho_mixed_target, p)
    out_pf = phase_flip_channel(rho_mixed_target, p)
    out_dep = depolarizing_channel(rho_mixed_target, p)
    ok = (np.allclose(out_bf, rho_mixed_target)
          and np.allclose(out_pf, rho_mixed_target)
          and np.allclose(out_dep, rho_mixed_target))
    print(f"p={p:.2f}: all three channels leave I/2 invariant -> {ok}")
"""
    )
)

cells.append(
    md(
        """## Recap

* Density matrices generalise pure-state vectors so that mixed states
  and subsystems of entangled states fit into a single formalism.
  Three checks define a valid `rho`: Hermitian, trace 1, PSD.
* Partial trace produces reduced densities on subsystems. For a Bell
  state, both marginals are `I/2`; that is the operational content of
  "maximal entanglement".
* Quantum channels in Kraus form `E(rho) = sum K_k rho K_k^dagger`
  with `sum K_k^dagger K_k = I`. We implemented bit-flip, phase-flip,
  and depolarizing single-qubit channels and verified
  trace-preservation, the analytic action on `|0><0|` and `|+><+|`,
  and the `I/2` fixed point.

Phase 1 is done. **Next: Phase 2** — stabilizer formalism, Pauli
group machinery, and the first true QEC code (the three-qubit
repetition code).
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
