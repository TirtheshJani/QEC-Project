# 01 — The single qubit

A qubit is a unit vector in `C^2`. That's the whole definition. Everything else is consequences and conventions.

## State

The two computational-basis states are
```
|0> = (1, 0)^T,    |1> = (0, 1)^T.
```
A general pure single-qubit state is
```
|psi> = alpha |0> + beta |1>,    alpha, beta in C,    |alpha|^2 + |beta|^2 = 1.
```
The numbers `|alpha|^2` and `|beta|^2` are the probabilities of measuring 0 or 1 in the **Z basis** (the computational basis).

Two real degrees of freedom remain after enforcing the norm and dropping the global phase. They parameterise the **Bloch sphere**:
```
|psi> = cos(theta/2) |0> + e^{i phi} sin(theta/2) |1>.
```
- `theta = 0` → `|0>` (north pole).
- `theta = pi` → `|1>` (south pole).
- `theta = pi/2, phi = 0` → `|+> = (|0> + |1>) / sqrt(2)` (the `+x` axis).
- `theta = pi/2, phi = pi/2` → `|i+> = (|0> + i|1>) / sqrt(2)` (the `+y` axis).

The Bloch sphere is more than a memnonic: rotations on the sphere correspond exactly to single-qubit unitaries, and Pauli measurements project onto its three orthogonal axes.

## Pauli operators

The four Pauli matrices on one qubit:
```
I = [[1, 0], [0, 1]]
X = [[0, 1], [1, 0]]      (NOT, bit-flip)
Y = [[0, -i], [i, 0]]
Z = [[1, 0], [0, -1]]     (phase-flip on |1>)
```
Key algebraic facts (memorise these):
- `X^2 = Y^2 = Z^2 = I`.
- `XY = iZ`, `YZ = iX`, `ZX = iY` (cyclic).
- `Y X = -iZ` etc.: distinct Paulis **anticommute**; identical ones commute.
- `XZ = -ZX` is the single most-used relation in stabilizer theory.

The set `{I, X, Y, Z, ±, ±i}` is the **single-qubit Pauli group**, and it's the foundation of every code in this repo.

## Measurement

A **Z-basis measurement** is described by the projectors `P_0 = |0><0|, P_1 = |1><1|`. Born's rule:
```
Pr(outcome k) = <psi| P_k |psi>,
post-measurement state = P_k |psi> / sqrt(Pr(outcome k)).
```
Measuring `|+>` in the Z basis gives 0 or 1 with equal probability. Measuring it in the **X basis** (eigenbasis of `X`: `|+>`, `|->`) gives `+1` deterministically.

This is the first thing classical intuition will mislead you on. There is no "true" pre-measurement bit value of `|+>`. The state is fully specified, but the outcome is random — and *which observable you measure changes the statistics*.

## Common gates

These appear constantly:

| Gate | Matrix | What it does |
|---|---|---|
| `X` | `[[0,1],[1,0]]` | Flip `|0> <-> |1>`. |
| `Z` | `[[1,0],[0,-1]]` | Phase-flip `|1> -> -|1>`. |
| `Y` | `iXZ` | Bit + phase flip. |
| `H` | `(1/sqrt(2)) [[1,1],[1,-1]]` | Z basis ↔ X basis. `H|0> = |+>`. |
| `S` | `[[1,0],[0,i]]` | Quarter rotation around Z. `S^2 = Z`. |
| `T` | `[[1,0],[0, e^{i pi/4}]]` | Eighth rotation around Z. `T^2 = S`. |
| `R_x(theta)` | `e^{-i theta X / 2}` | Rotation around the X axis on the Bloch sphere. |
| `R_y, R_z` | analogous | Around Y, Z. |

`H, S, T` is one famous **universal** single-qubit gate set: any single-qubit unitary can be approximated to arbitrary precision by sequences of `H, S, T`. We'll come back to this when fault tolerance forces us to care about which gates are "cheap" vs "expensive".

## Why we'll lose `T` (and gain it back painfully)

Foreshadowing: in the stabilizer formalism, the gates that map Paulis to Paulis under conjugation are called **Clifford gates** — `H`, `S`, `CNOT`, and the gates they generate. `T` is *not* Clifford. This is great news for simulation (Cliffords are classically efficient — Gottesman–Knill) but bad news for computation, because Cliffords alone are not universal. Bridging that gap — recovering `T` from a fault-tolerant code — is what magic state distillation is for. We'll meet it in note 10.

## Demo

Run `demos/01_statevec_vs_qiskit.ipynb`. The cells you care about for this note:
- Hadamard creates a uniform superposition.
- Pauli `Z` is invisible in the Z basis but flips outcomes after a Hadamard.
- `R_x(pi)` equals `-iX` (up to a global phase) — see the Bloch sphere picture.
