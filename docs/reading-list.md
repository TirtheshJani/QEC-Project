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
- Claude E. Shannon. *A Mathematical Theory of Communication.* Bell
  System Technical Journal 27 (3): 379–423 (1948).
  doi:10.1002/j.1538-7305.1948.tb01338.x. — Source for the binary
  symmetric channel capacity formula C = 1 - H_2(p) used in Phase 0.2.

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
