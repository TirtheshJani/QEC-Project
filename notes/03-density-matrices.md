# 03 — Density matrices and mixed states

State vectors describe pure quantum states. They cannot describe **statistical mixtures** ("with probability 1/2 the state is `|0>`, otherwise `|+>`") and they cannot describe a subsystem of an entangled state (where partial information is lost). The density-matrix formalism handles both.

## Definition

For a pure state `|psi>`, the density matrix is the rank-1 projector
```
rho = |psi><psi|.
```
For a statistical ensemble `{p_i, |psi_i>}` (with `sum_i p_i = 1`), the density matrix is
```
rho = sum_i p_i |psi_i><psi_i|.
```
Every density matrix `rho` satisfies three properties:
1. `rho^dagger = rho`  (Hermitian)
2. `rho >= 0`            (positive semi-definite — all eigenvalues `≥ 0`)
3. `Tr(rho) = 1`         (probabilities sum to 1)

Conversely, any matrix with those three properties is a valid density matrix.

A density matrix is **pure** iff `Tr(rho^2) = 1`; otherwise it is **mixed** and `Tr(rho^2) < 1`. The quantity `Tr(rho^2)` is called the **purity**.

## Why we need it

Three reasons, all of which show up in QEC:

**1. Statistical ignorance.** If a noise process produces `|0>` half the time and `|1>` half the time, the state is `rho = (1/2)(|0><0| + |1><1|) = I/2`. There is no state vector that means "I/2"; only the density matrix does.

**2. Subsystems of entangled states.** If you have `|Phi+>` between qubits A and B but you only have access to A, your description of A is the **reduced state**
```
rho_A = Tr_B(|Phi+><Phi+|) = I/2.
```
A is *maximally mixed* even though the joint state is pure. This is the formal statement that "entangled" = "the parts know less than the whole".

**3. Noise.** Real qubits couple to an environment. If you start in a pure state and let it interact unitarily with a (much larger) environment, then trace out the environment, you generically get a mixed state. The map `rho_in -> rho_out` is a **quantum channel** (note 04).

## Operations

- **Unitary evolution**: `rho -> U rho U^dagger`.
- **Measurement** with projectors `{P_k}`:
  - `Pr(k) = Tr(P_k rho)`.
  - Post-measurement state given outcome `k`: `P_k rho P_k / Pr(k)`.
- **Expectation value of an observable A**: `<A> = Tr(A rho)`.

These all reduce to the state-vector versions when `rho = |psi><psi|`. Density-matrix formulas are strictly more general.

## Partial trace, in coordinates

For `rho_AB` on a 2-qubit system (with q1 the "B" qubit, q0 the "A" qubit), the reduced density matrix on A is the 2x2 matrix
```
(rho_A)_{ij} = sum_{k} (rho_AB)_{(k,i), (k,j)}
```
i.e. you sum over the diagonal of the B index. Numerically: reshape the 4x4 matrix to (2,2,2,2), then trace axes 0 and 2 (or 1 and 3 — be careful which qubit is which).

## Bloch-ball picture

For a single qubit, every density matrix can be written
```
rho = (I + r_x X + r_y Y + r_z Z) / 2,    r = (r_x, r_y, r_z) in R^3,    ||r|| <= 1.
```
- `||r|| = 1` ↔ pure state, on the Bloch *sphere*.
- `||r|| < 1` ↔ mixed state, strictly inside the Bloch *ball*.
- `r = 0` ↔ maximally mixed `I/2`, the centre.

So mixed states fill the interior of the Bloch ball. Noise channels typically shrink the ball ("decoherence" is "the radius of `r` decreases").

## Fidelity and trace distance

Two ways to ask "how close are these two states":
- **Fidelity**: `F(rho, sigma) = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2`. For pure states it reduces to `|<psi|phi>|^2`.
- **Trace distance**: `D(rho, sigma) = (1/2) Tr|rho - sigma|`. Operationally: the maximum probability of distinguishing them with a single measurement.

We'll mainly use `F` because it's easy to compute (especially for `sigma` pure: `F = <phi|rho|phi>`).

## Why this matters for QEC

QEC tracks how a *logical* density matrix changes under noise. Every figure of merit you'll encounter — logical error rate, code performance vs `p`, threshold — is ultimately a statement about the trace distance (or fidelity) between the noisy logical state and the noiseless target. State vectors are not enough; the moment you simulate noise honestly, you need density matrices (or you need to *sample* from them, which is what stabilizer simulators effectively do).

## Demo

Density matrices appear explicitly in `demos/02_noise_channels.ipynb` (Phase 2). For now you can verify on paper that
```
(1/2) |0><0| + (1/2) |1><1|  =  (1/2) |+><+| + (1/2) |-><-|  =  I/2.
```
**Different ensembles can produce the same density matrix.** That's not a contradiction — it's the formal statement that statistical mixtures are only as distinguishable as their density matrices say they are. Two ensembles with the same `rho` are operationally identical.
