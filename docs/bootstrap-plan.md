# Plan: Bootstrap QEC-Project as a long-running, NRC-EOI-ready curriculum + portfolio

Governed by three plugins (Superpowers, ARS, Scientific Agent Skills) and the **Anthropic long-running-Claude pattern** (`CHANGELOG.md` as portable agent memory).

## Context

The user is preparing to qualify for the next NRC **Applied Quantum Computing Challenge** call (QEC stream — 2025 cycle: Jun 2 → Aug 29, 2025; we plan for the 2026 cycle). The repo must take them from **true beginner** to a **decoder-focused capstone** strong enough to ground an EOI under NRC's annex-A criteria.

Locked from the questionnaire:
- **Starting point:** true beginner — Phase 0 covers linear algebra, probability, classical EC before quantum.
- **Capstone aim:** decoder algorithms (MWPM, Union-Find, BP+OSD, neural decoders; benchmark study on rotated surface code under realistic noise).
- **Budget:** 20+ hrs/week, ~4–6 months to capstone.
- **Stack:** Python + Stim + PyMatching + Qiskit. `uv` for env mgmt.

User asked us to fold in:
1. **`Imbad0202/academic-research-skills` (ARS)** — CC-BY-NC 4.0 plugin: 4 skills, 10 `/ars-*` commands, 32 agents, paper-production pipeline with integrity gates at stages 2.5 & 4.5.
2. **`obra/superpowers`** — 14 software-engineering methodology skills (TDD, plan-writing, git worktrees, code review, systematic debugging, parallel-agent dispatch, verification-before-completion).
3. **`K-Dense-AI/scientific-agent-skills`** — MIT-licensed catalog of 135 science skills (most are bio/chem; a focused ~10-skill subset matters for QEC).
4. **Anthropic, "Long-running Claude for scientific computing."** Key takeaway: a project-level **`CHANGELOG.md`** acts as the agent's portable long-term memory across many sessions. Tracks current status, completed tasks, **failed approaches and why** (so future sessions don't repeat dead ends), accuracy tables at key checkpoints, and known limitations. The CLAUDE.md instructs the agent to read/update it every session. Demonstrated at scale (~2000 sessions to build a C compiler that compiled the Linux kernel).

Repo state today: `README.md` (one line), `LICENSE` (MIT), single commit. Branch: `claude/init-project-setup-LlShn`.

## Why this is the right architecture

This project is intrinsically long-running (4–6 months, many sessions, many sub-experiments) and intrinsically dual-track (build code AND write a paper). The four ingredients map cleanly:

| Concern | Mechanism |
| --- | --- |
| Continuity across many sessions | **`CHANGELOG.md` long-running pattern** (Anthropic) + ARS Material Passport |
| Engineering quality (decoder code is easy to get subtly wrong) | **Superpowers** (TDD, plans, two-stage review, verification-before-completion) |
| Research/writing quality + anti-hallucination | **ARS** (integrity gates at stages 2.5 & 4.5; `/ars-fact-check`; `/ars-lit-review`) |
| Specialized scientific tooling (arXiv lookup, GPU scale-out, Bayesian uncertainty, neural decoder ML stack, figure quality) | **Scientific Agent Skills** (focused subset; the rest stay dormant) |
| Long-horizon Monte Carlo sweeps | Sinter (deps) + Scientific Agent Skills' **Modal** skill for cloud burst when local maxes out |

## Plugin install (one script: `scripts/install_plugins.sh`)

```bash
# Superpowers — engineering methodology
/plugin install superpowers@claude-plugins-official

# Academic Research Skills — paper/EOI workflow
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills

# Scientific Agent Skills — domain catalog (135 skills, only ~10 active for QEC)
npx skills add K-Dense-AI/scientific-agent-skills
```

**Nothing is vendored.** License compliance is by reference, not redistribution.

## Long-running-Claude pattern: `CHANGELOG.md` as memory

Top-level `CHANGELOG.md` is **the single most important file in this repo for cross-session continuity.** Structure:

```markdown
# CHANGELOG — QEC-Project research journal

## Current status
<one paragraph: which phase, what's next, blocked on what>

## Completed milestones
- 2026-MM-DD  Phase 0.1 linear-algebra notebook landed; tests green.
- 2026-MM-DD  Phase 2 stabilizer formalism notebook + Steane code passes Knill–Laflamme check.

## Decoder accuracy tables (capstone)
| Run ID | Code | Distance | Decoder | Noise model | p_phys | p_log | shots | seed | commit | notes |
| ------ | ---- | -------- | ------- | ----------- | ------ | ----- | ----- | ---- | ------ | ----- |

## Failed approaches & why
- 2026-MM-DD  Tried hand-rolling MWPM matching on NetworkX — too slow at d≥7. Use PyMatching's `Matching.decode_batch`. Don't repeat.
- 2026-MM-DD  Used uniform depolarizing noise to compare BP+OSD vs MWPM; comparison was meaningless because PyMatching is optimized for circuit-level noise. Always use Stim's DEM-derived weights.

## Known limitations
- Local hardware caps at d=9, ~1M shots/run; for d≥11 we burst to Modal (see `scripts/run_threshold_sweep.py --remote`).
```

CLAUDE.md will instruct Claude to **read CHANGELOG.md first thing every session**, and to append entries on phase completion, failed approach, and every threshold-sweep run.

## Workflow map: which tool when

### Engineering workflow (Superpowers governs)

| Trigger | Superpowers skill | What happens |
| --- | --- | --- |
| Start of phase | `brainstorming` | Define goals + deliverables. |
| Before non-trivial `src/qec_project/` change | `writing-plans` | Plan file in `plans/`; 2–5 min tasks. |
| Decoder / code-construction work | `test-driven-development` | Property tests vs Stim ground truth. RED→GREEN→REFACTOR. |
| Decoder implementation | `subagent-driven-development` | Implementer + independent reviewer agent. |
| Multiple sweeps in parallel | `dispatching-parallel-agents` | One agent per (decoder × noise × distance), backed by Sinter / Modal. |
| Concurrent experiment branches | `using-git-worktrees` | Sims don't collide. |
| Sim diverges from expected threshold | `systematic-debugging` | Hypothesis log; eliminate causes one at a time. Append to CHANGELOG "Failed approaches". |
| Before merging | `requesting-code-review` + `receiving-code-review` | Plan-compliance review. |
| Before declaring a phase done | `verification-before-completion` | Tests pass, ruff clean, notebooks rerun, reading-list DOIs verified, CHANGELOG updated. |
| Closing phase | `finishing-a-development-branch` | Merge decision; lessons in CHANGELOG. |
| Inventing a QEC-specific skill | `writing-skills` | Under `.claude/skills/qec-<name>/`. |

### Paper / EOI workflow (ARS governs)

| QEC stage | ARS command / skill | Produces |
| --- | --- | --- |
| Phase 0–1 stuck on math/QM | `/ars-socratic` | Guided Socratic explanation. |
| Phase 2+ new "fact" notebook | `/ars-fact-check` | Citation against primary refs → `docs/reading-list.md`. |
| Phase 3 surface-code reading | `/ars-lit-review` | First slice of capstone bibliography. |
| Phase 4 design decisions | `devils_advocate_agent` | Stress-tests overhead/threshold claims. |
| Phase 5 entry — capstone gap | `/ars-lit-review --mode systematic-review` on decoders | PRISMA-grade gap statement → `capstone/proposal/literature-review.md`. NRC criterion 4 evidence. |
| Capstone planning | `/ars-plan` | Outline + experiment matrix. |
| Capstone outline | `/ars-outline` | Section-by-section structure. |
| Capstone draft | `/ars-full` | LaTeX-ready first pass. |
| Capstone integrity gates | `academic-pipeline` stages 2.5 & 4.5 | `integrity_verification_agent` verifies citations exist and numbers reproduce. |
| Internal peer review | `/ars-review --mode full` | Multi-perspective 0–100 rubric. |
| EOI revision | `/ars-revision-coach` | Prioritized revision plan. |
| EOI abstract (EN; optional FR) | `/ars-abstract` (bilingual) | Bilingual abstract. |
| Format | `/ars-format-convert` (LaTeX, APA-7) + `/ars-citation-check` | Tectonic LaTeX + verified bib. |
| EOI final pass | `/ars-disclosure --venue "NRC AQC Challenge 2026"` | AI-use disclosure. |

### Scientific Agent Skills — active subset

We don't enumerate all 135; we declare which ~10 are in-scope and let the agent discover the rest as needed.

| Skill | When we use it |
| --- | --- |
| **Paper Lookup** (arXiv, PubMed, bioRxiv) | Capstone lit review (arXiv quant-ph). The arXiv access is the single biggest gap in our base toolkit. |
| **BGPT Paper Search** | Structured metadata extraction (methods, sample sizes, quality scores) when bulk-reviewing 30+ decoder papers. |
| **Scientific Writing / Peer Review** | Second-opinion review pass independent of ARS. |
| **Matplotlib / Seaborn** | Publication-quality figures (threshold plots, decoder comparison curves). |
| **NetworkX** | Tanner graphs, lattice-surgery merge/split diagrams. |
| **scikit-learn + PyTorch Lightning** | Neural decoder branch of capstone. |
| **SHAP** | Interpret what the neural decoder learned (novelty angle). |
| **PyMC** | Bayesian uncertainty on threshold estimates (rigor angle). |
| **GPU Optimization (CuPy / Numba CUDA)** | Scaling decoder Monte Carlo when CPU caps. |
| **Modal** | Cloud burst for d≥11 sweeps; integrates with `scripts/run_threshold_sweep.py --remote`. |
| **What-If Oracle** | Multi-branch scenario analysis ("which decoder under which noise model wins"). |
| **Open Notebook** | Optional: generate a podcast-style audio summary of each phase for self-review. |

Out of scope (declared so Claude doesn't pull them): BioPython, RDKit, Scanpy, DiffDock, DeepChem, ClinVar/COSMIC, PyDESeq2, all clinical/laboratory skills.

## NRC EOI criterion → asset mapping

| NRC annex-A criterion | Evidence source in this repo |
| --- | --- |
| 1. Methodology | `capstone/experiments/` reproducible scripts + Superpowers TDD trail; ARS `methodology_reviewer_agent`. |
| 2. Project team & resources | Portfolio of completed phase deliverables; `collaboration_depth_agent` log. |
| 3. Alignment with scope | `capstone/proposal/eoi-mock.md` §3; produced via `/ars-plan` + `research_architect_agent`. |
| 4. Addressing a gap | `capstone/proposal/literature-review.md`; `/ars-lit-review --mode systematic-review` + Paper Lookup. |
| 5. Innovation | `capstone/paper/` novelty section; pressure-tested by `devils_advocate_agent`. |
| 6. Economic/social impact | `capstone/proposal/eoi-mock.md` §6; `synthesis_agent`. |
| 7. NRC collaboration | Hand-drafted; polished via `/ars-revision-coach`. |
| Anti-hallucination | ARS integrity gates + `scripts/verify_reading_list.py` (CI) + CHANGELOG "Failed approaches". |
| AI-use disclosure | `/ars-disclosure`. |

## Repository skeleton

```
QEC-Project/
├── CLAUDE.md                          # north star + all three workflow maps + CHANGELOG protocol
├── CHANGELOG.md                       # long-running agent memory (Anthropic pattern)
├── README.md                          # mission, phase index, quickstart, plugin install
├── pyproject.toml                     # uv: stim, pymatching, sinter, ldpc, qiskit,
│                                      #   qiskit-aer, numpy, scipy, matplotlib,
│                                      #   networkx, jupyterlab, pytest, hypothesis,
│                                      #   ruff, mypy
├── .python-version                    # 3.12
├── .gitignore                         # Python, Jupyter, .venv, data/, *.npz, *.stim
├── .pre-commit-config.yaml            # ruff + ruff-format
├── .github/workflows/ci.yml           # uv sync → pytest → ruff → verify_reading_list
│
├── .claude/
│   ├── settings.json                  # permissions allowlist (uv, pytest, stim, sinter)
│   └── skills/                        # symlink target dir; populated by install script
│
├── scripts/
│   ├── install_plugins.sh             # installs Superpowers + ARS + Scientific Agent Skills
│   ├── run_threshold_sweep.py         # Sinter sweep harness, --remote flag for Modal
│   ├── verify_reading_list.py         # CI: every DOI in reading-list.md resolves
│   └── update_changelog.py            # appends a templated entry to CHANGELOG.md
│
├── plans/                             # Superpowers writing-plans output lives here
│   └── .gitkeep
│
├── prompts/                           # ARS pre-prompts, QEC-tailored
│   ├── ars-plan-capstone.md
│   ├── ars-lit-review-decoders.md
│   ├── ars-review-eoi.md
│   └── ars-disclosure-nrc.md
│
├── src/qec_project/
│   ├── codes/                         # rep, Steane, surface, qLDPC constructors
│   ├── decoders/                      # MWPM/UF/BP-OSD wrappers w/ common interface
│   ├── noise/                         # depolarizing, biased, SI1000, leakage
│   └── analysis/                      # logical error rate fits, threshold plots
├── tests/                             # mirrors src/, uses hypothesis
│
├── phase-00-foundations/              # math + classical EC          (~3 wks)
├── phase-01-quantum-basics/           # qubits, gates, noise          (~3 wks)
├── phase-02-qec-fundamentals/         # stabilizers, Steane, Stim     (~4 wks)
├── phase-03-topological-codes/        # surface code + MWPM           (~4 wks)
├── phase-04-fault-tolerance/          # FT-SE, magic states, lattice  (~3 wks)
├── phase-05-advanced-decoders/        # BP+OSD, UF, neural, qLDPC     (~4 wks)
│   └── (each phase dir: 01-…, 02-…, README.md = Goals/Deliverables/Refs +
│       Superpowers + ARS + SciSkills command hints)
│
├── capstone/
│   ├── proposal/
│   │   ├── eoi-mock.md                # NRC 7-criterion EOI template (stub)
│   │   └── literature-review.md       # produced via /ars-lit-review (stub)
│   ├── experiments/                   # Sinter sweeps + run scripts
│   ├── figures/
│   ├── paper/                         # LaTeX preprint draft (arXiv quant-ph target)
│   └── README.md                      # capstone scope + experiment matrix
│
└── docs/
    ├── reading-list.md                # spine of capstone lit review (DOI-keyed)
    ├── glossary.md
    ├── nrc-call-notes.md              # NRC priorities & criteria verbatim
    ├── ars-cheatsheet.md              # condensed ARS mode map
    ├── superpowers-cheatsheet.md      # condensed Superpowers skill map
    ├── sciskills-active.md            # the active 10-skill subset and when each fires
    └── long-running-protocol.md       # CHANGELOG.md protocol + session start/end rituals
```

## CLAUDE.md content (final outline)

1. **Required prefix** (verbatim from `/init`).
2. **Project north star** — repo is a self-study curriculum + capstone targeting an EOI to NRC's Applied Quantum Computing Challenge (QEC stream); capstone aimed at decoder algorithms.
3. **Long-running session protocol** — non-negotiable rituals:
   - **Session start:** read `CHANGELOG.md` first. Identify current status + last-failed-approach to avoid.
   - **During work:** append failed approaches with one-line reason as you hit them.
   - **Session end:** append a Completed-milestone or Accuracy-table entry. Run `scripts/update_changelog.py` if it makes that easier.
4. **Three pillar workflows** — bullet statement: engineering follows Superpowers; paper/EOI follows ARS; specialized scientific tooling pulled from Scientific Agent Skills. Install commands inline.
5. **Repository layout** — short table.
6. **Stack & commands** — `uv sync`, `uv run pytest [path]`, `uv run jupyter lab`, `uv run ruff check .`, `bash scripts/install_plugins.sh`, `python scripts/verify_reading_list.py`.
7. **Engineering workflow (Superpowers)** — full map. Highlight: writing-plans before src/ changes; TDD for decoders; verification-before-completion before phase close.
8. **Paper/EOI workflow (ARS)** — full map. Highlight: `/ars-lit-review` at Phase 5 entry → NRC criterion 4 evidence; integrity gates non-negotiable.
9. **Scientific Agent Skills — active subset** — the 10-skill table; explicit out-of-scope list.
10. **NRC criterion → asset table** — keeps every session aimed at the EOI.
11. **Working conventions** —
    - Notebooks expose; promoted code in `src/qec_project/` with tests.
    - Stim circuits constructed programmatically; seeds always set; long sweeps via Sinter (local) or Modal (remote).
    - Every phase README: Goals / Deliverables / References + Superpowers/ARS/SciSkills hints.
    - **Integrity rule:** any cited number lives in `docs/reading-list.md` with its DOI; `scripts/verify_reading_list.py` runs in CI.
    - **Memory rule:** every threshold sweep run appends to CHANGELOG's accuracy table with seed + commit; every dead-end gets a Failed-Approaches entry.
12. **Authoring guidance for Claude** —
    - Default to building toward the decoder capstone. If a request looks off-track, surface that.
    - **Engineering tasks:** check Superpowers skills before improvising.
    - **Research/writing tasks:** prefer matching `/ars-*` command.
    - **Domain lookups (arXiv, PyMC, Modal, etc.):** use the Scientific Agent Skills catalog.
    - Use `mcp__github__*` for GitHub interactions (no `gh`).
    - bioRxiv MCP exists but is biology-only — arXiv via SciSkills Paper Lookup.
    - Never fabricate threshold numbers / decoder performance — cite (DOI in reading-list.md) or rerun.

## Critical files to create

| Path | Why |
| --- | --- |
| `CLAUDE.md` | Pins mission, three workflows, CHANGELOG protocol. |
| `CHANGELOG.md` | Long-running agent memory; seeded with empty section headers + one initial status entry. |
| `README.md` (rewrite) | Mission + phase index + plugin install lines. |
| `pyproject.toml`, `.python-version`, `.gitignore`, `.pre-commit-config.yaml` | `uv sync && uv run pytest` from clone. |
| `.github/workflows/ci.yml` | CI: pytest, ruff, verify_reading_list. |
| `.claude/settings.json` | Permissions allowlist. |
| `scripts/install_plugins.sh` | One command installs all three plugins. |
| `scripts/verify_reading_list.py` | Anti-hallucination CI check on cited DOIs. |
| `scripts/update_changelog.py` | Templated CHANGELOG append helper (Completed / Failed / Accuracy entries). |
| `prompts/ars-*.md` | Pre-seeded contexts for the four ARS commands we'll re-run most. |
| `src/qec_project/__init__.py` + subpackages | Empty packages so phase notebooks can `from qec_project.codes import …`. |
| `tests/test_smoke.py` | CI green from day one. |
| Each `phase-NN-*/README.md` | Curriculum spine. |
| `capstone/README.md`, `capstone/proposal/eoi-mock.md` (NRC 7-criterion template), `capstone/proposal/literature-review.md` (stub) | EOI artifacts as week-1 forcing function. |
| `docs/reading-list.md`, `docs/nrc-call-notes.md`, `docs/ars-cheatsheet.md`, `docs/superpowers-cheatsheet.md`, `docs/sciskills-active.md`, `docs/long-running-protocol.md`, `docs/glossary.md` | Seeded docs. |

## What we will *not* create yet

- Phase content (notebooks, real code) — that's the user's learning, not bootstrap.
- Populated `eoi-mock.md` — only the 7-criterion template; real content emerges through Phases 2–5.
- Stim/Qiskit code beyond `__init__.py` and typed interfaces.
- Vendored copies of ARS, Superpowers, or Scientific Agent Skills (plugin installs handle them).

## License hygiene

- ARS: CC-BY-NC 4.0 — install only, don't copy.
- Superpowers + Scientific Agent Skills: install only.
- Our cheatsheets paraphrase upstream and link out.

## Verification

1. `cd /home/user/QEC-Project && ls` shows the skeleton above (including `CHANGELOG.md`).
2. `bash scripts/install_plugins.sh` succeeds; `/ars-plan`, Superpowers skills, and `npx skills` are recognized.
3. `uv sync` resolves without errors.
4. `uv run pytest -q` passes (smoke test).
5. `uv run ruff check .` passes.
6. `python scripts/verify_reading_list.py` passes on seeded list.
7. `python scripts/update_changelog.py --kind milestone --text "Bootstrap complete"` appends to CHANGELOG.md.
8. `git status` clean; commit on `claude/init-project-setup-LlShn`.
9. `git push -u origin claude/init-project-setup-LlShn` succeeds. **No PR opened** unless the user asks.
10. Open `CLAUDE.md` and confirm sections 1–12 are present, three workflow maps included, CHANGELOG protocol prominent.

## Sources

- [Long-running Claude for scientific computing — Anthropic](https://www.anthropic.com/research/long-running-Claude)
- [academic-research-skills — Imbad0202](https://github.com/Imbad0202/academic-research-skills)
- [superpowers — obra](https://github.com/obra/superpowers)
- [scientific-agent-skills — K-Dense-AI](https://github.com/K-Dense-AI/scientific-agent-skills)
