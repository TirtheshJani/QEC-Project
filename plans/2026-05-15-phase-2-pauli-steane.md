# Plan: Phase 2 — Pauli formalism + Steane [[7,1,3]]

Date: 2026-05-15. Branch: `claude/deploy-multiple-agents-915lI`.

Scope: symplectic Pauli representation and Steane code construction with
TDD against ground-truth matrix algebra.

## Tasks

- [ ] Write `tests/test_pauli.py` (RED): from-string round-trip on random
      strings; full single-qubit multiplication table (X*Y = iZ etc.);
      `P^2 ∝ I`; weight equals non-I count; property test that
      symplectic-inner-product commutation agrees with direct
      `2^n x 2^n` matrix commutation for `n in {1, 2, 3}`.
- [ ] Implement `src/qec_project/codes/pauli.py`: dataclass `Pauli(n, x, z, phase)`
      with `__mul__` tracking phase via the standard formula, `commutes_with`
      using symplectic inner product `sum(x1*z2 + z1*x2) mod 2`, `weight`,
      `from_string`/`to_string`, and helpers `commutes_with_set` and
      `stabilizer_group_commutes`.
- [ ] Write `tests/test_steane.py` (RED): `verify_steane()` True; logical
      X anti-commutes with logical Z; exhaustive weight-1 and weight-2
      Pauli enumeration shows every non-trivial low-weight error either
      anti-commutes with at least one stabilizer or equals identity
      up to a logical-trivial element (distance >= 3).
- [ ] Implement `src/qec_project/codes/steane.py`: the canonical
      Steane stabilizers (3 X-type + 3 Z-type) and logicals based on
      Hamming(7,4); `verify_steane()`.
- [ ] `uv run ruff check` + `uv run pytest tests/test_pauli.py
      tests/test_steane.py` green.
- [ ] Build `phase-02-qec-fundamentals/03-stabilizer-formalism/stabilizers.ipynb`
      via `nbformat` + `nbclient`. Print stabilizer table; show syndromes
      for a few sample errors. Execute before saving; check outputs in JSON.
- [ ] `uv run pytest` full suite stays green.
