# Search protocol — decoder literature review for the rotated surface code

This is the **reproducible search plan** that backs `capstone/proposal/literature-review.md`.
It is the artifact NRC reviewers (and `integrity_verification_agent`) will
audit when they ask "how did you find these papers, and what did you miss?"

## Question

> Which decoder families are competitive for the **rotated surface code**
> at distances $d \in \{3,5,7,9\}$ under depolarizing, circuit-level
> SI1000, and biased noise, when judged jointly on logical error rate
> and wall-clock latency in the **real-time regime** (target syndrome
> cycle $\sim 1\,\mu s$ on superconducting hardware)? Where in this
> joint frontier is the literature thin?

## Scope (PRISMA inclusion/exclusion)

**Date range.** 2012-01-01 (Fowler et al., arXiv:1208.0928) → 2026-05-15.

**Population.** Papers proposing, optimizing, benchmarking, or implementing
in hardware a decoder for the planar / rotated surface code (or directly
transferring such a decoder to it).

**Decoder families in scope.**
- MWPM family: blossom, Sparse Blossom, Fusion Blossom, weighted-edge MWPM,
  FPGA / ASIC matching engines.
- Union-Find family: Delfosse–Nickerson and parallel / weighted / hardware
  successors.
- Belief Propagation: vanilla BP, BP+OSD, BP+OTS, neural-BP, closed-branch.
- Neural decoders: feedforward, CNN, RNN, transformer, recurrent-transformer
  (AlphaQubit class), neural pre-/post-decoders.
- Hybrid / real-time: predecoder cascades, parallel-window decoders,
  online / streaming decoders.

**Noise models tracked per paper.**
- Code-capacity vs phenomenological vs circuit-level.
- Uniform depolarizing.
- SI1000 (Gidney et al.).
- Biased noise (Z-biased, dephasing-dominated).
- Leakage / non-Pauli noise.

**Outcome variables extracted per paper.**
- Threshold $p_{\text{th}}$ (with the noise model that produced it).
- Sub-threshold suppression $\Lambda$ when reported.
- Wall-clock per syndrome cycle or shots/second.
- Hardware platform (CPU / GPU / FPGA / ASIC) when applicable.
- Reproducibility artifacts (Stim circuit, public code).

**Inclusion criteria.**
1. Reports at least one of (threshold, $\Lambda$, logical error rate at a
   specified $p_\text{phys}$ and distance, or wall-clock latency).
2. Either peer-reviewed OR posted to arXiv with reproducible methodology.
3. English.

**Exclusion criteria.**
1. Pure architecture / compiler papers with no decoder algorithm content.
2. Decoders only demonstrated on non-2D-topological codes with no
   adaptation to the surface code.
3. Reviews and book chapters (cited as context, not categorised).
4. Editorials, perspectives, talks without an associated technical paper.

## Information sources

Direct arXiv / DOI fetching is blocked by the container's network policy
(verified: HTTP 403 to `arxiv.org`, `export.arxiv.org`,
`api.semanticscholar.org`, `api.crossref.org`). `WebSearch` is available
and returns title + URL metadata from Google's index.

Therefore the protocol relies on:
1. `WebSearch` Google index — title, authors, arXiv ID extracted from
   result snippets.
2. The author / venue / arXiv-ID triple is cross-confirmed by retrieving
   **at least two independent search-result URLs** per paper (e.g. one
   `arxiv.org/abs/...` link and one `quantum-journal.org`,
   `semanticscholar.org`, `nature.com`, or `journals.aps.org` link).
3. Out of band: authors known from `docs/reading-list.md` seed entries
   used as known-good anchors.

Anything that cannot be confirmed via the protocol above is flagged
`[unverified]` in the review and **not added to** `docs/reading-list.md`.

## Boolean search strings (executed as `WebSearch` queries)

Each string below corresponds to one slice of the literature review.

### S1 — MWPM family
- `arXiv "minimum-weight perfect matching" "surface code" decoder`
- `arXiv "Sparse Blossom" OR "Fusion Blossom" surface code`
- `"PyMatching" OR "blossom" "surface code" threshold benchmark`
- `FPGA OR ASIC "minimum-weight matching" surface code decoder real-time`

### S2 — Union-Find family
- `arXiv "Union-Find" decoder "surface code" Delfosse Nickerson`
- `arXiv "Union-Find" decoder parallel OR hardware OR FPGA surface code`
- `arXiv "weighted Union-Find" surface code biased noise`

### S3 — Belief propagation + OSD
- `arXiv "belief propagation" "ordered statistics" decoder surface code`
- `arXiv "BP-OSD" OR "BP+OSD" qLDPC OR "surface code"`
- `arXiv "neural belief propagation" quantum decoder`
- `arXiv "closed-branch decoder" OR "OTS" surface code`

### S4 — Neural decoders
- `arXiv "neural network decoder" "surface code"`
- `arXiv "convolutional neural network" decoder surface code`
- `arXiv "transformer" decoder "quantum error correction"`
- `"AlphaQubit" OR "recurrent transformer" surface code decoder`

### S5 — Real-time / hybrid / hardware / noise-aware
- `arXiv "real-time decoder" surface code FPGA OR ASIC`
- `arXiv predecoder OR "two-stage decoder" surface code`
- `arXiv "biased noise" decoder surface code threshold`
- `arXiv leakage decoder surface code`
- `arXiv SI1000 noise circuit-level surface code`

## PRISMA flow target

Each slice agent reports:
1. Number of unique titles surfaced.
2. Number passing the inclusion criteria.
3. Number with confirmed arXiv ID or DOI (the only ones admitted to the
   review and reading-list).
4. Excluded counts with reason categories.

A combined PRISMA flow diagram is assembled in
`capstone/proposal/literature-review.md` from the per-slice numbers.

## Integrity gates

1. Every reference in `literature-review.md` has a `docs/reading-list.md`
   entry with arXiv ID or DOI; `scripts/verify_reading_list.py` is green.
2. No paper title, author, or year is paraphrased — they are copy-pasted
   from `WebSearch` results and the URL is recorded next to each entry
   in `capstone/proposal/literature-review-evidence.md`.
3. Any unverifiable claim is flagged `[unverified]` and excluded from
   the gap statement.

## Known limitations of this search

- Without arXiv full-text fetch, papers' **numerical claims** (thresholds,
  $\Lambda$, latencies) cannot be extracted in-container. The review
  categorises decoders by claim *type* and cites the paper, but a
  follow-up session (with direct arXiv access) is required before the
  capstone paper draft can quote specific numbers.
- WebSearch ranks Google's index; non-indexed or very recent (≤30 day)
  arXiv preprints may be missed.
- This protocol is biased toward English-language work; non-English
  decoder literature is out of scope for the EOI.
