# Per-Task Execution Result — task-015 (T2.5)

**Status**: COMPLETED
**Phase 4 gate**: PASSED (11/11 scenarios, exit 0)

## Files Modified

- `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`

## Files Created

None.

## What Was Done

Extended the smoke test with four new scenarios appended after the existing seven (A–G):

**Scenario H — 18 positive fixtures**
Each of the 18 positive fixtures is read from disk, frontmatter parsed via `parse_frontmatter`, then passed to `validate_issue_artifact` with a synthetic path matching the fixture's topic slug. Every call must return `[]`. All 18 pass.

**Scenario I — 10 negative/advisory fixtures**
Three sub-groups:
- 6 missing-companion-field fixtures: each asserts exactly 1 blocker finding whose message contains the expected field name.
- 3 invalid-status fixtures: each asserts exactly 1 blocker finding whose message contains "vocabulary" (the short-circuit path per spec).
- 1 advisory fixture: asserts exactly 1 info finding whose message contains "proposes_future_feature".

**Scenario J — AC-BE-10 evidence-path early-return**
Calls `validate_file` on the real fixture at `test_fixtures/issue_doc_types/evidence-path-fixtures/Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md`. The path-prefix early-return (ADR-0044 §4) fires and returns `[]`.

**Scenario K — positive control**
Calls `validate_pipeline_artifact` directly with `doc_type: not-a-known-type` on a `working/feature/...` path (not under Issues/). Asserts exactly 1 minor finding with "not in known category" in the message, confirming the evidence-path skip does not over-silence.

## Judgment Call

The advisory fixture (`advisory-proposal-no-proposes_future_feature.md`) carries `id: PROPOSAL-test-proposal-no-pff`. The synthetic path used for Scenario I uses topic slug `test-proposal-no-pff` to match the fixture's actual id, preventing Check 5 (id vs path-derived expected id) from adding a spurious second finding. This is the correct alignment with the fixture's as-authored content.

## 4-Phase Gate

| Phase | Result |
|---|---|
| Phase 1 — lint/compile | `python3 -m py_compile` — OK |
| Phase 2 — build | n/a (pure Python script) |
| Phase 3 — test | smoke test 11/11 PASS, exit 0 |
| Phase 4 — final gate | smoke test re-run 11/11 PASS, exit 0 |

## Scope Deviations

None.
