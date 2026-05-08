# 00 — Linear algebra, just the QEC-relevant bits

The bits of linear algebra that matter for QEC. Skip the proofs; what you need is a working vocabulary so the notation in later notes doesn't trip you up.

## State spaces are complex Hilbert spaces

A pure quantum state lives in a finite-dimensional complex vector space `H = C^d`. We write vectors with **bra-ket** notation: `|psi>` for a column vector, `<psi|` for its conjugate transpose row vector. The inner product is `<phi|psi> = sum_i phi_i^* psi_i`, and the norm is `||psi|| = sqrt(<psi|psi>)`. **Physical states are unit vectors:** `<psi|psi> = 1`.

Two states that differ only by an overall phase, `|psi>` and `e^{i alpha} |psi>`, are *physically the same state*. This is the global-phase invariance and is why the Bloch sphere is a 2-sphere rather than a 3-sphere — one real degree of freedom is unobservable.

## Operators as matrices

A linear operator `A: H -> H` is a `d x d` complex matrix. Three classes matter:

- **Unitary** `U U^dagger = I`. These preserve the norm, so they are the only operators allowed as "evolution" of a closed quantum system. All quantum gates are unitary.
- **Hermitian** `A = A^dagger`. Real eigenvalues; orthogonal eigenvectors. These represent **observables** (energy, spin component, etc.). Measurement outcomes are eigenvalues; post-measurement states are the corresponding eigenvectors.
- **Projectors** `P^2 = P = P^dagger`. Special Hermitians whose eigenvalues are 0 or 1. Measurement is implemented by a set of projectors `{P_k}` that sum to `I`.

Two facts you will use constantly:

1. **Spectral theorem**: every Hermitian `A` decomposes as `A = sum_k lambda_k |k><k|` where the `|k>` are orthonormal eigenvectors. So you can replace any Hermitian with a list of (eigenvalue, projector) pairs.
2. **A unitary is "exp(i Hermitian)"**: `U = e^{-i H t}` for some Hermitian `H` (the Hamiltonian) and time `t`. Don't dwell on this; it will come back when discussing noise.

## Tensor products: how multi-qubit space is built

If qubit A lives in `H_A` and qubit B in `H_B`, the joint system lives in **`H_A ⊗ H_B`**, the tensor product. Concretely:
- `|0>_A ⊗ |1>_B = |01>` is a 4-vector.
- An operator that acts only on A becomes `A ⊗ I` on the joint space.
- Tensor product of matrices is the **Kronecker product**: a 4x4 matrix from two 2x2s.

The dimension multiplies, not adds: `n` qubits → `2^n`-dimensional state space. This is the root of "exponential blowup" and the reason classical simulation gets hard.

**Important convention used in this repo (matches Qiskit):** for a basis state index `k`, qubit 0 is the *least significant bit*. So `|01>` means qubit 0 is 1, qubit 1 is 0. (This bites you the first time. Write the index in binary if you ever feel uncertain.)

## Inner products, outer products, and `|i><j|`

The "outer product" `|psi><phi|` is a rank-1 matrix. In particular:
- `|0><0| = diag(1, 0)` is the projector onto `|0>`.
- `|0><1|` is the matrix that maps `|1>` to `|0>` — a "lowering" operator.
- Any operator can be expanded in a basis: `A = sum_{ij} A_{ij} |i><j|`.

This is just matrix component notation in a more readable disguise.

## Trace, partial trace

The trace is `Tr(A) = sum_i A_{ii} = sum_i <i|A|i>`. Two facts:
- **Cyclic**: `Tr(ABC) = Tr(BCA) = Tr(CAB)`.
- **Probability of measurement outcome `P`** in state `|psi>` is `<psi|P|psi> = Tr(P |psi><psi|)`.

The **partial trace** `Tr_B(rho_AB)` "throws away" subsystem B and gives a description of A alone. It's the rule that takes a joint state to a "reduced" state on one part. We'll use it constantly when an environment couples to our qubits and we don't want to track the environment explicitly. Concretely: `Tr_B(|a><a'| ⊗ |b><b'|) = <b'|b> · |a><a'|`, extended by linearity.

## Why this matters for QEC

Almost everything below is some statement about Hermitian operators with eigenvalues `±1` (Paulis), unitaries built out of them (Cliffords), and projections onto stabilizer subspaces. You don't need a deep linear algebra background, but you do need to be fluent enough to write a tensor product without flinching.

## See also

- Nielsen & Chuang, *Quantum Computation and Quantum Information*, Ch. 2 — the standard reference.
- 3Blue1Brown, *Essence of linear algebra* (YouTube) — for intuition if you want a refresher.
