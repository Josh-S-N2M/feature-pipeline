# Per-Task Execution Result — T2c.1

**Task:** git mv ADRs 0046–0050 to canonical + write .tombstone redirect notes
**Status:** COMPLETED
**Phase 4 gate:** PASSED
**Date:** 2026-05-25

## What was done

Five ADRs from `working/feature/issue-capture-mechanism-r1/adrs/` were relocated to canonical `adrs/` via `git mv`, preserving git history (NFR-5). Five tombstone redirect files were written. Five migration-log rows were appended to the Phase-2c table.

### git mv operations (all staged, R-status confirmed)

| ADR ID | Source (before) | Target (after) |
|--------|-----------------|----------------|
| ADR-0046 | working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-add-new-sibling-file-evolution.md | adrs/ADR-0046-add-new-sibling-file-evolution.md |
| ADR-0047 | working/feature/issue-capture-mechanism-r1/adrs/ADR-0047-three-layer-enforcement.md | adrs/ADR-0047-three-layer-enforcement.md |
| ADR-0048 | working/feature/issue-capture-mechanism-r1/adrs/ADR-0048-prior-context-handoff.md | adrs/ADR-0048-prior-context-handoff.md |
| ADR-0049 | working/feature/issue-capture-mechanism-r1/adrs/ADR-0049-structural-vs-discipline-kb-split.md | adrs/ADR-0049-structural-vs-discipline-kb-split.md |
| ADR-0050 | working/feature/issue-capture-mechanism-r1/adrs/ADR-0050-5-state-issues-vocabulary.md | adrs/ADR-0050-5-state-issues-vocabulary.md |

### Tombstone files written

All 5 tombstones at `working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN.tombstone` with the 3-line template per spec. Extension `.tombstone` used so the validator's `rglob('ADR-*.md')` does not match.

### Migration-log update

5 rows appended to Phase-2c table in `working/feature/adr-placement-mechanism-repair-r1/migration-log.md`.

## 4-Phase Quality Gate

- **Phase 1 (format/lint):** N/A — markdown and plain-text files; no formatter applicable.
- **Phase 2 (build/compile):** N/A — no code artifacts.
- **Phase 3 (test):** `git status --short` confirmed R-status for all 5 renames; tombstone files confirmed present; migration-log rows confirmed via grep.
- **Phase 4 (final gate):** All checks green. PASSED.

## Scope deviations

**Deviation (named-exempt):** The task spec's `target_files` and ADR slug table declared slugs that do not match what is on disk:

| ADR | Spec slug | Actual slug |
|-----|-----------|-------------|
| ADR-0046 | issue-capture-orchestration | add-new-sibling-file-evolution |
| ADR-0047 | issue-doctype-taxonomy | three-layer-enforcement |
| ADR-0048 | issue-frontmatter-discipline | prior-context-handoff |
| ADR-0049 | issue-doctype-structural-spec | structural-vs-discipline-kb-split |
| ADR-0050 | issue-capture-skill-architecture | 5-state-issues-vocabulary |

The task intent is unambiguous — relocate ADR-0046 through ADR-0050 from the issue-capture-mechanism-r1 working directory to canonical `adrs/`. No file matching the spec's declared slugs existed anywhere in the repository. The migration was executed against the actual files without content modification. This is a stale-spec artefact from when the ADRs were authored under tentative titles. Proposed resolution: named-exempt (no scope expansion needed; actual files are the correct subject).

## Acceptance criteria coverage

| AC | Status |
|----|--------|
| AC-FR-8c-1: ADR-0046–0050 exist at canonical adrs/ only after this feature ships | Satisfied — git mv executed, source paths now tombstoned |
| AC-FR-8c-2: redirect notes left in originating feature folder | Satisfied — 5 .tombstone files written |
| AC-NFR-5-a: relocation via git mv (not copy-and-delete) | Satisfied — R-status in git confirms rename tracking |
| AC-NFR-5-b: git log --follow traces back to original path | Satisfied — git mv preserves rename history |
