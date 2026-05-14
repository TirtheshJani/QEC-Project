# Plan: Phase 1.2 — Multi-qubit states, Bell states, teleportation, superdense coding

Authored: 2026-05-14. Methodology: Superpowers `writing-plans` (in spirit;
plugin not yet installed). Followed by `test-driven-development` for any
code promoted into `src/qec_project/`.

## Goal

Deliver the second Phase 1 content notebook,
`phase-01-quantum-basics/02-multi-qubit-entanglement/multi_qubit.ipynb`,
covering exactly Phase 1 README learning goal 2: tensor products,
multi-qubit states, the four Bell states constructed two ways (by-hand
numpy.kron and via Qiskit), superdense coding (2 classical bits over 1
qubit + shared Bell pair), and the standard three-qubit teleportation
circuit. Qiskit + qiskit-aer enter the curriculum here for the first
time. The notebook runs top-to-bottom with seeds set.

## Scope

### In scope

- General multi-qubit state vector
  `|psi>_{AB} = sum_{ij} c_{ij} |i>_A |j>_B`.
- Basis-ordering convention statement: `numpy.kron` is big-endian (first
  factor is the most-significant qubit; pinned in Phase 0.1). Qiskit
  uses little-endian in its display strings (qubit 0 is the rightmost).
  Spell out the difference so the reader can switch between the two.
- The four Bell states `|Phi+>, |Phi->, |Psi+>, |Psi->` constructed by
  hand with `qec_project.linalg.tensor`. Verify they are orthonormal.
- Qiskit Bell-state circuits: H on qubit 0, CNOT(0, 1) for `|Phi+>`;
  three sibling circuits for the other Bell states (X / Z prep on
  qubit 0 / 1 before the H or after). Verify via
  `qiskit.quantum_info.Statevector` that the state vector matches the
  hand-computed one (modulo Qiskit's qubit-ordering convention; we
  reverse to match `numpy.kron`).
- Superdense coding: implement in Qiskit. Alice and Bob share `|Phi+>`;
  Alice applies one of `{I, X, Z, XZ}` to encode 2 classical bits;
  she sends her qubit; Bob applies CNOT then H and measures. Run on
  `qiskit_aer.AerSimulator` with 1000 shots per message and confirm
  correct decode for all four 2-bit messages.
- Teleportation: standard 3-qubit teleportation. Use
  `qiskit.circuit.classical.expr` / classical conditional gates
  (`with circuit.if_test`) for the feed-forward. Verify by preparing a
  random one-qubit state on qubit 0, teleporting to qubit 2, and
  comparing `Statevector` of qubit 2 (conditional on the measurement
  outcomes) to the original state.

### Out of scope (deferred)

- Mixed states, density matrices, partial trace -> Phase 1.3.
- Multi-qubit Pauli operators as stabilizer generators -> Phase 2.
- Hardware-specific transpilation, layout, calibration.
- Any noise on top of the circuits (Phase 1.3 starts noise on single
  qubits; multi-qubit noise comes in Phase 2+).

## File-by-file changes

| Path | Action | Notes |
| ---- | ------ | ----- |
| `plans/phase-01-02-multi-qubit-entanglement.md` | create | this plan |
| `phase-01-quantum-basics/02-multi-qubit-entanglement/multi_qubit.ipynb` | create | the notebook |
| `phase-01-quantum-basics/02-multi-qubit-entanglement/_build_notebook.py` | create | nbformat builder |
| `phase-01-quantum-basics/02-multi-qubit-entanglement/README.md` | create | one-pager |

No `src/qec_project/` changes here. Bell-state constants, the
superdense codec, and the teleportation circuit could in principle be
promoted, but they are pedagogical artefacts; Phase 2 stabilizer
machinery generates Bell states as a special case.

### Promoted helpers — justification

None. The Phase 2 stabilizer simulator (next phase) will subsume what
this notebook does by hand. Promoting now would create code we have to
keep in sync with the eventual stabilizer-based generator.

## Tests added

None new. The notebook's Statevector cross-checks and the 1000-shot
superdense-coding decode are the tests; if they fail, the notebook
fails. The `qec_project.linalg.tensor` helper used here is already
tested in `tests/test_linalg.py`.

## Acceptance criteria

- `python -m uv run pytest` continues to return 0.
- `python -m uv run ruff check .` returns 0 findings.
- `python -m uv run jupyter nbconvert --to notebook --execute
  phase-01-quantum-basics/02-multi-qubit-entanglement/multi_qubit.ipynb
  --output _check.ipynb` runs to completion.
- Notebook sets `np.random.default_rng(0)` in its first code cell;
  `aer_simulator` is seeded via `seed_simulator=0` on `Sampler.run`.
- Notebook contains: basis-convention note, Bell-state by-hand + Qiskit
  construction with Statevector cross-check, superdense coding with
  >= 1000 shots and correct decode for all four messages, teleportation
  with Statevector-based fidelity check.

## Tasks (2-5 minute units, ordered)

1. Scaffold `_build_notebook.py` with headings.
2. Add the basis-convention markdown + the by-hand Bell state cells.
3. Add the Qiskit Bell circuits + Statevector cross-checks (note the
   little-endian reversal).
4. Add the superdense coding circuit and 1000-shot Aer run; assert
   the empirical mode equals the encoded 2-bit message for each of
   the four inputs.
5. Add the teleportation circuit. Prepare a random 1-qubit state,
   build the 3-qubit circuit with two classical bits and the
   `if_test` feed-forward, verify Statevector of qubit 2 equals the
   original.
6. Run `_build_notebook.py`; execute the notebook via nbconvert; iterate.
7. Write the README.

## Out-of-band notes

- Qiskit's classical feed-forward syntax changed across the 1.x series;
  we are on `qiskit>=1.2`. `with circuit.if_test((cbit, value)):` is
  the supported pattern. If that fails on the installed version, fall
  back to `circuit.c_if(cbit, value)` on the gate (legacy API still
  works in 1.x).
- AerSimulator's `run` returns a result whose `get_counts` gives a dict
  keyed by little-endian bitstrings; reverse on read.
- Qiskit qubit ordering: `Statevector` from a 2-qubit circuit returns
  a length-4 vector with the convention `|q1 q0>` (qubit 0 is the
  least significant). Our by-hand `tensor(|q0>, |q1>)` has the
  opposite convention. We reconcile by reversing one or the other
  explicitly in the cross-check.
