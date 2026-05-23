---
id: PTER-<feature-slug>-<task-id>
version: 1.0.0
status: draft
feature_slug: <feature-slug>
doc_type: per-task-execution-result
task_id: <task-id>
phase_id: <phase-id>
generated: <ISO-8601-UTC>
generated_by: execute-task-code-producer
derived_from:
  - working/feature/<feature-slug>/tasks.json (task entry for <task-id>)
  - working/feature/<feature-slug>/blueprint-v<N>.md (Component 2 contract)
agent_invocation_simulation: false
---

# Per-Task Execution Result — <task-id>

## Contents

Section completion checklist (per Plan template discipline):

- [ ] Status
- [ ] Files Modified
- [ ] Files Created
- [ ] Findings (4-phase + stub-check passes)
- [ ] Scope Deviations (per ADR-0033 surfacing)
- [ ] Notes

## Status

One of: **COMPLETED** | **INCOMPLETE** | **BLOCKED** (per Blueprint Contract 1 + D-2a selective BLOCKING discipline).

| Status | Meaning | Orchestrator response |
|---|---|---|
| COMPLETED | 4-phase gate passed; revision_context (if any) fully addressed | quality-handler dispatch (T2) |
| INCOMPLETE | One or more 4-phase failures the agent expects to fix in a revision cycle | NEEDS_REVISION re-dispatch (T4) |
| BLOCKED | Cannot be completed without scope expansion OR upstream design change | Escalate to user (AC-FR-2-e) |

## Files Modified

List of every file path modified during this task execution. Used by quality-handler for scope verification (out-of-scope edits → BLOCKER finding).

- `<path-1>`
- `<path-2>`

## Files Created

New files created. Same scope-verification semantics.

- `<path-1>`

## Findings (4-phase gate)

For each phase (lint, build, test, final gate): pass/fail + details.

| Phase | Tool | Result | Notes |
|---|---|---|---|
| Format/Lint | <tool> | PASS \| FAIL | <details> |
| Build/Compile | <tool> | PASS \| FAIL | <details> |
| Test | <tool> | PASS \| FAIL | <details> |
| Final gate | composite | PASS \| FAIL | overall verdict |

## Scope Deviations (per ADR-0033)

Surface any deviation from the task's declared Target Files scope discovered during execution. Do NOT silently expand scope.

For each deviation:

- **Deviation**: what was discovered
- **Proposed resolution**: `expand-scope` | `defer` | `reject`
- **Evidence**: what led to the discovery

If no deviations: emit `(none)` explicitly. Do NOT omit the section — ADR-0033 requires affirmative no-deviation surfacing.

## Notes

Free-form prose for human review. Anything not captured in structured fields.

## Companion JSON

This .md is the human-readable half of a D-5 pair pattern. The machine-readable .json half lives at:

`working/feature/<feature-slug>/per-task-execution-result-<task-id>.json`

JSON schema (canonical):

```json
{
  "task_id": "<task-id>",
  "phase_id": "<phase-id>",
  "status": "COMPLETED | INCOMPLETE | BLOCKED",
  "files_modified": ["<path>", "..."],
  "files_created": ["<path>", "..."],
  "findings_4phase": {
    "lint": {"tool": "<tool>", "result": "PASS|FAIL", "notes": "..."},
    "build": {"tool": "<tool>", "result": "PASS|FAIL", "notes": "..."},
    "test": {"tool": "<tool>", "result": "PASS|FAIL", "notes": "..."},
    "final_gate": {"result": "PASS|FAIL"}
  },
  "scope_deviations": [
    {"deviation": "...", "proposed_resolution": "...", "evidence": "..."}
  ],
  "notes": "..."
}
```
