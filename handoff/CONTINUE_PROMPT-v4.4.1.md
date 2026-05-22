# Continuation prompt — feature-pipeline v4.4.1

You are resuming a multi-session project for `feature-pipeline`. The current canonical artifact is **v4.4.1**.

## State summary

v4.4.1 is a PATCH bump over v4.4.0. Pure machinery fixes; no content, agent, or Blueprint changes.

| What changed | File | Closes |
|---|---|---|
| DE-2 regex hardened (path-component context) | `auditing-skills/scripts/scan_security.py` | ADR-0025 defect 2 |
| `normalize()` handles KB- prefixed paths | `auditing-skills/scripts/lint_references.py` | ADR-0025 defect 3 |
| Depth-2 check scoped to within-skill | `auditing-skills/scripts/lint_references.py` | (bonus during testing) |
| Summary uses `final_severity` | `auditing-cc-configs/scripts/verdict_compute.py` | ADR-0025 defect 4 |

**Baseline reduction:** BLOCKER 95 → 77 (-18); MAJOR 71 → 69 (-2); MINOR 28 → 28.

**v4.4.0 workarounds reverted:** `process.env.X` natural form restored; cross-KB references restored to backticked-full-path form. The machinery now handles both cleanly.

## ⚠️ What's still open

**ADR-0025 defect 1 (pedagogical-marker backfill in existing platform KBs)** is the largest remaining baseline contributor. 25+ real pedagogical-content findings need `pedagogical_sections:` declarations + `audit-example` fence wrapping in KB-cc-platform, KB-codespaces-platform, KB-github-actions-platform, KB-codespaces-design.

Recommended as **v4.5.0** — a marker-backfill feature run.

## What's next — two recommended threads

**Thread 1: Formalized execution pipeline** (user's original stated next priority). Build-Time pipeline mirroring the Design-Time pipeline's 12-stage discipline.

**Thread 2: v4.5.0 marker-backfill run.** Address remaining ADR-0025 defect 1.

Both threads are independent.

## Files to read first

1. `handoff/HANDOFF-v4.4.1.md` — this version's handoff
2. `adrs/ADR-0026-audit-machinery-fixes-v4-4-1.md` — what changed and why
3. `adrs/ADR-0025-pipeline-machinery-defects-integration-test-2.md` — the original four defects; defects 2-4 are now closed
4. `handoff/HANDOFF-v4.4.0.md` — prior version's handoff (still relevant for the corpus state)

## Discipline reminders

- Per **ADR-0005**: never edit prior versions in place; reconcile via a new version.
- Per **ADR-0026**: new authoring may freely use `process.env.X` and backticked cross-KB references — the machinery handles both.
- AC-FR-5-b verification may use either JSON summary counts OR line-text comparison; they now agree.
