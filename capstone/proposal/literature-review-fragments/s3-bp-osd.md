# Slice S3 — Belief Propagation and BP-augmented decoders

**Scope.** Vanilla belief propagation (BP), BP+OSD, BP with stabilizer
inactivation (BP-SI), BP with ordered Tanner forest / closed-branch
post-processors, neural-BP, and recent "improved BP" variants (Relay-BP,
Momentum/AdaGrad-BP). Slice produced under the
`capstone/proposal/search-protocol.md` PRISMA protocol with `WebSearch`
as the only allowed retrieval channel; numerical claims from papers that
were not read in full are deliberately *not* paraphrased.

## 3.0 Framing

Belief propagation is the workhorse decoder of classical LDPC codes: a
sum-product message-passing algorithm on the Tanner graph that converges
to the MAP solution on tree-like factor graphs and works extremely well
on the long, sparse codes used in 5G and Wi-Fi. Carrying it across to
quantum stabilizer codes runs into two new obstacles. First, the Tanner
graphs of practical quantum LDPC (qLDPC) codes — and emphatically the
rotated surface code — are *not* tree-like: they contain short cycles by
construction. Second, and more damaging, stabilizer codes are
*degenerate*: distinct error patterns can have identical syndromes and
identical *logical effects*, so a unique-MAP-error objective is the
wrong target. On the surface code in particular, vanilla BP famously
fails to reach a below-threshold regime (Old and Rispler 2023 give a
clean modern statement of the failure mode and a remediation that
restores it).

The fix that turned BP from "fails on quantum codes" into "default
qLDPC decoder" is **post-processing**. When BP fails to converge to a
syndrome-consistent error, an outer routine resolves the residual
ambiguity by solving a small linear system on the columns BP found
least reliable. The original instance is BP + ordered statistics
decoding (BP+OSD), introduced for qLDPC by Panteleev and Kalachev
(2021, arXiv:1904.02703) and pushed into the community as a reusable
software tool by Roffe et al. (2020, arXiv:2005.07016). BP+OSD now
serves as the *de facto* baseline against which every new qLDPC decoder
is benchmarked, including in IBM's bivariate-bicycle work
(arXiv:2308.07915, already in `docs/reading-list.md`).

For the capstone, the surface code is the focus, but the BP family is
in scope for two reasons: (i) the experiment matrix uses BP+OSD as a
baseline (mainly for cross-checking and for any bivariate-bicycle side
runs); (ii) recent work argues that improved BP variants *are*
competitive with MWPM on the surface code under circuit-level noise —
a claim the capstone needs to evaluate on its own data, not paraphrase.

## 3a. Vanilla BP on stabilizer codes — historical note

The starting point for quantum BP is the binary or quaternary
sum-product algorithm run on the Tanner graph of the stabilizer
parity-check matrix. On 2D topological codes the algorithm cycles and
oscillates because of (a) the short cycles in the lattice and (b) the
degeneracy-induced symmetry in the messages: two equally likely
corrections differing by a stabilizer keep cancelling each other.
Old and Rispler (arXiv:2212.03214) document this failure mode for the
surface code and propose a *generalized BP* with an outer
re-initialization loop that recovers the sub-threshold regime known
from MWPM and stat-mech mappings. This paper is the most quotable
recent reference for "why naive BP fails on the surface code, and the
minimal fix".

## 3b. BP + OSD — the qLDPC default

OSD post-processing for classical LDPC error floors is due to Fossorier
and Lin (1990s); its translation to the quantum setting is
**Panteleev and Kalachev** (arXiv:1904.02703, Quantum 5, 585 (2021)).
The construction is: run BP for a fixed number of iterations; if the
output is not syndrome-consistent, sort qubits by BP-reported
reliability, take a most-reliable basis of the parity-check matrix,
and solve the remaining linear system to fix the syndrome. Tuneable
"OSD-w" variants exhaust low-weight combinations among the *least*
reliable bits for incremental accuracy gains.

**Roffe, White, Burton, Campbell** (arXiv:2005.07016) — already an
anchor in `docs/reading-list.md` — operationalized BP+OSD as a general
decoder for hypergraph product qLDPC codes and shipped the open-source
`bp_osd` / `ldpc` library that essentially every subsequent paper in
this slice uses for baselines. The paper reports thresholds across
hypergraph product, fixed-rate random, and "semi-topological" code
families (values not extracted in this slice; the paper is read in
full in a downstream session).

## 3c. Alternatives and improvements

Several lines of work address the two practical weaknesses of BP+OSD —
its super-linear OSD stage, and BP's own convergence pathologies on
degenerate codes.

- **BP + Stabilizer Inactivation (BP-SI).** du Crest, Mhalla, Savin
  (arXiv:2205.06125, ITW 2022). Inactivate a small set of qubits
  supporting a dual-code check, rerun MP outside that set, and solve a
  constant-size linear system on the inactivated qubits. The paper
  claims BP-SI outperforms BP-OSD across several qLDPC families at
  reduced complexity (numerical comparison not extracted here).

- **Closed-branch decoder.** deMarti iOlius and Etxezarreta Martinez
  (arXiv:2402.01532). Worst-case complexity stated as O(n·max_gr·max_br)
  with accuracy/speed tunable via the two limit parameters. Benchmarked
  on bivariate-bicycle codes against BP+OSD (similar accuracy at lower
  complexity for small distances; reported degradation at larger
  distances).

- **BP + ordered Tanner forest (BP+OTF).** Companion line of work from
  the same group (arXiv:2409.01440) proposing an almost-linear-time
  post-processor that prunes the decoding graph to a tree where BP is
  guaranteed to converge. Listed here as a BP+OSD alternative aimed
  squarely at circuit-level noise.

- **Localized Statistics Decoding (LSD).** Hillmann, Berent,
  Quintavalle, Eisert, Wille, Roffe (arXiv:2406.18655, Nat. Commun.
  16, 8214 (2025)). A parallelizable inversion post-processor that
  matches BP+OSD accuracy with sub-threshold runtime reductions.

- **Neural BP.** Miao, Schnerring, Li, Schmalen (arXiv:2212.10245,
  with quaternary extension arXiv:2308.08208). Learn the BP message
  weights end-to-end on an overcomplete redundant-row check matrix to
  attenuate the cycle and degeneracy problems. Targets qLDPC, not the
  surface code, but is the cleanest example of "learn the BP schedule".

- **Improved BP for real-time.** Müller, Alexander, Beverland, Bühler,
  Johnson, Maurer, Vandeth (arXiv:2506.01779; IBM). The
  Relay-BP decoder uses disordered, dynamically chained memory
  strengths to escape BP trapping sets and is reported to be
  comparable to MWPM on the surface code while outperforming
  BP+OSD+CS-10 on bivariate-bicycle codes (numbers not extracted
  here). Companion direction: Chen, Yi, Liang, Wang
  (arXiv:2407.11523) propose Momentum-BP / AdaGrad-BP / EWAInit-BP
  for the surface code without OSD post-processing.

- **Machine-learnt message passing.** Maan and Paler (arXiv:2408.07038,
  npj Quantum Information 11, 78 (2025)) train a graph neural network
  ("Astra") as a drop-in replacement for the BP stage and report
  threshold and logical-error-rate gains over BP+OSD on both surface
  and bivariate-bicycle codes when trained at small distances and
  extrapolated to larger ones (numbers not extracted).

## 3d. BP-family decoders on the rotated surface code

The competitiveness picture on the surface code has shifted in the last
two years. Three datapoints to anchor the gap statement:

1. **Old and Rispler (arXiv:2212.03214)** show that BP can be coaxed
   below threshold on the surface code with the right outer loop —
   refuting the older folklore "BP just doesn't work on the surface
   code".
2. **Chen et al. (arXiv:2407.11523)** report that Momentum-/AdaGrad-/
   EWAInit-BP, *without* OSD post-processing, achieve the highest
   accuracy among BP-only decoders on the surface code (specific
   thresholds not extracted in this slice).
3. **Müller et al. (arXiv:2506.01779)** claim Relay-BP is comparable
   to MWPM on the surface code under circuit-level noise while running
   in a regime compatible with real-time FPGA/ASIC implementation.

The structural appeal is that BP-family decoders are **inherently
parallel message-passing** and therefore map naturally to hardware,
whereas MWPM requires a global matching that is harder to pipeline.
Whether the accuracy claims hold against weighted-edge MWPM on
SI1000-style circuit-level noise at distance $d \geq 7$ is the open
question.

## 3.5 Accuracy / runtime trade-off

A consistent picture across the slice: BP itself is O(n) per
iteration and trivially parallel, but on its own it does not reach the
sub-threshold regime on the surface code. OSD post-processing is the
historical fix and the standard baseline but is super-linear (Gaussian
elimination on the most-reliable basis), which is the bottleneck for
real-time use. The 2022-2025 wave of work splits cleanly in two:
(a) replace OSD with a *cheaper* post-processor of comparable
accuracy (closed-branch, OTF, LSD, SI) — batched throughput goal; or
(b) fix BP itself so that no post-processor is needed (Relay-BP,
Momentum-BP family, Astra) — streaming-latency goal.

## 3.6 PRISMA mini-flow (this slice)

- Unique titles surfaced via the four S3 search strings + the optional
  BP-OTS / SI string: **16**.
- Excluded by scope (classical-only OSD/polar-code applications,
  reviews, surveys, talk abstracts, GitHub-only artifacts): **3**
  (`arXiv:2102.07994` polar codes; review papers at
  `arXiv:2307.14989` and the EPJQT FPGA-design review; `bp_osd` repo
  listed only as software).
- Excluded for inability to verify arXiv ID, authorship, or year via
  two independent URLs: **0** in this slice (all admitted entries
  passed second-search confirmation).
- Admitted to slice fragment with verified arXiv ID and two evidence
  URLs: **13**.
- Already in `docs/reading-list.md` (anchor, re-confirmed only):
  **1** (Roffe et al., arXiv:2005.07016).

## 3.7 Open gaps this slice sees

Two gaps are visible from titles, abstracts, and second-hand summaries
alone, and they are conservative because numerical claims were not
extracted in-container. (1) **Head-to-head BP-family vs MWPM on the
rotated surface code under SI1000 circuit-level noise** at distances
$d \in \{5,7,9\}$ is not, to this slice's knowledge, a single
controlled benchmark — Relay-BP, improved-BP, and Astra each report
"comparable to" or "better than" MWPM on surface codes but with
non-overlapping noise models, distance ranges, and matching baselines.
(2) **Joint latency–accuracy Pareto** for BP-family decoders on the
rotated surface code — many papers report one axis (threshold *or*
shots/s) but the published evidence base does not yet pin down where
on the $(\text{logical error}, \text{wall-clock})$ frontier each
sub-family sits at $\sim 1\,\mu s$ syndrome cycle. Both gaps line up
with the capstone experiment matrix and are appropriate evidence for
NRC criterion 4.
