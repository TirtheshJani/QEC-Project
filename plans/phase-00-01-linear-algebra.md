# Plan: Phase 0.1 — Linear algebra notebook + tensor / Pauli helpers

Authored: 2026-05-14. Methodology: Superpowers `writing-plans` (in spirit;
plugin not yet installed). Followed by `test-driven-development` for any code
promoted into `src/qec_project/`.

## Goal

Deliver the first content notebook of the curriculum,
`phase-00-foundations/01-linear-algebra/linear_algebra.ipynb`, covering
exactly the Phase 0 README learning goal 1 (linear algebra over finite
complex vector spaces: vectors, matrices, eigendecomposition, tensor
products) and the linear-algebra portion of goal 3 (parity-check / generator
matrices live in Phase 0.3; only matrix mechanics are introduced here). The
notebook runs top-to-bottom with seeds set and produces no figures that
require external data. Where a helper has obvious reuse downstream (Pauli
matrices, "is this unitary?" check), promote it to `src/qec_project/` with
tests; otherwise leave the code in the notebook.

## Scope

### In scope

- Complex vectors, inner products, norms (brief).
- Matrices: matmul, conjugate transpose, unitary check.
- Eigendecomposition of the four Pauli matrices `I, X, Y, Z`; numerical
  verification that `P = V D V^H`.
- Tensor (Kronecker) product:
  - Worked 2x2 kron 2x2 example with arithmetic shown in a markdown cell.
  - Numerical verification against `numpy.kron`.
  - One worked tensor product of two single-qubit states `|psi> kron |phi>`
    forming a 2-qubit state. State and document the basis ordering
    convention used by `numpy.kron` (Kronecker / big-endian: the first
    factor enumerates the most-significant qubit index).
- Connection to measurement: note that the Pauli eigenvalues `+/-1` are
  exactly the outcomes a Pauli measurement produces in Phase 1-2, so the
  eigendecomposition we compute here will be reused. No formal QM yet.

### Out of scope (deferred)

- Probability, channels, mutual information -> Phase 0.2.
- Hamming(7,4) and classical EC -> Phase 0.3.
- Density matrices, partial trace, Bloch sphere -> Phase 1.
- Stabilizer formalism, codes, decoders -> Phases 2+.
- Any plotting beyond what is needed pedagogically (this notebook is
  arithmetic, not figures).

## File-by-file changes

| Path | Action | Notes |
| ---- | ------ | ----- |
| `plans/phase-00-01-linear-algebra.md` | create | this plan |
| `phase-00-foundations/01-linear-algebra/linear_algebra.ipynb` | create | the notebook |
| `phase-00-foundations/01-linear-algebra/README.md` | create | what / how / outcomes |
| `src/qec_project/linalg.py` | create | small reusable module: Pauli constants, `is_unitary`, `tensor` wrapper, `eigendecompose` returning `(values, vectors)` |
| `tests/test_linalg.py` | create | unit + hypothesis property tests |
| `CHANGELOG.md` | edit | append milestone; update Current status |

I am **not** modifying `pyproject.toml`, `tests/test_smoke.py`,
`src/qec_project/__init__.py`, or anything in `phase-00-foundations/README.md`.

### `src/qec_project/linalg.py` — promoted helpers

Justification for promotion: every later phase needs Pauli matrices and a
unitarity check. Defining them in this notebook only to redefine them in
the next is wasteful; promotion saves duplication starting in Phase 0.3
(parity-check matrices benefit from the same helpers) and is mandatory in
Phase 2.

Public signatures (with type hints):

```python
PAULI_I: Final[np.ndarray]
PAULI_X: Final[np.ndarray]
PAULI_Y: Final[np.ndarray]
PAULI_Z: Final[np.ndarray]
PAULIS: Final[dict[str, np.ndarray]]  # {"I": ..., "X": ..., "Y": ..., "Z": ...}

def is_unitary(matrix: np.ndarray, atol: float = 1e-10) -> bool: ...
def tensor(*matrices: np.ndarray) -> np.ndarray: ...
def eigendecompose(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...
```

`tensor` is a thin variadic wrapper around `numpy.kron` so that
`tensor(X, Y, Z)` reads as `X kron Y kron Z`. `eigendecompose` returns
eigenvalues and eigenvectors with the convention that eigenvectors are
columns of the returned matrix (matches `numpy.linalg.eig`).

## Tests added (`tests/test_linalg.py`)

1. `test_pauli_shapes_and_dtype` — every Pauli is 2x2 complex.
2. `test_pauli_hermitian` — `P == P.conj().T` for `X, Y, Z` and `I`.
3. `test_pauli_unitary` — `is_unitary(P)` for each Pauli.
4. `test_pauli_squares_to_identity` — `P @ P == I` for `X, Y, Z`.
5. `test_pauli_anticommutation` — pairwise `{X, Y} = 0`, `{X, Z} = 0`,
   `{Y, Z} = 0` (anticommutator equals zero matrix).
6. `test_is_unitary_rejects_non_unitary` — random non-unitary matrices
   return `False`.
7. `test_tensor_matches_numpy_kron` — `tensor(X, Y)` equals
   `numpy.kron(X, Y)`.
8. `test_tensor_variadic_three_factors` — `tensor(X, Y, Z)` equals
   `numpy.kron(numpy.kron(X, Y), Z)`.
9. `test_eigendecompose_reconstructs_pauli_z` —
   `V @ diag(d) @ V^H == Z` within tolerance.
10. `test_eigendecompose_eigenvalues_pauli_z` — eigenvalues of `Z` are
    `{+1, -1}` as a set.
11. (hypothesis) `test_unitary_tensor_is_unitary` — for two random 2x2
    unitary matrices `U, V` (generated via QR of random complex matrices,
    seeded by hypothesis), `is_unitary(tensor(U, V))` is `True`.

## Acceptance criteria

- `python -m uv run pytest` returns 0; total tests >= 13 (existing 2 +
  >=11 new).
- `python -m uv run ruff check .` returns 0 findings.
- `jupyter nbconvert --to notebook --execute linear_algebra.ipynb` runs
  to completion without error.
- `python scripts/verify_reading_list.py` exits 0 (no new entries needed;
  Nielsen-Chuang and MacKay already named in `docs/reading-list.md`).
- Notebook has a fixed seed (`np.random.default_rng(0)`).
- Notebook has at least one markdown cell explicitly stating the basis
  ordering convention used by `numpy.kron`.
- `CHANGELOG.md` `## Completed milestones` has a new 2026-05-14 Phase 0.1
  entry, and `## Current status` points the next session at Phase 0.2.

## Tasks (2-5 minute units, ordered)

1. Write `src/qec_project/linalg.py` with the four Pauli constants and
   the three helpers.
2. Write `tests/test_linalg.py` covering the cases above. Run
   `pytest tests/test_linalg.py -x`; iterate until green.
3. Run `ruff check src/qec_project/linalg.py tests/test_linalg.py`;
   fix any issues.
4. Scaffold the notebook structure (markdown headings + empty code
   cells) using `nbformat` from a Python script invoked once.
5. Fill in the notebook cells:
   a. Header markdown (goals, references, seed cell).
   b. Vectors / inner product / norm section.
   c. Matrices / unitarity / Pauli definitions (import from
      `qec_project.linalg`).
   d. Pauli eigendecomposition + verification.
   e. Tensor product: hand-worked 2x2 kron 2x2, then numerical check.
   f. Tensor product of states with basis-ordering note.
   g. Recap.
6. Execute the notebook via `jupyter nbconvert --execute`. Iterate
   if it fails.
7. Write `phase-00-foundations/01-linear-algebra/README.md` (one page).
8. Final verification sweep: `pytest`, `ruff`, `verify_reading_list.py`.
9. Append CHANGELOG milestone; update Current status.
10. `git add` the new files; commit on branch `main` with
    `Phase 0.1: linear algebra notebook + tensor product + Pauli eigendecomp`.

## Out-of-band notes

- `uv` was not on PATH on this machine; using `python -m uv` works
  because `uv` is installed in user-site. The standing commands in
  `CLAUDE.md` (`uv run …`) are unchanged for documentation; only the
  invocation path differs locally.
- No new entries to `docs/reading-list.md` this phase: Nielsen-Chuang
  and MacKay are already listed by name. Add specific chapters when a
  numerical claim from one of them lands.
- Lint adjustment: `PAULI_Y` is exposed by `qec_project.linalg` (and
  tested), but the notebook accesses it via the `PAULIS` dict rather
  than by symbol, so it is not re-imported into the notebook cell. Ruff
  caught this on the first run; fix applied in `_build_notebook.py`.
