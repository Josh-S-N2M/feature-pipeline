---
id: BP-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: blueprint
version: 1.1.0
status: draft
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
scope_class: FULL
layer_scope: [cc]
derived_from:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md
codebase_analysis: working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-dependencies.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design-review-issues.json
  - Issues/analysis-execute-orchestrator-dispatch-limitation.md
adrs_authored:
  - ADR-0044 (Flatten execution-phase dispatch hierarchy — parent orchestrator dispatches the four specialists directly)
  - ADR-0045 (Sub-agents MUST NOT declare `Agent` in their `tools:` frontmatter array)
inherited_adrs:
  - ADR-0011
  - ADR-0017
  - ADR-0019
  - ADR-0021
  - ADR-0022
  - ADR-0027
  - ADR-0029
  - ADR-0033
  - ADR-0035
  - ADR-0036
  - ADR-0037
  - ADR-0040
  - ADR-0041
version_history:
  - {version: "1.0.0", date: "2026-05-23T21:30:00Z", note: "Initial composition by design-composer"}
  - {version: "1.1.0", date: "2026-05-23T22:45:00Z", note: "v2 patch absorbing reviewer findings I-DR-101 (3-occurrence count correction on execute-finalize-reconciler.md; line 84 cites ADR-0017 not ADR-0034) and I-DR-102 (frontmatter adrs_referenced -> inherited_adrs; added ADR-0011)"}
generated: 2026-05-23T21:30:00Z
generated_by: design-composer (v1) + parent-orchestrator-surgical-patch (v1.1.0)
---

# execute-orchestrator Dispatch Mechanism Repair (r1) Design Document

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft.

- [x] Overview
- [x] Design Summary (Meta)
- [x] Background and Context
- [x] Acceptance Criteria (AC) - EARS Format
- [x] Existing Codebase Analysis
- [x] Design
- [x] Implementation Plan
- [x] Security Considerations
- [x] Test Boundaries
- [x] Verification Strategy
- [x] Future Extensibility
- [x] Alternative Solutions
- [x] Risks and Mitigation
- [x] References
- [x] Update History

## Overview

This Blueprint restores the `execute-orchestrator` sub-agent's runtime dispatch capability after Discovery Research (T-001) confirmed via three independent Anthropic-controlled primary sources that Claude Code sub-agents cannot dispatch other sub-agents — even when `Agent` is declared in the `tools:` frontmatter array. The repair flattens the execution-phase dispatch hierarchy: the parent `recipe-feature-pipeline` orchestrator skill becomes the direct dispatcher of the four execution-side specialists at the main-conversation level (where dispatch IS supported), and `execute-orchestrator.md` is re-scoped as a state-machine advisor / canonical reference rather than retired. The four load-bearing audit-trail properties documented in analysis §3.2 (per-dispatch logging, per-task / per-phase cycle-counter enforcement, dispatch-matrix routing, ADR-0033 symmetric D-12 application) are preserved.

### Layer Scope

Declared layers and disposition (per the 9-layer engineering taxonomy in `KB-documentation-criteria/references/layer-taxonomy.md`):

- [x] **Claude Code / Project Filesystem** — sub-agent definitions, the parent orchestrator skill, the canonical schema references, and pipeline-internal state artifacts all live here. **Sole activated layer.**
- [ ] **Frontend** — N/A — out of scope. No UI surface is affected.
- [ ] **Backend** — N/A — out of scope. No backend service is affected.
- [ ] **API** — N/A — out of scope. No API contract is affected.
- [ ] **Query / Data Access** — N/A — out of scope. No data-access layer is affected.
- [ ] **Database** — N/A — out of scope. No schema is affected; checkpoint.json and state-transitions.log are filesystem-resident cc artifacts.
- [ ] **CI/CD (GitHub Actions)** — N/A — out of scope. No workflow is affected.
- [ ] **Infrastructure as Code** — N/A — out of scope. No IaC module is affected.
- [ ] **Dev Environment (Codespaces / Devcontainer)** — N/A — out of scope. The defect surfaced during a devcontainer-mcp-provisioning-r1 run, but the defect lives in the dispatch mechanism, not the devcontainer layer.

### Referenced Specifications

- **PRD** — `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md`
- **Per-layer cc Design** — `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design.md` (integrated below; reviewer-flagged extensions applied)
- **Synthesis (rationale brief)** — `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md`
- **Research note T-001** — `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md`
- **Source analysis** — `Issues/analysis-execute-orchestrator-dispatch-limitation.md`

## Design Summary (Meta)

```yaml
design_type: "refactoring"
risk_level: "medium"
complexity_level: "medium"
complexity_rationale: |
  (1) PRD FR-3-c invariants are load-bearing across multiple files (ADR-0017
  4-cycle cap; dispatch-matrix definitions; ADR-0033 symmetric D-12) and the
  schema closure (D-004) and dispatch-section addition (D-001) share a single
  load-bearing file (recipe-feature-pipeline/SKILL.md) so edit ordering is
  load-bearing.
  (2) The state-transitions-log v1 `invoking_agent` invariant is preserved
  via re-interpretation (logical owner, not literal emitter) — a documentation
  clarification rather than a schema change but with operational implications
  for downstream audit consumers.
  (3) F-7 (mid-session agent-registry constraint) is a novel single-instance
  observation that constrains FR-6 verification sequencing.
layers_touched:
  - "Claude Code / Project Filesystem"
blast_radius:
  runtime: "Every future feature execution pipeline; the pipeline operator (single user)."
  build_time: "N/A — no build pipeline; pipeline-internal cc-layer artifacts only."
main_constraints:
  - "PRD FR-3-c — preserve ADR-0017 4-cycle cap, dispatch-matrix definitions, ADR-0033 symmetric D-12."
  - "PRD FR-4 — 8-file inventory cap; AC-FR-4-a operator gate for any out-of-inventory edit."
  - "PRD NFR-5-a — canonical schema reference lockstep with any schema change."
  - "PRD NFR-6-a — no migration of in-flight devcontainer-mcp-provisioning-r1 artifacts."
  - "Claude Code substrate constraint (T-001) — sub-agents cannot dispatch sub-agents."
  - "F-7 — agent registry loaded at session start; no hot-reload mid-session (synthesis §4)."
biggest_risks:
  - "Edit-ordering on recipe-feature-pipeline/SKILL.md (schema first, then dispatch section) is documented but plan-author could invert without consequence; schema-references-not-yet-stable risk."
  - "Incomplete ADR-0034 → ADR-0033 sweep on execute-finalize-reconciler.md (3 occurrences flagged by reviewer; Blueprint edit-list extends to cover all)."
  - "F-7 verification sequencing for FR-6 synthetic test (if plan-author authors new sub-agents)."
unknowns:
  - "Whether the audit-extension to enforce ADR-0045 (Agent-grant prohibition) lands in SA-13 or a new audit family — deferred to follow-on feature."
  - "Whether `current_stage` in checkpoint.json gains a single 'execution' value or splits into per-substantive-state values (plan-author decision; substrate prefers single)."
```

## Background and Context

### Prerequisite ADRs

The following ADRs are inherited and load-bearing for this Blueprint. Each is honored without modification.

| ADR | Load-bearing invariant | Applied to |
|---|---|---|
| ADR-0017 | 4-cycle reconciliation cap (per-task + per-phase, symmetric per D-12) | Preserved in dispatch-section design (parent owns counter; halt at cycle 4) |
| ADR-0019 | Sub-agent / skill / ADR naming convention | Honored across affected files |
| ADR-0021 | KB-and-ADR-first discipline | Governs this Blueprint's authoring |
| ADR-0022 | Sub-agent reasoning configuration intentional and audited (model/effort/skills triplet) | All 5 execute-* agents' triplets preserved unchanged |
| ADR-0027 | Cwd MUST equal repo root for parent skill invocation | Preserved — parent skill precondition unchanged |
| ADR-0029 | No silent scope changes | Honored — kill-criterion-#1 NOT exercised (kill-criterion-#2 fired per T-001); FULL repair is user-gated |
| ADR-0033 | ADR-0029 execution-phase extension; canonical home for symmetric D-12 application | Cited throughout Blueprint, ADR-0044, and all downstream artifacts (DISSENT-2 carry-through per synthesis Constraint 5.4) |
| ADR-0035 | auditing-shared skill-binding convention | Honored — execute-finalize-reconciler's auditing-shared binding preserved |
| ADR-0036 | Single-location ADR placement (adrs/ project-wide registry only) | Both new ADRs (0044, 0045) land at `adrs/` only; no feature-scoped copies |
| ADR-0037 | mcp-events.jsonl transition surfacing | Conditionally applicable — option (a) does not exercise; marked N/A for this run |
| ADR-0040 | Serena narrowed always-on | Marginally applicable — no execute-* agent on Serena allowlist |
| ADR-0041 | Install-mechanism hybrid | Marginally applicable — no new install script under option (a) |

ADRs newly surfaced by the codebase researcher that are NOT inherited (disposition justified in Fact Disposition Table):

| ADR | Subject | Disposition | Rationale |
|---|---|---|---|
| ADR-0042 | auditing-mcp family graduation | N/A — orthogonal | Grep verification: zero references to any execute-* agent. ADR-0042 scopes auditing-skill family relationships; no constraint on dispatch mechanism. |
| ADR-0043 | auditing-mcp Gate-6 hard gate | N/A — orthogonal | Grep verification: zero references to any execute-* agent. ADR-0043 scopes orchestrator-level Gate 6 hard-gate behavior for MCP auditing findings; no constraint on the execution-phase dispatch mechanism. |

ADRs authored in this run (per FR-5, only design-composer authors ADRs):

- **ADR-0044** (`adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md`) — captures the §6 option (a) choice with rationale, kill criteria, and the rejection of options (b) and (c).
- **ADR-0045** (`adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md`) — codifies the project-wide convention that sub-agents MUST NOT declare `Agent` in their `tools:` array. Ratifies the cc-design Q-CC-1 option (a) recommendation, diverging from synthesis D-005 (Composer's call).

### External Resources Used

None. The repair is entirely internal to the project's Claude Code primitives surface.

### Agreement Checklist

#### Scope

- [x] Restore execution-phase dispatch capability under the harness-supported pattern (parent dispatches sub-agents at main-conversation level).
- [x] Re-scope `execute-orchestrator.md` as state-machine advisor; remove `Agent` and `TaskUpdate` from its `tools:`.
- [x] Add an "Execution Phase Dispatch" section to `recipe-feature-pipeline/SKILL.md`.
- [x] Close the canonical `checkpoint.json` schema-reference gap in `recipe-feature-pipeline/SKILL.md` (lines 96–128) and the `state-transitions.log` per-entry schema in `state-transitions-log-entry-template.md`.
- [x] Re-frame `execute-finalize-reconciler.md` to emit `dispatch_directives[]` rather than dispatching `Agent` directly; remove `Agent` from its `tools:`.
- [x] Sweep ADR-0034 → ADR-0033 across all 3 occurrences in `execute-finalize-reconciler.md` (Blueprint extends cc-design's edit list per I-DR-001).
- [x] Author two ADRs (ADR-0044, ADR-0045) per FR-5 design-composer authority.

#### Non-Scope (Explicitly not changing)

- [x] No changes to the four specialists' substantive domain responsibilities (PRD FR-3-b / FR-4-c).
- [x] No changes to ADR-0017 4-cycle cap definition, dispatch-matrix definitions (D-2a/c/d, D-12, D-13, D-14), or ADR-0033 symmetric D-12 application.
- [x] No retrofit of `devcontainer-mcp-provisioning-r1` in-flight artifacts (PRD NFR-6-a).
- [x] No broader sub-agent roster redesign.
- [x] No new sub-agent files authored by this feature (existing sub-agents are edited only).
- [x] No MCP server changes; no hooks added.
- [x] No cleanup of other Agent-declaring sub-agents beyond the 2 in the FR-5 sweep (the sweep closed at 2).

#### Constraints

- [x] Parallel operation: No — single-tenant pipeline operator.
- [x] Backward compatibility: Required — applies to in-flight `devcontainer-mcp-provisioning-r1` artifacts per NFR-6-a; new schema fields documented as v1 with `execution_mode: "single-agent-fallback"` preserved as compatibility marker.
- [x] Performance measurement: Not required — human-timescale operation per PRD NFR Performance.
- [x] Zero-downtime deployment: N/A — not a deployed service.
- [x] Forward-compatible migration: Required — old (workaround-emitted) artifacts must remain readable by post-repair tooling.

#### Applicable Standards

- [x] ADR-0019 sub-agent / skill / ADR naming convention `[explicit]` — Source: `adrs/ADR-0019-naming-convention.md`.
- [x] ADR-0036 single-location ADR placement `[explicit]` — Source: `adrs/ADR-0036-single-location-adr-placement.md`.
- [x] ADR-0022 sub-agent reasoning configuration audit `[explicit]` — Source: `adrs/ADR-0022-subagent-reasoning-configuration.md`.
- [x] Bundled commit for FR-5 cleanup `[implicit]` — Evidence: synthesis §5.2 Constraint 5.2 — Confirmed: Yes (plan-author honors).
- [x] EARS acceptance-criteria format `[explicit]` — Source: `KB-documentation-criteria/references/disciplines/ears-acceptance-criteria.md`.

#### Quality Assurance Mechanisms

- [x] `shared-document-reviewer` Gate 0/1 review — Enforces: structural completeness + content quality — Config: `.claude/agents/shared-document-reviewer.md` — Covers: this Blueprint + both new ADRs — Status: `adopted`.
- [x] `review-architecture-auditor` substantive audit — Enforces: blast-radius coverage + brief honoring + CoVe-style claim verification — Config: `.claude/agents/review-architecture-auditor.md` — Covers: this Blueprint — Status: `adopted`.
- [x] FR-5 cleanup commit-message discipline — Enforces: "affected set = 2" documentation — Source: synthesis §5.2 — Covers: the `Agent`-removal commit — Status: `adopted`.

### Problem to Solve

The `execute-orchestrator` sub-agent's frontmatter declares `tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]`, but its runtime tool surface contains only `[Read, Write, Bash, Edit]`. The Claude Code harness silently drops `Agent`, `Glob`, `Grep`, and `TaskUpdate`, adds an undeclared `Edit`, and strips the `Bash(python3:*)` scope restriction. As a result, the agent cannot dispatch the four execution-side specialists. The `devcontainer-mcp-provisioning-r1` run shipped via a parent-driven workaround that loses the four load-bearing audit-trail properties documented in analysis §3.2.

### Current Challenges

- The substrate constraint is harness-level and not addressable via frontmatter, environment variables, or flags (T-001 exhaustive enumeration; absence-of-feature claim with bounded falsifiability).
- The `execute-finalize-reconciler` sub-agent has the same defect pattern (also declares `Agent` in `tools:`) but its dispatch path was never exercised in flight (the workaround halted before T9).
- The canonical `checkpoint.json` schema reference in `recipe-feature-pipeline/SKILL.md` (lines 96–128) does not document the execution-phase fields that are de facto present in the in-flight artifact.
- The state-transitions-log per-entry schema does not document the `void` / `void_reason` and `-prime` suffix conventions observed in the in-flight log.
- The PRD's FR-3-c phrase "ADR-0034 symmetric D-12" was a documentary mis-credit; the canonical home is ADR-0017 + ADR-0033, and the mis-credit propagated into `execute-finalize-reconciler.md` (3 occurrences on lines 3, 19, 82) but the cc-design's edit list only addressed line 19.

### Requirements

#### Functional Requirements

- FR-1 (in-pipeline Discovery investigation) — addressed by T-001 with `dispatch_supported: false` outcome.
- FR-2 (kill-criterion-#1 pause-and-rescope) — NOT exercised (T-001 returned kill-criterion-#2).
- FR-3 (per-layer cc Design selects among §6 options under constraints) — addressed; option (a) chosen.
- FR-4 (implementation across the affected-files inventory) — addressed; 8 in-inventory + 1 outside-inventory (1 AC-FR-4-a open item).
- FR-5 (inventory sweep of other Agent-declaring sub-agents) — addressed; sweep closed at 2 (both cleaned in this run).
- FR-6 (verification via synthetic minimal test feature) — addressed at design level; plan-author authors the test.
- FR-7 (real-feature re-run as confidence check) — non-gating P2 per PRD.
- FR-8 (ADR for project-wide convention) — addressed by ADR-0045.

#### Non-Functional Requirements

- **Reliability** — dispatch-loop stability under synthetic test (PRD NFR-1).
- **Observability / Audit Trail** — per-dispatch state-transition logging (NFR-2); per-task / per-phase cycle-counter visibility (NFR-3).
- **Maintainability** — investigation finding preserved as citable artifact (NFR-4 — research-note T-001); schema reference consistency (NFR-5 — D-004 closes the gap in lockstep with D-001).
- **Compatibility** — in-flight artifacts left as-shipped (NFR-6-a); new schema fields documented as v1 with compatibility markers (NFR-6-b).
- **Developer Experience** — synthetic test feature archived as regression artifact (NFR-7).

## Acceptance Criteria (AC) - EARS Format

ACs are organized by Functional Requirement and traceable to the PRD. They propagate to the test-acceptance-author for the synthetic minimal test feature (FR-6).

### AC inheritance from PRD (I-CA-001 absorption)

This Blueprint section enumerates the **cc-design-introduced ACs** (AC-FR-3-* through AC-FR-8-* plus AC-CC-N items). The Blueprint **inherits** all PRD ACs not enumerated below — specifically AC-FR-1-a/b/c, AC-FR-2-a/b/c, AC-FR-7-*, AC-FR-4-c, and the 9 AC-NFR-* items — without restating them, per the canonical Blueprint discipline that the PRD is the authoritative AC source and the Blueprint adds only what the design composition introduces. Plan v1.1.x maps **35 ACs total**: 29 inherited from PRD (including AC-FR-1-a/b/c as `satisfied-upstream` via T-001 and AC-FR-2-a/b/c as `vacuous-by-kc2`) + 6 implicit AC-CC-N items introduced by this Blueprint's design subsection. Acceptance-tests v1.0.1 maps the same 35 ACs across 54 tests (27 L1 + 14 L2 + 13 L3).

### Functional ACs

#### FR-3 — §6 option selection (Layer: Claude Code)

- [ ] **AC-FR-3-a** (PRD verbatim) — Where the investigation outcome is kill-criterion-#2, the per-layer cc Design subsection shall name exactly one chosen option from {flatten-hierarchy, retire-execute-orchestrator, bash-script-dispatch} and shall record the rationale tying the choice to (i) the investigation finding, (ii) the specialist-isolation invariants. **Resolved:** option (a) flatten-hierarchy named in this Blueprint and in ADR-0044 with three-reason rationale (FR-4 inventory; state-transitions-log v1 invariant; specialist-isolation).
- [ ] **AC-FR-3-b** (PRD verbatim) — Where the investigation outcome is kill-criterion-#2, the per-layer cc Design shall preserve the four specialists' substantive domain responsibilities regardless of which option is chosen — only their tool grants, dispatch interfaces, and parent orchestrator may change.
- [ ] **AC-FR-3-c** (PRD verbatim) — The chosen option shall preserve the ADR-0017 4-cycle cap, the dispatch-matrix definitions (D-2a/c/d, D-12, D-13, D-14), and the ADR-0033 symmetric D-12 application as load-bearing invariants.

#### FR-4 — Implementation across the affected-files inventory (Layer: Claude Code)

- [ ] **AC-FR-4-a** — When the implementation phase completes, the system shall have modified exactly the 8 files in the PRD FR-4 inventory PLUS exactly 1 file outside the inventory (`state-transitions-log-entry-template.md`). Any edit outside this 8+1 set shall trigger an AC-FR-4-a operator-gate open item.
- [ ] **AC-FR-4-b** — Where `recipe-feature-pipeline/SKILL.md` is modified by D-001 (dispatch section), the canonical `checkpoint.json` schema reference at the same file (lines 96–128) shall be updated in the same commit set to document the 3 execution-phase fields (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`) and the `void` / `-prime` extensions to the state-transitions-log per-entry schema.

#### FR-5 — Sweep and cleanup (Layer: Claude Code)

- [ ] **AC-FR-5-a** — When the implementation phase completes, `execute-finalize-reconciler.md` shall have `Agent` removed from its `tools:` array, body line 76 "Dispatch via Agent" re-framed to "emit `dispatch_directives[]` in `quality-reconciliation-log.json`", AND all three ADR-0034 occurrences corrected to ADR-0033 (lines 3, 19, 82). Bundled with `execute-orchestrator.md`'s `Agent`-removal in a single commit; commit message documents "FR-5 sweep closure: affected set = 2".
- [ ] **AC-FR-5-b** — When the implementation phase completes, an inventory artifact shall exist (e.g., `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/agent-tool-grant-inventory.md` or equivalent) documenting the sweep result (36 files swept; 2 violations; both cleaned in this run).

#### FR-6 — Verification via synthetic minimal test feature (Layer: Claude Code)

- [ ] **AC-FR-6-a** — When the synthetic minimal test feature runs end-to-end against the repaired mechanism, the system shall emit at least one `state-transitions.log` entry per specialist sub-agent dispatch boundary, with `invoking_agent: "execute-orchestrator"` preserved as the v1 logical-owner invariant.
- [ ] **AC-FR-6-b** — When the synthetic minimal test feature crosses a task or phase boundary, the parent orchestrator shall increment the corresponding cycle counter in `checkpoint.json.execution_pipeline_cycle_counters.per_task[<task-id>]` or `…per_phase[<phase-id>]` — specifically at T4 (per-task NEEDS_REVISION) for per_task counters and T10 (phase reconciliation cycle complete) for per_phase counters per I-AA-609 invariant 10. T0 and T13 boundary transitions are logged but do NOT increment.
- [ ] **AC-FR-6-c** — If a cycle counter reaches 4 without resolution, then the parent orchestrator shall halt with a TERMINATED transition `trigger: cycle-cap-exhaustion`, write `escalation-cycle-cap.json`, and surface to the user — NOT silently continue.
- [ ] **AC-FR-6-d** (F-7 constraint) — While the FR-6 synthetic minimal test feature is being verified, the verification shall occur in a session distinct from any session that authors new test-artifact sub-agent files. If `plan-author`'s synthetic test design authors no new sub-agents, this AC is vacuously satisfied; otherwise the plan MUST include an explicit operator session-restart step between the authoring task and the test-execution task.

#### FR-8 — Project-wide convention ADR (Layer: Claude Code)

- [ ] **AC-FR-8-a** — Where the investigation outcome is kill-criterion-#2 AND design-composer determines a project-wide convention is warranted, the system shall produce an ADR documenting the convention with explicit linkage to the investigation finding and to the chosen §6 option. **Resolved:** ADR-0045 authored at `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md`.

### Cross-Layer / Operational ACs

- [ ] **AC-CC-1** (decision documentation) — The Blueprint's Design section names "option (a) flatten dispatch hierarchy" with rationale citing (i) PRD FR-4 8-file inventory compliance, (ii) state-transitions-log v1 `invoking_agent` invariant preservation, (iii) specialist-isolation audit-trail preservation, AND ADR-0017 + ADR-0033 (NOT ADR-0034) cited throughout for the 4-cycle cap + symmetric D-12 application.
- [ ] **AC-CC-2** (NFR-5-a lockstep) — Where `recipe-feature-pipeline/SKILL.md` Execution Phase Dispatch section is added, the canonical `checkpoint.json` schema reference at the same file's lines 96–128 is updated in the same commit set per FR-4-b.
- [ ] **AC-CC-3** (Q-CC-3 disposition — preserve self-reference with rationale) — `execute-orchestrator.md`'s `skills:` array continues to list `recipe-feature-pipeline`; the body includes an explicit prose rationale ("this advisor documents the state machine the parent skill orchestrates; the self-reference is intentional") to provide file-resident evidence for SA-13 audits per I-DR-006.
- [ ] **AC-CC-4** (I-DR-005 error-state) — `recipe-feature-pipeline/SKILL.md`'s Execution Phase Dispatch section includes an error-state entry for malformed or empty `dispatch_directives[]` from `quality-reconciliation-log.json` (parent surfaces to user; treats as cycle-cap-equivalent escalation rather than silent fallback).

## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | Existing | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Parent orchestrator skill; the 13-stage taxonomy. Modified to add Execution Phase Dispatch section + close schema gap. |
| Claude Code | Existing | `.claude/agents/execute-orchestrator.md` | Re-scoped to state-machine advisor. Agent + TaskUpdate removed from `tools:`. |
| Claude Code | Existing | `.claude/agents/execute-task-code-producer.md` | Body prose update only. |
| Claude Code | Existing | `.claude/agents/execute-task-quality-handler.md` | Body prose update only. |
| Claude Code | Existing | `.claude/agents/execute-phase-quality-reviewer.md` | Body prose update only. |
| Claude Code | Existing | `.claude/agents/execute-finalize-reconciler.md` | Agent removed from `tools:`. 3 ADR-0034 → ADR-0033 corrections (lines 3, 19, 82). Body line 76 re-framed to emit dispatch_directives[]. |
| Claude Code | Existing (referenced) | `working/feature/<slug>/checkpoint.json` schema | De-facto execution-phase fields documented in the canonical reference at recipe-feature-pipeline/SKILL.md:96–128. |
| Claude Code | Existing | `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` | v1 `invoking_agent` invariant clarified (logical owner); `void` / `-prime` extensions folded into v1. Outside FR-4 inventory — 1 AC-FR-4-a open item. |
| Claude Code | New | `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md` | §6 option (a) decision. |
| Claude Code | New | `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` | Project-wide convention. |

### Integration Points

- **Integration Target:** the four execution-side specialists (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`).
- **Invocation Method:** `Agent` dispatch from the parent `recipe-feature-pipeline` orchestrator skill at the main-conversation level (where dispatch IS supported per T-001 Finding F-1).

### Code Inspection Evidence

| File/Function | Relevance |
|---|---|
| `.claude/agents/execute-orchestrator.md:6` | Frontmatter `tools:` declaration with `Agent` — defective at runtime. |
| `.claude/agents/execute-orchestrator.md:24-43` | 14-row state machine narrative — preserved as canonical reference under advisor role. |
| `.claude/agents/execute-finalize-reconciler.md:6` | Frontmatter `tools:` with `Agent` — second affected file per FR-5 sweep. |
| `.claude/agents/execute-finalize-reconciler.md:3,19,82` | Three ADR-0034 occurrences — all corrected to ADR-0033 per I-DR-001 extension. |
| `.claude/agents/execute-finalize-reconciler.md:76` | "Dispatch via Agent" prose — re-framed to emit `dispatch_directives[]`. |
| `.claude/skills/recipe-feature-pipeline/SKILL.md:96-128` | Canonical `checkpoint.json` schema reference — incomplete; closed by D-004. |
| `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md:63` | v1 `invoking_agent` invariant — clarified as logical owner. |
| `working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log` | In-flight artifact demonstrating the v1 invariant value `"execute-orchestrator"` across all entries; preserved per NFR-6-a. |
| `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json:8-39` | In-flight artifact with the de facto execution-phase fields documented by D-004. |

### Fact Disposition Table

One row per codebase-analysis-relevant focus area. The codebase-analysis.json uses `affected_files`, `affected_agents`, `fr5_inventory_sweep`, `blast_radius`, `known_issues`, and `open_questions_for_human` as its top-level focus categories. Each is dispositioned below.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---|---|---|---|---|
| FD-1 | `affected_files[recipe-feature-pipeline/SKILL.md]` (gap: no execution-phase content, no execution-phase checkpoint.json schema fields) | transform | Add new "Execution Phase Dispatch" section (D-001) AND close schema-reference gap (D-004) at lines 96–128 in lockstep per synthesis Constraint 5.1. Recommended order: schema closure FIRST, then dispatch-section absorption (I-DR-004 absorption). | codebase-analysis.json `affected_files[0]` lines 27–42 |
| FD-2 | `affected_files[execute-orchestrator.md]` (frontmatter `Agent` declared; runtime no-op; body documents dispatch loops) | transform | Re-scope as state-machine advisor; remove `Agent` + `TaskUpdate` from `tools:`; re-frame body sections from "what this agent does" to "what the parent orchestrator MUST execute." | codebase-analysis.json `affected_files[1]` lines 44–63 |
| FD-3 | `affected_files[execute-task-code-producer.md]` | preserve (substantive); transform (prose) | Substantive domain responsibilities unchanged per FR-3-b. Body-prose-only dispatcher reference update ("dispatched by execute-orchestrator" → "dispatched by recipe-feature-pipeline parent orchestrator"). | codebase-analysis.json `affected_files[2]` lines 64–81 |
| FD-4 | `affected_files[execute-task-quality-handler.md]` | preserve (substantive); transform (prose) | Same disposition as FD-3. | codebase-analysis.json `affected_files[3]` lines 82–99 |
| FD-5 | `affected_files[execute-phase-quality-reviewer.md]` | preserve (substantive); transform (prose) | Same disposition as FD-3. | codebase-analysis.json `affected_files[4]` lines 100–119 |
| FD-6 | `affected_files[execute-finalize-reconciler.md]` (frontmatter `Agent`; 3 ADR-0034 mis-cites; line 76 "Dispatch via Agent" prose) | transform | Remove `Agent` from `tools:`. Correct all 3 ADR-0034 occurrences to ADR-0033 (lines 3, 19, 82) — Blueprint extends cc-design edit list per I-DR-001. Re-frame line 76 prose to emit `dispatch_directives[]`. | codebase-analysis.json `affected_files[5]` lines 120–139; `cc-design-review-issues.json` I-DR-001 |
| FD-7 | `affected_files[devcontainer-mcp-provisioning-r1/checkpoint.json]` | out-of-scope | In-flight artifact left as-shipped per NFR-6-a. Used as de-facto schema source for D-004. | codebase-analysis.json `affected_files[6]` lines 140–157 |
| FD-8 | `affected_files[devcontainer-mcp-provisioning-r1/state-transitions.log]` | out-of-scope | In-flight artifact left as-shipped per NFR-6-a. Used as evidence base for state-transitions-log v1 extension folding. | codebase-analysis.json `affected_files[7]` lines 158–175 |
| FD-9 | `affected_agents[execute-orchestrator]` (Agent declared; same defect would manifest) | transform | Per ADR-0044 option (a) — re-scoped to advisor; `Agent` + `TaskUpdate` removed. | codebase-analysis.json `affected_agents[0]` lines 178–198 |
| FD-10 | `affected_agents[execute-task-code-producer / quality-handler / phase-quality-reviewer]` (leaf agents; no Agent declaration) | preserve | Substantive responsibilities unchanged. Body prose updates only. | codebase-analysis.json `affected_agents[1-3]` |
| FD-11 | `affected_agents[execute-finalize-reconciler]` (Agent declared; never reached in flight) | transform | Per ADR-0044 — `Agent` removed; dispatch-directives indirection introduced. Memory: project preserved (Q-CC-5 disposition). | codebase-analysis.json `affected_agents[4]` lines 245–259 |
| FD-12 | `fr5_inventory_sweep` (36 files swept; 2 violations: execute-orchestrator + execute-finalize-reconciler) | transform (closure) | Both violations cleaned in this run. ADR-0045 codifies the forward-looking convention. AC-FR-5-b records the sweep result as an inventory artifact. | codebase-analysis.json `fr5_inventory_sweep` |
| FD-13 | `blast_radius[option_a_flatten]` (3 in-inventory + 1 outside-inventory; 1 AC-FR-4-a open item) | preserve (as authoritative) | Selected option's blast-radius enumeration is canonical for this Blueprint. | codebase-analysis.json `blast_radius.option_a_flatten` |
| FD-14 | `blast_radius[option_b_retire]` (5+ outside-inventory; widest AC-FR-4-a surface) | out-of-scope (rejected) | Option (b) rejected per ADR-0044; recorded as rejection rationale. | codebase-analysis.json `blast_radius.option_b_retire` |
| FD-15 | `blast_radius[option_c_bash]` (1 new dispatch script; audit-trail loss) | out-of-scope (rejected) | Option (c) rejected per ADR-0044; recorded as rejection rationale. | codebase-analysis.json `blast_radius.option_c_bash` |
| FD-16 | `known_issues` (DISSENT-2 ADR-0034 mis-cite; v1 invariant clarification gap; F-7 single-instance) | transform | DISSENT-2 carry-through applied across Blueprint + ADR-0044 + plan-author scope; v1 invariant clarification in D-004; F-7 honored via FR-6-d AC. | synthesis §5.4; cc-design-review-issues.json I-DR-001/I-DR-002 |
| FD-17 | `open_questions_for_human` (OQ-CR-003 skills self-reference; OQ-CR-004 reconciler memory; OQ-CR-005 v1 invariant interpretation) | resolved via Q-CC-N dispositions | Q-CC-3 preserve with rationale (AC-CC-3); Q-CC-5 preserve memory: project; Q-CC-4 accept logical-owner clarification. | cc-design.md §15 + this Blueprint's Decision Record |
| FD-18 | Newly-surfaced ADR-0042 (auditing-mcp graduation) | out-of-scope (N/A — orthogonal) | Grep verification: zero references to execute-* agents. ADR-0042 scopes auditing-skill family relationships; no constraint on dispatch mechanism. Disposition documented in this Blueprint per I-DR-010 absorption. | adrs/ADR-0042-auditing-mcp-family-graduation.md (Grep); cc-design-review-issues.json I-DR-010 |
| FD-19 | Newly-surfaced ADR-0043 (auditing-mcp Gate-6 hard gate) | out-of-scope (N/A — orthogonal) | Grep verification: zero references to execute-* agents. ADR-0043 scopes Gate-6 hard-gate for MCP auditing findings; no constraint on execution-phase dispatch. Disposition documented per I-DR-010 absorption. | adrs/ADR-0043-auditing-mcp-gate-6-hard-gate.md (Grep); cc-design-review-issues.json I-DR-010 |

## Design

### Change Impact Map

```yaml
Change Target: execution-phase dispatch mechanism (cc layer)
Direct Impact:
  cc:
    - .claude/skills/recipe-feature-pipeline/SKILL.md: add "Execution Phase Dispatch" section (D-001); close schema-reference gap at lines 96-128 (D-004)
    - .claude/agents/execute-orchestrator.md: re-scope to advisor (frontmatter Agent + TaskUpdate removed; body re-framed)
    - .claude/agents/execute-task-code-producer.md: body prose only (dispatcher reference)
    - .claude/agents/execute-task-quality-handler.md: body prose only (dispatcher reference)
    - .claude/agents/execute-phase-quality-reviewer.md: body prose only (dispatcher reference)
    - .claude/agents/execute-finalize-reconciler.md: Agent removed; body re-framed; 3 ADR-0034 -> ADR-0033 corrections (lines 3, 19, 82)
    - .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md: v1 invariant clarification; void / -prime extension folding (outside FR-4 inventory; 1 AC-FR-4-a open item)
    - adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md: new
    - adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md: new
Indirect Impact:
  - Every future feature pipeline execution exercises the new dispatch loop.
  - Audit-trail consumers (state-transitions.log readers) see one entry per specialist boundary with invoking_agent preserved as logical owner.
  - checkpoint.json execution-phase fields become documented v1 schema rather than de-facto.
No Ripple Effect:
  - The 34 sub-agents NOT in the FR-5 inventory sweep are unaffected.
  - The four specialists' substantive domain responsibilities (Contract 1, Contract 2, Contract 4 dispatch-matrix definitions) are unchanged.
  - Planning-phase sub-agents (intake-, design-, plan-, finalize-, test-, review-) are unaffected.
  - In-flight devcontainer-mcp-provisioning-r1 artifacts are unchanged per NFR-6-a.
  - MCP server configuration, hooks, and CLAUDE.md are unchanged.
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|---|---|---|---|
| `execute-orchestrator` dispatches the 4 specialists via `Agent` (defective; runtime no-op) | Parent `recipe-feature-pipeline/SKILL.md` dispatches the 4 specialists via `Agent` at main-conversation level | Yes — dispatch moves up one level | Same Agent tool; same payload contracts; logical-owner-vs-emitter re-interpretation of `invoking_agent` |
| `execute-finalize-reconciler` dispatches Contract-4 targets via `Agent` (would have been defective at runtime) | `execute-finalize-reconciler` emits `dispatch_directives[]` array in `quality-reconciliation-log.json`; parent reads array and dispatches each named target via `Agent` | Yes — indirection introduced | New JSON field (`dispatch_directives[]`); parent gains a new read step before each reconciliation-cycle dispatch |
| `checkpoint.json` execution-phase fields (de-facto only) | Same fields documented as v1 schema in `recipe-feature-pipeline/SKILL.md` lines 96–128 | No (documentation-only) | `execution_mode: "single-agent-fallback"` value preserved as v1 compatibility marker for in-flight workaround artifacts |
| `state-transitions.log` per-entry `void` / `void_reason` and `-prime` suffix (de-facto only) | Same fields documented as v1 extensions in `state-transitions-log-entry-template.md` | No (documentation-only) | In-flight log entries remain valid; new entries follow documented v1 |
| `state-transitions-log-entry-template.md:63` v1 invariant: "`invoking_agent` always `execute-orchestrator`" | Same invariant clarified: `invoking_agent` is the LOGICAL OWNER of the transition (always `execute-orchestrator` in v1, even when emitted by the parent on its behalf) | No (clarification) | In-flight log entries' value `"execute-orchestrator"` remains correct under the clarified semantics |

### Architecture Overview

The execution-phase dispatch model under option (a):

```
                   [ Main conversation / user ]
                              │
                              │ invokes /feature-pipeline
                              ▼
        ┌─────────────────────────────────────────────────────┐
        │ recipe-feature-pipeline/SKILL.md (parent orchestrator)│
        │                                                     │
        │  Stages 1..13 (planning + design + plan + audits)   │
        │  Gate 6 (Deliverable approved)                      │
        │                                                     │
        │  NEW: Execution Phase Dispatch                      │
        │  ───────────────────────────                        │
        │  Per-task loop:                                     │
        │   T0 → T1 dispatch code-producer ──────────────────►├──► .claude/agents/execute-task-code-producer.md
        │   T2 dispatch quality-handler ─────────────────────►├──► .claude/agents/execute-task-quality-handler.md
        │   T3/T4 verdict loop                                │
        │   T5 STUB escalation                                │
        │                                                     │
        │  Per-phase loop:                                    │
        │   T7 dispatch phase-quality-reviewer ──────────────►├──► .claude/agents/execute-phase-quality-reviewer.md
        │   T9 dispatch finalize-reconciler ─────────────────►├──► .claude/agents/execute-finalize-reconciler.md
        │   ◄──── dispatch_directives[] in                    │
        │         quality-reconciliation-log.json             │
        │   T10 iterate over directives, dispatch named       │
        │        targets via Agent                            │
        │                                                     │
        │  Cycle-cap (per-task, per-phase, ADR-0017 + 0033):  │
        │   read/write checkpoint.json                        │
        │     .execution_pipeline_cycle_counters              │
        │                                                     │
        │  State-transition log emission:                     │
        │   invoke auditing-shared/log_state_transition.py    │
        │   (invoking_agent preserved as logical owner        │
        │    "execute-orchestrator" per v1 invariant)         │
        │                                                     │
        │  Termination: T12 → write pipeline-run-summary.json │
        └─────────────────────────────────────────────────────┘
                              │
                              │ references for narrative
                              ▼
        ┌─────────────────────────────────────────────────────┐
        │ .claude/agents/execute-orchestrator.md (ADVISOR)    │
        │  - Canonical state-machine reference                │
        │  - 14-row T0..T13 transition narrative              │
        │  - Per-task / per-phase loop semantics              │
        │  - NOT invoked at runtime                           │
        │  - tools: [Read, Glob, Grep, Write, Bash(python3:*)]│
        │    (no Agent; no TaskUpdate)                        │
        └─────────────────────────────────────────────────────┘
```

Sub-agent → sub-agent dispatch (the original defect's design intent) is replaced by main-conversation → sub-agent dispatch, which IS supported per T-001 Finding F-1.

### Data Flow

End-to-end per-task lifecycle under the repaired mechanism:

```
1. Parent skill reads next task from tasks.json (DAG-ordered).
2. Parent verifies task dependencies are APPROVED in checkpoint.json.
3. Parent invokes auditing-shared/log_state_transition.py with T0 (task entering execution).
4. Parent dispatches execute-task-code-producer via Agent at main-conversation level.
   - Payload: { task spec from tasks.json + revision_context (if revision cycle) }
   - Specialist returns per-task-execution-result.{json,md} pair with status enum.
5. Parent invokes log_state_transition.py with T1 (code-producer dispatched).
6. On COMPLETED: parent dispatches execute-task-quality-handler via Agent.
   - Payload: { pointer to per-task-execution-result.json + task spec + modified files }
   - Specialist returns Contract 1 verdict object.
7. Parent reads verdict:
   - APPROVED → log T3; advance to next task.
   - NEEDS_REVISION → log T4; increment checkpoint.json.execution_pipeline_cycle_counters.per_task[<task-id>]; if counter == 4: log T13 with trigger: cycle-cap-exhaustion + write escalation-cycle-cap.json + surface to user. Otherwise: re-dispatch code-producer with revision_context.
   - STUB_DETECTED → log T5; escalate per D-2d.
   - BLOCKER → log T13; escalate to user.
8. When all tasks in current phase APPROVED: parent dispatches execute-phase-quality-reviewer via Agent (T7).
9. Phase verdict:
   - PASS → log T8; advance to next phase or T12 (pipeline_complete).
   - NEEDS_RECONCILIATION → parent dispatches execute-finalize-reconciler via Agent (T9).
     - Reconciler returns quality-reconciliation-log.{json,md} pair with dispatch_directives[] array.
     - Parent iterates dispatch_directives[]; for each row: log T10; increment per_phase counter; dispatch named target via Agent with revision_context.
     - Cycle-cap check on per_phase counter (same logic as per_task).
   - BLOCKER → escalate to user.
10. On T12 (pipeline_complete): parent writes pipeline-run-summary.json; updates checkpoint.json.current_stage = "complete".
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|---|---|---|---|---|---|
| Dispatch of code-producer | recipe-feature-pipeline/SKILL.md (new section) | execute-orchestrator → Agent (no-op at runtime) | parent skill → Agent at main-conversation | Direct refactor; advisor file ceases to be invoked | FR-6 synthetic test verifies one state-transitions.log entry per dispatch boundary |
| Dispatch of quality-handler | (same) | (same) | (same) | (same) | (same) |
| Dispatch of phase-quality-reviewer | (same) | (same) | (same) | (same) | (same) |
| Dispatch of finalize-reconciler | (same) | (same) | (same) | (same) | (same) |
| Reconciliation re-dispatch | (same) | finalize-reconciler → Agent (would have failed at runtime) | finalize-reconciler emits dispatch_directives[]; parent dispatches per row | New `dispatch_directives[]` field in quality-reconciliation-log.json | FR-6 synthetic test exercises NEEDS_RECONCILIATION path if test design includes one |
| State-transition log emission | parent skill | execute-orchestrator body invoked log_state_transition.py | parent skill invokes log_state_transition.py | Move invocation site; script unchanged | Per-dispatch log entry asserted by AC-FR-6-a |

### Main Components

#### Component 1 — Parent orchestrator's Execution Phase Dispatch section (new in `recipe-feature-pipeline/SKILL.md`)

- **Responsibility:** drive the 14-row T0..T13 state machine after Gate 6; dispatch the four specialists via `Agent` at the main-conversation level; emit per-transition state-transition log entries via `auditing-shared/log_state_transition.py`; read/write per-task and per-phase cycle counters in `checkpoint.json.execution_pipeline_cycle_counters`; consume `dispatch_directives[]` from `quality-reconciliation-log.json` during phase reconciliation; terminate cleanly at T12.
- **Interface:** invoked automatically after Gate 6 approval within the same pipeline run; no user-invoked entry point. Reads `tasks.json` (DAG), `blueprint-v<N>.md`, `phase-validators.md`, `acceptance-tests.md`. Writes `state-transitions.log` (JSONL), `pipeline-run-summary.json`, `checkpoint.json`.
- **Dependencies:** the four specialist sub-agents (intra-cc dispatch); the advisor file `execute-orchestrator.md` (documentation reference, not runtime dispatch); `auditing-shared/scripts/log_state_transition.py` (Bash invocation).

#### Component 2 — State-machine advisor (`execute-orchestrator.md` re-scoped)

- **Responsibility:** document the canonical 14-row state machine, the per-task loop, the per-phase loop, the cycle-cap escalation, and the dispatch-matrix routing for the reader (human or downstream agent consulting the file). NOT a runtime dispatcher.
- **Interface:** read-only reference. Linked from `recipe-feature-pipeline/SKILL.md`'s Execution Phase Dispatch section.
- **Dependencies:** none at runtime (file is not invoked). The `skills:` array continues to declare `recipe-feature-pipeline` for documentation lineage (Q-CC-3 preserve disposition); the body explicitly justifies the self-reference for SA-13 audit traceability (AC-CC-3).

#### Component 3 — `execute-finalize-reconciler` (re-framed)

- **Responsibility:** classify phase-quality findings against the 8-row Contract 4 dispatch matrix; emit a `dispatch_directives[]` array in `quality-reconciliation-log.json` per row; track 4-cycle reconciliation budget per ADR-0017 + ADR-0033 symmetric D-12 application; surface cycle-cap exhaustion. **Does NOT dispatch via `Agent`** — the parent orchestrator consumes the directives and dispatches.
- **Interface:** dispatched by parent at T9 with `phase-quality-report.json` (NEEDS_RECONCILIATION verdict), current cycle counter, and feature-artifact pointers. Returns `quality-reconciliation-log.{json,md}` pair including the new `dispatch_directives[]` array.
- **Dependencies:** `auditing-shared` (skill binding preserved per ADR-0035); `memory: project` (preserved per Q-CC-5 disposition; budget-tracking within a single dispatch).

#### Component 4 — The three other specialists (substantively unchanged)

- **Responsibility (`execute-task-code-producer`):** author code per task spec; return Contract 1 result. UNCHANGED.
- **Responsibility (`execute-task-quality-handler`):** issue quality verdict per Contract 1 (APPROVED / NEEDS_REVISION / STUB_DETECTED / BLOCKER). UNCHANGED.
- **Responsibility (`execute-phase-quality-reviewer`):** issue 5-dimensional phase verdict per Contract 2. UNCHANGED.
- **Interface:** dispatched by parent (was: by execute-orchestrator). Payload contracts unchanged.
- **Dependencies:** unchanged.

### Contract Definitions

The Contract 1, Contract 2, Contract 4, and Contract 5 definitions from the existing Blueprint v5 corpus (planning side) are preserved. The new contract this Blueprint introduces is the dispatch-directives indirection.

**Contract 6 — Dispatch directives indirection (NEW under option (a))**

`execute-finalize-reconciler` emits `quality-reconciliation-log.json` containing:

```json
{
  "phase": "<phase-id>",
  "cycle": <integer>,
  "budget_used": <integer>,
  "budget_remaining": <integer>,
  "dispatch_directives": [
    {
      "dispatch_target": "<agent-name | escalate-to-user>",
      "revision_context": { ... },
      "rationale": "<one-paragraph>"
    }
  ],
  "consolidated_by_target": { ... },
  "scope_deviations_resolved": [],
  "cycle_cap_reached": false
}
```

The parent orchestrator reads `dispatch_directives[]` and invokes each named target via `Agent` at the main-conversation level. If the array is empty or malformed, the parent surfaces an error to the user (AC-CC-4) and treats the situation as cycle-cap-equivalent escalation (does NOT silently fall back to a default dispatch).

### Data Contract

**Component 1 — Execution Phase Dispatch section (per-task loop):**

```yaml
Input:
  Type: tasks.json (DAG); checkpoint.json (cycle counters + state); blueprint Components 2-6 contracts
  Preconditions: Gate 6 PASSED; current_stage = "complete" pre-execution; tasks.json well-formed
  Validation: tasks.json frontmatter validated by auditing-shared/validate_pipeline_frontmatter.py

Output:
  Type: state-transitions.log (JSONL); checkpoint.json updates; pipeline-run-summary.json (at T12)
  Guarantees: one log entry per state transition; invoking_agent = "execute-orchestrator" (logical owner); per-task and per-phase counters increment only at T4 and T10 respectively (per I-AA-609 invariant 10)
  On Error: cycle-cap exhaustion → T13 TERMINATED + escalation-cycle-cap.json + user surface; malformed dispatch_directives[] → user surface (AC-CC-4)

Invariants:
  - Each specialist is dispatched in its own sub-agent context (Contract 5 isolation).
  - Per-task counter increments at T4 (NEEDS_REVISION); per-phase counter increments at T10 (phase reconciliation cycle).
  - T0 and T13 are logged but do NOT increment counters.
  - invoking_agent is "execute-orchestrator" across all entries in v1 (logical owner clarification).
```

### Field Propagation Map

| Field | Boundary | Status | Detail |
|---|---|---|---|
| `task spec` | parent skill → execute-task-code-producer | preserved | Unchanged from existing Contract 1 input |
| `per-task-execution-result.json` | execute-task-code-producer → parent skill → execute-task-quality-handler | preserved | Unchanged |
| `Contract 1 verdict` | execute-task-quality-handler → parent skill | preserved | Unchanged |
| `phase-quality-report.json` | execute-phase-quality-reviewer → parent skill → execute-finalize-reconciler | preserved | Unchanged |
| `dispatch_directives[]` | execute-finalize-reconciler → parent skill → dispatched targets | NEW | Indirection introduced under option (a) |
| `revision_context` | parent skill (from dispatch_directives[]) → re-dispatched target | preserved (relocated) | Was emitted directly by reconciler under defective design; now flows via parent |
| `invoking_agent` | parent skill → log_state_transition.py → state-transitions.log | preserved (clarified semantics) | Logical owner = "execute-orchestrator" in v1 |
| `cycle_counter` | parent skill ↔ checkpoint.json.execution_pipeline_cycle_counters | preserved (relocated) | Was via memory: project shared between orchestrator and reconciler; now in canonical checkpoint location read/written by parent |

### State Transitions and Invariants

The 14-row T0..T13 state machine is preserved as canonical (advisor file `execute-orchestrator.md` is the reference). New under option (a):

- T0 (task pending → active): logged by parent; counter NOT incremented.
- T1 (code-producer dispatched): logged by parent.
- T2 (quality-handler dispatched): logged by parent.
- T3 (APPROVED): logged by parent; advance.
- T4 (NEEDS_REVISION): logged by parent; per_task counter incremented; re-dispatch code-producer.
- T5 (STUB_DETECTED): logged by parent; escalate per D-2d.
- T7 (phase-quality-reviewer dispatched): logged by parent.
- T8 (PASS): logged by parent; advance.
- T9 (finalize-reconciler dispatched): logged by parent.
- T10 (phase reconciliation cycle complete; iterate dispatch_directives[]): logged by parent; per_phase counter incremented.
- T12 (pipeline_complete): write pipeline-run-summary.json; checkpoint current_stage = "complete".
- T13 (TERMINATED): cycle-cap-exhaustion OR user-escalation OR BLOCKER; counter NOT incremented.

**System Invariants:**

- A specialist sub-agent is invoked exactly once per dispatch boundary (Contract 5 isolation; ADR-0044 carry-through).
- The 4-cycle cap (ADR-0017) applies symmetrically (ADR-0033 D-12) at per-task (T4) and per-phase (T10) boundaries.
- `invoking_agent` in state-transitions.log entries is "execute-orchestrator" (v1 logical-owner invariant).
- No sub-agent's `tools:` array contains `Agent` (ADR-0045).

---

### Claude Code / Project Filesystem Design

This is the sole activated layer. The per-layer cc-design subsection produced by `design-cc` is integrated below with extensions absorbing the reviewer's IMPORTANT findings.

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | Parent orchestrator skill; gains new "Execution Phase Dispatch" section (D-001) AND closes canonical `checkpoint.json` schema-reference gap (D-004 — lines 96–128) | **modified** (additive; ~3 PW combined; edit order: D-004 schema closure FIRST, then D-001 dispatch-section absorption per I-DR-004) |
| `.claude/agents/execute-orchestrator.md` | Re-scoped from dispatcher to **state-machine advisor**. `Agent`, `TaskUpdate` removed from `tools:`. Body re-framed; explicit prose rationale added for the `recipe-feature-pipeline` self-reference in `skills:` (AC-CC-3) | **modified** (frontmatter + body re-framing + rationale comment) |
| `.claude/agents/execute-task-code-producer.md` | Substantive responsibilities unchanged. Body's "dispatched by execute-orchestrator" updated to "dispatched by recipe-feature-pipeline parent orchestrator" | **modified** (prose-only) |
| `.claude/agents/execute-task-quality-handler.md` | Same as code-producer | **modified** (prose-only) |
| `.claude/agents/execute-phase-quality-reviewer.md` | Same as code-producer | **modified** (prose-only) |
| `.claude/agents/execute-finalize-reconciler.md` | `Agent` removed from `tools:` (D-003). **All three** ADR-0034 references corrected to ADR-0033 (lines 3, 19, 82) per I-DR-001 absorption. Body line 76 "Dispatch via Agent" re-framed to "emit `dispatch_directives[]` in `quality-reconciliation-log.json`" | **modified** (frontmatter + body re-framing + 3-occurrence ADR citation sweep) |
| `working/feature/<slug>/checkpoint.json` schema (canonical reference) | Documented in `recipe-feature-pipeline/SKILL.md:96–128`. Gains 3 new execution-phase fields plus their value semantics | **modified** (canonical-reference update in lockstep with §4 — D-004) |
| `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` per-entry schema | v1 `invoking_agent` invariant at line 63 is **clarified, not changed** (logical owner). De facto `void` / `void_reason` and transition-name `-prime` suffix folded into v1 documentation. TWO distinct sub-edits: (a) invariant clarification per §5; (b) extension folding per §5 (I-DR-008 absorption — split for Fact Disposition Table clarity) | **modified** (outside FR-4 inventory; 1 file → AC-FR-4-a open-item count = 1) |

#### CLAUDE.md Updates

| File | Change | Rationale |
|---|---|---|
| Root `CLAUDE.md` | **No change** | The dispatch repair is project-internal mechanism. The convention captured in ADR-0045 is enforced via ADR scope + future audit-extension; not via every-request CLAUDE.md reminder (KB-cc-design Principle 5 — one source of truth). |

#### Slash Commands

No slash commands added or modified.

#### Hooks

| Hook Event | Script | Behavior | Failure Mode | Change |
|---|---|---|---|---|
| State-transition emission | `.claude/skills/auditing-shared/scripts/log_state_transition.py` | Bash-invoked from the parent orchestrator's per-transition step; writes one JSONL line to `working/feature/<slug>/state-transitions.log` | Observer-only per D-16; failure surfaces as Level-1 finding per AC-FR-5-e but does NOT block the substantive transition | **unchanged** — invocation site moves from `execute-orchestrator` body to the parent skill's Execution Phase Dispatch section; script and REQUIRED_FIELDS unchanged |

#### Skills

| Skill | Location | When Triggered | What It Provides | Change |
|---|---|---|---|---|
| `recipe-feature-pipeline` | `.claude/skills/recipe-feature-pipeline/SKILL.md` | User invokes `/feature-pipeline` (parent orchestrator) | Full 13-stage pipeline + new Execution Phase Dispatch section; canonical `checkpoint.json` schema reference | **modified** (D-001 + D-004; load-bearing single-file pressure per synthesis Constraint 5.1) |

No new skills introduced. Per KB-cc-design Principle 1 (lowest-cost primitive), the new dispatch behavior fits inside the existing parent skill rather than a new skill — there is no separate user-invoked entry-point.

#### Sub-Agents

| Sub-Agent | Location | Phase | What It Does | Change |
|---|---|---|---|---|
| `execute-orchestrator` | `.claude/agents/execute-orchestrator.md` | execution-phase | **Re-scoped to state-machine advisor.** Canonical 14-row state-machine narrative. Not dispatched at runtime. | frontmatter (`Agent` + `TaskUpdate` removed); body re-framing |
| `execute-task-code-producer` | `.claude/agents/execute-task-code-producer.md` | execution-phase | Authors code per task spec; Contract 1 result | body prose only |
| `execute-task-quality-handler` | `.claude/agents/execute-task-quality-handler.md` | execution-phase | Issues Contract 1 verdict | body prose only |
| `execute-phase-quality-reviewer` | `.claude/agents/execute-phase-quality-reviewer.md` | execution-phase | Issues 5-dimensional Contract 2 verdict | body prose only |
| `execute-finalize-reconciler` | `.claude/agents/execute-finalize-reconciler.md` | execution-phase | Classifies phase-quality findings; emits `dispatch_directives[]` (NEW under option (a)) | frontmatter (`Agent` removed); body re-framing (lines 19, 76); 3-occurrence ADR-0033 sweep (lines 3, 19, 82) |

**Per-sub-agent reasoning configuration** (per ADR-0022, KB-cc-design Principle 9). All triplets preserved; no reasoning-configuration changes:

| Sub-Agent | `model:` | `effort:` | `skills:` | Verdict |
|---|---|---|---|---|
| `execute-orchestrator` | `opus` | `high` | `[KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]` | **PRESERVED**. Triplet retained despite advisor role — reversal of option (a) would require re-invocation; preserving the triplet keeps reversal cheap (I-DR-009 absorption). |
| `execute-task-code-producer` | `sonnet` | `medium` | `[ai-development-guide, KB-cc-design]` | PRESERVED |
| `execute-task-quality-handler` | `sonnet` | `medium` | `[ai-development-guide, KB-cc-design, auditing-shared]` | PRESERVED |
| `execute-phase-quality-reviewer` | `opus` | `high` | `[KB-cc-design, KB-review-disciplines, auditing-shared]` | PRESERVED |
| `execute-finalize-reconciler` | `opus` | `high` | `[KB-cc-design, KB-review-disciplines, auditing-shared]` | PRESERVED |

#### MCP Servers

| Server | Configuration | Change |
|---|---|---|
| (existing servers per `.mcp.json`) | unchanged | **No change** — option (a) does not interact with MCP. |

#### File Naming & Layout Conventions Introduced

- **ADR-0045 convention (NEW):** sub-agents in this project MUST NOT declare `Agent` in their `tools:` frontmatter array. Applies to all `.claude/agents/*.md`. Enforcement: manual review interim; SA-13-style audit extension deferred to follow-on feature.
- No other naming or layout conventions introduced.

#### Project Filesystem Error State Design

How the feature behaves when expected Claude Code constructs are missing or malformed:

- **`execute-orchestrator.md` missing or unreadable.** The advisor file is a documentation surface, not a dispatchable agent. The parent orchestrator's Execution Phase Dispatch section references it for the canonical state-machine narrative; if missing, the parent surfaces a clear "advisor reference missing" error at Step 15 entry (before any dispatch). Plan-author implements a precondition check.
- **One of the four specialists missing.** The harness reports the missing agent in its loaded-agent-set error message (per T-001 F-7 finding). The parent surfaces this to the user before dispatching. Per F-7, no in-pipeline hot-reload remedy; the operator restarts the session.
- **`checkpoint.json` malformed (e.g., missing `execution_pipeline_cycle_counters`).** The parent orchestrator initializes the field with the documented v1 schema on first execution-phase entry. Pre-existing in-flight artifacts (per NFR-6-a) are left as-is.
- **`auditing-shared/scripts/log_state_transition.py` fails.** Per D-16, observer-only; transition proceeds, failure surfaces as Level-1 finding.
- **`dispatch_directives[]` malformed or empty** (NEW per AC-CC-4 / I-DR-005 absorption). The parent surfaces to the user; treats as cycle-cap-equivalent escalation. The parent does NOT silently fall back to a default dispatch.

### Other Layers

- **Frontend Design** — N/A — out of scope.
- **Backend Design** — N/A — out of scope.
- **API Design** — N/A — out of scope.
- **Query & Data Access Design** — N/A — out of scope.
- **Database Schema & Migration Design** — N/A — out of scope.
- **CI/CD Design (GitHub Actions)** — N/A — out of scope.
- **Infrastructure as Code Design** — N/A — out of scope.
- **Dev Environment (Codespaces) Design** — N/A — out of scope.

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---|---|---|---|---|
| Pipeline (dispatch loop) | Specialist sub-agent file missing from registry | Harness error at dispatch attempt | Surface to user with the harness error message; per F-7, no hot-reload remedy — operator restarts session | Pipeline halts; clear surface message |
| Pipeline (cycle cap) | Per-task counter reaches 4 without resolution | Parent's counter check before re-dispatch | Halt run; emit T13 TERMINATED with `trigger: cycle-cap-exhaustion`; write `escalation-cycle-cap.json`; surface to user | Pipeline halts at well-defined boundary; user sees cycle history |
| Pipeline (malformed dispatch_directives[]) | Reconciler returns empty or invalid array | Parent's read of `quality-reconciliation-log.json` | Surface to user; treat as cycle-cap-equivalent escalation; do NOT silently fall back | Pipeline halts; user sees the malformed-directive context |
| Pipeline (log emission failure) | `log_state_transition.py` non-zero exit | Bash exit code | Observer-only per D-16; substantive transition proceeds; failure recorded as Level-1 finding | No pipeline halt; finding surfaced at phase quality review |
| Schema (checkpoint malformed) | Missing `execution_pipeline_cycle_counters` | Parent's read on first execution-phase entry | Initialize field with documented v1 schema; proceed | No pipeline halt; one-time init |

### Logging and Monitoring

- **Log events:** state transitions (T0..T13) via `state-transitions.log` JSONL; cycle-counter increments via `checkpoint.json`; pipeline completion via `pipeline-run-summary.json`.
- **Log levels:** N/A — single-tenant pipeline-internal artifacts; no log-level taxonomy.
- **Sensitive data:** none in scope.
- **Metrics:** N/A — no monitoring service consumes pipeline-internal artifacts.
- **Traces:** N/A.
- **Alerts:** N/A.
- **Dashboards:** N/A.

## Implementation Plan

### Implementation Approach

**Selected Approach:** flatten dispatch hierarchy (option (a)) per ADR-0044.

**Selection Reason:** see ADR-0044 §Rationale — three load-bearing reasons (FR-4 inventory; v1 invariant preservation; specialist-isolation) plus joint framer-and-substrate recommendation from synthesis §3.1.

### Technical Dependencies and Implementation Order

#### Required Implementation Order

1. **Phase 0 — Schema closure on `recipe-feature-pipeline/SKILL.md` (D-004)**
   - Layer: Claude Code
   - Technical Reason: the canonical `checkpoint.json` schema reference (lines 96–128) must be stable before the dispatch section can cite the new fields. Per I-DR-004 absorption and synthesis Constraint 5.1, **schema closure precedes dispatch-section absorption** (load-bearing ordering).
   - Dependent Elements: Phase 1 (dispatch section absorption); Phase 2 (state-transitions-log-entry-template.md extension folding).

2. **Phase 1 — Dispatch section absorption into `recipe-feature-pipeline/SKILL.md` (D-001)**
   - Layer: Claude Code
   - Technical Reason: with the schema reference stable, the new Execution Phase Dispatch section can reference the documented fields (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`) without forward references.
   - Prerequisites: Phase 0 complete.

3. **Phase 2 — Sub-agent file edits (bundled `Agent`-removal commit)**
   - Layer: Claude Code
   - Technical Reason: bundles the two `Agent`-removals (`execute-orchestrator.md` + `execute-finalize-reconciler.md`) into a single commit per synthesis Constraint 5.2; bundles the 3-occurrence ADR-0034 → ADR-0033 sweep on `execute-finalize-reconciler.md` (per I-DR-001 absorption) into the same commit; bundles body-prose updates on the three other specialists.
   - Prerequisites: Phase 1 complete (so the dispatch section is the authoritative reference for the dispatcher-prose updates).

4. **Phase 3 — `state-transitions-log-entry-template.md` extension folding**
   - Layer: Claude Code
   - Technical Reason: outside FR-4 inventory (1 AC-FR-4-a open item); the v1 invariant clarification and `void` / `-prime` extension folding are documentation-only and should be applied after the schema closure is stable.
   - Prerequisites: Phase 0 complete.

5. **Phase 4 — FR-5 inventory artifact + ADR-0045 placement**
   - Layer: Claude Code
   - Technical Reason: AC-FR-5-b inventory artifact records the FR-5 sweep result (36 files; 2 violations cleaned). ADR-0045 is already in place at `adrs/`; the inventory artifact cross-references it.
   - Prerequisites: Phases 0–3 complete.

6. **Phase 5 — FR-6 verification (synthetic minimal test feature)**
   - Layer: Claude Code
   - Technical Reason: per FR-6 / AC-FR-6-d, this phase runs the dispatch loop end-to-end. F-7 mid-session-agent-registry constraint: if plan-author's synthetic test design authors any new sub-agent file, this phase MUST cross a session boundary.
   - Prerequisites: Phases 0–4 complete.

#### Cross-Layer Sequencing Notes

- N/A — single-layer feature.

### Migration Strategy

No data migration. In-flight `devcontainer-mcp-provisioning-r1` artifacts remain as-shipped per NFR-6-a. New-format artifacts produced by post-repair runs are distinguishable via the `execution_mode` field value: "single-agent-fallback" for the workaround run; "specialist-isolation" for new runs.

### Feature Flags & Rollout

No feature flags. The repair is applied once across the affected files; the next post-repair execution-phase run exercises the new dispatch loop.

## Security Considerations

Evaluate per layer in scope. All other layers N/A.

### Cross-Cutting

- **Authentication & Authorization:** N/A — no new entry points, no auth surface affected.
- **Input Validation:** the parent orchestrator validates `dispatch_directives[]` shape before dispatching each row; malformed entries surface to user (AC-CC-4).
- **Sensitive Data Handling:** none; pipeline-internal state artifacts only.

### Claude Code

- **Sub-agent tool grants:** ADR-0045 codifies the prohibition on `Agent` in sub-agent `tools:` arrays. Audit-extension to enforce automatically is deferred.
- **Hook safety:** no new hooks; existing `log_state_transition.py` is observer-only per D-16.
- **MCP exposure:** unchanged.

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---|---|---|
| Claude Code harness | No | Verification IS the harness behavior; the synthetic test feature exercises real dispatch. |
| Specialist sub-agents | No | Each specialist's substantive responsibilities are preserved; the test exercises them as-is. |
| `log_state_transition.py` | No | Observer hook; failure is non-blocking per D-16; verify real emission. |
| `checkpoint.json` | No | Read/write the real file; verify counter increments at correct boundaries. |

### Data Layer Testing Strategy

N/A — no data layer.

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|---|---|---|---|
| Claude Code | functional (FR-6 synthetic minimal test feature dispatch loop) | The feature-pipeline itself running against the synthetic test | `working/test-features/<test-feature-slug>/` (plan-author determines exact path per NFR-7) |

### Integration Verification Points

- The four specialist sub-agents are dispatchable from the parent at the main-conversation level (per T-001 Finding F-1).
- `dispatch_directives[]` shape conforms to the documented schema (the parent reads it; specialist emits it).
- Cycle-counter increments happen at T4 (per_task) and T10 (per_phase), not at T0 or T13 (per I-AA-609 invariant 10).
- `state-transitions.log` emits one JSONL line per state transition with `invoking_agent: "execute-orchestrator"` preserved as logical-owner invariant.

## Verification Strategy

### Correctness Proof Method

- **Correctness definition:** the synthetic minimal test feature runs end-to-end through the repaired dispatch mechanism without stalling at the boundary that produced the original defect; one `state-transitions.log` entry emits per specialist dispatch boundary; per-task and per-phase cycle counters increment at T4 and T10 respectively in `checkpoint.json`; cycle-cap (4) halt path exercises correctly if the test is designed to invoke a NEEDS_RECONCILIATION path.
- **Verification method:** plan-author authors a 1-phase / 1–2-task synthetic test feature; the test is run end-to-end against the repaired mechanism; the log + checkpoint are inspected against the AC-FR-6-a/b/c criteria.
- **Verification timing:** Phase 5 of this implementation plan; after Phases 0–4 complete. Across a session boundary per AC-FR-6-d if the synthetic test design authors any new sub-agent file.

### Early Verification Point

- **First verification target:** a minimal 1-task synthetic feature exercises the per-task dispatch loop (T0 → T1 → T2 → T3) end-to-end.
- **Success criteria:** `state-transitions.log` contains at least one entry per transition; `checkpoint.json` reflects task-completion state; `invoking_agent` value is `"execute-orchestrator"` across all entries.
- **Failure response:** per AC-FR-6-c, surface `verification-failed` posture; per-layer cc Design is re-engaged.

### Output Comparison

N/A — the repair replaces a defective behavior with a working one (rather than transforming output of an existing working behavior). Verification is functional (dispatch loop completes) not output-comparison-based.

### Operational Verification

- **Pre-merge gates:** Gate 6 of the parent skill (Deliverable approved); this Blueprint's `shared-document-reviewer` Gate 0/1 verdict; `review-architecture-auditor` substantive audit.
- **Post-deploy verification:** N/A — not a deployed service.
- **Migration verification:** N/A — no migration.
- **Rollback rehearsal:** the reversal path documented in ADR-0044 §Implementation Guidance covers rollback if a future harness change enables sub-agent → sub-agent dispatch.

## Future Extensibility

- **Extension points:**
  - `dispatch_directives[]` array is forward-compatible for new directive types (extra rows; new optional fields).
  - `execution_mode` field in `checkpoint.json` allows future variants (e.g., a hypothetical "true-nested-dispatch" if the harness ever supports it).
  - The state-transitions-log schema is at v1; future versions can add fields with the parent skill's emission discipline backward-compatible.
- **Known future requirements:** the audit-extension to enforce ADR-0045 automatically (deferred follow-on feature).
- **Intentional limitations:** the advisor pattern for `execute-orchestrator.md` is documentation-driven; if future readers find the advisor-vs-dispatcher framing confusing, a body-prose refresh is the remedy (not a structural change).

## Alternative Solutions

### Alternative 1: Retire `execute-orchestrator` entirely (synthesis §3.1 option b)

- **Overview:** delete `execute-orchestrator.md`; fold the 14-row state machine into `recipe-feature-pipeline/SKILL.md`.
- **Advantages:** single locus of state-machine knowledge; eliminates advisor-vs-dispatcher ambiguity.
- **Disadvantages:** escapes the PRD FR-4 8-file inventory by ≥5 outside-inventory files; breaks the state-transitions-log v1 `invoking_agent` invariant; requires a separate schema-ownership-transfer ADR; roughly 2× effort of option (a) for equivalent functional outcome.
- **Reason for Rejection:** per ADR-0044 — widest AC-FR-4-a operator-gate surface and breaks the v1 invariant. Codebase-analysis blast-radius enumeration confirms 5+ outside-inventory files; synthesis substrate analysis confirms the v1 invariant break.

### Alternative 2: Bash-script dispatch surface (synthesis §3.1 option c)

- **Overview:** `execute-orchestrator` dispatches Bash scripts; scripts invoke specialists via another mechanism.
- **Advantages:** physically possible per T-001 (runtime surface includes `Bash`); preserves `execute-orchestrator` as runtime entity.
- **Disadvantages:** specialists invoked via Bash sub-process bypass the harness's per-agent transcript and state-transitions logging; script becomes the audit boundary, not the agent — degrades the very property the repair must preserve.
- **Reason for Rejection:** per ADR-0044 — same outside-inventory cost as option (a) but lowest pattern fidelity. Real audit-trail loss per source analysis §3.2 / AN-0037.

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|---|---|---|---|---|
| Plan-author inverts the recommended D-004-before-D-001 edit ordering on `recipe-feature-pipeline/SKILL.md` | Claude Code | Medium — schema-references-not-yet-stable risk | Low | Implementation Plan Phase 0 (schema closure) ordered before Phase 1 (dispatch section); ADR-0044 Implementation Guidance reiterates the ordering; I-DR-004 absorption explicit |
| Plan-author misses an ADR-0034 occurrence in `execute-finalize-reconciler.md` | Claude Code | Medium — DISSENT-2 carry-through gap | Low | Blueprint edit list explicitly enumerates all 3 occurrences (lines 3, 19, 82); AC-FR-5-a verbatim names the requirement |
| F-7 mid-session-agent-registry constraint missed during FR-6 verification | Claude Code | High — FR-6 verification fails or is invalid | Low–Medium (depends on plan-author's synthetic test design) | AC-FR-6-d makes the constraint conditional and explicit; plan-author MUST sequence accordingly; cc-dependencies.json captures |
| Reviewer detects an additional ADR-0034 mis-credit elsewhere in the codebase | Claude Code | Low — DISSENT-2 carry-through extension | Low | Architecture-auditor's CoVe-style sweep; if found, surface as a follow-on edit during reconciliation |
| `dispatch_directives[]` malformed at runtime under unexpected reconciler state | Claude Code | Medium — pipeline halt | Low | AC-CC-4 makes the failure mode explicit (surface to user; do NOT silent fall back); error-state design documents the behavior |
| Audit-extension for ADR-0045 never lands in a follow-on feature | Claude Code | Low — convention enforced manually | Medium | ADR-0045 explicitly names the deferred follow-on feature and the manual-review interim; future sub-agent reviews enforce the rule |
| Reversal of option (a) (if a future harness update enables sub-agent → sub-agent dispatch) is more complex than ADR-0044 anticipates | Claude Code | Low — option-a-reversal cost | Low | ADR-0044 §Implementation Guidance preserves the advisor file and its `opus/high` triplet to keep reversal cheap; reversal path documented |

## References

### Decision Record (this Blueprint's explicit decisions)

**§6 option chosen:** **option (a) flatten dispatch hierarchy.** Captured in ADR-0044. Rationale (verbatim from ADR-0044 §Rationale): (1) PRD FR-4 8-file inventory compliance — option (a) touches 3 in-inventory + 1 outside (1 AC-FR-4-a open item) vs option (b)'s ≥5 outside-inventory escape; (2) state-transitions-log v1 `invoking_agent` invariant preservation via logical-owner re-interpretation vs option (b)'s schema-ownership transfer; (3) specialist-isolation audit-trail preservation across four distinct sub-agent boundaries vs option (c)'s Bash-sub-process audit-boundary degradation.

**Q-CC-1 disposition (project-wide convention ADR):** **author the ADR in this feature (option a).** Diverges from synthesis D-005's defer recommendation. Composer rationale: T-001's 3-source citation work and the D-003 cleanup are both shipped in this run; deferring re-incurs the citation work; the convention generalizes the cleanup precedent. Reviewer's I-DR-003 verdict ("well-rationalized — Composer's call") supports the divergence. Captured in ADR-0045.

**Q-CC-2 disposition (explicit inheritance of ADR-0017 / 0033 / 0019 / 0022 in primary ADR):** **explicit inheritance.** ADR-0044's frontmatter `adrs_inherited` field names ADR-0017, ADR-0019, ADR-0022, ADR-0029, ADR-0033, ADR-0035, ADR-0036. The "Related Information" section enumerates each with its load-bearing invariant.

**Q-CC-3 disposition (`execute-orchestrator.md`'s `recipe-feature-pipeline` self-reference in `skills:`):** **preserve with rationale.** AC-CC-3 propagates the requirement to add an explicit body-prose rationale in `execute-orchestrator.md` ("this advisor documents the state machine the parent skill orchestrates; the self-reference is intentional") so future SA-13 audits have file-resident evidence of intentionality (I-DR-006 absorption).

**Q-CC-4 disposition (state-transitions-log v1 `invoking_agent` invariant clarification):** **(a) accept the logical-owner clarification.** The v1 invariant text in `state-transitions-log-entry-template.md:63` is updated to read: "`invoking_agent` is the LOGICAL OWNER of the transition — always `execute-orchestrator` in v1, even when emitted by the parent orchestrator on its behalf." This honors both the in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` artifact's existing values and the v1 invariant.

**Q-CC-5 disposition (`execute-finalize-reconciler`'s `memory: project`):** **preserve.** The reconciler tracks `budget_used` / `budget_remaining` across cycles within a single dispatch (per its workflow §7); the memory declaration is load-bearing for that intra-dispatch budget tracking. Cycle counters move to `checkpoint.json.execution_pipeline_cycle_counters` (parent-owned), but the budget tracking is reconciler-local.

**Q-CC-6 disposition (FR-6 H-a vs H-b sub-question for Edit-tool mechanism):** **defer to test-acceptance-author; non-load-bearing for kill-criterion-#2 closure.** The H-a (baseline-inheritance) vs H-b (memory-field auto-enable) sub-question for the Edit-tool addition observed on `execute-orchestrator`'s runtime surface (analysis §1.2) is surfaced to `test-acceptance-author` via the cross-references. CR-0023 confirms `execute-orchestrator` declares `memory: project`, supporting H-b. A falsifying test (probe agent without `memory:` exhibiting the Edit-tool addition) would settle it. Test-acceptance-author may include or omit the sub-question at their discretion.

**ADR-0042 / ADR-0043 disposition:** **N/A — orthogonal.** Grep verification on both ADRs shows zero references to any execute-* agent. ADR-0042 scopes auditing-skill family relationships; ADR-0043 scopes Gate-6 hard-gate for MCP auditing. Neither constrains the execution-phase dispatch mechanism. Documented in the Fact Disposition Table (FD-18, FD-19) per I-DR-010 absorption.

**ADR-0036 placement disposition:** **honor-adr-0036-canonical-root.** Per user ratification recorded in the orchestrator prompt: both new ADRs (0044, 0045) land at `adrs/` only; no feature-scoped duplicates. This explicitly diverges from the `devcontainer-mcp-provisioning-r1` feature's feature-scoped pattern; the user explicitly chose ADR-0036-canonical root for this feature.

### Rationale Brief

Per ADR-0009 — a rationale brief describing how the Composer weighed evidence and made decisions.

This Blueprint's load-bearing decisions are anchored in three sources, weighted as follows:

1. **T-001 (research note)** carries anchor evidence for the substrate constraint. Three independent Anthropic-controlled primary sources (URLs verified during critique on 2026-05-23) with verbatim quotes establish `dispatch_supported: false`. The Composer treats this as **highest-weight evidence** because: (a) all three sources are Anthropic-controlled and prescriptive ("Don't include Agent in a subagent's tools array"); (b) Anthropic has no incentive to falsely publish a restriction that constrains product expressiveness; (c) exhaustive frontmatter / environment-variable enumeration (T-001 Finding F-4) found no enable-nesting affordance. The absence-of-feature claim is bounded by Anthropic documentation discipline rather than mathematically zero (synthesis §8 limitation), but no countervailing evidence was located.

2. **Codebase-analysis blast-radius enumeration** carries the per-option file-count evidence that distinguishes option (a) from (b). The FR-4 8-file inventory is a hard PRD constraint with AC-FR-4-a operator gate; option (b)'s ≥5 outside-inventory cost is direct evidence that option (a) is FR-4-compliant and option (b) is not. The Composer treats this as **load-bearing for the option choice** (not just framing evidence) because the FR-4 inventory is a user-gated constraint.

3. **Per-layer cc-design Q-CC-N surfaces** carry the Composer-side judgment calls. Of the six Q-CC items, Q-CC-1 is the most consequential (whether to author ADR-0045 in this feature vs defer). The Composer ratifies cc-design's recommendation to author in this feature on the rationale that T-001's citation work and the D-003 cleanup are both shipped here; deferring re-incurs the work. The reviewer's I-DR-003 "well-rationalized — Composer's call" verdict supports this position.

**DISSENT-2 carry-through** is honored explicitly: every reference to the 4-cycle cap and symmetric D-12 application cites ADR-0017 + ADR-0033 (NOT ADR-0034). The Blueprint extends the per-layer cc-design's edit list to cover all 3 occurrences of ADR-0034 on `execute-finalize-reconciler.md` (lines 3, 19, 82) per I-DR-001 absorption.

**F-7 carry-through** is honored conditionally: AC-FR-6-d makes the session-boundary constraint conditional on plan-author's synthetic test design. If plan-author authors no new sub-agents, the constraint is vacuously satisfied; otherwise the two-session pattern (synthesis D-002) applies.

**Edit ordering** on `recipe-feature-pipeline/SKILL.md` is documented as load-bearing per I-DR-004 absorption: schema closure (D-004) FIRST, then dispatch-section absorption (D-001). The synthesis substrate prefers schema closure first to stabilize the documented schema before the dispatch section references it.

### Resolved Q-CC-N Items

| Q-CC-N | Resolution | Location |
|---|---|---|
| Q-CC-1 | Author ADR-0045 in this feature (Composer ratifies cc-design recommendation, diverging from synthesis D-005) | ADR-0045; Decision Record above |
| Q-CC-2 | Explicit inheritance | ADR-0044 frontmatter |
| Q-CC-3 | Preserve self-reference with body-prose rationale | AC-CC-3 |
| Q-CC-4 | Accept logical-owner clarification | `state-transitions-log-entry-template.md:63` edit; D-004 schema closure |
| Q-CC-5 | Preserve `memory: project` on reconciler | Component 3 §Dependencies |
| Q-CC-6 | Defer to test-acceptance-author; non-load-bearing | Decision Record above |

### Unresolved Items

None requiring user input pre-implementation. The audit-extension for ADR-0045 is deferred to a follow-on feature by design (not unresolved; explicitly scoped out).

### Related documentation

- `Issues/analysis-execute-orchestrator-dispatch-limitation.md`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design.md`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design-review-issues.json`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-dependencies.json`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json`
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md`
- `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md` (new)
- `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` (new)

## Update History

| Date | Version | Changes | Author |
|---|---|---|---|
| 2026-05-23 | 1 | Initial Blueprint integrating per-layer cc-design with reviewer's IMPORTANT findings (I-DR-001 extended ADR-0034 sweep; I-DR-003 Q-CC-1 ratification; I-DR-004 edit ordering documented; I-DR-010 ADR-0042/0043 disposition). Authored ADR-0044 (§6 option (a)) and ADR-0045 (project-wide convention). | design-composer |
