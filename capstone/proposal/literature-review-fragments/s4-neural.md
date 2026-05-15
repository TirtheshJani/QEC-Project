# S4 — Neural decoders for the rotated surface code

*PRISMA slice for the literature review. Companion `.bib.md` lists admitted
references with two evidence URLs each. Numerical claims attributed to a
paper are reported only when the paper's title, authors, and venue are
both confirmed and the claim was visible in the search-result metadata
returned by `WebSearch`; otherwise the field is left to follow-up.*

## Framing

Neural decoders attack the surface-code decoding problem by **learning the
posterior distribution of logical-failure events given a syndrome
history**, typically using Stim-simulated training data. The promise is
threefold: (i) capture spatially or temporally correlated noise (leakage,
cross-talk, drift) that breaks the independence assumption built into
minimum-weight perfect matching (MWPM); (ii) amortize all decoder
complexity into a forward pass that can be pipelined on commodity
accelerators or FPGAs; and (iii) adapt to hardware-specific noise
fingerprints without an explicit decoding graph re-weighting. The
counter-weight pressures are equally clear: training-data volume scales
poorly with distance and noise diversity; inference latency must beat
the ~1 µs syndrome-cycle budget of superconducting hardware (a *much*
tighter bar than ML accuracy on offline data); and out-of-distribution
generalization across distance, noise model, and device drift is the
field's standing open problem.

## 4a. Feedforward / CNN era

The first wave (2016–2020) established that neural networks can in
principle play the role of a surface-code decoder. Torlai and Melko
trained a stochastic Boltzmann machine on the 2-D toric code and showed
threshold-region performance under phase-flip noise [Torlai–Melko 2017].
Varsamopoulos, Criger and Bertels reduced surface-code decoding to a
classification problem solved by a feedforward network for small
distances [Varsamopoulos–Criger–Bertels 2017; the anchor entry in
`docs/reading-list.md`]. Krastanov and Jiang introduced a *probabilistic*
deep-network decoder that learns the conditional distribution
$P(\text{error}\mid\text{syndrome})$ for arbitrary stabilizer codes
[Krastanov–Jiang 2017]. Chamberland and Ronagh extended this to
fault-tolerant near-term experiments combining algorithmic + neural
stages [Chamberland–Ronagh 2018]. Varsamopoulos, Bertels and Almudever
later compared low-level vs high-level neural decoder designs across
hyperparameters [Varsamopoulos–Bertels–Almudever 2019]. Breuckmann and
Ni argued for CNN-style locality and a renormalization-group structure
to scale to higher-dimensional codes [Breuckmann–Ni 2018]. Meinerz, Park
and Trebst made the CNN scalable by sliding a fixed preprocessing window,
reporting performance up to tens of thousands of qubits in a regime
competitive with Union-Find [Meinerz–Park–Trebst 2022]. Gicev,
Hollenberg and Usman extended convolutional surface-code decoders to
arbitrary shapes and boundary conditions, with demonstrations on code
distances exceeding a thousand under depolarizing noise [Gicev–Hollenberg–Usman
2023]. Bordoni and Giagu probed CNN architectures and applied
explainability tooling [Bordoni–Giagu 2024].

## 4b. Recurrent / transformer era (AlphaQubit class)

The 2023–2024 generation moved from per-shot classification to
*sequence* models that ingest the full syndrome history. Bausch, Senior,
Heras *et al.* — Google DeepMind / Google Quantum AI — introduced a
recurrent transformer architecture for the surface code, first as a
preprint [Bausch *et al.* 2023, arXiv:2310.05900] and then in Nature as
**AlphaQubit** [Bausch *et al.* 2024, "Learning high-accuracy error
decoding for quantum processors," *Nature* 635, 834–840
(doi:10.1038/s41586-024-08148-8)]. The decoder is reported to beat
state-of-the-art classical decoders on real Sycamore data at $d=3,5$ and
to extend that advantage on simulated data with leakage and cross-talk
up to $d=11$. Hanrui Wang and collaborators released Transformer-QEC
[Wang *et al.* 2023], which uses transferable transformers to amortize
training across code distances. Subsequent work has continued this
trajectory; we list the recurrent-transformer line as the current
state-of-the-art *accuracy* baseline against which new decoders should
benchmark on real hardware data.

## 4c. Neural pre-/post-decoders cascaded with MWPM / UF

A complementary strand uses neural networks **not as the primary
decoder** but as a fast first pass that strips local errors before a
global decoder (MWPM, Union-Find) is invoked. Chamberland, Ollé, Li,
Thornton and Baratta (NVIDIA) introduced a "Fast and accurate AI-based
pre-decoder" that performs local, parallel correction and forwards
residual syndromes downstream [Chamberland *et al.* 2026,
arXiv:2604.12841]. Conceptually this matches the predecoder /
two-stage decoder strand catalogued under S5, but the *primitive* here
is neural. The motivation is squarely real-time: AI pre-decoders shed
the bulk of trivial syndrome events at very low latency, leaving the
heavy MWPM/UF pipeline to handle hard residuals — the same labour
division that makes Sparse Blossom plus a predecoder attractive in
practice.

## 4d. Hardware-aware neural decoders (FPGA / NPU)

The most directly real-time-relevant subline puts the neural decoder on
custom silicon. Zhang *et al.* (2023) proposed a scalable, fast and
programmable neural decoder architecture for the rotated surface code
[Zhang *et al.* 2023, arXiv:2305.15767]. Yang, Sun, Wu *et al.* (2026)
report a hardware-integrated FPGA neural-network decoder demonstrated in
closed loop on a superconducting processor for distance-3 surface-code
QEC [Yang *et al.* 2026, arXiv:2605.04892]; the search-result metadata
states a 124 ns NN-decode component inside a 550 ns closed-loop latency
within a 1.25 µs QEC cycle (these numbers should be re-extracted from
the PDF before being quoted in the capstone draft).

## Where neural decoders demonstrably help — and where they don't

The bull case (confirmed by *multiple* primary sources):
1. **Real hardware data with structured noise.** AlphaQubit
   [Bausch *et al.* 2024] is the strongest published evidence that a
   neural decoder can beat MWPM on real Sycamore $d=3,5$ data, where
   leakage and cross-talk break MWPM's edge-independence assumption.
2. **Adaptability without re-weighting a decoding graph.** Multiple
   papers (e.g. Varbanov *et al.* 2023) report neural decoders matching
   or beating MWPM without prior knowledge of physical error rates.
3. **Hardware deployment.** FPGA-resident neural decoders have been
   demonstrated in closed loop [Yang *et al.* 2026], and pre-decoder
   variants reduce latency further [Chamberland *et al.* 2026].

The bear case:
1. **Training-data cost and distance scaling.** Recent CNN/3D-CNN work
   [Gicev *et al.* 2023, 2025] is explicit that generalising to larger
   $d$ is the dominant obstacle, and even the scalable architectures
   need code-specific training data.
2. **Latency at large $d$.** Transformer attention scales unfavourably
   with distance ($\mathcal{O}(d^4)$ has been flagged in follow-on work),
   which is why the pre-decoder cascade pattern matters.
3. **Reproducibility on circuit-level / SI1000 noise at $d \geq 9$**
   remains thin in the published record.

## PRISMA mini-flow (S4)

- Unique titles surfaced across the five S4 search queries: **~24**.
- Passing inclusion criteria (decoder for surface code, reports
  threshold / $\Lambda$ / logical error rate / latency, English,
  arXiv or peer-reviewed): **13**.
- With arXiv ID confirmed by two independent search-result URLs
  (admitted to `s4-neural.bib.md`): **13**.
- Excluded: ~11 — categories: very recent preprints (≤30 days) lacking a
  second independent URL in the index; non-surface-code targets (e.g.
  qLDPC-only); review-style write-ups; titles whose author list we
  could not confirm to two URLs (logged below).

## Open gaps this slice sees

Across the neural-decoder corpus, the clearest hole — and the one most
relevant to the capstone — is the **joint accuracy + latency frontier at
$d \in \{7,9\}$ under circuit-level SI1000 noise**, evaluated on the
*rotated* surface code rather than the planar variant, with public Stim
circuits and seeds. AlphaQubit demonstrates the accuracy ceiling on real
hardware data but is closed-source and trained against Google's
specific noise fingerprint; the open CNN line has chased distance and
threshold but largely under depolarizing rather than SI1000 circuit
noise; the FPGA / pre-decoder line has chased latency at $d=3$. No
single open-source artifact in the surveyed set reports (logical error
rate, $\Lambda$, wall-clock per cycle) jointly for one neural family
against an MWPM baseline at $d \in \{7,9\}$ under SI1000 with seeds and
Stim circuits checked in. That joint table is exactly what the
capstone's experiment matrix can produce.

## Suspected-but-unverified

The following candidates surfaced but I could not pin two independent
URLs to a confirmed title + author list and have *excluded* them from
the bib:

- A frequently-cited "Distributed neural-network decoder" by
  Sweke / Kesselring / van Nieuwenburg / Eisert (the title pattern
  appeared in search results, but I could not separately confirm the
  exact author list and arXiv ID via a second search; not added).
- "Decoding the surface code with a spatio-temporal transformer"
  surfaced in an EPJ Quantum Technology link but with no
  search-result author list; not added.
- "Scalable Neural Decoders for Practical Real-Time Quantum Error
  Correction" (arXiv:2510.22724) and "A scalable and real-time neural
  decoder for topological quantum codes" (arXiv:2512.07737) appear to
  be very recent preprints citing AlphaQubit; titles confirm but I
  could not confirm full author lists to two independent URLs.

## AlphaQubit verification note (per integrity rule)

Specifically confirmed via at least two independent URLs each:

- **Nature paper title:** "Learning high-accuracy error decoding for
  quantum processors." Confirmed via `nature.com/articles/s41586-024-08148-8`
  and PubMed (PMID 39567694) / PMC (PMC11602728).
- **Venue:** *Nature* 635 (8040), 834–840 (2024).
  doi:10.1038/s41586-024-08148-8.
- **arXiv preprint ID:** 2310.05900 — "Learning to Decode the Surface
  Code with a Recurrent, Transformer-Based Neural Network." Confirmed
  via `arxiv.org/abs/2310.05900` and `paperswithcode.com`.
- **Authors:** Lead authors Bausch, Senior, Heras, Edlich confirmed in
  two independent search results (Nature article page; Semantic
  Scholar entry). The full author list reported in search-result
  metadata also includes Davies, Newman, Jones, Satzinger, Niu,
  Blackwell, Holland, Kafri, Atalaya, Gidney, Hassabis, Boixo, Neven,
  Kohli. Affiliation: Google DeepMind and Google Quantum AI.

I did **not** read the PDF, and I have *not* paraphrased numerical
performance claims from AlphaQubit beyond what appeared verbatim in
two distinct search-result snippets.
