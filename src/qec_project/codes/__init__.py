"""Code constructors: repetition, Shor, Steane, surface, qLDPC.

Populated during Phases 2-5. Each constructor returns a `stim.Circuit` (for
runnable noise simulations) and exposes the stabilizers / logical operators
as `numpy` parity-check matrices for decoder development.
"""

from qec_project.codes.shor9 import Shor9Code

__all__ = ["Shor9Code"]
