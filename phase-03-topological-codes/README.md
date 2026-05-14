# Phase 3 — Topological codes & the surface code

**Duration:** ~4 weeks. **Prereq:** Phase 2.

This is the phase where the capstone starts to take shape. The rotated
surface code is the dominant code in the lab today; the rest of the
curriculum builds tooling around it.

## Learning goals

1. Topological codes intuitively: stabilizers as plaquette checks on a 2D
   lattice; logical operators as homologically nontrivial loops.
2. The planar (rotated) surface code: distance, qubit count, stabilizer
   structure.
3. Syndrome-extraction circuits with measurement ancillas. Repeated rounds.
4. MWPM decoding: detector graphs, error-edge weights, perfect matching.
5. **PyMatching** in anger: feed it a Stim DEM, decode batches, measure
   logical error rate.
6. Threshold simulation: vary $p_{\\text{phys}}$ and $d$; produce the canonical
   crossing plot. Extract $p_{\\text{th}}$ and sub-threshold $\\Lambda$.

## Deliverables

- [ ] `01-toric-and-surface/`: construct the rotated surface code at
      $d \\in \\{3,5,7\\}$ programmatically; visualize stabilizers.
- [ ] `02-syndrome-extraction/`: build the depth-6 stabilizer-measurement
      circuit in Stim; sample syndromes; verify boundary conditions.
- [ ] `03-mwpm-pymatching/`: end-to-end pipeline: `stim.Circuit` →
      detector data → `Matching.decode_batch` → logical error rate. Lives in
      `src/qec_project/decoders/mwpm.py` behind the common `decode()`
      interface.
- [ ] `04-threshold-simulation/`: replicate the textbook crossing plot using
      `sinter`. Append each run as an Accuracy table entry via
      `python scripts/update_changelog.py --kind accuracy ...`.
- [ ] Phase entry in `CHANGELOG.md`. ~15 references in
      `docs/reading-list.md`.

## Workflow hints

- This is the first phase that runs serious Monte Carlo. Use
  Superpowers `dispatching-parallel-agents` for sweeps and always set seeds.
- Don't hand-roll matching — wrap PyMatching. This is in CHANGELOG's
  "Failed approaches" pre-emptively.

## References

- Austin G. Fowler, Matteo Mariantoni, John M. Martinis, Andrew N. Cleland,
  *Surface codes: Towards practical large-scale quantum computation.* Phys.
  Rev. A 86, 032324 (2012). arXiv:1208.0928.
- Oscar Higgott, *PyMatching v2.* arXiv:2303.15933.
- Google Quantum AI, *Suppressing quantum errors by scaling a surface code
  logical qubit.* Nature 614, 676 (2023). arXiv:2207.06431.
