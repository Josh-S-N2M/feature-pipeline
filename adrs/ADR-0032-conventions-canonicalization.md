---
id: ADR-0032
title: Conventions canonicalization — pipeline-frontmatter fields, per-doc-type state vocabulary, and `doc_type` taxonomy
status: proposed
date: 2026-05-22
deciders: [user, claude (as design-composer)]
supersedes: []
superseded_by: []
related: [ADR-0005, ADR-0017, ADR-0019, ADR-0029, ADR-0031]
authored_in_feature: execution-pipeline-design-r1
pairs_synthesis_decisions: [D-4, D-18]
subsumes: ["IN-005 doc_type taxonomy gap (3rd observed instance)"]
---

# ADR-0032: Conventions canonicalization — pipeline-frontmatter fields, per-doc-type state vocabulary, and `doc_type` taxonomy

## Context

During the `execution-pipeline-design-r1` Discovery Research stage (codebase-analysis.md v1.1.1, IN-004 and IN-005), substantial drift was identified between `shared-conventions.md` v1 (the canonical spec) and what pipeline artifacts actually produce in practice across multiple feature runs. Three distinct categories of drift were observed:

**Category 1 — Frontmatter field drift (D-4 substrate)**: Four+ archive-practice fields are used in essentially every gated artifact but are absent from the spec:
- `gate_passed: <integer>` — present in every gated artifact (IC, PRD, Research Plan, Blueprint, Plan)
- `approved_at: <ISO-8601-UTC-timestamp>` — present in every artifact after reviewer pass
- `reviewer_verdict: <string>` — present in every artifact after reviewer pass; format varies but consistently includes Gate 0/1 pass+scores
- `<prior-stage>_user_token` chain — discipline already in practice: each gated stage carries the prior stage's confirmation token (PRD frontmatter has `intent_user_token`, Research Plan has `prd_user_token`, codebase-analysis has `research_plan_user_token`); the spec only documents `user_token` for Intent Clarification

**Category 2 — State vocabulary drift (D-18 substrate)**: The canonical 5-state vocab (`draft | proposed | accepted | superseded | rejected`) is correct for gated artifacts but doesn't accommodate analysis/log artifacts. Observed:
- codebase-analysis.md uses `status: complete` — NOT in canonical vocabulary
- synthesis.md stays `status: draft` indefinitely — there is no `accepted` state for ungated artifacts, but `draft` semantically implies authoring incomplete which is also wrong
- cc-design.md (per-layer design) — same as synthesis
- ADRs in practice start at `status: accepted` (post-Architecture-Audit) or `status: proposed` (pre-Architecture-Audit) — `draft` is never used

**Category 3 — `doc_type` taxonomy gap (IN-005 substrate)**: The `doc_type` field is implicit in `shared-conventions.md` (sections defined per type) but never surfaced as an explicit frontmatter field. `shared-document-reviewer` references `doc_type` for type-dispatched vocabulary and field-completeness checking — currently has no canonical source. The gap was observed three times during the execution-pipeline-design-r1 run: codebase-analysis lacks doc_type entry, synthesis lacks doc_type entry, cc-design (per-layer design) lacks doc_type entry. The systematic resolution belongs in `shared-conventions.md` alongside the per-doc-type vocabulary categorization (Category 2) since the two are joint dispatch keys.

The three categories share root cause: `shared-conventions.md` v1 was authored before sufficient feature-run experience accumulated to surface the practice/spec divergence. Continuing to accumulate the drift compounds two costs: (a) the frontmatter validator (FR-6 in execution-pipeline-design-r1) cannot mechanically enforce conformance without a canonical spec; (b) every authoring agent has to choose between spec compliance and operational reality, defaulting to the latter and silently perpetuating drift.

## Decision

**Adopt archive-authoritative spec direction**: canonicalize validated archive practice into `shared-conventions.md` (rather than retrofitting practice to match the legacy spec). Three coordinated changes apply:

### Change 1: Universal frontmatter fields (extend required set)

Promote these fields from "implicit-or-doc-type-specific" to universal required:

| Field | Type | Notes |
|---|---|---|
| `feature_slug: <slug>` | string | Universally present in practice; only some doc-type sections specified it. Promote to universal. |
| `derived_from: <path>` | string OR list | Universally present in practice; was previously specified only for Blueprint + Plan. Promote to universal. |

Add these fields as required for gated artifacts (IC, PRD, Research Plan, Blueprint, Plan):

| Field | Type | Notes |
|---|---|---|
| `gate_passed: <integer>` | integer | The pipeline gate number this artifact passed (1 = IC, 2 = PRD, 3 = Research Plan, 4 = Blueprint, 5 = Plan, 6 = Final). Set by orchestrator's state-transition hook (FR-5). |
| `approved_at: <ISO-8601-UTC>` | string | Timestamp of gate-pass. Set by orchestrator's state-transition hook. |
| `reviewer_verdict: <string>` | string | Reviewer-pass verdict in format: `"approved (Gate 0 pass, Gate 1 pass — Consistency N, Completeness N, Rule compliance N, Clarity N)"` for accepted; `"rejected: <reason>"` for rejected. |

Add these fields as optional for revisable artifacts (any of the above plus analysis/log):

| Field | Type | Notes |
|---|---|---|
| `revised: <ISO-8601-UTC>` | string | Timestamp of revision (when artifact has been substantively revised post-acceptance). |
| `revision_reason: <string>` | string | Free-form rationale for the revision. Companion to `revised`. |

### Change 2: User-token chain pattern (formalize chained-token discipline)

The chained-token discipline is already in practice: each gated stage carries the user-token of the prior stage's confirmation, plus adds its own confirmation token. The spec adds an explicit "User-token chain" section documenting the pattern:

```yaml
# Intent Clarification:
user_token: IC-CONFIRM-<feature-slug>-<timestamp>   # the IC's own confirmation token

# PRD:
intent_user_token: IC-CONFIRM-<feature-slug>-<timestamp>   # IC's token (carried forward)
user_token: PRD-CONFIRM-<feature-slug>-<timestamp>          # PRD's own token

# Research Plan:
prd_user_token: PRD-CONFIRM-<feature-slug>-<timestamp>      # PRD's token (carried forward)
user_token: RP-CONFIRM-<feature-slug>-<timestamp>           # RP's own token

# Codebase Analysis (ungated; carries only the upstream token):
research_plan_user_token: RP-CONFIRM-<feature-slug>-<timestamp>

# Blueprint:
research_plan_user_token: RP-CONFIRM-<feature-slug>-<timestamp>
user_token: BP-CONFIRM-<feature-slug>-<timestamp>
```

The chain is the audit trail across the gated stages. The chain pattern is universal for gated artifacts; analysis/log artifacts carry only the most-recent upstream token (their authoring is not itself a gate).

### Change 3: Per-doc-type state vocabulary

Replace the single 5-state vocab with three doc-type-categorized vocabularies:

| Doc-type category | Doc types | Canonical vocabulary | Notes |
|---|---|---|---|
| **Gated artifacts** | `intent-clarification`, `prd`, `research-plan`, `blueprint`, `plan` | `draft` → `proposed` → `accepted` → `superseded` OR `rejected` (5 states) | Current vocab. `proposed` is post-reviewer-pass pre-gate; `accepted` is post-gate-pass. |
| **Analysis/log artifacts** | `codebase-analysis`, `synthesis`, `<layer>-design`, `architecture-audit-issues`, `cross-artifact-audit-issues`, `reconciliation-log`, `task-dag`, plus execution-phase artifacts | `draft` → `complete` OR `superseded` (3 states) | No gate. `complete` is post-reviewer-pass; remains there until superseded. |
| **ADRs** | `adr` (single doc-type) | `proposed` → `accepted` OR `superseded` OR `rejected` (4 states; no `draft`) | ADRs start as `proposed` once authored; reach `accepted` after Architecture Audit pass; `superseded` only via supersession ADR. |

The vocabulary differentiation resolves the drift: codebase-analysis.md's `status: complete` becomes spec-valid (analysis category); synthesis.md and per-layer designs are spec-valid in `status: complete` once reviewer-approved.

### Change 4: `doc_type` field (explicit taxonomy)

Add `doc_type: <enum>` as a required universal field:

| `doc_type` value | Category | Notes |
|---|---|---|
| `intent-clarification` | gated | One per feature run |
| `prd` | gated | Versioned per ADR-0005 |
| `research-plan` | gated | Versioned per ADR-0005 |
| `codebase-analysis` | analysis/log | One per feature run; may be revised |
| `synthesis` | analysis/log | One per feature run |
| `<layer>-design` | analysis/log | One per activated layer (e.g., `claude-code-design`, `backend-design`) |
| `blueprint` | gated | Versioned per ADR-0005 |
| `architecture-audit-issues` | analysis/log | JSON artifact; one per Architecture Audit pass |
| `plan` | gated | Versioned per ADR-0005 |
| `acceptance-tests` | analysis/log | One per feature run |
| `phase-validators` | analysis/log | One per feature run |
| `cross-artifact-audit-issues` | analysis/log | JSON artifact |
| `reconciliation-log` | analysis/log | One per reconciliation cycle |
| `task-dag` | analysis/log | JSON artifact |
| `adr` | ADRs | Per-decision file |
| `per-task-execution-result` | analysis/log | Execution-phase; one pair (.json+.md) per task per D-5 |
| `phase-quality-report` | analysis/log | Execution-phase; one pair per phase |
| `quality-reconciliation-log` | analysis/log | Execution-phase; one pair per reconciliation cycle |
| `state-transitions-log` | analysis/log | Execution-phase; one JSONL file per feature run |
| `pipeline-run-summary` | analysis/log | Execution-phase; one JSON per feature run |

`shared-document-reviewer` uses `doc_type` as the dispatch key for type-specific checks; the validator (FR-6 / `validate_pipeline_frontmatter.py`) uses it to look up the per-doc-type vocabulary and required-field set.

### Change 5: Execution-phase artifact frontmatter (new section)

`shared-conventions.md` gains a new section "Execution-phase artifact frontmatter" documenting the field schemas for the 5 execution-phase artifact types listed in FR-7-c floor plus the 2 introduced beyond the floor (per Blueprint Open items / AC-FR-7-d). The section covers per-task-execution-result, phase-quality-report, quality-reconciliation-log, state-transitions-log, and pipeline-run-summary.

## Validation evidence

Evidence is drawn from the 6 pipeline artifacts produced in this feature run (intent-clarification.md, prd-v1.1.0.md, research-plan.md, codebase-analysis.md, synthesis.md, cc-design.md):

### Frontmatter field practice

| Field | In spec? | Observed in practice (6 artifacts) | Disposition |
|---|---|---|---|
| `gate_passed` | ✗ | 3/6 (IC, PRD, RP) | Add as required for gated artifacts |
| `approved_at` | ✗ | 3/6 (IC, PRD, RP) | Add as required after reviewer pass |
| `reviewer_verdict` | ✗ | 3/6 (PRD, RP, synthesis) | Add as required after reviewer pass |
| `<prior>_user_token` chain | ✗ (only `user_token` for IC) | 4/6 (PRD, RP, codebase-analysis, synthesis indirectly) | Formalize chain pattern (Change 2) |
| `feature_slug` | ✗ universal (only some doc types) | 6/6 | Promote to universal required (Change 1) |
| `derived_from` | ✗ universal (only Blueprint, Plan) | 6/6 (every non-IC artifact) | Promote to universal required (Change 1) |
| `revised` | ✗ | 3/6 (RP, codebase-analysis, synthesis) | Add as optional for revised artifacts (Change 1) |
| `revision_reason` | ✗ | 3/6 (RP, codebase-analysis, synthesis) | Add as optional companion (Change 1) |

### State vocabulary practice

| Artifact | Observed `status` | In canonical 5-state vocab? | Disposition under per-doc-type vocab (Change 3) |
|---|---|---|---|
| intent-clarification.md | `accepted` | ✓ | ✓ (gated; `accepted` is valid) |
| prd-v1.1.0.md | `accepted` | ✓ | ✓ (gated; `accepted` is valid) |
| research-plan.md | `accepted` | ✓ | ✓ (gated; `accepted` is valid) |
| codebase-analysis.md | `complete` | ✗ | ✓ (analysis/log; `complete` is valid) |
| synthesis.md | `draft` (would stay `draft` indefinitely under v1 vocab) | partial — `draft` itself is valid but no `accepted` next state for ungated | Becomes `complete` post-reviewer per Change 3 |
| cc-design.md (per-layer design) | `draft` (would stay `draft` indefinitely under v1 vocab) | partial — same as synthesis | Becomes `complete` post-reviewer per Change 3 |
| (no ADR in this feature's working dir yet; ADR-0032 itself is `proposed` per Change 3) | n/a | n/a | `proposed` initial state per Change 3 ADR vocab |

### Doc-type taxonomy practice

Three observed instances of doc_type taxonomy gap during this feature run:
- codebase-analysis.md — `doc_type` absent; vocabulary check defaults to gated 5-state (incorrect for analysis)
- synthesis.md — `doc_type` absent; vocabulary check defaults to gated 5-state (incorrect for analysis)
- cc-design.md — `doc_type` absent; vocabulary check defaults to gated 5-state (incorrect for analysis)

All three resolve under Change 4 (explicit `doc_type` field) + Change 3 (per-doc-type vocabulary dispatch).

## Consequences

**Positive:**

- Spec reflects archive-validated practice. Future authoring agents don't have to choose between spec compliance and operational reality.
- `shared-document-reviewer` and `validate_pipeline_frontmatter.py` (FR-6) can mechanically validate frontmatter completeness AND vocabulary correctness from a single canonical spec.
- `doc_type` taxonomy is explicit; reviewer can dispatch type-specific checks (per-doc-type vocabulary, per-doc-type required fields, per-doc-type traceability rules).
- Per-doc-type vocabulary fixes the `complete` drift without forcing all artifacts into a 5-state model that doesn't apply to ungated artifacts.
- The user-token chain pattern (Change 2) is documented as an audit trail discipline rather than a per-doc-type quirk.

**Negative:**

- Existing artifacts under the prior spec are out-of-conformance until validator either ignores pre-implementation artifacts (per AC-FR-11-d) OR a one-time migration is performed. Per IC scope declaration, historical archives are NOT migrated. The validator's enforcement is scoped to post-implementation date forward.
- Adds 3 new required fields (`gate_passed`, `approved_at`, `reviewer_verdict`) for gated artifacts. Authoring agents need updates to set these reliably. The orchestrator's state-transition hook (FR-5) is the natural enforcement point — it sets all three at gate-pass time.

**Forward implications:**

- The `shared-conventions.md` edits documented here are spec-level decisions. The actual file changes happen as Plan + Execution tasks (executed by `execute-task-code-producer` in a follow-on feature run). This ADR documents the decision; downstream tasks apply it.
- The frontmatter validator (FR-6 / `validate_pipeline_frontmatter.py`) implements the validation per the per-doc-type vocabulary and required-field schemas defined here.
- The `doc_type` field is the dispatch key for type-specific checks in `shared-document-reviewer` (per-doc-type vocabulary lookup, per-doc-type required-field set, per-doc-type traceability rules).
- Templates in `KB-documentation-criteria/references/templates/` need updates to set `doc_type` in their default frontmatter; this is in scope for the FR-7 implementation tasks.
- `shared-document-reviewer.md` agent definition needs updates to consume `doc_type` for dispatched checks; this is in scope for the FR-9 doc_type-taxonomy-extension tasks (per cc-design.md D-9 second role).

**Risk of over-application:**

- Authors may misclassify edge-case artifacts (e.g., is `architecture-audit-issues.json` an analysis/log or gated artifact?). The decision: any artifact that the pipeline produces and that does NOT pass a user-approval gate is analysis/log. Architecture-audit-issues fits analysis/log (no user gate on the audit results themselves; the user gate is on the Blueprint that the audit informs).

## Alternatives considered

**Alternative 1: Keep the 5-state vocab universal; migrate codebase-analysis.md and synthesis.md to use `accepted` for their final state.** Rejected: `accepted` implies gate passage; analysis/log artifacts don't pass gates. Forcing them into `accepted` would semantically muddle gate-passage semantics and create downstream confusion (e.g., "what gate did this synthesis pass?").

**Alternative 2: Make all 4 archive-practice fields optional rather than required for gated artifacts.** Rejected: optional fields are inconsistently set in practice; making them required exposes mistakes to the validator immediately. The cost of setting 3 required fields is small — the orchestrator's state-transition hook (FR-5) sets all three at gate-pass time automatically.

**Alternative 3: Defer the convention canonicalization to a follow-on feature, just observing drift now in this one.** Rejected: deferring perpetuates the drift; the discipline-5 mechanical-enforcement (D-15) and FR-6 (frontmatter validator) cannot operate without a canonical spec to validate against. ADR-0032 is the substrate prerequisite for both.

**Alternative 4: Add `doc_type` to spec but keep the 5-state vocab universal; per-doc-type vocabulary checks handled by reviewer dispatch logic alone.** Rejected: the vocabulary is a structural property of the artifact, not a dispatch rule. Encoding it in spec makes the canonical statement legible to authors and tools alike; pushing it into reviewer dispatch logic hides the rule and makes it harder to evolve.

**Alternative 5: Fold the PRD v1.1.0 ADR-0017 vs ADR-0021 mis-credit cleanup into this ADR as a third category.** Available alternative for ADR-0034 disposition (per cc-design Open items). Decision deferred to ADR-0034's authoring in Blueprint Batch 4: if ADR-0034 turns out lightweight enough to fold, this ADR-0032 can absorb it as a fifth change (Section 5 "PRD v1.1.0 narrative housekeeping"). If ADR-0034 needs separate framing (e.g., to explicitly correct the prior PRD's prose), it stands alone.

## Notes

This ADR pairs synthesis-stage decisions **D-4** (4 archive-practice fields canonicalization) and **D-18** (per-doc-type state vocabulary), and additionally subsumes the `doc_type` taxonomy gap from **IN-005** (third observed instance closes systematically here per discipline-5 mechanical-enforcement substrate). The pairing is justified by the joint dispatch-key nature of `doc_type` + per-type vocabulary: separating them across ADRs would force a forward reference one direction.

The ADR documents the decision; the actual `shared-conventions.md` edits and template-default-frontmatter updates are Plan-and-Execution-stage tasks. This Blueprint's `derived_from` includes `shared-conventions.md` v1 to anchor the "before" state; the post-edit spec (`shared-conventions.md` v2) is the canonical target.

The archive-authoritative spec direction (codifying validated practice into spec, rather than retrofitting practice to legacy spec) is consistent with ADR-0005's append-only supersession discipline applied at the spec level: the v1 spec is preserved (via git history), the v2 spec supersedes, and the practice that motivated the change is documented in this ADR as the validation evidence.
