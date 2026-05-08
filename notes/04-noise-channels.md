# 04 — Noise & quantum channels

Real qubits are not closed systems. They couple to whatever they are made of (cavity photons, phonons, control electronics, neighbouring qubits) and to a much larger uncontrolled environment. The mathematical object that captures "what this coupling does to the qubit's density matrix" is a **quantum channel**.

This is the conceptual leap that makes QEC necessary: closed-system unitaries never increase entropy, but real physical evolution does, and we have to describe + correct that.

## Why classical ECC ideas don't transfer directly

Three classical-coding instincts that fail in the quantum setting:

1. **No-cloning.** You cannot copy an unknown qubit. So the simplest classical recipe — "send the same bit three times" — is not available. Repetition coding still *exists* in the quantum world (note 06), but you do not encode by copying; you encode by **entangling** with ancillas.
2. **Measurement collapses.** You cannot peek at a qubit and check it. Reading out a qubit destroys its superposition. So you cannot just compare three copies and majority-vote the way a classical decoder would. QEC works by measuring **stabilizers** — operators whose eigenvalues tell you about *errors* without revealing the encoded data.
3. **Errors are continuous.** A classical bit is either flipped or it isn't. A quantum error can be `e^{i 0.001 X}` — a tiny rotation. Naively this means there are uncountably many errors and we can't correct all of them. The miracle that saves QEC is **error discretization**: any error that you can correct on `{I, X, Y, Z}` you can also correct on any linear combination thereof. So fixing a code that handles single-qubit Paulis is enough to handle *any* single-qubit error.

The discretization argument is the conceptual heart of QEC. It works because measuring the stabilizers projects the noisy state onto an eigenspace of the discrete error set, after which the recovery operator is the corresponding Pauli.

## Quantum channels

A quantum channel is a linear map `E: rho -> E(rho)` on density matrices that is

- **Linear** (`E(a rho_1 + b rho_2) = a E(rho_1) + b E(rho_2)`),
- **Trace-preserving** (`Tr E(rho) = Tr rho`),
- **Completely positive** (`E ⊗ I` is positive on any extension — equivalent to "the channel produces a valid density matrix when applied to any subsystem of any larger system").

Any CPTP map admits a **Kraus representation**: there exist matrices `K_1, K_2, ..., K_m` (the *Kraus operators*) such that
```
E(rho) = sum_k K_k rho K_k^dagger,    sum_k K_k^dagger K_k = I.
```
The number of Kraus operators is at most `d^2` for a `d`-dim system. Kraus form is not unique — many different sets of `K_k` can describe the same channel — but it's the most computationally convenient form for what we need.

(Equivalent representations: **Stinespring dilation** "noisy evolution = unitary on system + environment, then trace out environment", **Choi matrix**, **superoperator / Liouville form** as a `d^2 x d^2` matrix. Each is useful in different contexts; we'll mostly stay in Kraus.)

## The channels we'll meet

### Bit-flip
```
K_0 = sqrt(1-p) I,   K_1 = sqrt(p) X
```
With probability `p`, an `X` is applied. Useful as the simplest non-trivial example; not very physical on its own. The 3-qubit repetition code is *exactly* the right code for this channel.

### Phase-flip
```
K_0 = sqrt(1-p) I,   K_1 = sqrt(p) Z
```
Mathematically identical to bit-flip after a basis change (`H X H = Z`). Models pure dephasing — loss of phase coherence with no energy loss. Far more common than pure bit-flip in real hardware.

### Depolarizing
```
K_0 = sqrt(1 - 3p/4) I,   K_X = sqrt(p/4) X,   K_Y = sqrt(p/4) Y,   K_Z = sqrt(p/4) Z
```
With probability `p` the qubit is replaced by `I/2` (the maximally mixed state); with probability `1-p` it is left alone. The most pessimistic single-qubit Pauli noise model, and the one most often used as a worst-case benchmark in QEC.

(Convention check: some authors parameterise this with `p` meaning "probability a Pauli error occurs", so the Kraus weights become `(1-p) I, (p/3) X, (p/3) Y, (p/3) Z`. The two conventions agree at the endpoints. We follow the "probability of full depolarisation" convention in `qec.channels.depolarizing` — verify with the tests.)

### Amplitude damping
```
K_0 = [[1, 0], [0, sqrt(1-gamma)]],   K_1 = [[0, sqrt(gamma)], [0, 0]]
```
T1 relaxation: the qubit decays from `|1>` to `|0>` with probability `gamma`. Crucially **non-unital** — `I/2` is not a fixed point — so it cannot be written as a probabilistic mixture of Paulis. This is the "asymmetry" of real noise: hot states relax to cold states, not the other way around.

### General Pauli channel
```
E(rho) = (1 - p_X - p_Y - p_Z) rho + p_X X rho X + p_Y Y rho Y + p_Z Z rho Z
```
Any convex combination of Paulis. A useful intermediate model: more realistic than pure bit-flip, far simpler than amplitude damping, and the kind of noise that stabilizer simulators handle natively.

## Two design patterns

**Pauli-twirling.** Almost any single-qubit channel can be turned into a Pauli channel by averaging over a uniformly-random Pauli pre/post conjugation. Useful theoretically — it lets you reduce arbitrary noise to a Pauli mixture for which stabilizer simulation is exact.

**Stochastic Pauli sampling.** When simulating a Pauli channel, instead of evolving the full density matrix, you can sample a random Pauli error per gate and propagate it. This is what stabilizer simulators do (Phase 3) and is dramatically faster than density-matrix evolution.

## Fidelity vs `p`: a sanity formula

For depolarizing noise on a pure input state `|psi>`, the channel output has fidelity
```
F(rho_out, |psi><psi|) = 1 - p/2.
```
So at `p = 0.1`, the post-channel state has fidelity `0.95`; at `p = 1`, fidelity is `0.5` (the maximally mixed state has equal overlap with any pure state). This formula is independent of `|psi>` (depolarizing is symmetric across the Bloch ball), so it shows up as a clean line in the demo plot.

This is also what we need to *beat* with QEC: a `[[n, 1, d]]` code should give a logical error rate that scales as `p^{(d+1)/2}` instead of `p` — so for a distance-3 code, sub-threshold logical-error scales like `p^2`. We'll see this in Phase 4.

## Demo

`demos/02_noise_channels.ipynb` walks through:
- Visualising channel action on the Bloch ball (the depolarizing channel shrinks the ball uniformly; amplitude damping skews it toward the north pole; phase-flip flattens the equator).
- Plotting fidelity vs `p` for each channel.
- Cross-checking our Kraus operators against `qiskit_aer.noise.depolarizing_error` and `qiskit.quantum_info.Kraus`.

The acceptance test for this phase is `tests/test_channels.py`: every channel is CPTP, the depolarizing endpoint behaviour is exact, and `apply_1q_channel` agrees with the explicit-Kronecker reference on 3-qubit GHZ inputs.
