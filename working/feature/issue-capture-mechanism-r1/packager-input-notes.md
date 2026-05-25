---
id: PACKAGER-INPUT-issue-capture-mechanism-r1
doc_type: packager-input-notes
status: complete
feature_slug: issue-capture-mechanism-r1
generated: 2026-05-25
generated_by: execute-task-code-producer (T7.10)
consumed_by: finalize-deliverable-packager (Stage 13)
---

# Packager Input Notes — `issue-capture-mechanism-r1`

## 1. Deviation summary

The 7 new ADRs authored by this feature run (ADR-0051 through ADR-0050) remain at
`working/feature/issue-capture-mechanism-r1/adrs/` rather than the canonical `/adrs/`
root-level location prescribed by ADR-0036. This is a deliberate, user-accepted deviation
per the Architecture Audit cycle 1 escalation (I-AA-001).

## 2. Authoritative evidence

Root-cause analysis: `Issues/adr-placement-rootcause/analysis.md` (post-Phase-3 migrated
path; previously `Issues/analysis-adr-placement-rootcause.md`). The analysis documents
that ADR-0036 (accepted 2026-05-22) retired the dual-location ADR convention and mandated
a single canonical location at `/adrs/`, but the amendment was never propagated to the 4
files that drive ADR placement and verification (orchestrator SKILL.md, design-composer.md,
finalize-deliverable-packager.md, shared-document-reviewer.md DeliverableArchive check).
The current feature inherits this gap.

## 3. User acceptance

Per `checkpoint.json` gate_history:
`{"gate": "i_aa_001_user_escalation", "decision": "accepted_deviation",
"timestamp": "2026-05-24T00:30:00Z", "user_notes": "Option A: Accept ADR placement
deviation."}`. The user chose Option A: keep the 7 ADRs under
`working/feature/<slug>/adrs/` for this run; defer the location-normalization remediation
to a future drift-remediation feature (slug TBD).

## 4. Packager direction

**finalize-deliverable-packager (Stage 13) follows the CURRENT OPERATIONAL CONVENTION**
(`working/feature/<slug>/adrs/`) for this run's 7 new ADRs:

- DO follow current convention: the 7 ADRs (ADR-0051 through ADR-0050) ship at
  `working/feature/issue-capture-mechanism-r1/adrs/`
- DO NOT relocate them to `/adrs/` — the user's Option A scope decision explicitly
  accepts the current location
- DO NOT flag the placement as a packaging error in `packager-report.json` — the
  deviation is user-accepted
- DO NOT block on ADR-0036's canonical-location assertion — that assertion is the subject
  of the future drift-remediation feature, not this one

## 5. Future remediation scope

A separate drift-remediation feature (slug TBD) is responsible for:

- Re-affirming or revising ADR-0036's single-canonical-location assertion
- Bulk-relocating any historical ADRs whose location violates the affirmed convention
- Propagating the affirmed convention to the 4 files identified by
  `Issues/adr-placement-rootcause/analysis.md`

That feature is OUT OF SCOPE for this run. The packager's job for this run is to ship the
archive without re-litigating the deviation.

## Cross-references

- Root-cause analysis: `Issues/adr-placement-rootcause/analysis.md`
- ADR-0036 (the mandate that drifted): `adrs/ADR-0036-*.md`
- The 7 ADRs at the user-accepted location:
  `working/feature/issue-capture-mechanism-r1/adrs/ADR-{0044..0050}-*.md`
- Checkpoint gate history: `working/feature/issue-capture-mechanism-r1/checkpoint.json`
  (gate `i_aa_001_user_escalation`)
