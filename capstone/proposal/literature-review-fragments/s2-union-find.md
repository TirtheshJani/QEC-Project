# S2 — Union-Find decoder family

*PRISMA slice for the rotated surface code literature review. Companion
bibliography: `s2-union-find.bib.md`. Search strings, inclusion criteria,
and integrity rules are defined in `capstone/proposal/search-protocol.md`.
This slice does not paraphrase numerical claims from papers that were not
read in full; threshold / latency figures appear only where the value (or
its absence) was reported in the search-result snippet, and are flagged
accordingly.*

## 1. Framing

The Union-Find (UF) decoder is the canonical "fast, near-MWPM-accurate"
decoder for topological codes. Conceptually it replaces minimum-weight
perfect matching with a two-phase procedure: a **cluster-growth** phase,
in which connected components seeded on non-trivial syndrome vertices
expand outward through the decoding graph until every cluster contains an
even number of defects, followed by a **peeling** phase that walks a
spanning tree of each cluster to produce a Pauli correction. Because the
disjoint-set ("union–find") data structure resolves cluster merges in
amortised inverse-Ackermann time, the overall worst-case complexity is
almost linear in the number of physical qubits — *O(nα(n))* in the
foundational analysis (Delfosse & Nickerson). That complexity, together
with very small per-qubit constants, is why UF is repeatedly cited as the
leading candidate decoder for **real-time** syndrome processing on
superconducting hardware (target cycle ~1 µs), where MWPM-class
algorithms struggle to keep up at large code distances. The trade-off
that this slice tracks is the gap between UF's speed and its (slightly
lower) accuracy versus MWPM, and how subsequent work — weighted variants,
parallel/streaming architectures, and FPGA/ASIC implementations — has
closed or repositioned that gap.

## 2. Verified work

### 2a. Delfosse–Nickerson original

Delfosse & Nickerson's *Almost-linear time decoding algorithm for
topological codes* (arXiv:1709.06218, published in *Quantum* 5, 595,
2021) is the foundational reference and is already the known-good anchor
in `docs/reading-list.md`. Confirmation searches reproduce the
arXiv ID, the journal-of-record (Quantum, December 2021 issue), and the
DOI 10.22331/q-2021-12-02-595. The paper introduces the UF decoder for
2D topological codes (including the surface code), handles combined
Pauli + erasure noise, and gives the *O(nα(n))* complexity result; the
search-result snippet quotes a 9.9% code-capacity threshold for the 2D
toric code under perfect syndromes and 2.6% under faulty measurements,
but those numbers should be re-extracted from the PDF before they are
cited in the capstone paper.

### 2b. Parallel / streaming / hardware UF

Three works form the core of this sub-cell.

**Liyanage, Wu, Deters, Zhong**, *Scalable Quantum Error Correction for
Surface Codes using FPGA* (arXiv:2301.08419, ISCA-class venue, 2023), is
the first FPGA realisation of a **distributed** UF decoder. The authors
introduce the **Helios** tree-grid architecture and report that the
per-round decoding latency *decreases* with distance once enough parallel
resources are provided — a qualitative behaviour the snippet describes as
"a first" for a quantum decoder. Concrete latency figures appear in the
snippet ("11.5 ns per round at d = 21 under phenomenological noise") but
remain `[unverified]` until the PDF is read.

**Liyanage, Wu, Tagare, Zhong**, *FPGA-based Distributed Union-Find
Decoder for Surface Codes* (arXiv:2406.08491, IEEE Trans. on Quantum
Eng. 5, art. 7271, 2024) extends and journal-formalises the Helios line,
again with claimed sublinear-in-*d* decoding latency given *O(d³)*
parallel resources.

**Skoric, Browne, Barnes, Gillespie, Campbell**, *Parallel window
decoding enables scalable fault tolerant quantum computation*
(arXiv:2209.08552; Nature Communications 14, 7040, 2023) is
decoder-family-agnostic but explicitly targets UF (and MWPM) as the
inner solver: it shows that a sliding-/sandwich-window scheme lets an
inner decoder run on independent time-slices in parallel, eliminating
the exponential backlog blow-up that otherwise defeats real-time
operation. We admit it here because it is the most-cited route to
**streaming** UF and is the architectural pattern most current
real-time-decoder proposals reuse.

### 2c. Weighted-edge UF (biased / circuit-level noise)

**Huang, Newman, Brown**, *Fault-tolerant weighted union-find decoding
on the toric code* (arXiv:2004.04693; Phys. Rev. A 102, 012419, 2020),
is the canonical weighted-UF paper. It introduces edge weights derived
from circuit-level noise statistics and benchmarks the resulting
decoder on the toric code under circuit-level depolarizing noise;
weighting closes much of the threshold gap to weighted MWPM while
preserving the near-linear-time complexity (specific numbers
`[unverified]`).

**Wu, Liyanage, Zhong**, *An interpretation of Union-Find Decoder on
Weighted Graphs* (arXiv:2211.03288, 2022), reformulates UF as a
weighted-graph algorithm and applies it to the XZZX surface code under
biased noise; the snippet asserts UF accuracy equals MWPM accuracy in
the infinite-bias, perfect-measurement limit — a useful theoretical
anchor for the slice 5 (biased-noise) discussion.

**Higgott, Bohdanowicz, Kubica, Flammia, Campbell**, *Improved decoding
of circuit noise and fragile boundaries of tailored surface codes*
(arXiv:2203.04948; Phys. Rev. X 13, 031007, 2023) introduces
**belief-find**, a hybrid in which a BP pre-pass re-weights the UF
matching graph before the standard cluster-growth + peeling pipeline,
narrowing the accuracy gap to weighted MWPM under circuit-level noise.
This paper sits at the S2/S3 boundary; we admit it here because its
back-end is a weighted UF.

### 2d. FPGA / ASIC implementations and locality

Two further hardware-flavoured papers are admitted.

**Chan, Benjamin**, *Actis: A Strictly Local Union–Find Decoder*
(arXiv:2305.18534; *Quantum* 7, 1183, 2023) studies a strictly
nearest-neighbour-local variant of UF — every cluster operation acts
only on a constant-size neighbourhood — which is the locality regime
required by superconducting-control ASICs.

**Ziad, Zalawadiya, Topal, Camps, Gehér, Stafford, Turner** (Riverlane),
*Local Clustering Decoder as a fast and adaptive hardware decoder for
the surface code* (arXiv:2411.10343; Nature Communications, 2025) is an
adaptive, FPGA-implemented descendant of UF (the "local clustering"
family) that also includes runtime leakage-aware adaptivity — directly
relevant to NRC criterion-1 noise modelling.

**Griffiths, Browne**, *Union-find quantum decoding without union-find*
(arXiv:2306.09767; Phys. Rev. Research 6, 013154, 2024) is an
*algorithmic* hardware paper rather than a chip paper: it shows the
disjoint-set structure is under-utilised at scale and proposes
simplifications that yield a linear-time worst case, which matters when
budgeting FPGA logic.

## 3. UF vs MWPM trade-off

Across the admitted papers, a consistent picture emerges in the search
snippets (numbers not paraphrased): unweighted UF gives up some threshold
relative to MWPM but with significantly better worst-case scaling and a
much smaller hardware footprint, weighted UF closes most of the
remaining threshold gap, and parallel / hardware UF wins decisively on
latency at every distance studied. Where the literature draws the line
depends on the metric: for **threshold** alone, weighted-MWPM (Higgott)
and BP+MWPM still lead; for **latency under a 1 µs cycle**, UF-family
hardware implementations are the only published designs that have been
demonstrated to keep up at *d ≥ 17* (Helios) — albeit under
phenomenological, not full circuit-level, noise.

## 4. PRISMA mini-flow (S2)

- Unique titles surfaced across the three S2 search strings: **14**.
- Excluded as out-of-scope (non-UF, e.g. LILLIPUT lookup-table,
  Roffe et al. BP+OSD review hits, color-code-only UF variants, neural
  predecoders surfaced as side hits): **5**.
- Excluded for failure to confirm via a second independent URL
  (none — all candidates that passed the relevance filter also passed
  the two-URL confirmation step): **0**.
- Admitted to this slice's bib: **9**.
- Of these, **9** have arXiv IDs confirmed by two independent search-
  result URLs; **6** additionally have a confirmed journal DOI or
  journal-of-record (the remaining three are arXiv-only at time of
  search and are marked accordingly in the bib).

## 5. Open gaps this slice sees

The UF literature is rich on **algorithmic** variants (weighted,
strictly-local, peeling-free) and on **FPGA prototypes** at small-to-
medium *d*, but is conspicuously thin on **end-to-end benchmarks** of
the *same* UF variant across the noise-model axis our protocol cares
about — uniform depolarizing, SI1000 circuit-level, biased
(Z-bias η ≥ 30) — at the rotated-surface-code distances *d ∈ {3, 5, 7,
9}*. Most parallel/FPGA UF papers report only one noise model
(typically phenomenological), and most weighted-UF papers report only
toric- or XZZX-code geometry, not rotated. A capstone that holds the
decoder fixed (UF, MWPM, BP+OSD, neural) and varies (noise model ×
distance × rotated geometry) on a common Stim circuit therefore lands
squarely in an under-occupied region of this slice's matrix — useful
material for NRC criterion 4.
