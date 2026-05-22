---
feature_slug: audit-machinery-fixes-r1
version: 1.0.0
status: approved
approved_at: 2026-05-21T02:00:00Z
gate_passed: 1
scope_class: PATCH
---

# Intent Clarification — audit-machinery-fixes-r1

## User intent

> "Fix the audit-machinery defects identified during the v4.4.0 (frontend-design-knowledge-r1) execution. Re-baseline the audit and revert the v4.4.0 workarounds since the machinery will handle them cleanly. Package as v4.4.1 (PATCH bump — pipeline structure unchanged)."

User signal type: continuation. Defects were enumerated in ADR-0025 (authored as part of v4.4.0); this feature is the remediation.

## Scope

In-scope:

- The four defects from ADR-0025: DE-2 false-match on `process.env.X`; BACKTICK_PATH cross-KB resolution; pedagogical-marker pre-triage scope; summary count vs line count divergence.
- Reverting two v4.4.0 workarounds (bracket-notation `process['env']['X']` and rewritten cross-KB references) once the machinery handles them.
- Documenting the fixes (ADR-0026).
- Re-running the baseline cc-audit to verify reduction.

Out of scope:

- ADR-0025 defect 1 (pedagogical-marker backfill in existing platform KBs). Identified during scoping as substantial standalone work (6-10 platform KB files needing per-block fence wrapping). Deferred to v4.5.0 as its own feature run.
- New KB content, agent surface changes, Blueprint structure changes. v4.4.1 is pure machinery; no functional pipeline change.

## Acceptance signal

- BLOCKER baseline strictly decreases from v4.4.0's 95.
- Summary count and line count agree exactly after fixes.
- v4.4.0 workarounds are reverted; the natural authoring patterns now produce no false positives.
- ADR-0026 documents the fixes with regex test cases and validation methodology.

## Discovery shortcut

This is a small machinery patch following an integration-test finding. The full 12-stage pipeline is not warranted. Justification per ADR-0023 (integration-test refinements): defects identified during prior execution with concrete remediation guidance documented in the source ADR (ADR-0025) qualify for the shortened discipline.

Stages executed in shortened form:

- Intent Clarification (this document)
- PRD (single doc; covers what + why + AC)
- Blueprint (single doc; covers approach + ADR-0026 link)
- Plan (single doc; covers ordered task list)
- Acceptance Tests (single doc; ties to AC in PRD)
- Phase Validators (single doc; covers per-fix validation)

Skipped (justified for PATCH-scope machinery work):

- Discovery Planning / Research / Synthesis — root causes already in ADR-0025
- Per-layer Design — no architectural surface change
- Architecture Audit — no architectural surface change
- Cross-Artifact Audit — single-domain feature
- Task Decomposition — Plan tasks are atomic enough at scope this small
- Reconciliation — no reviewer cycle needed

## ADRs

- **ADR-0025** (inherited): Pipeline-machinery defects from integration test #2 (authored in v4.4.0; provides the defect taxonomy this feature remediates).
- **ADR-0026** (authored): Audit-machinery fixes — closes ADR-0025 defects 2, 3, 4.
