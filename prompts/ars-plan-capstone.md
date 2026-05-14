# Pre-prompt: `/ars-plan` for the capstone paper

Paste the block below before invoking `/ars-plan` (academic-paper.plan mode).
Anchors the Socratic dialogue inside this repo's scope so the resulting
paper outline is on-target for the NRC EOI.

---

I am the principal author of a solo decoder benchmark study for the rotated
surface code, targeting an EOI submission to NRC's Applied Quantum
Computing Challenge (QEC stream, *Decoding algorithm optimization* objective).

**Working title:** *Benchmarking real-time-feasible decoders for the rotated
surface code under biased and leakage-augmented noise.*

**Experiment matrix:** PyMatching (MWPM), Union-Find, BP+OSD, and a small
CNN neural decoder, across distances {3,5,7,9} and three noise models
(uniform depolarizing, SI1000, biased). 1e6 shots per cell. Latency
measured alongside accuracy.

**Novelty knob** (single, pre-committed): one of
(a) biased-noise-aware BP schedule;
(b) UF/MWPM hybrid trading latency for accuracy;
(c) neural pre-decoder + MWPM post-decoder.

**Existing artifacts to draw on:**
- `capstone/proposal/literature-review.md` — PRISMA gap statement
  (produced earlier via `/ars-lit-review`).
- `capstone/experiments/*.py` — reproducible scripts.
- `CHANGELOG.md` — accuracy tables with seeds and commit SHAs for every run.

**Constraints:**
- Target venue: arXiv quant-ph + NRC EOI. Length 10–15 pages.
- Anti-hallucination: every numerical claim must be either reproduced from
  one of our scripts or cited to a paper that appears in `docs/reading-list.md`
  with a DOI/arXiv ID.

**Ask:** Walk me Socratically through:
1. The opening (motivation + gap + this paper's contribution in 3 sentences).
2. The minimum methodology section that supports the experiment matrix.
3. The result presentation (what is the headline figure?).
4. The discussion's structure (where does the novelty knob live).

Output: an outline with section headings, two sentences per section, plus
the questions you still need answered before writing the abstract.
