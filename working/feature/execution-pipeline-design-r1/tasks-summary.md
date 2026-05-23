---
id: TasksSummary-execution-pipeline-design-r1
version: 1.0.0
status: draft
feature_slug: execution-pipeline-design-r1
doc_type: tasks-summary
derived_from:
  - working/feature/execution-pipeline-design-r1/tasks.json
generated: 2026-05-22T23:59:00Z
generated_by: finalize-task-decomposer (Claude Code subagent dispatch, authoritative)
agent_invocation_simulation: false
---

# Tasks Summary: Execution Pipeline Design (run r1)

Human-readable companion to `tasks.json`. Single-source-of-truth is the JSON; this summary is for reviewer comprehension at Gate 6.

## Top-Line Numbers

| Metric | Value |
|---|---|
| Plan v2 tasks consumed | 31 |
| DAG tasks after decomposition | 32 (T3.1 split into T3.1.1 + T3.1.2) |
| DAG edges | 76 |
| Phases | 7 (Phase 0 through Phase 6) |
| Phase Validators (PV-0 through PV-6) mapped | 7 |
| Acceptance Tests (AT-001 through AT-078) mapped | 78 |
| PRD ACs covered | 60 (all) |
| Operational ACs covered | 3 (all) |
| Orphan ACs | 0 |
| User-decision items for Gate 6 | 1 (T6.1 Posture A vs B) |

## DAG Visualization (textual)

```
PHASE 0 (Setup)
  T0.1 ──┬──> T0.2 ──> [Phase 4: T4.1] ──> [Phase 5: T5.*]
         ├──> T0.3 ──> [Phase 5: T5.*]
         ├──> T0.4 ──> [Phase 1: T1.1..T1.6] ──> T0.5 ──┐
         └──> T2.3 (skill install; AC-FR-9-e)            │
                                                         │
PHASE 1 (auditing-shared scripts)                        │
  T0.4+T0.5 ──> T1.1 ─┐                                  │
                T1.2 ─┤                                  │
                T1.3 ─┼─> T1.4 ─> T1.7 (Phase 1 gate)    │
                T1.5 ─┤    ▲                             │
                T1.6 ─┘    │                             │
                          T2.1 (cross-phase)             │
                                                         │
PHASE 2 (Skills)                                         │
  T0.1 ──> T2.1 ──┬──> T1.4 (back-arrow)                 │
            T2.3 ─┴──> T3.2, T3.3 (AC-FR-9-e)            │
            T1.6 ──> T2.2                                │
                                                         │
PHASE 3 (Agents) — 5 parallel after substrate            │
  T3.1.1 ──> T3.1.2                                      │
  T3.2 (binds ai-development-guide; NOT auditing-shared) │
  T3.3 (binds auditing-shared; UNRESTRICTED Bash)        │
  T3.4 (binds auditing-shared)                           │
  T3.5 (binds auditing-shared)                           │
                                                         │
PHASE 4 (Conventions + Existing-agent ext)               │
  T4.1 ──> T4.2                                          │
  T2.1 ──> T4.3                                          │
  T2.2 ──> T4.4                                          │
                                                         │
PHASE 5 (Templates) — 5 parallel                         │
  T0.3 + T4.1 ──> T5.1, T5.2, T5.3, T5.4, T5.5           │
                                                         │
PHASE 6 (Rollout)                                        │
  T6.1 (POSTURE A=defer/POSTURE B=execute) ◄── USER GATE 6
  T6.2 (smoke test) ◄────────────────────────────────────┘
```

## Critical Path

Two co-equal critical chains terminate at the integration test (T6.2):

1. **Conventions canonicalization chain**: `T0.1 → T0.2 → T4.1 (L) → T5.x → T6.2`
2. **AC-FR-9-e skill-install-before-binding chain**: `T0.1 → T0.2 (or T0.4 → T0.5) → T2.3 → T3.2/T3.3 → T6.2`

**Longest-effort path by accumulated estimates**: `T0.1 (XS) → T0.4 (S) → T0.5 (S) → T1.1 (L) → T1.4 (L) → T3.4 (L) → T6.2 (L)` — approximately **24-30 hours** of serial work along this chain alone.

## Effort Totals

Per Plan v2 estimation methodology (T-shirt sizes mapped to hours; XS<1, S=1-2, M=2-4, L=4-8, XL=8+):

| Phase | Tasks | XS | S | M | L | XL | Effort range (hours) |
|---|---|---|---|---|---|---|---|
| Phase 0 | 5 | 2 | 3 | 0 | 0 | 0 | 3-9 |
| Phase 1 | 7 | 1 | 1 | 3 | 2 | 0 | 17-31 |
| Phase 2 | 3 | 0 | 1 | 0 | 2 | 0 | 9-18 |
| Phase 3 | 6 | 0 | 0 | 4 | 2 | 0 | 16-32 |
| Phase 4 | 4 | 2 | 0 | 1 | 1 | 0 | 6-14 |
| Phase 5 | 5 | 0 | 3 | 2 | 0 | 0 | 7-14 |
| Phase 6 | 2 | 0 | 0 | 0 | 1 | 1* | 4-11 (Posture A); 6-14 (Posture B) |
| **Totals** | **32** | **5** | **8** | **10** | **8** | **1*** | **~62-129** |

*T6.1 is XL_or_zero depending on posture; Posture A = 0h, Posture B = ~2-3h.

Per Plan v2 estimation:
- **Serial total**: ~110-150 hours
- **With full parallelization (multiple Claude Code sessions)**: ~70-90 hours, limited by critical path

## Parallelism Opportunity Summary

Maximum parallel tasks within each phase (after their substrate predecessors land):

| Phase | Max parallel | Tasks that can run concurrently |
|---|---|---|
| Phase 0 | 3 | T0.2, T0.3, T0.4 (all post-T0.1) |
| Phase 1 | 5 | T1.1, T1.2, T1.3, T1.5, T1.6 (all post-T0.4+T0.5) |
| Phase 2 | 3 | T2.1, T2.2, T2.3 (post-substrate-fans-out) |
| Phase 3 | 5 | T3.1.1, T3.2, T3.3, T3.4, T3.5 (after Phase 2 lands) |
| Phase 4 | 3 | T4.2, T4.3, T4.4 (after T4.1 + T2.1 + T2.2 land) |
| Phase 5 | 5 | T5.1-T5.5 (after T0.3 + T4.1 land) |
| Phase 6 | 2 | T6.1, T6.2 (independent) |

**Cross-phase parallelism**: Phase 1 and Phase 2 partially overlap — most Phase 1 script-authoring tasks are independent of Phase 2, but T1.4 (the coordinator) requires T2.1 as an invocation target. T2.3 (ai-development-guide install) is parallel with all Phase 1 work.

## Posture Decisions Surfaced for Gate 6

### T6.1 Posture (USER DECISION REQUIRED)

The Plan v2 default is **Posture A (defer)**. Both postures are preserved in the DAG per ADR-0029 + ADR-0033 no-silent-absorption.

| Aspect | Posture A (default) | Posture B (alternative) |
|---|---|---|
| Action | Skip T6.1; record Scope-Deviation | Execute ~20+ planning-side agent edits |
| Effort | 0h | ~2-3h (XL) |
| Downstream impact | Next post-ratification feature run triggers validator failures at Gate 0 for those agents' artifacts | Clean state for next feature run |
| Verification | Scope-Deviation entry in Plan Update History + Open Items + T6.2 pipeline-run-summary.json | All ~20+ edits parse; validator passes; agents emit doc_type |

**Recommendation**: Surface the choice to the user at Gate 6 with the explicit downstream-impact note.

## Decomposer Concerns for Gate 6

| ID | Severity | Concern |
|---|---|---|
| DC-1 | MAJOR | T6.1 Posture A vs B is a user-decision blocker for Gate 6 |
| DC-2 | MINOR | T1.1 ↔ T4.1 forward dependency (staged authoring per Open Item #3); verify staging is sound |
| DC-3 | CRITICAL | Reconciliation budget exhausted (per Plan v2 Open Item #9); non-trivial Gate 6 findings require user escalation per ADR-0017 cap-exhaustion |
| DC-4 | INFO | T3.1 split into T3.1.1 + T3.1.2 is discretionary; reversible if user prefers single task |
| DC-5 | MINOR | Phase 1 ↔ Phase 2 cross-phase dependency (T1.4 needs T2.1); strict phase isolation violated for T1.4 — flagged in Plan v2 Cross-Phase Dependencies |
| DC-6 | MINOR | PV-0/PV-1/PV-2 bootstrapping: first three phase validators enforced before T3.4 exists; user-verified manually using phase-validators.md as checklist |

## Key Architectural Patterns Preserved in DAG

| Pattern | Where preserved |
|---|---|
| **AC-FR-9-e skill-install-before-binding** sequencing | T2.3 → T3.2 + T2.3 → T3.3 explicit edges |
| **ADR-0035 4-of-5 binding pattern** (auditing-shared) | T3.1.1, T3.3, T3.4, T3.5 (positive); T3.2 (negative-binding documented in task description and verified by AT-070) |
| **I-AA-602 unrestricted Bash on quality-handler** | T3.3 task description + complexity_drivers; verified by AT-067, AT-068 |
| **I-AA-608 orchestrator HAS Write** | T3.1.1 task description + verified by AT-076 |
| **I-AA-609 14-transition state machine** (12 substantive + 2 boundary) | T3.1.1 (orchestrator body) + T1.2 (log payload schema); verified by AT-077, AT-078 |
| **I-AA-604 AC correction-surface** (cite ADR-0017 forward, not ADR-0021) | T3.5 verifies AC-FR-6-e + AC-FR-10-b via AT-034, AT-072 |
| **ADR-0017 4-cycle cap (canonical home per ADR-0034)** | T3.5 (reconciler enforces); T0.2 (ratifies) |
| **ADR-0033 no-silent-scope-changes (execution extension)** | T3.5 scope-deviation dispatch; T5.1 per-task-result template Scope Deviations section; T6.1 Posture A surfacing |
| **ADR-0032 doc_type universal-required** | This file declares `doc_type: tasks-summary`; tasks.json declares `doc_type: tasks` |

## Open Items Inherited (Consolidated)

11 open items carried forward into tasks.json `open_items_for_orchestrator`:

- OI-1 through OI-9: from Plan v2 Open Items
- OI-AT-1: from Acceptance Tests (test implementation handling)
- OI-PV-1: from Phase Validators (bootstrapping consequence)

The full disposition for each is in `tasks.json`. The most consequential is **OI-9** (reconciliation budget exhausted) and **OI-5** (T6.1 Posture A vs B user decision) — both surface to user at Gate 6.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-22 | finalize-task-decomposer (Claude Code subagent dispatch, authoritative) | Initial summary companion to tasks.json v1.0.0. |
