# Literature review — decoders for the rotated surface code

> **Status:** stub. This document is **produced**, not written by hand. At
> Phase 5 entry, run:
>
> ```
> /ars-lit-review --mode systematic-review
> ```
>
> using `prompts/ars-lit-review-decoders.md` as the seed context. The output
> overwrites this file and is then iterated.

## Required structure (PRISMA-aligned)

1. **Background and motivation.** Why the rotated surface code; why decoders
   in particular; what "real-time feasibility" means concretely (target
   syndrome cycle ~1 µs on superconducting hardware).
2. **Search protocol.** Databases (arXiv quant-ph via Scientific Agent
   Skills *Paper Lookup*, plus Google Scholar). Date range. Keywords.
   Inclusion/exclusion criteria.
3. **Results.** Categorize papers by decoder family (MWPM, UF, BP/BP+OSD,
   neural, hybrid) and by noise model used. Standard PRISMA flow diagram.
4. **Gap statement.** One paragraph maximum. The gap must be specific
   enough that the capstone experiment matrix in `capstone/README.md`
   credibly fills it.
5. **References.** Every entry mirrored in `docs/reading-list.md` with DOI
   or arXiv ID; `scripts/verify_reading_list.py` must pass on this file
   too.

## Integrity gate

Once produced, this file passes through ARS `integrity_verification_agent`
(stage 2.5). No paper title, year, or claimed number advances to
`paper/` without verification.
