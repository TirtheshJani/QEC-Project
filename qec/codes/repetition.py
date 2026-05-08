"""The 3-qubit repetition code: bit-flip and phase-flip variants.

This is the simplest non-trivial QEC code. It cannot correct an arbitrary
single-qubit error (it is *not* a [[3,1,3]] code in the proper QEC sense —
its distance against arbitrary Pauli noise is 1), but it correctly handles
either pure bit-flip noise (the X variant) or pure phase-flip noise (the Z
variant). It is the bridge between classical 3-bit majority voting and the
proper distance-3 codes (Shor / Steane) we'll build in Phase 5.

Encoded states (bit-flip variant):
    |0_L> = |000>,
    |1_L> = |111>,
    alpha|0_L> + beta|1_L> = alpha|000> + beta|111>.

Stabilizers (bit-flip variant): Z_0 Z_1 and Z_1 Z_2. Their joint +1 eigenspace
is span{|000>, |111>}, exactly the codespace.

We provide:
- `encode_bitflip` / `encode_phaseflip` (pure-Python state-vector helpers)
- `syndrome_bitflip` / `syndrome_phaseflip` (extract the two syndrome bits
  from a noisy state vector or from a known Pauli error)
- `recovery_pauli` (table from syndrome to Pauli correction)
- `monte_carlo_logical_error` (Pauli sampling: cheap and exact for Pauli noise)
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from qec import statevec as sv

# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------
def encode_bitflip(alpha: complex, beta: complex) -> np.ndarray:
    """Return alpha|000> + beta|111> as a 3-qubit state vector.

    Implementation: prepare |psi_0> = alpha|0> + beta|1>, then apply
    CNOT(0->1) and CNOT(0->2). This is the standard textbook encoding.
    """
    psi = np.zeros(2**3, dtype=complex)
    psi[0b000] = alpha
    psi[0b001] = beta  # qubit 0 = LSB; setting qubit 0 to |1> means basis index 1
    psi = sv.cnot(psi, control=0, target=1)
    psi = sv.cnot(psi, control=0, target=2)
    return psi


def encode_phaseflip(alpha: complex, beta: complex) -> np.ndarray:
    """Return the phase-flip-code encoding of alpha|0> + beta|1>.

    Logical states: |0_L> = |+++>, |1_L> = |--->. Realised by encoding into
    the bit-flip code and then applying H to every qubit.
    """
    psi = encode_bitflip(alpha, beta)
    for q in range(3):
        psi = sv.apply_1q(psi, sv.H, q)
    return psi


# ---------------------------------------------------------------------------
# Syndrome extraction
# ---------------------------------------------------------------------------
# The bit-flip-code syndrome is two bits:
#   s0 = parity(q0, q1)   (i.e. measurement of Z_0 Z_1)
#   s1 = parity(q1, q2)   (i.e. measurement of Z_1 Z_2)
# Each non-trivial Pauli X error maps to a unique 2-bit syndrome:
SYNDROME_TO_X_RECOVERY: dict[tuple[int, int], int | None] = {
    (0, 0): None,   # no error (or X_0 X_1 X_2, which is logical X — undetected)
    (1, 0): 0,      # X on qubit 0 only
    (1, 1): 1,      # X on qubit 1 only
    (0, 1): 2,      # X on qubit 2 only
}


def syndrome_bitflip_from_error(x_pattern: tuple[int, int, int]) -> tuple[int, int]:
    """Return the (s0, s1) syndrome that an X-error pattern would produce.

    `x_pattern[q]` is 1 iff X has been applied to qubit q. Useful for
    Monte-Carlo sampling without ever building a state vector.
    """
    if len(x_pattern) != 3:
        raise ValueError("x_pattern must have length 3")
    s0 = (x_pattern[0] ^ x_pattern[1]) & 1
    s1 = (x_pattern[1] ^ x_pattern[2]) & 1
    return s0, s1


def recovery_x(syndrome: tuple[int, int]) -> int | None:
    """Return the qubit index to apply X to (or None for no recovery)."""
    return SYNDROME_TO_X_RECOVERY[tuple(syndrome)]


# ---------------------------------------------------------------------------
# Logical-error analysis (Pauli noise — bit-flip channel)
# ---------------------------------------------------------------------------
def logical_error_after_recovery(error_pattern: tuple[int, int, int]) -> int:
    """Return 1 iff applying the syndrome-table recovery leaves a logical X
    on the encoded qubit, else 0.

    Logical X for the bit-flip code is X_0 X_1 X_2 (any odd-weight X is
    equivalent to logical X modulo the stabilizer group). After recovery,
    the *remaining* X pattern is the original XOR the recovery's
    single-qubit correction.
    """
    s = syndrome_bitflip_from_error(error_pattern)
    rec = recovery_x(s)
    after = list(error_pattern)
    if rec is not None:
        after[rec] ^= 1
    # Logical X iff total weight is odd.
    return sum(after) & 1


def analytic_logical_error_rate(p: float) -> float:
    """Analytic logical X error rate for the 3-qubit bit-flip code under
    independent X errors at rate p per qubit.

    Decoding succeeds iff at most one qubit fails: P(success) = (1-p)^3 + 3 p (1-p)^2.
    P(fail)   = 3 p^2 (1-p) + p^3 = 3 p^2 - 2 p^3.
    """
    return 3 * p**2 - 2 * p**3


def monte_carlo_logical_error(
    p: float, shots: int, rng: np.random.Generator | None = None
) -> float:
    """Estimate logical-error rate by sampling the bit-flip channel."""
    rng = rng or np.random.default_rng()
    if shots <= 0:
        raise ValueError("shots must be > 0")
    # Each row of `errs` is an independent bit-flip pattern on 3 qubits.
    errs = (rng.random(size=(shots, 3)) < p).astype(np.int8)
    s0 = errs[:, 0] ^ errs[:, 1]
    s1 = errs[:, 1] ^ errs[:, 2]
    after = errs.copy()
    # Apply syndrome-table recoveries vectorised.
    mask_q0 = (s0 == 1) & (s1 == 0)
    mask_q1 = (s0 == 1) & (s1 == 1)
    mask_q2 = (s0 == 0) & (s1 == 1)
    after[mask_q0, 0] ^= 1
    after[mask_q1, 1] ^= 1
    after[mask_q2, 2] ^= 1
    logical_failures = (after.sum(axis=1) & 1).astype(np.float64)
    return float(logical_failures.mean())


# ---------------------------------------------------------------------------
# Inject errors and verify recovery on a real state vector
# ---------------------------------------------------------------------------
def apply_x_pattern(psi: np.ndarray, x_pattern: Iterable[int]) -> np.ndarray:
    for q, do in enumerate(x_pattern):
        if do:
            psi = sv.apply_1q(psi, sv.X, q)
    return psi


def measure_zz_parity(psi: np.ndarray, q0: int, q1: int) -> tuple[int, np.ndarray]:
    """Z_q0 Z_q1 has eigenvalues +/-1. The +1 eigenspace is span of basis
    states with q0 ^ q1 == 0; the -1 eigenspace has q0 ^ q1 == 1.

    Implementation note: for a *codespace* state the result is deterministic
    (the parity is a stabilizer's eigenvalue, and the codespace is the +1
    joint eigenspace). After noise, the parity tells us about the error and
    the projected state is the post-syndrome state.

    Returns (parity, post-projection state).
    """
    n = int(np.log2(psi.size))
    even_amp = np.zeros_like(psi)
    odd_amp = np.zeros_like(psi)
    for k in range(2**n):
        bit_q0 = (k >> q0) & 1
        bit_q1 = (k >> q1) & 1
        if bit_q0 ^ bit_q1 == 0:
            even_amp[k] = psi[k]
        else:
            odd_amp[k] = psi[k]
    even_p = float(np.sum(np.abs(even_amp) ** 2))
    if even_p > 1 - 1e-12:
        return 0, even_amp / np.sqrt(even_p)
    if even_p < 1e-12:
        odd_p = 1.0 - even_p
        return 1, odd_amp / np.sqrt(odd_p)
    # Mixed: return both branches by sampling — but in this module we only
    # use this for codespace states, where one branch has zero weight.
    raise RuntimeError(f"Z_{q0}Z_{q1} parity is non-deterministic (P_even={even_p})")


def round_trip_with_x_error(
    alpha: complex, beta: complex, x_pattern: tuple[int, int, int]
) -> tuple[np.ndarray, tuple[int, int]]:
    """End-to-end: encode, inject X errors, extract syndrome, recover.

    Returns (final 3-qubit state, syndrome bits). For weight <= 1 errors the
    final state must equal the noiseless encoded state.
    """
    psi = encode_bitflip(alpha, beta)
    psi = apply_x_pattern(psi, x_pattern)
    s0, _ = measure_zz_parity(psi, 0, 1)
    s1, _ = measure_zz_parity(psi, 1, 2)
    rec = recovery_x((s0, s1))
    if rec is not None:
        psi = sv.apply_1q(psi, sv.X, rec)
    return psi, (s0, s1)
