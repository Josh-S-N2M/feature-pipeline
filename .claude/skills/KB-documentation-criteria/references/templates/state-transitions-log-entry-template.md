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

### v1 invariant: `invoking_agent` is the logical owner, not the literal emitter

**v1 invariant (clarified per ADR-0044).** The `invoking_agent` field is the **logical owner** of the state transition, not the literal emitting agent. In v1 of the state-transitions-log schema, this value is **always `"execute-orchestrator"`** — even when the parent `recipe-feature-pipeline` orchestrator is the literal agent emitting the entry under ADR-0044's flatten pattern. The decoupling of "who emits" (mutable across dispatch patterns) from "who owns" (stable across patterns) preserves the audit-trail invariant and ensures in-flight artifacts like `working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log` remain valid under the new pattern WITHOUT migration. Per NFR-6-a, no schema evolution is required to honor this invariant; it is a clarification of v1 semantics, not a new field. Future v2+ schemas may add a separate `literal_emitter` field if multi-owner topologies emerge; this is out of scope for v1.

**Cross-references:**
- ADR-0044 §Implementation Guidance — the flatten pattern that makes "literal emitter" vs. "logical owner" distinct
- `recipe-feature-pipeline/SKILL.md` §Execution Phase Dispatch → invoking_agent Logical-Owner Invariant — the canonical normative statement of this invariant (authors of new orchestration patterns must read this sub-section)
- AC-FR-6-a, AC-NFR-6-a — the acceptance criteria this invariant verifies
- NFR-6-a — the in-flight artifact preservation guarantee (no migration required for existing logs)

## Optional fields

- `task_id` — present for per-task transitions (T1-T6); null for phase-level
- `phase_id` — present for phase-level transitions (T7-T12); null for per-task
- `cycle_counter` — present when the transition increments a cycle counter (T4 per-task, T10 phase)
- `artifact_paths_affected` — list of paths the transition touched
- `context` — free-form additional metadata

### Void / re-emission optional fields

**`void`** (boolean, optional, default `false`). Set to `true` when this transition entry was emitted but subsequently superseded by a `-prime` re-emission (e.g., a quality-handler verdict was first emitted as `NEEDS_REVISION` but the reconciler later reclassified it; the prior entry is voided with `void: true` and the new entry's `transition` field uses the `-prime` suffix). Voided entries are PRESERVED in the log (audit-trail property: every emitted transition is logged, including voided ones). The void chain is auditable by traversing the entries in timestamp order.

**`void_reason`** (string, optional). Paired with `void: true`; documents WHY the entry was voided (e.g., `"reconciler reclassified as APPROVED after re-review"`, `"cycle-cap exhaustion triggered re-dispatch"`). Required only when `void: true`; otherwise omit. Free-text; aim for one short sentence.

**Cross-references for void/void_reason:**
- `recipe-feature-pipeline/SKILL.md` §execution_pipeline_state_transitions — per-entry semantics — the canonical schema narrative for these fields (authors of new orchestration patterns must read this sub-section)
- See "Re-emission Conventions" section below for the `-prime` suffix that pairs with these fields

## Re-emission Conventions

### `-prime` transition-name suffix convention

**`-prime` transition-name suffix convention.** When a transition needs to be re-emitted (e.g., after reconciliation reclassifies a verdict, or after cycle-cap exhaustion triggers re-dispatch), the re-emission uses the same T-N label suffixed with `-prime`, `-double-prime`, `-triple-prime`, etc. For example: the initial T2 (per_task_active → quality_active) is logged with `transition: "T2"`; if the reconciler later reclassifies and quality is re-emitted, the new entry uses `transition: "T2-prime"`. The prior T2 entry's `void` field is set to `true` with a `void_reason` recording the supersession. The suffix chain is finite in practice (per ADR-0017's 4-cycle cap; max 3 suffixes = `-triple-prime` before escalation per AC-FR-10-c).

**Cross-references for `-prime` suffix:**
- `recipe-feature-pipeline/SKILL.md` §execution_pipeline_state_transitions — The `-prime` transition-name suffix convention — the canonical normative statement (including the audit-trail invariant per analysis §3.1)
- ADR-0017 — 4-cycle cap that bounds the suffix chain depth
- AC-FR-10-c — cycle-cap escalation (enforced by `execute-finalize-reconciler`) that triggers when the cap would be exceeded

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

### Void + re-emission example

The following pair illustrates a T4 entry being voided after the reconciler reclassifies the verdict, with the replacement logged as `T4-prime`:

```json
{"timestamp":"2026-05-23T01:00:00Z","transition_name":"T4","from_state":"quality_active","to_state":"per_task_active","trigger":"quality-handler returned NEEDS_REVISION","task_id":"T2.1","phase_id":"phase-2","cycle_counter":1,"artifact_paths_affected":[],"invoking_agent":"execute-orchestrator","void":true,"void_reason":"reconciler reclassified as COMPLETED after reviewing full context","context":{"verdict":"NEEDS_REVISION","finding_count":1}}
{"timestamp":"2026-05-23T01:05:00Z","transition_name":"T4-prime","from_state":"quality_active","to_state":"per_task_active","trigger":"reconciler reclassified quality verdict; re-emitting as COMPLETED","task_id":"T2.1","phase_id":"phase-2","cycle_counter":1,"artifact_paths_affected":[],"invoking_agent":"execute-orchestrator","context":{"verdict":"COMPLETED","finding_count":0,"additional_notes":"supersedes voided T4 entry at 2026-05-23T01:00:00Z"}}
```

The voided entry retains `"void": true` + `"void_reason"` for audit; the replacement entry uses the `-prime` suffix. Neither entry is deleted or overwritten (append-only log invariant).

## Note on AC-FR-7-c floor coverage

Per Blueprint § AC-FR-7 floor coverage Path B disposition (cross-referenced by ADR-0033 §Context per I-AA-606): the 5th floor item "frontmatter-validation report" is NOT a separately-templated artifact. It is satisfied by the script-output schema inline in `validate_pipeline_frontmatter.py` source. `state-transitions-log-entry` is a beyond-floor artifact per AC-FR-7-d permission.
