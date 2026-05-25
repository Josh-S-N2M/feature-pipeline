# Per-Task Execution Result — T2d.4

**Task:** Sub-procedure (iv) — Canonical-only for ADR-0007 with v1-superseded variant deletion per AA-003
**Phase:** P-2d
**Status:** COMPLETED
**Phase-4 gate passed:** yes

## Steps Executed

### Step 1 — Canonical verification
`adrs/ADR-0007-code-graph-mcp-selection.md` confirmed present and untouched.

### Step 2 — git rm of 4 archive variants
All four files removed from `adrs-migrated/` via `git rm`:
- `ADR-0007-code-graph-mcp-selection-pre-naming-convention.md`
- `ADR-0007-code-graph-mcp-selection-v1-pre-template-migration.md`
- `ADR-0007-code-graph-mcp-selection-v1-superseded.md` (AA-003 critical inclusion)
- `ADR-0007-code-graph-mcp-selection-v2-pre-template-migration.md`

### Step 3 — adrs-migrated/ directory removal
Git automatically removed the directory when its last tracked file was deleted. `ls adrs-migrated/` returns "No such file or directory". `git ls-files adrs-migrated/` returns 0 entries.

### Step 4 — Post-deletion verification
No ADR-0007 files remain tracked in `adrs-migrated/`. Zero tracked files remain in the directory path.

### Step 5 — migration-log rows appended
Two rows added to the Phase-2d table:
- ADR-0007 sub-procedure (iv) canonical-only + AA-003 v1-superseded deletion row
- (cleanup) adrs-migrated/ directory removal closeout row

## Files Modified
- `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` (2 rows appended)

## Files Deleted (git rm)
- `adrs-migrated/ADR-0007-code-graph-mcp-selection-pre-naming-convention.md`
- `adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-pre-template-migration.md`
- `adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-superseded.md`
- `adrs-migrated/ADR-0007-code-graph-mcp-selection-v2-pre-template-migration.md`

## Directories Removed
- `adrs-migrated/` (auto-removed by git; 0 tracked files remaining)

## Scope Deviations
None.

## Quality Gate Notes
IDE lint warnings (MD036/MD060) on migration-log.md are pre-existing throughout the file — same table formatting pattern used in all prior phase rows. No new regressions introduced by this task. Static analysis, build verification (markdown parse), and file-state verification all pass.

## AC Satisfaction
- AC-FR-8d-1 (full): All adrs-migrated/ variants for ADR-0007 removed; canonical retained.
- AC-FR-8d-2.1: AA-003 v1-superseded variant (`ADR-0007-code-graph-mcp-selection-v1-superseded.md`) deleted.
- AC-FR-8d-3: adrs-migrated/ directory is empty and removed from the working tree.
