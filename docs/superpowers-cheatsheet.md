# Superpowers — cheatsheet

Upstream: <https://github.com/obra/superpowers>. Installed via
`bash scripts/install_plugins.sh` — **not** vendored.

Paraphrased skill map. The authoritative source is upstream `skills/`.

## Four foundational principles (paraphrased)

1. Test-driven development — write tests first.
2. Systematic over ad-hoc — process over guessing.
3. Complexity reduction — simplicity as primary goal.
4. Evidence over claims — verify before declaring success.

## When to use which Superpowers skill

| Trigger | Skill | Why |
| --- | --- | --- |
| Starting a phase | `brainstorming` | Pin goals + deliverables before any code. |
| Before any non-trivial `src/qec_project/` change | `writing-plans` | Decompose into 2–5 min tasks. Plan file under `plans/`. |
| Building / changing decoder or code-constructor logic | `test-driven-development` | Decoder bugs hide. Property-test against Stim. RED→GREEN→REFACTOR. |
| Implementing a non-trivial algorithm | `subagent-driven-development` | Implementer + independent reviewer agent. |
| Running multiple sweeps at once | `dispatching-parallel-agents` | Map (decoder × noise × distance) onto parallel agents. |
| Concurrent capstone experiments | `using-git-worktrees` | Avoid sim collisions, isolate large output dirs. |
| Sim result doesn't match expectations | `systematic-debugging` | Hypothesis log; eliminate causes one at a time. Append to CHANGELOG "Failed approaches". |
| Before merging a phase branch | `requesting-code-review` + `receiving-code-review` | Plan-compliance check. |
| Before declaring a phase "done" | `verification-before-completion` | Tests, ruff, notebooks, reading-list, CHANGELOG entry. |
| Closing a phase | `finishing-a-development-branch` | Lessons in CHANGELOG; merge decision. |
| Inventing a QEC-specific skill (e.g. `stim-circuit-builder`) | `writing-skills` | Lives under `.claude/skills/qec-<name>/`. |
| Onboarding | `using-superpowers` | Read once. |
