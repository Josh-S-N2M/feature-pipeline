# PASS Criteria — Synthetic Test Feature T6

This document defines the end-to-end acceptance criteria that T6.3 (executed in the next session) must validate to declare the ADR-0044 dispatch repair verified.

## File Existence Checks

| File | Required | Notes |
|---|---|---|
| `working/feature/synthetic-test-feature-T6/state-transitions.log` | YES | Created by execute-orchestrator during task dispatch |
| `working/feature/synthetic-test-feature-T6/checkpoint.json` | YES | Created/updated at T4 phase boundaries |
| `working/feature/synthetic-test-feature-T6/test-fixture.txt` | YES | Modified by TS.1 and TS.2 |

## state-transitions.log Criteria

The log must contain **at least 4 entries** covering:

1. `TS.1` transition: `pending` → `per_task_active` (T1 boundary — TS.1 dispatched to execute-task-code-producer)
2. `TS.1` transition: `per_task_active` → `quality_active` (T2 boundary — TS.1 dispatched to execute-task-quality-handler)
3. `TS.2` transition: `pending` → `per_task_active` (T1 boundary — TS.2 dispatched to execute-task-code-producer)
4. `TS.2` transition: `per_task_active` → `quality_active` (T2 boundary — TS.2 dispatched to execute-task-quality-handler)

**All entries** must include `invoking_agent: "execute-orchestrator"` — this is the logical-owner invariant per ADR-0044 (the execute-orchestrator is the single point of dispatch; specialist agents do not re-dispatch laterally).

## checkpoint.json Criteria

- `execution_mode` field must equal `"specialist-dispatch"`
- `execution_pipeline_cycle_counters` must show **0 revision cycles** for both TS.1 and TS.2 (a clean first-pass run)
- Phase 1 must appear as complete in the phase-tracking structure

## test-fixture.txt Post-Task Content

After TS.1 and TS.2 complete, `test-fixture.txt` must contain:

- **1 appended marker line** below the `markers:` line (added by TS.1), containing a timestamp or run identifier
- **`counter: 1`** (incremented from the initial `counter: 0` by TS.2)

Exact format of the marker line is at TS.1's discretion, but it must be non-empty and identifiable as a TS.1 artifact.

## Session Boundary Criterion

The session that ran TS.1 and TS.2 must be **different** from the session that authored these files (the T6.1 session). Verify via:

- Operator confirmation that a session restart occurred per T6.2 before invoking tasks.json
- Or: compare process IDs / session identifiers in state-transitions.log timestamps vs. T6.1 artifact timestamps

This criterion is the F-7 fresh-session guarantee: the dispatch mechanism must initialise from scratch, not inherit in-memory state from the authoring session.

## execute-phase-quality-reviewer Criterion

At Phase 1 exit, the execute-phase-quality-reviewer must have been invoked and must have emitted a phase-exit entry in state-transitions.log (or an equivalent phase-complete artifact). This confirms the full dispatch loop — producer → quality-handler → phase-reviewer — completed without short-circuiting.

## FAIL Conditions

A run FAILS if any of the following are true:

- `state-transitions.log` is absent or has fewer than 4 entries
- Any entry lacks `invoking_agent: "execute-orchestrator"`
- `checkpoint.json` is absent or records non-zero revision cycles (indicates a NEEDS_REVISION loop fired, which is unexpected for this trivial workload)
- `test-fixture.txt` counter is not 1 or the marker line is absent
- T6.3 was run in the same session as T6.1 (violates F-7)

On FAIL: surface the specific criterion that failed; consult the rollback path in README.md.
