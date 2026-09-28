"""The 3-qubit bit-flip repetition code.

Encoding:
    a |0> + b |1>  ->  a |000> + b |111>

Stabilizers (computational basis, qubit 0 leftmost):
    S0 = Z (x) Z (x) I
    S1 = I (x) Z (x) Z

Logical operators:
    X_L = X (x) X (x) X
    Z_L = Z (x) Z (x) Z

Single-qubit X errors are detectable and uniquely identified by the
two-bit syndrome (s0, s1):
    (0, 0) -> no error (or weight-3 error on the code space)
    (1, 0) -> X on qubit 0
    (1, 1) -> X on qubit 1
    (0, 1) -> X on qubit 2

Z and Y errors are NOT corrected: a single Z is undetectable because both
stabilizers are products of Z's. This is the headline limitation that
motivates Shor 9 in Phase 2.2.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from qec_project.noise.quantum import (
    PAULI_I,
    PAULI_X,
    PAULI_Z,
    apply_channel_to_qubit,
    depolarizing_kraus,
)

# Recovery table: (s0, s1) -> qubit index to flip with X (or -1 for "no flip").
_SYNDROME_RECOVERY: dict[tuple[int, ...], int] = {
    (0, 0): -1,
    (1, 0): 0,
    (1, 1): 1,
    (0, 1): 2,
}


class ThreeQubitBitFlipCode:
    """3-qubit bit-flip repetition code with density-matrix simulation."""

    n_qubits: int = 3
    k_qubits: int = 1
    distance: int = 3

    def encode(self, state_1q: NDArray[np.complex128]) -> NDArray[np.complex128]:
        """Map a single-qubit state vector (length 2) to the 3-qubit code space.

        |0> -> |000>, |1> -> |111>, linear in between.
        """
        if state_1q.shape != (2,):
            raise ValueError(f"state_1q must have shape (2,); got {state_1q.shape}")
        out = np.zeros(8, dtype=complex)
        out[0] = state_1q[0]  # |000>
        out[7] = state_1q[1]  # |111>
        return out

    @staticmethod
    def stabilizers() -> tuple[NDArray[np.complex128], NDArray[np.complex128]]:
        """Return the two stabilizer generators as 8x8 matrices.

        S0 = Z (x) Z (x) I  detects X on qubit 0 or qubit 1.
        S1 = I (x) Z (x) Z  detects X on qubit 1 or qubit 2.
        """
        S0 = np.kron(np.kron(PAULI_Z, PAULI_Z), PAULI_I)
        S1 = np.kron(np.kron(PAULI_I, PAULI_Z), PAULI_Z)
        return S0, S1

    @staticmethod
    def logical_x() -> NDArray[np.complex128]:
        """X_L = X (x) X (x) X."""
        return np.kron(np.kron(PAULI_X, PAULI_X), PAULI_X)

    @staticmethod
    def logical_z() -> NDArray[np.complex128]:
        """Z_L = Z (x) Z (x) Z (any single Z_i acts identically on the code space)."""
        return np.kron(np.kron(PAULI_Z, PAULI_Z), PAULI_Z)

    def syndrome_extract(
        self,
        rho: NDArray[np.complex128],
        rng: np.random.Generator,
    ) -> tuple[int, int]:
        """Project rho onto a joint eigenspace of (S0, S1) and return the
        outcome (s0, s1) in {0, 1} x {0, 1}.

        The four eigenspaces partition the 8-dim Hilbert space:
            (0, 0): {|000>, |111>}     -- code space
            (1, 0): {|100>, |011>}     -- X error on qubit 0
            (1, 1): {|010>, |101>}     -- X error on qubit 1
            (0, 1): {|001>, |110>}     -- X error on qubit 2

        Outcome probabilities are read off the diagonal of rho in the
        computational basis; rng selects an outcome stochastically.

        NOTE (pedagogy): on real hardware, syndromes are measured
        non-destructively via ancilla qubits and CNOT chains. Phase 2.2
        builds that ancilla circuit explicitly in Qiskit. Here we shortcut
        through the density-matrix picture to keep the focus on what the
        syndrome means.
        """
        diag = np.real(np.diag(rho))
        diag = np.clip(diag, 0.0, None)
        total = diag.sum()
        if total <= 0:
            raise ValueError("density matrix has non-positive trace")
        probs = diag / total

        # Index bits b0 b1 b2 (b0 leftmost). Z on qubit i has eigenvalue (-1)^bi.
        # s_i = 1 when the corresponding ZZ product = -1 = (bi XOR b_{i+1}).
        idx = int(rng.choice(8, p=probs))
        b = [(idx >> 2) & 1, (idx >> 1) & 1, idx & 1]
        s0 = b[0] ^ b[1]
        s1 = b[1] ^ b[2]
        return s0, s1

    def apply_noise(
        self,
        rho: NDArray[np.complex128],
        p: float,
        rng: np.random.Generator,
    ) -> NDArray[np.complex128]:
        """Apply independent single-qubit depolarizing noise with parameter p
        to each of the 3 physical qubits.

        The depolarizing channel is deterministic on density matrices; `rng`
        is accepted to match the channel-agnostic protocol used by
        ``simulate_logical_error_rate`` and stochastic channels added later.
        """
        del rng  # see docstring
        K = depolarizing_kraus(p)
        out = rho
        for q in range(self.n_qubits):
            out = apply_channel_to_qubit(out, K, target=q, n_qubits=self.n_qubits)
        return out

    def decode(
        self,
        rho: NDArray[np.complex128],
        syndrome: tuple[int, int],
    ) -> NDArray[np.complex128]:
        """Apply the maximum-likelihood single-qubit X recovery for the
        observed syndrome and return the corrected density matrix.
        """
        q = _SYNDROME_RECOVERY.get(tuple(syndrome))
        if q is None:
            raise ValueError(f"unknown syndrome {syndrome}")
        if q == -1:
            return rho
        ops: list[NDArray[np.complex128]] = [PAULI_I, PAULI_I, PAULI_I]
        ops[q] = PAULI_X
        X_q = np.kron(np.kron(ops[0], ops[1]), ops[2])
        return X_q @ rho @ X_q.conj().T

    # Four basis logical states used to estimate the average channel infidelity.
    _LOGICAL_BASIS: tuple[tuple[str, NDArray[np.complex128]], ...] = (
        ("0", np.array([1.0, 0.0], dtype=complex)),
        ("1", np.array([0.0, 1.0], dtype=complex)),
        ("+", np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)),
        ("-", np.array([1.0, -1.0], dtype=complex) / np.sqrt(2.0)),
    )

    @staticmethod
    def _project_to_syndrome_subspace(
        rho: NDArray[np.complex128], syndrome: tuple[int, int]
    ) -> NDArray[np.complex128]:
        """Project rho onto the joint eigenspace of (S0, S1) labelled by
        syndrome and renormalize. The four eigenspaces are 2-dim and span
        pairs of computational basis states (see syndrome_extract docstring).
        """
        members: list[int] = []
        for idx in range(8):
            b0, b1, b2 = (idx >> 2) & 1, (idx >> 1) & 1, idx & 1
            s0 = b0 ^ b1
            s1 = b1 ^ b2
            if (s0, s1) == tuple(syndrome):
                members.append(idx)
        P = np.zeros((8, 8), dtype=complex)
        for m in members:
            P[m, m] = 1.0
        rho_proj = P @ rho @ P
        tr = np.real(np.trace(rho_proj))
        if tr <= 1e-15:
            return rho
        return rho_proj / tr

    def _decode_to_logical_density_matrix(
        self, rho: NDArray[np.complex128]
    ) -> NDArray[np.complex128]:
        """Project rho onto the code space {|000>, |111>} and read off the
        single-qubit (2x2) logical density matrix, renormalized.
        """
        rho_log = np.array(
            [[rho[0, 0], rho[0, 7]], [rho[7, 0], rho[7, 7]]], dtype=complex
        )
        tr = np.real(np.trace(rho_log))
        if tr <= 0:
            return 0.5 * np.eye(2, dtype=np.complex128)
        return rho_log / tr

    def simulate_logical_error_rate(
        self,
        p: float,
        n_trials: int,
        rng: np.random.Generator,
    ) -> float:
        """Monte-Carlo estimate of average logical infidelity at physical
        error rate p.

        Per trial: sample one of {|0>, |1>, |+>, |->}, encode, apply
        independent single-qubit depolarizing(p), syndrome-extract, project
        onto the matching eigenspace, decode, read out the 2x2 logical
        density matrix, then measure it in a basis containing psi: the trial
        fails with probability 1 - <psi|rho_L|psi>. (A threshold rule such as
        "fidelity < 0.5" is not an infidelity estimate, and it is decided by
        floating-point roundoff on branches where the fidelity is exactly 1/2.)
        """
        if n_trials <= 0:
            raise ValueError("n_trials must be positive")
        failures = 0
        for _ in range(n_trials):
            _, state_1q = self._LOGICAL_BASIS[int(rng.integers(0, 4))]
            psi = self.encode(state_1q)
            rho = np.outer(psi, psi.conj())
            rho = self.apply_noise(rho, p=p, rng=rng)
            syn = self.syndrome_extract(rho, rng)
            rho = self._project_to_syndrome_subspace(rho, syn)
            rho = self.decode(rho, syndrome=syn)
            rho_log = self._decode_to_logical_density_matrix(rho)
            fidelity = float(np.real(state_1q.conj() @ rho_log @ state_1q))
            if rng.random() >= fidelity:
                failures += 1
        return failures / n_trials
