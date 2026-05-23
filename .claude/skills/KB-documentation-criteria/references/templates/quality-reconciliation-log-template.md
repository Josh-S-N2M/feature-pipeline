---
id: QRL-<feature-slug>-<phase-id>-cycle-<cycle>
version: 1.0.0
status: draft
feature_slug: <feature-slug>
doc_type: quality-reconciliation-log
phase_id: <phase-id>
cycle: <integer>
budget_used: <integer>
budget_remaining: <integer>
budget_cap_reference: "ADR-0017 (4-cycle cap; symmetric application per D-12)"
generated: <ISO-8601-UTC>
generated_by: execute-finalize-reconciler
derived_from:
  - working/feature/<feature-slug>/phase-quality-report-<phase-id>.json
  - working/feature/<feature-slug>/blueprint-v<N>.md (Contract 4 dispatch matrix)
agent_invocation_simulation: false
---

# Quality Reconciliation Log — <phase-id>, cycle <cycle>

## Contents

- [ ] Cycle context (budget + cap reference)
- [ ] Per-finding dispatch table
- [ ] Consolidated dispatches by (target_agent, target_artifact)
- [ ] Scope-deviations resolved (per ADR-0033 surfacing chain walk)
- [ ] Outcome (CONVERGED | RECONCILIATION_EXHAUSTED)

## Cycle context

| Field | Value |
|---|---|
| Cycle | <integer> |
| Budget used (after this dispatch) | <integer> |
| Budget remaining | <integer> |
| Cycle cap reached? | true \| false |

Per ADR-0017's 4-cycle cap (symmetric to per-task quality loops per D-12). Cycle 4 is terminal — if findings remain after cycle 4 dispatch, the outcome is `RECONCILIATION_EXHAUSTED` and the orchestrator escalates per AC-FR-10-c.

## Per-finding dispatch table

For each finding from the source `phase-quality-report`, classify per Blueprint Contract 4 (8-row dispatch matrix):

| Finding ID | Domain | Source Activity | Dispatch Target | Revision Context Summary | Rationale |
|---|---|---|---|---|---|
| F-1 | tests | unit | execute-task-code-producer (for task `<id>`) | failing tests + expected behavior | task-scope match |
| F-2 | scope_deviations | scope-deviation-scan | <agent walked from surfacing chain> | deviation context | per surfacing-location walk |

## Consolidated dispatches by (target_agent, target_artifact)

Multi-findings on one artifact are consolidated into a single re-invocation. Group key: `(target_agent, target_artifact)`.

| Target | Findings (count + IDs) | Revision context payload location |
|---|---|---|
| `execute-task-code-producer:T<id>:files=[<paths>]` | <count> findings (F-1, F-3, ...) | `working/feature/<slug>/revision-context-<task-id>-cycle-<N>.json` |

## Scope-deviations resolution chain walk (per ADR-0033 + I-AA-005 procedure)

For each scope_deviations finding, walk the surfacing-location chain to identify the responsible agent. Fallback: if no agent can be deterministically identified, escalate to user per AC-FR-10-c with full chain trace.

| Finding ID | Surfacing chain walked | Resolved target | Notes |
|---|---|---|---|
| F-N | <surfacing-location-1> → <surfacing-location-2> → ... | <agent> OR escalate-to-user | <notes> |

## Outcome

One of:

- **CONVERGED** — all findings dispatched; phase will re-run quality (T10); next cycle (if needed) will count.
- **RECONCILIATION_EXHAUSTED** — cycle 4 dispatched but findings persist; orchestrator escalates to user.

## Companion JSON

This .md is the human-readable half of a D-5 pair pattern. The machine-readable .json half lives at:

`working/feature/<feature-slug>/quality-reconciliation-log-<phase-id>-cycle-<cycle>.json`

JSON schema (per FR-13 machine-parseability + Blueprint Contract 4):

```json
{
  "phase": "<phase-id>",
  "cycle": <integer>,
  "budget_used": <integer>,
  "budget_remaining": <integer>,
  "outcome": "CONVERGED | RECONCILIATION_EXHAUSTED",
  "dispatches": [
    {
      "finding_id": "<id>",
      "dispatch_target": "<agent-name | escalate-to-user>",
      "revision_context_path": "<path>",
      "rationale": "<text>"
    }
  ],
  "consolidated_by_target": { "<key>": ["<finding-id>", "..."] },
  "scope_deviations_resolved": [
    {"finding_id": "<id>", "chain": ["...", "..."], "resolved_target": "<agent>"}
  ],
  "cycle_cap_reached": false
}
```
