---
id: STLE-template
version: 1.0.0
status: draft
feature_slug: <example-feature-slug>
doc_type: state-transitions-log
generated: <ISO-8601-UTC>
generated_by: documentation-criteria template authoring
derived_from:
  - working/feature/<feature-slug>/blueprint-v<N>.md (Contract 5 state-transition payload)
agent_invocation_simulation: false
---

# State Transitions Log Entry — Template

## Contents

- [ ] Log file conventions
- [ ] Per-entry JSONL schema
- [ ] Required fields
- [ ] Optional fields
- [ ] Boundary transitions (T0, T13) per I-AA-609
- [ ] Example entries

## Log file conventions

- **Path**: `working/feature/<feature-slug>/state-transitions.log`
- **Format**: JSONL (one JSON object per line; line-delimited)
- **Append-only**: never edit or delete prior entries. Per Blueprint Contract 5 + D-16 the log is the audit trail.
- **No frontmatter on the log itself**: the log is a stream of JSONL entries, not a Markdown document. This template documents the per-entry schema; the actual file has no `---` block.

## Per-entry JSONL schema (per Blueprint Contract 5)

Each line is one JSON object conforming to:

```json
{
  "timestamp": "<ISO-8601-UTC>",
  "transition_name": "<symbolic-name-from-14-row-table>",
  "from_state": "<state-name>",
  "to_state": "<state-name>",
  "trigger": "<what-caused-the-transition>",
  "task_id": "<task-id-if-applicable, else null>",
  "phase_id": "<phase-id-if-applicable, else null>",
  "cycle_counter": <integer-if-applicable, else null>,
  "artifact_paths_affected": ["<path>", "..."],
  "invoking_agent": "execute-orchestrator",
  "context": {
    "verdict": "<if from quality-handler or phase-quality-reviewer>",
    "finding_count": <integer-if-applicable>,
    "additional_notes": "<free-form>"
  }
}
```

## Required fields

- `timestamp` — ISO-8601 UTC
- `transition_name` — one of T0..T13 per Blueprint § State Transitions and Invariants
- `from_state` — state-name
- `to_state` — state-name
- `trigger` — short description
- `invoking_agent` — always `execute-orchestrator` in v1 (other agents may emit events via the orchestrator)

## Optional fields

- `task_id` — present for per-task transitions (T1-T6); null for phase-level
- `phase_id` — present for phase-level transitions (T7-T12); null for per-task
- `cycle_counter` — present when the transition increments a cycle counter (T4 per-task, T10 phase)
- `artifact_paths_affected` — list of paths the transition touched
- `context` — free-form additional metadata

## Boundary transitions (T0, T13) per I-AA-609

Boundary transitions ARE logged using the same protocol as substantive transitions, with these distinctions:

| Boundary | from_state | to_state | trigger pattern |
|---|---|---|---|
| T0 | `INIT` | `pending` | `execution-phase invocation` |
| T13 | <any> | `TERMINATED` | `pipeline_complete` \| `user-escalation` \| `cycle-cap-exhaustion` |

**Invariant 10 scope (per I-AA-609 clarification)**: T0 and T13 transitions are logged but do NOT increment cycle counters. Only T4 (per-task NEEDS_REVISION) and T10 (phase reconciliation cycle complete) increment counters.

## Example entries

```json
{"timestamp":"2026-05-22T23:00:00Z","transition_name":"T0","from_state":"INIT","to_state":"pending","trigger":"execution-phase invocation","task_id":null,"phase_id":null,"cycle_counter":null,"artifact_paths_affected":[],"invoking_agent":"execute-orchestrator","context":{"additional_notes":"feature execution started"}}
{"timestamp":"2026-05-22T23:05:00Z","transition_name":"T1","from_state":"pending","to_state":"per_task_active","trigger":"dispatch code-producer for T0.4","task_id":"T0.4","phase_id":"phase-0","cycle_counter":null,"artifact_paths_affected":[],"invoking_agent":"execute-orchestrator","context":{}}
{"timestamp":"2026-05-22T23:10:00Z","transition_name":"T4","from_state":"quality_active","to_state":"per_task_active","trigger":"quality-handler returned NEEDS_REVISION","task_id":"T0.4","phase_id":"phase-0","cycle_counter":1,"artifact_paths_affected":[".claude/skills/auditing-shared/scripts/log_state_transition.py"],"invoking_agent":"execute-orchestrator","context":{"verdict":"NEEDS_REVISION","finding_count":2}}
{"timestamp":"2026-05-23T00:00:00Z","transition_name":"T13","from_state":"phase_complete","to_state":"TERMINATED","trigger":"pipeline_complete","task_id":null,"phase_id":"phase-6","cycle_counter":null,"artifact_paths_affected":["working/feature/<slug>/pipeline-run-summary.json"],"invoking_agent":"execute-orchestrator","context":{"additional_notes":"feature execution complete"}}
```

## Note on AC-FR-7-c floor coverage

Per Blueprint § AC-FR-7 floor coverage Path B disposition (cross-referenced by ADR-0033 §Context per I-AA-606): the 5th floor item "frontmatter-validation report" is NOT a separately-templated artifact. It is satisfied by the script-output schema inline in `validate_pipeline_frontmatter.py` source. `state-transitions-log-entry` is a beyond-floor artifact per AC-FR-7-d permission.
