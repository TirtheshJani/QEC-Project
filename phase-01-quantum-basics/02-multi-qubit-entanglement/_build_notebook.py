"""One-shot generator for ``multi_qubit.ipynb``.

Run once:

    python -m uv run python phase-01-quantum-basics/02-multi-qubit-entanglement/_build_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / "multi_qubit.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


cells: list[nbf.NotebookNode] = []

cells.append(
    md(
        """# Phase 1.2 — Multi-qubit states, Bell states, superdense coding, teleportation

Second Phase 1 notebook. Goal: get fluent with tensor products, Bell
states, and the two famous two-qubit protocols (superdense coding and
teleportation). Qiskit and `qiskit_aer.AerSimulator` enter the
curriculum here for the first time.

Outline:

1. Multi-qubit state vectors and the basis-ordering conventions of
   `numpy.kron` (Phase 0.1: big-endian) and Qiskit (little-endian).
2. The four Bell states built by hand with `numpy.kron`, then via
   Qiskit, with a `Statevector` cross-check.
3. Superdense coding: 2 classical bits over 1 qubit using a shared
   Bell pair. Run on `AerSimulator` for all four 2-bit messages with
   1000 shots each; verify perfect decode.
4. Teleportation: standard 3-qubit circuit with classical feed-forward
   via `if_test`. Prepare a random one-qubit state, teleport it, and
   confirm via Statevector that qubit 2 matches the original (modulo
   the classically conditioned Pauli corrections).

Reuses `qec_project.linalg` (`PAULI_X/Z`, `PAULIS`, `tensor`).

References (in `docs/reading-list.md`):
- Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  sections 1.3 (multi-qubit), 1.3.7 (superdense coding), 1.3.6
  (teleportation), 4.4 (universality of gates).
"""
    )
)

cells.append(
    code(
        """import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import Statevector, partial_trace, random_statevector
from qiskit_aer import AerSimulator

from qec_project.linalg import tensor

rng = np.random.default_rng(0)
np.set_printoptions(precision=4, suppress=True)
"""
    )
)

cells.append(
    md(
        """## 1. Multi-qubit states and basis ordering

For two qubits A, B,

$$|\\psi\\rangle_{AB} = \\sum_{i,j \\in \\{0,1\\}} c_{ij}\\, |i\\rangle_A \\otimes |j\\rangle_B,$$

so the joint state lives in `C^4`. There are two ordering conventions
in common use, and *they disagree*. Phase 0.1 pinned the convention for
`numpy.kron`:

* **`numpy.kron` is big-endian** (a.k.a. Kronecker ordering). The
  first factor is the most-significant qubit:
  `numpy.kron(|q0>, |q1>) = |q0 q1>` with index `2 * q0 + q1`. So
  `kron(|0>, |1>) = (0, 1, 0, 0)^T`, the index-`01` basis vector.
* **Qiskit is little-endian** in its display strings and in its
  `Statevector` ordering. Bitstring `'q_{n-1} ... q_1 q_0'`: qubit 0
  is the rightmost. For two qubits, Qiskit's basis index is
  `2 * q1 + q0`, i.e. the *reverse* of `numpy.kron`.

We reconcile by either reversing one of the two state vectors, or by
preparing the Qiskit circuit so that qubit indices on the Qiskit side
match the qubits we wrote on the math side. Throughout this notebook
we use `qec_project.linalg.tensor` (which is `numpy.kron`) on the
hand-computed side and reverse the Qiskit `Statevector` before
comparison.
"""
    )
)

cells.append(
    code(
        """ket_0 = np.array([[1.0], [0.0]], dtype=np.complex128)
ket_1 = np.array([[0.0], [1.0]], dtype=np.complex128)

# numpy.kron is big-endian: kron(|0>, |1>) puts the 1 at index 0*2+1 = 1.
v = tensor(ket_0, ket_1).ravel()
print(f"tensor(|0>, |1>) =\\n{v}")
print(f"non-zero index   = {int(np.argmax(np.abs(v)))} (basis state |01>)")
"""
    )
)

cells.append(
    md(
        """## 2. The four Bell states

The Bell states are the maximally entangled basis of `C^2 \\otimes C^2`:

$$|\\Phi^+\\rangle = \\tfrac{1}{\\sqrt{2}} (|00\\rangle + |11\\rangle), \\quad
  |\\Phi^-\\rangle = \\tfrac{1}{\\sqrt{2}} (|00\\rangle - |11\\rangle),$$
$$|\\Psi^+\\rangle = \\tfrac{1}{\\sqrt{2}} (|01\\rangle + |10\\rangle), \\quad
  |\\Psi^-\\rangle = \\tfrac{1}{\\sqrt{2}} (|01\\rangle - |10\\rangle).$$

Construct them by hand with `tensor`, then check orthonormality, then
build them with Qiskit and confirm via `Statevector` (after reversing
to match our big-endian convention).
"""
    )
)

cells.append(
    code(
        """ket_00 = tensor(ket_0, ket_0)
ket_01 = tensor(ket_0, ket_1)
ket_10 = tensor(ket_1, ket_0)
ket_11 = tensor(ket_1, ket_1)

phi_plus  = (ket_00 + ket_11) / np.sqrt(2.0)
phi_minus = (ket_00 - ket_11) / np.sqrt(2.0)
psi_plus  = (ket_01 + ket_10) / np.sqrt(2.0)
psi_minus = (ket_01 - ket_10) / np.sqrt(2.0)

bell = {
    "Phi+": phi_plus,
    "Phi-": phi_minus,
    "Psi+": psi_plus,
    "Psi-": psi_minus,
}

# Orthonormality check: <B_i | B_j> = delta_ij.
labels = list(bell)
inner = np.zeros((4, 4), dtype=np.complex128)
for i, a in enumerate(labels):
    for j, b in enumerate(labels):
        inner[i, j] = complex((bell[a].conj().T @ bell[b]).item())
print("|<B_i | B_j>|:")
print(np.abs(inner))
"""
    )
)

cells.append(
    md(
        """The inner-product matrix is the 4x4 identity, so the Bell states form
an orthonormal basis. Now build each one in Qiskit.

The standard preparation for `|Phi+>` is

```
q0: ---H---*---
            |
q1: -------X---
```

(Hadamard on qubit 0, then CNOT(0, 1)). The other three are obtained
by applying an `X` or `Z` to qubit 0 or 1 before the H+CNOT pair:

| Target  | Preparation                                           |
|---------|-------------------------------------------------------|
| `Phi+`  | H(0), CX(0, 1)                                        |
| `Phi-`  | X(0), H(0), CX(0, 1)                                  |
| `Psi+`  | X(1), H(0), CX(0, 1)                                  |
| `Psi-`  | X(0), X(1), H(0), CX(0, 1)                            |

We construct each circuit, take its `Statevector`, reverse the index
ordering to match `numpy.kron`, and compare to the hand-computed Bell
state up to a possible global phase (we test by computing
`|<psi_hand | psi_qiskit>|`, which should be 1.0).
"""
    )
)

cells.append(
    code(
        """def bell_circuit(label: str) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    if label in ("Phi-", "Psi-"):
        qc.x(0)
    if label in ("Psi+", "Psi-"):
        qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def qiskit_to_bigendian(sv: Statevector) -> np.ndarray:
    \"\"\"Reverse Qiskit's little-endian basis ordering to numpy.kron's big-endian.\"\"\"
    data = sv.data
    n = int(np.log2(data.size))
    return data.reshape([2] * n).transpose(*range(n - 1, -1, -1)).reshape(-1)


print(f"{'state':>5}  |<hand | qiskit>|")
for label, target in bell.items():
    qc = bell_circuit(label)
    sv = Statevector(qc)
    rev = qiskit_to_bigendian(sv)
    overlap = abs(complex(target.ravel().conj() @ rev))
    print(f"{label:>5}  {overlap:.6f}")
    assert overlap > 1 - 1e-12, f"Bell state mismatch for {label}"
print("\\nall four Bell circuits match the hand-computed states to 1e-12")
"""
    )
)

cells.append(
    md(
        """## 3. Superdense coding

Alice wants to send Bob a 2-bit classical message using only 1 qubit.
She and Bob pre-share a Bell pair `|Phi+>`. Alice's two message bits
`(z_bit, x_bit)` select one of four local operations on her qubit:

| `(z, x)` | operation on Alice's qubit |
|----------|----------------------------|
| `(0, 0)` | `I`                        |
| `(0, 1)` | `X`                        |
| `(1, 0)` | `Z`                        |
| `(1, 1)` | `Z X`                      |

Then she sends her qubit to Bob. Bob undoes the Bell preparation
(`CNOT(alice, bob)` then `H` on Alice) and measures both qubits.
After the decode, Alice's classical bit `c[0]` recovers `z_bit` and
Bob's classical bit `c[1]` recovers `x_bit`. (Intuition: an X-flip
on Alice's qubit propagates through the CNOT onto Bob; a Z-flip on
Alice's qubit propagates through the Hadamard onto Alice's
measurement.)

We run the protocol for all four messages on `AerSimulator` with 1000
shots each, expecting every shot to recover the input message exactly.
Qiskit reports counts as `'c1 c0'` (little-endian classical register
string), so the expected key for message `(z, x)` is the string
`f"{x_bit}{z_bit}"`.
"""
    )
)

cells.append(
    code(
        """def superdense_circuit(z_bit: int, x_bit: int) -> QuantumCircuit:
    \"\"\"Alice sends a 2-bit message (z_bit, x_bit) to Bob.

    Encoding on Alice's qubit: x_bit selects an X; z_bit selects a Z.
    After Bob's Bell decode (CNOT then H on Alice), the X information
    appears on Bob's qubit (measured into ``c[1]``) and the Z information
    on Alice's qubit (measured into ``c[0]``). Qiskit reports counts as
    ``'c1 c0'`` (little-endian classical-register string), so the
    expected key for message ``(z, x)`` is the string ``f"{x}{z}"``.
    \"\"\"
    alice = QuantumRegister(1, "alice")
    bob = QuantumRegister(1, "bob")
    c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(alice, bob, c)

    # 1) Prepare Bell pair |Phi+> on (alice, bob).
    qc.h(alice[0])
    qc.cx(alice[0], bob[0])

    # 2) Alice encodes 2 bits into her qubit.
    if x_bit == 1:
        qc.x(alice[0])
    if z_bit == 1:
        qc.z(alice[0])

    # 3) Bob applies CNOT (alice -> bob) then H on alice, then measures both.
    qc.cx(alice[0], bob[0])
    qc.h(alice[0])
    qc.measure(alice[0], c[0])
    qc.measure(bob[0], c[1])
    return qc


sim = AerSimulator(seed_simulator=0)
shots = 1000

print(f"{'msg (z, x)':>11}  {'counts':>40}  ok")
for z_bit in (0, 1):
    for x_bit in (0, 1):
        qc = superdense_circuit(z_bit, x_bit)
        tqc = transpile(qc, sim)
        counts = sim.run(tqc, shots=shots).result().get_counts()
        # Qiskit count strings are 'c1 c0' little-endian; c0 == z_bit,
        # c1 == x_bit, so the expected string is f"{x_bit}{z_bit}".
        expected_key = f"{x_bit}{z_bit}"
        ok = counts.get(expected_key, 0) == shots
        label = f"({z_bit}, {x_bit})"
        print(f"{label:>11}  {counts!s:>40}  {ok}")
        assert ok, f"superdense decode failed for (z={z_bit}, x={x_bit})"

print("\\nall four messages decoded with 100% confidence at 1000 shots each")
"""
    )
)

cells.append(
    md(
        """Every shot decodes exactly to the input message: the channel is
noiseless and the Bell-basis discrimination is deterministic.
Superdense coding is the simplest demonstration that a maximally
entangled pair augments classical communication: one qubit + one
shared ebit transmits two classical bits.

## 4. Teleportation

Alice has an unknown qubit `|psi>` she wants to transfer to Bob. They
share a Bell pair `|Phi+>` on a second qubit (Alice's half) and a
third qubit (Bob's half). The protocol:

1. Alice applies CNOT(`psi`, `alice`) and H(`psi`).
2. Alice measures both her qubits, obtaining two classical bits
   `(c_psi, c_alice)`.
3. Bob applies `X^{c_alice} Z^{c_psi}` to his qubit (classical
   feed-forward). His qubit is now in state `|psi>`.

We test by preparing a random one-qubit state, running the circuit,
and using `Statevector` on the post-measurement state. Because
`Statevector(qc)` gives the wavefunction *after* measurement and
feed-forward (Qiskit handles this for circuits with classical
operations as long as we use the path through `qc.save_statevector` or
equivalent — the simpler approach is to *not* measure and instead
verify the corrections by inspecting the conditional branches).

Cleanest verification path used here: simulate with `AerSimulator`'s
statevector method and `save_statevector` to capture the final
state on all three qubits, then partial-trace down to qubit 2 (Bob's)
and compare to `|psi><psi|` via the trace-distance / overlap.
"""
    )
)

cells.append(
    code(
        """def teleportation_circuit(psi_data: np.ndarray) -> QuantumCircuit:
    \"\"\"Standard 3-qubit teleportation. psi_data is a length-2 statevector.\"\"\"
    qpsi = QuantumRegister(1, "psi")
    qa = QuantumRegister(1, "alice")
    qb = QuantumRegister(1, "bob")
    c_psi = ClassicalRegister(1, "c_psi")
    c_alice = ClassicalRegister(1, "c_alice")
    qc = QuantumCircuit(qpsi, qa, qb, c_psi, c_alice)

    # Prepare |psi> on qpsi.
    qc.initialize(psi_data, qpsi[0])

    # Prepare Bell pair |Phi+> on (qa, qb).
    qc.h(qa[0])
    qc.cx(qa[0], qb[0])

    # Alice's basis change and measurement.
    qc.cx(qpsi[0], qa[0])
    qc.h(qpsi[0])
    qc.measure(qpsi[0], c_psi[0])
    qc.measure(qa[0], c_alice[0])

    # Bob's classically conditioned corrections.
    with qc.if_test((c_alice, 1)):
        qc.x(qb[0])
    with qc.if_test((c_psi, 1)):
        qc.z(qb[0])

    qc.save_statevector()
    return qc


# Prepare a random one-qubit state and teleport it.
target = random_statevector(2, seed=7)
psi_data = target.data

sim_sv = AerSimulator(method="statevector", seed_simulator=0)
qc = teleportation_circuit(psi_data)
tqc = transpile(qc, sim_sv)
result = sim_sv.run(tqc).result()
final_sv = result.get_statevector()

# Reduce to Bob's qubit (qubit index 2 in Qiskit's little-endian register).
rho_bob = partial_trace(final_sv, [0, 1])
fidelity = float((target.data.conjugate() @ rho_bob.data @ target.data).real)

print(f"random |psi> components: alpha = {psi_data[0]:.4f}, beta = {psi_data[1]:.4f}")
print(f"teleportation fidelity F = <psi | rho_bob | psi> = {fidelity:.6f}")
assert fidelity > 1 - 1e-9, f"teleportation fidelity too low: {fidelity}"
"""
    )
)

cells.append(
    md(
        """Fidelity 1.0 (to numerical precision): Bob's qubit ends up in exactly
the same state Alice started with. Note that no qubit *moved* in any
physical sense; only two classical bits and a pre-shared ebit were
consumed.

## Recap

* Two-qubit (and n-qubit) state vectors live in `C^{2^n}` with two
  rival ordering conventions: big-endian (`numpy.kron`,
  `qec_project.linalg.tensor`) and little-endian (Qiskit). We
  reconciled by reversing the index ordering on the Qiskit side.
* The four Bell states were built two ways and matched to numerical
  precision.
* Superdense coding sends 2 classical bits over 1 qubit (plus a
  pre-shared ebit), and the decoded counts were 100% correct for all
  four messages at 1000 shots.
* Teleportation transfers an unknown qubit state using 2 classical
  bits and a pre-shared ebit; verified by an exact-statevector
  simulation followed by partial trace to Bob's qubit.

**Next: Phase 1.3.** Density matrices, partial trace, Kraus
operators, and the three single-qubit noise channels that will
become the workhorse of Phase 2's stabilizer-formalism error models.
"""
    )
)


nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.12",
    },
}

OUT.write_text(nbf.writes(nb), encoding="utf-8")
print(f"wrote {OUT}")
