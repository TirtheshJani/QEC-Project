# 10 — Fault tolerance basics

Up to here we've assumed that everything except the *physical qubits* is perfect: encoders apply unitaries with no error, syndrome-extraction circuits never go wrong, and measurements give exactly the right answer. This is wishful thinking. In any real device, every gate, every CNOT, every ancilla preparation, every measurement is itself noisy — and a single bad CNOT in the syndrome circuit can spread one physical error into many. **Fault tolerance** is the discipline of designing QEC procedures that don't make things worse.

This note is conceptual rather than computational; the small numerical demo at the end illustrates *why* naive QEC is not enough.

## The propagation problem

Take the Steane code. To measure stabilizer `Z_3 Z_4 Z_5 Z_6` (one of the X-side syndromes), the textbook circuit puts an ancilla in `|0>`, applies a CNOT from each of qubits 3, 4, 5, 6 to the ancilla, and measures the ancilla. The ancilla's outcome is the parity of those qubits' Z-eigenvalues — exactly the syndrome we want.

Now suppose **the ancilla suffers an X error in the middle** of those four CNOTs. By the CNOT propagation rules (note 02), `X` on the *target* of a CNOT does nothing to the control. But `X` on the *control* propagates `X` to the target. The ancilla here is the *target* of all four CNOTs, so an X error on it stays put and contaminates the measurement (one bit of syndrome is corrupted) — but doesn't spread to the data.

What about a `Z` error on the ancilla mid-circuit? Z on a CNOT *target* propagates to the *control* (note 02). So a single Z on the ancilla becomes Z on whichever data qubits its CNOTs have already touched — turning into a multi-qubit Pauli on the *data*, which can be a logical operator. **One ancilla error → logical failure.** Distance-3 protection has been demolished by a non-fault-tolerant syndrome circuit.

The lesson: in a non-fault-tolerant scheme, one fault produces *more than one* error on the data — defeating the very property a distance-`d` code was supposed to give you (correct fewer than `d` errors).

## What fault-tolerant means

A circuit (or gadget) is **fault-tolerant** at level `r` if any combination of at most `r` faults — anywhere in the circuit — produces at most `r` errors on each output codeblock. The standard target is `r = (d-1)/2`, matching the code's correction capacity.

The two canonical FT designs for syndrome extraction:

- **Shor-style ancillas (cat states).** Use `w` ancilla qubits in a `w`-qubit cat state `(|0...0> + |1...1>) / sqrt(2)` to measure a weight-`w` stabilizer; one CNOT from each data qubit to its dedicated ancilla; finally measure all ancillas in the X basis and XOR the results to recover the parity. A single fault on one ancilla affects at most one data qubit. Costly (many ancilla qubits), but conceptually clean.

- **Steane-style ancillas.** Prepare an ancilla *encoded in the same Steane block*, and use a transversal CNOT between the data block and the ancilla block to copy syndrome information. A single fault inside the ancilla preparation propagates to at most one data qubit. Less ancilla overhead than Shor-style.

Both schemes can repeat the syndrome measurement multiple times to make the *measurement outcome* itself fault-tolerant — at the cost of running the syndrome circuit `O(d)` times before deciding what recovery to apply. This is what surface-code papers refer to when they talk about "rounds of syndrome extraction".

## Transversal gates and Eastin–Knill

A logical gate `U_L` is **transversal** if it can be written as a tensor product of single-qubit gates (or pairwise gates between two code blocks): one physical operation per qubit. Transversal gates are automatically fault-tolerant — a single physical fault produces at most one physical error per output block, since the gate touches each qubit independently.

For Steane, the Hadamard, S (or its dagger), and CNOT (between two Steane blocks) are all transversal. **Steane has a transversal Clifford set.** That alone makes it the leading candidate for fault-tolerant Clifford circuits.

But Cliffords aren't universal: `T` is also needed, and:

> **Eastin–Knill (2009)**: No code that detects an arbitrary single-qubit error admits a universal transversal gate set. There is always at least one gate (typically `T`) that cannot be implemented transversally.

This is a structural obstruction, not an engineering failure. It means any FT-universal scheme has to provide non-Clifford gates by some non-transversal route.

## Magic state distillation (overview)

The standard answer: implement the Cliffords transversally on your code, then for each logical `T` gate, *consume* an auxiliary "magic state" `|T> = (|0> + e^{i pi/4} |1>) / sqrt(2)` via a Clifford-only "T-injection" gadget. Magic states are noisy (they came from imperfect physical preparation), so we **distil** them: take many noisy `|T>` states, run them through a Clifford circuit, and extract a smaller number of cleaner ones. Iterate until the residual error rate is acceptable.

Magic state distillation is enormously expensive — typically dozens to thousands of physical qubits per distilled magic state — and is the dominant overhead in any forecast of "what does a useful fault-tolerant computer cost?" We won't implement it here; the point of this note is to flag where the cost lives.

## The threshold theorem (informally)

The headline FT result. Concatenate a distance-`d` code with itself `r` times; the logical error rate at level `r` is approximately
```
p_L^{(r)}  ≈  p_th  ·  (p_phys / p_th)^{2^r},
```
where `p_th` is a code-and-architecture-specific **threshold**: as long as `p_phys < p_th`, concatenation drives `p_L` doubly-exponentially toward zero. Below threshold, you can buy arbitrary reliability with polynomial overhead. Above threshold, adding more layers makes things worse.

Numerical thresholds:
- Concatenated Steane with FT syndrome extraction: ~10^{-4} or so.
- Surface code with FT syndrome extraction: ~10^{-2} (the canonical headline number).

The surface-code threshold being two orders of magnitude higher than Steane's is why the surface code is the leading candidate for first-generation FT hardware.

## Numerical demo: naive syndrome extraction *increases* errors

`qec/codes/repetition.py` provides a Pauli sampler. We'll re-use it to make a small "naive vs FT" comparison: with noisy ancillas, the naive 3-qubit-repetition syndrome circuit can produce a *higher* logical error rate than no encoding at all, when ancilla noise is comparable to data noise. The exact crossover is not pretty mathematics, but the qualitative point is robust.

(This illustration is sketched in `demos/07_css_klc.ipynb` text — actually implementing FT syndrome extraction is beyond the scope of Phase 7. The repetition-code Qiskit notebook from Phase 4 *implicitly* uses fault-tolerant ancillas — `qiskit-aer` has the noise model attached only to the data qubits, not the ancillas — which is why its threshold matches the analytic curve.)

## What's next

This note is the gateway between "QEC codes" and "QEC architectures". The actual fault-tolerant designs we'd build on real hardware live in the surface code (note 11), where 2D locality, planar layouts, and a high threshold make the engineering tractable. From here, the phase-2 follow-on work would be:

- A Stim-based simulation of the surface code with circuit-level Pauli noise.
- A PyMatching-based MWPM decoder, producing an honest threshold plot.
- A magic-state-distillation cost estimate for a target logical error rate.

These are the "out of scope" items from the project plan and are good directions if you ever return to QEC after the conceptual walk-through.

## See also

- Aliferis, Gottesman, Preskill (2006), https://arxiv.org/abs/quant-ph/0504218 — rigorous threshold proof.
- Eastin & Knill (2009), https://arxiv.org/abs/0811.4262 — the no-universal-transversal-set theorem.
- Bravyi & Kitaev (2005), https://arxiv.org/abs/quant-ph/0403025 — the magic-state-distillation paper.
- Preskill, Ph229 Ch. 7 — the canonical lecture-notes treatment.
- Gottesman, *An Introduction to Quantum Error Correction and Fault-Tolerant Quantum Computation* (2009), https://arxiv.org/abs/0904.2557 — short, friendly, comprehensive.
