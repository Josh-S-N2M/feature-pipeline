---
id: ANALYSIS-<kebab-topic-slug>
version: 1.0.0
doc_type: issue-analysis
status: draft
feature_slug: <slug-of-feature-that-surfaced-this-issue>
generated: <ISO-8601-date>
generated_by: <sub-agent-name or "claude (orchestrator)">
# --- Per-state companion fields (add the block matching your status value) ---
# status: draft  → no additional fields required
#
# status: open   → add:
# since: <ISO-8601-date>
#
# status: adopted → add:
# since: <ISO-8601-date>
# adopted_by_feature_slug: <feature-slug>
# adopted_at: <ISO-8601-date>
#
# status: complete → add:
# since: <ISO-8601-date>
# resolved_by: <description or reference>
# resolved_at: <ISO-8601-date>
# resolution_summary: <one-sentence summary>
#
# status: superseded → add:
# since: <ISO-8601-date>
# superseded_by_issue_id: ANALYSIS-<kebab-topic-slug>
# superseded_at: <ISO-8601-date>
#
# status: wontfix-with-rationale → add:
# since: <ISO-8601-date>
# wontfix_rationale: <rationale text>
# decided_at: <ISO-8601-date>
#
# --- Optional cross-link fields (add only when an evolution event has occurred) ---
# escalates_from: REGISTER-<kebab-topic-slug>   # this analysis was spawned from a register
# escalated_to: PROPOSAL-<kebab-topic-slug>      # a proposal was spawned from this analysis
# rolled_into_register: REGISTER-<kebab-topic-slug>  # advisory: topic also tracked in a register
---

# [Title — state the phenomenon being analysed]

## Contents

Section completion checklist — check each box before this document leaves draft.

- [ ] TL;DR
- [ ] Background / Evidence
- [ ] Root Cause
- [ ] Implications
- [ ] Recommendations / Open Questions
- [ ] Cross-links

## TL;DR

[2–4 sentences. State the phenomenon, the root cause in one line, and whether this issue is currently safe to proceed or warrants blocking action. Example shape: "The pipeline has no X. The root cause is Y in Z. The current feature is unaffected; the systemic gap is not."]

---

## Background / Evidence

[Describe what was observed. Cite concrete file:line evidence where available. Use numbered subsections (1.1, 1.2, …) when multiple independent evidence threads exist — see `Issues/per-agent-design-evaluation-gap/analysis.md` for a 7-subsection example, or keep flat paragraphs for simpler single-thread analyses (see `Issues/adr-placement-rootcause/analysis.md` §1 table). Both shapes are valid; choose based on the number of evidence sources.]

### 1. [Evidence thread or observation heading]

[Body — specific artifact paths, line references, verbatim quotes if load-bearing.]

### 2. [Second evidence thread, if needed — remove subsection if not needed]

[Body.]

---

## Root Cause

[The analytical conclusion. One to three paragraphs. Explain the structural or process cause — not just what went wrong, but why the system allowed it. Reference the evidence sections above by number (§1.1, §2, etc.). For a multi-causal analysis, use H3 subsections (### Causal site 1, ### Causal site 2, …).]

---

## Implications

[What the root cause affects beyond the immediate observation. Address: (a) the current feature or run — is it safe to proceed? (b) the broader system — what else is at risk? Use a table when implications are enumerable and short; use prose when the implications require reasoning to follow.]

---

## Recommendations / Open Questions

[Proposed remediation paths or open questions for the human. Use a table (`| Rec | Description | Owner | Cost shape |`) for multiple options, or a flat numbered list for a short set. Mark items clearly as recommendations (not directives). If no fix is proposed (report-only mode), state that explicitly.]

---

## Cross-links

**Evolution cross-links (per ADR-0046):**
- `escalates_from` — present when this analysis was triggered by a prior register (the register's ID is the value). The register's frontmatter carries a matching `escalated_to` back-link.
- `escalated_to` — present when a proposal was subsequently spawned from this analysis. The proposal's frontmatter carries a matching `escalates_from` back-link.
- Both fields are optional; add them only when the evolution event has occurred. Values must match the `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>` ID format.

**State vocabulary (per ADR-0050):**
Full per-state required companion field table: `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md`. Five-state vocabulary: `draft → open → adopted | complete | superseded | wontfix-with-rationale`.

**Related files:**
- [Cite supporting evidence, related registers, proposals, or pipeline artifacts by path]
