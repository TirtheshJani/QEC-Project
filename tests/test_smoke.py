"""Smoke test: package imports cleanly and exposes its version."""

import qec


def test_import_and_version():
    assert hasattr(qec, "__version__")
    assert isinstance(qec.__version__, str)


def test_statevec_submodule_imports():
    from qec import statevec

    assert callable(statevec.zero_state)
    assert callable(statevec.apply_1q)
    assert callable(statevec.cnot)
