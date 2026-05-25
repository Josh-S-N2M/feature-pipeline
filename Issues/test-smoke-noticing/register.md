---
id: REGISTER-test-smoke-noticing
version: 0.2.0
doc_type: issue-register
status: wontfix-with-rationale
feature_slug: issue-capture-mechanism-r1
generated: 2026-05-25
generated_by: issue-capture-author (T7.1 smoke test)
since: 2026-05-25
wontfix_rationale: Synthetic artifact produced by the T7.1 Plan B live-session smoke test. This file served its purpose (verifying the create-mode write path of the issue-capture-author mechanism). No real issue is tracked here. Kept in place per NFR-6 no-deletion invariant; transitioned to wontfix-with-rationale to signal no further action is required.
decided_at: 2026-05-25
---

# Issue Register — `test-smoke-noticing`

## Contents

Section completion checklist — mark each box `[x]` when the corresponding section is complete.

- [x] Status
- [x] Purpose
- [x] Entries
- [x] Cross-links
- [x] Resolution / supersession notes (if applicable)

## Status

wontfix-with-rationale — 2026-05-25

## Purpose

Smoke-test register produced by the T7.1 Phase 7 verification step for the `issue-capture-mechanism-r1` feature run. This register records the single smoke-test event (the `/capture-issue test-smoke-noticing` invocation) as a minimal single-item capture. It is a synthetic test artifact: its sole purpose is to verify that the `issue-capture-author` sub-agent can produce a structurally valid `issue-register` file at the canonical `Issues/<topic-slug>/register.md` path with correct frontmatter per `issue-doctypes-spec.md`.

**Counts:** 1 distinct item across 1 category. Zero are blocking any gate or milestone.

---

## Entries

### A. Smoke-test events

| ID | Item | Source | Why deferred / noticed | Re-examination condition | Forgetting risk |
|---|---|---|---|---|---|
| **A-1** | T7.1 create-mode smoke test: `issue-capture-author` successfully wrote `Issues/test-smoke-noticing/register.md` with canonical frontmatter (id, version, doc_type, status, feature_slug, generated, generated_by) per spec §4.1 | `/workspaces/feature-pipeline/Issues/test-smoke-noticing/register.md` | Captured as Phase 7 verification artifact for `issue-capture-mechanism-r1`; the write confirms the create-mode workflow path is operational end-to-end | When this register is transitioned to a terminal state via the update-mode smoke test (T7.1 continuation) | Low — this is a synthetic test artifact; forgetting risk is intrinsically low |

---

## Cross-links

- `escalates_from`: (none — this is a root file; no prior analysis in this topic folder)
- `escalated_to`: (none — no evolution has occurred at time of capture)
- `rolled_into_register`: (not applicable)

For the full bidirectional evolution discipline, see `ADR-0046` at
`working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-add-new-sibling-file-evolution.md`.

For the per-state companion-field authoritative table and 5-state lifecycle vocabulary, see:
- `ADR-0050` at `working/feature/issue-capture-mechanism-r1/adrs/ADR-0050-5-state-issues-vocabulary.md`
- `.claude/skills/KB-documentation-criteria/references/issue-doctypes-spec.md`

---

## Resolution / supersession notes

**Status: wontfix-with-rationale — decided 2026-05-25**

This file was a synthetic artifact produced by the T7.1 Plan B live-session smoke test. It has served its purpose (verifying the create-mode write path of the `issue-capture-author` mechanism). It is being transitioned to the `wontfix-with-rationale` terminal state to honor NFR-6 (no-deletion of `Issues/*.md` files) while signalling no further action is required. The underlying smoke-test event (A-1) is fully resolved by the successful write; there is no real issue to address.

---

*End of register.*
