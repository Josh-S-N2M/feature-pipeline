---
id: ADR-0017
version: 1.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (new ADR for blueprint v4)
supersedes: []
adrs_inherited:
  - ADR-0002 (critique-1 single-critic CoVe)
  - ADR-0003 (critique-2 CMC + diff-mode + convergence)
  - ADR-0008 (issue ledger per-feature)
  - ADR-0011 (canonical document skill)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0
---

# ADR-0017: document-reviewer integration — five invocation points + critic renames

## Status

Accepted — 2026-05-12

## Context

The user identified an existing pipeline sub-agent, `document-reviewer`, designed to detect contradictions and rule violations in technical documents with improvement suggestions. The provided template (uploaded as `document_reviewer_template.txt`) specifies:

- `doc_type` values: `PRD`, `ADR`, `UISpec`, `DesignDoc`
- Inputs: `mode` (composite recommended), `target` (path), optional `code_verification` JSON, optional `codebase_analysis` JSON with `focusAreas`
- Two-gate review: Gate 0 (structural existence) must pass before Gate 1 (quality assessment)
- Output: structured JSON verdict with severity (`critical` / `important` / `recommended`), category (`consistency` / `completeness` / `compliance` / `clarity` / `feasibility`), and decision (`approved` / `approved_with_conditions` / `needs_revision` / `rejected`)
- Built-in prior-context-resolution checking via `prior_context_check`
- Uses `TaskCreate`/`TaskUpdate`; does NOT have Agent tool (recursion-safe)

The reviewer's scope overlaps substantially with the existing critique stages but at a different angle: structural conformance + rule-based completeness vs. substantive architectural critique vs. cross-artifact consistency.

The user also requested renaming critics for intuitive naming: synth-critic-1 → reflects what it checks; synth-critic-2 → same.

The user requested five invocation points be evaluated. After analysis (prior turn), all five are appropriate.

## Decision

Integrate `document-reviewer` at five invocation points in the pipeline. Extend `doc_type` values to include `IntentClarification` and `Plan`. Rename critique sub-agents to reflect what they check. The full three-stage review chain operates as: document-reviewer (structural + rule conformance) → architecture-auditor (substantive architectural review) → cross-artifact-auditor (cross-document + cross-model + convergence).

## Decision Details

| Item | Content |
|---|---|
| Decision | document-reviewer runs at 5 explicit invocation points; doc_type extended to include IntentClarification and Plan; synth-critic-1 renamed synth-architecture-auditor; synth-critic-2 renamed synth-cross-artifact-auditor. |
| Why now | The pipeline gains new document artifacts (PRD, Intent Clarification doc, Plan) at v4; integrating document-reviewer at the right points before stage proliferation prevents retrofit. Critic names became actively misleading once document-reviewer entered the picture. |
| Why this | document-reviewer is purpose-built for template conformance and structural review (claim C-R3-0024 production reference: Microsoft Conductor parallel specialist reviewers feed substantive synthesis); architecture-auditor and cross-artifact-auditor handle distinct substantive concerns (claim C-R3-0026: STOA Council 3-stage system as production reference). Three stages compose without redundancy. |
| Known unknowns | Whether document-reviewer's existing `doc_type` taxonomy will absorb new types (IntentClarification, Plan) cleanly via template-conformance rules, or whether dedicated review logic per type is needed; whether the reviewer's iteration discipline (prior_context_check) will compose with the pipeline's 4-cycle fixed-point iteration from blueprint v3. |
| Kill criteria | If document-reviewer's verdict consistently disagrees with synth-architecture-auditor (i.e., reviewer approves what architecture-auditor flags as critical) for 3+ consecutive feature runs, the structural/substantive boundary is blurry and the integration design needs revisiting. |

## Rationale

The three review stages serve distinct purposes that compose:

(1) **document-reviewer (structural + rule conformance + completeness against codebase analysis):**
- Gate 0: required template sections present
- Gate 1: consistency within the document, rule compliance, completeness checks, feasibility check, dependency realizability via Grep/Glob against codebase, fact disposition completeness against codebase_analysis.focusAreas
- Output: verdict + structured issues + scores
- Operates per-document, can run on any of: IntentClarification, PRD, DesignDoc (blueprint), ADR, Plan, UISpec

(2) **synth-architecture-auditor (renamed from synth-critic-1, substantive architectural review):**
- Single-critic CoVe per ADR-0002 — verifies architectural decisions against synthesis claims
- Blast-radius analysis via GitNexus / codebase-memory-mcp (per ADR-0007 v2)
- Brief-honor verification per ADR-0009
- Operates on blueprint output

(3) **synth-cross-artifact-auditor (renamed from synth-critic-2, cross-artifact + cross-model + convergence):**
- CMC posture + diff-mode + convergence per ADR-0003 — verifies consistency across blueprint, plan, and tests
- Cross-model: typically opus override per ADR-0003
- Fixed-point iteration per blueprint v3 §3.7
- Operates on the integrated set of artifacts before Build Approval Gate

The renames clarify the boundary: "auditor" implies evidence-based stance, distinguishes from "reviewer" (document-reviewer's role) and from "validator" (synth-phase-validator's role).

Cross-stage composition is well-supported by production references (claim C-R3-0024 Microsoft Conductor; claim C-R3-0026 STOA Council).

## Options Considered

**Option 1: document-reviewer only at points 2 and 3 (PRD and Blueprint).** Match the reviewer template's description ("PROACTIVELY after PRD/Design Doc/work plan creation") narrowly — skip Intent Clarification doc and Plan.
- Pros: minimal extension to existing doc_type taxonomy; lower invocation count.
- Cons: leaves Intent Clarification and Plan documents unreviewed by structural-conformance discipline; relies on downstream stages (PRD generation reading unreviewed Intent doc; test generation reading unreviewed plan) to catch structural issues, which they're not designed for.

**Option 2: document-reviewer at all 5 points; do NOT rename critics.**
- Pros: full document review coverage; preserves existing critic names.
- Cons: critic names actively misleading once document-reviewer is in the picture — synth-critic-1 sounds like a duplicate of document-reviewer; new contributors will be confused about which to invoke when.

**Option 3 (Selected): document-reviewer at all 5 points (PRD, Blueprint, ADR per-write, Plan, Reconcile-produced versions); extend doc_type with IntentClarification and Plan; rename critics to architecture-auditor and cross-artifact-auditor.**
- Pros: full coverage; clear semantic boundaries between three review stages; matches production references (Microsoft Conductor, STOA Council); critic names tell you what they check.
- Cons: 5 invocation points increase review-stage budget per feature run; doc_type extension means document-reviewer template needs new content for IntentClarification and Plan types.

## Consequences

### Positive Consequences

- Every templated document the pipeline produces is reviewed for structural conformance before substantive critique runs against it.
- document-reviewer's Gate 0 catches structural errors cheaply (no expensive blast-radius queries) before architecture-auditor's substantive review begins.
- document-reviewer's prior_context_check mechanism integrates with the pipeline's iterative review pattern — when document-reviewer is re-invoked on a superseding version, it tracks resolution of prior issues.
- Three-stage review composes without redundancy: each stage has a distinct scope and outputs.
- Critic names (architecture-auditor, cross-artifact-auditor) tell contributors what each stage checks; reduces invocation confusion.
- Plan and Intent Clarification documents gain template-conformance enforcement they previously lacked.

### Negative Consequences

- Five invocation points add wall-clock overhead per feature run. Each invocation is a sub-agent call with its own context-window allocation. Mitigated by: document-reviewer's checks are fast structural ones (Gate 0 in particular); not every invocation requires full Gate 1 quality assessment if Gate 0 fails fast.
- doc_type extension (IntentClarification, Plan) requires document-reviewer template updates — adding template-conformance rules per new doc_type. This is content authoring (in documentation-criteria), not architectural change.
- Renaming critics requires updating cross-references in blueprint v3 artifacts (Critique-1 references → architecture-auditor references; Critique-2 references → cross-artifact-auditor references). Blueprint v4 supersedes v3 with the new names; no in-place edits to v3 per ADR-0005.
- The three-stage review chain at maximum depth (document-reviewer → architecture-auditor → cross-artifact-auditor, each with up to 4 iterations) creates a deep critique pipeline. Token/cost cost is real. Mitigated by Gate 0 fast-fail and per-stage early exit when verdicts converge.

### Neutral Consequences

- document-reviewer's existing JSON output format (verdict + scores + issues) is preserved; integrates with the issues-ledger from ADR-0008 by mapping reviewer issues into the ledger's lifecycle states (reviewer's `critical`/`important`/`recommended` maps to ledger severity).

## Architecture Impact

**Components that change:**
- Pipeline topology: document-reviewer invocation inserted at 5 points (see Implementation Guidance for exact placement).
- `document-reviewer` template: doc_type taxonomy extended with `IntentClarification` and `Plan` values; corresponding template-conformance rules added.
- `synth-critic-1` renamed to `synth-architecture-auditor` (skill `critique-1-knowledge` renamed `architecture-audit-knowledge`).
- `synth-critic-2` renamed to `synth-cross-artifact-auditor` (skill `critique-2-knowledge` renamed `cross-artifact-audit-knowledge`).
- `documentation-criteria` skill (per ADR-0011): extended with template-conformance rules for IntentClarification and Plan document types.

**New dependencies introduced:**
- document-reviewer's invocations depend on the corresponding stage outputs (Intent Clarification doc, PRD, individual ADRs, Blueprint, Plan, Reconciled artifacts).
- document-reviewer's `code_verification` input parameter (optional per template) is wired to upstream code-verification stages when those exist; left empty when not applicable.
- document-reviewer's `codebase_analysis` input parameter is wired to `synth-codebase-researcher`'s output (per ADR-0018).

**Architectural constraints added:**
- document-reviewer MUST run after each Intent Clarification doc, PRD, individual ADR write, Blueprint (5b composer output), Plan, and Reconcile-produced superseding version.
- document-reviewer's verdict feeds into the human gate for that stage (PRD Approval Gate, Blueprint Approval Gate, etc.) and into the issues-ledger.
- synth-architecture-auditor and synth-cross-artifact-auditor MUST run after document-reviewer's verdict is `approved` or `approved_with_conditions` (not before); they do not run if document-reviewer's verdict is `rejected` or `needs_revision` — reconcile runs first.

**Architectural constraints removed:**
- The names "synth-critic-1" and "synth-critic-2" no longer used in blueprint v4 or beyond.

## Implementation Guidance

### Five invocation points (canonical)

1. **After Intent Clarification doc** (between Stage 1 and Stage 1.5): document-reviewer invoked with `doc_type: IntentClarification`. Verdict feeds into Intent Confirmation Gate.

2. **After PRD generation** (between Stage 1.5 and Stage 2): document-reviewer invoked with `doc_type: PRD`. Verdict feeds into PRD Approval Gate (new per ADR-0012).

3. **After Blueprint composition** (between Stage 5b and Stage 6 — i.e., between synth-designer-composer's output and synth-architecture-auditor's review): document-reviewer invoked with `doc_type: DesignDoc`. Verdict feeds into Blueprint Approval Gate. document-reviewer's `codebase_analysis` parameter is populated from synth-codebase-researcher's output (per ADR-0018).

4. **After Plan production** (between Stage 7 and Stage 8): document-reviewer invoked with `doc_type: Plan`. Verdict feeds into the architecture-auditor's intermediate review for plan quality (the plan does NOT have its own approval gate; it flows to acceptance test generation after document-reviewer passes).

5. **After each individual ADR write** (during reconcile loops or at any stage that introduces an ADR): document-reviewer invoked with `doc_type: ADR` for each new ADR. Issues incorporated into the issues-ledger.

### Reviewer iteration discipline

When document-reviewer's verdict is `needs_revision` or `rejected`, synth-reconcile runs and produces a new version of the document. document-reviewer re-invoked on the new version with `prior_context_check` populated from the previous invocation's issues. Iteration cap: 4 cycles (matching the pipeline's broader fixed-point iteration discipline from blueprint v3 §3.7). After 4 cycles, escalate to Cycle-Cap Escalation Gate.

### Reviewer output → issues-ledger mapping

When document-reviewer surfaces issues:
- Severity mapping: `critical` → ledger severity `critical`; `important` → ledger severity `major`; `recommended` → ledger severity `minor`.
- Category mapping: preserved as-is in the ledger entry's `category` field.
- Issues entered with `current_state: open`; subsequent reviewer invocations with `prior_context_check` results may transition to `verifying` and `verified`.

### Critic rename implementation

- File rename: `.claude/agents/synth-critic-1.md` → `.claude/agents/synth-architecture-auditor.md`.
- Skill rename: `.claude/skills/critique-1-knowledge/SKILL.md` → `.claude/skills/architecture-audit-knowledge/SKILL.md` (and same for critique-2 → cross-artifact-audit).
- All inheritance references in blueprint v4 and forthcoming ADRs use the new names.
- Blueprint v3 (already written) is NOT edited per ADR-0005; v4 supersedes v3 with the new names.

## Related Information

- User-provided template: document_reviewer_template.txt (uploaded; canonical from this ADR forward, with doc_type extension).
- ADR-0011: `documentation-criteria` holds template-conformance rules for each doc_type.
- ADR-0002: synth-architecture-auditor still uses single-critic CoVe discipline (renamed, not redefined).
- ADR-0003: synth-cross-artifact-auditor still uses CMC + diff-mode + convergence discipline (renamed, not redefined).
- ADR-0008: issues-ledger receives document-reviewer issues.
- Claims C-R3-0024 (Microsoft Conductor) and C-R3-0026 (STOA Council): production references for multi-stage review composition.
