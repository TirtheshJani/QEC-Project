# S5 — Real-time / hybrid / hardware / noise-aware decoders

*Slice of the PRISMA-aligned decoder literature review (see
`capstone/proposal/search-protocol.md`).* This is the **integration slice**:
it tracks how decoder algorithms, noise models, and classical hardware come
together at the latency budget set by the syndrome-extraction cycle of the
physical platform.

## Framing — what "real-time" means for the rotated surface code

A surface-code quantum memory generates a fresh syndrome every measurement
cycle. On superconducting hardware the cycle target quoted in the literature
is roughly one microsecond per round (Skoric et al., *Parallel window
decoding…* (2022, arXiv:2209.08552); Caune et al., *Demonstrating real-time
and low-latency QEC…* (2024, arXiv:2410.05202); Barber et al., *A real-time,
scalable, fast and highly resource-efficient decoder…* (2023, arXiv:2309.05558)).
If the decoder cannot drain syndromes at this rate, unprocessed rounds
accumulate. Terhal's **backlog problem** — referenced and quantified in
Skoric et al. (2022, arXiv:2209.08552) and again in Viszlai et al.,
*Predictive Window Decoding…* (2024, arXiv:2412.05115) — shows that whenever
the decoding rate falls below the syndrome rate, time-to-solution grows
**exponentially** in the number of non-Clifford operations. "Real-time" is
therefore not a soft latency goal; it is the condition that prevents an
exponential slowdown of any logical computation that contains feedback or
T-gate teleportation. The capstone's latency benchmarks at $d=7$ are
designed against this constraint.

## 5a. The noise-model landscape

Three abstraction levels recur in the literature:

- **Code-capacity noise:** errors only on data qubits, perfect syndromes.
  A theoretical baseline used by tensor-network and threshold-proof work,
  e.g. Tuckett, Bartlett & Flammia, *Ultrahigh Error Threshold for Surface
  Codes with Biased Noise* (2018, arXiv:1708.08474; PRL 120, 050505) — code
  capacity with pure dephasing.
- **Phenomenological noise:** measurement errors are added on top of
  code-capacity noise; a common stepping stone before circuit-level
  simulation.
- **Circuit-level noise:** errors are inserted at every gate, idle, reset,
  and measurement location. This is the regime the capstone targets.

Within circuit-level noise, three concrete parametric models dominate
benchmarks:

- **Uniform depolarizing circuit-level noise.** A single parameter $p$
  drives a depolarizing channel after every operation; used as a generic
  baseline since Fowler et al. (2012, arXiv:1208.0928).
- **SI1000 ("superconducting-inspired, 1000 ns cycle").** Introduced and
  named by Gidney, Newman, Fowler & Broughton, *A Fault-Tolerant Honeycomb
  Memory* (2021, arXiv:2108.10457; Quantum 5, 605). SI1000 reweights the
  individual error locations so measurement and reset dominate over
  one-qubit gates, mimicking transmon-qubit budgets. It is now the de-facto
  noise model whenever a paper benchmarks against superconducting
  expectations (cf. Higgott et al., *Improved decoding of circuit noise…*,
  2022, arXiv:2203.04948; Local Clustering Decoder, 2024, arXiv:2411.10343;
  LUCI / dynamic-surface follow-ups).
- **Biased noise.** A Pauli channel in which $Z$ (dephasing) errors are
  more probable than $X$ or $Y$ by a bias ratio $\eta$. The relevant
  baseline thresholds are Tuckett, Bartlett & Flammia (2018,
  arXiv:1708.08474) for the unmodified surface code, then Tuckett et al.,
  *Tailoring surface codes for highly biased noise* (2019, arXiv:1812.08186),
  and Tuckett et al., *Fault-tolerant thresholds for the surface code in
  excess of 5%…* (2019, arXiv:1907.02554).

Beyond Pauli channels, **leakage** (population escaping the computational
subspace) is treated separately because it breaks the stabilizer
formalism. The capstone's experiment matrix names depolarizing, SI1000,
and biased noise — anchoring the "why these three" argument in the
above primary sources.

## 5b. Real-time / streaming / parallel-window decoders

Skoric, Browne, Barnes, Gillespie & Campbell (*Parallel window decoding…*,
2022, arXiv:2209.08552; Nat. Commun. 14, 7040) and Tan, Zhang, Chao, Shi
& Chen (*Scalable surface code decoders with parallelization in time*,
2022, arXiv:2209.09219; PRX Quantum 4, 040344) independently formalised
the sliding-/parallel-window approach: cut the syndrome history into
overlapping windows along time, decode each in parallel with any inner
matching/UF/BP decoder, then stitch. Both demonstrate that the trick
preserves circuit-level threshold to within stated uncertainty. Viszlai
et al., *Predictive Window Decoding…* (2024, arXiv:2412.05115) extends
this to feed-forward logic and program-level scheduling.

## 5c. Predecoder / two-stage / cascaded decoders

The pattern: a cheap local stage reduces syndrome weight, then a heavier
global decoder cleans up the residual. Delfosse, *Hierarchical decoding
to reduce hardware requirements…* (2020, arXiv:2001.11427) introduced
the "lazy decoder" plus heavy fallback. Promatch (Alavisamani et al.,
*Promatch: Extending the Reach of Real-Time QEC with Adaptive
Predecoding*, 2024, arXiv:2404.03136; ASPLOS '24) is an adaptive
predecoder built on top of a real-time MWPM engine that the authors
report enables real-time decoding at distances beyond what a stand-alone
MWPM engine reached at the time of submission (target distances 11 and
13; numerical claims not extracted from full text in this slice).

## 5d. Biased-noise-aware decoders

The line begins with Tuckett, Bartlett & Flammia (2018, arXiv:1708.08474),
formalising biased-noise thresholds with a tensor-network decoder. The
*tailored* and *XY*-surface families follow in Tuckett et al. (2019,
arXiv:1812.08186 and arXiv:1907.02554). The most-cited modern tailored
code is the **XZZX surface code** of Bonilla Ataides, Tuckett, Bartlett,
Flammia & Brown (2020, arXiv:2009.07851; Nat. Commun. 12, 2172),
designed so the code factorises into repetition codes in the
infinite-bias limit. Higgott, Bohdanowicz, Kubica, Flammia & Campbell,
*Improved decoding of circuit noise and fragile boundaries of tailored
surface codes* (2022, arXiv:2203.04948; PRX 13, 031007), introduced
**belief-matching** and **belief-find**, decoders that exploit
correlated hyperedge fault mechanisms and report higher circuit-level
thresholds than vanilla MWPM under biased noise (specific numerical
improvements not paraphrased here).

## 5e. Leakage-aware decoders

Varbanov, Battistel, Tarasinski, Ostroukh, O'Brien, DiCarlo & Terhal,
*Leakage detection for a transmon-based surface code* (2020,
arXiv:2002.07119; npj Quantum Inf. 6, 102), shows leakage can be
detected via hidden Markov models on ancilla readout, opening the door
to "leakage-aware" decoding. Hardware-side, McEwen et al., *Removing
leakage-induced correlated errors…* (2021, arXiv:2102.06131), and Miao,
McEwen, Atalaya et al., *Overcoming leakage in scalable quantum error
correction* (2022, arXiv:2211.04728; Nat. Phys. 19, 1780), demonstrate
multi-level reset protocols on Sycamore that drop steady-state leakage
populations. On the decoder side, the Local Clustering Decoder
(Hillmann, Caune, Skoric et al., 2024, arXiv:2411.10343) explicitly
integrates a leakage-adaptation engine that updates edge weights in
real time on heralded leakage events.

## 5f. Hardware platforms — FPGA / ASIC at the real-time line

Several distinct hardware decoders now claim sub-microsecond per-round
decoding on actual or representative surface-code distances:

- **Collision Clustering decoder** (Barber, Caune, Coker et al., 2023,
  arXiv:2309.05558; Nat. Electron. 7, 1003): FPGA *and* ASIC
  implementations targeting MHz throughput on surface-code patches
  reported up to ~1000 qubits (specific size/latency numbers not
  paraphrased).
- **LCD — Local Clustering Decoder** (2024, arXiv:2411.10343): FPGA;
  authors target sub-µs/round with a leakage-adaptive backend.
- **Demonstrating real-time and low-latency QEC with superconducting
  qubits** (Caune et al., 2024, arXiv:2410.05202): Riverlane × Rigetti
  integration of the Collision Clustering decoder into Ankaa-class
  control hardware, including an end-to-end fast-feedback experiment.
- **Quantum error correction below the surface code threshold** (Google
  Quantum AI / Acharya et al., 2024, arXiv:2408.13687; Nature 638, 920):
  Willow processor result that *includes* a real-time decoder for the
  distance-5 memory, plus an offline tensor-network result for the
  distance-7 memory.
- The seminal Google Quantum AI surface-code paper, *Suppressing quantum
  errors by scaling a surface code logical qubit* (2022, arXiv:2207.06431;
  Nature 614, 676), did *not* yet decode in real time but defined the
  syndrome stream and noise budget that every subsequent real-time
  decoder is measured against. This entry is already in
  `docs/reading-list.md`.

A second class — FPGA MWPM engines (Micro-Blossom, Helios, etc.) — sits
mostly inside the S1 slice; it is cross-referenced here only as the
"matching engine" that Promatch and Caune et al. wrap.

## Cross-cutting trade-off

The slice surfaces a three-axis Pareto frontier — **logical accuracy**,
**wall-clock latency per round**, and **hardware footprint** (FPGA
LUTs / ASIC area / power). MWPM-class decoders saturate accuracy but
historically lose latency at large $d$; clustering / UF-class decoders
trade some accuracy for sub-µs throughput on FPGA; neural decoders
(AlphaQubit / 2310.05900; see S4) match or beat MWPM accuracy on real
hardware data but introduce a different latency profile (NN inference
on accelerators rather than fixed-pipeline FPGAs). Predecoders are the
explicit bridge: they let a slow accurate decoder retain its accuracy
budget by handing it only the syndromes the predecoder could not
already explain. The *noise model* picks the winner: SI1000 favours
matching-aware schedules; high-bias regimes favour XZZX / belief-matching;
leakage-dominated regimes favour the LCD-style adaptive cascade.

## PRISMA mini-flow (this slice)

- Search-string hits surfaced (unique titles after dedup across the seven
  WebSearch queries listed in `search-protocol.md` §S5 plus the AlphaQubit
  / Google / parallel-window anchor queries): **≈ 30**.
- Excluded — out-of-scope code family, non-surface, review/blog, not a
  decoder paper, or paper that I could not verify to two independent
  evidence URLs at the level of arXiv ID + title + at least one author:
  **≈ 13**.
- Admitted with verified arXiv ID and two independent evidence URLs:
  **17** (listed in `s5-realtime-noise.bib.md`).
- Already in `docs/reading-list.md` (anchors): **2** (Fowler 1208.0928;
  Google QAI 2207.06431). Confirmed, not duplicated.

## Open gaps THIS slice sees

Three gaps look exploitable for the capstone:

1. **No single benchmark study sweeps the same decoder family across
   depolarizing + SI1000 + biased noise at the same distances with a
   shared shot budget.** The biased-noise threshold line (1708.08474 /
   1812.08186 / 1907.02554 / 2009.07851 / 2203.04948) and the SI1000
   / real-time line (2108.10457 / 2209.08552 / 2209.09219 / 2309.05558
   / 2410.05202 / 2411.10343 / 2408.13687) overlap in noise-model space
   but rarely in decoder space — the biased-noise papers benchmark
   bespoke tailored-code decoders; the real-time papers benchmark
   matching/clustering on uniform circuit-level or SI1000 noise. A
   like-for-like sweep on the *rotated* surface code with PyMatching /
   Union-Find / BP+OSD / a small CNN (the capstone matrix) under the
   same shot budget directly fills this hole and is the strongest
   "novelty knob (a)" candidate listed in `capstone/README.md`.
2. **Latency-vs-accuracy Pareto curves under realistic noise are
   reported per-decoder, not joined.** Promatch (2404.03136), Caune
   et al. (2410.05202), LCD (2411.10343), and AlphaQubit 2 advertise
   sub-µs latencies, but at different distances and on different noise
   models, so an apples-to-apples Pareto plot does not exist in the
   indexed literature. The capstone latency benchmark at $d=7$ across
   the four decoder families would produce that plot.
3. **Leakage-aware vs biased-aware decoders are rarely compared.** The
   leakage line (2002.07119 / 2102.06131 / 2211.04728 / 2411.10343) and
   the bias line (the Tuckett / XZZX / belief-matching line) operate on
   disjoint subsets of the noise-model phase diagram. A modest
   leakage-augmented biased channel is precisely the regime where a
   noise-aware predecoder + matching backend would be most useful, and
   it is empirically underexplored in the indexed corpus. This points
   at "novelty knob (a)" with a leakage-augmented twist, or at
   "novelty knob (c)" (neural pre-decoder + MWPM) as the most
   defensible NRC-criterion-5 framing.

These three gaps are the slice's contribution to the capstone's NRC
criterion-4 case and should feed directly into the gap paragraph of
`capstone/proposal/literature-review.md`.
