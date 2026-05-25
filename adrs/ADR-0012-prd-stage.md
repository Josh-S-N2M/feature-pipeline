---
id: ADR-0012
version: 2.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes: []
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0009 (rationale brief at stage handoff)
  - ADR-0011 (canonical document skill)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0
superseded_by_consolidation: 2026-05-25
superseded_canonical_archived_to: adrs/superseded/ADR-0012-pre-consolidation-canonical.md
---

# ADR-0012: PRD generation as Stage 1.5 with single sub-agent (intake-prd-author)

## Status

Accepted — 2026-05-12

## Context

Blueprint v3 transitioned directly from Intent Clarification (Stage 1) to Research Planning (Stage 2). The user has identified that an explicit business-requirements artifact — a Product Requirements Document (PRD) — should sit between these stages, structuring the clarified intent into stakeholder-tagged functional and non-functional requirements before research is planned.

A PRD differs from Intent Clarification in scope: Intent Clarification surfaces what the user wants and what's ambiguous; the PRD enumerates stakeholders, defines layer scope as product surfaces, formalizes user stories per stakeholder, tags functional requirements with stakeholder + layer, organizes non-functional requirements by quality attribute, declares product policy decisions, and defines success criteria with measurable targets.

Research planning benefits materially from having a structured PRD as input rather than a free-form intent: research topics can be derived from PRD sections (each stakeholder's user stories → research topics; each non-functional requirement → research topics on relevant patterns; each product policy decision → research topics on common approaches).

## Decision

Insert a new pipeline stage between Intent Clarification (Stage 1) and Research Planning (Stage 2): Stage 1.5 — PRD Generation. A single sub-agent (`intake-prd-author`) consumes the Intent Clarification document and produces a PRD following the canonical PRD template (sourced from `KB-documentation-criteria` per ADR-0011). A new human gate, PRD Approval, fires after shared-document-reviewer review of the PRD.

## Decision Details

| Item | Content |
|---|---|
| Decision | Single sub-agent `intake-prd-author` produces the PRD as a coherent document; not fan-out across stakeholder perspectives. |
| Why now | Adding PRD as a separate stage before research planning is the right time to commit to a single-author topology, before downstream stages depend on a different shape. |
| Why this | PRDs require unified voice across stakeholder sections — stakeholder enumeration and cross-cutting policy decisions are coherent only when authored together. Fan-out across stakeholder perspectives would force a composer to reconcile voice, terminology, and emphasis without obvious gain (claim C-R3-0015: AI quality on user stories is HIGH; the issue is over-generation not under-coverage). |
| Known unknowns | Whether PRDs for very large multi-stakeholder features (5+ distinct stakeholder groups) will hit intake-prd-author's context limits; whether the single-author topology will need re-evaluation if practical experience shows specific stakeholder sections being consistently underdeveloped. |
| Kill criteria | If 3+ consecutive feature runs produce PRDs where shared-document-reviewer issues `important` or `critical` issues for missing stakeholder coverage despite the stakeholder being identified, supersede with a stakeholder-fan-out design. |

## Rationale

Three findings converge on single-author:

(1) Claim C-R3-0015 documents AI quality is HIGH for problem statement, user stories, acceptance criteria, and edge cases — the bulk of PRD content. The issue is not depth per stakeholder but rather over-generation and missing organizational context. Fan-out doesn't address either problem.

(2) Claim C-R3-0017 documents AI tendency to produce 8-12 user stories when MVP needs 3-4. Fan-out across stakeholder perspectives would multiply this — each per-stakeholder author produces over-broad lists, and the composer must prune from a larger surface area.

(3) Claim C-R3-0024 (Microsoft Conductor) demonstrates that parallel specialist reviewers feeding a synthesis step is a documented production pattern — but reviewers, not authors. The patterns for parallel-author coherence (entity canonicalization, evidence-based arbitration per claim C-R3-0013) add complexity that the PRD use case doesn't warrant.

The single-author approach trades depth-per-stakeholder for unified voice and reduced reconciliation cost. Document-reviewer's stakeholder-coverage checks catch under-coverage post-hoc — the safer side of the tradeoff to land on.

## Options Considered

**Option 1: Fan-out across stakeholder perspectives.** One sub-agent per major stakeholder type (end-user-perspective-author, api-consumer-perspective-author, admin-perspective-author, etc.) producing per-stakeholder sections; composer integrates.
- Pros: each stakeholder section gets focused attention; per-stakeholder context isolation.
- Cons: PRDs have substantial cross-cutting content (Layer Scope, Product Policy Decisions, Success Criteria, Rollout Plan) that doesn't map to stakeholders; voice inconsistency requires composer reconciliation; over-generation per claim C-R3-0017 multiplies.

**Option 2: Two-pass single-author.** intake-prd-author writes a draft, then a second invocation refines based on shared-document-reviewer feedback.
- Pros: bounded refinement loop with explicit improvement target.
- Cons: this is already captured by the shared-document-reviewer iteration discipline (ADR-0017 forthcoming) — adding explicit two-pass scheduling duplicates that mechanism.

**Option 3 (Selected): Single sub-agent (intake-prd-author) producing the full PRD in one invocation.**
- Pros: unified voice; minimal coordination overhead; matches AI-quality profile per claim C-R3-0015; shared-document-reviewer catches under-coverage post-hoc; aligns with production-validated pattern from Microsoft Conductor (single author, parallel reviewers).
- Cons: very large multi-stakeholder features may stress context budget; less depth per stakeholder section than fan-out would produce.

## Consequences

### Positive Consequences

- Single authorial voice across the PRD.
- Reduced coordination overhead vs fan-out (no composer step needed at Stage 1.5).
- Pipeline shape stays linear at the PRD stage; only Stage 5 (Design) uses fan-out per Q-v4-3 inverted.
- KB-documentation-criteria can teach the full PRD template structure to one agent rather than coordinating multiple per-stakeholder skills.
- AI-PRD failure modes (claim C-R3-0014) are addressed in one place via KB-documentation-criteria content guidance.

### Negative Consequences

- For features with 5+ stakeholder groups, intake-prd-author may produce under-detailed per-stakeholder sections. shared-document-reviewer's "stakeholder coverage gaps" check (extension of its existing completeness analysis) is the mitigation; not preventive.
- Single agent owning all PRD content means a single failure point — if intake-prd-author hallucinates, the entire PRD is suspect rather than just one section.
- maxTurns budget for intake-prd-author needs to be generous (recommendation: 50, matching synth-designer) to allow multi-section authoring without truncation.

### Neutral Consequences

- PRD becomes a versioned artifact in the run directory: `01-5-prd-v1.md` (and subsequent versions on supersession per ADR-0005).

## Architecture Impact

**Components that change:**
- Pipeline topology gains Stage 1.5 between Stage 1 and Stage 2.
- Sub-agent inventory adds `intake-prd-author`.
- Knowledge skill inventory adds `KB-documentation-criteria`.
- Human-gate inventory adds **PRD Approval Gate** (after shared-document-reviewer review of the PRD).
- Research planner (Stage 2) input changes: now consumes the approved PRD rather than the Intent Clarification document.

**New dependencies introduced:**
- `intake-prd-author` depends on `KB-documentation-criteria` (for PRD template) and `KB-documentation-criteria` (for process guidance).
- Stage 2 (Research Planning) depends on Stage 1.5's approved PRD output.

**Architectural constraints added:**
- Stage 2 (Research Planning) MUST NOT begin until PRD Approval Gate clears.
- intake-prd-author MUST produce the PRD as a single markdown document per the canonical template.
- shared-document-reviewer MUST run on the PRD before the PRD Approval Gate fires (per ADR-0017).

**Architectural constraints removed:**
- None. Prior gate structure preserved.

## Implementation Guidance

- intake-prd-author's tools should be Read (clarified intent doc + manifest), Write (PRD output), AskUserQuestion (for clarification of business-level ambiguities that surface during PRD authoring).
- Memory: `project`.
- maxTurns: 50.
- intake-prd-author should NOT have Agent tool (recursion-safe; cannot spawn sub-agents).
- KB-documentation-criteria should include explicit guidance on AI-PRD failure modes (claim C-R3-0014): never fabricate customer reactions; specify exact dimensions only with rationale; do not include implementation suggestions; do not over-generate user stories (target 3-4 per stakeholder for MVP).
- The PRD Approval Gate uses AskUserQuestion with options: `approve / refine / cancel` with text-input for refinement direction.

## Related Information

- ADR-0011 (canonical document skill): PRD template lives in `KB-documentation-criteria`.
- ADR-0017 (forthcoming): shared-document-reviewer integration — reviews PRD at Stage 1.5 completion.
- ADR-0009 (rationale brief): orchestrator generates brief at Stage 1 → Stage 1.5 handoff and at Stage 1.5 → Stage 2 handoff.
- Claims C-R3-0014, C-R3-0015, C-R3-0016, C-R3-0017: AI PRD failure modes and quality profile.
- User-provided template: PDR.txt (uploaded; adopted as canonical PRD template via ADR-0011).

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0012-prd-stage-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
