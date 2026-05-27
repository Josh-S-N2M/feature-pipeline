# Cross-task patch: T7.1 parser fix — Execution Result

**Status:** COMPLETED
**Patch type:** Bug fix — `_parse_markdown_table()` multi-table scanner

## Summary

Fixed `_parse_markdown_table()` in `audit_feature_touch_coverage.py` to correctly
identify the canonical 5-column matrix table among multiple tables in a markdown document.

**Root cause confirmed:** The original parser exited on the first non-pipe line after
entering table mode. For the T8.1 matrix file, that first non-pipe line was the `---`
horizontal rule separating the 4-row Trigger-Evidence Record table from the canonical
37-row matrix. The parser therefore returned 4 rows with wrong column headers, producing
two MAJOR findings (row count mismatch, missing columns) on a structurally correct matrix.

## Files modified

- `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py`
- `.claude/skills/auditing-subagents/scripts/smoke_test_audit_feature_touch_coverage.py`

## What changed

### audit_feature_touch_coverage.py

Replaced `_parse_markdown_table()` (single-table-first parser) with:

1. `_split_row()` — extracted helper (was nested inside the old function)
2. `_collect_all_tables()` — scans the full document and accumulates ALL pipe-line blocks as (headers, rows) pairs; a non-pipe line ends the current block and scanning continues
3. `_is_canonical_matrix_table()` — returns True if a table's headers contain all five required columns (case-insensitive after normalisation)
4. `_parse_markdown_table()` — now calls the above: finds all tables, filters by canonical header signature, returns the matching table or a new error rule

Two new rule constants:
- `RULE_TABLE_NOT_FOUND = "SA-14.matrix_table_not_found"` (severity: BLOCKER)
- `RULE_TABLE_AMBIGUOUS = "SA-14.matrix_table_ambiguous"` (severity: MAJOR)

`_validate_matrix()` updated to unpack the new three-value return `(headers, rows, error_rule)` and emit the appropriate finding for each error case.

### smoke_test_audit_feature_touch_coverage.py

Added scenario F: writes a multi-table matrix file with a 4-row preamble table
(Condition/Description/Fired?/Evidence columns) followed by a `---` separator and the
canonical 6-column matrix — the exact document structure that triggered the regression.
Asserts clean PASS with correct row count.

## 4-Phase Gate

| Phase | Check | Result |
|---|---|---|
| 1 (lint) | `python3 -c "import ast; ast.parse(...)"` on both files | PASS |
| 2 (build) | stdlib-only imports; no compilation step needed | PASS |
| 3 (test) | `python3 smoke_test_audit_feature_touch_coverage.py` — 6/6 scenarios | PASS (exit 0) |
| 4 (final gate) | Re-run syntax check + smoke suite | PASS (exit 0) |

## Smoke test output (post-fix)

```
[PASS] A passed — predicate silent → not_applicable PASS
[PASS] B passed — predicate fired + compliant matrix → clean PASS
[PASS] C passed — predicate fired + matrix absent → BLOCKER FAIL
[PASS] D passed — bare no-change cell → MAJOR cell finding FAIL
[PASS] E passed — row count mismatch (3 vs 5 agents) → MAJOR row-count finding FAIL
[PASS] F passed — multi-table matrix (preamble table + canonical matrix) → parser finds canonical table → clean PASS

6/6 scenarios passed.
```

## Live SA-14 audit verdict

```json
{
  "sa14_status": "clean",
  "feature_slug": "pipeline-design-time-discipline-r1",
  "matrix_path": "...working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md",
  "agent_count_expected": 37,
  "row_count_observed": 37,
  "findings": [],
  "verdict": "PASS",
  "elapsed_ms": 110
}
```

## Scope Deviations

None. Only the two declared target files were modified. The matrix file at
`working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md`
was not touched (it was correct; the defect was in the parser).
