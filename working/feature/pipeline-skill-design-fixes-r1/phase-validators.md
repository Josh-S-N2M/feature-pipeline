---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/pipeline-skill-design-fixes-r1/plan-v1.md
approved_at: 2026-05-21T05:30:00Z
gate_passed: 5
---

# Phase Validators — pipeline-skill-design-fixes-r1

## Phase 1 — Spec authoring (T-1)

**Exit criteria.**
- `deliverable-archive-spec.md` written.
- AC-8 verified: file exists, `## Contents` H2 present.
- AC-9 verified: FULL / MINOR / PATCH sections present.

**Failure handling.** If spec drafting reveals an ambiguity in ADR-0023's scope-class taxonomy, escalate before continuing.

## Phase 2 — Packager authoring (T-2)

**Exit criteria.**
- `finalize-deliverable-packager.md` written.
- AC-3 verified: file exists, frontmatter parses.
- AC-4 verified: all 7 body sections present.

## Phase 3 — Orchestrator edits (T-3, T-4)

**Exit criteria.**
- Precondition section added to SKILL.md.
- Stage 1 procedure extended with verification step.
- Stage 13 added to sequence.
- AC-1, AC-2, AC-5 verified.

**Failure handling.** Edits must preserve all existing orchestrator stages unchanged.

## Phase 4 — Reviewer extension (T-5)

**Exit criteria.**
- `DeliverableArchive` doc_type added to taxonomy comment + body section.
- AC-6, AC-7 verified.

**Failure handling.** Extension must be additive; existing doc_types (Plan, Blueprint, IntentClarification, etc.) must continue to work unchanged.

## Phase 5 — Retroactive validation (T-6)

**Exit criteria.**
- Manual validation against v4.4.2's `working/feature/frontend-design-knowledge-r1/` produces a clean verdict for FULL scope.
- Manual validation against v4.4.2's `working/feature/audit-machinery-fixes-r1/` produces a clean verdict for PATCH scope.
- AC-10, AC-11 verified.

**Failure handling.** If the validator flags issues in v4.4.2's archives, either (a) fix the spec if it over-specifies, or (b) document the issue in ADR-0028 as a known gap requiring follow-up.

## Phase 6 — Documentation closure (T-7, T-8)

**Exit criteria.**
- ADR-0028 authored.
- HANDOFF-v4.5.0.md authored.
- CONTINUE_PROMPT-v4.5.0.md authored.
- AC-12 verified.

## Phase 7 — Audit + Package (T-9, T-10)

**Exit criteria.**
- cc-audit run; no new BLOCKERs vs v4.4.2 baseline (BLOCKER 77 expected unchanged).
- v4.5.0 zip packaged with correct structure.
- File presented to user.

**Failure handling.** New BLOCKERs introduced → investigate before packaging.
