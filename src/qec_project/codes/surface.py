"""Rotated surface-code memory experiments as Stim circuit factories.

Phase 3. The rotated surface code is the workhorse of the capstone decoder
benchmark. Circuits are built *programmatically* with
:func:`stim.Circuit.generated` (a CLAUDE.md rule); any ``.stim`` / ``.dem``
files are reproducibility artifacts, never inputs. The decomposed detector
error model returned by :meth:`RotatedSurfaceCode.detector_error_model` is the
object every decoder in :mod:`qec_project.decoders` consumes.

References (in ``docs/reading-list.md``):

* A. G. Fowler, M. Mariantoni, J. M. Martinis, A. N. Cleland. *Surface codes:
  Towards practical large-scale quantum computation.* Phys. Rev. A 86, 032324
  (2012). doi:10.1103/PhysRevA.86.032324.
* C. Gidney. *Stim: a fast stabilizer circuit simulator.* Quantum 5, 497
  (2021). doi:10.22331/q-2021-07-06-497.
"""

from __future__ import annotations

from dataclasses import dataclass

import stim

from qec_project.noise.circuit import CircuitNoise

_MEMORY_TASK = {
    "Z": "surface_code:rotated_memory_z",
    "X": "surface_code:rotated_memory_x",
}


@dataclass(frozen=True, slots=True)
class RotatedSurfaceCode:
    """A rotated-surface-code memory experiment ``[[d^2, 1, d]]``.

    Parameters
    ----------
    distance:
        Code distance ``d``; an odd integer ``>= 3``. The code uses ``d**2``
        data qubits and ``d**2 - 1`` measure qubits and protects one logical
        qubit.
    rounds:
        Number of stabilizer-measurement rounds (``>= 1``). The standard choice
        is ``rounds == distance`` so temporal and spatial distances match; use
        :meth:`memory` to default it.
    basis:
        ``"Z"`` for a memory-Z experiment (default) or ``"X"`` for memory-X.
    """

    distance: int
    rounds: int
    basis: str = "Z"

    def __post_init__(self) -> None:
        if self.distance < 3 or self.distance % 2 == 0:
            raise ValueError(f"distance must be an odd integer >= 3; got {self.distance}")
        if self.rounds < 1:
            raise ValueError(f"rounds must be >= 1; got {self.rounds}")
        if self.basis not in _MEMORY_TASK:
            raise ValueError(f"basis must be 'X' or 'Z'; got {self.basis!r}")

    @classmethod
    def memory(
        cls, distance: int, rounds: int | None = None, basis: str = "Z"
    ) -> RotatedSurfaceCode:
        """Build a memory experiment, defaulting ``rounds`` to ``distance``."""
        return cls(distance=distance, rounds=distance if rounds is None else rounds, basis=basis)

    @property
    def num_data_qubits(self) -> int:
        """``d**2`` data qubits."""
        return self.distance**2

    def circuit(self, noise: CircuitNoise) -> stim.Circuit:
        """Return the noisy memory circuit for the given physical-noise knobs."""
        return stim.Circuit.generated(
            _MEMORY_TASK[self.basis],
            rounds=self.rounds,
            distance=self.distance,
            **noise.to_stim_kwargs(),
        )

    def detector_error_model(self, noise: CircuitNoise) -> stim.DetectorErrorModel:
        """Return the decomposed detector error model every decoder consumes."""
        return self.circuit(noise).detector_error_model(decompose_errors=True)
