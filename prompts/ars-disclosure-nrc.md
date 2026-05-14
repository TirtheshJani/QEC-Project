# Pre-prompt: `/ars-disclosure` for NRC submission

Paste before invoking the academic-paper.disclosure mode. The output goes
into the EOI / preprint as the AI-use disclosure section.

---

Generate an **AI-use disclosure** paragraph suitable for an NRC Applied
Quantum Computing Challenge EOI and a companion arXiv quant-ph preprint.

**Context (truthful — disclose accurately):**
- Tooling used: Claude Code (this CLI), with three plugins installed in
  the repository:
  - `obra/superpowers` (engineering methodology: TDD, plan-writing, code
    review).
  - `Imbad0202/academic-research-skills` (CC-BY-NC 4.0; paper-production
    pipeline with anti-hallucination integrity gates at stages 2.5 and 4.5).
  - `K-Dense-AI/scientific-agent-skills` (MIT; specialised scientific
    skills, used subset is documented in `docs/sciskills-active.md`).
- Long-running pattern: a project-level `CHANGELOG.md` acted as persistent
  agent memory across all sessions (per Anthropic's *Long-running Claude
  for scientific computing*).

**What the AI was and was not used for:**
- Used for: curriculum scaffolding (Phases 0–5 deliverables), code
  authoring under test-driven development with reviewer agents,
  literature review under ARS integrity gates, draft writing of this
  document and the companion paper.
- **Not** used for: fabricating numerical results, inventing references,
  or replacing the principal author's responsibility for the scientific
  claims. Every reported number is either reproduced from an open-source
  script in `capstone/experiments/` or cited to a paper present in
  `docs/reading-list.md` with a verifiable DOI or arXiv identifier.
- Verification: `scripts/verify_reading_list.py` runs in CI and confirms
  every cited identifier resolves; the ARS `integrity_verification_agent`
  confirmed every paper in the literature review exists and every borrowed
  number reproduces from the cited source.

**Tone:** factual, neutral, single paragraph (≤200 words) suitable for
inclusion verbatim in both the EOI and the arXiv preprint's
"AI-use disclosure" section.

**Compliance:** the disclosure should make explicit that the principal
author retains responsibility for all scientific claims and that the AI
was used as an assistive tool, not as an autonomous co-author.
