"""Circuit-level noise models for surface-code memory experiments.

Phase 3 deliverable (foreshadowed in this package's ``__init__``). A
:class:`CircuitNoise` bundles the four physical-error knobs that
:func:`stim.Circuit.generated` exposes for rotated-surface-code memory
circuits, and the module-level factories turn a single physical error rate
``p`` into a named noise profile.

Only the uniform ``depolarizing`` profile is a first-class, fully-specified
model used by the capstone threshold sweep. ``si1000`` is an *approximation*
of the superconducting-inspired SI1000 model mapped onto the four available
knobs; the full SI1000 model needs a hand-built circuit and is Phase-5
roadmap. ``biased`` and ``leakage`` require asymmetric / non-Pauli channels
that the generated circuits cannot express and therefore raise
:class:`NotImplementedError`.

References (in ``docs/reading-list.md``):

* C. Gidney. *Stim: a fast stabilizer circuit simulator.* Quantum 5, 497
  (2021). doi:10.22331/q-2021-07-06-497. — the ``Circuit.generated`` noise knobs.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CircuitNoise:
    """The four circuit-level error knobs of a generated surface-code memory.

    Each field is a probability in ``[0, 1]`` passed straight to
    :func:`stim.Circuit.generated` (see
    :meth:`qec_project.codes.surface.RotatedSurfaceCode.circuit`).
    """

    after_clifford_depolarization: float
    after_reset_flip_probability: float
    before_measure_flip_probability: float
    before_round_data_depolarization: float

    def __post_init__(self) -> None:
        for name, value in self.to_stim_kwargs().items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]; got {value}")

    def to_stim_kwargs(self) -> dict[str, float]:
        """Return the keyword mapping for :func:`stim.Circuit.generated`."""
        return {
            "after_clifford_depolarization": self.after_clifford_depolarization,
            "after_reset_flip_probability": self.after_reset_flip_probability,
            "before_measure_flip_probability": self.before_measure_flip_probability,
            "before_round_data_depolarization": self.before_round_data_depolarization,
        }


def depolarizing(p: float) -> CircuitNoise:
    """Uniform circuit-level depolarizing noise: every knob equals ``p``.

    This is the primary, fully-specified noise model for the capstone
    threshold sweep.
    """
    return CircuitNoise(p, p, p, p)


def si1000(p: float) -> CircuitNoise:
    """Approximate SI1000 superconducting-inspired profile scaled by ``p``.

    Maps SI1000-style ratios onto the four generated-circuit knobs: two-qubit
    gate depolarizing ``p``, reset flip ``2p``, measurement flip ``5p``, and
    idle/data depolarizing ``p / 10``. This is an *approximation* — the full
    SI1000 model (idle-during-measurement and friends) needs a hand-built
    circuit and is Phase-5 roadmap. Values are clamped to ``[0, 1]``.
    """
    return CircuitNoise(
        after_clifford_depolarization=min(p, 1.0),
        after_reset_flip_probability=min(2.0 * p, 1.0),
        before_measure_flip_probability=min(5.0 * p, 1.0),
        before_round_data_depolarization=min(p / 10.0, 1.0),
    )


def _unsupported(model: str) -> Callable[[float], CircuitNoise]:
    def factory(p: float) -> CircuitNoise:
        raise NotImplementedError(
            f"{model!r} noise needs asymmetric / non-Pauli channels that "
            f"stim.Circuit.generated cannot express; it is Phase-5 roadmap. "
            f"Use 'depolarizing' (or 'SI1000' for an approximate profile)."
        )

    return factory


# Keyed by the ``--noise`` choices of scripts/run_threshold_sweep.py. Only
# 'depolarizing' (real) and 'SI1000' (approximate) are wired; the rest raise.
NOISE_MODELS: dict[str, Callable[[float], CircuitNoise]] = {
    "depolarizing": depolarizing,
    "SI1000": si1000,
    "biased": _unsupported("biased"),
    "leakage": _unsupported("leakage"),
}
