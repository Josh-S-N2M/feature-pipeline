<!-- Authored by finalize-deliverable-packager 2026-05-21T21:37:00Z; companion to handoff/HANDOFF-v4.6.0-planning-complete.md. Gate 6 confirmed 2026-05-21T21:40:00Z. -->

# Continuation prompt — audit-findings-remediation-r1 (planning complete; execution pending)

You are resuming a multi-session project for `feature-pipeline`. The current canonical repo version is **v4.5.0**. The feature `audit-findings-remediation-r1` has **completed its planning pipeline** (all authoring + audit + reconciliation stages converged) and is **ready for execution dispatch** toward shipping v4.6.0.

## TL;DR — where you are

You're running the project's own feature pipeline on a feature whose goal is to drive the cc-audit baseline (77 BLOCKER / 42 MAJOR / 29 MINOR = 148 findings) to zero, under a discipline (mechanism α) that prevents pedagogical markers from becoming silent suppression.

- **All planning + audit stages complete.** Read `handoff/HANDOFF-v4.6.0-planning-complete.md` for full state.
- **Final human gate (Final Approval) is the only remaining gate before execution begins.** If you're in the session right after Gate-6 approval, you're executing.
- **`tasks.json` is the execution input.** 34 work units, critical path identified, parallelization opportunities flagged.
- **No implementation code has changed.** The 148-finding baseline still stands in the repo; execution closes it.

## What to read first

1. `handoff/HANDOFF-v4.6.0-planning-complete.md` — full planning state, deviations resolved, what to do next.
2. `working/feature/audit-findings-remediation-r1/tasks.json` — the 34-task DAG. Read the critical_path and parallelization_summary fields.
3. `working/feature/audit-findings-remediation-r1/phase-validators-v1.1.0.md` — gate criteria for each Plan phase. PV-0 runs first; PV-6 last.
4. `working/feature/audit-findings-remediation-r1/plan-v1.2.0.md` — the canonical plan (v1.2.0 after 2 reconciliation cycles).

## Critical disciplines this feature operates under

- **ADR-0005** — Append-only supersession. Never edit prior versions in place.
- **ADR-0021** — 4-cycle reconciliation hard cap (execution gets a fresh budget; planning used 2 cycles).
- **ADR-0023** — Plan owns task sequencing.
- **ADR-0027** — Working directory must be repo root.
- **ADR-0028** — No pipeline-stage references by number. Stage names only. (Scope extends to feature-internal artifacts per user 2026-05-21 confirmation.)
- **ADR-0029** — Surface every deviation; "1 could be major"; no silent absorption.
- **ADR-0030** — Mechanism α: inline justification required per pedagogical marker. The feature being built.
- **ADR-0031** — `auditing-shared` is canonical home for cross-audit utilities.

## Open items requiring execution-time judgment

- **T025 is xlarge** (32 KB files with new markers). Split into 4 sub-tasks (T025-A through T025-D) before scheduling per tasks.json open_items_for_orchestrator.
- **T029 may surface a preloaded skill that fails its own audit.** Per Plan OI-3 + ADR-0029: surface the deviation; user decides PRD-amend vs Won't-Have for this feature.
- **T020 + T021 Option A vs Option B** (per Plan D-7): default Option A (delete + subprocess); Option B (3-line shim) as per-callsite fallback.
- **OBS-PLAN-001, OBS-CA-001/002, OBS-AUDIT-BLIND-001** in `observations.md` are flagged for follow-on improvement of plan-author + review-cross-artifact-auditor agents. NOT in scope for this feature; queue as a follow-on feature.

## First action on resumption

If Final Approval Gate has been passed:
1. Run T001 (capture baseline audit) — confirm it matches the 77/42/29 baseline; if drift, surface per ADR-0029 before continuing.
2. Dispatch T002, T003 in parallel.
3. Begin Phase 1 work: T004 → T005 || T006 → T007 → T008 (intermediate audit capture per I-CA-002 fix) → T009 (mechanism-α wired).

If Final Approval Gate has NOT been passed:
1. Read `packager-report.json` open_items_for_gate_6_human_review section.
2. Surface the 6 items to the user; await disposition.

## What success looks like at v4.6.0 ship

- Final audit: BLOCKER=0, MAJOR≤1 (the named-exempt Bash MAJOR), MINOR<29.
- All 32 ACs verified pass in `acceptance-verification-matrix.md`.
- Cross-Artifact Audit (execution-time round) converges to PASS.
- Final `packager-report.json` verdict PASS, no MAJOR findings.
- Successor HANDOFF (HANDOFF-v4.6.0-final.md or just HANDOFF-v4.6.0.md depending on naming-convention decision) authored describing the realized changes.
