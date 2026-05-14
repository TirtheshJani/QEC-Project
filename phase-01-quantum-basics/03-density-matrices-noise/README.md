# Phase 1.3 — Density matrices, partial trace, single-qubit Kraus channels

The third Phase 1 notebook. Builds the density-operator formalism and
the three single-qubit noise channels that Phase 2's stabilizer
simulator (and Phase 3+'s circuit-level noise model) will rely on.

## What it covers

1. Density matrices: pure vs mixed, the three defining properties
   (Hermitian, trace 1, positive semi-definite), and purity
   `Tr(rho^2)` as a discriminator.
2. Partial trace: for the Bell state `|Phi+>`, both marginals are
   `I/2`; for a product state, each marginal is the local factor.
   Implemented in `qec_project.analysis.density.partial_trace` using
   the Kronecker / big-endian convention pinned in Phase 0.1.
3. Three single-qubit channels in Kraus form:
   - **Bit-flip** `K_0 = sqrt(1-p) I`, `K_1 = sqrt(p) X`.
   - **Phase-flip** `K_0 = sqrt(1-p) I`, `K_1 = sqrt(p) Z`.
   - **Depolarizing** (Nielsen-Chuang Eq. 8.102 form)
     `K_0 = sqrt(1 - 3p/4) I`, `K_{1,2,3} = sqrt(p/4) {X, Y, Z}`,
     giving the closed form `rho -> (1 - p) rho + p I/2`.
4. Numerical sanity checks for each channel: completeness
   `sum_k K_k^dagger K_k = I`, the closed-form action on `|0><0|` and
   `|+><+|`, the `I/2` fixed point, and (in tests) the
   property-test that random density matrices stay valid under any
   of the three channels.

## Promoted helpers

Two new modules entered `src/qec_project/`:

- `qec_project.noise.quantum` — `apply_channel`, `is_trace_preserving`,
  `{bit_flip, phase_flip, depolarizing}_{kraus, channel}`. Reused
  from Phase 2 onward.
- `qec_project.analysis.density` — `is_density_matrix`, `partial_trace`.
  Reused from Phase 2 onward (reduced densities on logical qubits).

Tests live in `tests/test_quantum_noise.py` (16 tests including a
hypothesis property test) and `tests/test_density.py` (13 tests
including a hypothesis property test).

## How to run

From the repo root:

```bash
uv sync --extra dev
uv run jupyter lab phase-01-quantum-basics/03-density-matrices-noise/density_kraus.ipynb
```

Or non-interactively:

```bash
uv run jupyter nbconvert --to notebook --execute \
    phase-01-quantum-basics/03-density-matrices-noise/density_kraus.ipynb \
    --output _check.ipynb
```

A fixed seed (`np.random.default_rng(0)`) is set in the first code
cell. The notebook is deterministic across runs.

`_build_notebook.py` is the source from which the notebook is
generated; edit it then re-run.

## After reading this you should be able to

- Test whether a numpy array is a valid density matrix.
- Compute the partial trace of any density matrix on a tensor-product
  space.
- Write down the Kraus operators for the bit-flip, phase-flip, and
  depolarizing channels with the Nielsen-Chuang depolarizing
  parametrisation.
- Apply a Kraus channel to a density matrix and verify that the
  result is still a valid density.

## References

In `docs/reading-list.md`:

- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  sections 2.4 (density operator), Box 2.6 (partial trace), and 8.3
  (operator-sum representation; Eq. 8.102 is our depolarizing form).
