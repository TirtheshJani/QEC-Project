"""The planar surface code (Phase 8 — intro only).

This module supports the *intro* level: build a `d x d` planar (rotated)
surface-code patch, expose its X- and Z-stabilizer generators as Pauli
strings, generate the matching-graph "stabilizer footprint" for a small
visualisation, and compute the syndrome of a given Pauli error pattern.

We deliberately stop short of implementing a decoder. The standard decoder
is minimum-weight perfect matching (MWPM), e.g. via PyMatching; a full
implementation is out of scope for this repo's theory-first walk-through.
The note 11 explains why MWPM works and what it costs.

Lattice convention (rotated surface code, distance d, d odd >= 3):
- d^2 data qubits arranged on a d x d grid; row-major index q = r * d + c
  for row r, col c (0-indexed).
- Z-type stabilizers ("Z plaquettes"): one per square on a checkerboard
  pattern; weight 4 in the bulk, weight 2 on the top/bottom boundaries.
- X-type stabilizers ("X plaquettes"): the alternate checkerboard squares;
  weight 4 in the bulk, weight 2 on the left/right boundaries.
- Logical Z is a vertical X-string from top to bottom on the leftmost column;
  logical X is a horizontal Z-string from left to right on the top row.

The (rotated) surface code's parameters are [[d^2, 1, d]]. The number of
stabilizer generators is d^2 - 1.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qec.pauli import Pauli


@dataclass(frozen=True)
class SurfaceCode:
    """A distance-d (rotated) planar surface code with d odd."""

    d: int

    def __post_init__(self) -> None:
        if self.d < 3 or self.d % 2 == 0:
            raise ValueError("d must be an odd integer >= 3")

    @property
    def n(self) -> int:
        """Number of data qubits."""
        return self.d * self.d

    def qubit(self, r: int, c: int) -> int:
        """Map (row, col) on the lattice to the linear qubit index."""
        if not (0 <= r < self.d and 0 <= c < self.d):
            raise IndexError(f"({r}, {c}) out of range for d = {self.d}")
        return r * self.d + c

    # ------------------------------------------------------------------
    # Stabilizer plaquettes
    # ------------------------------------------------------------------
    def _plaquette_qubits(self, r: int, c: int) -> tuple[int, ...]:
        """Return the data qubits forming the plaquette at the (r, c) face.

        Faces are indexed by their top-left data qubit, with `0 <= r, c < d-1`
        for bulk plaquettes. Boundary plaquettes have weight 2 and live on
        rows / cols where one side is missing.
        """
        d = self.d
        qubits = []
        for dr, dc in ((0, 0), (0, 1), (1, 0), (1, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < d and 0 <= cc < d:
                qubits.append(self.qubit(rr, cc))
        return tuple(qubits)

    def stabilizer_generators(self) -> tuple[list[Pauli], list[Pauli]]:
        """Return (X-stabilizers, Z-stabilizers) as Pauli objects.

        Bulk: a 2x2 face with bottom-right at (r+1, c+1). Boundary: the
        weight-2 plaquettes on the top/bottom (Z) and left/right (X) edges.

        Standard rotated-surface-code coloring:
        - X plaquettes on faces where (r + c) is even.
        - Z plaquettes on faces where (r + c) is odd.
        - The boundaries: top and bottom belong to Z; left and right to X.
        """
        d = self.d
        x_gens: list[Pauli] = []
        z_gens: list[Pauli] = []

        # Bulk plaquettes: each "face" identified by its top-left corner
        # (r, c) with 0 <= r, c <= d - 2.
        for r in range(d - 1):
            for c in range(d - 1):
                qs = self._plaquette_qubits(r, c)
                if (r + c) % 2 == 0:
                    x_gens.append(self._pauli_on(qs, kind="X"))
                else:
                    z_gens.append(self._pauli_on(qs, kind="Z"))

        # Top/bottom boundary Z-plaquettes (weight 2).
        for c in range(0, d - 1, 2):
            # Top edge: pair (0, c), (0, c+1).
            z_gens.append(self._pauli_on((self.qubit(0, c), self.qubit(0, c + 1)), kind="Z"))
            # Bottom edge: pair (d-1, c+1), (d-1, c+2) — shifted to alternate.
        for c in range(1, d - 1, 2):
            z_gens.append(self._pauli_on(
                (self.qubit(d - 1, c), self.qubit(d - 1, c + 1)), kind="Z"
            ))

        # Left/right boundary X-plaquettes (weight 2).
        for r in range(1, d - 1, 2):
            x_gens.append(self._pauli_on((self.qubit(r, 0), self.qubit(r + 1, 0)), kind="X"))
        for r in range(0, d - 1, 2):
            x_gens.append(self._pauli_on(
                (self.qubit(r, d - 1), self.qubit(r + 1, d - 1)), kind="X"
            ))

        return x_gens, z_gens

    def _pauli_on(self, qubits: tuple[int, ...], kind: str) -> Pauli:
        x = np.zeros(self.n, dtype=np.int8)
        z = np.zeros(self.n, dtype=np.int8)
        for q in qubits:
            if kind == "X":
                x[q] = 1
            elif kind == "Z":
                z[q] = 1
            else:
                raise ValueError(f"unknown kind {kind!r}")
        return Pauli(x, z, 0)

    # ------------------------------------------------------------------
    # Logical operators (computed from the stabilizer group via GF(2) linalg)
    # ------------------------------------------------------------------
    def _stabilizer_symplectic_matrix(self) -> np.ndarray:
        """Stack stabilizer generators into a (m, 2n) binary matrix [x | z]."""
        x_gens, z_gens = self.stabilizer_generators()
        rows = []
        for g in x_gens + z_gens:
            rows.append(np.concatenate([g.x, g.z]).astype(np.int8))
        return np.stack(rows)

    def _find_logicals(self) -> tuple[Pauli, Pauli]:
        """Compute (logical X, logical Z) by solving for non-stabilizer
        operators in the centralizer of the stabilizer group.

        For an [[n, k, d]] stabilizer code, the centralizer modulo the
        stabilizer group has dimension 2k (k logical X / Z pairs). For k=1
        we just need *any* non-trivial pair that anticommutes with each
        other. We find one by:
        1. Build S in GF(2) symplectic form (m x 2n).
        2. Centraliser = ker( S omega^T mod 2 ), where omega swaps x and z
           halves, so a vector v (length 2n) commutes with every row r of S
           iff (r_x . v_z + r_z . v_x) = 0 mod 2.
        3. Find a vector in the centralizer that is *not* in the row span
           of S (so it's not a stabilizer); call it L1.
        4. Find another centraliser vector that anticommutes with L1; call
           it L2.
        """
        n = self.n
        S = self._stabilizer_symplectic_matrix()  # (m, 2n)
        m = S.shape[0]

        # Build the commutation-check matrix C of shape (m, 2n) where row i
        # is (S_i_z, S_i_x) — i.e. swap halves. v commutes with S_i iff
        # C_i . v = 0 mod 2.
        C = np.concatenate([S[:, n:], S[:, :n]], axis=1) % 2

        # Solve C v = 0 over GF(2): Gaussian elimination on C, find null space.
        null_basis = _gf2_nullspace(C)

        # Now we have a basis for the centraliser of dim 2n - rank(C).
        # The stabilizer rows themselves are in this null space. We want a
        # logical = centraliser \ stabilizer.
        # Strategy: find a centraliser vector not in row(S).
        # Build augmented basis: [stabilizer rows] then [null space];
        # walk through null-space vectors, take the first that's
        # linearly independent from the stabilizer rows.
        stab_rank = _gf2_rank(S)
        assert stab_rank == m, f"stabilizer rows not independent (rank {stab_rank} < {m})"

        L1 = None
        for v in null_basis:
            if _gf2_independent(S, v):
                L1 = v
                break
        if L1 is None:
            raise RuntimeError("could not find a logical operator")

        # Find L2 in the null space that anticommutes with L1.
        L1_check = np.concatenate([L1[n:], L1[:n]]) % 2  # symplectic-check for "anticommutes with L1"
        L2 = None
        for v in null_basis:
            if int(np.dot(L1_check, v)) % 2 == 1 and _gf2_independent(np.vstack([S, L1]), v):
                L2 = v
                break
        if L2 is None:
            raise RuntimeError("could not find a partner logical operator")

        return _logical_from_vec(L1, n), _logical_from_vec(L2, n)

    def logical_x(self) -> Pauli:
        L1, _ = self._find_logicals()
        return L1

    def logical_z(self) -> Pauli:
        _, L2 = self._find_logicals()
        return L2


# ---------------------------------------------------------------------------
# GF(2) helpers
# ---------------------------------------------------------------------------
def _gf2_rank(M: np.ndarray) -> int:
    A = M.astype(np.int8) % 2
    rows, cols = A.shape
    r = 0
    for c in range(cols):
        # find a pivot in column c at row >= r
        pivot = None
        for i in range(r, rows):
            if A[i, c]:
                pivot = i
                break
        if pivot is None:
            continue
        A[[r, pivot]] = A[[pivot, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
    return r


def _gf2_nullspace(M: np.ndarray) -> list[np.ndarray]:
    """Return a list of basis vectors for {v : M v = 0 mod 2}, length M.shape[1] each."""
    A = M.astype(np.int8) % 2
    rows, cols = A.shape
    # Reduced row echelon
    pivot_cols = []
    r = 0
    for c in range(cols):
        pivot = None
        for i in range(r, rows):
            if A[i, c]:
                pivot = i
                break
        if pivot is None:
            continue
        A[[r, pivot]] = A[[pivot, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        pivot_cols.append(c)
        r += 1

    free_cols = [c for c in range(cols) if c not in pivot_cols]
    basis = []
    for free in free_cols:
        v = np.zeros(cols, dtype=np.int8)
        v[free] = 1
        # For each pivot row, set v[pivot_col] = A[pivot_row, free]
        for pr, pc in enumerate(pivot_cols):
            v[pc] = A[pr, free]
        basis.append(v)
    return basis


def _gf2_independent(rows: np.ndarray, v: np.ndarray) -> bool:
    """True iff v is linearly independent from the rows of `rows` over GF(2)."""
    M = np.vstack([rows, v[None, :]])
    return _gf2_rank(M) > _gf2_rank(rows)


def _logical_from_vec(v: np.ndarray, n: int) -> Pauli:
    return Pauli(v[:n].astype(np.int8), v[n:].astype(np.int8), 0)


# ---------------------------------------------------------------------------
# Convenience: extract the syndrome of a Pauli error
# ---------------------------------------------------------------------------
def syndrome(code: SurfaceCode, error: Pauli) -> tuple[list[int], list[int]]:
    """Return ([X-stabilizer outcomes], [Z-stabilizer outcomes]) for a Pauli
    error on the data qubits of the surface code. Each entry is 1 iff the
    corresponding stabilizer anticommutes with `error`."""
    x_gens, z_gens = code.stabilizer_generators()
    x_out = [0 if g.commutes_with(error) else 1 for g in x_gens]
    z_out = [0 if g.commutes_with(error) else 1 for g in z_gens]
    return x_out, z_out
