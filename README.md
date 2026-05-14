# QEC-Project

Self-study quantum error correction (QEC) curriculum + decoder-focused
capstone, structured to ground an Expression of Interest to the National
Research Council of Canada's
[Applied Quantum Computing Challenge](https://nrc.canada.ca/en/research-development/research-collaboration/research-centres/emerging-directions-fault-tolerant-quantum-computing-call-proposals)
(QEC stream).

The intent is not to read about QEC — it is to *build* enough of it that
the capstone preprint is a credible artifact behind an EOI conversation.

## Mission

Take a true beginner (math + QM from scratch) through 5 curriculum phases
and into a focused decoder benchmark study on the rotated surface code,
targeting NRC's *Decoding algorithm optimization* objective. Budget:
~4–6 months at 20+ hrs/week.

## Curriculum index

| Phase | Topic | Duration |
| --- | --- | --- |
| [Phase 0](phase-00-foundations/) | Linear algebra, probability, classical error correction | ~3 wks |
| [Phase 1](phase-01-quantum-basics/) | Qubits, gates, entanglement, noise channels (Qiskit) | ~3 wks |
| [Phase 2](phase-02-qec-fundamentals/) | Stabilizer formalism, Steane, intro to Stim | ~4 wks |
| [Phase 3](phase-03-topological-codes/) | Surface code, MWPM/PyMatching, thresholds | ~4 wks |
| [Phase 4](phase-04-fault-tolerance/) | FT syndrome extraction, magic states, lattice surgery | ~3 wks |
| [Phase 5](phase-05-advanced-decoders/) | BP+OSD, Union-Find, neural decoders, qLDPC | ~4 wks |
| [Capstone](capstone/) | Decoder benchmark study + arXiv preprint + mock EOI | ~6–8 wks |

## Quickstart

```bash
# 1. Install Python deps via uv (https://docs.astral.sh/uv/)
uv sync --extra dev

# 2. Install the three Claude Code plugins this project uses
bash scripts/install_plugins.sh

# 3. Sanity check
uv run pytest -q
uv run ruff check .
uv run python scripts/verify_reading_list.py

# 4. Start
uv run jupyter lab phase-00-foundations/
```

## How this repo is governed

Three plugins + one cross-session memory pattern:

- **[Superpowers](https://github.com/obra/superpowers)** — engineering
  methodology (TDD, plans, code review, parallel agents,
  verification-before-completion). Governs everything under
  `src/qec_project/`, `tests/`, `scripts/`, and `capstone/experiments/`.
  See `docs/superpowers-cheatsheet.md`.
- **[Academic Research Skills (ARS)](https://github.com/Imbad0202/academic-research-skills)**
  (CC-BY-NC 4.0) — paper/EOI workflow with anti-hallucination integrity
  gates. Governs `capstone/proposal/`, `capstone/paper/`, and
  `docs/reading-list.md`. See `docs/ars-cheatsheet.md`.
- **[Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills)**
  (MIT) — domain catalog. We pull a focused ~10-skill subset; see
  `docs/sciskills-active.md`. The rest stay dormant.
- **[Long-running Claude pattern](https://www.anthropic.com/research/long-running-Claude)**
  — `CHANGELOG.md` is the project's portable long-term memory across
  sessions. Read at session start; write at session end. See
  `docs/long-running-protocol.md`.

Nothing from the three plugins is vendored — they are installed by
reference. `CLAUDE.md` is the single source of truth for how Claude Code
sessions should operate inside this repo.

## Stack

Python 3.12, managed by `uv`. Core: Stim, PyMatching, Sinter, ldpc, Qiskit,
NumPy, SciPy, Matplotlib, NetworkX. Dev: pytest + hypothesis, ruff, mypy,
JupyterLab. Optional ML extras: torch + lightning + scikit-learn + SHAP + PyMC.
Optional remote: `modal` for cloud burst on large sweeps.

## License

The `LICENSE` in this repo (MIT) covers code we author. The three plugins
above retain their own licenses upstream — none of their files are copied
into this repo.
