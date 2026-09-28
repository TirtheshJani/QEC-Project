"""Tests for scripts/update_changelog.py (loaded from its file; scripts/ is not a package)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "update_changelog.py"
_BACKSLASHES = r"Lambda_{3\to5} = 1.99, \lbrace x \rbrace, \1 and \g<0> stay literal"


def _load_script():
    spec = importlib.util.spec_from_file_location("update_changelog", _SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_append_under_keeps_backslashes_literal():
    mod = _load_script()
    text = "# Log\n\n## Completed milestones\n\n- old entry\n"
    out = mod.append_under(text, "## Completed milestones", f"- {_BACKSLASHES}")
    assert out == f"# Log\n\n## Completed milestones\n\n- {_BACKSLASHES}\n\n- old entry\n"


def test_rewrite_status_keeps_backslashes_literal():
    mod = _load_script()
    text = "## Current status\nold status\n\n## Completed milestones\n"
    out = mod.rewrite_status(text, _BACKSLASHES)
    assert out == f"## Current status\n{_BACKSLASHES}\n\n## Completed milestones\n"
