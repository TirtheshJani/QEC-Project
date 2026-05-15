# Plan: Phase 3 — Rotated surface code + MWPM decoder

Date: 2026-05-15. Branch: `claude/deploy-multiple-agents-915lI`.

Scope: build the rotated surface-code circuit factory, the MWPM decoder
wrapper (capstone primary baseline), tests against Stim ground truth, and
a small illustrative threshold sweep notebook for d in {3, 5}.

## Tasks

- [ ] `src/qec_project/decoders/base.py`: `Decoder` Protocol with
      `decode_batch(detection_events) -> predictions`. Shapes documented in
      docstring: `(shots, n_detectors) bool/uint8 -> (shots, n_observables)`.
- [ ] `tests/test_surface_code.py` (RED): for `d=3, rounds=3, p=0.01`,
      assert `num_detectors == 24` and `num_observables == 1` (regression
      baseline computed by direct Stim inspection). For `p_phys=0`, 100
      shots produce zero detector clicks and zero observable flips. Input
      validation: even distance, distance<3, rounds<1, p out of [0, 0.5]
      raise ValueError.
- [ ] `src/qec_project/codes/surface_code.py`: `rotated_surface_code_circuit`
      wraps `stim.Circuit.generated('surface_code:rotated_memory_z', ...)`
      with depolarizing noise knobs set equal to `p_phys`. Validate inputs.
      Helper `code_parameters(distance)` returns
      `{"n_data", "n_stabilizers", "n_x_stabilizers", "n_z_stabilizers",
      "distance"}`.
- [ ] `tests/test_mwpm.py` (RED): `from_circuit` round-trip; at `p_phys=0`,
      `d=3, rounds=2, shots=200`: zero logical errors. At `p_phys=0.001`,
      `d=3, rounds=2, shots=2_000`, seeded: logical error rate < p_phys.
- [ ] `src/qec_project/decoders/mwpm.py`: `MwpmDecoder` constructed from a
      `stim.DetectorErrorModel`. `decode_batch` returns `(shots, n_obs)`
      uint8 predictions. `from_circuit` classmethod builds DEM with
      `decompose_errors=True`.
- [ ] Build + execute notebook
      `phase-03-topological-codes/04-threshold-simulation/threshold_d3_d5_d7.ipynb`
      programmatically via nbformat + nbclient. Sweep ~6 p_phys points in
      [0.005, 0.02] for d in {3, 5} with rounds=d, shots ~10_000. Plot
      logical-error-rate-per-round vs p_phys. Print table at end. Seeds set.
- [ ] `uv run ruff check` new files + `uv run pytest` full suite green.
