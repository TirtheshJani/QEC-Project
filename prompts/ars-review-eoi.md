# Pre-prompt: `/ars-review --mode full` on the mock NRC EOI

Paste before invoking academic-paper-reviewer.full. The reviewers should
score against NRC's evaluation criteria, not generic peer-review rubrics.

---

Conduct a multi-perspective peer review of the document at
`capstone/proposal/eoi-mock.md`. The target venue is **NRC's Applied
Quantum Computing Challenge — Expression of Interest (QEC stream,
Decoding algorithm optimization objective)**.

**Rubric:** Score 0–100 on each of NRC's 7 annex-A evaluation criteria,
equally weighted. For each criterion, return:
- A score with one-line rationale.
- The single most impactful improvement (1–2 sentences).

**The 7 criteria (verbatim from NRC):**
1. **Methodology.** Well-developed workplan, key tasks, viable methodology.
2. **Project team and resources.** Roles, ability, capacity over project
   lifetime; EDI considered.
3. **Alignment with scope.** Clear statement of how it addresses the call.
4. **Addressing a gap.** Value of technology + knowledge gap; risks if
   not funded.
5. **Innovation.** Novelty vs Canadian and international work; metrics
   of success.
6. **Economic and social impacts.** Quantitative estimate of benefits.
7. **NRC collaboration.** NRC lead researcher identified; leverage of
   NRC's resources; feasibility against existing NRC capacity.

**Reviewer perspectives:** assign these explicitly.
- A **methodology reviewer** — pressure-tests the experiment matrix and
  the reproducibility story.
- A **field analyst** — checks novelty against the published decoder
  literature.
- A **Devil's Advocate** — argues the proposal should be rejected; lists
  the strongest counterarguments.

**Output:**
- One paragraph per reviewer perspective (their headline take).
- The 7-row criterion table with scores + improvements.
- A final Accept / Minor Revision / Major Revision / Reject
  recommendation with one-paragraph justification.

**Anti-hallucination:** do not cite papers that aren't already in
`docs/reading-list.md`. If you need to reference a paper that isn't
there, flag it as "uncited — needs adding to reading-list before final
EOI."
