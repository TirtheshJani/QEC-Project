# Long-running session protocol

This repo is a 4–6 month, many-session research project. Anthropic's
*Long-running Claude for scientific computing* describes the pattern this
follows: **a project-level journal (`CHANGELOG.md`) acts as portable
long-term memory across sessions.** Their C-compiler project demonstrated
it at ~2000 sessions to compile the Linux kernel.

Sources:
- <https://www.anthropic.com/research/long-running-Claude>

## The rule

**Read `CHANGELOG.md` first thing every session. Write to it before you stop.**

That's it. If you only remember one ritual from this repo, that's it.

## Sections of `CHANGELOG.md`

- **Current status** — one paragraph: which phase, what's next, blocked on
  what. Update when the situation changes:
  `python scripts/update_changelog.py --kind status --text "..."`
- **Completed milestones** — append on phase / sub-phase completion:
  `python scripts/update_changelog.py --kind milestone --text "Phase 0.1 …"`
- **Decoder accuracy tables (capstone)** — append after every Sinter sweep:
  `python scripts/update_changelog.py --kind accuracy --run-id …
   --code rotated-surface --distance 5 --decoder pymatching --noise SI1000
   --p-phys 1e-3 --p-log 1.2e-5 --shots 1000000 --seed 42 --notes "..."`
- **Failed approaches & why** — append the moment a dead end is confirmed:
  `python scripts/update_changelog.py --kind failed --text "..."`
- **Known limitations** — slow-growing list of constraints:
  `python scripts/update_changelog.py --kind limitation --text "..."`

The single most valuable section over the life of the project is **Failed
approaches & why** — without it, future sessions re-attempt the same dead
ends. Always include the *why*, not just the *what*.

## Session-start ritual (~30 seconds)

1. `cat CHANGELOG.md`
2. Note the current status paragraph and the most recent failed-approaches
   entries.
3. Pick up where the status paragraph said you'd pick up. If it doesn't
   match your intent, update the status first.

## Session-end ritual (~1 minute)

1. Append any new failed approaches.
2. Append a milestone or accuracy entry for what shipped.
3. If the next session should start somewhere new, update the status
   paragraph.

## Why CHANGELOG.md, not Claude's built-in memory?

Three reasons:

1. **Portable.** It travels with the repo, survives plugin changes, and is
   readable by humans and any future AI.
2. **Versioned.** Every entry is in `git log`, so dead ends and milestones
   have an audit trail.
3. **Reviewable.** When the capstone needs a paper-trail (NRC criterion 1
   "Methodology", criterion 2 "Team and resources"), `CHANGELOG.md` IS
   the paper trail.
