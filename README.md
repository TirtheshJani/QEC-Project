# QEC-Project

[![ci](https://github.com/TirtheshJani/QEC-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/TirtheshJani/QEC-Project/actions/workflows/ci.yml)

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

**Status:** Phases 0, 1 and 3 complete (foundations → a runnable surface-code decoder
benchmark). Phase 2 is partly done: 2.1 (3-qubit repetition code) and 2.2 (Shor 9)
are in; 2.3 to 2.5 (stabilizer formalism, Steane, intro to Stim) are not started.
Phases 4–5 + the written EOI are the roadmap.

## Results so far — the capstone decoder benchmark

The capstone payload **runs end to end**: a reproducible rotated-surface-code
threshold study comparing **MWPM (PyMatching)** and **BP+OSD (ldpc)** under uniform
circuit-level depolarizing noise, built on Stim with an in-process, explicitly
seeded Monte-Carlo harness.

![Surface-code threshold crossing under MWPM](capstone/figures/threshold_depolarizing_pymatching.png)

| Decoder | threshold $p_\mathrm{th}$ (per round) | suppression $\Lambda_{3\to5}$ at $p=0.002$ | decode latency @ d=5 |
| --- | --- | --- | --- |
| MWPM (PyMatching) | $0.0122 \pm 0.0013$ | 5.8× | ~9 µs/shot |
| BP+OSD (ldpc)     | $0.0134 \pm 0.0015$ | 6.3× | ~5400 µs/shot (~600× slower) |

At $p=0.002$ each $+2$ in code distance suppresses the logical error rate ~4–6×
(those cells hold only 5 to 49 logical errors, so $\Lambda$ there is uncertain; at
$p=0.005$ it is ~2–3×); the $d=3,5,7$ curves cross at $p_\mathrm{th}$. BP+OSD is
the more accurate decoder at $d=5$ (lower $p_L$ than MWPM at all nine swept $p$, ~35%
lower at $p=0.005$), though its fitted threshold is within the fit uncertainty of
MWPM's, and it pays a steep, distance-scaling latency cost — exactly the accuracy vs
real-time-feasibility frontier the capstone targets (NRC *Decoding algorithm
optimization*). Every number is seed- and commit-stamped in
[`CHANGELOG.md`](CHANGELOG.md); reproduce via
[`capstone/experiments/README.md`](capstone/experiments/README.md).

How the numbers are measured: $p_\mathrm{th}$ is a fit of
$p_L = A\,(p/p_\mathrm{th})^{(d+1)/2}$ to per-round logical error rates over the whole
$p$ grid (the per-shot curves cross lower, near $p = 0.007$). Latency is wall-clock
time per shot for Stim sampling plus decoding, summed over the $p$ grid at $d=5$, with
cells running in parallel worker processes; BP+OSD runs through ldpc's file-based
sinter interface. It is a same-harness comparison, not a tuned decoder-only benchmark.

## Quickstart

```bash
# 1. Install Python deps via uv (https://docs.astral.sh/uv/); Python 3.12
uv sync --extra dev

# 2. Sanity check (the same steps CI runs)
uv run pytest -q
uv run ruff check .
uv run python scripts/verify_reading_list.py

# 3. Regenerate the capstone figures + summary.json from the committed sweep data
uv run python scripts/make_figures.py capstone/experiments/*/stats.csv --noise depolarizing

# 4. Start
uv run jupyter lab phase-00-foundations/
```

`uv run pytest -m slow` runs the Monte-Carlo physics tests, which are deselected by
default. Step 3 rewrites `capstone/figures/` with files byte-identical to the committed
ones, so `git status` stays clean.

Optional, only for working on the repo with Claude Code (not needed to run anything
above): `bash scripts/install_plugins.sh` installs the three plugins described below.

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
