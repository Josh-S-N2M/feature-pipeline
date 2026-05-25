# Per-Task Execution Result: T2d.1

**Task:** Sub-procedure (i) — No-collision adds for ADRs 0001-0006, 0008-0010 (9 IDs)
**Status:** COMPLETED
**Phase 4 gate passed:** true

## Operations Executed

### git mv (9 renames)

| Source (adrs-migrated/) | Target (adrs/) |
|-------------------------|----------------|
| ADR-0001-orchestrator-placement.md | ADR-0001-orchestrator-placement.md |
| ADR-0002-critique-1-discipline.md | ADR-0002-critique-1-discipline.md |
| ADR-0003-critique-2-discipline.md | ADR-0003-critique-2-discipline.md |
| ADR-0004-test-split.md | ADR-0004-test-split.md |
| ADR-0005-append-only-supersession.md | ADR-0005-append-only-supersession.md |
| ADR-0006-synthesis-inlined.md | ADR-0006-synthesis-inlined.md |
| ADR-0008-issue-ledger-scope.md | ADR-0008-issue-ledger-scope.md |
| ADR-0009-rationale-brief-discipline.md | ADR-0009-rationale-brief-discipline.md |
| ADR-0010-knowledge-skill-frontmatter-correction.md | ADR-0010-knowledge-skill-frontmatter-correction.md |

### git rm (18 deletes)

Each of the 9 IDs had 2 variant files deleted:
- `-pre-naming-convention.md` variant (9 files)
- `-pre-template-migration.md` variant (9 files)

### Migration-log

9 rows appended to the Phase 2d table under sub-procedure (i) in `working/feature/adr-placement-mechanism-repair-r1/migration-log.md`.

## Verification

- `git status --short` shows exactly 9 renames (R) and 18 deletes (D) for the target IDs.
- All 9 canonical targets confirmed present at `adrs/`.
- No ADR-0001 through ADR-0006, ADR-0008 through ADR-0010 files remain in `adrs-migrated/`.
- No collision detected at `adrs/` for any of the 9 IDs (verified before operations).

## Scope Deviation Note

The task spec describes source files with a `-final` suffix (e.g., `ADR-0001-canonical-process-naming-final.md`) and lists target slugs that differ from the actual source slugs. The actual source files in `adrs-migrated/` carry plain slugs without `-final` (e.g., `ADR-0001-orchestrator-placement.md`), and the slugs differ from those in `target_files` (task spec lists `adrs/ADR-0001-canonical-process-naming.md` but source slug is `orchestrator-placement`).

Per the task spec sanity-check instruction ("use the SOURCE filename's slug for the target"), canonical targets were placed using the source slugs. This deviation is surfaced for orchestrator / reconciler review. Proposed resolution: defer (the files are now at canonical with correct content; the slug difference reflects a discrepancy between the task spec's anticipated slug and the actual historical slug in the archive).
