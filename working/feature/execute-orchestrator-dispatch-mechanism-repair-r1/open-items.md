---
id: OI-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: open-items
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
version: 1.0.0
status: active
generated: 2026-05-24T02:45:00Z
generated_by: parent-orchestrator (Phase 0 / T0.2)
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/checkpoint.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/packager-report.json
  - Issues/analysis-adr-placement-rootcause.md
---

# Open Items: execute-orchestrator Dispatch Mechanism Repair (r1)

This document satisfies T0.2 (Phase 0 setup task) — recording the items the planning side surfaced as either (a) expected-issues-with-waiver-path, or (b) known-followups. Validated by PV-0.C3.

## OI-1 — Stage-13 packager BLOCKER (anticipated, did NOT fire)

**Planned status:** Phase 0 anticipated `PKG-BLOCKER-001-INVERSE` (canonical-only ADR placement absent the feature-scoped mirror copy) per `Issues/analysis-adr-placement-rootcause.md` §2.3 + §9.

**Observed status:** The packager **PASSED** with verdict `PASS` (25/25 artifacts present; 0 BLOCKER / 0 MAJOR / 0 MINOR / 1 INFO). The packager agent's runtime discretion to consult the current spec at `KB-documentation-criteria/references/deliverable-archive-spec.md` (which IS fully amended per ADR-0036, lines 136–150) overrode the agent file's static dual-location BLOCKER text. See `packager-report.json` for details.

**Waiver path that was prepared but not needed:** The user's Gate-7 disposition (`checkpoint.adr_placement_disposition.choice == "honor-adr-0036-canonical-root"`) documented the canonical-only choice. If the packager had blockered, the waiver would have cited this ratification + ADR-0036 + the spec lines 136–150.

**Disposition for this run:** No action required. Packager passed without invoking the waiver path.

**Disposition surfaced for `adr-placement-mechanism-repair-r1` follow-on:** The packager + reviewer agent FILE TEXTS still contain the retired dual-location check (per `Issues/analysis-adr-placement-rootcause.md` §10). The follow-on should align those texts with the spec. **Re-scoped from FULL to MINOR** per §10.

## OI-2 — `adr-placement-mechanism-repair-r1` follow-on (queued, re-scoped)

**Status:** Queued; not yet a feature folder.

**Original scope (per analysis §6):** FULL — 4 operator files + promotion mechanism + ADR migration.

**Revised scope (per analysis §10, post-this-run):** MINOR — delete retired dual-location BLOCKER text from `finalize-deliverable-packager.md:56–63` + `shared-document-reviewer.md:349`; change orchestrator + design-composer defaults for `output_adrs_dir` from feature-scoped to canonical-root. Estimated 4–6 hours.

**Trigger to advance:** User prioritization after this feature's execution lands.

## OI-3 — ADR-0045 audit-machinery extension (deferred)

**Status:** Deferred to a follow-on feature; placeholder pointer recorded in Plan T5.2.

**Scope:** The audit-machinery extension that enforces ADR-0045 ("sub-agents MUST NOT declare `Agent` in tools array") across `.claude/agents/*.md`. Would integrate with the auditing-subagents skill family.

**Interim:** Manual review per Plan T5.2 — reviewers check for `Agent` in `tools:` arrays during sub-agent authoring.

## OI-4 — F-7 fresh-session boundary (operational, encoded in tasks.json)

**Status:** Encoded as `tasks.json:T6.2.forced_session_boundary == true`.

**Action:** Operator must restart the Claude Code session between Phase 3 sub-agent edits and Phase 6 synthetic test feature run (T6.3). Plan §Cross-Phase Sequencing Constraint 3 documents the requirement; PV-6.C3 validates the restart artifact.

**Rationale:** F-7 finding (memory: `project_f7_mid_session_agent_registry`) — the harness does not register mid-session agent files. For THIS feature, this is defensive (T6.1 design vacuously satisfies AC-FR-6-d by NOT authoring new sub-agents), but the restart remains as a load-bearing safety boundary.

## OI-5 — Synthetic test feature shape (open for T6.1)

**Status:** Plan T6.1 designs the synthetic test feature; substantive shape (1 phase × 2 tasks recommended) ratified by user via Gate 5. NEEDS_RECONCILIATION-path inclusion explicitly opted-out for v1 (would re-include in v2 if FR-6 reveals gaps).

**Action:** During T6.1 execution, author the synthetic minimal feature spec; archive at `working/feature/synthetic-test-feature-T6/`.

## OI-6 — `current_stage` enumeration in checkpoint.json (open for T2.1)

**Status:** Cross-artifact auditor's I-CA finding noted the open question; Blueprint deferred to T2.1 implementation.

**Action:** During T2.1, finalize whether `current_stage` gains a single `"execution"` value or splits into per-substantive-state values (e.g., `"executing_phase_1"`, `"executing_phase_2"`). Synthesis substrate recommended single value; preserve this default unless T2.1 implementation surfaces a reason to split.

## OI-7 — PKG-REC-001 / PKG-REC-003 (informational, already absorbed)

**Status:** Absorbed in `Issues/analysis-adr-placement-rootcause.md` §10 (Gate-6 disposition: "Approve and address PKG-REC-001/003 now"). No remaining action.

---

## Re-validation

PV-0.C3 expects this document to contain `ADR-0036` AND `placement disposition` (case-insensitive). Both phrases present (OI-1 §"Disposition" line + multiple references throughout). PV-0.C3 should pass.
