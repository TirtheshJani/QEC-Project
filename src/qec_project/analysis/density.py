"""Density-matrix helpers: validation and partial trace.

Density matrices are the right object for representing the state of a
subsystem of an entangled register and for tracking what happens under
noise. The two helpers here are introduced in Phase 1.3 and reused
throughout Phases 2-4:

* :func:`is_density_matrix` checks Hermiticity, unit trace, and
  positive-semi-definiteness.
* :func:`partial_trace` traces out one subsystem of a bipartite (or
  multipartite) register, producing the reduced density matrix on the
  remaining subsystem(s). The convention matches
  :func:`qec_project.linalg.tensor` (Kronecker / big-endian: first
  factor is the most-significant qubit).

References (in ``docs/reading-list.md``):

* Nielsen and Chuang, *Quantum Computation and Quantum Information*,
  chapter 2 (density operator), Box 2.6 (partial trace).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

_DENSITY_TOL = 1e-9


def is_density_matrix(rho: np.ndarray, atol: float = _DENSITY_TOL) -> bool:
    """Return True iff ``rho`` is Hermitian, trace 1, and positive semi-definite.

    Positive semi-definiteness is checked by computing the smallest
    eigenvalue of the Hermitised matrix; we allow a small negative slack
    of ``atol`` for floating-point error.
    """
    arr = np.asarray(rho, dtype=np.complex128)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        return False
    if not np.allclose(arr, arr.conj().T, atol=atol):
        return False
    if abs(np.trace(arr).real - 1.0) > atol or abs(np.trace(arr).imag) > atol:
        return False
    # Smallest eigenvalue of the (Hermitised) matrix must be >= -atol.
    eigvals = np.linalg.eigvalsh((arr + arr.conj().T) / 2.0)
    return bool(eigvals.min() >= -atol)


def partial_trace(
    rho: np.ndarray,
    keep: Sequence[int] | int,
    dims: Sequence[int],
) -> np.ndarray:
    """Trace out the subsystems not in ``keep`` from a multipartite ``rho``.

    Parameters
    ----------
    rho:
        Density matrix on a tensor-product space with subsystem
        dimensions ``dims``. Shape must be ``(prod(dims), prod(dims))``.
    keep:
        Subsystem index, or sequence of indices, to **keep**. Indices
        refer to positions in ``dims`` (most-significant factor first,
        matching :func:`qec_project.linalg.tensor`).
    dims:
        Tuple of subsystem dimensions, e.g. ``(2, 2)`` for two qubits.

    Returns
    -------
    np.ndarray
        Reduced density matrix on the kept subsystems with shape
        ``(prod(kept_dims), prod(kept_dims))``.

    Examples
    --------
    For a Bell state ``|Phi+> = (|00> + |11>) / sqrt(2)``, the reduced
    density on either qubit is ``I / 2``:

        >>> rho = ...  # bell state outer product
        >>> partial_trace(rho, keep=0, dims=(2, 2))  # -> I/2
    """
    arr = np.asarray(rho, dtype=np.complex128)
    dim_list = [int(d) for d in dims]
    total = int(np.prod(dim_list))
    if arr.shape != (total, total):
        raise ValueError(
            f"rho shape {arr.shape} inconsistent with dims {tuple(dim_list)} "
            f"(expected ({total}, {total}))"
        )
    n_sys = len(dim_list)
    keep_list = [keep] if isinstance(keep, int) else sorted(int(k) for k in keep)
    for k in keep_list:
        if not 0 <= k < n_sys:
            raise ValueError(f"keep index {k} out of range for {n_sys} subsystems")
    trace_list = [i for i in range(n_sys) if i not in keep_list]

    # Reshape rho into a 2 * n_sys tensor: (row_0, row_1, ..., col_0, col_1, ...).
    tensor_shape = dim_list + dim_list
    rho_t = arr.reshape(tensor_shape)

    # Sum the diagonal across each subsystem we trace out. Indices on the
    # row side are 0..n_sys-1; the matching col-side index is i + n_sys.
    for sys in sorted(trace_list, reverse=True):
        rho_t = np.trace(rho_t, axis1=sys, axis2=sys + (rho_t.ndim // 2))

    kept_dim = int(np.prod([dim_list[i] for i in keep_list])) if keep_list else 1
    return rho_t.reshape(kept_dim, kept_dim)
