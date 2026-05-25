---
doc_type: phase-quality-report
feature_slug: adr-placement-mechanism-repair-r1
phase: P-2
phase_scope: [P-2a, P-2b, P-2c, P-2d]
verdict: NEEDS_RECONCILIATION
created: 2026-05-25
---

# Phase Quality Report — P-2 (Consolidated: P-2a + P-2b + P-2c + P-2d)

## Verdict

**NEEDS_RECONCILIATION**

Driven exclusively by **F-P2-VAL-1** (MAJOR, revisable): 5 tombstone files lack the literal ADR-0036 citation that Blueprint §Migration map FR-8c template requires. All other structural and dimensional checks PASS.

## 5-Dimensional Status (Contract 2)

| Dimension | Status | Notes |
|-----------|--------|-------|
| tests | PASS | No test execution in this phase (Phase 2 is filesystem reconciliation). |
| audits | PASS | (stub — codespaces audits unavailable; not measured rather than clean per Q-CC-4) |
| validator | NEEDS_RECONCILIATION | F-P2-VAL-1 MAJOR: 5 tombstones missing ADR-0036 citation (PV-2c.C3). |
| discipline | PASS | All discipline conventions honored (ADR-0036 single-location, ADR-0053 renumber algorithm, ADR-0055 archive-wins policy). |
| scope_deviations | PASS | 5 task-spec-staleness deviations surfaced (F-P2-SD-1..5), all named-exemption / actual-filename-used per ADR-0033. None block execution. |

## Phase Validator Results

### PV-2a (Byte-identical dedupes) — PASS

- **C1** 12/12 feature-scoped copies deleted (IDs 0026, 0028-0031, 0037-0043).
- **C2** 12/12 canonical retained at adrs/.
- **C3** 12 byte-equality + deletion rows in migration-log Phase 2a section.

### PV-2b (Status-lift dedupe + renumber) — PASS

- **C1** ADR-0024 feature-scoped copy deleted.
- **C2** ADR-0024 canonical at status Accepted.
- **C3** Outcome A (zero non-frontmatter divergence) recorded.
- **C4** ADR-0044 → ADR-0051 renumber complete (canonical present, source absent).
- **C5** ADR-0045 → ADR-0052 renumber complete (symmetric).
- **C6** `original_id: ADR-0044` / `original_id: ADR-0045` provenance present in renumbered files.
- **C7** `id: ADR-0051` / `id: ADR-0052` frontmatter confirmed.
- **C8** Git history preserved (rename status `RM` in git status; `git log --follow` chain inferable).

### PV-2c (Feature-scoped relocations) — NEEDS_RECONCILIATION

- **C1** PASS — all 5 ADRs 0046-0050 at canonical adrs/.
- **C2** PASS — 5 .tombstone files present at working/feature/issue-capture-mechanism-r1/adrs/.
- **C3** **MAJOR FAIL** — tombstones contain canonical move, original location, and git-log provenance pointer, but lack the literal ADR-0036 citation. See F-P2-VAL-1.
- **C4** PASS — no .md files remain for 0046-0050 in feature dir.
- **C5** PASS — git history preserved (R renames).
- **C6** PASS — 5 rows in Phase 2c section of migration log.

### PV-2d (adrs-migrated/ consolidation) — PASS

- **T2d.1** (no-collision): 9 IDs 0001-0006, 0008-0010 each at exactly 1 canonical file.
- **T2d.2** (archive-wins): 7 archives at adrs/superseded/ADR-NNNN-pre-consolidation-canonical.md (0011-0017); 7 canonical files updated; all 7 carry `superseded_by_consolidation` + `superseded_canonical_archived_to` frontmatter per ADR-0055 v1.0.1.
- **T2d.3** (canonical-wins): ADR-0018 canonical-only; both archive variants git-rm'd.
- **T2d.4** (closeout): adrs-migrated/ directory removed (PASS); ADR-0007 canonical-only with AA-003 v1-superseded inclusion resolved.

## Critical Structural Checks (orchestrator-requested)

| Check | Result |
|-------|--------|
| adrs-migrated/ no longer exists | PASS |
| adrs/superseded/ has 7 ADR-NNNN-pre-consolidation-canonical.md files | PASS |
| adrs/ contains renumbered ADR-0051 + ADR-0052 with proper original_id frontmatter | PASS |
| adrs/ contains ADRs 0046-0050 at canonical | PASS |
| working/feature/issue-capture-mechanism-r1/adrs/ has 5 .tombstone + 0 .md | PASS |
| T2a.1 source dirs (4 sub-features) empty of .md | PASS |
| Migration-log has rows for every task | PASS (12 + 3 + 5 + 18 = 38 Phase-2 rows) |

## Findings

### F-P2-VAL-1 — MAJOR (validator, revisable)

**PV-2c.C3 — Tombstone template gap**. All 5 tombstones at `working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}.tombstone` contain the canonical move, original location, and git-log provenance pointer, but NONE carry the literal ADR-0036 citation that the Blueprint FR-8c template specifies.

**Remediation**: Append a 4th line `Canonical placement per ADR-0036 (single-location ADR placement).` to each of the 5 tombstones. <2 minutes.

### F-P2-SD-1..5 — MINOR (scope_deviations, non-blocking)

Five task-spec-staleness deviations surfaced by producers across T2b.1, T2c.1, T2d.1, T2d.2, T2d.3. In each case the task spec referenced a filename slug (or `-final` suffix) that did not match disk reality. Producers correctly adapted using actual filenames; outcomes architecturally equivalent. These are task-spec maintenance items per ADR-0033, not execution failures.

## Audit-Counter Delta (Contract 3)

```
gating: informational (default)
baseline_ref: phase-quality-report-P-1.json

per_domain_delta:
  tests:            0 -> 0
  audits:           0 -> 0 (stub)
  validator:        0 -> 1  (F-P2-VAL-1 MAJOR revisable)
  discipline:       0 -> 0
  scope_deviations: 3 -> 8  (5 new task-spec-staleness, all named-exemption)

aggregate_delta:  0 -> 6
audit_severity_breakdown: null (reserved per Q-CC-3)
```

**Interpretation**: Per Q-CC-3 per-domain primacy, tests/audits/discipline held at 0 (no regression). Validator gained 1 MAJOR revisable finding. Scope_deviations grew by 5, all classified named-exemption / actual-filename-used — task-spec staleness adapted by producers using actual disk filenames. Aggregate 0→6 is dominated by scope_deviations + 1 validator MAJOR. Verdict NEEDS_RECONCILIATION is driven exclusively by F-P2-VAL-1, a 5-file append-only edit.

## Rollup Rationale

Per Contract 2 rollup rule: revisable finding in validator dimension (F-P2-VAL-1, blocking=false) → validator dimension NEEDS_RECONCILIATION → phase verdict NEEDS_RECONCILIATION. All other 4 dimensions PASS. Scope_deviations dimension is PASS because all 5 deviations were correctly surfaced and resolved via named-exemption (not silently absorbed elsewhere).

## Reconciliation Required

| Finding | Action | Files | Effort |
|---------|--------|-------|--------|
| F-P2-VAL-1 | Append ADR-0036 citation line | 5 tombstones in `working/feature/issue-capture-mechanism-r1/adrs/` | <2 minutes |

After reconciliation, re-run PV-2c.C3 grep loop to confirm.

## Phase Completion Summary

- **Tasks completed**: T2a.1, T2b.1, T2b.2, T2c.1, T2d.1, T2d.2, T2d.3, T2d.4
- **git rm**: ~44 deletions (12 dedupes + 1 ADR-0024 + 18 pre-naming/pre-template variants + 7 canonical-pre-archive + 2 ADR-0018 archive + 4 ADR-0007 variants)
- **git mv**: ~21 renames (2 renumber + 5 issue-capture relocations + 9 no-collision + 7 archive moves)
- **Tombstone writes**: 5 (ADR-0046..0050)
- **Archive writes**: 7 (ADR-0011..0017-pre-consolidation-canonical.md)
- **Frontmatter edits**: 16 (2 renumber + 7 archived + 7 canonical with superseded_by_consolidation)
- **Final state**: 55 canonical ADRs at adrs/ (0001-0055); 7 pre-consolidation archives at adrs/superseded/; adrs-migrated/ removed; 5 tombstones at issue-capture working dir.
