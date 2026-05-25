# Notification: ADR Placement Repair (adr-placement-mechanism-repair-r1) — Multiple Impacts to issue-capture-mechanism-r1 ADRs

**Date:** 2026-05-25
**From:** adr-placement-mechanism-repair-r1 Phase-R closeout
**Status:** Informational

## Impacts to your run

### 1. FR-8c — ADRs 0046–0050 relocated to canonical

Per T2c.1 of adr-placement-mechanism-repair-r1 Phase 2c:
- 5 ADRs (0046, 0047, 0048, 0049, 0050) git-mv'd from `working/feature/issue-capture-mechanism-r1/adrs/` to canonical `adrs/`.
- Tombstone files written at `working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN.tombstone` with redirect notes.
- 5 .tombstone files persist in your run's `adrs/` directory (intentional; provenance retained).

### 2. FR-8b — ADR-0044 + ADR-0045 renumbered to ADR-0051 + ADR-0052 per ADR-0053

Per T2b.2 of adr-placement-mechanism-repair-r1 Phase 2b:
- Original IDs ADR-0044 (per-issue-folder-model) and ADR-0045 (three-doctypes-preserved) collided with canonical ADR-0044 (flatten-execution-dispatch-hierarchy) and ADR-0045 (subagent-agent-tool-grant-prohibition).
- Per ADR-0053 v1.0.1 renumbering collision resolution algorithm (baseline = max(canonical) + 1 = 0051):
  - ADR-0044-per-issue-folder-model → ADR-0051-per-issue-folder-model (now at canonical `adrs/`)
  - ADR-0045-three-doctypes-preserved → ADR-0052-three-doctypes-preserved (now at canonical `adrs/`)
- Frontmatter of new canonical files carries `original_id`, `renumbered_per: ADR-0053`, `renumbered_at: 2026-05-25` provenance fields.

### 3. FR-9 — 197 bare-ID rewrites across your run's design artifacts

Per T3.3 of adr-placement-mechanism-repair-r1 Phase 3:
- 194 bare-ID rewrites (ADR-0044→ADR-0051: 158 occurrences; ADR-0045→ADR-0052: 41 occurrences) performed across 41 files repo-wide, including many files in `working/feature/issue-capture-mechanism-r1/`.
- T3.1 pre-classified 481 occurrences (197 feature-meaning → rewrite; 284 canonical-meaning → preserve as ADR-0044/0045 references to the canonical feature-pipeline orchestrator decisions).
- 0 ambiguous; 0 classification overrides on re-read.

## Empirical confirmation

- Validator scan: PASS (zero findings; 30ms) per T6.4.
- 3-surface negative-path harness: PASS (all surfaces block fixture) per T6.7.

## Cross-references

- adrs/ADR-0036, ADR-0053, ADR-0054, ADR-0055 (canonical decisions)
- working/feature/adr-placement-mechanism-repair-r1/migration-log.md (full execution log)
- working/feature/adr-placement-mechanism-repair-r1/bare-id-inventory.json (per-occurrence classification)
