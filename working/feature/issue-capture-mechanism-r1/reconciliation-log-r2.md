# Reconciliation Log — issue-capture-mechanism-r1 — Cycle 2

**Date**: 2026-05-23T23:55:00Z
**Issues inputs**: `working/feature/issue-capture-mechanism-r1/architecture-audit-issues.json`
**Cycle**: 2 of 4 (cap per ADR-0017)
**Trigger**: `review-architecture-auditor` returned `conditional_pass` on `blueprint-v2.md` with 2 MAJOR + 3 MINOR + 5 INFO findings. No BLOCKER. Per severity rules, MAJOR-without-BLOCKER → conditional_pass, finalize-reconciler dispatches revisions unless an issue warrants user escalation.

## Summary

- Total issues triaged this cycle: 10 (2 MAJOR + 3 MINOR + 5 INFO)
- New issues this cycle: 10 (auditor's first pass on blueprint-v2; previous cycle was a reviewer pass on v1, distinct issue family with `DR-BP` prefix)
- Persistent issues (carried from prior cycles): 0 strict-persistence; 1 incomplete-propagation (see Convergence Assessment)
- Issues dispatched for re-authoring: 4 (I-AA-002, I-AA-003, I-AA-004, I-AA-005)
- Issues escalated to user: 1 (I-AA-001 — ADR placement drift)
- Issues deferred to acceptance: 5 (all 5 INFO findings — audit-positive observations, no action needed)

All re-author dispatches target a single sub-agent (`design-composer`). One dispatch consolidates the four findings into a single re-authoring brief; sub-edits are localized and mechanical.

## Issue dispositions

### Categorization table

| Issue ID | Severity | Category | Disposition |
|---|---|---|---|
| I-AA-001 | MAJOR | ADR placement drift vs ADR-0036 (scope-of-this-run question) | USER ESCALATION |
| I-AA-002 | MAJOR | Cross-section inconsistency: ADR-0044 vs Blueprint Backend Design (evidence/updates validator exclusion not implemented) | Re-author dispatch → `design-composer` |
| I-AA-003 | MINOR | Internal Blueprint inconsistency: Interface Change Matrix "or"-wording stale | Re-author dispatch → `design-composer` |
| I-AA-004 | MINOR | Internal ADR inconsistency: ADR-0047 frontmatter four-vs-five (incomplete propagation of cycle-1 fix into ADR-0047) | Re-author dispatch → `design-composer` (per FR-5, only design-composer authors ADRs) |
| I-AA-005 | MINOR | Citation inaccuracy: Blueprint line 294 cites AC-FR-11-c which does not exist in PRD | Re-author dispatch → `design-composer` |
| I-AA-006..I-AA-010 | INFO | Audit-positive observations; pre-existing template drift (I-AA-006 only) is out-of-scope per the auditor's own resolution | Defer to acceptance |

### Classification rationale

**I-AA-001 (MAJOR) — USER ESCALATION.** The Blueprint places the 7 new ADRs (ADR-0044..0050) at `working/feature/<slug>/adrs/` per the still-current operational convention. ADR-0036 (accepted, repo-root `/adrs/`) mandates `/adrs/` placement. The same drift is documented as a pipeline-wide issue in `Issues/adr-placement-rootcause/analysis.md`, an outside-pipeline analysis explicitly scoped as a separate future feature; the PRD's Won't-Have section excludes resolving this drift in this run.

This is not the reconciler's call to make. The auditor offered three resolution paths:
- (a) Move the 7 ADRs to repo-root `/adrs/` — clean brief-honor resolution but extends scope into the drift-remediation feature that is tracked separately.
- (b) Author a superseding ADR per ADR-0005 amending ADR-0036 to permit feature-scoped authoring during pipeline runs — requires design-composer to author a new ADR per FR-5, also extends scope.
- (c) User-disposition escalation — record the deviation explicitly in the Blueprint frontmatter (e.g., `user_token_for_adr_placement_deviation`) and revise the synthesis claim to align.

Surfacing to the user is mandatory because each option has different scope/cost trade-offs that the reconciler is not authorized to choose between. The user previously acknowledged this drift as a separate feature concern; whether this run accepts the drift with a frontmatter token, fixes it inline, or supersedes the inherited ADR is a user-judgment call.

**I-AA-002 (MAJOR) — RE-AUTHOR BACKEND DESIGN (via design-composer).** ADR-0044 §Decision §4 + §Implementation Guidance commit that files under `Issues/<topic>/evidence/` and `Issues/<topic>/updates/` are explicitly excluded from FR-7's validator extension. The Blueprint's Backend Design §Service/Module Layout, §Corrected Pseudocode Reference, and §Data Contract describe the validator extension WITHOUT this path-prefix skip mechanism. Empirically verified: `validate_pipeline_frontmatter.py` currently emits a `minor` finding on `agent-roster-impact-matrix.md`, and the same finding will persist post-FR-9 migration into `Issues/per-agent-design-evaluation-gap/evidence/` unless the validator gains an explicit skip. This is a genuine cross-section inconsistency — the new ADR commits to behavior the new Backend Design does not specify how to deliver.

The fix is mechanical: add a path-prefix skip either (a) in the outer dispatch at `validate_pipeline_frontmatter.py` lines 365-371 (early-return empty findings if path matches `Issues/<topic>/(evidence|updates)/`), or (b) in the unknown-category branch at lines 304-312 (skip rather than emit minor finding). The Blueprint must specify which mechanism the implementation will use. ~3-5 lines of pseudocode in Backend Design §Corrected Pseudocode + a one-line addition to the Service/Module Layout's algorithm sketch.

Dispatch target is `design-composer` because the change touches the Blueprint's Backend Design subsection (a cross-cutting authored artifact). The Blueprint owns the canonical specification; the layer-source `backend-design.md` is consistent with the Blueprint per the per-layer flow. Routing through design-composer ensures both Blueprint and (downstream) layer-source agreement.

**I-AA-003 (MINOR) — RE-AUTHOR BLUEPRINT (via design-composer).** Stale "or"-wording in Interface Change Matrix line 469 carries forward v1 phrasing after the Backend Design §Service/Module Layout explicitly chose one of the two options. Mechanical one-line edit, same artifact, same author as I-AA-002. Folding into the same dispatch.

**I-AA-004 (MINOR) — RE-AUTHOR ADR-0047 (via design-composer).** ADR-0047 frontmatter `applies_to` says "four project firsts" but Decision §5 says "five firsts". This is incomplete propagation of the cycle-1 I-DR-BP-001 fix: the Blueprint's `complexity_rationale` was updated to five, but ADR-0047 (authored alongside the cycle-1 fix) was not aligned. One-line frontmatter edit. Per FR-5, only `design-composer` authors or amends ADRs.

Note on the convergence-classification: this is NOT a strict-persistence (the same issue did not survive cycle 1 unchanged); it is an **incomplete propagation** where the cycle-1 fix was applied to the Blueprint but not to the new ADR that records the same audit trail. See Convergence Assessment below.

**I-AA-005 (MINOR) — RE-AUTHOR BLUEPRINT (via design-composer).** Blueprint line 294 cites `AC-FR-11-a/b/c`; PRD-v2 defines only `AC-FR-11-a` and `AC-FR-11-b`. Two correction paths exist: (i) drop the spurious `/c` from the citation; (ii) expand PRD's FR-11 to define an AC-FR-11-c. Path (ii) requires reopening the PRD after Gate 2 approval, which is out-of-scope per the supersession discipline. Path (i) is the right call — one-character fix. Mechanical, same artifact as I-AA-002 / I-AA-003.

**I-AA-006..I-AA-010 (INFO × 5) — DEFER TO ACCEPTANCE.**
- I-AA-006: Blueprint frontmatter omits `doc_type`. Pre-existing template drift; the canonical blueprint-template.md itself omits `doc_type`. Auditor's own resolution explicitly scopes this for a future templates-consolidation run. Defer.
- I-AA-007: F-003 BLOCKER mitigation verified rigorous. No action.
- I-AA-008: Pipeline-isolation invariant verified at zero-baseline at audit time. No action.
- I-AA-009: All 14 synthesis decision frames (D-01..D-14) addressed. No action.
- I-AA-010: All Q-CC-1..5 + Q-BE-1..5 open items have explicit dispositions. No action.

### Re-author dispatch: `design-composer`

**Issues consolidated**: I-AA-002 (MAJOR), I-AA-003 (MINOR), I-AA-004 (MINOR), I-AA-005 (MINOR).

**Why a single consolidated dispatch**: all four findings target artifacts the design-composer owns (Blueprint v2 cross-cutting sections + ADR-0047 frontmatter, all already authored by design-composer per FR-5). All four edits are mechanical and localized; no design judgment required. Bundling avoids artifact-version churn.

**Re-authoring brief (high-level — full text in dispatch JSON):**

1. **MUST — I-AA-002 Backend Design evidence/updates exclusion mechanism.** Amend Blueprint §Backend Design §Service/Module Layout (around line 856) and §Corrected Pseudocode Reference (lines 887-921) to specify the path-prefix skip mechanism for `Issues/<topic>/(evidence|updates)/`. Recommended approach: extend the outer dispatch in `validate_pipeline_frontmatter.py` (around lines 365-371) with an early-return for paths matching the skip pattern, before reaching `validate_pipeline_artifact`. Also add a one-line entry to §Data Contract or Field Propagation Map noting the skipped path family. The Blueprint's claim that ADR-0044 is fully implemented by FR-7 must become true after this fix.

2. **MUST — I-AA-003 Interface Change Matrix "or"-wording.** Replace the stale "or"-phrasing at line 469 with the single chosen mechanism: "extends `doc_type_category` (lines 147-154) to return 'issue' when doc_type ∈ ISSUE_DOC_TYPES; adds an `elif category == 'issue'` branch inside `validate_pipeline_artifact`." Removes the false-options ambiguity.

3. **MUST — I-AA-004 ADR-0047 frontmatter four-vs-five.** Amend `ADR-0047-three-layer-enforcement.md` frontmatter line 14 (`applies_to`) to enumerate five firsts, adding "first 5-state lifecycle vocabulary distinct from ADR-0008's 4-state intra-pipeline ledger and ADR-0032's 3-tier per-doc-type vocabulary". This aligns the frontmatter with the ADR's own Decision §5 enumeration and with the Blueprint's `complexity_rationale` (cycle-1 fix).

4. **MUST — I-AA-005 AC-FR-11-c citation.** Replace `AC-FR-11-a/b/c` at Blueprint line 294 with `AC-FR-11-a/b`. One-character drop.

**Sequencing**: single dispatch; no ordering constraints between the four edits. All edits land in `blueprint-v3.md` (Blueprint version bump v2.x → v3.0 or v2.1 at composer's discretion per supersession discipline) plus an in-place amendment to `ADR-0047-three-layer-enforcement.md` (ADR is editable in-place during the design phase per FR-5; if the ADR is already considered "accepted", a superseding ADR is required, but typical convention for in-cycle amendments is in-place).

**Out-of-scope for this dispatch**:
- I-AA-001 (handled via user escalation channel; do NOT pre-empt the user's choice).
- I-AA-006 doc_type frontmatter (out-of-scope per the auditor's own resolution).

### User escalations

**I-AA-001 — ADR placement drift vs ADR-0036.**

- **Issue summary**: 7 new ADRs (ADR-0044..0050) placed at `working/feature/<slug>/adrs/` contradicting ADR-0036 which mandates `/adrs/` at repo root. Same drift is acknowledged as a pipeline-wide issue tracked separately in `Issues/adr-placement-rootcause/analysis.md`. PRD's Won't-Have section excludes resolving this drift in this run.
- **Severity**: MAJOR (per auditor classification).
- **Why this needs user judgment**: choosing among the three resolution paths is a scope-trade-off question (resolve the drift here vs maintain the boundary of this feature's intent), not an artifact-quality question. The reconciler cannot decide whether resolving the drift inline expands scope beyond the user's Gate-2 intent approval.
- **Recommended options to surface**:
  - **Option A — accept the drift with explicit user-token**: leave the 7 ADRs where they are; add a `user_token_for_adr_placement_deviation: "<token>"` field to the Blueprint frontmatter, with a one-paragraph rationale in §References explaining the deviation references the separate drift-remediation feature. Lowest scope-impact; preserves the Won't-Have boundary.
  - **Option B — move the 7 ADRs to `/adrs/`**: clean brief-honor resolution. Requires updating cross-references in Blueprint, synthesis, and any layer doc that points to the working-feature ADR paths. Moderate scope-impact; partially pre-empts the drift-remediation feature.
  - **Option C — author a superseding ADR amending ADR-0036**: design-composer authors a new ADR per ADR-0005 explicitly permitting feature-scoped authoring during pipeline runs (with deliverable-packager canonicalizing later). Highest scope-impact; pre-empts the drift-remediation feature entirely.
- **Trade-off summary**: Option A is the lowest-cost path that respects the Won't-Have boundary but leaves a documented inconsistency between the Blueprint and ADR-0036. Option B is clean but partially absorbs work assigned to the separate feature. Option C is the most architecturally satisfying but unilaterally absorbs the drift-remediation feature into this run.

### Acceptance deferrals

| Issue ID | Severity | Rationale |
|---|---|---|
| I-AA-006 | INFO | Pre-existing template drift; canonical `blueprint-template.md` itself omits `doc_type`. Auditor's own resolution scopes this for a future templates-consolidation run. |
| I-AA-007 | INFO | Audit-positive observation (F-003 mitigation rigorous). No action required. |
| I-AA-008 | INFO | Audit-positive observation (pipeline-isolation invariant verified at zero-baseline). No action required. |
| I-AA-009 | INFO | Audit-positive observation (14/14 decision frames addressed). No action required. |
| I-AA-010 | INFO | Audit-positive observation (10/10 Q-CC/Q-BE items dispositioned). No action required. |

## Convergence assessment

- **Convergence verdict**: **converging**. Cycle 1 surfaced 10 reviewer findings (2 important + 8 recommended); cycle 1's dispatch consolidated to a single design-composer invocation and produced `blueprint-v2.md`. The auditor's cycle-2 pass on v2 returned zero BLOCKER, two MAJOR, three MINOR — a substantively narrower issue set. No strict-persistence: none of the cycle-1 reviewer issues (I-DR-BP-001..010) re-surfaced verbatim.
- **Incomplete-propagation observation (not strict persistence)**: I-AA-004 is the auditor catching that the cycle-1 fix for I-DR-BP-001 (Blueprint `complexity_rationale` four→five) was applied to the Blueprint but not propagated into ADR-0047's `applies_to` frontmatter. This is mechanical drift, not a substantive recurrence; the cycle-2 dispatch resolves it. Flagged here so the next cycle (if needed) can verify the propagation actually landed in ADR-0047.
- **Divergence indicators**: none. The cycle-2 issue set is bounded (two MAJOR are localized to specific lines / one frontmatter edit / one cross-section gap), and the user-escalation issue (I-AA-001) is a pre-known scope question, not a new architectural problem surfaced by the audit.
- **Recommended next-cycle posture**: **regular**. After design-composer produces `blueprint-v3.md` + amended ADR-0047, re-invoke `review-architecture-auditor` for a scoped pass on the four addressed findings. Expect convergence (`pass` verdict) in cycle 3 contingent on the I-AA-001 user-escalation resolution being applied in the same cycle. If the user chooses Option B or C for I-AA-001 (any path that requires design-composer artifact changes), bundle it into the same cycle-2 dispatch retroactively; if the user chooses Option A (frontmatter token only), the design-composer can apply it as part of the consolidated dispatch.

## Cycle-cap posture

- Current cycle: 2 of 4. Well within cap (ADR-0017's 4-cycle hard cap).
- No structural-change recommendation needed.
- No terminal-cycle handling needed.

## Audit trail

- Cycle 1 log: `working/feature/issue-capture-mechanism-r1/reconciliation-log-r1.md`
- Cycle 1 dispatch JSON: `working/feature/issue-capture-mechanism-r1/dispatch-r1.json`
- Cycle 2 dispatch JSON: `working/feature/issue-capture-mechanism-r1/dispatch-r2.json`
- Upstream artifact this cycle: `working/feature/issue-capture-mechanism-r1/blueprint-v2.md` + `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044..0050`
- Auditor verdict source: `working/feature/issue-capture-mechanism-r1/architecture-audit-issues.json`
- Outside-pipeline scope reference for I-AA-001: `Issues/adr-placement-rootcause/analysis.md`
