---
id: tasks-summary-devcontainer-mcp-provisioning-r1
version: 1.0.0
status: draft
doc_type: TasksSummary
feature_slug: devcontainer-mcp-provisioning-r1
generated: 2026-05-23T00:00:00Z
generated_by: finalize-task-decomposer
companion_to: tasks.json
---

# Tasks Summary — devcontainer-mcp-provisioning-r1

Human-readable companion to `tasks.json` (canonical machine-actionable DAG). All counts and edges are sourced from `tasks.json`; this document narrates them.

## Headline numbers

| Metric | Value |
|---|---|
| Total task nodes | **39** |
| Total dependency edges (inter-task `depends_on`) | **70** |
| Phases | **6** (Phase 0 + Phases 1–4 Feature Delivery + Phase 5 Rollout) |
| Phase validators | **6** (PV-0 through PV-5) |
| PV criteria total | **113** (PV-0: 13, PV-1: 16, PV-2: 21, PV-3: 20, PV-4: 20, PV-5: 23) |
| Acceptance criteria mapped | **51 / 51** (complete) |
| Acceptance tests mapped | **50 / 50** (AT-001..AT-049 + AT-HG) |
| Gate-blocking task nodes (hard-gate carriers) | **3** (T4.3, T5.1, T5.4) |
| Verify-at-execution task nodes (§H-1..§H-7) | **7** (T0.1..T0.7) |
| ADR-0042 6-step family graduation coverage | **6 / 6** (T4.4 covers steps 1+2; T4.5 covers step 3; T4.6 covers steps 4+5+6) |
| Sub-decompositions made | **0** (plan tasks retained 1:1; rationale below) |

## Sub-decomposition decisions

The Plan reviewer noted five L-sized tasks (T2.2, T2.3, T3.4, T3.5, T4.3) as candidates for sub-decomposition. The task-decomposer chose to **retain all five as single nodes**, recorded per-task in `tasks.json` under `sub_decomposition_decision`. Rationale by task:

- **T2.2 (KB-mcp-platform/references/ + assets)** — 8 mandated files form one cohesive trifecta What-half body; PV-2.C4–C7 verify them as a set. Splitting per-file would create file-level fragmentation that loses trifecta coherence.
- **T2.3 (KB-mcp-design/SKILL.md + 2 refs)** — SKILL.md + principles.md + patterns-and-anti-patterns.md are tightly coupled (pedagogical_sections justifications reference both reference files; principles.md owns the mcp-events.jsonl schema load-bearing for AC-CC-7 + ADR-0037).
- **T3.4 (postCreate.sh)** — 5 per-server install paths share the sentinel+binary-presence pattern and a single fail-fast harness; splitting per-server would duplicate the harness 5× and create false serialization.
- **T3.5 (postStart.sh + §D-6)** — Enumeration loop + redaction filter + warn-and-continue logic + §D-6 staleness check form one cohesive lifecycle script; splitting would create artificial sub-tasks that share state at runtime.
- **T4.3 (10 OP scripts + audit_mcp.py)** — The 10 OPs share the audit_mcp.py harness + severity model + fixture-loading discipline. Splitting per-OP would create 10 micro-tasks that all consume the same harness.

Execution-time scheduling (i.e., authoring file-by-file inside a single L-sized task) is a downstream concern, not a DAG-structure concern. The downstream executor is free to checkpoint inside an L-sized task; the DAG only constrains task-level dependency.

## Critical path

```
T0.1 → T1.1 → T2.1 → T2.2 → T2.3 → T2.4 → T3.1 → T3.4 → T3.5 → T4.3 → T5.2 → T5.4 → T5.7
```

**13 nodes long.** This matches Plan §Critical Path exactly. Minimizing wall-clock time means maximizing parallelism within each phase (see below).

T0.1 is chosen as the Phase-0 representative on the critical path because T1.3 (its closest downstream consumer in Phase 1) requires the Terraform GPG-verify smoke-test result. All Phase 0 tasks are independent, so the choice of representative is informational only.

## Parallelization opportunities (by phase)

### Phase 0 — full parallelization (10 nodes)

All 10 setup tasks (T0.1..T0.10) are independent. A single contributor serializes; 2–3 contributors can dispatch in parallel. The single HIGH-risk item (T0.4 — GitNexus env-var smoke-test) is the long pole; everything else is XS/S.

### Phase 1 — three parallel after T1.1

- T1.1 (ADR promotion) gates everything in Phase 1.
- After T1.1: **T1.3, T1.5 parallel**; T1.2 depends on T1.1 only and can run alongside.
- T1.4 depends on T0.9 + T1.3 — serializes once T1.3 lands.

### Phase 2 — partial chain

- T2.1 → T2.2 serialize (assets/templates depend on SKILL.md pedagogical_sections shape).
- **T2.3 can parallelize with T2.2** (T2.3 only depends on T2.1 frontmatter for sister cross-ref + T1.1 for ADR-0037).
- T2.4 waits for T2.2 (template).

### Phase 3 — two-cluster parallel

- **T3.1 + T3.3 parallel** (mcp-ping.sh and terraform-mcp.sh are independent).
- T3.2 depends on T3.1.
- T3.4 + T3.5 serialize: postCreate completes + binaries on PATH before postStart can probe.

### Phase 4 — heaviest parallelization opportunity

- **T4.1, T4.4, T4.5, T4.7 all parallelizable in principle** (independent file groups; though T4.7 ultimately depends on T4.1 for final per-agent overhead numbers).
- After T4.1: T4.2 (verification-only).
- T4.3 depends on the most upstream tasks (T2.1, T2.3, T2.4, T3.4, T3.5, T4.1, T4.2). Typically completed before/in parallel with T4.6.
- After T4.4 + T4.5: T4.6 (auditing-shared + cross-file + singular→plural sweep).

### Phase 5 — serial chain

T5.1 → T5.2 → T5.3 → T5.4 → T5.5 → T5.6/T5.7. Each smoke consumes the live state of the previous; **inherently serial**. T5.6 (§OI-5 follow-up file) depends only on T1.2 (relocation) and could in principle run anywhere in Phase 5; T5.7 (deliverable archive) requires all prior Phase 5 tasks.

## Gate-blocking task nodes (ADR-0043 hard-gate)

| Task | Role | Gate criteria |
|---|---|---|
| **T4.3** | Authors `audit_mcp.py` — the script whose exit code IS the Gate-6 gate signal | PV-4.C6..C11 (script existence + fixture exercises) |
| **T5.1** | Declares the orchestrator Gate-6 contract per ADR-0043 (no-bypass semantics) | PV-5.C-HARDGATE, PV-5.C17 |
| **T5.4** | Live exercise: seeded-BLOCKER simulation; confirms halt + remediation + resume | PV-5.C-HARDGATE, **PV-5.C-HARDGATE-EXERCISE** |

T5.4's `cleanup_required` field is non-optional: the seeded credential MUST be removed before any commit. Failing this leaves the working tree non-shippable.

## AC discharge coverage (51 / 51)

Every AC from Blueprint v3 is mapped to ≥1 task. Detailed AC→task index in `tasks.json` `ac_coverage_summary.ac_to_task_index`. Source-of-truth: Plan v1 §Acceptance Test Cross-Reference (lines 1087–1166).

One reconciliation note: **AC-NFR-4-a** (per-agent context overhead) was tagged in the Plan body of T4.7 as "no specific Blueprint AC ID; this is the OI-4 closure." `acceptance-tests.md` authored AT-043 for it. Mapped T4.7 → AC-NFR-4-a here pending cross-artifact-audit confirmation (logged in `open_questions_for_human`).

## PV criterion coverage (113 / 113)

Every PV criterion has at least one task whose `gates:` array references it. See `tasks.json` `pv_coverage_summary` for the per-phase breakdown.

The hard-gate criteria (PV-5.C-HARDGATE, PV-5.C-HARDGATE-EXERCISE) are gated by T5.1 + T5.4 with `gate_blocking: true` and a rationale field.

## Open items carried forward (for orchestrator awareness)

5 items, all non-blocking for task decomposition:

1. **PA-OI-2** — T3.5 §D-6 postAttach staleness = 5 min (plan-author judgment); amend if reviewer revises.
2. **PA-OI-3** — T4.7 OI-4 measurement may discover NFR-4 breach → conditional-activation re-scope not currently in DAG; T4.7 would halt Phase 4 if so.
3. **PA-OI-4** — MINOR-V3-001 disposition (AC-FR-11-c carried via unified triplet) — option (b) v3.0.1 patch remains available if audit finds option (a) insufficient.
4. **PA-OI-5** — T4.3 test-fixtures authored at execution time; not a separate DAG node.
5. **AC-NFR-4-a vs PRD-NFR-4 naming** — confirm canonical AC identifier with cross-artifact auditor.

Full text in `tasks.json` `open_questions_for_human`.

## Event-trigger discipline observed

Per Plan §O / §OI-6, no calendar machinery in this DAG:

- **T5.6** event trigger = "next ADR-0007 touch" (no calendar)
- **T5.7** preserves §OI-6: ADR-0040 design-codespaces Serena 90-day kill criterion stays in the ADR as design-time documentation; live event trigger = "when auditing-codespaces stub-fill is undertaken"
- **PV-5.C19** (per phase-validators) sweeps follow-ups.md for time-based triggers and flags any survivor

## Cross-cutting concerns indexed

Tasks tagged with `cross_cutting:` arrays:

- **security** — T1.4, T1.5, T0.5, T0.7, T0.10, T2.2, T2.3, T2.4, T3.1, T3.2, T3.3, T3.4, T3.5, T3.6, T4.1, T5.1, T5.4, T5.5, T4.3 (per ADR-0039 redact-at-source posture)
- **observability** — T0.10, T2.2, T2.3, T3.1, T3.2, T3.4, T3.5, T4.3, T4.7, T5.2, T5.3, T5.4, T5.5 (per ADR-0037 mcp-events.jsonl)

## Schema version

`tasks.json` is schema v1.0.0 per KB-task-decomposition. Field semantics:

- `id` — plan task ID retained 1:1 (e.g., `T0.1`, `T4.6`) for traceability to plan-v1.md.
- `layer` ∈ {`cc` (Claude Code), `codespaces`}. Only 2 layers activated (per Blueprint Layer Scope).
- `effort` ∈ {`xs`, `small`, `medium`, `large`} — T-shirt sizes from plan-v1.
- `gates` — references PV-N.Cn criteria from phase-validators.md.
- `verifies_acceptance_criterion` — Blueprint v3 AC IDs.
- `gate_blocking: true` (optional) — flags hard-gate carriers per ADR-0043.
- Sidecar fields preserved for downstream consumers: `adr_0042_graduation_steps`, `event_trigger`, `cleanup_required`, `load_bearing_for`, `verify_at_execution`, `deferral_register_item`, `open_items_carried`, `sub_decomposition_decision`.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-23 | finalize-task-decomposer | Initial. 39 nodes 1:1 with plan-v1.md tasks. 70 inter-task edges. 6 phases mirroring plan. 113 PV criteria mapped, 51 ACs mapped, 50 ATs mapped, 7 §H verify-at-execution items in Phase 0. ADR-0042 6-step graduation distributed across T4.4 (1+2), T4.5 (3), T4.6 (4+5+6). Hard-gate severity carried on T4.3 + T5.1 + T5.4 with T5.4 the live anchor. No sub-decompositions (rationale per L-sized task in tasks.json). 5 open items carried forward for orchestrator awareness; none block decomposition. Event-trigger discipline observed (no calendar machinery). |
