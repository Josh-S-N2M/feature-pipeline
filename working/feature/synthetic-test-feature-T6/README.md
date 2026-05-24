# Synthetic Test Feature T6

## What This Is

A regression test for the **ADR-0044 flatten-dispatch repair** (`execute-orchestrator-dispatch-mechanism-repair-r1`). It is a self-contained, minimal 1-phase / 2-task feature whose sole purpose is to exercise the repaired execute-orchestrator dispatch loop end-to-end in a fresh session.

The two tasks (TS.1 and TS.2) make small edits to `test-fixture.txt`. The real verification target is the pipeline machinery: do state-transitions.log entries appear, do checkpoint.json cycle counters increment correctly, and does `invoking_agent: "execute-orchestrator"` appear on every dispatch boundary?

This feature is part of the Phase 6 verification sequence for the dispatch-repair feature. It was authored in the T6.1 session and must be *executed* in a subsequent fresh session (T6.3).

## Prerequisites

1. **Session restart (T6.2):** Do NOT run these tasks in the same session that authored this directory. A session boundary must separate authoring from execution (the F-7 fresh-session constraint). The next session after T6.1 is the correct session.
2. **Repo state:** The dispatch-repair implementation (Phase 1–5 tasks of `execute-orchestrator-dispatch-mechanism-repair-r1`) must already be applied.

## How to Invoke

### Option A — pipeline resume command

In the fresh session (post T6.2 restart):

```
/feature-pipeline --resume synthetic-test-feature-T6
```

The orchestrator will read `tasks.json`, dispatch TS.1 to execute-task-code-producer, then dispatch TS.2 after TS.1 quality-handler completes, then invoke execute-phase-quality-reviewer at Phase 1 exit.

### Option B — direct execution loop (manual verification)

If the resume command is unavailable, drive the loop manually:

1. Invoke `execute-task-code-producer` with task spec `TS.1` from `tasks.json`
2. Invoke `execute-task-quality-handler` for `TS.1`
3. Invoke `execute-task-code-producer` with task spec `TS.2` from `tasks.json`
4. Invoke `execute-task-quality-handler` for `TS.2`
5. Invoke `execute-phase-quality-reviewer` for Phase 1

## Where to Find the PASS Criteria

See `PASS-criteria.md` in this directory. Key checks:

- `state-transitions.log` exists with 4+ entries, all carrying `invoking_agent: "execute-orchestrator"`
- `checkpoint.json` records `execution_mode: "specialist-dispatch"` and 0 revision cycles
- `test-fixture.txt` has `counter: 1` and 1 appended marker line

## Verification Artifacts

After a successful T6.3 run, the following artifacts will exist in this directory:

| Artifact | Created by |
|---|---|
| `state-transitions.log` | execute-orchestrator (dispatch loop) |
| `checkpoint.json` | execute-orchestrator (T4 phase boundaries) |
| `test-fixture.txt` (modified) | TS.1 and TS.2 via execute-task-code-producer |
| `per-task-execution-result.json` (TS.1) | execute-task-code-producer |
| `per-task-execution-result.json` (TS.2) | execute-task-code-producer |

T6.4 (next session after T6.3) will author a `T6-verification-report.md` summarising the results against PASS-criteria.md.

## What to Do If It Fails

1. Identify which PASS criterion failed (see `PASS-criteria.md` FAIL Conditions section).
2. If `invoking_agent` is wrong or absent: the ADR-0044 logical-owner invariant was not applied correctly in the dispatch repair. Review `execute-orchestrator`'s state-transition emit calls.
3. If `state-transitions.log` is absent: the dispatch repair did not wire the log-emit step. Review Phase 2 tasks of the repair feature.
4. If `checkpoint.json` has non-zero revision cycles: TS.1 or TS.2 produced an INCOMPLETE result unexpectedly. Check the per-task-execution-result files for details.
5. If `test-fixture.txt` is unmodified: the execute-task-code-producer was not dispatched or returned BLOCKED. Check for scope-deviation entries in per-task-execution-result.json.

**Rollback path:** The repair feature maintains a `rollback-baseline.txt` at `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/rollback-baseline.txt`. Revert to that baseline if the dispatch mechanism is in an unrecoverable state, then re-apply the repair from the beginning of the execute-orchestrator-dispatch-mechanism-repair-r1 plan.

## Session and Authoring Notes

- **Authored by:** execute-task-code-producer (T6.1 session)
- **Execution session:** T6.3 (requires fresh session post T6.2 restart)
- **Verification report:** T6.4 (next session after T6.3)
- **ADR reference:** ADR-0044 (flatten-execution-dispatch-hierarchy)
- **Feature reference:** `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/`
