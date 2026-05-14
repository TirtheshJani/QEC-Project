# Glossary

Living document. Add a term the moment you have to look it up twice.

- **CSS code.** A stabilizer code whose stabilizer generators split into
  pure X-type and pure Z-type. Examples: Steane[[7,1,3]], surface code.
- **DEM (detector error model).** Stim's compact representation of a noisy
  circuit's effect on syndrome detectors. Most decoders consume a DEM,
  not the raw circuit.
- **Distance ($d$).** The minimum weight of a logical operator; equivalently
  the smallest number of physical-qubit errors that can cause an undetected
  logical error.
- **Knill–Laflamme conditions.** Algebraic conditions on a code's error set
  $\{E_a\}$ that are necessary and sufficient for the errors to be
  correctable.
- **Logical error rate ($p_L$).** Probability per syndrome cycle (or per
  shot, depending on convention) of an uncorrected logical error.
- **MWPM.** Minimum-weight perfect matching. The canonical surface-code
  decoder. Concrete implementation: PyMatching.
- **qLDPC code.** Quantum low-density parity-check code — stabilizers each
  involve a small number of qubits, and each qubit participates in a small
  number of stabilizers. Recent good examples: bivariate bicycle codes
  (IBM 2024).
- **Rotated surface code.** A more qubit-efficient layout of the surface
  code on a square lattice; the standard "surface code" in modern hardware
  papers.
- **SI1000.** Stim's standard superconducting-inspired circuit-level noise
  model. Roughly: 1-qubit gate error 0.1×p, 2-qubit gate 1×p, measurement
  5×p, idle 0.1×p.
- **Sub-threshold $\Lambda$.** The factor by which the logical error rate
  drops when distance increases by 2, at fixed physical error rate, below
  threshold. $\Lambda > 1$ means scaling up the code helps.
- **Threshold ($p_{\text{th}}$).** The physical error rate at which logical
  error rate becomes distance-independent. Below it, scaling helps; above
  it, scaling makes things worse.
- **Transversal gate.** A logical gate implemented by acting independently
  on each physical qubit of a code block. Inherently fault-tolerant.
  Eastin–Knill forbids a universal set of these on any non-trivial code.
- **Union-Find decoder.** A near-linear-time alternative to MWPM for
  topological codes; the inspiration for current FPGA decoders.
