"""Map ``--decoder`` names to the decoder back-ends the sweep harness needs.

Phase 3 capstone benchmark. Keeping this mapping in one place lets the sweep
harness stay agnostic about decoder internals and makes the MWPM-vs-BP+OSD
head-to-head genuinely apples-to-apples: every decoder consumes the *same*
detector error model derived from one Stim circuit.

* ``pymatching`` — MWPM (Sparse Blossom), decoded in-process via
  :class:`pymatching.Matching`.
* ``bp-osd`` — belief propagation + ordered-statistics decoding from the
  ``ldpc`` library (``ldpc.sinter_decoders.SinterBpOsdDecoder``).
* ``union-find`` — belief-find from ``ldpc`` (wired for completeness; a
  Phase-5 roadmap comparison).

The ``ldpc`` sinter decoders implement ``decode_via_files`` rather than
in-process ``compile_decoder_for_dem``; :mod:`qec_project.decoders.harness`
drives that file interface.

References (in ``docs/reading-list.md``):

* J. Roffe, D. R. White, S. Burton, E. Campbell. *Decoding across the quantum
  LDPC code landscape.* Phys. Rev. Research 2, 043423 (2020).
  doi:10.1103/PhysRevResearch.2.043423.
* N. Delfosse, N. H. Nickerson. *Almost-linear time decoding algorithm for
  topological codes.* Quantum 5, 595 (2021). doi:10.22331/q-2021-12-02-595.
"""

from __future__ import annotations

import sinter

_BUILTIN = frozenset({"pymatching"})
_FILE_BACKED = frozenset({"bp-osd", "union-find"})

DECODERS: tuple[str, ...] = ("pymatching", "bp-osd", "union-find")


def builtin_decoder_names() -> set[str]:
    """Decoders decoded in-process by PyMatching (no ``sinter.Decoder`` object)."""
    return set(_BUILTIN)


def custom_decoders(decoder: str) -> dict[str, sinter.Decoder]:
    """Return the ``{name: sinter.Decoder}`` mapping for a file-backed decoder.

    Built-in (PyMatching) decoders return ``{}``. The ``ldpc`` imports are
    done lazily so importing this module stays cheap.
    """
    if decoder in _BUILTIN:
        return {}
    if decoder == "bp-osd":
        from ldpc.sinter_decoders import SinterBpOsdDecoder

        return {
            "bp-osd": SinterBpOsdDecoder(
                max_iter=20,
                bp_method="ms",
                osd_method="osd_cs",
                osd_order=7,
            )
        }
    if decoder == "union-find":
        from ldpc.sinter_decoders import SinterBeliefFindDecoder

        return {"union-find": SinterBeliefFindDecoder()}
    raise ValueError(f"unknown decoder {decoder!r}; choose from {DECODERS}")
