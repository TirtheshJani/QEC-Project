# Phase 0.1 — Linear algebra

The first content notebook of the curriculum. Builds the linear-algebra
fluency that every QEC paper assumes you already have.

## What it covers

1. Complex vectors, inner products, norms (one-qubit states `|0>, |1>,
   |+>, |->` as worked examples).
2. Matrices, conjugate transpose, the unitarity check we will reuse for
   every quantum gate, and the four Pauli matrices `I, X, Y, Z` —
   hermiticity, unitarity, `P @ P == I`, anticommutation.
3. Eigendecomposition of each Pauli with numerical verification that
   `P = V D V^H`. Eigenvalues `+/-1` are foreshadowed as the
   measurement outcomes that will reappear in Phase 1 and as the
   syndrome bits in Phase 2.
4. Tensor (Kronecker) product:
   - A worked `2x2 kron 2x2` example (`X kron Z`) with the arithmetic
     written out explicitly in markdown, then checked against
     `numpy.kron`.
   - One tensor product of single-qubit states (`|0> kron |1>`,
     `|+> kron |0>`) with an explicit note that `numpy.kron` uses
     Kronecker / big-endian ordering: the first factor is the
     most-significant qubit.
   - A property check that the tensor of two random unitaries is
     unitary.

The notebook reuses `qec_project.linalg` (`PAULI_I/X/Y/Z`, `PAULIS`,
`tensor`, `is_unitary`, `eigendecompose`). Those helpers were promoted
to `src/qec_project/` because every subsequent phase needs them; their
tests are in `tests/test_linalg.py`.

## How to run

From the repo root:

```bash
uv sync --extra dev
uv run jupyter lab phase-00-foundations/01-linear-algebra/linear_algebra.ipynb
```

Or non-interactively:

```bash
uv run jupyter nbconvert --to notebook --execute \
    phase-00-foundations/01-linear-algebra/linear_algebra.ipynb \
    --output _check.ipynb
```

A fixed seed (`np.random.default_rng(0)`) is set in the first code cell;
the notebook is deterministic across runs.

`_build_notebook.py` in this directory is the source from which the
notebook is generated. Edit it (not the `.ipynb` directly) when the
notebook structure needs to change, then re-run it.

## After reading this you should be able to

- Write a one- or two-qubit state as a column vector and check its norm.
- Verify that a matrix is unitary, and explain why every gate must be.
- Compute the eigendecomposition of a Hermitian matrix and read off the
  measurement outcomes from its eigenvalues.
- Compute a Kronecker product by hand for two 2x2 matrices and verify
  numerically.
- State which factor is the most-significant qubit under
  `numpy.kron`'s convention and predict the non-zero index of
  `|a> kron |b>` for any one-qubit computational-basis states.

## References

Both are in `docs/reading-list.md`:

- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  10th anniversary ed., Cambridge, 2010 — chapter 2.
- MacKay, *Information Theory, Inference, and Learning Algorithms*,
  Cambridge, 2003 — chapters 1 and 2 (linear-algebra-flavoured
  prerequisites).

For visual intuition: 3Blue1Brown's *Essence of Linear Algebra* series
on YouTube. (Not numerically cited so not in the reading list.)
