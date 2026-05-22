---
feature_slug: audit-machinery-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/audit-machinery-fixes-r1/plan-v1.md
approved_at: 2026-05-21T02:25:00Z
gate_passed: 5
---

# Phase validators — audit-machinery-fixes-r1

This is a small machinery patch; phases are coarse-grained.

## Phase 0 — Reconnaissance (T-1, T-2)

**Exit criteria.**
- v4.4.0 baseline audit captured to `/tmp/v44-baseline.md`.
- Baseline BLOCKERs classified by type (DE-2 false-positives identified as a distinct subset; pedagogical content identified as a separate subset).
- Scope decision documented: defects 2-4 in scope; defect 1 deferred to v4.5.0.

**Deviation policy.** If baseline reveals defects beyond the four in ADR-0025, escalate before proceeding.

## Phase 1 — DE-2 regex hardening (T-3, T-4)

**Exit criteria.**
- Proposed regex validated against 14-case TP/FP matrix.
- 14/14 cases pass (8/8 true positives match; 6/6 false positives don't match).
- `scan_security.py:57-66` edit applied.

**Deviation policy.** If any test case fails, iterate on the regex before applying.

## Phase 2 — BACKTICK_PATH cross-KB fix + summary alignment (T-5, T-6)

**Exit criteria.**
- `lint_references.py` `normalize()` extended with KB- branch.
- `verdict_compute.py` `deductions_by_severity` reads `final_severity`.

## Phase 3 — Post-fix validation (T-7)

**Exit criteria.**
- Audit re-runs without error.
- Baseline BLOCKER count strictly decreased (AC-5 partial check).
- Summary count equals line count for BLOCKER (AC-4).

**Deviation policy.** If baseline did NOT decrease, the fix is wrong or insufficient. Investigate before continuing.

## Phase 4 — Workaround reversion + bonus fix (T-8, T-9, T-10, T-11)

**Exit criteria.**
- Workaround 1 reverted; `process.env.NODE_ENV` present in expected 2 sites.
- Workaround 2 reverted; cross-KB backticked-full-path present in expected 16 sites.
- Post-revert audit runs.
- If new MAJORs surface (as actually happened — depth-2 nesting fires on cross-KB refs), apply within-skill scoping fix.

**Deviation policy.** Document any deviation in the run log; if scope expands materially, escalate.

## Phase 5 — Final audit + ADR + packaging (T-12, T-13, T-14, T-15, T-16)

**Exit criteria.**
- Final audit `/tmp/v441-final2.md` captures the steady state.
- All 7 ACs verified.
- ADR-0026 authored.
- HANDOFF-v4.4.1.md + CONTINUE_PROMPT-v4.4.1.md authored.
- v4.4.1 zip packaged with correct structure.
- File presented to user.

**Deviation policy.** Any AC failure at this stage requires reconciliation cycle.
