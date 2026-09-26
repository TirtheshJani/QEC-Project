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
6. Threshold simulation: vary $p_{\text{phys}}$ and $d$; produce the canonical
   crossing plot. Extract $p_{\text{th}}$ and sub-threshold $\Lambda$.

## Deliverables

- [x] `01-toric-and-surface/`: construct the rotated surface code at
      $d \in \lbrace 3,5,7 \rbrace$ programmatically; visualize the check lattice. Promoted
      `qec_project.codes.surface.RotatedSurfaceCode`.
- [x] `02-syndrome-extraction/`: sample the detector stream in Stim; verify the
      noiseless circuit fires no detectors; show detection density vs $p$.
- [x] `03-mwpm-pymatching/`: end-to-end pipeline `stim.Circuit` → DEM →
      `Matching.decode_batch` → logical error rate. Promoted
      `qec_project.decoders.pymatching_decoder` + `qec_project.decoders.harness`.
- [x] `04-threshold-simulation/`: the textbook crossing plot from the
      `capstone/experiments/` sweeps, plus the **MWPM vs BP+OSD** benchmark.
      Accuracy entries appended via `scripts/run_threshold_sweep.py --changelog`.
- [x] Phase entry in `CHANGELOG.md`; surface-code/decoder references in
      `docs/reading-list.md`.

## Result (uniform depolarizing noise, seed 42)

| Decoder | $p_\mathrm{th}$ (fit, per round) | time per shot, sampling + decoding @ d=5 |
| --- | --- | --- |
| MWPM (PyMatching) | $0.0122 \pm 0.0013$ ($d=3,5,7$) | ~9 µs |
| BP+OSD (ldpc) | $0.0134 \pm 0.0015$ ($d=3,5$) | ~5400 µs (about 600× MWPM) |

Figures in `capstone/figures/`; reproduce via `capstone/experiments/README.md`.
The decoders were driven **in-process** (not `sinter.collect`, which is incompatible
with NumPy 2.x here — see `CHANGELOG.md`). The threshold is specific to the
uniform-depolarizing model, not a published circuit-level number. The two fitted
thresholds overlap within fit error. See the top-level `README.md` for what the timing
measures, the fit-window systematic, and $\Lambda$ at $p=0.005$ with intervals.

## Workflow hints

- This is the first phase that runs serious Monte Carlo. Use
  Superpowers `dispatching-parallel-agents` for sweeps and always set seeds.
- Don't hand-roll matching — wrap PyMatching. This is in CHANGELOG's
  "Failed approaches" pre-emptively.

## References

- Austin G. Fowler, Matteo Mariantoni, John M. Martinis, Andrew N. Cleland,
  *Surface codes: Towards practical large-scale quantum computation.* Phys.
  Rev. A 86, 032324 (2012). arXiv:1208.0928.
- Oscar Higgott, Craig Gidney, *Sparse Blossom: correcting a million errors per core
  second with minimum-weight matching.* arXiv:2303.15933.
- Google Quantum AI, *Suppressing quantum errors by scaling a surface code
  logical qubit.* Nature 614, 676 (2023). arXiv:2207.06431.
