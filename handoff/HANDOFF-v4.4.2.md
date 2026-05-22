# Feature-Pipeline v4.4.2 — Handoff

**Run-id:** docs-patch-r1-20260521
**Completed:** 2026-05-21
**Status:** Accepted (pending Final Approval Gate)

## What v4.4.2 contains

The v4.4.2 release is a **PATCH-PATCH bump over v4.4.1** — pure documentation backfill plus one skill-design ADR. No code changes, no audit-machinery changes, no KB content changes.

Three actions:

1. **v4.4.0 planning artifacts copied into repo at canonical location.** All 25 artifacts from the frontend-design-knowledge-r1 planning workspace (intent-clarification, PRD, research plan, research notes, codebase analysis, synthesis, per-layer design, blueprint, plan, acceptance-tests, phase-validators, tasks.json, audit issues JSONs, checkpoint, feature-scoped ADR-0024) now live at `working/feature/frontend-design-knowledge-r1/` in the repo, matching the discipline documented in `KB-documentation-criteria/references/disciplines/design-composition.md`.

2. **v4.4.1 lightweight planning artifacts authored.** Six new documents at `working/feature/audit-machinery-fixes-r1/`: intent-clarification, prd-v1, blueprint-v1, plan-v1, acceptance-tests, phase-validators. Plus feature-scoped copy of ADR-0026. Uses the PATCH-scope shortcut per ADR-0023 (skips Discovery / Synthesis / per-layer Design / Architecture Audit / Cross-Audit / Reconciliation / Task Decomposition).

3. **ADR-0027 authored.** Documents the pipeline skill-design gap that allowed v4.4.0's artifacts to not land in the deliverable archive. Proposes three improvements: explicit `cwd` precondition in the orchestrator; new `finalize-deliverable-packager` sub-agent; deliverable-archive validator extending `shared-document-reviewer`. Targets v4.6.0 or alongside v4.5.0.

## What was missing before v4.4.2

The v4.4.0 archive shipped with 5 new KBs, 2 ADRs, 1 handoff doc, 1 continuation prompt — and **zero planning artifacts** at the canonical location. Same for v4.4.1: machinery edits + 1 ADR + 2 handoff docs, zero planning artifacts.

The discipline (Blueprint at `working/feature/<slug>/blueprint-v<N>.md`, etc.) was documented in the KBs. The gap was machinery-enforcement: nothing in the orchestrator's stages verifies the deliverable archive contains the canonical artifact set. ADR-0027 captures this for the future fix.

## Files in this handoff

### New planning artifacts (copied or authored)

**v4.4.0 frontend-design-knowledge-r1** (copied verbatim from planning workspace):

| Path | Source |
|------|--------|
| `working/feature/frontend-design-knowledge-r1/intent-clarification.md` (+ 2 versioned copies) | planning workspace |
| `working/feature/frontend-design-knowledge-r1/prd-v1.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/research-plan.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/research-notes/T-001` through `T-006.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/codebase-analysis.json` + `codebase-analysis-report.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/synthesis.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/cc-design.md` + `cc-dependencies.json` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/blueprint-v1.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/plan-v1.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/acceptance-tests.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/phase-validators.md` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/tasks.json` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/architecture-audit-issues.json` + `cross-artifact-audit-issues.json` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/checkpoint.json` | planning workspace |
| `working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md` | planning workspace |

**v4.4.1 audit-machinery-fixes-r1** (newly authored; PATCH-scope shortcut):

| Path | Status |
|------|--------|
| `working/feature/audit-machinery-fixes-r1/intent-clarification.md` | authored in v4.4.2 |
| `working/feature/audit-machinery-fixes-r1/prd-v1.md` | authored in v4.4.2 |
| `working/feature/audit-machinery-fixes-r1/blueprint-v1.md` | authored in v4.4.2 |
| `working/feature/audit-machinery-fixes-r1/plan-v1.md` | authored in v4.4.2 |
| `working/feature/audit-machinery-fixes-r1/acceptance-tests.md` | authored in v4.4.2 |
| `working/feature/audit-machinery-fixes-r1/phase-validators.md` | authored in v4.4.2 |
| `working/feature/audit-machinery-fixes-r1/adrs/ADR-0026-*.md` | copied from `adrs/` |

### New ADR

| Path | Purpose |
|------|---------|
| `adrs/ADR-0027-pipeline-skill-design-gap-deliverable-archive.md` | Documents the gap; proposes 3 improvements; targets v4.6.0 |

### Preserved artifacts

All v4.4.1 artifacts unchanged. v4.4.1's HANDOFF + CONTINUE_PROMPT remain accurate for the audit-machinery state.

## Decisions carried forward unchanged

- All v4.4.x audit-machinery fixes (ADR-0026)
- All v4.4.0 corpus expansion (ADR-0024)
- All baseline reductions (BLOCKER 95 → 77; summary/line alignment)
- ADR-0025 defect 1 still deferred to v4.5.0

## What's next — three recommended threads

**Thread 1: Formalized execution pipeline** (user's originally-stated priority). Independent of pipeline-machinery work.

**Thread 2: v4.5.0 marker-backfill run.** Address remaining ADR-0025 defect 1 (~25 pedagogical false-positives in existing platform KBs).

**Thread 3: v4.6.0 pipeline skill-design improvements.** Implement ADR-0027's three fixes (cwd precondition; packager agent; deliverable-archive validator). Recommended before or alongside Thread 1, since Thread 1 will compound the gap if not.

Recommended ordering: Thread 3 → Thread 2 → Thread 1. Thread 3 fixes the discipline-enforcement gap; Thread 2 cleans residual baseline noise; Thread 1 stands on a more solid foundation.
