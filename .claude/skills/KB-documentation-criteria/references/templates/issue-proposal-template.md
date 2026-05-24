---
# Universal-required fields (all issue doctypes — ADR-0050 §Decision §4 + ADR-0032)
id: PROPOSAL-<kebab-topic-slug>
# Derivation: UPPERCASE-DOCTYPE + hyphen + kebab-slug of the topic folder name.
# Example: PROPOSAL-auditing-family-graduation-review
version: 0.1.0
doc_type: issue-proposal
# Canonical string per ADR-0045 / Q-BE-1. Do NOT use "proposal" (pre-rename value).
status: draft
# 5-state vocabulary (ADR-0050): draft | open | adopted | complete | superseded | wontfix-with-rationale
# Per-state companion fields (full table in issue-doctypes-spec.md):
#   draft               — no additional fields required
#   open                — since: <ISO-8601 date>
#   adopted             — since: <date>, adopted_by_feature_slug: <slug>, adopted_at: <date>
#   complete            — since: <date>, resolved_by: <description>, resolved_at: <date>, resolution_summary: <text>
#   superseded          — since: <date>, superseded_by_issue_id: <PROPOSAL-slug>, superseded_at: <date>
#   wontfix-with-rationale — since: <date>, wontfix_rationale: <text>, decided_at: <date>
feature_slug: <feature-slug-that-originated-this-capture>
generated: <ISO-8601-date>
generated_by: <sub-agent-name or "claude (planning-mode)">

# Proposal-distinctive advisory field (ADR-0050 §Decision §6):
# When present, any string is accepted — no format enforcement.
# When absent, the validator emits an info-severity finding (advisory, not blocker).
# Two accepted shapes observed in precedents (F-006):
#   suggested-slug form: proposes_future_feature: auditing-family-structure-review-r1 (suggested slug)
#   fixed-slug form:     proposes_future_feature: issue-capture-mechanism-r1
# Both shapes are valid. Use the suggested-slug annotation when the future feature slug
# is not yet confirmed; omit the annotation when the slug is fixed.
proposes_future_feature: <feature-slug or "feature-slug (suggested slug)">

# Optional cross-link fields (ADR-0046 / ADR-0050 §Decision §5):
# Include only when this proposal evolved from an existing sibling doctype.
# escalates_from: <ANALYSIS-topic-slug or REGISTER-topic-slug>
# escalated_to: <REGISTER-topic-slug>    # if this proposal triggered a register
# rolled_into_register: <REGISTER-id>    # advisory; cross-topic relationship
---

# Proposal — [Human-readable title describing the future-feature opportunity]

## Contents

Section completion checklist — each box must be checked (including `N/A` rows) before
this document leaves draft.

- [ ] TL;DR
- [ ] Proposed Feature
- [ ] Motivation
- [ ] Open Questions
- [ ] Scope Considerations
- [ ] Cross-links

## TL;DR

[2–4 sentences. Identify the opportunity or gap; state what future feature this proposes
and why it is worth a pipeline run. Do not restate the title verbatim — add signal.]

## Proposed Feature

[High-level shape of the feature this proposal seeds. Suggested feature slug (or fixed
slug if already confirmed). Describe the key deliverables or mechanism the future run
would produce. Keep to 3–8 bullet points or a short paragraph — the Blueprint stage will
refine this.]

## Motivation

[What gap, observed problem, or opportunity grounds this proposal? Cite evidence: an ADR
decision, a Gate 4 output, a codebase-analysis finding, user feedback, or a prior Issue
file. Explain why the gap matters and what happens if it remains unaddressed.]

## Open Questions

[Unresolved design questions for the future feature run to answer. Frame as questions, not
answers. Examples: "Should X subsume Y, or remain a sibling?"; "Is the failure-domain blast
radius distinct enough to warrant a separate layer?"]

- [ ] Q1: [Question]
- [ ] Q2: [Question]

## Scope Considerations

**In-scope (proposed):**
- [Item 1]

**Out-of-scope (proposed):**
- [Item 1]

**Deferred / conditionally in-scope:**
- [Item 1]

## Cross-links

- **Escalates from**: [Path to prior analysis or register, if applicable — per ADR-0046]
- **Escalated to**: [Path to register or analysis this proposal triggered, if applicable]
- **Companion artifacts**: [Paths to supporting files that ground this proposal]
- **Related ADRs**: [e.g., ADR-0045 (three doctypes), ADR-0046 (sibling evolution), ADR-0050 (5-state lifecycle)]
- **Structural spec**: `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md`
  (full per-state companion-field table and doctype vocabulary)

---

<!-- Authoring notes — delete this section in the final file -->

**Frontmatter discipline:**
- `id`: PROPOSAL-<kebab-topic-slug>. Matches the topic folder name. Validator verifies the match.
- `doc_type`: must be `issue-proposal` (canonical post-rename value per Q-BE-1).
- `status`: start at `draft`; advance via /capture-issue --update <path>.
- `proposes_future_feature`: advisory field; omitting it is valid but the validator emits an
  info-severity finding. Include it whenever the future feature slug is known or guessable.
- Cross-link fields (`escalates_from`, `escalated_to`, `rolled_into_register`) are optional.
  Add them only when evolution from a sibling doctype has occurred (ADR-0046).

**Structural-only reminder (ADR-0049):**
- This template codifies shape only. Doctype-classification rubric and approval-prompt
  wording live in KB-issue-capture/references/, not here.

**Body shape reference:**
- Two precedents: Issues/auditing-family-graduation-review/proposal.md (suggested-slug form)
  and Issues/issue-capture-mechanism/proposal.md (fixed-slug form).
-->
