---
id: RECON-pipeline-quickwins-hardening-r1-r1
version: 1.0.0
status: dispatched
generated: 2026-05-26T03:30:00Z
generated_by: finalize-reconciler
cycle_number: 1
cap: 4
feature_slug: pipeline-quickwins-hardening-r1
audited_artifact: blueprint-v2.md
verdict_received: approved_with_conditions
---

# Reconciliation Log — pipeline-quickwins-hardening-r1 — Cycle 1

**Date**: 2026-05-26
**Issues inputs**: `working/feature/pipeline-quickwins-hardening-r1/architecture-audit-issues.json`
**Cycle**: 1 of 4 (cap per pipeline policy)
**Auditor verdict**: approved_with_conditions (0 critical, 3 important, 2 recommended)

## Summary

- Total issues triaged this cycle: 5
- New issues this cycle: 5 (this is the first reconciliation cycle for this feature's Blueprint family)
- Persistent issues (carried from prior cycles): 0
- Issues dispatched for re-authoring: 5 (all five ride in one consolidated `design-composer` dispatch)
- Issues escalated to user: 0
- Issues deferred to acceptance: 0

All five findings can be addressed in a single coherent Blueprint+ADR revision pass. None requires user judgment; none is low-enough severity to defer; all upstream artifacts in scope are owned by the same author (`design-composer`).

## Plain-English narrative

The architecture audit cleared the Blueprint with conditions, not a hard fail. The conditions split into three patterns:

**Pattern 1 — inherited prose error from ADR-0037 that the Blueprint and ADR-0058 picked up.** ADR-0037's prose claims the existing event-type vocabulary is `{primary_degraded, readiness_probe, structured_failure}`. That's wrong. The on-disk vocabulary is `{install_complete, readiness_probe, structured_failure}` per the OP-7 schema validator and per the records actually written by `postCreate.sh`. ADR-0037 says one thing; its own implementation does another. The Blueprint v2 trusted ADR-0037's prose and repeated the wrong trio in at least eight places; ADR-0058 then quoted Blueprint v2 and repeated it in three more. This is finding I-AA-001.

**Pattern 2 — same shape, different label.** ADR-0037's prose names the schema-validation rule as "OP-6". The implementation is OP-7. OP-6 actually audits credential redaction in the runtime log. Blueprint v2 and ADR-0058 both quote the wrong label. A plan author told to extend "OP-6" for `calibration_result` shape validation would edit the credential-redaction script. This is finding I-AA-002.

**Pattern 3 — blast-radius scope.** The Blueprint's FR-3 day-one false-positive analysis names only one ADR-0041 row (mcp-openapi-schema, row 71) as needing a `[DEPRECATED]` annotation. The auditor's targeted Read confirms ADR-0041 row 70 (Serena) also drifts — the row documents `uvx --from "git+..."` but `.mcp.json` runs the installed binary. The Blueprint's canonicalize+opaque-tokens algorithm will produce a finding on Serena's row 70 on day one. This is finding I-AA-003.

The two recommended findings are minor:

- I-AA-004: ADR-0057 says `execution_mode` is being introduced; in fact the field already exists in the SKILL.md prose and in the live checkpoint.json (currently nulled). The decision content is sound — ADR-0057 is canonicalizing a documented-but-aspirational field into a load-bearing one. The framing is wrong but the decision isn't.
- I-AA-005: a sequencing note for the Plan author. The Q-CS-1b "NEVER RUN" banner will appear on every operator's first post-merge rebuild because no `calibration_result` event exists yet. The plan should schedule an immediate post-merge workflow run to retire the banner.

### Key arbitration calls

**Call 1: ADR-0037 amendment — in scope or out.**

The feature's carve-out excludes broader systemic ADR remediation. ADR-0037's prose error (both Pattern 1 and Pattern 2) is pre-existing. Argument for keeping ADR-0037 out of scope: respect the carve-out. Argument for pulling ADR-0037 in: (a) this feature's entire rationale is preventing exactly this drift class; leaving the source of the drift uncorrected while fixing every downstream propagation is incoherent, (b) ADR-0058 cites ADR-0037 by name and inherits its trio claim, so amending one without the other leaves an interlocking inconsistency live, (c) the correction is a prose fix, not a decision change — well within "amendment" rather than "rework."

**Decision: pull ADR-0037 amendment into this feature's scope.** Amend in place — bump ADR-0037 from v1.0.1 to v1.0.2 with a `change_summary` noting "prose corrections: `primary_degraded` → `install_complete` in event-type triad; `OP-6 audit rule` → `OP-7 audit rule` for schema validation." This is the one architectural call this reconciliation makes; everything else is downstream label correction. The append-only supersession discipline (ADR-0005) admits prose-correction amendments without supersession when the decision content is unchanged — only the description of pre-existing state changes.

**Call 2: I-AA-001 reconciliation route — option (b)(i) acknowledge inline vs (b)(ii) correct everywhere.**

The auditor offered both. (b)(i) preserves the Blueprint's "faithful-to-ADR-0037-prose" wording and adds an inline acknowledgement. (b)(ii) corrects everywhere to match on-disk reality.

**Decision: route (b)(ii).** The Blueprint's entire mission is documentation-vs-realization drift prevention. The Blueprint should not perpetuate the very drift it is built to prevent. Correct the enumeration in Blueprint v2 (frontmatter `change_summary`, §Background and Context, §NFR-13 prose, §AC-X-2, Interface Change Matrix, Data Flow, State Transitions, References — Inherited ADRs), ADR-0058 (§Context, §Decision, §Rationale item 1), and ADR-0037 (the prose source). Add a single sentence in the Blueprint's §Background and Context (ADR-0037 row) acknowledging the ADR-0037 prose was corrected as part of this feature for exactly this reason.

**Call 3: I-AA-002 — same correction route applied to OP-6 → OP-7.**

Trivial label swap. Apply everywhere: Blueprint v2, ADR-0058, ADR-0037. The Implementation Guidance bullet in ADR-0058 that currently reads "OP-6 audit rule discipline applies: any record in mcp-events.jsonl whose event: field is calibration_result MUST conform to the canonical payload shape; ad-hoc fields are rejected" becomes "OP-7 audit rule discipline applies: ...". This is the one bullet where the wrong label would actually cause a Plan author to edit the wrong script, so this correction must land.

**Call 4: I-AA-003 — annotate row 70 vs amend row 70.**

The Blueprint's chosen pattern for the mcp-openapi-schema case is the annotation pattern: leave the row text intact, add a `[DEPRECATED INVOCATION FORM ...]` tag. The same pattern fits Serena row 70 with the same rationale (locality-of-truth; ADR-0005 hygiene; no supersession needed because the decision content stands; only the documented invocation form has moved on).

**Decision: annotate row 70.** Add a `[DEPRECATED INVOCATION FORM — actual installed via uv-tool; runtime invocation is `serena start-mcp-server` from PATH after `uv tool install`; see postCreate.sh:82 + .mcp.json:28-31]` to ADR-0041 row 70. Update Blueprint v2's FR-3 day-one false-positive analysis to enumerate both annotations (row 70 Serena + row 71 mcp-openapi-schema).

**Call 5 — required Plan-task surfaces.**

The architecture audit surfaced two Plan-author concerns that must be threaded into the Blueprint's Implementation Plan section before plan authoring:

- **Plan task A (from I-AA-001 part (a)):** extend `audit_op7_events_schema.py`'s `REQUIRED_FIELDS` dict to admit `calibration_result` with its canonical payload shape per ADR-0058. Without this extension every FR-4b event emission produces an OP-7 MAJOR finding (the script logs unknown event types as MAJOR by default).
- **Plan task B (from I-AA-005):** sequence an immediate post-merge `gh workflow run gitnexus-grammar-skip-calibration.yml` invocation as a Plan task, before any operator's first post-merge devcontainer rebuild. This writes the first `calibration_result` event and retires the Q-CS-1b "NEVER RUN" banner from operator experience.

Both belong in Blueprint §Implementation Plan as ordered tasks so the plan-author picks them up at Stage 9.

## Issue dispositions

### Re-author dispatches

#### Re-invoke `design-composer` (single consolidated dispatch)

All five findings consolidate into one revision pass because they all touch artifacts owned by `design-composer`: Blueprint v2, ADR-0058 (still draft per Gate 4 status), ADR-0037 (amendment to v1.0.2), and ADR-0041 (annotation to row 70).

Issues consolidated for this dispatch:
- I-AA-001 (important) — event-type triad correction across Blueprint + ADR-0058 + ADR-0037 source
- I-AA-002 (important) — OP-6 → OP-7 label correction across Blueprint + ADR-0058 + ADR-0037 source
- I-AA-003 (important) — ADR-0041 row 70 annotation + Blueprint FR-3 false-positive list expansion
- I-AA-004 (recommended) — ADR-0057 prose framing correction (Context section reword)
- I-AA-005 (recommended) — Blueprint §Implementation Plan new ordered task for post-merge workflow run

Re-authoring brief (verbatim copy in dispatch-r1.json `feedback_brief`):

```
Blueprint v2 → v2.1 revision pass. Five findings from architecture-audit-r1 (verdict approved_with_conditions). Plain-English summary of required edits below; full audit JSON at architecture-audit-issues.json for cross-reference.

EDIT SET 1 — event-type triad correction (I-AA-001)
Across Blueprint v2 and ADR-0058 and ADR-0037, the phrase "primary_degraded, readiness_probe, structured_failure" (in any order) must become "install_complete, readiness_probe, structured_failure". The on-disk vocabulary per audit_op7_events_schema.py REQUIRED_FIELDS dict and per postCreate.sh actual writes is install_complete (not primary_degraded). primary_degraded is a boolean sub-field of structured_failure, not a distinct event type. Specific locations in Blueprint v2: frontmatter change_summary; §Background and Context (ADR-0037 row); §NFR-13 prose; §AC-X-2; Interface Change Matrix (ADR-0037 row); §Data Flow; §State Transitions; §References — Inherited ADRs (ADR-0037 row). In ADR-0058: §Context line 43; §Decision line 56; §Rationale item 1. Add one sentence to Blueprint §Background and Context (ADR-0037 row) noting that ADR-0037's prose was corrected as part of this feature because the feature's entire mission is preventing exactly this kind of documentation-vs-realization drift.

EDIT SET 2 — OP-6 → OP-7 label correction (I-AA-002)
Across Blueprint v2 and ADR-0058 and ADR-0037, every instance of "OP-6 audit rule" (or "OP-6") used in the context of schema/vocabulary discipline must become "OP-7 audit rule" (or "OP-7"). OP-6 audits credential redaction in the runtime log; OP-7 validates event-type vocabulary and per-type required fields. Critical landing: ADR-0058 §Implementation Guidance final bullet currently reads "OP-6 audit rule discipline applies: any record in mcp-events.jsonl whose event: field is calibration_result MUST conform to the canonical payload shape; ad-hoc fields are rejected." Change to OP-7. A plan author following the wrong label would edit audit_op6_runtime_log_redaction.py instead of audit_op7_events_schema.py. Other Blueprint locations: §Background and Context (ADR-0037 row); §Architecture Overview block discussing closed-enum; §Interface Change Matrix (ADR-0037 → ADR-0058 row); §Data Representation Decision table. Other ADR-0058 locations: §Context line 43; §Why this in Decision Details; §Rationale item 1 (line 74); Options Considered Option 1 cons; §Consequences (line 119); §Implementation Guidance final bullet (already cited).

EDIT SET 3 — ADR-0037 amendment to v1.0.2 (in support of EDIT SETS 1 and 2)
This feature's scope expands by one tightly-bounded prose correction: amend ADR-0037 in place from v1.0.1 to v1.0.2 with change_summary "prose corrections: primary_degraded → install_complete in event-type triad; OP-6 audit rule → OP-7 audit rule for schema validation." The decision content of ADR-0037 is unchanged; only the description of pre-existing state moves to match the on-disk implementation. This is admitted under ADR-0005's append-only supersession discipline because no decision shifts. Specific ADR-0037 locations: §Architecture Impact item 4 line 136 (OP-6 → OP-7); and any prose enumerating the event-type triad as primary_degraded/readiness_probe/structured_failure (correct to install_complete/readiness_probe/structured_failure). Bump frontmatter version 1.0.1 → 1.0.2 and add the change_summary.

EDIT SET 4 — ADR-0041 row 70 annotation + Blueprint FR-3 false-positive list expansion (I-AA-003)
Currently Blueprint v2 §Background and Context (ADR-0041 row) cites only row 71 (mcp-openapi-schema) as the [DEPRECATED]-annotation target for FR-3 day-one false-positive avoidance. Row 70 (Serena) has the same shape of drift: row 70 documents `uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena start-mcp-server` but `.mcp.json` runs `command: "serena", args: ["start-mcp-server"]` (binary install from `uv tool install` per postCreate.sh:82). Two edits: (a) in adrs/ADR-0041-install-mechanism-hybrid.md, add an annotation to row 70 reading `[DEPRECATED INVOCATION FORM — actual installed via uv-tool; runtime invocation is `serena start-mcp-server` from PATH after `uv tool install`; see postCreate.sh:82 + .mcp.json:28-31]`. (b) in Blueprint v2 §Background and Context (ADR-0041 row), expand the deprecation-annotation list to enumerate both rows (row 70 Serena + row 71 mcp-openapi-schema). Update the Blueprint's FR-3 risk-table row "FR-3 false positives on .mcp.json shapes ADR-0041 didn't anticipate" mitigation to cite both annotations.

EDIT SET 5 — ADR-0057 §Context reword (I-AA-004)
In adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md §Context line 44, the sentence "there is no existing execution_mode field on checkpoint.json today" overclaims novelty. The field is documented in recipe-feature-pipeline/SKILL.md:138 and 412 and is present (currently nulled) in this feature's working checkpoint.json:106. Reword to: "The execution_mode field is documented in the orchestrator's checkpoint schema (recipe-feature-pipeline/SKILL.md:138) and is written by the orchestrator at Stage 1 (recipe-feature-pipeline/SKILL.md:412), but is not yet a load-bearing audit surface for downstream sub-agents; this ADR canonicalizes the field as the FR-2 dispatch-self-check inspection surface, fixing the closed-enum values, the writer, the reader, and the absence-default rule." Bump ADR-0057 patch version (e.g., 1.0.0 → 1.0.1) with change_summary "Context section reworded to accurately describe pre-existing state of execution_mode field per architecture-audit-r1 I-AA-004."

EDIT SET 6 — Blueprint §Implementation Plan two new ordered Plan tasks (from I-AA-001 part (a) and I-AA-005)
Add two ordered Plan tasks to Blueprint v2 §Implementation Plan (so the Stage 9 plan-author picks them up):

  Plan Task A (from I-AA-001): "Extend audit_op7_events_schema.py's REQUIRED_FIELDS dict to admit calibration_result with its canonical payload shape per ADR-0058. Without this extension every FR-4b event emission produces an OP-7 MAJOR finding because the script's default for unknown event types is MAJOR. Sequencing: this task must complete in the same PR as the FR-4b script and the new ADR-0058 record; OP-7 schema must learn the new vocabulary in lockstep with the first emission." This task is bundled into the single-PR D-0008 decision; no scope creep.

  Plan Task B (from I-AA-005): "Immediately post-merge, invoke `gh workflow run gitnexus-grammar-skip-calibration.yml` once to write the first calibration_result event to .claude/runtime/mcp-events.jsonl. This retires the Q-CS-1b 'NEVER RUN' banner before any operator's first post-merge devcontainer rebuild. Without this task, every operator sees the banner on first rebuild, which is correct behavior but undermines the banner's signal-to-noise (the banner is meant to flag long-stale calibration data, not first-deploy state)."

EDIT SET 7 — frontmatter and change_summary
Bump Blueprint v2 → v2.1 (patch bump; same blueprint family). frontmatter change_summary: "Architecture-audit-r1 reconciliation: event-type triad corrected install_complete (was primary_degraded across multiple sections; inherited from ADR-0037 prose error); OP-6 → OP-7 label corrected for schema-validation rule references; ADR-0041 row 70 (Serena) added to FR-3 day-one [DEPRECATED]-annotation list; ADR-0057 Context reworded to accurately describe pre-existing execution_mode field; two new ordered Plan tasks (OP-7 schema extension; immediate post-merge banner-retirement workflow run); supporting ADR-0037 v1.0.1 → v1.0.2 prose amendment in same PR."

Bump ADR-0058 frontmatter status remains "draft" (still pre-Gate-4); add change_summary "Pre-finalization reconciliation: event-type triad corrected (was inheriting ADR-0037 prose error); OP-6 → OP-7 label corrected for schema-validation rule references."

The above six edit sets plus the frontmatter bumps are the complete revision brief. No new architectural decisions are made in this reconciliation; only label/triad corrections plus two ordered Plan tasks plus one in-scope-by-necessity ADR-0037 amendment. After applying, the Blueprint v2.1 should re-enter shared-document-reviewer (Gate 0/1) and then re-enter architecture-audit (cycle 2) for verification that all five findings are resolved.
```

### User escalations

None this cycle. All five findings have clear, low-risk resolutions that fit the feature's mission. The one judgement call (pull ADR-0037 amendment into scope) is bounded enough — prose-only correction, no decision shift, append-only-discipline compliant — that the reconciler can make it without user escalation per the standing auto-mode posture.

### Acceptance deferrals

None this cycle. Two findings were recommended-severity but both have low-cost in-scope fixes (one prose reword in ADR-0057; one Plan task line); deferring would be more work than fixing.

## Convergence assessment

- Convergence verdict: **n/a (cycle 1)** — no prior reconciliation cycle exists for this Blueprint family.
- Persistent issues: none (cycle 1 baseline)
- Recommended next-cycle posture: **regular**. After `design-composer` produces Blueprint v2.1 + amended ADR-0037 + revised ADR-0058 + ADR-0057 + annotated ADR-0041, re-run shared-document-reviewer Gate 0/1 on the Blueprint, then re-invoke `review-architecture-auditor` for cycle 2 verification.

## Audit trail

- Cycle 1 log: this file (`working/feature/pipeline-quickwins-hardening-r1/reconciliation-log-r1.md`)
- Cycle 1 dispatch: `working/feature/pipeline-quickwins-hardening-r1/dispatch-r1.json`
- Cycle 1 input issues: `working/feature/pipeline-quickwins-hardening-r1/architecture-audit-issues.json`
- Cycle 2 log: not yet authored
- Cycle 3 log: not yet authored
- Cycle 4 log: not yet authored

## Post-conditions for orchestrator

1. Orchestrator dispatches `design-composer` per `dispatch-r1.json` order 1.
2. `design-composer` produces Blueprint v2.1 + ADR-0037 v1.0.2 + ADR-0058 (revised draft) + ADR-0057 v1.0.1 + ADR-0041 (row 70 annotation).
3. Orchestrator re-runs `shared-document-reviewer` (Gate 0/1) on Blueprint v2.1 and the four ADR products.
4. If Gate 0/1 passes, orchestrator re-runs `review-architecture-auditor` for cycle 2 with prior_context_check populated from this log.
5. If cycle 2 returns clean (no carry-over of I-AA-001..005), Blueprint family is finalized and Stage 9 (plan-author) is unblocked.
