# Capstone — Decoder benchmark study for the rotated surface code

**Duration:** ~6–8 weeks. **Prereq:** Phases 0–5 complete.

This is the artifact you bring to an NRC EOI conversation. It is one focused,
reproducible decoder study end-to-end, not a survey.

## Working title

*Benchmarking real-time-feasible decoders for the rotated surface code under
biased and leakage-augmented noise.*

(Refine after the lit review, but keep the scope this tight.)

## NRC priority alignment

Maps to NRC's stated objective:

> **Decoding algorithm optimization:** Design and optimize decoding algorithms
> to achieve high-efficiency, noise-resistant decoders capable of real-time
> signal recovery in noisy environments.

## Experiment matrix (target)

| Decoder | Noise models | Distances | Shots/cell |
| --- | --- | --- | --- |
| PyMatching (MWPM) | depolarizing, SI1000, biased | 3, 5, 7, 9 | 1e6 |
| Union-Find | depolarizing, SI1000, biased | 3, 5, 7, 9 | 1e6 |
| BP + OSD | depolarizing, SI1000, biased | 3, 5, 7 | 1e6 |
| Small CNN (Phase 5 model) | depolarizing, SI1000 | 5, 7 | 1e6 |

Plus latency benchmarks: wall-clock per shot at $d=7$, batched.

## Novelty knob (pick ONE during Phase 5)

- (a) Biased-noise-aware BP schedule + comparison to vanilla BP+OSD.
- (b) UF/MWPM hybrid: short codeword → UF, long → MWPM; trace the
      latency / accuracy frontier.
- (c) Neural pre-decoder + MWPM post-decoder; measure if the neural net
      can substitute for higher-order MWPM in a fixed latency budget.

The novelty section in the paper draft argues why your choice fills the gap
identified in `proposal/literature-review.md`.

## Deliverables

- [ ] `proposal/literature-review.md` — PRISMA-grade gap statement built via
      `/ars-lit-review --mode systematic-review`.
- [ ] `proposal/eoi-mock.md` — fully filled NRC EOI (all 7 criteria) using
      this study as the basis.
- [ ] `experiments/` — one runnable script per matrix row; each writes a
      seeded `sinter` artifact and appends an entry to CHANGELOG's accuracy
      table.
- [ ] `figures/` — threshold-crossing plot per noise model; latency vs
      accuracy Pareto curve.
- [ ] `paper/` — LaTeX preprint draft, ~10–15 pages, arXiv quant-ph format.
- [ ] Final pass: `/ars-review --mode full` on your own paper. Address
      every reviewer point. Then `/ars-disclosure --venue "NRC AQC Challenge"`.

## Integrity gates (non-negotiable)

- Stage 2.5 (after lit review): `integrity_verification_agent` confirms
  every cited paper exists and every borrowed number reproduces from the
  cited source.
- Stage 4.5 (after experiments): same gate, plus `verify_reading_list.py`
  is green and every result in `figures/` is reproducible from a script
  in `experiments/`.
