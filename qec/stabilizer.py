"""Aaronson-Gottesman tableau simulator (CHP).

A pure-Python implementation of the algorithm in
    Aaronson & Gottesman, *Improved Simulation of Stabilizer Circuits*,
    Phys. Rev. A 70, 052328 (2004), https://arxiv.org/abs/quant-ph/0406196.

The state of n qubits is encoded by a (2n+1) x (2n+1) binary tableau:
    rows  0 .. n-1   : destabilizer generators g_1, ..., g_n
    rows  n .. 2n-1  : stabilizer    generators s_1, ..., s_n
    row   2n         : scratch row used during deterministic measurement
    cols  0 .. n-1   : x bits  (one per qubit, leftmost = qubit 0)
    cols  n .. 2n-1  : z bits  (one per qubit, leftmost = qubit 0)
    col   2n         : sign bit r in {0, 1}, meaning row represents (-1)^r * Pauli

Each row encodes a Pauli operator P = (-1)^r X^x Z^z (no factor of i; with
this encoding 'Y' is represented by x=z=1 and a sign comes from any prior
multiplications via the rowsum function below). The simulator is exact for
Clifford circuits and Z-basis projective measurements; sampling is exact and
classical-polynomial-time. It cannot represent non-Clifford gates (T) or
arbitrary states.

Qubit-index convention: qubit 0 is the leftmost column of x and z, matching
qec.pauli (and the AG paper). Cross-checking against qec.statevec uses the
matrix() method on extracted Pauli generators, which converts to the
qec.statevec LSB convention.
"""

from __future__ import annotations

import numpy as np

from qec.pauli import Pauli


def _g(x1: int, z1: int, x2: int, z2: int) -> int:
    """The function g from Aaronson-Gottesman, Eq. (3) of the 2004 paper.

    Returns the exponent of i (mod 4) that comes from multiplying two
    single-qubit Pauli factors X^x1 Z^z1 * X^x2 Z^z2 in the AG (no-i)
    convention, *after* combining x and z bits via XOR.

    The output is in {-1, 0, +1} expressed as 0/1/3 (we'll use it in mod-4
    arithmetic and only ever care about the parity of the running sum / 2).
    """
    if x1 == 0 and z1 == 0:
        return 0
    if x1 == 1 and z1 == 1:
        return z2 - x2  # in {-1, 0, +1}
    if x1 == 1 and z1 == 0:
        return z2 * (2 * x2 - 1)  # 0 or +/-1
    # x1 == 0 and z1 == 1
    return x2 * (1 - 2 * z2)


class StabilizerState:
    """An n-qubit stabilizer state, evolved by Clifford gates and measurements.

    Methods mutate the tableau in place and (where useful) return values:
    `measure` returns the binary outcome.
    """

    __slots__ = ("n", "tab")

    def __init__(self, n: int):
        if n < 1:
            raise ValueError("n must be >= 1")
        self.n = n
        # (2n+1) rows x (2n+1) cols of int8 in {0, 1}. Row layout:
        #   rows 0..n-1  : destabilizers
        #   rows n..2n-1 : stabilizers
        #   row 2n       : scratch
        # Col layout: x[0..n-1], z[0..n-1], r.
        T = np.zeros((2 * n + 1, 2 * n + 1), dtype=np.int8)
        # Initialise to |0...0>: destabilizer i is X_i, stabilizer i is Z_i.
        for i in range(n):
            T[i, i] = 1                 # destabilizer x bit
            T[n + i, n + i] = 1         # stabilizer z bit
        self.tab = T

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _x(self, i: int, q: int) -> int:
        return int(self.tab[i, q])

    def _z(self, i: int, q: int) -> int:
        return int(self.tab[i, self.n + q])

    def _r(self, i: int) -> int:
        return int(self.tab[i, 2 * self.n])

    def _rowsum(self, h: int, i: int) -> None:
        """Set row h := row h * row i (Aaronson-Gottesman, Eq. (4))."""
        n = self.n
        # Sign update: count the imaginary factors.
        sum_g = 0
        for q in range(n):
            sum_g += _g(self._x(i, q), self._z(i, q), self._x(h, q), self._z(h, q))
        total = 2 * self._r(h) + 2 * self._r(i) + sum_g
        # total mod 4 is in {0, 2}; the new sign bit is total/2 mod 2.
        new_r = (total % 4) // 2
        self.tab[h, 2 * n] = new_r
        # x and z bits XOR.
        self.tab[h, : 2 * n] ^= self.tab[i, : 2 * n]

    # ------------------------------------------------------------------
    # Clifford gates
    # ------------------------------------------------------------------
    def h(self, q: int) -> None:
        """Hadamard on qubit q. AG Table I row "H"."""
        if not 0 <= q < self.n:
            raise ValueError(f"qubit {q} out of range")
        n = self.n
        T = self.tab
        # For every row: r ^= x_q * z_q; then swap x_q <-> z_q.
        x_col = T[: 2 * n, q].astype(np.int8)
        z_col = T[: 2 * n, n + q].astype(np.int8)
        T[: 2 * n, 2 * n] ^= (x_col & z_col)
        T[: 2 * n, q], T[: 2 * n, n + q] = z_col.copy(), x_col.copy()

    def s(self, q: int) -> None:
        """Phase gate on qubit q. AG Table I row "S"."""
        if not 0 <= q < self.n:
            raise ValueError(f"qubit {q} out of range")
        n = self.n
        T = self.tab
        x_col = T[: 2 * n, q]
        z_col = T[: 2 * n, n + q]
        T[: 2 * n, 2 * n] ^= (x_col & z_col)
        T[: 2 * n, n + q] = (z_col ^ x_col).astype(np.int8)

    def x(self, q: int) -> None:
        """Pauli X on qubit q. Equivalently H S^2 H. We update r directly."""
        if not 0 <= q < self.n:
            raise ValueError(f"qubit {q} out of range")
        # X = H Z H = H (S^2) H. Easier: X anticommutes with Z, so the only
        # effect on the tableau is to flip r for any row whose z_q = 1.
        n = self.n
        T = self.tab
        T[: 2 * n, 2 * n] ^= T[: 2 * n, n + q]

    def z(self, q: int) -> None:
        """Pauli Z on qubit q. Flips r for any row whose x_q = 1."""
        if not 0 <= q < self.n:
            raise ValueError(f"qubit {q} out of range")
        n = self.n
        T = self.tab
        T[: 2 * n, 2 * n] ^= T[: 2 * n, q]

    def y(self, q: int) -> None:
        """Pauli Y on qubit q (= i X Z). Flip r if x_q xor z_q is 1."""
        # Y anticommutes with both X and Z (and commutes with Y).
        # For a row Pauli P = X^x Z^z, conjugating by Y flips the sign iff
        # P anticommutes with Y, i.e. iff x_q ^ z_q == 1 (X and Z, but not Y or I).
        if not 0 <= q < self.n:
            raise ValueError(f"qubit {q} out of range")
        n = self.n
        T = self.tab
        T[: 2 * n, 2 * n] ^= (T[: 2 * n, q] ^ T[: 2 * n, n + q])

    def cnot(self, control: int, target: int) -> None:
        """CNOT with given control and target. AG Table I row "CNOT"."""
        if control == target:
            raise ValueError("CNOT control and target must differ")
        if not (0 <= control < self.n and 0 <= target < self.n):
            raise ValueError("qubit out of range")
        n = self.n
        a, b = control, target
        T = self.tab
        # r ^= x_a * z_b * (x_b ^ z_a ^ 1)
        x_a = T[: 2 * n, a]
        z_a = T[: 2 * n, n + a]
        x_b = T[: 2 * n, b]
        z_b = T[: 2 * n, n + b]
        T[: 2 * n, 2 * n] ^= (x_a & z_b & (x_b ^ z_a ^ 1)).astype(np.int8)
        # x_b ^= x_a; z_a ^= z_b
        T[: 2 * n, b] = (x_b ^ x_a).astype(np.int8)
        T[: 2 * n, n + a] = (z_a ^ z_b).astype(np.int8)

    def cz(self, q0: int, q1: int) -> None:
        """CZ via H-CNOT-H on the target."""
        self.h(q1)
        self.cnot(q0, q1)
        self.h(q1)

    def swap(self, q0: int, q1: int) -> None:
        """SWAP via 3 CNOTs."""
        self.cnot(q0, q1)
        self.cnot(q1, q0)
        self.cnot(q0, q1)

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------
    def measure(self, q: int, rng: np.random.Generator | None = None) -> int:
        """Project qubit q in the Z basis; return 0 or 1.

        Implementation follows Aaronson-Gottesman exactly: find a stabilizer
        row that anticommutes with Z_q (random outcome) or fall back to the
        deterministic-outcome path.
        """
        rng = rng or np.random.default_rng()
        n = self.n
        T = self.tab

        # Find a stabilizer row p in [n, 2n) with x[p, q] == 1.
        p = -1
        for i in range(n, 2 * n):
            if T[i, q] == 1:
                p = i
                break

        if p >= 0:
            # Random outcome.
            for i in range(2 * n):
                if i != p and T[i, q] == 1:
                    self._rowsum(i, p)
            # Move stabilizer p down to destabilizer p - n; new stabilizer is Z_q +/- 1.
            T[p - n, : 2 * n + 1] = T[p, : 2 * n + 1]
            T[p, : 2 * n + 1] = 0
            outcome = int(rng.integers(0, 2))
            T[p, n + q] = 1
            T[p, 2 * n] = outcome
            return outcome

        # Deterministic outcome: zero the scratch row and multiply in any
        # stabilizer corresponding to a destabilizer that has x[i, q] == 1.
        T[2 * n, :] = 0
        for i in range(n):
            if T[i, q] == 1:
                self._rowsum(2 * n, n + i)
        return int(T[2 * n, 2 * n])

    def sample(self, shots: int, rng: np.random.Generator | None = None) -> np.ndarray:
        """Take `shots` independent samples by copying the tableau and
        measuring every qubit. Returns an array of shape (shots, n) of bits."""
        rng = rng or np.random.default_rng()
        out = np.empty((shots, self.n), dtype=np.int8)
        for s in range(shots):
            other = self.copy()
            for q in range(self.n):
                out[s, q] = other.measure(q, rng=rng)
        return out

    # ------------------------------------------------------------------
    # Inspection / interop
    # ------------------------------------------------------------------
    def copy(self) -> StabilizerState:
        new = StabilizerState.__new__(StabilizerState)
        new.n = self.n
        new.tab = self.tab.copy()
        return new

    def stabilizer_generators(self) -> list[Pauli]:
        """Return the n stabilizer generators as Pauli objects.

        The AG tableau stores rows in (-1)^r X^x Z^z form (no implicit i).
        To convert to the qec.pauli i^phase X^x Z^z encoding, each Y-like
        position (x=z=1) needs an explicit +i in the phase, plus the row's
        sign bit r contributes a factor of (-1)^r = i^(2r).
        """
        out = []
        for row in range(self.n, 2 * self.n):
            x = self.tab[row, : self.n].astype(np.int8).copy()
            z = self.tab[row, self.n : 2 * self.n].astype(np.int8).copy()
            r = int(self.tab[row, 2 * self.n])
            # AG convention: a row (x, z, r) names the Pauli (-1)^r * (tensor
            # of I/X/Y/Z chosen by each (x_q, z_q)). To translate into our
            # `i^phase * X^x Z^z` encoding we need to absorb one factor of
            # i per Y position (since Y = i X Z), plus the (-1)^r sign as 2r.
            n_y = int(np.sum(x & z))
            phase = (2 * r + n_y) & 3
            out.append(Pauli(x, z, phase))
        return out

    def destabilizer_generators(self) -> list[Pauli]:
        out = []
        for row in range(self.n):
            x = self.tab[row, : self.n].astype(np.int8).copy()
            z = self.tab[row, self.n : 2 * self.n].astype(np.int8).copy()
            r = int(self.tab[row, 2 * self.n])
            n_y = int(np.sum(x & z))
            phase = (2 * r + n_y) & 3
            out.append(Pauli(x, z, phase))
        return out

    def to_statevector(self) -> np.ndarray:
        """Reconstruct the (2^n,) state vector from the tableau.

        For pedagogy / cross-checking only — exponential in n. Method: build
        the rank-1 projector
            P = prod_k (I + s_k) / 2
        onto the joint +1 eigenspace of all n stabilizer generators. The
        stabilizer state is the unique unit vector in the image of P; pick
        whichever column of P has the largest norm and normalise.

        Global phase is fixed by an arbitrary convention (the largest non-
        zero amplitude is real positive). State-vector cross-checks should
        compare absolute amplitudes, not signed ones.
        """
        n = self.n
        dim = 2**n
        P = np.eye(dim, dtype=complex)
        for s_gen in self.stabilizer_generators():
            P = ((np.eye(dim, dtype=complex) + s_gen.matrix()) / 2) @ P
        # P is rank 1 and Hermitian; any column with non-zero norm is parallel
        # to the stabilizer state.
        norms = np.linalg.norm(P, axis=0)
        col = int(np.argmax(norms))
        psi = P[:, col]
        psi = psi / np.linalg.norm(psi)
        # Fix global phase: largest |amp| made real positive.
        k = int(np.argmax(np.abs(psi)))
        if abs(psi[k]) > 1e-12:
            psi = psi * np.conj(psi[k]) / np.abs(psi[k])
        return psi
