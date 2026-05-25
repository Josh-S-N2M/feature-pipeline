# Per-Task Execution Result — T2d.3

**Task:** Sub-procedure (iii) — Canonical-wins for ADR-0018
**Phase:** P-2d
**Status:** COMPLETED

## Summary

Canonical-wins procedure executed for ADR-0018. The `adrs/ADR-0018-codebase-analysis-schema.md` (with ADR-0038 supersession marker per IN-004) is retained as the authoritative copy. Both `adrs-migrated/ADR-0018-*` variants have been removed via `git rm`.

## Operations Performed

### git rm (2 files)

- `adrs-migrated/ADR-0018-codebase-analysis-schema.md` — removed (v2.0.0 finalize-reconciler artifact, status "Accepted", no supersession marker; loses to canonical)
- `adrs-migrated/ADR-0018-codebase-analysis-schema-pre-naming-convention.md` — removed (pre-naming-convention archive variant; loses to canonical)

### Retained (unchanged)

- `adrs/ADR-0018-codebase-analysis-schema.md` — canonical (status "Superseded by ADR-0038", supersession marker present, per IN-004)

### Migration-log update

Appended row to Phase-2d table in `working/feature/adr-placement-mechanism-repair-r1/migration-log.md`:

```
| ADR-0018 | (iii) canonical-wins | adrs-migrated/ADR-0018-* variants | adrs/ADR-0018-codebase-analysis-schema.md (retained) | N/A | COMPLETED |
```

## Scope Deviations

One naming discrepancy surfaced between the task spec and the actual repository state:

- Task spec listed `adrs-migrated/ADR-0018-codebase-analysis-schema-final.md` as a target
- Actual file in repo is `adrs-migrated/ADR-0018-codebase-analysis-schema.md` (no `-final` suffix)

This is a task-spec naming artifact. The intent is unambiguous (remove all `adrs-migrated/ADR-0018-*` variants) and was fully executed. Surfaced as `named-exempt` scope deviation.

## 4-Phase Gate

| Phase | Check | Result |
|-------|-------|--------|
| 1 — Lint/Format | Markdown files; no formatter configured; structural validity confirmed | PASS |
| 2 — Build | `adrs-migrated/ADR-0018-*` files absent from filesystem; `adrs/ADR-0018` canonical intact with supersession marker confirmed | PASS |
| 3 — Test | Migration-log row present with correct values (adr_id, sub_procedure, source, target, result) | PASS |
| 4 — Final gate | git status shows 2 staged deletions + migration-log modified; no unexpected changes | PASS |

## Files Modified

- `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` (Phase-2d row appended)

## Files Removed

- `adrs-migrated/ADR-0018-codebase-analysis-schema.md`
- `adrs-migrated/ADR-0018-codebase-analysis-schema-pre-naming-convention.md`
