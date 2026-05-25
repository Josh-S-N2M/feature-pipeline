# Notification: ADR Placement Repair (adr-placement-mechanism-repair-r1) — Disposition for ADR-0024

**Date:** 2026-05-25
**From:** adr-placement-mechanism-repair-r1 Phase-R closeout
**Status:** Informational

## ADR-0024 disposition

Per T2b.1 of adr-placement-mechanism-repair-r1 Phase 2b:

- **Outcome:** Status-lift-only divergence detected between feature-scoped and canonical ADR-0024 (`status: Proposed` → `status: Accepted` only; body byte-identical).
- **Action:** `git rm working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md`. The canonical version at `adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md` (status: Accepted) is now the single source.
- **No archive write needed** (body identical; status-lift only).
- **Empty `adrs/` directory cleanup:** confirmed during T6.5 (the dir was already absent post-Phase 2 git rm).

## Cross-references

- adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md (canonical)
- adrs/ADR-0036-single-location-adr-placement.md (canonical placement invariant)
- working/feature/adr-placement-mechanism-repair-r1/migration-log.md (Phase 2b row)
