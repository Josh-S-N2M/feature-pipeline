---
id: PQR-<feature-slug>-<phase-id>
version: 1.0.0
status: draft
feature_slug: <feature-slug>
doc_type: phase-quality-report
phase_id: <phase-id>
generated: <ISO-8601-UTC>
generated_by: execute-phase-quality-reviewer
derived_from:
  - working/feature/<feature-slug>/plan-v<N>.md (phase definition + exit criteria)
  - working/feature/<feature-slug>/phase-validators.md (phase pass criteria)
  - script output from .claude/skills/auditing-shared/scripts/run_phase_checks.py
agent_invocation_simulation: false
---

# Phase Quality Report — <phase-id>

## Contents

- [ ] Verdict (overall + per-dimension)
- [ ] Findings
- [ ] Audit-counter delta (per Contract 3)
- [ ] Scope Deviations
- [ ] Rationale

## Verdict (per Blueprint Contract 2 — 5-dimensional dimensional verdict)

**Overall**: `PASS` | `NEEDS_RECONCILIATION` | `BLOCKER`

**Per dimension**:

| Dimension | Verdict | Notes |
|---|---|---|
| tests | PASS \| NEEDS_RECONCILIATION \| BLOCKER | unit + integration + E2E |
| audits | PASS \| NEEDS_RECONCILIATION \| BLOCKER | cc-audit + gha-audit + codespaces-audit (stub or real) |
| validator | PASS \| NEEDS_RECONCILIATION \| BLOCKER | frontmatter-validator results |
| discipline | PASS \| NEEDS_RECONCILIATION \| BLOCKER | discipline-5 check results |
| scope_deviations | PASS \| NEEDS_RECONCILIATION \| BLOCKER | ADR-0033 surfacing aggregation |

**Rollup rule (per Contract 2)**: blocking finding in any dimension → overall `BLOCKER`; revisable finding in any dimension → overall `NEEDS_RECONCILIATION`; all clean → overall `PASS`.

**Q-CC-4 stub-vs-real distinction**: if any audit dimension's underlying source returns `{"stub": true, ...}`, that dimension is treated as **not measured**, not "measured zero". The `stub: true` marker is preserved in the JSON half.

## Findings

For each finding, per the canonical schema (Blueprint Field Propagation Map finding schema):

| ID | Domain | Severity | Source Activity | File Path | Message | Dispatch Hint | Depth Level |
|---|---|---|---|---|---|---|---|
| F-1 | tests \| audits \| validator \| discipline \| scope_deviations | blocker \| major \| minor \| info | <source> | <path> | <description> | <upstream stage> | 0-8 |

## Audit-counter delta (per Blueprint Contract 3 + Q-CC-3 per-domain breakdown)

```json
{
  "audit_counter_delta": {
    "baseline_type": "feature_start | prior_phase",
    "primary_baseline": "feature_start",
    "feature_start": {
      "per_domain": {
        "tests": "N1→N2",
        "audits": "N3→N4",
        "validator": "N5→N6",
        "discipline": "N7→N8",
        "scope_deviations": "N9→N10"
      },
      "aggregate": "N11→N12"
    },
    "prior_phase": {
      "per_domain": { },
      "aggregate": "..."
    },
    "gating": "informational | gating",
    "gating_rule": null,
    "audit_severity_breakdown": null
  }
}
```

## Scope Deviations (per ADR-0033)

Surface every ADR-0033 scope-deviation finding discovered during the phase. Categories per Blueprint Contract 4 row 8:

- Deviation from declared task scope
- Deviation from Plan phase scope
- Deviation from Blueprint Layer Scope
- Deviation from PRD Functional Requirements scope

If no deviations: emit `(none)` explicitly.

## Rationale

One paragraph summarizing why the overall verdict is what it is. Specifically: which dimension(s) drive the verdict; whether the orchestrator should advance to next phase (T8), trigger reconciliation (T9), or escalate.

## Companion JSON

This .md is the human-readable half of a D-5 pair pattern. The machine-readable .json half lives at:

`working/feature/<feature-slug>/phase-quality-report-<phase-id>.json`

The JSON conforms to Blueprint Contract 2 (the verdict + per_dimension_status + findings array + audit_counter_delta) verbatim.
