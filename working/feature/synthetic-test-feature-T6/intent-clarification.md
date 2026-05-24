---
id: IC-synthetic-test-feature-T6
doc_type: intent-clarification
scope_class: PATCH
feature_slug: synthetic-test-feature-T6
purpose: regression-test for execute-orchestrator-dispatch-mechanism-repair-r1 (Plan T6.1/T6.3)
user_token: synthetic-test-pre-ratified
generated: 2026-05-24
generated_by: execute-task-code-producer (T6.1)
---

## Purpose

This feature is a self-contained regression test for the repaired ADR-0044 flatten-dispatch loop implemented in `execute-orchestrator-dispatch-mechanism-repair-r1`. It exercises the full execute-orchestrator dispatch cycle end-to-end in a fresh session, providing load-bearing verification that the repaired mechanism works correctly before Phase 6 is declared complete.

## Shape

The feature comprises **1 phase, 2 tasks** (TS.1 and TS.2), both targeting a sacrificial `test-fixture.txt` file. This minimal shape is intentional: the goal is to exercise the dispatch loop (parent → execute-task-code-producer → execute-task-quality-handler per task → execute-phase-quality-reviewer at phase exit) without authoring new sub-agents or introducing scope that would require an additional session boundary.

- **TS.1** appends a timestamped marker line to `test-fixture.txt`
- **TS.2** increments the counter in `test-fixture.txt` and verifies TS.1's state-transitions.log entry exists

## PASS Criteria

A run is considered PASSING when all of the following hold:

1. `state-transitions.log` exists at `working/feature/synthetic-test-feature-T6/state-transitions.log`
2. The log contains at least 4 entries covering the T1/T2 state transitions for both TS.1 and TS.2
3. All log entries carry `invoking_agent: "execute-orchestrator"` (the logical-owner invariant per ADR-0044)
4. `checkpoint.json` exists with `execution_pipeline_cycle_counters` showing 0 revision cycles (clean run)
5. `checkpoint.json` records `execution_mode: "specialist-dispatch"`
6. `test-fixture.txt` contains 1 appended marker line and `counter: 1`

## F-7 Fresh-Session Prerequisite

Per the F-7 constraint, this tasks.json **must be invoked in a fresh session** after the session that authored these files (T6.2 session restart). Running TS.1 and TS.2 in the same session that authored this directory would defeat the purpose of the regression test: the fresh-session requirement ensures the dispatch mechanism initialises from scratch and produces its own checkpoint and state-transitions artifacts.
