# QEC-Project

A theory-first, self-paced walk through Quantum Error Correction.

The goal is not to build a production QEC framework — it is to *understand* QEC by writing notes, building tiny implementations from scratch in NumPy, and cross-checking them against Qiskit. Each phase produces a markdown note + a runnable demo + a pytest sanity check before moving on.

## Roadmap

| Phase | Topic | Notes | Code |
|---|---|---|---|
| 0 | Repo & environment | — | `pyproject.toml`, dir skeleton |
| 1 | Linear algebra & QC basics | `notes/00`–`03` | `qec/statevec.py` |
| 2 | Noise & quantum channels | `notes/04` | `qec/channels.py` |
| 3 | Stabilizer formalism | `notes/05` | `qec/pauli.py`, `qec/stabilizer.py` |
| 4 | Repetition code | `notes/06` | `qec/codes/repetition.py` |
| 5 | Shor & Steane codes | `notes/07`–`08` | `qec/codes/shor.py`, `qec/codes/steane.py` |
| 6 | CSS codes & general theory | `notes/09` | (extends Steane demo) |
| 7 | Fault tolerance basics | `notes/10` | (small demo) |
| 8 | Surface code (intro) | `notes/11` | `demos/07_surface_code_intro.ipynb` |
| 9 | Capstone write-up | `notes/12` | `demos/00_grand_tour.ipynb` |

See `notes/README.md` (once populated) for the table of contents, and `references/reading_list.md` for the source material.

## Repo layout

```
qec/             pure-Python / NumPy library, written from scratch
demos/           Jupyter notebooks — one per concept
qiskit_demos/    parallel Qiskit reference implementations
notes/           markdown — the running "book" of what I've learned
tests/           pytest sanity checks for qec/
references/      reading list, papers, links
```

## Setup

Requires Python ≥ 3.10. Two install paths — pick one.

### Option A: `uv` (recommended, fast)

```bash
# install uv if you don't have it: https://docs.astral.sh/uv/
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -e ".[notebooks,dev]"
```

### Option B: stdlib `venv` + pip

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[notebooks,dev]"
```

The base install (`pip install -e .`) only pulls NumPy / SciPy / matplotlib. The `[notebooks]` extra adds JupyterLab + Qiskit; the `[dev]` extra adds pytest + ruff.

## Verify

```bash
pytest                # all tests for completed phases should pass
jupyter lab           # opens demos/ — try 01_statevec_vs_qiskit.ipynb
```

## Working on this repo

- Each phase lands as: a `notes/NN-*.md` write-up + code in `qec/` + a notebook in `demos/` + tests.
- Run `pytest` after each phase — every demo's headline claim is also a test.
- Notes should be readable cold in 6 months. If a future-you reading them wouldn't follow the *why*, rewrite.

## License

See `LICENSE`.
