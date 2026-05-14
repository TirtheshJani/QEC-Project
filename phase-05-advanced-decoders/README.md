# Phase 5 — Advanced decoders & qLDPC codes

**Duration:** ~4 weeks. **Prereq:** Phase 4. **This is the capstone runway.**

By the end of this phase you are ready to pick one focused decoder question
and chase it through the capstone. Everything here should be done with the
capstone in mind.

## Learning goals

1. Belief propagation on Tanner graphs; why vanilla BP fails on the surface
   code (degenerate errors), why it works on qLDPC codes.
2. **BP + OSD** as the standard decoder for qLDPC. Hands-on with Joschka
   Roffe's `ldpc` package.
3. **Union-Find** decoding (Delfosse–Nickerson) — linear-time, real-time
   feasible, what most current FPGA decoders approximate.
4. Neural decoders — a small CNN/transformer trained on Stim syndrome
   samples for $d \\in \\{5,7,9\\}$. Where they help, where they don't.
5. **qLDPC codes**: the bivariate-bicycle family (IBM 2024) and hypergraph
   product codes. Why they matter (better rate/distance/overhead).

## Deliverables

- [ ] `01-belief-propagation/`: BP on a small Tanner graph; observe the
      surface-code failure mode.
- [ ] `02-bp-osd/`: BP+OSD on a $[[72,12,6]]$ bivariate bicycle code; logical
      error rate vs $p_{\\text{phys}}$.
- [ ] `03-union-find/`: implement (or wrap) Union-Find; compare logical
      error AND wall-clock latency vs PyMatching on the surface code.
- [ ] `04-neural-decoders/`: train a small CNN on Stim syndromes for the
      $d=5$ surface code; measure accuracy AND inference latency. Use the
      Scientific Agent Skills **PyTorch Lightning** skill.
- [ ] `05-qldpc-bivariate-bicycle/`: construct the IBM 2024 codes; verify
      stabilizers commute; sample logical error rates.
- [ ] Phase entry in `CHANGELOG.md`. ~25 references in
      `docs/reading-list.md`. The capstone literature review (next stop)
      is built on top of these.

## Workflow hints

- Time to run `/ars-lit-review --mode systematic-review` on decoders. The
  output seeds `capstone/proposal/literature-review.md` and underwrites
  NRC criterion 4 ("Addressing a gap").
- For sweeps that don't fit on local hardware, switch to Modal via
  `scripts/run_threshold_sweep.py --remote`.

## References (seed)

- Joschka Roffe et al., *Decoding across the quantum LDPC code landscape.*
  arXiv:2005.07016.
- Nicolas Delfosse, Naomi H. Nickerson, *Almost-linear time decoding
  algorithm for topological codes.* Quantum 5, 595 (2021).
  arXiv:1709.06218.
- Sergey Bravyi et al., *High-threshold and low-overhead fault-tolerant
  quantum memory.* Nature 627, 778 (2024). arXiv:2308.07915.
  (the IBM bivariate-bicycle paper).
- Savvas Varsamopoulos, Ben Criger, Koen Bertels, *Decoding small surface
  codes with feedforward neural networks.* Quantum Sci. Technol. 3, 015004
  (2017). arXiv:1705.00857.
