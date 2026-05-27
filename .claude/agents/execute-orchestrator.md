---
name: execute-orchestrator
description: "Use when consulting the canonical state-machine reference for the execution-side dispatch loop. ADVISOR ONLY — non-invocable per ADR-0044. The parent recipe-feature-pipeline orchestrator (not this agent) directly dispatches the four execution-side specialists. This file documents the 12-substantive-state machine (plus 2 boundary states INIT/TERMINATED) that the parent orchestrator follows. Previously described as: invoke once per feature run after tasks.json is ratified, at the INIT → pending boundary transition; centralized owner of the execution-pipeline state machine; routes dispatch matrix outputs back to upstream agents; tracks per-task and phase-level cycle counters against ADR-0017's 4-cycle cap (symmetric application per D-12)."
model: opus
effort: high
tools: [Read, Glob, Grep, Write, Bash(python3:*)]
skills: [KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]
memory: project
---

# execute-orchestrator

> **Advisor role per ADR-0044.** This file is the canonical state-machine reference for the execution-phase dispatch loop. Under ADR-0044's flatten pattern (option (a)), the parent `recipe-feature-pipeline` orchestrator (not this agent) directly dispatches the 4 execution-side specialists. This file documents WHAT the state machine is; the parent skill at `.claude/skills/recipe-feature-pipeline/SKILL.md` §Execution Phase Dispatch documents HOW the parent dispatches. Treat references to "this agent" or "you" in the body below as historical / canonical-reference framing; the literal invocation belongs to the parent.

> **Note on the `skills:` self-reference to `recipe-feature-pipeline` (Q-CC-3 disposition).** This advisor file declares `recipe-feature-pipeline` in its `skills:` frontmatter array per the Q-CC-3 disposition ratified during design composition. Although the file is no longer invocable as a dispatcher (per ADR-0044), the skill self-reference is preserved because the advisor's state-machine narrative IS the operational contract that `recipe-feature-pipeline` §Execution Phase Dispatch realizes. The skill loaded ensures any future reader (or any future-reactivated dispatch path) sees the same canonical framing the recipe documents. The self-reference is **NOT** an invocation hint — it is a documentation-consistency anchor.

The **execution side** of the feature pipeline is governed by the state machine below. Execution starts when `tasks.json` and the deliverable archive from the design side are ready, and ends when the feature's execution work is complete (a verified phase-quality-report PASS for the final phase + a pipeline-run-summary committed).

Authoritative references:
- `working/feature/execution-pipeline-design-r1/blueprint-v5.md` — the design the parent orchestrator implements
- `working/feature/execution-pipeline-design-r1/plan-v2.md` — the implementation plan
- `working/feature/execution-pipeline-design-r1/acceptance-tests.md` — the 78 acceptance tests
- `working/feature/execution-pipeline-design-r1/phase-validators.md` — the 7 phase validators
- `.claude/skills/recipe-feature-pipeline/SKILL.md` — the 13-stage pipeline overview
- `adrs/ADR-0017-reconciliation-cap.md` — the 4-cycle cap
- `adrs/ADR-0033-adr-0029-execution-extension.md` — Scope-Deviation surfacing for execution-phase artifacts

## The 12-substantive-state machine (+ 2 boundary states)

| Transition | From | To | Trigger |
|---|---|---|---|
| T0 (boundary) | INIT | pending | execution-phase invocation; tasks.json + archive validated |
| T1 | pending | per_task_active | orchestrator dispatches code-producer for the next task |
| T2 | per_task_active | quality_active | code-producer returns COMPLETED |
| T3 | quality_active | per_task_approved | quality-handler returns APPROVED |
| T4 | quality_active | per_task_active | quality-handler returns NEEDS_REVISION (increments per-task cycle counter) |
| T5 | quality_active | escalated_stub | quality-handler returns STUB_DETECTED (D-2d) |
| T6 | per_task_approved | pending | next task in the DAG; back to T1 |
| T7 | per_task_approved | phase_quality_active | all tasks in current phase approved |
| T8 | phase_quality_active | phase_complete | phase-quality-reviewer returns PASS |
| T9 | phase_quality_active | phase_reconciliation | phase-quality-reviewer returns NEEDS_RECONCILIATION |
| T10 | phase_reconciliation | phase_quality_active | finalize-reconciler dispatches; re-runs phase quality (increments phase cycle counter) |
| T11 | phase_complete | pending | next phase begins; back to T1 |
| T12 | phase_complete | pipeline_complete | last phase complete; emit pipeline-run-summary |
| T13 (boundary) | any | TERMINATED | pipeline_complete OR user-escalation OR cycle-cap-exhaustion |

**Invariant 10 (scope clarified per I-AA-609)**: only T4 (per-task NEEDS_REVISION) and T10 (phase reconciliation cycle complete) increment cycle counters. T0/T13 boundary transitions are logged but do NOT increment.

## State-transition hook

For EVERY transition (including T0 and T13), the parent orchestrator MUST invoke:

```bash
echo '<contract-5-payload>' | python3 .claude/skills/auditing-shared/scripts/log_state_transition.py \
  --feature-slug <slug>
```

Hook failure is observer-only (D-16) — it does NOT block the substantive transition. A failure surfaces as a Level-1 finding per AC-FR-5-e.

## Per-task loop

For each task in the DAG, the parent orchestrator MUST:

1. Verify task dependencies are satisfied (all `dependencies:` entries are status APPROVED).
2. Dispatch `execute-task-code-producer` with the task spec (including any per-task-declared skills to load).
3. Receive `per-task-execution-result.json` from code-producer.
4. If status COMPLETED → dispatch `execute-task-quality-handler` (T2).
5. If status INCOMPLETE → the parent orchestrator decides retry strategy (within per-task cycle budget).
6. If status BLOCKED → escalate to user (T13).
7. quality-handler verdict APPROVED → mark task APPROVED, advance to next task (T3 → T6 → T1).
8. quality-handler verdict NEEDS_REVISION → re-dispatch code-producer with revision context (T4); increment per-task cycle counter.
9. quality-handler verdict STUB_DETECTED → T5 → escalate per D-2d.
10. quality-handler verdict BLOCKER → T5-equivalent → escalate.

**Per-task cycle cap**: 4 (symmetric per ADR-0017 ↔ D-12). Cycle 4 failure escalates to user per AC-FR-10-c.

## Per-phase loop

After all tasks in a phase reach APPROVED, the parent orchestrator MUST:

1. Dispatch `execute-phase-quality-reviewer` (T7).
2. Receive `phase-quality-report.json` per Contract 2 (5-dimensional verdict).
3. If verdict PASS → T8 → advance to next phase OR pipeline_complete.
4. If verdict NEEDS_RECONCILIATION → dispatch `execute-finalize-reconciler` (T9).
5. finalize-reconciler classifies findings + dispatches upstream agents; the parent orchestrator re-runs phase quality (T10); increment phase cycle counter.
6. Phase cycle cap: 4. Cycle 4 failure escalates to user per AC-FR-10-c.

## Outputs the parent orchestrator owns

- `working/feature/<slug>/state-transitions.log` — one JSONL line per transition (via the auditing-shared script).
- `working/feature/<slug>/pipeline-run-summary.json` — final summary written at T12.

## What the parent orchestrator does NOT do

- The parent orchestrator does NOT author code. That's code-producer.
- The parent orchestrator does NOT issue quality verdicts. That's quality-handler / phase-quality-reviewer.
- The parent orchestrator does NOT classify findings or dispatch reconciliation. That's finalize-reconciler.
- The parent orchestrator does NOT modify upstream design artifacts (Blueprint, Plan, PRD). Reconciliation-driven re-authoring goes through the planning-side agents via finalize-reconciler's dispatch.

## Contract obligations

The parent orchestrator consumes the 5 Blueprint contracts and emits per them:
- Contract 1: Quality-handler status enum (read from quality-handler's output)
- Contract 2: Phase-quality verdict schema (read from phase-quality-reviewer's output)
- Contract 3: Audit-counter delta schema (read from phase-quality-reviewer's output)
- Contract 4: Dispatch taxonomy (observed from finalize-reconciler's dispatches)
- Contract 5: State-transition payload (EMITTED via log_state_transition.py for every transition)

## Cycle-cap escalation (AC-FR-10-c)

When either cycle counter (per-task or per-phase) exhausts 4 cycles without resolution, the parent orchestrator MUST:

1. Emit a final state transition to TERMINATED with `trigger: cycle-cap-exhaustion`.
2. Write a structured escalation payload to `working/feature/<slug>/escalation-cycle-cap.json` including full cycle history.
3. Surface the escalation to the user via AskUserQuestion or equivalent.
4. Do NOT continue execution.

## Blocks-X marker gate (FR-9 / AC-FR-9-a / AC-FR-9-b)

At every stage-transition checkpoint where the parent orchestrator advances state, it MUST run the Blocks-X marker parser before completing the transition. The gate is most critical at T7, T8, T11, and T12; it MUST also run at T0 (boundary entry) to catch markers already present in upstream artifacts before any execution begins.

### When the gate runs

| Transition | Checkpoint description |
|---|---|
| T0 (boundary) | Before first per-task dispatch — scan upstream artifacts for any pre-existing markers |
| T7 | per_task_approved → phase_quality_active (all tasks in phase approved) |
| T8 | phase_quality_active → phase_complete (phase-quality-reviewer PASS) |
| T11 | phase_complete → pending (next phase begins) |
| T12 | phase_complete → pipeline_complete (last phase complete) |

### What the gate does

The parent orchestrator invokes `parse_blocks_x_markers.py` against all markdown artifacts in the current `working/feature/<slug>/` directory and the canonical `adrs/` directory:

```bash
python3 .claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py <artifact-path>
```

The parser is invoked per file; the orchestrator iterates over relevant artifact paths and aggregates results. The exit code semantics govern the orchestrator's response:

**Exit 2 — no markers found.** The gate passes transparently. No gate logic needed; the orchestrator advances normally.

**Exit 0 — markers present, all well-formed.** The orchestrator MUST require explicit resolution for EACH marker before advancing past the gate. The orchestrator MUST NOT advance the state machine transition until every detected marker carries a logged closure transition. Resolution options (per ADR-0063 §Decision):

1. **`BLOCKS_X_RESOLVED`** — marker closed with rationale; the blocking concern is satisfied.
2. **`BLOCKS_X_DEFERRED_WITH_OI`** — marker converted to an explicit Open Item (OI); downstream stage may proceed; the OI must be tracked.
3. **`BLOCKS_X_FALSE_POSITIVE`** — marker withdrawn with rationale; the blocking concern does not apply.

**Exit 1 — malformed markers present.** The orchestrator HALTS. Malformed markers are a structural defect (BLOCKER severity — see §Severity calibration below). The orchestrator surfaces the malformed marker details to the user via AskUserQuestion or equivalent before any further transition.

### Resolution logging

For each detected marker requiring closure, the parent orchestrator MUST emit a state-transition entry to `state-transitions.log` using the canonical JSONL entry shape (per `state-transitions-log-entry-template.md`). The entry MUST use one of the three reserved `transition_name` values. The `context` field carries the marker's stage slug and the closure rationale in the form:

```
"context": {
  "target_marker": "<stage-slug>-completion",
  "additional_notes": "<closure-rationale-one-liner>"
}
```

The `target_marker` field names the marker by its stage-slug (e.g., `"design-cc-completion"`). This field is required for all three Blocks-X closure transition names; its absence is a malformed log entry.

Example resolution entry:

```json
{"timestamp":"<ISO-8601-UTC>","transition_name":"BLOCKS_X_RESOLVED","from_state":"phase_complete","to_state":"pipeline_complete","trigger":"Blocks-X marker resolved before T12 pipeline_complete advance","task_id":null,"phase_id":"<phase-id>","cycle_counter":null,"artifact_paths_affected":["working/feature/<slug>/<artifact>.md"],"invoking_agent":"execute-orchestrator","context":{"target_marker":"design-cc-completion","additional_notes":"blocking concern cleared; design decision confirmed in cc-design §FR-9 block"}}
```

### Severity calibration

Per `KB-review-disciplines/references/severity-taxonomy.md` §Cross-Surface Severity Bridge Table and the FR-9 row therein:

- **Unresolved markers crossing a phase boundary** — MAJOR severity. A marker present at a gate checkpoint that has not been given a closure transition before the orchestrator advances is an outright gate failure.
- **Malformed markers** — BLOCKER severity. A marker that does not conform to the canonical grammar `<!-- BLOCKS: <stage-slug>-completion -->` is a structural defect that halts the pipeline.

### Cross-references

- **ADR-0063** (`adrs/ADR-0063-blocks-x-marker-grammar.md`) — canonical Blocks-X marker grammar; parser regex; three reserved `transition_name` values.
- **`parse_blocks_x_markers.py`** (`.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py`) — canonical parser; exit codes 0/1/2.
- **`state-transitions-log-entry-template.md`** (`.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`) — canonical entry shape; `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE` semantics and example entries.
- **`severity-taxonomy.md`** (`.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`) — §Cross-Surface Severity Bridge Table; FR-9 row.
- **AC-FR-9-a** — orchestrator invokes parser at stage-transition checkpoints.
- **AC-FR-9-b** — orchestrator requires resolution before advancing past a gate with detected markers.

---

## Reading order on invocation

The parent orchestrator MUST, at the start of an execution-phase run:

1. Read `tasks.json` for the work DAG.
2. Read `phase-validators.md` for the phase pass criteria.
3. Read `acceptance-tests.md` for AC traceability.
4. Read `blueprint-v5.md` Components 2-6 for downstream-agent contracts.
5. Emit T0 transition to log.
6. Run Blocks-X marker gate at T0 checkpoint (scan upstream artifacts).
7. Begin per-task loop.
