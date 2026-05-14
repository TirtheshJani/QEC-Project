# Pre-prompt: `/ars-lit-review --mode systematic-review` on decoders

Paste before invoking the deep-research systematic-review mode. The output
overwrites `capstone/proposal/literature-review.md` and is the basis for
NRC criterion 4 ("Addressing a gap").

---

Conduct a PRISMA-aligned systematic literature review on **decoders for
the rotated surface code**, with a particular eye on **real-time
feasibility** (target syndrome-cycle ~1 µs on superconducting hardware).

**Scope:**
- Decoder families: MWPM (and its variants — Sparse Blossom, Fusion
  Blossom, weighted-edge MWPM), Union-Find (Delfosse–Nickerson and
  successors), Belief Propagation + OSD, neural decoders (CNNs,
  transformers, RNNs), hybrid schemes.
- Noise models: uniform depolarizing, circuit-level SI1000, biased noise,
  noise with leakage.
- Date range: 2012 (Fowler et al.) → present.

**Required sections in output:**
1. Background & motivation. Why decoders, why rotated surface, why
   real-time matters.
2. Search protocol. Use the Scientific Agent Skills **Paper Lookup** for
   arXiv quant-ph queries. List exact search strings, date filters,
   inclusion/exclusion criteria.
3. PRISMA flow (counts at each stage).
4. Categorized results. One paragraph per (decoder family × noise model)
   cell that has published work; cite primary sources only.
5. **Gap statement** in a single paragraph. The gap must be specific
   enough that the experiment matrix in `capstone/README.md`
   credibly fills it.
6. References. DOI or arXiv ID per entry. Synchronize with
   `docs/reading-list.md`; do not introduce a reference here that isn't
   added there.

**Integrity rules (non-negotiable):**
- Do not invent paper titles, authors, or years.
- Every claimed number must be cited; do not paraphrase a result without
  giving the source.
- After producing the draft, run the `integrity_verification_agent` (ARS
  stage 2.5 gate) and report which entries failed verification. Do not
  ship a review that fails this gate.

**Output target:** ~3000 words, suitable as the lit-review section of an
arXiv preprint and as evidence for NRC EOI criterion 4.
