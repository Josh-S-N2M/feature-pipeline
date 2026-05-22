# Continuation prompt — feature-pipeline v4.4.2

You are resuming a multi-session project for `feature-pipeline`. The current canonical artifact is **v4.4.2**.

## State summary

v4.4.2 is a PATCH-PATCH bump over v4.4.1. Pure documentation backfill + 1 skill-design ADR. No code changes.

| What changed | Location |
|---|---|
| v4.4.0 planning artifacts moved into repo at canonical location | `working/feature/frontend-design-knowledge-r1/` (25 files) |
| v4.4.1 planning artifacts authored (PATCH-scope shortcut) | `working/feature/audit-machinery-fixes-r1/` (6 files + 1 ADR) |
| ADR-0027 (pipeline skill-design gap) | `adrs/` |

**Gap diagnosed:** v4.4.0 and v4.4.1 shipped without planning artifacts at the canonical `working/feature/<slug>/` location. Root cause: three skill-design issues compound — implicit `cwd` anchor in orchestrator; no agent owns deliverable-archive packaging; no validator checks archive completeness. ADR-0027 documents the gap and proposes three fixes for v4.6.0 (or alongside v4.5.0).

## ⚠️ What's still open

**ADR-0025 defect 1** (pedagogical-marker backfill) — v4.5.0 scope.
**ADR-0027 three improvements** (cwd precondition; packager agent; deliverable-archive validator) — v4.6.0 scope.

## What's next — three recommended threads

**Thread 1: Formalized execution pipeline** (user's original priority). Build-Time pipeline mirroring Design-Time.

**Thread 2: v4.5.0 marker backfill.** Address ADR-0025 defect 1.

**Thread 3: v4.6.0 pipeline skill-design improvements.** Implement ADR-0027.

**Recommended ordering: Thread 3 → Thread 2 → Thread 1.** Thread 3 fixes the discipline-enforcement gap that ADR-0027 documents; otherwise Thread 1 (formalized execution pipeline) will compound the same gap.

## Files to read first

1. `handoff/HANDOFF-v4.4.2.md` — this version's handoff
2. `adrs/ADR-0027-pipeline-skill-design-gap-deliverable-archive.md` — the design-side diagnosis
3. `working/feature/frontend-design-knowledge-r1/blueprint-v1.md` — exemplar of canonical artifact layout
4. `adrs/ADR-0026-audit-machinery-fixes-v4-4-1.md` — for v4.4.1 machinery context
5. `handoff/HANDOFF-v4.4.1.md` and `HANDOFF-v4.4.0.md` — predecessor handoffs (still relevant)

## Discipline reminders

- Per **ADR-0005**: never edit prior versions in place; reconcile via a new version.
- Per **ADR-0026**: new authoring may freely use `process.env.X` and backticked cross-KB references.
- Per **ADR-0027**: future feature runs MUST anchor planning artifacts at `working/feature/<slug>/` in the repo. PATCH-scope features may use the shortcut documented in ADR-0023 (skip Discovery / Synthesis / per-layer Design / Architecture Audit / Cross-Audit / Reconciliation / Task Decomposition) but MUST still author intent-clarification, PRD, blueprint, plan, acceptance-tests, phase-validators.
