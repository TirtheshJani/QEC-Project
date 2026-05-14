"""Smoke tests: keep CI green from day one.

Real tests for codes / decoders / noise land alongside their implementations
during Phases 2-5 (Superpowers TDD: write the test first).
"""

from __future__ import annotations

import importlib

import qec_project


def test_package_imports() -> None:
    assert qec_project.__version__


def test_subpackages_importable() -> None:
    for name in ("analysis", "codes", "decoders", "noise"):
        importlib.import_module(f"qec_project.{name}")
