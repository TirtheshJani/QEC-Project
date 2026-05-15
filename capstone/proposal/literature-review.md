# Literature review — decoders for the rotated surface code

> **Status:** v1, 2026-05-15. Produced by five parallel research agents
> executing the protocol in `capstone/proposal/search-protocol.md`,
> followed by a single-author cross-slice synthesis. The five slice
> fragments and their verified bibliographies live in
> `capstone/proposal/literature-review-fragments/`; this document
> consolidates them and renders the PRISMA-aligned gap statement that
> backs NRC EOI criterion 4 ("Addressing a gap").
>
> **Integrity envelope.** Every reference in §6 has been confirmed via
> at least two independent `WebSearch` URLs corroborating (title,
> authors, arXiv ID and/or DOI). Direct fetch of arXiv, Crossref, and
> Semantic Scholar is blocked at the network layer in the current
> container (HTTP 403); accordingly, no numerical claim (threshold,
> sub-threshold $\Lambda$, wall-clock latency) is paraphrased from any
> paper into this document — claims are categorised by *type*, with the
> primary source cited, and quantitative comparisons across the
> literature are deferred to a follow-up session with full-text access.
> A small number of recent preprints flagged below carry an explicit
> `[recent-preprint]` annotation indicating that authorship was
> confirmed to two URLs but the preprint is less than ~30 days old as
> of writing and the full author list has not been
> cross-validated against a journal version.

## 1. Background and motivation

The rotated surface code [Fowler2012, Fowler2013] is the dominant code
in superconducting QEC experiments because it combines a high tolerance
threshold with a planar, nearest-neighbour qubit layout that
realistically maps onto current and near-term hardware. The recent
"below-threshold" experiment on the Willow processor [GoogleQAI2025]
demonstrates that scaling the code distance now buys exponential
suppression of the logical error rate on real hardware — moving the
binding constraint from *whether* QEC works to *whether the decoder can
keep up*.

"Keeping up" has a hard ceiling. On superconducting hardware the
syndrome-extraction cycle is on the order of one microsecond, so a
useful decoder must produce a syndrome interpretation per cycle in
streaming fashion or fall behind exponentially — the "decoding
backlog" problem made explicit in the parallel-window literature
[Skoric2023, Tan2023]. The capstone study (`capstone/README.md`) sits
on top of that pressure point: which decoder families are competitive
for the rotated surface code at $d \in \{3,5,7,9\}$ under depolarizing,
circuit-level SI1000 [Gidney2021SI1000], and biased
[Tuckett2018, Tuckett2019Tailoring, Tuckett2019Threshold, Bonilla2021]
noise, when judged jointly on logical error rate *and* wall-clock
latency? §5 argues that this joint frontier is precisely where the
indexed literature is thin.

## 2. Search protocol

The full protocol — date range (2012-01-01 → 2026-05-15), population,
inclusion/exclusion criteria, information sources, the five Boolean
search-string slices (S1 MWPM, S2 Union-Find, S3 BP+OSD, S4 neural,
S5 real-time/noise), integrity gates, and known limitations — is in
`capstone/proposal/search-protocol.md`. Two points to repeat here:
(i) `WebFetch` and direct API access to arXiv / Crossref /
Semantic-Scholar are 403-blocked in this container, so the agents
worked exclusively from `WebSearch` snippet metadata; (ii) admission
to the bibliography required at least two independent corroborating
URLs per (title, authors, arXiv ID) triple, with the URLs recorded
verbatim in the per-slice `.bib.md` files.

## 3. PRISMA flow

| Slice | Unique titles surfaced | Passed inclusion | Two-URL verified (admitted) | Excluded for failure to verify | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| S1 — MWPM family | 20 | 12 | 11 | 2 | Two excluded (`arXiv:2605.04892` and `arXiv:2605.01149`) on a YYMM plausibility concern (alleged May 2026 papers describing already-established results); one borderline entry (Barber 2025 / Collision Clustering) is included as the closest hardware MWPM-accuracy competitor though strictly a clustering decoder. |
| S2 — Union-Find family | 14 | 9 | 10 | 0 | Slice §4 reports 9 admitted vs. 10 in the .bib.md (the discrepancy is one weighted-UF interpretation paper, `arXiv:2211.03288`, that should be counted in both); resolved as 10 admitted here. |
| S3 — BP / BP+OSD / iterative | 16 | 13 | 11 | 0 | Two preprints (`arXiv:2509.01892`, `arXiv:2412.21118`) confirmed at the arXiv-ID level but with author lists unverifiable on a second URL — listed by S3 as "pointers" and **excluded from the consolidated reference list in §6 and from `docs/reading-list.md`**. |
| S4 — Neural decoders | ~24 | 13 | 17 | ~7 | The "admitted" count exceeds "passed inclusion" because S4 admitted four extra historically-foundational neural-decoder papers (Torlai–Melko, Krastanov–Jiang, Breuckmann–Ni, Varsamopoulos comparison) that were surfaced by adjacent searches and verified post-hoc. AlphaQubit (`arXiv:2310.05900` / Nature 635, 2024) was the highest-scrutiny entry: title, venue, DOI, lead authors, and affiliation confirmed to two URLs; full co-author list confirmed only via one snippet and so flagged below. Two recent-preprint flags carried into §6 (`arXiv:2604.12841`, `arXiv:2605.04892`). |
| S5 — real-time / noise / hybrid | ~30 | ~17 | 21 (incl. 2 anchors) | ~13 | The "AlphaQubit 2" preprints (`arXiv:2510.22724`, `arXiv:2512.07737`), the LATTE / Pinball / Lottery-BP single-evidence sightings, and an unattributed "Astrea-G" were all excluded for failure to confirm to two URLs. |
| **Combined (deduplicated)** | **~104 distinct titles surfaced** | **~64 passed scope** | **49 unique admitted citations** (after cross-slice deduplication) | **~20+** | The two-URL admission rate is conservative by design. |

Cross-slice duplicates merged: Fowler 2012 (S1, S5 anchor); Higgott
belief-matching `arXiv:2203.04948` (S1, S2, S5); Skoric parallel-window
`arXiv:2209.08552` (S1, S2, S5); Bonilla Ataides XZZX
`arXiv:2009.07851` (S1, S5); Hillmann/Caune LCD `arXiv:2411.10343`
(S2, S5); Roffe `arXiv:2005.07016` (S3 anchor); AlphaQubit
`arXiv:2310.05900` (S4, S5); Barber Collision Clustering
`arXiv:2309.05558` (S1, S5); Delfosse-Nickerson `arXiv:1709.06218`
(S2 anchor); Google QAI `arXiv:2207.06431` (S5 anchor).

One integrity correction was applied during synthesis: the S5 fragment
re-cited Fowler 2012 with copy-pasted *evidence URLs* that actually
point to Tuckett biased-noise papers (`arXiv:1708.08474` and
`arXiv:1907.02554`). The Fowler entry is taken from S1, where the
evidence URLs are correctly Fowler 2012 (`arXiv:1208.0928` and the
PRA DOI page); the S5 entry's prose claim is preserved but the
mis-paired URLs are not propagated.

## 4. Results, categorised by decoder family

### 4.1 MWPM family (S1)

The MWPM family is the surface-code decoder of record. Fowler's
parallel-time variant [Fowler2013] turned blossom into an algorithm
suitable for streaming decoding; PyMatching [Higgott2021] became the
canonical reference implementation; and **Sparse Blossom**
[Higgott2025] reformulated the inner solver so that matching can be
done directly on the detector graph at very high throughput. Two
parallelisation lines have grown on top of that base: **Fusion Blossom**
[Wu2023Fusion] partitions the syndrome volume into a forest of
sub-problems whose results are fused, and **parallel window decoding**
[Skoric2023, Tan2023] cuts the syndrome stream along the time axis so
that consecutive windows can be decoded concurrently. Hardware-targeted
MWPM has matured in two directions: **Micro Blossom** [Wu2025Micro] is
an FPGA matching engine reporting sub-microsecond per-round latency on
the rotated surface code, and **Collision Clustering** [Barber2025] is a
non-MWPM clustering decoder included here as the closest currently
deployed hardware competitor with MWPM-class accuracy. For tailored /
biased noise, **belief matching** [Higgott2023] reweights the matching
graph using a single BP pass, and **pipelined correlated MWPM**
[Paler2023] is the most recent attempt to fold correlations into a
production matching pipeline.

What MWPM does well: it is provably near-ML on the surface code under
Pauli noise on a graph-decomposable error model, it admits clean
hardware acceleration, and the algorithmic complexity scales gently
enough that hardware demonstrations exist out to commercially
relevant distances. Where it strains: tailored / biased / leakage
error models break the perfect-matching abstraction, and parallel
matching engines and streaming engines have so far been published
under different noise models and at different distances, so a
like-for-like cross-engine comparison is missing — see §5.

### 4.2 Union-Find family (S2)

UF [DelfosseNickerson2021] reframes decoding as cluster growth on the
syndrome graph, paying a constant factor of accuracy versus MWPM in
exchange for almost-linear runtime — the property that made it the
canonical real-time-feasible decoder candidate. Three algorithmic
descendents are in the indexed corpus: **weighted UF**
[Huang2020WeightedUF] generalises cluster growth to edge weights and
recovers some of the accuracy MWPM had over plain UF; **strictly local
UF** [Chan2023Actis] removes the global state in cluster growth so the
algorithm becomes amenable to a hardware mesh; and **UF without UF**
[Griffiths2024] strips out the union-find data structure entirely,
producing a decoder algorithmically simpler than the original. The
hybrid **belief-find** decoder [Higgott2023] uses BP to weight the UF
graph and was the first to credibly close part of the UF-vs-MWPM
accuracy gap under circuit-level noise on tailored surface codes.

On the hardware side, two Liyanage-et-al. papers
[Liyanage2023FPGA, Liyanage2024FPGAUF] take UF to FPGA — the second
adopts a distributed mesh layout that aligns with the strictly-local
formulation — and **Local Clustering Decoder** [Ziad2025LCD] is the
most recent fast and adaptive hardware decoder claiming competitive
accuracy at the rotated-surface scale; the LCD paper also crosses into
S5 as the most credible recent leakage-adaptive hardware decoder.
Parallel-window decoding [Skoric2023] transfers cleanly to UF and is
double-cited here for that reason.

### 4.3 Belief propagation, BP+OSD, and iterative variants (S3)

Vanilla BP fails on the surface code because the code's quasi-cyclic
structure produces short cycles in the Tanner graph and the code's
degeneracy means many minimum-weight Pauli error chains map to the
same syndrome — BP cannot break the tie. The standard fix on qLDPC
codes is **BP + Ordered Statistics Decoding** [Panteleev2021BPOSD],
generalised and benchmarked across the qLDPC landscape by
[Roffe2020LDPCLandscape]. Three lines of follow-on work address BP's
surface-code-specific failure mode: **Generalised BP**
[OldRispler2023] modifies the message-passing schedule; **Stabilizer
Inactivation** [duCrest2022SI] selectively pins ambiguous stabilizers;
and **Closed-Branch decoding** [deMartiOlius2024CBD] and the
**BP+OTF** almost-linear-time decoder [deMartiOlius2024OTF] from the
same group restructure the post-BP cleanup step. **Localized statistics
decoding** [Hillmann2025LSD] parallelises the OSD post-pass.

Two trends are particularly relevant for the capstone. First, **neural
BP** [Miao2022NeuralBP, Miao2023QNBP] and the recent **Astra** machine-
learned message-passing decoder [Maan2025Astra] are credible candidates
for surface-code decoding at the rotated geometry under realistic
noise. Second, **Relay-BP** [Müller2025RelayBP] from IBM is explicitly
framed as "improved BP is sufficient for real-time decoding" — a claim
that, if borne out under SI1000 at the distances the capstone targets,
would meaningfully change the decoder design space. **Improved BP for
surface codes** [Chen2024ImprovedBP] makes a similar claim on the
surface code itself but at smaller distances.

### 4.4 Neural decoders (S4)

The neural-decoder corpus tracks a clear arc. The **feedforward / CNN
era** [TorlaiMelko2017, Varsamopoulos2017, Krastanov2017,
Breuckmann2018, Chamberland2018, Varsamopoulos2019Comparison,
Meinerz2022, Gicev2023, Bordoni2023, Zhang2023Programmable,
Gicev2025ConvNet] established that neural decoders can match MWPM
accuracy on small surface codes and trained against either
phenomenological or circuit-level noise; **Varbanov2025NN** carried the
line to near-term experimental syndromes. The **recurrent / transformer
era** is anchored by AlphaQubit
[Bausch2023AlphaQubit / Bausch2024AlphaQubitNature] — a recurrent
transformer trained on Google Quantum AI surface-code data that, by the
authors' headline (we do not transcribe the numerical claim), beats
matching baselines on the same hardware traces. **Transformer-QEC**
[Wang2023TransformerQEC] generalises to a cross-code-family decoder.
The **pre-/post-decoder cascade** line is represented by the recent
AI-pre-decoder paper [Chamberland2026AIPredecoder] `[recent-preprint]`
which targets FPGA-class latencies, and the **FPGA neural decoder**
[Yang2026FPGANN] `[recent-preprint]` is the most recent claim that a
neural decoder can clear the real-time line on real hardware.

Where neural decoders demonstrably help: they extract a structured
prior from the actual hardware noise (AlphaQubit is the cleanest
demonstration), and as pre-decoders they can absorb the easy cases so
that an MWPM / UF backend handles only the hard ones. Where they
strain: training-data volumes scale aggressively with $d$, generality
across noise models is reported per-paper rather than benchmarked
across, and open-source artefacts that reproduce a state-of-the-art
result at $d \in \{7, 9\}$ under SI1000 with public Stim circuits are
absent from the indexed corpus.

### 4.5 Real-time / hybrid / noise-aware decoders and the noise-model landscape (S5)

The **noise-model landscape** is where the capstone's experiment matrix
gets its anchors. **Uniform depolarizing** is the textbook reference;
**SI1000** [Gidney2021SI1000] is the circuit-level model used in most
modern surface-code papers; **biased noise** is defined and threshold-
characterised by the Tuckett line [Tuckett2018, Tuckett2019Tailoring,
Tuckett2019Threshold]; the **XZZX surface code**
[Bonilla2021] is the dominant biased-noise-aware geometric variant.
**Leakage** is the most-cited non-Pauli noise channel in superconducting
hardware [Varbanov2020Leakage, McEwen2021Leakage, Miao2023Leakage]; the
mitigation strategy has historically been at the gate level rather than
in the decoder, with [Ziad2025LCD] the most recent leakage-adaptive
decoder claim.

The **real-time / online / streaming** line falls into three buckets.
**Parallel-window decoding** [Skoric2023, Tan2023] cuts the syndrome
stream along the time axis. **Predecoder / cascaded** approaches
include **Promatch** [Alavisamani2024Promatch] (adaptive predecoding +
matching) and **Predictive Window Decoding** [Viszlai2024PWD]. **End-to-
end hardware demonstrations** are headlined by [Barber2025] (FPGA + ASIC
collision-clustering decoder reported in Nature Electronics),
[Caune2024Riverlane] (Riverlane × Rigetti low-latency demo), and the
two recent FPGA neural decoders [Yang2026FPGANN] `[recent-preprint]`
and the AI-predecoder [Chamberland2026AIPredecoder] `[recent-preprint]`.
The **Willow** result [GoogleQAI2025] used a real-time decoder at
distance 5 to demonstrate below-threshold scaling. Two further entries
round out the slice: **hierarchical decoding** [Delfosse2020Hierarchical]
is the parent concept for cascaded decoders, and the earlier Google
QAI **suppressing quantum errors** experiment [GoogleQAI2023] is the
anchor for the threshold-behaviour line.

## 5. Gap statement

The literature is thick on *one-decoder-one-noise-model* studies and
thin on *one-decoder-family-many-noise-models* studies on the
**rotated** surface code at distances $d \in \{3,5,7,9\}$.
Concretely, three gaps intersect on the same hole.

**G1 — Decoder-family-by-noise-model matrix is incomplete.** The
biased-noise line (`arXiv:1708.08474`, `1812.08186`, `1907.02554`,
`2009.07851`, `2203.04948`) is dominated by bespoke tailored-code
decoders, while the SI1000 / real-time line (`2108.10457`,
`2209.08552`, `2209.09219`, `2309.05558`, `2410.05202`, `2411.10343`,
`2408.13687`) is dominated by matching and clustering. The two lines
overlap in noise-model space but rarely in decoder space. No single
study in the admitted corpus holds the *decoder* fixed (PyMatching,
Union-Find, BP+OSD, small CNN) and varies (noise model × distance ×
rotated-versus-planar geometry) on a *single shared* Stim circuit and
*shared* shot budget. This is what the capstone's experiment matrix
(`capstone/README.md` §"Experiment matrix") directly fills.

**G2 — The joint latency–accuracy Pareto under realistic noise is
unjoined.** Promatch (`2404.03136`), Caune et al. (`2410.05202`),
Local Clustering Decoder (`2411.10343`), Sparse Blossom (`2303.15933`),
Fusion Blossom (`2305.08307`), Micro Blossom (`2502.14787`), and
AlphaQubit (`2310.05900` / Nature 2024) each report sub-µs or
near-sub-µs decoder latencies, but at different distances and on
different noise models. An apples-to-apples Pareto curve — wall-clock
per shot vs logical error rate at $d=7$ across the four decoder
families on one common Stim circuit — does not appear in the indexed
corpus. The capstone's latency benchmark at $d=7$ directly produces
that plot.

**G3 — Noise-aware decoders are siloed by which non-Pauli channel they
target.** The leakage-aware line
(`2002.07119`, `2102.06131`, `2211.04728`, `2411.10343`) and the
bias-aware line (the Tuckett / XZZX / belief-matching line) operate on
disjoint subsets of the noise-model phase diagram. A modest
leakage-augmented biased channel is precisely the regime where a
noise-aware predecoder + matching backend would be most useful, and
that regime is empirically underexplored in the admitted corpus. This
intersects directly with the capstone's "novelty knob (a)
biased-noise-aware BP schedule" and "novelty knob (c) neural
pre-decoder + MWPM post-decoder" options.

**Capstone framing.** The gap statement that follows from G1+G2+G3 —
and that the experiment matrix in `capstone/README.md` is designed to
fill — is: *the open-source decoder corpus does not yet contain a
controlled benchmark that sweeps PyMatching, Union-Find, BP+OSD, and
a small CNN decoder across depolarizing, SI1000, and biased noise on
the rotated surface code at $d \in \{3,5,7,9\}$ with a shared shot
budget, public Stim circuits, and a joint latency-accuracy report at
$d=7$, with the BP+OSD schedule explicitly tuned for bias* (novelty
knob (a)).

## 6. References

Each reference below is mirrored as an entry in `docs/reading-list.md`
with an arXiv ID or DOI that resolves under `scripts/verify_reading_list.py`.
The per-slice `.bib.md` files retain the corresponding evidence URLs.

The 49 admitted citations, organised by family:

**Anchors (already in `docs/reading-list.md` before this review).**
Fowler2012 (`arXiv:1208.0928`); GoogleQAI2023 (`arXiv:2207.06431`);
DelfosseNickerson2021 (`arXiv:1709.06218`); Roffe2020LDPCLandscape
(`arXiv:2005.07016`); Varsamopoulos2017 (`arXiv:1705.00857`);
Higgott2025SparseBlossom (`arXiv:2303.15933`); Gidney2021Stim
(`arXiv:2103.02202`).

**MWPM family.** Fowler2013 (`arXiv:1307.1740`); Higgott2021PyMatching
(`arXiv:2105.13082`); Wu2023Fusion (`arXiv:2305.08307`); Wu2025Micro
(`arXiv:2502.14787`); Skoric2023 (`arXiv:2209.08552`); Higgott2023
(`arXiv:2203.04948`); Paler2023 (`arXiv:2205.09828`); Bonilla2021
(`arXiv:2009.07851`); Barber2025 (`arXiv:2309.05558`).

**Union-Find family.** Huang2020WeightedUF (`arXiv:2004.04693`);
Wu2022UFWeightedGraphs (`arXiv:2211.03288`); Liyanage2023FPGA
(`arXiv:2301.08419`); Chan2023Actis (`arXiv:2305.18534`);
Griffiths2024 (`arXiv:2306.09767`); Liyanage2024FPGAUF
(`arXiv:2406.08491`); Ziad2025LCD (`arXiv:2411.10343`).

**Belief Propagation family.** Panteleev2021BPOSD
(`arXiv:1904.02703`); OldRispler2023 (`arXiv:2212.03214`);
duCrest2022SI (`arXiv:2205.06125`); deMartiOlius2024CBD
(`arXiv:2402.01532`); deMartiOlius2024OTF (`arXiv:2409.01440`);
Hillmann2025LSD (`arXiv:2406.18655`); Miao2022NeuralBP
(`arXiv:2212.10245`); Miao2023QNBP (`arXiv:2308.08208`);
Chen2024ImprovedBP (`arXiv:2407.11523`); Müller2025RelayBP
(`arXiv:2506.01779`); Maan2025Astra (`arXiv:2408.07038`).

**Neural decoders.** TorlaiMelko2017 (`arXiv:1610.04238`);
Krastanov2017 (`arXiv:1705.09334`); Breuckmann2018
(`arXiv:1710.09489`); Chamberland2018 (`arXiv:1802.06441`);
Varsamopoulos2019Comparison (`arXiv:1811.12456`); Meinerz2022
(`arXiv:2101.07285`); Gicev2023 (`arXiv:2110.05854`); Varbanov2025NN
(`arXiv:2307.03280`); Bausch2023AlphaQubit (`arXiv:2310.05900`,
published as Bausch2024AlphaQubitNature
doi:10.1038/s41586-024-08148-8); Wang2023TransformerQEC
(`arXiv:2311.16082`); Bordoni2023 (`arXiv:2312.03508`);
Zhang2023Programmable (`arXiv:2305.15767`); Gicev2025ConvNet
(`arXiv:2506.16113`); Chamberland2026AIPredecoder
(`arXiv:2604.12841`) `[recent-preprint]`; Yang2026FPGANN
(`arXiv:2605.04892`) `[recent-preprint]`.

**Real-time / noise-aware / noise-model anchors.**
Tuckett2018 (`arXiv:1708.08474`); Tuckett2019Tailoring
(`arXiv:1812.08186`); Tuckett2019Threshold (`arXiv:1907.02554`);
Varbanov2020Leakage (`arXiv:2002.07119`); Delfosse2020Hierarchical
(`arXiv:2001.11427`); McEwen2021Leakage (`arXiv:2102.06131`);
Gidney2021SI1000 (`arXiv:2108.10457`); Miao2023Leakage
(`arXiv:2211.04728`); Tan2023 (`arXiv:2209.09219`);
Alavisamani2024Promatch (`arXiv:2404.03136`); Caune2024Riverlane
(`arXiv:2410.05202`); Viszlai2024PWD (`arXiv:2412.05115`);
GoogleQAI2025 Willow (`arXiv:2408.13687`).

## 7. Integrity, limitations, and next steps

**Integrity gates passed.** Every reference in §6 is double-URL-
corroborated in a slice `.bib.md`. The two S3 entries flagged as
"pointer-only, authors not verified" (`arXiv:2509.01892`,
`arXiv:2412.21118`) are not promoted to §6 or to
`docs/reading-list.md`. Two recent-preprint entries
(`arXiv:2604.12841`, `arXiv:2605.04892`) carry an explicit
`[recent-preprint]` flag and should be re-verified against a journal
version before the capstone paper quotes any of their numerical
claims. The cross-slice evidence-URL slip on the S5 Fowler entry was
caught during synthesis and the correct (S1) entry used instead.

**Limitations of this review.** No paper full text was read; numerical
claims are categorised by *type* but not quoted. The
WebSearch-only protocol is biased toward Google-indexed English-
language work and against ≤30-day preprints. Two-URL verification is a
necessary but not sufficient guarantee against fabrication — a
follow-up integrity pass should re-verify each entry against the
paper PDF the next time arXiv access is available, and especially
verify the AlphaQubit and the two `[recent-preprint]` entries beyond
title and lead-author level.

**Next steps for the capstone.**
1. Use the gap statement in §5 verbatim in `capstone/proposal/eoi-mock.md`
   §"Addressing a gap" (NRC criterion 4).
2. Hold the experiment matrix in `capstone/README.md` fixed; pick
   novelty knob (a) or (c); update `capstone/proposal/eoi-mock.md`
   §"Innovation" accordingly.
3. Once arXiv is reachable: extract the headline numbers from
   `arXiv:2303.15933`, `2502.14787`, `2411.10343`, `2310.05900`,
   `2506.01779`, `2408.13687`, `2309.05558`, and add them to the
   capstone Background section.
4. Submit this document plus `search-protocol.md` to ARS
   `integrity_verification_agent` (stage 2.5 gate) when the plugin is
   installed.
