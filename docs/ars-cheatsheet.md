# Academic Research Skills (ARS) — cheatsheet

Upstream: <https://github.com/Imbad0202/academic-research-skills> (CC-BY-NC 4.0).
Installed via `bash scripts/install_plugins.sh` — **not** vendored.

Paraphrased mode map. Authoritative source is upstream `MODE_REGISTRY.md`.

## When to invoke which `/ars-*` command

| Command | Mode | We use it for |
| --- | --- | --- |
| `/ars-plan` | academic-paper.plan | Socratic outline of the capstone paper or EOI. |
| `/ars-outline` | academic-paper.outline-only | Section-by-section paper structure. |
| `/ars-full` | academic-paper.full | First-pass LaTeX-ready capstone draft. |
| `/ars-revision` | academic-paper.revision | Apply reviewer comments to the draft. |
| `/ars-revision-coach` | academic-paper.revision-coach | Parse reviewer comments → prioritized plan. |
| `/ars-abstract` | academic-paper.abstract-only | Capstone abstract; bilingual (EN/FR) for NRC. |
| `/ars-lit-review` | deep-research.lit-review or .systematic-review | Phase 5 entry — produces the gap statement. |
| `/ars-fact-check` | deep-research.fact-check | Verify any claim before it ships into a notebook. |
| `/ars-citation-check` | academic-paper.citation-check | Verify references before submission. |
| `/ars-format-convert` | academic-paper.format-convert | LaTeX / APA-7 / Vancouver conversions. |
| `/ars-disclosure` | academic-paper.disclosure | AI-use disclosure paragraph. NRC-relevant. |
| `/ars-review` (no slash; via mode trigger) | academic-paper-reviewer.full | Run an internal peer review against NRC criteria. |
| `/ars-socratic` (via trigger) | deep-research.socratic | Guided explanation of a math/QM concept. |

## Agent roster (when to spawn one explicitly via the Agent tool)

Use these when the matching slash command isn't a fit but you want the role.

- `research_architect_agent` — designing experiment matrices (Phase 5 capstone).
- `bibliography_agent` — populating `docs/reading-list.md`.
- `devils_advocate_agent` — pressure-testing a claim (overhead estimates,
  novelty claims, threshold reproductions).
- `integrity_verification_agent` — the integrity-gate enforcer at stages
  2.5 and 4.5.
- `risk_of_bias_agent` — useful when reviewing decoder papers that compare
  unfavorably-tuned baselines.
- `methodology_reviewer_agent` — reviews the methodology section of the
  capstone draft before `/ars-review`.
- `synthesis_agent` — generates the §6 (Economic/social impact) narrative.
- `collaboration_depth_agent` — produces the delegation-intensity log that
  doubles as NRC criterion 2 (team & resources) evidence.

## Pre-seeded prompts

The four ARS commands we re-run most have pre-seeded QEC contexts in
`prompts/`:

- `prompts/ars-plan-capstone.md`
- `prompts/ars-lit-review-decoders.md`
- `prompts/ars-review-eoi.md`
- `prompts/ars-disclosure-nrc.md`

Paste the prompt's contents before invoking the slash command so the agent
starts inside our capstone scope.

## Non-negotiable: integrity gates

- **Stage 2.5** (post lit review): every paper exists; every cited number
  reproduces. Block the project until clean.
- **Stage 4.5** (post experiments): every figure regenerable from a script;
  every accuracy number logged in `CHANGELOG.md`; `verify_reading_list.py`
  green.
