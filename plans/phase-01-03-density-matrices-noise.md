# Plan: Phase 1.3 — Density matrices, partial trace, single-qubit Kraus channels

Authored: 2026-05-14. Methodology: Superpowers `writing-plans` (in spirit;
plugin not yet installed). Followed by `test-driven-development` for any
code promoted into `src/qec_project/`.

## Goal

Deliver the third Phase 1 content notebook,
`phase-01-quantum-basics/03-density-matrices-noise/density_kraus.ipynb`,
covering exactly Phase 1 README learning goal 3: density operators
(pure / mixed), the partial trace, and the three canonical single-qubit
noise channels (bit-flip, phase-flip, depolarizing) written as Kraus
sets and verified to be trace-preserving. Promotes two small modules
needed in Phase 2 (`qec_project.noise.quantum` and
`qec_project.analysis.density`) with tests. The notebook runs
top-to-bottom with seeds set.

## Scope

### In scope

- Density operator `rho = |psi><psi|` (pure) and
  `rho = sum_i p_i |psi_i><psi_i|` (mixed). Properties: Hermitian,
  trace 1, positive semi-definite. Numerical verification on a small
  pure / mixed pair.
- Partial trace: for a Bell state `|Phi+>`, show that
  `Tr_B(|Phi+><Phi+|) = I/2`. Implement and verify the partial-trace
  helper.
- Kraus channels:
  * **Bit-flip** `K_0 = sqrt(1-p) I`, `K_1 = sqrt(p) X`.
  * **Phase-flip** `K_0 = sqrt(1-p) I`, `K_1 = sqrt(p) Z`.
  * **Depolarizing** (Nielsen-Chuang Eq. 8.102):
    `K_0 = sqrt(1 - 3p/4) I`, `K_{1,2,3} = sqrt(p/4) {X, Y, Z}`. This
    is the parametrisation that gives the closed form
    `rho -> (1 - p) rho + p I/2`.
- Trace-preservation check: numerically verify
  `sum_k K_k^dagger K_k = I` for each channel at a few values of p.
- Action on `|0><0|` and `|+><+|`:
  * Bit-flip on `|0><0|`: `(1 - p) |0><0| + p |1><1|`.
  * Phase-flip on `|+><+|`: `(1 - p) |+><+| + p |-><-|`.
  * Depolarizing on any pure state: `(1 - p) rho + p I/2`.
  All verified numerically.

### Out of scope (deferred)

- Multi-qubit channels, correlated noise -> Phase 3+ (circuit-level).
- Bloch ball contraction visualisation. Educational but not strictly
  needed; could be added later.
- Amplitude damping / generalised damping channels -> Phase 2+ or
  optional reading.
- Process tomography, Choi / chi representations -> not on the
  curriculum path to the rotated surface code.

## File-by-file changes

| Path | Action | Notes |
| ---- | ------ | ----- |
| `plans/phase-01-03-density-matrices-noise.md` | create | this plan |
| `phase-01-quantum-basics/03-density-matrices-noise/density_kraus.ipynb` | create | the notebook |
| `phase-01-quantum-basics/03-density-matrices-noise/_build_notebook.py` | create | nbformat builder |
| `phase-01-quantum-basics/03-density-matrices-noise/README.md` | create | one-pager |
| `src/qec_project/noise/quantum.py` | create | Kraus constructors + channel functions |
| `src/qec_project/analysis/density.py` | create | `is_density_matrix`, `partial_trace` |
| `tests/test_quantum_noise.py` | create | unit + hypothesis tests for the channels |
| `tests/test_density.py` | create | unit + hypothesis tests for the density helpers |
| `CHANGELOG.md` | edit | one consolidated Phase 1 (1.1 + 1.2 + 1.3) milestone |

### Promoted helpers — justification

- `qec_project.noise.quantum`: Phase 2's stabilizer-formalism simulator
  needs single-qubit error channels to be defined once and reused, and
  the same channels feed Phase 3's circuit-level depolarizing model.
  Promoting them now avoids redefinition in three places.
- `qec_project.analysis.density`: the partial-trace operation appears
  in every QEC paper from Phase 2 onward (reduced density on a logical
  qubit). `is_density_matrix` is a free sanity check that pays for
  itself the first time a circuit returns a not-quite-Hermitian
  numpy array.

### Public signatures (with type hints)

```python
# src/qec_project/noise/quantum.py
def apply_channel(rho: np.ndarray, kraus: Sequence[np.ndarray]) -> np.ndarray: ...
def is_trace_preserving(kraus: Sequence[np.ndarray], atol: float = 1e-10) -> bool: ...
def bit_flip_kraus(p: float) -> tuple[np.ndarray, np.ndarray]: ...
def phase_flip_kraus(p: float) -> tuple[np.ndarray, np.ndarray]: ...
def depolarizing_kraus(p: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: ...
def bit_flip_channel(rho: np.ndarray, p: float) -> np.ndarray: ...
def phase_flip_channel(rho: np.ndarray, p: float) -> np.ndarray: ...
def depolarizing_channel(rho: np.ndarray, p: float) -> np.ndarray: ...

# src/qec_project/analysis/density.py
def is_density_matrix(rho: np.ndarray, atol: float = 1e-9) -> bool: ...
def partial_trace(rho: np.ndarray, keep: Sequence[int] | int, dims: Sequence[int]) -> np.ndarray: ...
```

## Tests added

### `tests/test_quantum_noise.py`

1. `test_bit_flip_kraus_completeness`, `test_phase_flip_kraus_completeness`,
   `test_depolarizing_kraus_completeness` — sum `K^dagger K == I` for a
   sweep of p values.
2. `test_bit_flip_p_zero_is_identity`, `test_bit_flip_p_one_acts_as_X`.
3. `test_bit_flip_on_zero_matches_analytic_form`,
   `test_phase_flip_on_plus_matches_analytic_form`,
   `test_phase_flip_on_zero_is_identity`.
4. `test_depolarizing_on_pure_matches_closed_form` —
   `E(rho) = (1-p) rho + p I/2`.
5. `test_depolarizing_p_one_sends_everything_to_max_mixed`.
6. `test_max_mixed_is_fixed_point_of_all_three` — `I/2` invariant under
   each channel.
7. `test_apply_channel_preserves_trace`.
8. `test_channels_reject_out_of_range_p`,
   `test_is_trace_preserving_rejects_empty`,
   `test_is_trace_preserving_rejects_non_kraus`.
9. (hypothesis) `test_random_density_stays_valid_under_channel` — for a
   random density rho and random p, all three channels map rho to a
   valid density (Hermitian, trace 1, PSD).

### `tests/test_density.py`

1. `test_is_density_matrix_accepts_pure_state`,
   `test_is_density_matrix_rejects_non_hermitian`,
   `test_is_density_matrix_rejects_wrong_trace`,
   `test_is_density_matrix_rejects_non_psd`,
   `test_is_density_matrix_rejects_non_square`.
2. `test_partial_trace_bell_phi_plus_gives_max_mixed`.
3. `test_partial_trace_all_four_bell_states`.
4. `test_partial_trace_product_state_is_local`.
5. `test_partial_trace_preserves_trace`.
6. `test_partial_trace_three_qubit_keep_subset` — trace out the middle
   qubit of `|0> tensor |1> tensor |+>` and recover the product
   density on qubits 0 and 2.
7. `test_partial_trace_rejects_bad_dims`,
   `test_partial_trace_rejects_out_of_range_keep`.
8. (hypothesis) `test_partial_trace_random_two_qubit_state` — for a
   random 4x4 density, both single-qubit reduced densities are valid.

## Acceptance criteria

- `python -m uv run pytest` returns 0; >= 29 new tests added on top of
  Phase 0.
- `python -m uv run ruff check .` returns 0 findings.
- `python -m uv run jupyter nbconvert --to notebook --execute
  phase-01-quantum-basics/03-density-matrices-noise/density_kraus.ipynb
  --output _check.ipynb` runs to completion.
- Notebook sets `np.random.default_rng(0)` in its first code cell.
- `CHANGELOG.md` has one consolidated Phase 1 (1.1 + 1.2 + 1.3) milestone.

## Tasks (2-5 minute units, ordered)

1. Write `src/qec_project/noise/quantum.py`.
2. Write `src/qec_project/analysis/density.py`.
3. Write `tests/test_quantum_noise.py` and `tests/test_density.py`. Run
   pytest; iterate until green.
4. Ruff sweep; fix.
5. Scaffold `_build_notebook.py` with headings.
6. Fill notebook sections: density-operator primer, partial trace
   demonstration, three channels demonstration.
7. Run the builder; execute the notebook via nbconvert; iterate.
8. Write the README.
9. Append CHANGELOG milestone for the whole of Phase 1; update Current
   status to Phase 2.
10. Commit on the worktree branch with a single descriptive message.

## Out-of-band notes

- The depolarizing parametrisation choice is the
  Nielsen-Chuang Eq. 8.102 form (`rho -> (1 - p) rho + p I/2`). Some
  references use a different `p` such that each Pauli error
  individually has probability `p/3` and `K_0 = sqrt(1 - p) I`; we do
  **not** use that one because every QEC threshold paper relevant to
  the capstone uses the Nielsen-Chuang form.
- `partial_trace` uses the Kronecker / big-endian ordering of
  `qec_project.linalg.tensor`. Phase 2 stabilizer code will inherit
  the same convention.
