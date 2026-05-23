---
id: PRS-template
version: 1.0.0
status: draft
feature_slug: <example-feature-slug>
doc_type: pipeline-run-summary
generated: <ISO-8601-UTC>
generated_by: documentation-criteria template authoring
derived_from:
  - working/feature/<feature-slug>/blueprint-v<N>.md (Data Representation Decision 3)
  - working/feature/<feature-slug>/state-transitions.log (transition history)
  - working/feature/<feature-slug>/phase-quality-report-*.json (per-phase verdicts)
agent_invocation_simulation: false
---

# Pipeline Run Summary — Template

## Contents

- [ ] Format note (JSON-only per D-3)
- [ ] Required fields
- [ ] Per-phase outcomes table
- [ ] Per-stage gate outcomes table
- [ ] Reconciliation cycles aggregation
- [ ] Final ship status
- [ ] Path B equivalence note (AC-FR-7-c floor coverage)

## Format note (per Blueprint § Data Representation Decision 3)

`pipeline-run-summary` is a **single JSON artifact per run** — no `.md` pair. This template documents the JSON schema; the actual artifact at `working/feature/<feature-slug>/pipeline-run-summary.json` is JSON-only.

This template file (the .md) exists for human reference / spec documentation only.

## JSON schema

```json
{
  "run_id": "<UUID-or-ISO-timestamp-string>",
  "feature_slug": "<slug>",
  "version_tag": "<semver-or-null>",
  "start_at": "<ISO-8601-UTC>",
  "end_at": "<ISO-8601-UTC>",
  "duration_seconds": <integer>,
  "per_stage_gate_outcomes": [
    {
      "stage": "intake-intent-clarification | intake-prd-authoring | discovery-planning | ...",
      "gate_passed": <integer>,
      "approved_at": "<ISO-8601-UTC>",
      "user_token": "<token>"
    }
  ],
  "per_phase_outcomes": [
    {
      "phase_id": "<phase-id>",
      "verdict": "PASS | NEEDS_RECONCILIATION | BLOCKER",
      "reconciliation_cycles_used": <integer>,
      "reconciliation_cycles_remaining": <integer>,
      "phase_quality_report_path": "working/feature/<slug>/phase-quality-report-<phase-id>.json"
    }
  ],
  "total_reconciliation_cycles_used": <integer>,
  "reconciliation_budget_cap": 4,
  "findings_dispatched_per_level": {
    "level_0": <integer>,
    "level_1": <integer>,
    "level_2": <integer>,
    "level_3": <integer>,
    "level_4": <integer>,
    "level_5": <integer>,
    "level_6": <integer>,
    "level_7": <integer>,
    "level_8": <integer>
  },
  "audit_counter_aggregate_delta": {
    "tests": "N1→N2",
    "audits": "N3→N4",
    "validator": "N5→N6",
    "discipline": "N7→N8",
    "scope_deviations": "N9→N10",
    "aggregate": "N11→N12"
  },
  "scope_deviations_surfaced": [
    {"phase_id": "<id>", "deviation": "...", "resolution": "..."}
  ],
  "final_ship_status": "SHIPPED | ESCALATED_TO_USER | ABANDONED",
  "escalation_payload": {
    "trigger": "cycle-cap-exhaustion | user-stop | other",
    "details": "..."
  }
}
```

## Required fields (per FR-13 machine-parseability + FR-12 audit-counter delta)

- `run_id`, `feature_slug`, `start_at`, `end_at` — identity + duration
- `per_stage_gate_outcomes` — covers planning-side gates (6 user gates)
- `per_phase_outcomes` — execution-side per-phase verdicts
- `total_reconciliation_cycles_used` — across all phases; aggregated against the 4-cycle cap per ADR-0017 (symmetric per D-12)
- `findings_dispatched_per_level` — per FR-4 9-level depth distribution
- `final_ship_status` — terminal-state classification

## Path B equivalence note (per Blueprint § AC-FR-7 floor coverage cross-referenced by ADR-0033 §Context per I-AA-606)

`pipeline-run-summary` serves a dual role per the Path B disposition:

1. **Primary role**: per-feature-run summary aggregating per-phase verdicts + per-stage gates + reconciliation usage.
2. **AC-FR-7-c floor coverage role**: the "execution-reconciliation log" floor item from PRD AC-FR-7-c is satisfied by this artifact — the per-feature-run reconciliation aggregation is the same artifact under a different framing. The Plan v2 + Blueprint v5 + ADR-0033 §Context all explicitly cross-reference this equivalence.

This bidirectional cross-reference is part of the I-AA-606 cycle-3 correction.

## Generation

Authored by `execute-orchestrator` at T12 (pipeline_complete transition). The orchestrator aggregates:

- `state-transitions.log` for gate-pass timestamps and per-phase transitions
- Each `phase-quality-report-<phase-id>.json` for per-phase verdicts
- Each `quality-reconciliation-log-<phase-id>-cycle-<N>.json` for reconciliation cycle counts
- `tasks.json` for the execution DAG (for findings_dispatched_per_level aggregation)
