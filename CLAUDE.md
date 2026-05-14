# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project north star

This repository is a self-study quantum-error-correction (QEC) curriculum +
capstone targeting an Expression of Interest to NRC's Applied Quantum
Computing Challenge (QEC stream, *Decoding algorithm optimization*
objective). The capstone is a decoder benchmark study on the rotated
surface code. Treat every session as building toward that artifact — if a
request looks off-track, surface it before acting.

Anchor docs:
- `docs/nrc-call-notes.md` — NRC priorities and EOI criteria, verbatim.
- `capstone/README.md` — capstone scope and experiment matrix.
- `capstone/proposal/eoi-mock.md` — the mock EOI, filled iteratively.

## Long-running session protocol (non-negotiable)

This is a multi-month, many-session project. Per Anthropic's
[*Long-running Claude for scientific computing*](https://www.anthropic.com/research/long-running-Claude),
`CHANGELOG.md` is the project's portable long-term memory.

- **Session start:** read `CHANGELOG.md` first. Note current status and the
  most recent "Failed approaches" entries so you don't re-attempt dead ends.
- **During work:** append failed approaches with a one-line *why* as you
  hit them.
- **Session end:** append a milestone or accuracy-table entry. If the next
  session should start somewhere new, update the status paragraph.
- **Helper:** `python scripts/update_changelog.py --kind {status|milestone|failed|accuracy|limitation} ...`
- Full ritual: `docs/long-running-protocol.md`.

## Three pillar workflows

Installed by `bash scripts/install_plugins.sh` (none vendored):

```
/plugin install superpowers@claude-plugins-official
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
npx skills add K-Dense-AI/scientific-agent-skills
```

- **Engineering** (`src/qec_project/`, `tests/`, `scripts/`, `capstone/experiments/`)
  → **Superpowers**. See `docs/superpowers-cheatsheet.md`.
- **Paper / EOI** (`capstone/proposal/`, `capstone/paper/`, `docs/reading-list.md`)
  → **ARS**. See `docs/ars-cheatsheet.md`. Pre-seeded prompts in `prompts/`.
- **Specialised scientific tooling** (arXiv lookup, neural-decoder stack,
  GPU scale-out, Bayesian uncertainty, figure quality, Modal cloud burst)
  → **Scientific Agent Skills** (focused subset). See `docs/sciskills-active.md`.

## Repository layout

| Path | Purpose |
| --- | --- |
| `phase-00-foundations/` … `phase-05-advanced-decoders/` | Curriculum spine; each has a README with Goals/Deliverables/References. |
| `capstone/` | Decoder benchmark study: proposal, experiments, figures, paper, README. |
| `src/qec_project/` | Reusable code (codes, decoders, noise, analysis). TDD-tested. |
| `tests/` | Mirrors `src/`. |
| `scripts/` | Install plugins, verify reading-list, update CHANGELOG, threshold sweep harness. |
| `plans/` | Superpowers `writing-plans` outputs. |
| `prompts/` | QEC-tailored pre-prompts for ARS slash commands. |
| `docs/` | Reading list, glossary, NRC notes, plugin cheatsheets, long-running protocol. |
| `.claude/` | Project-scoped Claude config (permissions + skills dir). |
| `CHANGELOG.md` | Cross-session memory (read first, write last). |

## Stack & commands

```bash
uv sync --extra dev                                    # install
uv run pytest                                          # all tests
uv run pytest tests/test_codes.py::test_steane         # one test
uv run jupyter lab                                     # notebooks
uv run ruff check .                                    # lint
uv run mypy src/qec_project                            # type-check (advisory)
bash scripts/install_plugins.sh                        # install plugins
python scripts/verify_reading_list.py                  # CI: DOIs resolve
python scripts/update_changelog.py --kind milestone --text "..."
uv run python scripts/run_threshold_sweep.py --help    # capstone harness
```

ML / remote work pulls extras: `uv sync --extra ml`, `uv sync --extra remote`.

## Engineering workflow (Superpowers governs)

| Trigger | Skill | What happens |
| --- | --- | --- |
| Start of a phase | `brainstorming` | Pin goals + deliverables. |
| Before non-trivial `src/qec_project/` change | `writing-plans` | Plan file under `plans/`; 2–5 min tasks. |
| Decoder / code-construction work | `test-driven-development` | Property-test against Stim ground truth. RED→GREEN→REFACTOR. |
| Decoder implementation | `subagent-driven-development` | Implementer + independent reviewer agent. |
| Multiple sweeps in parallel | `dispatching-parallel-agents` | One agent per (decoder × noise × distance), backed by Sinter / Modal. |
| Concurrent experiments | `using-git-worktrees` | Sims don't collide. |
| Sim diverges from expected | `systematic-debugging` | Hypothesis log; eliminate causes one at a time. **Append the dead end to CHANGELOG.** |
| Before merging | `requesting-code-review` + `receiving-code-review` | Plan-compliance review. |
| Before declaring a phase done | `verification-before-completion` | Tests pass, ruff clean, notebooks rerun, `verify_reading_list.py` green, CHANGELOG updated. |
| Closing a phase | `finishing-a-development-branch` | Merge decision; lessons captured. |
| Inventing a QEC-specific skill | `writing-skills` | Under `.claude/skills/qec-<name>/`. |

## Paper / EOI workflow (ARS governs)

| QEC stage | ARS command / agent | Produces |
| --- | --- | --- |
| Phase 0–1 stuck on math/QM | `/ars-socratic` | Guided Socratic explanation. |
| Phase 2+ new "fact" notebook | `/ars-fact-check` | Citation against primary refs; update `docs/reading-list.md`. |
| Phase 3 surface-code reading | `/ars-lit-review` | First slice of capstone bibliography. |
| Phase 4 overhead claims | `devils_advocate_agent` | Stress-tests overhead/threshold estimates. |
| **Phase 5 entry — capstone gap** | `/ars-lit-review --mode systematic-review` + `prompts/ars-lit-review-decoders.md` | PRISMA gap statement → `capstone/proposal/literature-review.md`. **NRC criterion 4 evidence.** |
| Capstone planning | `/ars-plan` + `prompts/ars-plan-capstone.md` | Outline + experiment matrix. |
| Capstone outline | `/ars-outline` | Section-by-section structure. |
| Capstone draft | `/ars-full` | LaTeX-ready first pass. |
| Capstone integrity gates | `academic-pipeline` stages 2.5 & 4.5 | `integrity_verification_agent` verifies citations exist and numbers reproduce. **Non-negotiable.** |
| Internal peer review | `/ars-review --mode full` + `prompts/ars-review-eoi.md` | Multi-perspective 0–100 rubric on NRC criteria. |
| EOI revision | `/ars-revision-coach` | Prioritized revision plan. |
| EOI abstract (EN; optional FR) | `/ars-abstract` (bilingual) | Bilingual abstract. |
| Format | `/ars-format-convert` + `/ars-citation-check` | Tectonic LaTeX + verified bib. |
| EOI final pass | `/ars-disclosure` + `prompts/ars-disclosure-nrc.md` | AI-use disclosure. |

## Scientific Agent Skills — active subset

| Skill | When |
| --- | --- |
| **Paper Lookup** (arXiv) | Capstone lit review; the biggest gap in our base toolkit. |
| **BGPT Paper Search** | Structured metadata across decoder papers. |
| **Scientific Writing / Peer Review** | Second-opinion review independent of ARS. |
| **Matplotlib / Seaborn** | Publication-quality figures. |
| **NetworkX** | Tanner graphs, lattice-surgery diagrams. |
| **scikit-learn + PyTorch Lightning** | Phase 5 neural decoder. |
| **SHAP** | Interpret what the neural decoder learned (novelty angle). |
| **PyMC** | Bayesian uncertainty on threshold estimates. |
| **GPU Optimization** (CuPy / Numba CUDA) | Scaling decoder Monte Carlo. |
| **Modal** | Cloud burst for $d \geq 11$ sweeps. |
| **What-If Oracle** | "Which decoder under which noise wins" scenario analysis. |

Out of scope (do not pull): everything bio/chem/clinical. Full list in
`docs/sciskills-active.md`.

## NRC EOI criterion → asset map

| NRC annex-A criterion | Where the evidence lives |
| --- | --- |
| 1. Methodology | `capstone/experiments/` + Superpowers TDD trail; `methodology_reviewer_agent`. |
| 2. Project team & resources | Completed phase deliverables; `collaboration_depth_agent` log. |
| 3. Alignment with scope | `capstone/proposal/eoi-mock.md` §3; `/ars-plan` + `research_architect_agent`. |
| 4. Addressing a gap | `capstone/proposal/literature-review.md`; `/ars-lit-review --mode systematic-review` + Paper Lookup. |
| 5. Innovation | `capstone/paper/` novelty section; `devils_advocate_agent`. |
| 6. Economic/social impact | `capstone/proposal/eoi-mock.md` §6; `synthesis_agent`. |
| 7. NRC collaboration | Hand-drafted §7; `/ars-revision-coach`. |
| Anti-hallucination | ARS integrity gates + `verify_reading_list.py` (CI) + CHANGELOG "Failed approaches". |
| AI-use disclosure | `/ars-disclosure`. |

## Working conventions

- Notebooks expose ideas; **promoted** code lives in `src/qec_project/` with
  tests before it's relied on downstream (Superpowers TDD).
- Stim circuits are constructed **programmatically**; save `.stim` files
  only as reproducibility artifacts.
- Seeds set in every experiment. Long sweeps via `sinter` for resumability
  (local) or Modal (remote).
- Every phase README starts with **Goals / Deliverables / References** plus
  Superpowers / ARS / SciSkills hints.
- **Integrity rule.** Any number cited from a paper must live in
  `docs/reading-list.md` with its DOI or arXiv ID. `scripts/verify_reading_list.py`
  enforces this in CI.
- **Memory rule.** Every threshold sweep run appends an Accuracy entry to
  `CHANGELOG.md` with seed + commit SHA. Every dead end gets a Failed-Approaches
  entry the same session it happens.

## Authoring guidance for Claude

- Default to building toward the decoder capstone. If a request looks
  off-track, surface that.
- **Engineering tasks:** check Superpowers skills first; write a plan
  (`writing-plans`), then a test (`test-driven-development`), then the
  code. Don't improvise around the methodology.
- **Research/writing tasks:** prefer the matching `/ars-*` command over
  rolling your own. Use the pre-seeded prompt in `prompts/` when one
  exists.
- **Domain lookups (arXiv, PyMC, Modal, neural-decoder ML, GPU sims):**
  reach into the Scientific Agent Skills catalog — but stay inside the
  active subset listed in `docs/sciskills-active.md`. Don't pull bio/chem
  skills.
- Use `mcp__github__*` for any GitHub interaction (the harness blocks
  `gh`). Scope is restricted to `tirtheshjani/qec-project`.
- bioRxiv MCP is biology-only — don't use it for QEC literature. arXiv
  access goes through Scientific Agent Skills' Paper Lookup.
- **Never fabricate threshold numbers, decoder accuracies, or paper
  metadata.** Cite the paper (with DOI in `docs/reading-list.md`) or
  rerun the sim. ARS `integrity_verification_agent` exists to catch this.
- Develop on branch `claude/init-project-setup-LlShn` per the
  user's standing instruction. Don't push to other branches without
  explicit permission.
