# Reading list

The spine of the capstone bibliography. Two rules:

1. Every numerical claim in this repo (notebooks, READMEs, paper draft) must
   point at an entry below or be a freshly computed sim result.
2. Every entry below carries a DOI or arXiv ID so
   `scripts/verify_reading_list.py` can check it resolves.

Entries are grouped by phase; the capstone lit-review document
(`capstone/proposal/literature-review.md`) is the canonical superset.

## Phase 0 — Foundations

- David J. C. MacKay. *Information Theory, Inference, and Learning
  Algorithms.* Cambridge University Press, 2003. (Free online.) — Chs. 1–2.

## Phase 1 — Quantum basics

- Michael A. Nielsen, Isaac L. Chuang. *Quantum Computation and Quantum
  Information.* 10th anniversary ed., Cambridge, 2010.

## Phase 2 — QEC fundamentals

- Daniel Gottesman. *Stabilizer Codes and Quantum Error Correction.* PhD
  thesis, Caltech, 1997. arXiv:quant-ph/9705052.
- Craig Gidney. *Stim: a fast stabilizer circuit simulator.* Quantum 5, 497
  (2021). arXiv:2103.02202. doi:10.22331/q-2021-07-06-497.

## Phase 3 — Topological codes & surface code

- A. G. Fowler, M. Mariantoni, J. M. Martinis, A. N. Cleland. *Surface
  codes: Towards practical large-scale quantum computation.* Phys. Rev.
  A 86, 032324 (2012). arXiv:1208.0928. doi:10.1103/PhysRevA.86.032324.
- Oscar Higgott, Craig Gidney. *Sparse Blossom: correcting a million
  errors per core second with minimum-weight matching.* arXiv:2303.15933.
- Google Quantum AI. *Suppressing quantum errors by scaling a surface code
  logical qubit.* Nature 614, 676–681 (2023). arXiv:2207.06431.
  doi:10.1038/s41586-022-05434-1.

## Phase 4 — Fault tolerance

- Bryan Eastin, Emanuel Knill. *Restrictions on Transversal Encoded Quantum
  Gate Sets.* Phys. Rev. Lett. 102, 110502 (2009). arXiv:0811.4262.
  doi:10.1103/PhysRevLett.102.110502.
- Sergey Bravyi, Alexei Kitaev. *Universal Quantum Computation with Ideal
  Clifford Gates and Noisy Ancillas.* Phys. Rev. A 71, 022316 (2005).
  arXiv:quant-ph/0403025. doi:10.1103/PhysRevA.71.022316.
- Clare Horsman, Austin G. Fowler, Simon Devitt, Rodney Van Meter. *Surface
  code quantum computing by lattice surgery.* New J. Phys. 14, 123011
  (2012). arXiv:1111.4022. doi:10.1088/1367-2630/14/12/123011.

## Phase 5 — Advanced decoders & qLDPC

- Joschka Roffe, David R. White, Simon Burton, Earl Campbell. *Decoding
  across the quantum LDPC code landscape.* Phys. Rev. Research 2, 043423
  (2020). arXiv:2005.07016. doi:10.1103/PhysRevResearch.2.043423.
- Nicolas Delfosse, Naomi H. Nickerson. *Almost-linear time decoding
  algorithm for topological codes.* Quantum 5, 595 (2021). arXiv:1709.06218.
  doi:10.22331/q-2021-12-02-595.
- Sergey Bravyi, Andrew W. Cross, Jay M. Gambetta, Dmitri Maslov, Patrick
  Rall, Theodore J. Yoder. *High-threshold and low-overhead fault-tolerant
  quantum memory.* Nature 627, 778–782 (2024). arXiv:2308.07915.
  doi:10.1038/s41586-024-07107-7.
- Savvas Varsamopoulos, Ben Criger, Koen Bertels. *Decoding small surface
  codes with feedforward neural networks.* Quantum Sci. Technol. 3, 015004
  (2017). arXiv:1705.00857. doi:10.1088/2058-9565/aa955a.

## Capstone — decoder benchmark lit review (v1, 2026-05-15)

The 42 verified additions below were admitted by the systematic review
in `capstone/proposal/literature-review.md` under the protocol in
`capstone/proposal/search-protocol.md`. Every entry is corroborated by
at least two independent `WebSearch` URLs recorded in the per-slice
`.bib.md` files. Numerical claims from these papers are not transcribed
into this repository until they can be verified against the paper PDF
(arXiv full-text fetch is blocked in the current container; see
`CHANGELOG.md` "Failed approaches" 2026-05-14). Entries tagged
`[recent-preprint]` were verified at title + lead-author level only
and should be re-checked against a journal version before being
quoted.

### MWPM family

- Austin G. Fowler. *Minimum weight perfect matching of fault-tolerant
  topological quantum error correction in average O(1) parallel time.*
  Quantum Information & Computation 15, 145 (2015). arXiv:1307.1740.
- Oscar Higgott. *PyMatching: A Python package for decoding quantum
  codes with minimum-weight perfect matching.* ACM Trans. Quantum
  Comput. 3, 16 (2022). arXiv:2105.13082. doi:10.1145/3505637.
- Yue Wu, Lin Zhong. *Fusion Blossom: Fast MWPM Decoders for QEC.*
  IEEE QCE (2023). arXiv:2305.08307.
- Yue Wu, Namitha Liyanage, Lin Zhong. *Micro Blossom: Accelerated
  Minimum-Weight Perfect Matching Decoding for Quantum Error
  Correction.* ASPLOS (2025). arXiv:2502.14787.
  doi:10.1145/3676641.3716005.
- Luka Skoric, Dan E. Browne, Kenton M. Barnes, Neil I. Gillespie,
  Earl T. Campbell. *Parallel window decoding enables scalable
  fault-tolerant quantum computation.* Nat. Commun. 14, 7040 (2023).
  arXiv:2209.08552. doi:10.1038/s41467-023-42482-1.
- Oscar Higgott, Thomas C. Bohdanowicz, Aleksander Kubica,
  Steven T. Flammia, Earl T. Campbell. *Improved decoding of circuit
  noise and fragile boundaries of tailored surface codes.* Phys. Rev. X
  13, 031007 (2023). arXiv:2203.04948.
  doi:10.1103/PhysRevX.13.031007.
- Alexandru Paler, Austin G. Fowler. *Pipelined correlated
  minimum-weight perfect matching of the surface code.* Quantum 7,
  1205 (2023). arXiv:2205.09828.
- J. Pablo Bonilla Ataides, David K. Tuckett, Stephen D. Bartlett,
  Steven T. Flammia, Benjamin J. Brown. *The XZZX surface code.*
  Nat. Commun. 12, 2172 (2021). arXiv:2009.07851.
  doi:10.1038/s41467-021-22274-1.
- Ben Barber et al. *A real-time, scalable, fast and resource-efficient
  decoder for a quantum computer.* Nat. Electron. (2025).
  arXiv:2309.05558. doi:10.1038/s41928-024-01319-5.

### Union-Find family

- Shilin Huang, Michael Newman, Kenneth R. Brown. *Fault-tolerant
  weighted union-find decoding on the toric code.* Phys. Rev. A 102,
  012419 (2020). arXiv:2004.04693. doi:10.1103/PhysRevA.102.012419.
- Yue Wu, Namitha Liyanage, Lin Zhong. *An interpretation of
  Union-Find decoder on weighted graphs.* arXiv:2211.03288 (2022).
- Namitha Liyanage, Yue Wu, Alexander Deters, Lin Zhong. *Scalable
  quantum error correction for surface codes using FPGA.* IEEE QCE
  (2023). arXiv:2301.08419.
- Sam J. Griffiths, Dan E. Browne. *Union-find quantum decoding
  without union-find.* Phys. Rev. Research 6, 013154 (2024).
  arXiv:2306.09767. doi:10.1103/PhysRevResearch.6.013154.
- Tim Chan, Simon C. Benjamin. *Actis: A strictly local union-find
  decoder.* Quantum 7, 1183 (2023). arXiv:2305.18534.
  doi:10.22331/q-2023-11-14-1183.
- Namitha Liyanage, Yue Wu, Siona Tagare, Lin Zhong. *FPGA-based
  distributed union-find decoder for surface codes.* IEEE Trans.
  Quantum Eng. 5 (2024). arXiv:2406.08491.
- Karim Ziad et al. *Local clustering decoder as a fast and adaptive
  hardware decoder for the surface code.* Nat. Commun. (2025).
  arXiv:2411.10343.

### Belief propagation, BP+OSD, and iterative variants

- Pavel Panteleev, Gleb Kalachev. *Degenerate quantum LDPC codes with
  good finite length performance.* Quantum 5, 585 (2021).
  arXiv:1904.02703. doi:10.22331/q-2021-11-22-585.
- Josias Old, Manuel Rispler. *Generalized belief propagation
  algorithms for decoding of surface codes.* Quantum 7, 1037 (2023).
  arXiv:2212.03214.
- Julien du Crest, Mehdi Mhalla, Valentin Savin. *Stabilizer
  inactivation for message-passing decoding of quantum LDPC codes.*
  IEEE ITW 2022, 488 (2022). arXiv:2205.06125.
- Antonio deMarti iOlius, Josu Etxezarreta Martinez. *The closed-branch
  decoder for quantum LDPC codes.* arXiv:2402.01532 (2024).
- Antonio deMarti iOlius, Josu Etxezarreta Martinez et al. *An
  almost-linear time decoding algorithm for quantum LDPC codes under
  circuit-level noise (BP+OTF).* arXiv:2409.01440 (2024).
- Lucas Hillmann, Lukas Berent, Armanda O. Quintavalle, Jens Eisert,
  Robert Wille, Joschka Roffe. *Localized statistics decoding for
  quantum low-density parity-check codes.* Nat. Commun. 16, 8214
  (2025). arXiv:2406.18655.
- Sisi Miao, Alexander Schnerring, Haizheng Li, Laurent Schmalen.
  *Neural belief propagation decoding of quantum LDPC codes using
  overcomplete check matrices.* arXiv:2212.10245 (2022).
- Sisi Miao et al. *Quaternary neural belief propagation decoding of
  quantum LDPC codes with overcomplete check matrices.*
  arXiv:2308.08208 (2023).
- Tianyi Chen, Yi Yi, Jiale Liang, Hailan Wang. *Improved belief
  propagation decoding algorithms for surface codes.*
  arXiv:2407.11523 (2024).
- Tobias Müller, Tristan Alexander, Michael Beverland, Marius Bühler,
  Thomas Johnson, Aaron Maurer, Tom Vandeth. *Improved belief
  propagation is sufficient for real-time decoding of quantum memory.*
  arXiv:2506.01779 (2025).
- Arshpreet Singh Maan, Alexandru Paler. *Machine learning
  message-passing for the scalable decoding of QLDPC codes (Astra).*
  npj Quantum Inf. 11, 78 (2025). arXiv:2408.07038.

### Neural decoders

- Giacomo Torlai, Roger G. Melko. *A neural decoder for topological
  codes.* Phys. Rev. Lett. 119, 030501 (2017). arXiv:1610.04238.
  doi:10.1103/PhysRevLett.119.030501.
- Stefan Krastanov, Liang Jiang. *Deep neural network probabilistic
  decoder for stabilizer codes.* Sci. Rep. 7, 11003 (2017).
  arXiv:1705.09334.
- Nikolas P. Breuckmann, Xiaotong Ni. *Scalable neural network
  decoders for higher-dimensional quantum codes.* Quantum 2, 68
  (2018). arXiv:1710.09489.
- Christopher Chamberland, Pooya Ronagh. *Deep neural decoders for
  near-term fault-tolerant experiments.* Quantum Sci. Technol. 3,
  044002 (2018). arXiv:1802.06441.
  doi:10.1088/2058-9565/aad1f7.
- Savvas Varsamopoulos, Koen Bertels, Carmen G. Almudever.
  *Comparing neural network based decoders for the surface code.*
  IEEE Trans. Comput. (2019). arXiv:1811.12456.
  doi:10.1109/TC.2019.2948612.
- Kai Meinerz, Chae-Yeun Park, Simon Trebst. *Scalable neural decoder
  for topological surface codes.* Phys. Rev. Lett. 128, 080505
  (2022). arXiv:2101.07285. doi:10.1103/PhysRevLett.128.080505.
- Spiro Gicev, Lloyd C. L. Hollenberg, Muhammad Usman. *A scalable
  and fast artificial neural network syndrome decoder for surface
  codes.* Quantum 7, 1058 (2023). arXiv:2110.05854.
- Boris M. Varbanov, Marc Serra-Peralta, David Byfield, Barbara M.
  Terhal. *Neural network decoder for near-term surface-code
  experiments.* Phys. Rev. Research 7, 013029 (2025).
  arXiv:2307.03280.
- Johannes Bausch, Andrew W. Senior, Francisco J. H. Heras, Thomas
  Edlich et al. *Learning to decode the surface code with a
  recurrent, transformer-based neural network.* arXiv:2310.05900
  (2023). Published as *Learning high-accuracy error decoding for
  quantum processors*, Nature 635, 834 (2024) ("AlphaQubit").
  doi:10.1038/s41586-024-08148-8.
- Hanrui Wang, Shaohua Liu, Pengyu Shao, Yuanrui Li, Junyi Gu, Hong
  Pan, Yongshan Ding, Song Han. *Transformer-QEC: Quantum error
  correction code decoding with transferable transformers.*
  arXiv:2311.16082 (2023).
- Simone Bordoni, Stefano Giagu. *Convolutional neural network
  based decoders for surface codes.* Quantum Inf. Process. 22, 449
  (2023). arXiv:2312.03508. doi:10.1007/s11128-023-03898-2.
- Mengyu Zhang, Xiangyu Ren, Guanglei Xi, Zhengwei Zhang, Qiaonian
  Yu, Fuming Liu, Hua Zhang, Shengyu Zhang, Yi-Cong Zheng. *A
  scalable, fast and programmable neural decoder for fault-tolerant
  quantum computation using surface codes.* arXiv:2305.15767 (2023).
- Spiro Gicev, Lloyd C. L. Hollenberg, Muhammad Usman. *Fully
  convolutional 3D neural network decoders for surface codes with
  syndrome circuit noise.* Quantum Sci. Technol. (2025).
  arXiv:2506.16113.
- Christopher Chamberland, Pol Ollé, Yifan Li, Tom Thornton, Pablo
  Baratta. *Fast and accurate AI-based pre-decoders for surface
  codes.* arXiv:2604.12841 (2026). `[recent-preprint]`
- Yang et al. *Real-time surface-code error correction using an
  FPGA-based neural-network decoder.* arXiv:2605.04892 (2026).
  `[recent-preprint]`

### Real-time / hybrid / noise-model anchors

- David K. Tuckett, Stephen D. Bartlett, Steven T. Flammia.
  *Ultrahigh error threshold for surface codes with biased noise.*
  Phys. Rev. Lett. 120, 050505 (2018). arXiv:1708.08474.
  doi:10.1103/PhysRevLett.120.050505.
- David K. Tuckett, Andrew S. Darmawan, Christopher T. Chubb, Sergey
  Bravyi, Stephen D. Bartlett, Steven T. Flammia. *Tailoring surface
  codes for highly biased noise.* Phys. Rev. X 9, 041031 (2019).
  arXiv:1812.08186.
- David K. Tuckett, Christopher T. Chubb, Sergey Bravyi, Stephen D.
  Bartlett, Steven T. Flammia. *Fault-tolerant thresholds for the
  surface code in excess of 5% under biased noise.* Phys. Rev. Lett.
  124, 130501 (2020). arXiv:1907.02554.
- Boris M. Varbanov, Francesco Battistel, Brian M. Tarasinski,
  Viacheslav P. Ostroukh, Thomas E. O'Brien, Leonardo DiCarlo,
  Barbara M. Terhal. *Leakage detection for a transmon-based surface
  code.* npj Quantum Inf. 6, 102 (2020). arXiv:2002.07119.
- Nicolas Delfosse. *Hierarchical decoding to reduce hardware
  requirements for quantum computing.* arXiv:2001.11427 (2020).
- Matthew McEwen et al. *Removing leakage-induced correlated errors
  in superconducting quantum error correction.* Nat. Commun. 12, 1761
  (2021). arXiv:2102.06131.
- Craig Gidney, Michael Newman, Austin Fowler, Michael Broughton.
  *A fault-tolerant honeycomb memory.* Quantum 5, 605 (2021).
  arXiv:2108.10457. (Primary source for the SI1000 circuit-level
  noise model.)
- Kevin C. Miao, Matthew McEwen, Juan Atalaya et al. *Overcoming
  leakage in scalable quantum error correction.* Nat. Phys. 19,
  1780 (2023). arXiv:2211.04728.
- Xinyu Tan, Fang Zhang, Rui Chao, Yaoyun Shi, Jianxin Chen.
  *Scalable surface code decoders with parallelization in time.*
  PRX Quantum 4, 040344 (2023). arXiv:2209.09219.
  doi:10.1103/PRXQuantum.4.040344.
- Narges Alavisamani, Poulami Das et al. *Promatch: Extending the
  reach of real-time quantum error correction with adaptive
  predecoding.* ASPLOS (2024). arXiv:2404.03136.
  doi:10.1145/3620666.3651339.
- Maxwell Caune et al. *Demonstrating real-time and low-latency
  quantum error correction with superconducting qubits.*
  arXiv:2410.05202 (2024).
- Joseph Viszlai et al. *Predictive window decoding for fault-tolerant
  quantum programs.* arXiv:2412.05115 (2024).
- Google Quantum AI (Acharya et al.). *Quantum error correction
  below the surface code threshold.* Nature 638, 920 (2025).
  arXiv:2408.13687. doi:10.1038/s41586-024-08449-y. ("Willow"
  experiment.)
