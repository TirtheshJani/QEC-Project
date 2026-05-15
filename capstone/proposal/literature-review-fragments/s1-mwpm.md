# S1 — MWPM family (slice fragment)

*Slice of the PRISMA-aligned decoder literature review backing the
capstone (`capstone/proposal/literature-review.md`). Protocol:
`capstone/proposal/search-protocol.md`. This fragment covers
minimum-weight perfect matching (MWPM) and its hardware/algorithmic
descendants only; Union-Find, BP/OSD, neural, and predecoder families
are covered by sibling slices.*

## 1. Framing — where MWPM sits

The rotated surface code's stabilizer measurements produce **detection
events** which, under independent Pauli noise, come in pairs at the
endpoints of each error chain. Decoding therefore reduces to building a
**detector graph** whose vertices are detection events (plus virtual
boundary nodes) and whose edges are weighted by $-\log(p_e/(1-p_e))$,
where $p_e$ is the probability of the elementary fault that flips that
edge. The most likely error consistent with the syndrome is the
**minimum-weight perfect matching** of that graph. For depolarising
Pauli noise on the surface code, MWPM with edge weights derived from the
circuit error model is provably near-maximum-likelihood (it is exact for
graph-like noise where every fault triggers at most two detection events,
and is a good approximation otherwise). This near-ML quality, plus
polynomial-time solvability via Edmonds' blossom algorithm, is why MWPM
has been the workhorse surface-code decoder since Fowler et al.'s 2012
overview paper [Fowler2012] and remains the accuracy yardstick that
faster decoders are benchmarked against.

## 2. Sub-families

### 2a. Classical blossom origins applied to QEC (Fowler-style MWPM)

The first systematic treatment of MWPM as a surface-code decoder is
Fowler, Mariantoni, Martinis, Cleland (2012) [Fowler2012], which
formulates the syndrome-matching problem and reports threshold and
overhead estimates for fault-tolerant surface-code computation; this is
the canonical reference for the MWPM/surface-code pairing. Fowler later
proved that, under reasonable locality and rate assumptions, MWPM on the
syndrome graph admits an **average-O(1) parallel time** implementation
[Fowler2013], establishing in principle that matching is not a barrier
to real-time decoding. These foundational papers fix the algorithmic
template — weighted graph from a circuit error model, decoded by an
exact (or near-exact) matching solver — that every subsequent MWPM
variant inherits.

### 2b. PyMatching and Sparse Blossom

PyMatching v1 [Higgott2021] was the first widely used open-source MWPM
library targeted at the surface code; it implemented a "local matching"
variant restricting each defect to be matched within a bounded
neighbourhood, gaining several orders of magnitude over the previous
Blossom V baseline at essentially unchanged logical accuracy.
PyMatching v2's core algorithm is **Sparse Blossom** [Higgott2025], a
reformulation of Edmonds' blossom that operates directly on the
(sparse) detector graph without all-to-all Dijkstra preprocessing. The
authors report that Sparse Blossom processes a distance-17 surface-code
round in under a microsecond per round on a single core at 0.1%
circuit-level depolarising noise (numerical claim attributed to the
paper; not independently verified in this slice). Sparse Blossom is the
de-facto MWPM accuracy/throughput baseline our capstone benchmarks
against.

### 2c. Fusion Blossom and parallelisation

Wu and Zhong's **Fusion Blossom** [Wu2023Fusion] is parallel independent
work to Sparse Blossom: it constructs a tree-structured partition of the
detector graph, solves sub-problems on separate cores, then fuses them
exactly. The paper reports streaming/batched throughput targeting the
~1 MHz syndrome rate of superconducting qubits at distances up to ~33
(numerical claim attributed to the paper; not independently verified).
A complementary line is **parallel-window decoding** [Skoric2023], which
slices the temporal axis into overlapping windows decoded by independent
MWPM instances, removing the exponential backlog problem when serial
decoding cannot keep up. Together these papers establish that MWPM
*throughput*, not just *accuracy*, is now competitive with the hardware
syndrome rate when given enough classical compute.

### 2d. Hardware MWPM (FPGA/ASIC)

For the **latency** axis the relevant primary source is **Micro
Blossom** [Wu2025Micro] (Wu, Liyanage, Zhong), a heterogeneous FPGA/CPU
accelerator that the authors describe as the first publicly known
sub-microsecond exact MWPM decoder; reported average latency 0.8 μs at
distance 13 and physical error rate 0.1% (numerical claim attributed to
the paper; not independently verified). On the same axis but using a
*non-matching* hardware algorithm tuned to behave MWPM-like, Riverlane's
**Collision Clustering** decoder [Barber2025] (Nature Electronics) is
implemented on both FPGA and ASIC and demonstrated up to 881-qubit
(FPGA) / 1057-qubit (ASIC) surface codes; while not strictly MWPM, it
is benchmarked against MWPM accuracy and is the closest production-grade
hardware competitor. Both papers signal that the "MWPM can't run in
real time" objection of the early 2010s is no longer literally true.

### 2e. Weighted-edge MWPM under biased / circuit-level noise

Two strands matter here. **Belief-matching** [Higgott2023], from the
"Improved decoding of circuit noise / fragile boundaries of tailored
surface codes" paper, runs belief propagation over the hyperedge fault
model to *reweight* the detector graph before handing it to MWPM (or
Union-Find), and the paper reports an improved circuit-level threshold
(specific numerical value not extracted in this slice — paper not fetched
in container). The **XZZX surface code** paper [Bonilla2021] is
primarily a code-design paper but its decoder *is* weighted MWPM applied
to a biased-noise-tailored stabilizer arrangement; it is included here
as the canonical worked example of weighted-edge MWPM extracting
suppression from biased noise. Both papers exemplify the modern pattern
"detector graph weights are not god-given — reweight them and matching
gets better." A separate noise-correlation-reweighting line is Paler &
Fowler's **pipelined correlated MWPM** [Paler2023], which factors
correlated-error reweighting into a pipeline stage compatible with
real-time MWPM.

## 3. What MWPM does well, where it strains

MWPM is the strongest available **graph-like** decoder for the surface
code under independent Pauli noise: it is near-ML, has near-optimal
threshold for depolarising and SI1000-type noise (when the detector
graph is properly weighted), and now has open-source single-core
implementations (Sparse Blossom) plus parallel (Fusion Blossom, parallel
windows) and FPGA (Micro Blossom) variants that meet the ~1 μs/round
target at moderate distances. Where it strains:

- **Hyperedge / non-graphlike fault models**: when single faults trigger
  more than two detection events (which is generic in circuit-level
  noise), pure MWPM is no longer ML. Belief-matching style reweighting
  closes part of this gap but adds a BP pre-pass.
- **Leakage and non-Pauli noise**: outside the scope of vanilla MWPM
  unless leakage is approximated as Pauli + erasure.
- **Latency at large distance**: even Micro Blossom is demonstrated at
  $d = 13$; how exact MWPM scales to $d \in \{21, 25\}$ at strict 1 μs
  budget is an open hardware question.
- **Streaming vs batched throughput**: Fusion Blossom and Sparse
  Blossom optimise different points on this curve, and which one wins
  depends on whether the QPU back-end is decode-then-act (streaming) or
  trace-collect-then-decode (batched).

## 4. PRISMA mini-flow for S1

- Unique titles surfaced by the 4 search strings: **20**.
- Passing scope filter (decoder paper on planar/rotated surface code,
  MWPM family, ≥1 reported outcome metric, 2012–2026, English): **12**.
- Admitted with two-URL verification of (title, authors, arXiv ID or
  DOI): **11** (see `s1-mwpm.bib.md`). One borderline entry (Barber
  2025 / Collision Clustering) is included as the closest hardware
  MWPM-accuracy competitor though strictly not MWPM.
- Excluded: 1 hardware-but-Union-Find paper (Helios / Liyanage 2024 —
  belongs to S2); 2 review/survey papers (review on surface-code
  decoding algorithms; "Decoding algorithms for surface codes" Quantum
  2024); 3 non-MWPM hardware/algorithm results (Local Clustering
  Decoder, Relay-BP, FPGA-Distributed-Union-Find); 2 candidates that
  could not be confirmed to two independent URLs in this session (see
  report).

## 5. Open gaps THIS slice sees

Within MWPM specifically: (i) no publicly verified end-to-end **real-time
FPGA/ASIC MWPM benchmark** at $d \geq 17$ under *circuit-level* (not
phenomenological) SI1000 noise that quotes both threshold *and*
worst-case latency in the same table — Micro Blossom is the closest but
is at $d = 13$, Riverlane's Collision Clustering is at large $d$ but not
strictly MWPM; (ii) the weighted-edge / biased-noise MWPM literature
(XZZX, belief-matching) and the streaming MWPM literature (Sparse,
Fusion, parallel windows) have not been jointly benchmarked on the
*same* circuit-level noise model — a gap directly actionable by the
capstone study. Cross-slice synthesis with S2 (Union-Find) and S5
(predecoders, real-time) is deferred to the parent document.
