"""Rotated surface-code circuit factory.

Thin, validated wrapper over `stim.Circuit.generated` so every capstone
experiment shares one source of truth for what "the rotated surface code
under depolarizing noise" means. All four standard noise channels are
driven by a single physical error rate `p_phys` — the simplest possible
phenomenological model and the one used in the canonical threshold
plots (Fowler et al. 2012; Higgott 2023).
"""

from __future__ import annotations

import stim


def rotated_surface_code_circuit(
    distance: int,
    rounds: int,
    p_phys: float,
    noise_model: str = "depolarizing",
) -> stim.Circuit:
    """Construct a rotated surface-code memory-Z circuit under depolarizing noise.

    Parameters
    ----------
    distance:
        Code distance ``d``. Must be an odd integer ``>= 3``.
    rounds:
        Number of stabilizer-measurement rounds. Must be ``>= 1``.
    p_phys:
        Physical error rate driving every noise knob. Must satisfy
        ``0 <= p_phys <= 0.5``.
    noise_model:
        Currently only ``"depolarizing"`` is supported.

    Returns
    -------
    stim.Circuit
        A compiled Stim circuit ready for detector sampling.
    """
    if not isinstance(distance, int) or distance < 3 or distance % 2 == 0:
        raise ValueError(f"distance must be an odd integer >= 3, got {distance}")
    if not isinstance(rounds, int) or rounds < 1:
        raise ValueError(f"rounds must be an integer >= 1, got {rounds}")
    if not (0.0 <= p_phys <= 0.5):
        raise ValueError(f"p_phys must lie in [0, 0.5], got {p_phys}")
    if noise_model != "depolarizing":
        raise ValueError(f"unsupported noise_model {noise_model!r}; only 'depolarizing'")

    return stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=p_phys,
        after_reset_flip_probability=p_phys,
        before_measure_flip_probability=p_phys,
        before_round_data_depolarization=p_phys,
    )


def code_parameters(distance: int) -> dict[str, int]:
    """Return integer parameters of the rotated surface code at ``distance``.

    For odd ``d`` the rotated layout has ``d**2`` data qubits and
    ``d**2 - 1`` stabilizers, split evenly between X- and Z-type.
    """
    if not isinstance(distance, int) or distance < 3 or distance % 2 == 0:
        raise ValueError(f"distance must be an odd integer >= 3, got {distance}")
    n_data = distance**2
    n_stabilizers = n_data - 1
    half = n_stabilizers // 2
    return {
        "distance": distance,
        "n_data": n_data,
        "n_stabilizers": n_stabilizers,
        "n_x_stabilizers": half,
        "n_z_stabilizers": half,
    }
