# 02 — Multi-qubit systems

The whole reason QC is interesting is that joint quantum systems are not just "two single qubits" — they admit **entanglement**, which has no classical analogue. This note covers the mechanics so the upcoming code-construction notes have a foundation.

## Tensor products

For qubits A and B, the joint state space is `H_A ⊗ H_B = C^2 ⊗ C^2 = C^4`. The four computational basis states are written
```
|00>, |01>, |10>, |11>
```
where the *left* symbol is the first-listed qubit. **In this repo and in Qiskit**, qubit 0 is the *least significant* bit of the basis-state index, so
```
basis index 0 = |00>   (q1=0, q0=0)
basis index 1 = |01>   (q1=0, q0=1)
basis index 2 = |10>   (q1=1, q0=0)
basis index 3 = |11>   (q1=1, q0=1)
```
(If you've read N&C this looks reversed. It is. The math doesn't care; just stay consistent.)

A general 2-qubit state is `alpha|00> + beta|01> + gamma|10> + delta|11>` with `|alpha|^2 + |beta|^2 + |gamma|^2 + |delta|^2 = 1`.

**Operators tensor too.** `X ⊗ I` is "apply X to the *second*-listed qubit, do nothing to the first" — a 4x4 matrix obtained by Kronecker product. In the `qec.statevec` simulator we never build `X ⊗ I`; instead we reshape the state vector into a tensor with `n` axes and act on the relevant axis. Same math, much faster.

## Separable vs entangled

A 2-qubit state is **separable** ("product state") if it can be written `|psi_A> ⊗ |psi_B>`. Otherwise it is **entangled**. Most states are entangled — separability is a measure-zero subset.

The four **Bell states** are the canonical maximally-entangled 2-qubit states:
```
|Phi+> = (|00> + |11>) / sqrt(2)
|Phi-> = (|00> - |11>) / sqrt(2)
|Psi+> = (|01> + |10>) / sqrt(2)
|Psi-> = (|01> - |10>) / sqrt(2)
```
Try to factor `|Phi+>` into `(a|0> + b|1>) ⊗ (c|0> + d|1>)`. You can't — there is no choice of `a, b, c, d` that gives `ac = 1/sqrt(2), ad = 0, bc = 0, bd = 1/sqrt(2)`.

The **physical signature** of entanglement: measuring qubit 0 of `|Phi+>` returns 0 or 1 with equal probability, but the post-measurement state of qubit 1 is then *correlated* with that outcome (also 0 or also 1). Classical bits do this too — the surprise is that the correlation persists across change of measurement basis (X, Y, Z), violating Bell inequalities. We won't dwell on Bell here; we just need entanglement as a tool.

## Entangling gates

You can't make entanglement out of single-qubit gates; you need an interaction. The two we'll use endlessly:

**CNOT** (controlled-NOT):
```
CNOT |c, t> = |c, t XOR c>     i.e.   if control=1, flip target.
```
Matrix in the `|q1 q0>` ordering with q0 as control, q1 as target:
```
[[1, 0, 0, 0],
 [0, 1, 0, 0],
 [0, 0, 0, 1],
 [0, 0, 1, 0]]
```
**CZ** (controlled-Z): adds a `-1` phase iff both qubits are `|1>`. CZ is symmetric in its qubits; it's diag(1, 1, 1, -1).

The **standard recipe** for a Bell pair (used in tests/test_statevec.py and demos/01):
```
1. start in |00>
2. H on qubit 0       -> (|00> + |01>)/sqrt(2)
3. CNOT q0 -> q1      -> (|00> + |11>)/sqrt(2) = |Phi+>
```

CNOT, CZ, and SWAP are all **Clifford** (they map Paulis to Paulis under conjugation):
```
CNOT (X ⊗ I) CNOT^dagger = X ⊗ X    (X on control propagates to target)
CNOT (I ⊗ X) CNOT^dagger = I ⊗ X    (X on target stays put)
CNOT (Z ⊗ I) CNOT^dagger = Z ⊗ I    (Z on control stays put)
CNOT (I ⊗ Z) CNOT^dagger = Z ⊗ Z    (Z on target propagates to control)
```
You will use these four equations more than any other in stabilizer theory. They say "errors propagate through CNOT", which is the single fact responsible for needing fault-tolerant gadgets later.

## Universality

The standard universal gate set for quantum computing is **`{H, T, CNOT}`**: every unitary on `n` qubits can be approximated to arbitrary precision by a circuit over those three gates. There are many such sets; this is just the most common.

## Worked example: quantum teleportation

The smallest interesting multi-qubit protocol. Alice has an unknown qubit `|psi>`; she and Bob share a Bell pair. After CNOT + H + 2 measurements, plus 2 classical bits sent to Bob, plus a conditional X / Z on Bob's qubit, **Bob's qubit is now in state `|psi>`**. Alice's copy has been destroyed (no-cloning is preserved).

Demo `demos/01_statevec_vs_qiskit.ipynb` includes this protocol with an explicit fidelity check. The point isn't the protocol itself — it's that you can verify it numerically with the tools we've built.

## Why this matters for QEC

Every QEC code we'll build has two ingredients:
1. An **encoding circuit** that takes a single logical qubit `|psi_L>` and entangles it across `n` physical qubits. This is just multi-qubit unitaries — Hadamards plus CNOTs in every code we'll touch.
2. A **syndrome circuit** that uses ancilla qubits and CNOTs to read out an error pattern *without* collapsing the encoded state. The four CNOT-Pauli identities above are what make this possible.
