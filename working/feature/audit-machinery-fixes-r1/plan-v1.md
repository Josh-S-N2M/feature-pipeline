---
feature_slug: audit-machinery-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/audit-machinery-fixes-r1/blueprint-v1.md
approved_at: 2026-05-21T02:15:00Z
gate_passed: 4
---

# Plan — audit-machinery-fixes-r1

## Tasks in execution order

| ID | Task | Deliverable |
|---|---|---|
| T-1 | Snapshot v4.4.0 baseline audit for delta tracking | `/tmp/v44-baseline.md` |
| T-2 | Classify baseline findings by type to scope cleanup | (analysis) |
| T-3 | Author + validate proposed DE-2 regex against 14-case TP/FP matrix | `/tmp/test_de2.py` |
| T-4 | Apply DE-2 fix to `scan_security.py` lines 57-66 | edit |
| T-5 | Apply BACKTICK_PATH cross-KB fix to `lint_references.py` `normalize()` | edit |
| T-6 | Apply `deductions_by_severity` fix to `verdict_compute.py` | edit |
| T-7 | Re-run audit; verify baseline reduction + summary/line alignment | `/tmp/v441-postfix.md` |
| T-8 | Revert workaround 1: `process['env']['X']` → `process.env.X` (2 sites) | sed |
| T-9 | Revert workaround 2: cross-KB references back to backticked-full-path (16 sites) | sed |
| T-10 | Re-run audit; verify reverts don't reintroduce findings | `/tmp/v441-final.md` |
| T-11 | (Bonus discovered during T-10) Add depth-2 within-skill check | edit |
| T-12 | Final audit pass; confirm AC-5 (baseline strictly decreased) | `/tmp/v441-final2.md` |
| T-13 | Author ADR-0026 documenting fixes + validation methodology | `adrs/ADR-0026-*.md` |
| T-14 | Author HANDOFF-v4.4.1.md + CONTINUE_PROMPT-v4.4.1.md | `handoff/` |
| T-15 | Package v4.4.1 zip; verify structure | `feature-pipeline-round-3-v4_4_1.zip` |
| T-16 | Present file to user | (deliverable) |

## Parallelization

None. Each task depends on its predecessor:
- T-4/T-5/T-6 could theoretically run in parallel but are small enough to sequence.
- T-11 was unplanned at run start; surfaced as a deviation during T-10.

## Validation

Each task has a definition of done in `acceptance-tests.md`. Phase boundaries are documented in `phase-validators.md`.
