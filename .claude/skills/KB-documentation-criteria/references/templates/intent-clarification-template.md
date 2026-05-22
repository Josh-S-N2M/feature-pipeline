---
id: IC-<feature-slug>
version: 1.0.0
status: draft
feature_slug: <feature-slug>
user_token: <token-from-user-confirmation>
generated: <ISO-8601-UTC>
generated_by: intake-intent-clarifier
---

# Intent Clarification: [Feature Name]

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [ ] Purpose
- [ ] Source
- [ ] Initial Interpretation
- [ ] Clarifying Questions and Answers
- [ ] Clarified Intent
- [ ] Scope Posture
- [ ] Stakeholder Posture (Preliminary)
- [ ] Success Posture (Preliminary)
- [ ] Confirmation
- [ ] Open Items (Pending PRD Authoring)

**Note to authoring sub-agent:** update this list if you add or remove top-level (H2) sections from the document. Do NOT remove the `## Contents` heading — it is required for Gate 0 structural review. Mark each box `[x]` when the corresponding section is complete (or contains an explicit `N/A — out of scope` marker for layers not in scope).

## Purpose

The Intent Clarification document is the first artifact in the feature-pipeline. It captures the user's intent before any PRD or design work begins. It is NOT a requirements document. It is NOT a design document. It is a structured record of: "what does the user want, in their own words, with ambiguities surfaced and resolved."

This document gates progression to PRD Authoring. The user must explicitly confirm the clarified intent (via Intent Confirmation Gate) before the orchestrator proceeds.

## Source

[One sentence: the user's original request, quoted or near-verbatim. Do NOT rephrase to sound more technical or more polished — the user's framing matters.]

## Initial Interpretation

[2–4 sentences: how `intake-intent-clarifier` first understood the request. This is the BEFORE picture — the interpretation BEFORE clarifying questions were asked. The point is to make visible the assumptions the AI was about to bake in.]

## Clarifying Questions and Answers

Each row records one ambiguity that the clarifier surfaced and the user's resolution. ALL questions must have answers before this document can proceed.

| # | Ambiguity | Question Asked | User Answer | Resolved? |
|---|---|---|---|---|
| 1 | [What was unclear] | [Question shown to user via AskUserQuestion] | [User's literal answer] | [x] |
| 2 | [What was unclear] | [Question] | [User's answer] | [x] |

If a question is unanswered, the row's "Resolved?" checkbox is `[ ]` (empty). `shared-document-reviewer`'s Gate 0 check fails any Intent Clarification doc with unresolved checkboxes.

## Clarified Intent

[The intent as it stands AFTER clarifying questions. Replaces the Initial Interpretation. 3–6 sentences. This is what the PRD will be built from.]

## Scope Posture

Three explicit declarations:

### What's in scope

- [Specific, observable thing the feature must accomplish]
- [Another]

### What's NOT in scope (explicitly excluded)

- [Specific thing that might seem in scope but isn't]
- [Another]

### What's undecided (deferred to PRD or later)

- [Question that's relevant but doesn't need to be answered yet]
- [Another]

The "explicitly excluded" section is the most valuable. AI-driven authoring tends to silently expand scope; this section is the user's anchor against that.

## Stakeholder Posture (Preliminary)

[One sentence per primary stakeholder: who they are and what they care about. This is a SKETCH, not the formal Stakeholder Inventory — that lives in the PRD.]

- **[Stakeholder 1]:** [What they care about in 5–10 words]
- **[Stakeholder 2]:** [...]

## Success Posture (Preliminary)

[2–4 sentences: how the user will know this feature is "done" or "working." This is also a SKETCH, formalized into acceptance criteria in the PRD/Blueprint.]

## Confirmation

Before the orchestrator proceeds to PRD Authoring, the user confirms this document. The confirmation token is recorded in frontmatter (`user_token`). The orchestrator's AskUserQuestion at the Intent Confirmation Gate captures this token.

## Open Items (Pending PRD Authoring)

[List of items the user surfaced but explicitly deferred to PRD Authoring or later. Each becomes an open item in the rationale brief for the PRD author.]

- [Open item 1]
- [Open item 2]

---

## Authoring notes (delete in the final document)

**Length budget:** The Intent Clarification doc should be SHORT — typically 60–150 lines. Anything longer suggests the clarifier is doing PRD work prematurely.

**Authored by:** `intake-intent-clarifier`. This sub-agent's role is narrow:
1. Read the user's request.
2. Produce the Initial Interpretation.
3. Surface ambiguities as AskUserQuestion calls.
4. Record answers verbatim.
5. Synthesize the Clarified Intent.
6. Produce Scope Posture (in / out / undecided).
7. Sketch Stakeholder and Success postures.
8. Surface open items for the PRD.

What this sub-agent MUST NOT do:
- Author Functional Requirements (that's the PRD)
- Author Acceptance Criteria (that's the PRD/Blueprint)
- Make design decisions (that's per-layer Design)
- Recommend a specific tech stack (Discovery + Design Composition)

**Frontmatter `user_token`:** The orchestrator generates a unique token at the Intent Confirmation Gate and records it. Downstream sub-agents reference this token in their rationale briefs as confirmation that the user actively gated this intent (rather than the clarifier proceeding without confirmation).
