"""Tests for scripts/check_seed_salts.py (loaded from its file; scripts/ is not a package)."""

from __future__ import annotations

import importlib.util
import zlib
from pathlib import Path

from qec_project.decoders import harness

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_seed_salts.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("check_seed_salts", _SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pre_crc32_seed(seed: int, salt: int, distance: int, p_phys: float, offset: int) -> int:
    """harness._cell_seed before f5a48b3, with ``hash(decoder) & 0xFFFF`` replaced by ``salt``."""
    h = (int(seed) & 0x7FFFFFFF) * 1_000_003
    h += distance * 100_003
    h += round(p_phys * 1e9) * 101
    h += (salt & 0xFFFF) * 31
    h += offset
    return h % (2**31 - 1)


def test_salted_seed_is_the_pre_crc32_formula():
    mod = _load_script()
    for salt in (0, 17237, 39723, 44539, 0xFFFF):
        seed_fn = mod.salted_cell_seed(salt)
        for d, p, off in [(3, 0.002, 0), (7, 0.025, 0), (5, 0.005, 20000)]:
            assert seed_fn(42, "pymatching", d, p, off) == _pre_crc32_seed(42, salt, d, p, off)


def test_salted_seed_with_the_crc32_salt_is_todays_harness_seed():
    mod = _load_script()
    for decoder in ("pymatching", "bp-osd"):
        seed_fn = mod.salted_cell_seed(zlib.crc32(decoder.encode()) & 0xFFFF)
        for d, p, off in [(3, 0.002, 0), (5, 0.013, 0), (7, 0.01, 8192)]:
            assert seed_fn(42, decoder, d, p, off) == harness._cell_seed(42, decoder, d, p, off)


def test_recovered_salts_follow_the_two_invocations():
    mod = _load_script()
    assert mod.recovered_salt("pymatching", 0.002) == 39723
    assert mod.recovered_salt("pymatching", 0.01) == 39723
    assert mod.recovered_salt("pymatching", 0.013) == 17237
    assert mod.recovered_salt("bp-osd", 0.01) == 44539
    assert mod.recovered_salt("bp-osd", 0.013) is None  # not recovered


def test_regenerate_restores_the_harness_seed():
    mod = _load_script()
    before = harness._cell_seed
    mod.regenerate("pymatching", 3, 0.002, 39723, "depolarizing", shots=64, max_errors=64)
    assert harness._cell_seed is before
