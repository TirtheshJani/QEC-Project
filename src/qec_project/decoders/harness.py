"""In-process Monte-Carlo harness for surface-code decoder benchmarks.

Phase 3 capstone payload. Samples detection events from a noisy
:class:`~qec_project.codes.surface.RotatedSurfaceCode` circuit with Stim
(explicitly seeded for reproducibility) and decodes them with a chosen
decoder, counting logical errors.

Why not :func:`sinter.collect`? In the locked environment sinter 1.15's
parallel sampler asserts ``isinstance(errors, int)``, but NumPy 2.x's
``np.count_nonzero`` returns a NumPy integer, so ``sinter.collect`` raises
``AssertionError`` in every worker (logged in CHANGELOG "Failed approaches").
This harness samples in-process instead, reusing the *tested* decoder
back-ends — PyMatching's batch decoder and ldpc's BP+OSD disk decoder — and
hands statistics to sinter's helpers in :mod:`qec_project.analysis.threshold`.

:func:`sample_cell` is a module-level function so it is importable by
``concurrent.futures.ProcessPoolExecutor`` workers (no ``__main__`` re-import
problem).
"""

from __future__ import annotations

import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pymatching
import sinter
import stim

from qec_project.codes.surface import RotatedSurfaceCode
from qec_project.decoders.registry import custom_decoders
from qec_project.noise.circuit import NOISE_MODELS, CircuitNoise

_DEFAULT_BATCH = 8192


@dataclass(frozen=True)
class CellResult:
    """Monte-Carlo outcome for one (decoder, distance, p_phys) cell."""

    decoder: str
    noise: str
    distance: int
    rounds: int
    p_phys: float
    shots: int
    errors: int
    seconds: float
    seed: int

    @property
    def shot_error_rate(self) -> float:
        """Logical errors per shot (``nan`` if no shots were taken)."""
        return self.errors / self.shots if self.shots else float("nan")


class _CompiledDecoder:
    """Predict bit-packed logical flips from bit-packed detection events."""

    def predict(self, det_bp: np.ndarray) -> np.ndarray:  # pragma: no cover - interface
        raise NotImplementedError


class _MatchingDecoder(_CompiledDecoder):
    """PyMatching MWPM, decoded fully in-process."""

    def __init__(self, dem: stim.DetectorErrorModel) -> None:
        self._matching = pymatching.Matching.from_detector_error_model(dem)

    def predict(self, det_bp: np.ndarray) -> np.ndarray:
        return self._matching.decode_batch(
            det_bp, bit_packed_shots=True, bit_packed_predictions=True
        )


class _FileDecoder(_CompiledDecoder):
    """Drive an ldpc ``sinter.Decoder`` that only implements ``decode_via_files``."""

    def __init__(self, decoder: sinter.Decoder, dem: stim.DetectorErrorModel, work_dir: Path) -> None:
        self._decoder = decoder
        self._num_obs = dem.num_observables
        self._num_dets = dem.num_detectors
        self._obs_bytes = (self._num_obs + 7) // 8
        self._dir = work_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._dem_path = self._dir / "model.dem"
        dem.to_file(self._dem_path)

    def predict(self, det_bp: np.ndarray) -> np.ndarray:
        num_shots = det_bp.shape[0]
        din = self._dir / "dets.b8"
        dout = self._dir / "preds.b8"
        with open(din, "wb") as f:
            det_bp.tofile(f)
        self._decoder.decode_via_files(
            num_shots=num_shots,
            num_obs=self._num_obs,
            num_dets=self._num_dets,
            dem_path=self._dem_path,
            dets_b8_in_path=din,
            obs_predictions_b8_out_path=dout,
            tmp_dir=self._dir,
        )
        pred = np.fromfile(dout, dtype=np.uint8, count=self._obs_bytes * num_shots)
        return pred.reshape((num_shots, self._obs_bytes))


def _cell_seed(seed: int, decoder: str, distance: int, p_phys: float, offset: int) -> int:
    """Deterministic per-cell Stim seed (independent of worker scheduling)."""
    h = (int(seed) & 0x7FFFFFFF) * 1_000_003
    h += distance * 100_003
    h += round(p_phys * 1e9) * 101
    h += (hash(decoder) & 0xFFFF) * 31
    h += offset
    return h % (2**31 - 1)


def _compile_decoder(
    decoder: str, code: RotatedSurfaceCode, noise_obj: CircuitNoise, work_dir: Path
) -> _CompiledDecoder:
    if decoder == "pymatching":
        # MWPM needs the decomposed (graph-like) DEM.
        return _MatchingDecoder(code.detector_error_model(noise_obj))
    mapping = custom_decoders(decoder)
    if decoder in mapping:
        # BP+OSD / belief-find handle hyperedges: use the plain DEM.
        plain = code.circuit(noise_obj).detector_error_model()
        return _FileDecoder(mapping[decoder], plain, work_dir)
    raise ValueError(f"unknown decoder {decoder!r}")


def sample_cell(
    *,
    decoder: str,
    distance: int,
    p_phys: float,
    noise: str = "depolarizing",
    shots: int,
    max_errors: int | None = None,
    seed: int = 42,
    rounds: int | None = None,
    batch_size: int = _DEFAULT_BATCH,
    shot_offset: int = 0,
) -> CellResult:
    """Estimate the logical error rate of one decoder/distance/noise cell.

    Samples up to ``shots`` detection-event shots from the noisy rotated
    surface-code memory circuit and decodes them, stopping early once
    ``max_errors`` logical errors have accumulated. Sampling is seeded
    deterministically from ``(seed, decoder, distance, p_phys, shot_offset)``.

    Parameters
    ----------
    decoder:
        ``"pymatching"``, ``"bp-osd"`` or ``"union-find"``.
    distance, p_phys, noise, rounds:
        Code + physical-noise parameters (see
        :class:`~qec_project.codes.surface.RotatedSurfaceCode` and
        :data:`qec_project.noise.circuit.NOISE_MODELS`).
    shots, max_errors, batch_size, shot_offset:
        Monte-Carlo budget knobs. ``shot_offset`` shifts the seed stream so a
        resumed run draws fresh samples.
    """
    if shots <= 0:
        raise ValueError(f"shots must be positive; got {shots}")
    target_errors = shots if max_errors is None else max_errors

    code = RotatedSurfaceCode.memory(distance, rounds=rounds)
    noise_obj = NOISE_MODELS[noise](p_phys)
    circuit = code.circuit(noise_obj)
    sampler = circuit.compile_detector_sampler(
        seed=_cell_seed(seed, decoder, distance, p_phys, shot_offset)
    )

    work_dir = Path(tempfile.mkdtemp(prefix="qec_dec_"))
    try:
        compiled = _compile_decoder(decoder, code, noise_obj, work_dir)
        total = 0
        errors = 0
        t0 = time.monotonic()
        while total < shots and errors < target_errors:
            n = min(batch_size, shots - total)
            det_bp, obs_bp = sampler.sample(n, separate_observables=True, bit_packed=True)
            pred_bp = compiled.predict(det_bp)
            obs_b = obs_bp.shape[1]
            errors += int(np.count_nonzero(np.any((pred_bp[:, :obs_b] ^ obs_bp) != 0, axis=1)))
            total += n
        seconds = time.monotonic() - t0
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return CellResult(
        decoder=decoder,
        noise=noise,
        distance=distance,
        rounds=code.rounds,
        p_phys=p_phys,
        shots=total,
        errors=errors,
        seconds=seconds,
        seed=int(seed),
    )
