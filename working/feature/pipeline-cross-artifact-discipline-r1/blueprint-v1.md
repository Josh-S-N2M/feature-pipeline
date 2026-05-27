---
id: BP-pipeline-cross-artifact-discipline-r1
version: 1.0.0
status: draft
feature_slug: pipeline-cross-artifact-discipline-r1
doc_type: blueprint
derived_from: working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md
codebase_analysis: working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json
adrs_referenced:
  - ADR-0005
  - ADR-0009
  - ADR-0013
  - ADR-0016
  - ADR-0017
  - ADR-0018
  - ADR-0020
  - ADR-0022
  - ADR-0027
  - ADR-0030
  - ADR-0036
  - ADR-0038
  - ADR-0039
  - ADR-0040
  - ADR-0041
  - ADR-0042
  - ADR-0044
  - ADR-0045
  - ADR-0046
  - ADR-0054
  - ADR-0056
adrs_authored:
  - ADR-0059
  - ADR-0060
  - ADR-0061
  - ADR-0062
  - ADR-0063
generated: 2026-05-26T17:30:00Z
generated_by: design-composer
---

# Cross-Artifact + Design-Time Discipline (R2) — Design Document

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

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

**Composer-authored sections specific to this feature** (in addition to the canonical template):

- [x] ADRs Authored in This Run
- [x] Open Items (Q-CC-N) — Composer Arbitration
- [x] Contingency Split Decision Record (Q-CC-1 / D-6)
- [x] §O.1 Row-Count Correction (Q-CC-5) — User-facing Gate 4 item
- [x] Decisions Adopted (D-1 .. D-10) — Final Disposition
- [x] Reasoning-Configuration Audit Table
- [x] Constraint Propagation Check
- [x] Cross-References (Inherited ADRs / Authored ADRs / Q-CC Dispositions)

## Overview

This feature ships **11 mechanisms** at the Claude Code / Project Filesystem layer that lift the pipeline's verification model from per-artifact correctness to **cross-artifact + cross-stage correctness**. Every recurrence path the user named in the rationale brief — the MCP shipment incident, the 28-untouched-agents evaluation gap, and the §O.1 register of unfired post-ship triggers — is a per-artifact validator missing a cross-artifact relationship check. The 11 mechanisms install those relationship checks structurally.

### Layer Scope

Declare which layers this feature touches. Sections under Design, Security, Test Boundaries, and Verification corresponding to unchecked layers may be marked `N/A — out of scope` without further elaboration.

- [x] **Claude Code / Project Filesystem** — KBs (cc-design, documentation-criteria, review-disciplines, task-decomposition, codebase-research, mcp-platform, mcp-design), the `recipe-feature-pipeline` skill, sub-agents (design-cc, discovery-codebase-researcher, review-architecture-auditor, design-composer, intake-prd-author, test-phase-validator-author, execute-orchestrator, cc-critique, synth-synthesizer), audit skills (auditing-mcp, auditing-cc-configs, auditing-subagents, auditing-shared, auditing-skills), the PV-author rubric, and discipline texts governing deferral phrasing.
- [ ] **Frontend** — N/A — out of scope (per user direction; PRD-v2 Layer Scope).
- [ ] **Backend** — N/A — out of scope (per user direction; PRD-v2 Layer Scope).
- [ ] **API** — N/A — out of scope (per user direction; PRD-v2 Layer Scope).
- [ ] **Query / Data Access** — N/A — out of scope (per user direction; PRD-v2 Layer Scope).
- [ ] **Database** — N/A — out of scope (per user direction; PRD-v2 Layer Scope).
- [ ] **CI/CD (GitHub Actions)** — N/A — out of scope (parallel `pipeline-quickwins-hardening-r1` run owns CI workflow changes).
- [ ] **Infrastructure as Code** — N/A — out of scope (per user direction; PRD-v2 Layer Scope).
- [ ] **Dev Environment (Codespaces / Devcontainer)** — N/A — out of scope (H2 — orchestrator-driven Codespace rebuild loop — is explicitly deferred to a future R4).

### Referenced Specifications

- **UI Spec** — N/A (no frontend in scope).
- **API Spec** — N/A (no API in scope).
- **Data Model Spec** — N/A (no DB in scope).
- **Runbook / Operational Spec** — `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` (per-layer Claude Code design); `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` (decision substrate).

## Design Summary (Meta)

```yaml
design_type: "tooling_change"
risk_level: "medium"
complexity_level: "high"
complexity_rationale: |
  (1) Necessitating ACs / FRs: 11 functional requirements (FR-1..FR-11) across discovery, synthesis, design, audit,
      validator authoring, and discipline-text editing surfaces. Cross-cutting concerns include a 3-vocabulary severity
      reconciliation (ADR-0061), an additive companion-file convention for ADRs (ADR-0059), and a stage-transition gate
      grammar (ADR-0063) that introduces a new mechanical contract for the orchestrator.
  (2) Constraints / risks driving complexity: the recurrence-prevention thesis is structural (the brief's verbatim
      direction). Half-measures defeat the goal. The 41-path touchpoint surface (per cc-dependencies.json) and the
      cross-cluster bridges (FR-1 ↔ FR-4/5 via severity bridge; FR-9 ↔ FR-2 via Discovery marker emission) require
      coordinated authoring at design and plan time.
layers_touched:
  - "Claude Code / Project Filesystem"
blast_radius:
  runtime: |
    Future feature runs (every run inherits the new disciplines). No end-user runtime; the affected runtime is the
    feature pipeline itself, executed by future feature-pipeline operators.
  build_time: |
    Future deliverable-archive packagings inherit two new pre-package audit checks (auditing-subagents SA-14;
    validate_adr_prescriptions.py). Pipeline operator wall-clock budget per NFR-1 (5000 ms) + NFR-2 (3000 ms/server) +
    NFR-3 (500 ms/server) + NFR-7 (30 min @ 100 agents) preserved.
main_constraints:
  - "Claude Code layer only; no new sub-agents; no retroactive register edits."
  - "Companion-file location bound by ADR-0036 + ADR-0054 + ADR-0056 (single canonical location, no carve-outs)."
  - "11 mechanisms must be authorable within the 4-cycle reconciliation cap; Contingency Split is the safety valve."
  - "NFR-4 (<5% drift FP rate) is mechanistic — pilot validation required at PV-authoring time."
biggest_risks:
  - "Q-CC-1 Contingency Split — two well-evidenced readings (orchestrator currently-open=6 vs cumulative=14); routes to user at Gate 4."
  - "NFR-4 FP-rate target is single-sourced and extrapolated; pilot will measure and may force catalog refinement."
  - "Companion-file backfill of 58 legacy ADRs (ADR-0001..ADR-0058) is event-triggered (per FR-11 framing) — actual cost is unmeasured."
unknowns:
  - "Whether the em-dash payload separator in Blocks-X markers (ADR-0063) is robust across editor environments."
  - "Whether the hybrid catalog (ADR-0060) scales past ~30 entries without deprecation pressure."
  - "Whether the cross-cluster severity-bridge consumption pattern (ADR-0061) needs the optional translator utility in v1 or v2."
```

## Background and Context

### Brief-honor citation

This feature exists to satisfy the user's verbatim thesis from the rationale brief:

> "the pipeline must verify relationships across artifacts, not just per-artifact correctness — cancels the structural defect-class behind r1's shipment and the recurrence risk every agent-surface feature inherits."

Every architectural decision in this Blueprint and every ADR authored in this run honors that thesis. The companion-file convention (ADR-0059), the cross-file invariant catalog (ADR-0060), the severity bridge table (ADR-0061), the tool-surface drift detection pipeline (ADR-0062), and the Blocks-X marker grammar (ADR-0063) are each the load-bearing artifact for a different cross-artifact relationship the pipeline did not previously verify.

### Source of the Recurrence

Two recent failures share a structural shape:

1. **`issue-capture-mechanism-r1` Phase 1** produced a structural spec whose §7 ID-derivation rule contradicted its three sibling templates and five empirical precedents. PV-1 passed cleanly because no validator compared the spec to the templates. Caught by post-phase human review.
2. **`devcontainer-mcp-provisioning-r1`** shipped a configuration where five of seven MCP servers were broken because no auditor compared ADR-0041's prescribed invocations against the eventual `.mcp.json` and `postCreate.sh`. Shipped silently; required forensic recovery.

A converging analysis (`Issues/per-agent-design-evaluation-gap/analysis.md`) traced the same `devcontainer-mcp-provisioning-r1` run and found a parallel design-time defect: the pipeline iterated the *changed* agent surface (8 of 36 agents got the new MCP tools) without ever enumerating the full inventory to confirm the other 28 should not change. Caught at Gate 4 by the user.

A third input (`Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O) named the pattern that "post-ship / N days post-ship" triggers have no firing mechanism in the project. The user chose to ship the prior feature unchanged and recorded the going-forward posture in the register.

### Prerequisite ADRs

| ADR | Relevance to this feature |
|---|---|
| **ADR-0005** | Append-only supersession discipline; this feature does not supersede any ADR but reaffirms the principle by extending Principle 9 in place rather than replacing. |
| **ADR-0009** | Rationale brief honor discipline; the verbatim citation above satisfies the L3 brief-honor check. |
| **ADR-0013** | Blueprint template; this Blueprint conforms. |
| **ADR-0016** | Per-layer fan-out / composer fan-in (single-layer fan-out for this feature — Claude Code only). |
| **ADR-0017** | shared-document-reviewer invocation points; this Blueprint reviewed at invocation 4. |
| **ADR-0018** + **ADR-0038** | codebase-analysis schema + additive-extension discipline; FR-2's schema extension is governed by these. |
| **ADR-0022** | Sub-agent reasoning-configuration discipline; FR-8 rewrites Principle 9 of KB-cc-design (which this ADR depends on). |
| **ADR-0027** | cwd == repo-root precondition; baseline storage (FR-5) uses repo-relative paths. |
| **ADR-0030** | Pedagogical-marker justification; new templates in KB-documentation-criteria conform. |
| **ADR-0036** + **ADR-0054** + **ADR-0056** | ADR placement canonical-rule + canonical-helper validator + no-carve-outs principle. FR-1 companion files live at `adrs/` per these (see ADR-0059 authored in this run). |
| **ADR-0039** | Credential indirection; NFR-6 redaction posture (FR-4/5 transport error redaction) rides on it. |
| **ADR-0040** | Serena narrowed-allowlist precedent — the canonical exemplar of the per-agent-design-evaluation-gap that FR-6 closes. |
| **ADR-0041** | install-mechanism-hybrid — the canonical ADR-prescription that FR-1 + ADR-0059's companion-file convention closes. |
| **ADR-0042** | auditing-mcp family graduation; hosts FR-4 + FR-5 edits. |
| **ADR-0044** | State-transitions log v1 invariant (execute-orchestrator is sole writer; free-string `transition_name`). FR-9 reserves new values consistent with the invariant (see ADR-0063 authored in this run). |
| **ADR-0045** | review-architecture-auditor has no Agent/Task tool; FR-1's new dimension runs inline, not via sub-agent spawn-out. |
| **ADR-0046** | New-sibling-file evolution discipline; ADR-0063's grammar spec is a new sibling under `KB-documentation-criteria/references/`. |
| **ADR-0020** | KB consolidation discipline; ADR-0060's catalog lives in KB-task-decomposition per the same discipline. |

### External Resources Used

| Resource (project-tier label) | Feature-specific identifier | Notes |
|---|---|---|
| Live MCP transport surface | `claude mcp ping` (or transport-equivalent JSON-RPC) against the 6 servers in `.mcp.json` | Required by FR-4 (reachability handshake). NFR-2 enforces 3000 ms per-server timeout. |
| Live MCP `tools/list` surface | `tools/list` JSON-RPC method against each MCP server | Required by FR-5 (drift detection). Stage 1 of the four-stage pipeline (ADR-0062) canonicalizes via RFC 8785. |
| Standards: RFC 8785, RFC 6902 | JSON Canonicalization Scheme + JSON-Patch | Stages 1 and 3 of the FR-5 drift-detection pipeline (ADR-0062). |

### Agreement Checklist

#### Scope

- [x] 11 mechanisms (FR-1..FR-11) at the Claude Code layer.
- [x] 5 new ADRs (ADR-0059..ADR-0063) authored in this run.
- [x] 14 new files created (per cc-dependencies.json sidecar; reconciled count per R-DR-CC-001).
- [x] 24 existing files edited.
- [x] 3 annotate-only references (no structural edit).

#### Non-Scope (Explicitly not changing)

- [x] No new pipeline sub-agents (per PRD Won't-Have + `per-agent-design-evaluation-gap` §6.3).
- [x] No retroactive edits to `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1 rows (per AC-FR-11-c + register §O.5).
- [x] No CI/CD workflow changes (parallel `pipeline-quickwins-hardening-r1` run owns these).
- [x] No CLAUDE.md modifications (per Principle 5; KBs and discipline texts suffice).
- [x] No splitting of the Claude Code layer into sub-layers.

#### Constraints

- [x] Parallel operation: Yes (the new disciplines apply to features whose Intent Clarification starts after this feature ships; in-flight features keep the existing contract).
- [x] Backward compatibility: Required — applies to existing audit/review/validator outputs; the severity-vocabulary trifecta is preserved (ADR-0061).
- [x] Performance measurement: Required — NFR-1 (5000 ms), NFR-2 (3000 ms/server), NFR-3 (500 ms/server), NFR-4 (<5% FP), NFR-7 (30 min @ 100 agents).
- [x] Zero-downtime deployment: N/A (pipeline-internal; no production user surface).
- [x] Forward-compatible migration: Required — legacy ADRs without companion files (ADR-0001..ADR-0058) work as-is (no auditor finding on absence per AC-FR-1-b).

#### Applicable Standards

- [x] RFC 8785 (JSON Canonicalization Scheme) `[explicit]` — Source: IETF; consumed by ADR-0062 Stage 1.
- [x] RFC 6902 (JSON-Patch) `[explicit]` — Source: IETF; consumed by ADR-0062 Stage 3.
- [x] EARS acceptance criteria `[explicit]` — Source: KB-documentation-criteria; all PRD-v2 ACs use EARS form.
- [x] Sub-agent reasoning-configuration discipline `[explicit]` — Source: ADR-0022 + KB-cc-design Principle 9 (post-FR-8 active framing).

#### Quality Assurance Mechanisms

- [x] `validate_adr_prescriptions.py` — Enforces: companion-file YAML schema, ADR-companion slug match, target-path existence — Config: `auditing-shared/scripts/` — Covers: `adrs/*.prescriptions.yaml` — Status: `adopted` (new in this feature; per ADR-0059).
- [x] `audit_feature_touch_coverage.py` (FR-10 / SA-14) — Enforces: `agent-roster-impact-matrix.md` presence + row-count parity — Config: `auditing-subagents/scripts/` — Covers: feature working directories where agent surface was touched — Status: `adopted`.
- [x] `check_mcp_reachability.py` + `check_tool_surface_drift.py` — Enforces: FR-4 + FR-5 — Config: `auditing-mcp/scripts/` — Covers: `.mcp.json` MCP servers — Status: `adopted` (per ADR-0062).

### Problem to Solve

The pipeline today verifies artifacts individually (each PRD, each Blueprint, each ADR, each implementation file is reviewed). It does not verify the **relationships** between artifacts: that an ADR's prescription matches the file shipped; that a phase's deliverables agree with each other on shared invariants; that the agent surface is enumerated rather than evaluated-by-absence; that new domain concepts pair with a deliberate skill-coverage decision; that deferral framings can actually fire.

### Current Challenges

- Cross-artifact relationships are evaluated by human review only. When the review misses a divergence, the divergence ships.
- The agent surface (currently 37 `.claude/agents/*.md` files per codebase-analysis Known Issue 6) is iterated supply-driven (changed agents) rather than demand-driven (full inventory). Untouched agents are evaluated by absence.
- New domain concepts are addressed reactively at gate review rather than at synthesis-time.
- Time-based deferral framings ("post-ship", "N days post-ship") accumulate without any pipeline mechanism that fires them.

### Requirements

#### Functional Requirements

- **FR-1 (H3) — Design-realization audit dimension on `review-architecture-auditor`.** Inherited verbatim from PRD-v2.
- **FR-2 (H6) — §Protocol Conformance subsection in `discovery-codebase-researcher` output.** Inherited verbatim from PRD-v2.
- **FR-3 (H9) — PV-tier cross-file consistency invariant catalog.** Inherited verbatim from PRD-v2.
- **FR-4 (H1) — Rename `--with-runtime` to `--with-mcp-reachability` + live handshake.** Inherited verbatim from PRD-v2.
- **FR-5 (H8) — Live tool-surface drift detection.** Inherited verbatim from PRD-v2.
- **FR-6 (B1) — Mandatory `agent-roster-impact-matrix.md` artifact when feature touches agent surface.** Inherited verbatim from PRD-v2.
- **FR-7 (B3) — Skill-coverage check at Synthesis / Design for new domain concepts.** Inherited verbatim from PRD-v2.
- **FR-8 (B2) — Strengthen KB-cc-design Principle 9 from defensive to active.** Inherited verbatim from PRD-v2.
- **FR-9 (B4) — Enforce "Blocks downstream" markers as stage-transition gates.** Inherited verbatim from PRD-v2.
- **FR-10 (B5) — `auditing-subagents` feature-touch-coverage rule.** Inherited verbatim from PRD-v2.
- **FR-11 (§O posture) — Replace post-ship time-based deferral triggers with event-triggered, honest-acceptance, or concrete-machinery framings.** Inherited verbatim from PRD-v2.

#### Non-Functional Requirements

Verbatim from PRD-v2:

- **Performance**: NFR-1 (5000 ms auditor pass); NFR-2 (3000 ms reachability timeout/server); NFR-3 (500 ms drift detection/server).
- **Reliability**: NFR-4 (<5% drift FP rate across 50 audits); NFR-5 (auditor idempotency — byte-identical output).
- **Security**: NFR-6 (credential redaction in audit output).
- **Scalability**: NFR-7 (matrix authoring < 30 min @ 100-agent inventory).
- **Operability**: NFR-8 (clear failure messages — four-field shape `rule`/`target`/`divergence`/`next_action`).
- **Developer Experience**: NFR-9 (grep-checkable affordance referencing).

## Acceptance Criteria (AC) - EARS Format

All ACs are carried verbatim from PRD-v2 (AC-FR-1-a through AC-FR-11-c plus NFR ACs). PRD-v2's EARS discipline is preserved without restatement here. The composer's role is to integrate, not to re-derive ACs.

### Functional ACs by FR — Pointers

Per ADR-0023 + ADR-0013 discipline, this Blueprint references PRD-v2's AC blocks rather than restating them. Reviewers verify each PRD AC has a corresponding design realization in this Blueprint's `### Design` section.

| FR | AC anchors (PRD-v2) | Design realization (this Blueprint) |
|---|---|---|
| FR-1 | AC-FR-1-a, AC-FR-1-b, AC-FR-1-c | `### Design` § FR-1; ADR-0059 (companion-file convention) |
| FR-2 | AC-FR-2-a, AC-FR-2-b | `### Design` § FR-2 |
| FR-3 | AC-FR-3-a, AC-FR-3-b, AC-FR-3-c | `### Design` § FR-3; ADR-0060 (hybrid catalog) |
| FR-4 | AC-FR-4-a, AC-FR-4-b, AC-FR-4-c, AC-FR-4-d | `### Design` § FR-4; ADR-0062 |
| FR-5 | AC-FR-5-a, AC-FR-5-b, AC-FR-5-c, AC-FR-5-d, AC-FR-5-e | `### Design` § FR-5; ADR-0062 (four-stage pipeline) |
| FR-6 | AC-FR-6-a, AC-FR-6-b, AC-FR-6-c, AC-FR-6-d | `### Design` § FR-6 |
| FR-7 | AC-FR-7-a, AC-FR-7-b, AC-FR-7-c | `### Design` § FR-7 |
| FR-8 | AC-FR-8-a, AC-FR-8-b | `### Design` § FR-8 |
| FR-9 | AC-FR-9-a, AC-FR-9-b, AC-FR-9-c | `### Design` § FR-9; ADR-0063 (grammar) |
| FR-10 | AC-FR-10-a, AC-FR-10-b, AC-FR-10-c | `### Design` § FR-10 |
| FR-11 | AC-FR-11-a, AC-FR-11-b, AC-FR-11-c | `### Design` § FR-11; §O.1 Row-Count Correction (Q-CC-5) |

### Cross-Layer / Operational ACs

- **NFR-1 / AC-NFR-1-a** — auditor design-realization pass within 5000 ms for ≤20 prescriptions.
- **NFR-2 / AC-NFR-2-a** — 3000 ms per-server reachability handshake timeout.
- **NFR-3 / AC-NFR-3-a** — 500 ms per-server drift comparison.
- **NFR-4 / AC-NFR-4-a** — <3 false-positive findings across 50 audits.
- **NFR-5 / AC-NFR-5-a + AC-NFR-5-b** — byte-identical findings JSON; MAJOR self-diagnostic on divergence.
- **NFR-6 / AC-NFR-6-a** — credential redaction in transport-error finding emission.
- **NFR-7 / AC-NFR-7-a** — matrix authoring wall-clock <30 min @ 100-agent inventory.
- **NFR-8 / AC-NFR-8-a** — four-field finding shape (`rule`, `target`, `divergence`, `next_action`) on blocking findings from FR-1/4/5/6/9/10.
- **NFR-9 / AC-NFR-9-a** — grep-checkable affordance referencing from consuming-agent `skills:` lists.

## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | Existing (edit) | `.claude/agents/review-architecture-auditor.md` | New audit phase (FR-1) added inline (no Agent/Task tool per ADR-0045). |
| Claude Code | Existing (edit) | `.claude/agents/discovery-codebase-researcher.md` | §Protocol Conformance + Blocks-X emission added (FR-2 + FR-9). |
| Claude Code | Existing (edit) | `.claude/agents/test-phase-validator-author.md` | Phase 2 rubric extended with Cross-File Invariants section + deferral-framing check (FR-3 + FR-11). |
| Claude Code | Existing (edit) | `.claude/agents/design-claude-code.md` | Roster-matrix + skill-coverage + Principle 9 active-framing citation (FR-6 + FR-7 + FR-8). |
| Claude Code | Existing (edit) | `.claude/agents/execute-orchestrator.md` | Blocks-X parsing + state-transition gating (FR-9). |
| Claude Code | Existing (edit) | `.claude/agents/intake-prd-author.md` | Undetermined Items prompt cross-refs new deferral conventions (FR-11). |
| Claude Code | Existing (edit) | `.claude/agents/design-composer.md` | Open Items prompt cross-refs deferral conventions; Blueprint composition reads skill-coverage rows (FR-7 + FR-11). |
| Claude Code | Existing (edit) | `.claude/agents/synth-synthesizer.md` | Emit Skill-Coverage Decisions section in synthesis output (FR-7; Q-CC-6 ratifies this as primary site). |
| Claude Code | Existing (edit) | `.claude/agents/cc-critique.md` | Flag-rename reference updates (FR-4). |
| Claude Code | Existing (edit) | `.claude/skills/KB-cc-design/references/principles.md` | Principle 9 rewritten active; W/H/A rubric; FR-11 sub-section (FR-6 + FR-7 + FR-8 + FR-11). |
| Claude Code | Existing (edit) | `.claude/skills/KB-review-disciplines/references/architecture-audit.md` | Lens 4 (Design Realization) added; FR-3 catalog cross-reference (FR-1 + FR-3). |
| Claude Code | Existing (edit) | `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` | D-10 bridge table + NFR-8 four-field shape (per ADR-0061). |
| Claude Code | Existing (edit) | `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` | `transition_name` enumeration extended (FR-9; per ADR-0063). |
| Claude Code | Existing (edit) | `.claude/skills/KB-codebase-research/SKILL.md` | Additive schema extension for `protocol_conformance[]` array (FR-2). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-mcp/scripts/audit_mcp.py` | Flag rename + new dispatches (FR-4 + FR-5). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-mcp/scripts/check_toxic_combinations.py` | Flag references updated (FR-4). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-mcp/SKILL.md` | Routing table + Runtime-mode section (FR-4 + FR-5). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-mcp/examples/good-mcp-annotated.md` | Flag references (FR-4). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-mcp/references/common-failures.md` | Flag reference (FR-4). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-mcp/references/toxic-combinations.md` | Flag references (FR-4). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-cc-configs/scripts/audit_project.py` | Flag forwarding + AC-FR-4-d loud-fail (FR-4). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-cc-configs/SKILL.md` + checklist + audit-rubric + common-failures | Flag references (FR-4; 4 files). |
| Claude Code | Existing (edit) | `.claude/skills/KB-mcp-platform/references/operator-runbook.md` + mcp-events-jsonl.md + troubleshooting.md | Flag references (FR-4; 3 files). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-subagents/SKILL.md` | New rule SA-14 added (FR-10). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-subagents/references/` | New reference text for SA-14 (FR-10). |
| Claude Code | Existing (edit) | `.claude/skills/auditing-skills/` | Separate reverse-check rule per Q-CC-7 (FR-10). |
| Claude Code | Existing (edit) | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Outputs table + checkpoint logic for Blocks-X (FR-6 + FR-9). |
| Claude Code | New (create) | `adrs/ADR-NNNN-<slug>.prescriptions.yaml` | Companion-file pattern (FR-1; per ADR-0059). Optional; only ADRs with machine-checkable prescriptions ship one. |
| Claude Code | New (create) | `.claude/skills/auditing-shared/scripts/validate_adr_prescriptions.py` | Companion-file linter (FR-1). |
| Claude Code | New (create) | `.claude/skills/auditing-mcp/scripts/check_mcp_reachability.py` | Reachability handshake (FR-4). |
| Claude Code | New (create) | `.claude/skills/auditing-mcp/scripts/check_tool_surface_drift.py` | Four-stage drift pipeline (FR-5). |
| Claude Code | New (create) | `.claude/skills/auditing-mcp/baselines/<server-name>.json` | Committed canonical baselines, 6 at first encounter (FR-5; per ADR-0062). |
| Claude Code | New (create) | `.claude/skills/auditing-mcp/references/drift-severity-catalog.md` | Stage 4 severity catalog (FR-5). |
| Claude Code | New (create) | `.claude/skills/KB-task-decomposition/cross-file-invariants.md` | Centralized catalog body (FR-3; per ADR-0060). |
| Claude Code | New (create) | `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` | Canonical grammar spec (FR-9; per ADR-0063). |
| Claude Code | New (create) | `.claude/skills/KB-documentation-criteria/references/disciplines/deferral-framing-conventions.md` | Three permitted framings (FR-11). |
| Claude Code | New (create) | `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md` | Matrix template (FR-6). |
| Claude Code | New (create) | `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md` | Section template (FR-7). |
| Claude Code | New (create) | `.claude/skills/KB-documentation-criteria/references/templates/protocol-conformance-subsection-template.md` | Subsection template (FR-2). |
| Claude Code | New (create) | `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` | Advisory predicate, FR-6 triggers 3+4 (per D-5). |
| Claude Code | New (create) | `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` | SA-14 audit script (FR-10). |

**Reconciliation of summary counts** (addresses advisory finding R-DR-CC-001): per the `cc-dependencies.json` sidecar, total creates = **14 files**; the cc-design.md prose figure of "11 files" was an undercount. This Blueprint adopts the sidecar count of 14 as canonical (4 new template files + 1 new conventions discipline file + 1 new grammar spec + 1 new catalog + 1 new severity-catalog reference + 3 new audit scripts + 1 new linter + 1 new baselines/ subdir = 14 file-equivalents). The cc-design and cc-dependencies are reconciled in the FR-by-FR design sections below.

### Integration Points (Include even for new implementations)

- **Integration Target**: `review-architecture-auditor` agent — adds Lens 4 / Design Realization phase.
  **Invocation Method**: direct call from existing agent body procedure; orchestrator dispatch at Stage 8 (per ADR-0017 invocation 4 / Architecture Audit).
- **Integration Target**: `execute-orchestrator` agent — Blocks-X parser at stage-transition checkpoints.
  **Invocation Method**: orchestrator reads upstream outputs at every stage transition; parses markers; refuses advance until each is closed.
- **Integration Target**: `design-cc` agent — roster-matrix authoring + skill-coverage row emission.
  **Invocation Method**: per-layer Design stage (Stage 6) procedure step; Design Composition refuses to mark Stage 7 complete if trigger fired and matrix absent.
- **Integration Target**: `auditing-mcp` runner — reachability + drift dispatches.
  **Invocation Method**: `audit_mcp.py --with-mcp-reachability` (renamed from `--with-runtime`); subprocess to new check scripts.
- **Integration Target**: `auditing-subagents` runner — SA-14 pre-deliverable-packaging audit.
  **Invocation Method**: existing `auditing-cc-configs/audit_project.py` family coordinator invokes at Stage 11 (deliverable archive).

### Code Inspection Evidence

| File/Function | Relevance |
|---|---|
| `.claude/agents/review-architecture-auditor.md:1-200` | Existing 6-phase procedure; FR-1 adds Phase 7 (Design Realization) inline. |
| `.claude/skills/auditing-mcp/scripts/audit_mcp.py:36` | Existing `--with-runtime` flag site; rename target for FR-4. |
| `.claude/skills/KB-cc-design/references/principles.md:184` | Principle 9 leading sentence; FR-8 rewrites to active framing. |
| `.claude/agents/design-claude-code.md:56` | Verbatim Principle 9 citation; FR-8 updates to match new wording + adds AC-FR-8-b cross-reference. |
| `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:198-202` | Single prior Blocks-X occurrence; ADR-0063 documents non-retroactive migration. |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1 | Five rows (A-3, D-5, E-2, E-3, I-1); PRD AC-FR-11-c names four — Q-CC-5 surfaces the discrepancy. |

### Fact Disposition Table

One row per codebase-analysis-report.md `focusArea`. Each fact's disposition is consistent with the design.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---|---|---|---|---|
| F-001 | review-architecture-auditor procedure structure | preserve + extend | FR-1 adds Phase 7 inline; existing 6 phases unchanged | `.claude/agents/review-architecture-auditor.md` |
| F-002 | auditing-mcp `--with-runtime` flag | transform (rename) | FR-4 renames to `--with-mcp-reachability`; AC-FR-4-d requires loud-fail on legacy | `.claude/skills/auditing-mcp/scripts/audit_mcp.py:36` |
| F-003 | `.mcp.json` six-server post-2026-05-24 state | preserve | Audit target only; no edits from this feature | `.mcp.json` |
| F-004 | codebase-analysis-report schema v1.1.0 | transform (additive extension) | FR-2 adds `protocol_conformance[]` array; ADR-0018 + ADR-0038 governance | `KB-codebase-research/SKILL.md` |
| F-005 | PV-author rubric inlined in test-phase-validator-author.md | preserve + extend | Per Known Issue 3 — rubric host is the agent body, not KB-task-decomposition. FR-3 extends Phase 2 rubric | `.claude/agents/test-phase-validator-author.md` |
| F-006 | KB-cc-design Principle 9 defensive framing | transform (active framing) | FR-8 rewrites; AC-FR-8-b adds mutual cross-reference to FR-6 | `.claude/skills/KB-cc-design/references/principles.md:184` |
| F-007 | `.claude/agents/*.md` inventory size = 37 | preserve | Per Known Issue 6 — current count; FR-6 row-count parity at audit time per AC-FR-6-b | `ls .claude/agents/*.md \| wc -l` |
| F-008 | state-transitions log `transition_name` free-string field | preserve | Per ADR-0044 v1; FR-9 reserves new values without schema evolution | `state-transitions-log-entry-template.md` |
| F-009 | auditing-mcp NIT vs auditor INFO sub-divergence | transform (document via bridge) | Per Known Issue 2 + ADR-0061 — bridge table documents non-monotonic edge | `KB-review-disciplines/references/severity-taxonomy.md` (post-this-feature) |
| F-010 | Single prior Blocks-X prose occurrence | preserve (non-retroactive) | Per ADR-0063 — historical artifact preserved as authored; canonical grammar applies to new emissions | `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:198-202` |
| F-011 | Zero "post-ship" precedent in `.claude/skills/` and `.claude/agents/` | preserve (cite as evidence) | Per Known Issue 7 / codebase-analysis-report line 285 — FR-11 implementation is purely additive | grep across `.claude/skills/`, `.claude/agents/` |
| F-012 | §O.1 register row count = 5 (A-3, D-5, E-2, E-3, I-1) | preserve verbatim | Per AC-FR-11-c + register §O.5; Q-CC-5 surfaces PRD enumeration discrepancy (PRD lists 4) | `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1 |

## Design

### Change Impact Map

```yaml
Change Target: Pipeline cross-artifact + design-time discipline
Direct Impact:
  claude_code:
    agents:
      - review-architecture-auditor.md (FR-1; new Phase 7)
      - discovery-codebase-researcher.md (FR-2, FR-9; §Protocol Conformance + Blocks-X)
      - test-phase-validator-author.md (FR-3, FR-11; Cross-File Invariants + deferral-framing check)
      - design-claude-code.md (FR-6, FR-7, FR-8; roster matrix + skill-coverage + Principle 9 citation)
      - execute-orchestrator.md (FR-9; Blocks-X parser)
      - intake-prd-author.md (FR-11; Undetermined Items prompt)
      - design-composer.md (FR-7, FR-11; Open Items prompt + skill-coverage block)
      - synth-synthesizer.md (FR-7; skill-coverage row emission)
      - cc-critique.md (FR-4; flag rename)
    kbs_and_skills:
      - KB-cc-design/references/principles.md (FR-6, FR-7, FR-8, FR-11)
      - KB-review-disciplines/references/architecture-audit.md (FR-1, FR-3)
      - KB-review-disciplines/references/severity-taxonomy.md (FR-1, FR-4, FR-5, FR-9, FR-10 — per ADR-0061)
      - KB-task-decomposition/cross-file-invariants.md (FR-3; new — per ADR-0060)
      - KB-codebase-research/SKILL.md (FR-2; additive schema)
      - KB-documentation-criteria/references/blocks-x-marker-grammar.md (FR-9; new — per ADR-0063)
      - KB-documentation-criteria/references/disciplines/deferral-framing-conventions.md (FR-11; new)
      - KB-documentation-criteria/references/templates/* (FR-2, FR-6, FR-7; 3 new templates)
      - KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md (FR-9; transition_name enum)
      - KB-mcp-platform/references/*.md (FR-4; 3 files, flag references)
      - auditing-mcp (FR-4, FR-5; renames + 2 new scripts + baselines/ + severity catalog)
      - auditing-cc-configs (FR-4; flag forwarding + loud-fail)
      - auditing-subagents (FR-10; new SA-14 + new advisory predicate script for FR-6 triggers 3+4)
      - auditing-skills (Q-CC-7 resolved → separate reverse-check rule)
      - auditing-shared/scripts/validate_adr_prescriptions.py (FR-1; new linter — per ADR-0059)
      - recipe-feature-pipeline/SKILL.md (FR-6, FR-9; outputs + checkpoint logic)
    adrs:
      - adrs/ADR-NNNN-<slug>.prescriptions.yaml (FR-1; new optional companion files — per ADR-0059)
      - adrs/ADR-0059..ADR-0063 (5 new ADRs authored in this run)
Indirect Impact:
  - Future feature runs inherit the 11 mechanisms by default (no opt-out per PRD).
  - codebase-analysis.json consumers (12 downstream agents/skills per blast-radius) inherit the additive protocol_conformance[] array.
  - The audit-issues.json schema gains the NFR-8 four-field shape (rule/target/divergence/next_action) on blocking findings.
No Ripple Effect:
  - CLAUDE.md (no edits; Principle 5 — single source of truth).
  - Frontend / Backend / API / Query / DB / CI/CD / IaC / Codespaces layers (all out of scope).
  - Existing `.mcp.json` server entries (audit target only; no edits).
  - Existing ADRs (ADR-0001..ADR-0058) (no edits; companion files are net-new sibling artifacts).
  - Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md §O.1 rows (annotate-only per AC-FR-11-c + register §O.5).
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|---|---|---|---|
| `--with-runtime` audit flag | `--with-mcp-reachability` | Yes (rename) | Legacy flag invocation raises `SystemExit(2)` with migration message per AC-FR-4-d (loud-fail, not silent no-op). |
| `audit-issues.json` finding shape | NFR-8 four-field shape (`rule`, `target`, `divergence`, `next_action`) | Yes (field-additive) | Existing fields preserved; four new fields populated by FR-1/4/5/6/9/10 emitters. Bridge table (ADR-0061) documents severity translation. |
| `codebase-analysis.json` schema v1.1.0 | v1.2.0 (additive `protocol_conformance[]`) | No | Additive extension; legacy consumers ignore new top-level array. Per ADR-0018 + ADR-0038. |
| KB-cc-design Principle 9 (defensive framing) | Active framing | Yes (in-place rewrite) | Per ADR-0005 — in-place edit with amendment note; existing principle ID preserved; cross-reference to FR-6 matrix discipline per AC-FR-8-b. |
| state-transitions log `transition_name` (free-string) | Reserved values: `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE` | No | Per ADR-0044 v1 + ADR-0063 — values reserved without schema evolution. |
| ADR file pattern (`ADR-NNNN-<slug>.md`) | + optional sibling `ADR-NNNN-<slug>.prescriptions.yaml` | No (optional) | Companion is opt-in per ADR-0059; legacy ADRs without companions work as-is (auditor no-ops per AC-FR-1-b). |
| Blocks-X marker prose form `Blocks <slug>-completion.` | Structured pragma `<!-- BLOCKS: <slug>-completion -->` | No (non-retroactive) | Single prior occurrence preserved verbatim; canonical grammar applies to new emissions only per ADR-0063. |

### Architecture Overview

The pipeline's verification surface expands at five points:

```
Stage 1 (Discovery)
  └─► discovery-codebase-researcher
        ├─► [FR-2] emits §Protocol Conformance subsections for each in-scope external interface
        └─► [FR-9] emits structured Blocks-X markers when discovery surfaces gating questions

Stage 2 (Synthesis) — composition pass
  └─► synth-synthesizer
        └─► [FR-7] emits Skill-Coverage Decisions section for new domain concepts

Stage 6 (Per-Layer Design — CC layer only for this feature)
  └─► design-cc
        ├─► [FR-6] authors agent-roster-impact-matrix.md when triggered
        └─► [FR-7] emits Skill-Coverage Decisions rows; design-composer reads at Stage 7

Stage 7 (Design Composition)
  └─► design-composer
        ├─► reads skill-coverage rows; blocks completion on missing justification
        ├─► authors any ADRs warranted by cross-layer arbitration (this Blueprint authored 5)
        └─► [FR-11] cross-references new deferral-framing conventions in Open Items

Stage 8 (Architecture Audit)
  └─► review-architecture-auditor
        ├─► [FR-1] Lens 4: Design Realization — reads ADR companion files (per ADR-0059)
        └─► Emits findings with NFR-8 four-field shape per ADR-0061 bridge

Stage 9 (Cross-Artifact Audit) — sibling to Stage 8
  └─► review-cross-artifact-auditor (unchanged; consumes bridge table)

Stage 10 (Phase Validator Authoring)
  └─► test-phase-validator-author
        ├─► [FR-3] authors Cross-File Invariants section per phase; references catalog by CFI-NNN
        └─► [FR-11] deferral-framing check on PV findings

Stage 11 (Pre-Deliverable Packaging)
  └─► auditing-cc-configs runs family pass
        ├─► auditing-mcp runs with --with-mcp-reachability [FR-4 + FR-5]
        ├─► auditing-subagents runs SA-14 [FR-10]
        ├─► auditing-skills runs reverse-check (per Q-CC-7 resolution)
        └─► auditing-shared/scripts/validate_adr_prescriptions.py runs

Every Stage Transition
  └─► execute-orchestrator parses Blocks-X markers from upstream outputs [FR-9]
        └─► refuses advance until each marker transitions to RESOLVED / DEFERRED_WITH_OI / FALSE_POSITIVE
```

### Data Flow

```
Future feature pipeline run (after this feature ships):

ADR authored (Stage 7)
  └─► if prescriptions exist: companion .prescriptions.yaml authored alongside (ADR-0059)
                                                                    │
                                                                    ▼
Implementation phase ships file matching prescription's target_path
                                                                    │
                                                                    ▼
Stage 8 Architecture Audit
  └─► review-architecture-auditor Phase 7 (Design Realization)
        └─► reads adrs/*.prescriptions.yaml for each ADR in this run's adrs[]
        └─► for each prescription P: open P.target_path; apply P.assertion
        └─► mismatch → BLOCKER finding (NFR-8 four-field shape)

Stage 11 Pre-Deliverable Packaging
  └─► auditing-mcp --with-mcp-reachability
        ├─► check_mcp_reachability.py per-server handshake (NFR-2: 3000 ms/server)
        └─► check_tool_surface_drift.py four-stage pipeline (per ADR-0062)
              ├─► Stage 1: RFC 8785 canonicalize live tools/list
              ├─► Stage 2: read baseline from auditing-mcp/baselines/<server>.json
              │            (if absent: write Stage 1 output as new baseline, emit INFO)
              ├─► Stage 3: RFC 6902 JSON-Patch diff (identity-keyed by tool name)
              └─► Stage 4: severity-catalog routing
                    └─► allowlisted-tool-remove → BLOCKER (AC-FR-5-a)
                    └─► tool-add → MAJOR (AC-FR-5-d)
                    └─► signature-change-on-allowlisted → MAJOR (AC-FR-5-e)
                    └─► description/title/icon → INFO (NFR-4 FP suppression)
                    └─► unparseable → MAJOR (AC-FR-5-c)
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|---|---|---|---|---|---|
| Architecture audit dimensions | `KB-review-disciplines/references/architecture-audit.md` | 3 lenses (CoVe, Blast-Radius, Brief-Honor) | 4 lenses (+ Design Realization) | Additive extension to the reference + new procedure phase in `review-architecture-auditor.md` | shared-document-reviewer Gate 0/1 on Blueprint; Architecture Audit (Stage 8) self-test on this feature's own deliverables |
| Severity-vocabulary surface | Multiple skills (auditor + reviewer + PV) | Independent trifecta | Trifecta + bridge table at `KB-review-disciplines/references/severity-taxonomy.md` | Bridge table is additive; vocabularies preserved on each surface | Cross-artifact audit (Stage 9) verifies bridge consistency |
| MCP audit flag | `auditing-mcp/audit_mcp.py:36` | `--with-runtime` | `--with-mcp-reachability` | Mechanical rename; legacy flag raises SystemExit(2) per AC-FR-4-d | Direct invocation test in PV-authoring |
| Stage-transition gate | `execute-orchestrator.md` + `recipe-feature-pipeline/SKILL.md` | No marker parsing | Blocks-X HTML-comment parser + gating | Additive parsing phase at each stage transition | Phase validators assert marker closure semantics |
| Skill-Coverage Decisions | Synthesis output + Blueprint | Ad-hoc; no enforcement | Required section; design-composer blocks on missing justification | New section in synthesis output template; design-composer procedure step | shared-document-reviewer Gate 1 on Blueprint |

### Main Components

#### Component 1: ADR Companion File + Linter (FR-1)

- **Responsibility**: Externalize machine-checkable predicates from ADR prose into structured, lint-checkable companion files.
- **Interface**: `adrs/ADR-NNNN-<slug>.prescriptions.yaml` (schema v1.0; see ADR-0059 §Schema).
- **Dependencies**: ADR-0036 + ADR-0054 + ADR-0056 (canonical placement); `validate_adr_prescriptions.py` linter; `review-architecture-auditor` Phase 7 consumer.

#### Component 2: Drift-Detection Pipeline (FR-5)

- **Responsibility**: Detect drift in MCP server `tools/list` responses against committed baselines using a four-stage RFC-grounded pipeline.
- **Interface**: `auditing-mcp/scripts/check_tool_surface_drift.py`; baseline at `auditing-mcp/baselines/<server>.json`; severity catalog at `auditing-mcp/references/drift-severity-catalog.md`.
- **Dependencies**: RFC 8785, RFC 6902, MCP transport surface, ADR-0061 severity bridge.

#### Component 3: Agent-Roster Impact Matrix (FR-6)

- **Responsibility**: Force demand-driven evaluation of the full `.claude/agents/*.md` inventory when a feature touches the agent surface; positive-evidence per cell.
- **Interface**: `working/feature/<slug>/agent-roster-impact-matrix.md` (template at `KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md`).
- **Dependencies**: KB-cc-design Principle 9 (post-FR-8 active framing); `auditing-subagents` SA-14 backstop; `check_feature_touch_predicate.py` advisory predicate (D-5 hybrid).

#### Component 4: Skill-Coverage Decisions Section (FR-7)

- **Responsibility**: Pair every new domain concept with a deliberate (a/b/c) decision: existing skill / new W/H/A proposal / no-skill-warranted rationale.
- **Interface**: Synthesis output section + Blueprint section; template at `KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md`.
- **Dependencies**: Synthesis-side emitter `synth-synthesizer` (Q-CC-6 resolved); design-composer blocks on missing justification.

#### Component 5: Blocks-X Marker + Orchestrator Gating (FR-9)

- **Responsibility**: Make Discovery-emitted gating questions into actual stage-transition gates.
- **Interface**: `<!-- BLOCKS: <stage-slug>-completion -->` HTML-comment pragma; grammar spec at `KB-documentation-criteria/references/blocks-x-marker-grammar.md` (per ADR-0063); orchestrator parser.
- **Dependencies**: ADR-0044 v1 free-string `transition_name`; three reserved values for closures.

#### Component 6: Cross-File Invariant Catalog (FR-3)

- **Responsibility**: Enable phase validators to assert cross-file relationships in deliverables with one assertion per relationship; catalog the predicate bodies centrally; declare locally.
- **Interface**: `KB-task-decomposition/cross-file-invariants.md` (CFI-NNN catalog); `test-phase-validator-author.md` Phase 2 rubric Cross-File Invariants section.
- **Dependencies**: ADR-0060 (hybrid shape); ADR-0061 bridge for severity floor.

### Contract Definitions

```yaml
# Companion file (ADR-0059) — illustrative
adr_id: ADR-NNNN
adr_path: adrs/ADR-NNNN-<slug>.md
schema_version: 1.0.0
prescriptions:
  - id: P-1
    summary: <one-line predicate description>
    target_path: <path-relative-to-repo-root>
    assertion:
      kind: regex_present | regex_not_present | jsonpath_equals | jsonpath_count | file_exists | file_not_exists | substring_present | substring_absent
      # additional kind-specific fields...
    severity_floor: BLOCKER | MAJOR | MINOR | INFO
```

```yaml
# Cross-File Invariant (ADR-0060) — illustrative catalog entry
- id: CFI-NNN
  predicate_logic: <natural-language description + machine-checkable pattern>
  error_message_template: <template with placeholders>
  severity_floor: blocking | warning | informational
  applicable_phases: [<phase-slug>, ...]
```

```yaml
# Agent-roster-impact-matrix cell (FR-6) — illustrative
<dimension>: <value> — <positive-evidence-string>
# Where dimension ∈ {tools, skills, model, effort, prompt_body}
# Where value ∈ {no-change, tools-add: ..., tools-remove: ..., skills-add: ..., skills-remove: ..., model-change: ..., effort-change: ..., prompt-edit: ...}
# Bare `no-change` without evidence string fails FR-10 SA-14 backstop audit.
```

### Field Propagation Map

| Field | Boundary | Status | Detail |
|---|---|---|---|
| `severity` | auditor → reviewer surfaces | transformed | Per ADR-0061 bridge table; non-monotonic edges (NIT, MAJOR-branching) require rationale field. |
| `severity` | auditor → phase-validator surfaces | transformed | Same bridge; PV uses `blocking`/`warning`/`informational`. |
| `next_action` | finding emitter → consumer | preserved | NFR-8 four-field shape; emitter populates; consumer reads verbatim. |
| `target_path` | ADR companion → auditor → finding | preserved | Companion declares; auditor reads; finding cites verbatim. |
| `BLOCKS:` stage slug | Discovery output → orchestrator | preserved | Per ADR-0063 grammar; orchestrator extracts slug; description payload dropped. |
| `transition_name` | orchestrator → state-transitions log | preserved | Three reserved values for marker closures; free-string per ADR-0044. |

### State Transitions and Invariants

```yaml
State Definition:
  - Blocks-X marker lifecycle (per FR-9 + ADR-0063):
    - emitted (by discovery-codebase-researcher)
    - active (parsed by orchestrator; gates the named stage)
    - closed (one of three terminal states)

State Transitions:
  emitted → active (parser identifies marker in upstream output)
  active → BLOCKS_X_RESOLVED (closure with rationale; downstream may proceed)
  active → BLOCKS_X_DEFERRED_WITH_OI (closure converts to Open Item; downstream may proceed; OI tracked)
  active → BLOCKS_X_FALSE_POSITIVE (closure with rationale; downstream may proceed)

System Invariants:
  - INV-1: For each active marker M targeting stage S, S cannot be marked complete by the orchestrator (AC-FR-9-a, AC-FR-9-b).
  - INV-2: Every closure transition is logged to state-transitions.log with the marker's slug + rationale (AC-FR-9-c).
  - INV-3: Per AC-FR-3-c, the cross-file finding's severity is the maximum of its component per-file assertions — never downgraded.
  - INV-4: Per AC-FR-1-b, when no ADR in the run has machine-checkable prescriptions (no companion files exist), the auditor no-ops.
  - INV-5: Per AC-FR-6-c, design composition is blocked when the trigger fired and the roster matrix row count ≠ `.claude/agents/*.md` file count at audit time.
```

---

### Claude Code / Project Filesystem Design

The Claude Code layer is the **sole activated layer** for this feature. The per-layer Design subsection from `cc-design.md` is integrated below by reference; reviewers cross-check the per-FR design here against the per-FR design in `cc-design.md`.

**Composer note on per-layer design embed.** Per ADR-0013, the composer integrates per-layer designs verbatim or by close-paraphrase. The cc-design.md content (the 11 per-FR sections, the Companion-file schema, the Drift-detection algorithm flow, the Agent-roster impact matrix schema, the Blocks-X marker grammar, and the Severity vocabulary bridge table) is the load-bearing per-layer-design content and is **integrated by reference into this Blueprint**. See `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` for the full text of:

- §FR-1 through §FR-11 — per-FR design (target files; surface shape; lowest-cost-primitive justification; reasoning-configuration justification).
- §Companion-file schema (D-1 / FR-1) — superseded in canonical-source role by ADR-0059 in this run.
- §Drift-detection algorithm flow (D-7 / FR-5) — superseded in canonical-source role by ADR-0062 in this run.
- §Agent-roster impact matrix schema (FR-6) — preserved as authored.
- §Blocks-X marker grammar (D-4 / FR-9) — superseded in canonical-source role by ADR-0063 in this run.
- §Severity vocabulary bridge table (D-10) — superseded in canonical-source role by ADR-0061 in this run.
- §Skill-coverage decisions for THIS feature (eat-own-dogfood per FR-7) — preserved as authored; 11 decisions all via option (a) covered by existing skills.

**Composer addition.** Beyond the per-layer design content embedded above, this Blueprint integrates cross-cutting concerns and arbitrates the 8 Q-CC items (see §Open Items below).

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.claude/agents/` | 9 sub-agent bodies edited; no new agents | modified (per file list above) |
| `.claude/skills/KB-*/` | 4 KBs edited (cc-design, review-disciplines, documentation-criteria, codebase-research); 2 KBs receive new content (task-decomposition cross-file-invariants; documentation-criteria 3 new templates + grammar spec + deferral conventions) | modified + new content added |
| `.claude/skills/auditing-*/` | 4 audit-skill families touched (auditing-mcp, auditing-cc-configs, auditing-subagents, auditing-shared); auditing-skills gets a new reverse-check rule | modified + 4 new scripts |
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | Outputs table + checkpoint logic | modified |
| `adrs/` | 5 new ADRs (ADR-0059..ADR-0063); optional `.prescriptions.yaml` siblings introduced as a new file pattern | new convention (companions) + 5 new ADRs |

#### CLAUDE.md Updates

**None.** Per KB-cc-design Principle 5 (single source of truth) — CLAUDE.md is the project-root context anchor; new conventions are documented in KBs and discipline texts. CLAUDE.md is not modified in this feature.

#### Slash Commands

| Command Path | Trigger | Purpose | Notes |
|---|---|---|---|
| N/A | N/A | N/A | No slash commands authored or modified in this feature. |

#### Hooks

| Hook Event | Script | Behavior | Failure Mode |
|---|---|---|---|
| N/A | N/A | N/A | No new hooks. Existing hooks unchanged. |

#### Skills

| Skill | Location | When Triggered | What It Provides |
|---|---|---|---|
| KB-cc-design | `.claude/skills/KB-cc-design/` | Always on for design-cc, design-composer | Principle 9 rewritten active; W/H/A rubric; FR-11 deferral sub-section |
| KB-review-disciplines | `.claude/skills/KB-review-disciplines/` | Always on for shared-document-reviewer, review-architecture-auditor, review-cross-artifact-auditor | Lens 4 added; severity bridge added |
| KB-task-decomposition | `.claude/skills/KB-task-decomposition/` | Loaded by `finalize-task-decomposer` + `test-phase-validator-author` | New catalog file `cross-file-invariants.md` |
| KB-codebase-research | `.claude/skills/KB-codebase-research/` | Loaded by `discovery-codebase-researcher` | Additive schema extension `protocol_conformance[]` |
| KB-documentation-criteria | `.claude/skills/KB-documentation-criteria/` | Loaded by every doc-authoring agent | New: grammar spec; 3 templates; 1 conventions discipline file |
| auditing-mcp | `.claude/skills/auditing-mcp/` | Pre-deliverable-packaging | New baselines/ subdir; 2 new scripts; new severity catalog reference |
| auditing-subagents | `.claude/skills/auditing-subagents/` | Pre-deliverable-packaging | New SA-14 rule + script; new advisory predicate for FR-6 triggers |
| auditing-skills | `.claude/skills/auditing-skills/` | Pre-deliverable-packaging | New separate reverse-check rule per Q-CC-7 |
| auditing-shared | `.claude/skills/auditing-shared/` | Cross-audit utility | New `validate_adr_prescriptions.py` linter |
| recipe-feature-pipeline | `.claude/skills/recipe-feature-pipeline/` | Always on for execute-orchestrator | Outputs table extended; Blocks-X checkpoint logic |

#### Sub-Agents

| Sub-Agent | Location | Phase | What It Does |
|---|---|---|---|
| review-architecture-auditor | `.claude/agents/review-architecture-auditor.md` | Architecture Audit (Stage 8) | Adds Lens 4 / Design Realization phase (FR-1) |
| discovery-codebase-researcher | `.claude/agents/discovery-codebase-researcher.md` | Discovery (Stage 1) | §Protocol Conformance subsection + Blocks-X emission (FR-2 + FR-9) |
| test-phase-validator-author | `.claude/agents/test-phase-validator-author.md` | Phase Validator Authoring (Stage 10) | Cross-File Invariants section + deferral-framing check (FR-3 + FR-11) |
| design-cc | `.claude/agents/design-claude-code.md` | Per-Layer Design (Stage 6) | Roster matrix + skill-coverage + Principle 9 cross-reference (FR-6 + FR-7 + FR-8) |
| execute-orchestrator | `.claude/agents/execute-orchestrator.md` | Every stage transition | Blocks-X parser + gating (FR-9) |
| intake-prd-author | `.claude/agents/intake-prd-author.md` | PRD Authoring (Stage 4) | Undetermined Items prompt cross-ref to deferral conventions (FR-11) |
| design-composer | `.claude/agents/design-composer.md` | Design Composition (Stage 7) | Open Items prompt cross-ref to deferral conventions; reads skill-coverage rows (FR-7 + FR-11) |
| synth-synthesizer | `.claude/agents/synth-synthesizer.md` | Synthesis (Stage 5) | Emits Skill-Coverage Decisions section for new domain concepts (FR-7; Q-CC-6 resolved → synthesizer is primary site) |
| cc-critique | `.claude/agents/cc-critique.md` | Various critique surfaces | Flag-rename references updated (FR-4) |

No new sub-agents introduced. Per PRD Won't-Have + `per-agent-design-evaluation-gap` §6.3 non-recommendation.

#### MCP Servers

| Server | Configuration | Tools Exposed | Auth Method |
|---|---|---|---|
| N/A | N/A | N/A | No new MCP servers. The 6 servers in `.mcp.json` are audit targets only (FR-4 reachability handshake; FR-5 drift detection); no edits to `.mcp.json`. |

#### File Naming & Layout Conventions Introduced

- **ADR companion file**: `adrs/ADR-NNNN-<slug>.prescriptions.yaml` — Applies to: ADRs with machine-checkable prescriptions — Enforcement: `auditing-shared/scripts/validate_adr_prescriptions.py` linter (per ADR-0059).
- **MCP baselines**: `.claude/skills/auditing-mcp/baselines/<server-name>.json` — Applies to: each MCP server entry in `.mcp.json` — Enforcement: `check_tool_surface_drift.py` updates only on `--accept-drift` flag (per ADR-0062).
- **Agent-roster impact matrix**: `working/feature/<slug>/agent-roster-impact-matrix.md` — Applies to: every feature run that triggers FR-6 — Enforcement: design-composer block at Stage 7 + auditing-subagents SA-14 backstop at Stage 11 (per FR-6 + FR-10).
- **Blocks-X marker grammar**: `<!-- BLOCKS: <stage-slug>-completion -->` — Applies to: any Discovery output that needs to gate a downstream stage — Enforcement: execute-orchestrator parser at stage transitions (per ADR-0063).
- **Cross-File Invariants section in PV**: required section heading in `test-phase-validator-author` Phase 2 output — Enforcement: PV-author rubric (per ADR-0060).

#### Project Filesystem Error State Design

- **Missing CLAUDE.md**: not relevant — CLAUDE.md is unchanged.
- **Hook script returns non-zero**: no new hooks.
- **Skill frontmatter invalid**: per ADR-0010 — KB SKILL.md edits maintain valid frontmatter; load-time guarantees preserved.
- **Companion file absent for an ADR with prescriptions**: AC-FR-1-b — auditor no-ops; not an error. Companion-required policy is event-triggered: a future operator who finds an FR-1 audit miss may backfill (per ADR-0059 implementation guidance).
- **Baseline absent on first encounter**: AC-FR-5-b — INFO diagnostic; baseline auto-written; not an error.
- **Roster matrix row count diverges from `.claude/agents/*.md` count**: AC-FR-6-c — BLOCKER finding; Design Composition blocked.
- **Active Blocks-X marker at stage transition**: AC-FR-9-b — BLOCKER finding; orchestrator refuses advance.
- **Legacy `--with-runtime` flag invoked**: AC-FR-4-d — `SystemExit(2)` with migration message; loud-fail.

### Frontend Design

N/A — out of scope (per Layer Scope).

### Backend Design

N/A — out of scope (per Layer Scope).

### API Design

N/A — out of scope (per Layer Scope).

### Query & Data Access Design

N/A — out of scope (per Layer Scope).

### Database Schema & Migration Design

N/A — out of scope (per Layer Scope).

### CI/CD Design (GitHub Actions)

N/A — out of scope (per Layer Scope; parallel `pipeline-quickwins-hardening-r1` run owns CI workflow changes).

### Infrastructure as Code Design

N/A — out of scope (per Layer Scope).

### Dev Environment (Codespaces) Design

N/A — out of scope (per Layer Scope; H2 deferred to a future R4).

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---|---|---|---|---|
| Validation | Companion-file YAML schema-invalid | `validate_adr_prescriptions.py` linter | BLOCKER finding; design-composer revises companion | Pipeline halts at Stage 7 review |
| Validation | Roster matrix row count ≠ `.claude/agents/*.md` count | auditing-subagents SA-14 | BLOCKER finding (AC-FR-6-c); design-cc revises matrix | Pipeline halts at Stage 11 |
| Validation | Bare `no-change` in matrix cell without evidence string | SA-14 grep audit | BLOCKER finding (AC-FR-6-d); design-cc fills evidence string | Pipeline halts at Stage 11 |
| External / Transport | MCP server unreachable during handshake | check_mcp_reachability.py (NFR-2 3000 ms timeout) | BLOCKER finding (AC-FR-4-b); operator investigates server | Pipeline halts at Stage 11 |
| External / Transport | Unparseable `tools/list` response | check_tool_surface_drift.py Stage 1 failure | MAJOR finding (AC-FR-5-c); operator investigates | Pipeline halts at Stage 11 |
| Business logic | Allowlisted tool removed from server | drift Stage 4 routing | BLOCKER finding (AC-FR-5-a); operator updates agent allowlists | Pipeline halts at Stage 11 |
| Business logic | Tool signature change on allowlisted tool | drift Stage 4 routing | MAJOR finding (AC-FR-5-e); operator reviews agent compatibility | Pipeline halts at Stage 11 |
| Pipeline | Active Blocks-X marker at stage transition | orchestrator parser | BLOCKER finding (AC-FR-9-b); upstream agent closes marker | Stage advance refused |
| Pipeline | ADR prescription target_path missing | review-architecture-auditor Phase 7 | BLOCKER finding (AC-FR-1-a); implementation phase ships file | Architecture Audit fails |
| Operator | Legacy `--with-runtime` flag invoked | flag-handler in audit_mcp.py | SystemExit(2) with migration message (AC-FR-4-d) | Operator updates invocation; loud-fail by design |

### Logging and Monitoring

- **Log events**: Every FR-9 Blocks-X marker closure (RESOLVED / DEFERRED_WITH_OI / FALSE_POSITIVE) logged to state-transitions.log via `auditing-shared/scripts/log_state_transition.py`. Every FR-6 trigger-evaluation override (advisory predicate result + human ratification) logged.
- **Log levels**: BLOCKER findings at ERROR; MAJOR at WARN; MINOR/INFO at INFO; advisory predicate annotations at DEBUG.
- **Sensitive data**: NFR-6 — credential-shaped strings in transport-error fields are redacted before emission (per ADR-0039).
- **Metrics**: Per-feature-run: count of BLOCKER findings by rule (NFR-8 four-field shape); FR-5 FP-rate counter for NFR-4 measurement (50-audit window).
- **Traces**: Stage-transition events (orchestrator) propagate the active-marker set as context.
- **Alerts**: Future feature runs where SA-14 fires on a feature whose touch was missed by trigger conditions 3/4 (advisory predicate false-negative) — operator review.
- **Dashboards**: N/A (pipeline-internal; no production user surface).

## Implementation Plan

### Implementation Approach

**Selected Approach**: Single-feature R1 posture (per Q-CC-1 / D-6 routing — composer-recommended; user ratifies at Gate 4).

**Selection Reason**: The Contingency Split watch-item names a threshold of 12 cumulative open items. The orchestrator's currently-open count is 6 (does not trip); the codebase researcher's cumulative count is 14 (trips). Both readings have direct PRD evidence. Per synthesis §Contingency-Split Resolution Substrate, the framer's instruction routes to user ratification at Gate 4, with single-feature as the default absent contradicting Gate-4 evidence. Reversibility asymmetry weighs the recommendation toward single: R1 → split later is mechanical (cluster boundaries are already drawn and evidence-grounded); split → merge later is one-way because downstream artifacts ship separately. **See §Contingency Split Decision Record below.**

### Technical Dependencies and Implementation Order

Implementation order follows the mechanism-dependency clusters drawn in PRD-v2 §Contingency Split (which double as implementation phases under the single-feature posture):

#### Required Implementation Order

1. **Phase 0 — Foundations** (per ADR-0061 + ADR-0063 + bridge table + grammar spec, which are load-bearing for downstream FRs):
   - Author `KB-review-disciplines/references/severity-taxonomy.md` updates (bridge table + NFR-8 shape).
   - Author `KB-documentation-criteria/references/blocks-x-marker-grammar.md` (grammar spec).
   - Author `KB-documentation-criteria/references/disciplines/deferral-framing-conventions.md` (three permitted framings).
   - Rationale: every downstream FR consumes one or more of these.

2. **Phase 1 — Design-time discipline cluster (R2a-shaped)**:
   - FR-8: Rewrite KB-cc-design Principle 9 (defensive → active framing); update `design-claude-code.md:56` citation.
   - FR-7: Author W/H/A rubric in KB-cc-design Principle 9 neighborhood; new template `skill-coverage-decisions-section-template.md`; add procedure step in `synth-synthesizer.md` and `design-claude-code.md`; block in `design-composer.md`.
   - FR-6: Author `agent-roster-impact-matrix-template.md`; extend `design-claude-code.md` Phase 2; author `check_feature_touch_predicate.py` advisory predicate (D-5 hybrid); cross-reference Principle 9 per AC-FR-8-b.
   - FR-1: Author `validate_adr_prescriptions.py` linter; extend `review-architecture-auditor.md` with Phase 7; add Lens 4 to `KB-review-disciplines/references/architecture-audit.md`. (No companion files authored yet — those are event-triggered.)
   - FR-9: Author `discovery-codebase-researcher.md` emission discipline; author `execute-orchestrator.md` parser + gating; extend `state-transitions-log-entry-template.md` enumeration; update `recipe-feature-pipeline/SKILL.md` checkpoint logic.
   - FR-10: Author `auditing-subagents` SA-14 + `audit_feature_touch_coverage.py`; author parallel reverse-check rule under `auditing-skills` (per Q-CC-7).

3. **Phase 2 — Gate/validator hardening cluster (R2b-shaped)**:
   - FR-2: Extend `discovery-codebase-researcher.md` with §Protocol Conformance procedure; extend `KB-codebase-research/SKILL.md` schema additively; author `protocol-conformance-subsection-template.md`.
   - FR-3: Author `KB-task-decomposition/cross-file-invariants.md` catalog; extend `test-phase-validator-author.md` Phase 2 with Cross-File Invariants section; cross-reference from `KB-review-disciplines/references/architecture-audit.md`.
   - FR-4: Rename `--with-runtime` → `--with-mcp-reachability` in `auditing-mcp/scripts/audit_mcp.py` + cascading reference updates across `auditing-mcp/`, `auditing-cc-configs/`, `KB-mcp-platform/references/*`, `cc-critique.md`; author `check_mcp_reachability.py`.
   - FR-5: Author `check_tool_surface_drift.py` (four-stage pipeline); author `auditing-mcp/baselines/` subdir + 6 baseline files at first encounter; author `auditing-mcp/references/drift-severity-catalog.md`.
   - FR-11: Extend `KB-cc-design/references/principles.md` with deferral-framing sub-section (Q-CC-8 resolved: sub-section under Principle 9); update `intake-prd-author.md` + `design-composer.md` + `test-phase-validator-author.md` cross-references to the new conventions file.

4. **Phase 3 — Eat-own-dogfood**:
   - Author `working/feature/pipeline-cross-artifact-discipline-r1/agent-roster-impact-matrix.md` (37 rows per current `.claude/agents/*.md` inventory; per FR-6 self-application).
   - Run NFR-4 pilot (50 audits against stable MCP server set; measure FP rate; refine catalog if FP > 5%).

#### Cross-Layer Sequencing Notes

- **Foundations before features**: ADR-0061 + ADR-0063 + deferral conventions must land before FR-6/7/8 procedure edits can cite them.
- **FR-8 before FR-6**: Principle 9's active framing is the load-bearing wording the roster-matrix cells cite (AC-FR-8-b mutual cross-reference).
- **FR-4 before FR-5**: drift detection (FR-5) consumes the same `--with-mcp-reachability` dispatch as the handshake (FR-4).
- **Phase 0 + Phase 1 + Phase 2 may parallelize internally** but FR-8 → FR-6 → FR-1 → FR-9 → FR-10 has a natural serialization in Phase 1 (the citation chain).

### Migration Strategy

- **In-flight features**: Features whose Intent Clarification stage started before this feature ships keep the existing contract. The new disciplines apply only to features whose IC starts after deliverable packaging.
- **Legacy ADRs (ADR-0001..ADR-0058)**: Companion-file backfill is event-triggered (per ADR-0059 + FR-11 framing) — an operator who hits an FR-1 audit miss may author the companion. No bulk backfill required.
- **Existing `--with-runtime` invocations**: Loud-fail (`SystemExit(2)`) ensures stale invocations surface immediately. No silent no-op.
- **Existing Blocks-X prose marker (1 occurrence)**: Not retroactively migrated (per ADR-0063); future emissions use structured grammar.
- **Existing `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1 rows**: Annotate-only (per AC-FR-11-c + register §O.5).

### Feature Flags & Rollout

| Flag | Default | Audience Progression | Kill-Switch Behavior |
|---|---|---|---|
| N/A | N/A | Internal-only pipeline change; first feature run that touches the agent surface AFTER this feature ships is the natural validation point | Per PRD Rollout Plan kill criteria: if matrix discipline (FR-6) breaches NFR-7 30-min budget without preventing detectable defects, FR-6 cell-granularity is revisited; if drift FP rate (NFR-4) exceeds 5% across 3 consecutive runs, FR-5 contract is revisited |

## Security Considerations

### Cross-Cutting

- **Authentication & Authorization**: No new authentication entry points. The MCP reachability handshake (FR-4) consumes existing MCP transport authentication via `.mcp.json` invocations (per ADR-0039 credential indirection). No tokens added to audit output.
- **Input Validation**: Companion-file YAML (FR-1) validated by `validate_adr_prescriptions.py`; malformed companions emit BLOCKER findings rather than crashing. Drift-detection live `tools/list` responses validated through Stage 1 RFC 8785 canonicalization (parseable JSON only).
- **Sensitive Data Handling**: NFR-6 — credential-shaped strings in transport-error fields are redacted before serialization into audit-issues.json (per ADR-0039). No PII; no production data; the feature surface is pipeline-internal.

### Frontend / Backend / API / Query / Database / IaC / Codespaces / CI-CD

All N/A — out of scope per Layer Scope.

### Claude Code

- **Skill loading surface**: New skills/references must conform to ADR-0010 frontmatter discipline; load-time guarantees preserved.
- **No new tool grants**: No sub-agent's tools list expands. Existing `Read`/`Bash`/etc. grants are sufficient for the new procedures.
- **Permission policy**: No new mutating-tool entries. Audit scripts read state and emit JSON; `--with-mcp-reachability` invokes a live JSON-RPC handshake with `.mcp.json` indirection per ADR-0039.
- **Sub-agent reasoning-config dogfood (per advisory finding R-DR-CC-002)**: see §Reasoning-Configuration Audit Table below — every modified sub-agent (including synth-synthesizer and design-composer, the two new entries) is evaluated for reasoning-load delta.

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---|---|---|
| MCP transport (live `tools/list`) | No (in PV tests) / Yes (in unit tests) | PV tests validate against the live MCP servers in `.mcp.json` to exercise the actual four-stage pipeline; unit tests for `check_tool_surface_drift.py` use fixture JSON to test catalog routing. |
| `.claude/agents/*.md` file inventory | No | FR-6 row-count parity asserts against the live filesystem at audit time per AC-FR-6-b. |
| ADR companion files | No (in PV tests) / Yes (in linter unit tests) | PV tests validate against real `adrs/*.prescriptions.yaml`; linter unit tests use fixture YAML. |
| State-transitions log | Yes (unit) / No (integration) | Unit tests for orchestrator parser use fixture logs; integration tests use the actual log writer (`log_state_transition.py`). |

### Data Layer Testing Strategy

- **Schema dependencies**: This feature has no DB schema. The "schemas" exercised by tests are: companion-file YAML (per ADR-0059), CFI-NNN catalog (per ADR-0060), drift-severity-catalog (per ADR-0062), Blocks-X grammar (per ADR-0063).
- **Test data approach**: Fixtures in `tests/fixtures/` (when PV tests authored) for each schema. Real `.claude/agents/*.md` inventory used for FR-6 row-count parity tests.
- **Mock limitations acknowledged**: NFR-4 (<5% drift FP rate) cannot be measured by mocks — the pilot must use live MCP servers across 50 audits. Mocks would defeat the FP-rate measurement purpose.

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|---|---|---|---|
| Claude Code | Unit (linter, script logic) | `pytest` against `auditing-shared/`, `auditing-mcp/`, `auditing-subagents/` scripts | `.claude/skills/<skill>/tests/` (TBD at Plan time) |
| Claude Code | Integration (cross-skill, cross-agent contract) | Phase validators (PV-tier) — assert FR-1/4/5/6/9/10 surface emits correct shape | `working/feature/pipeline-cross-artifact-discipline-r1/phase-validators.md` (Stage 10 deliverable) |
| Claude Code | Acceptance (PRD AC → behavior) | `working/feature/pipeline-cross-artifact-discipline-r1/acceptance-tests.md` (Stage 10 deliverable) | per AC anchors above |

### Integration Verification Points

- FR-1 audit dimension fires correctly when an ADR prescription diverges from the implementation file (positive test) and no-ops when no companion exists (negative test per AC-FR-1-b).
- FR-4 reachability handshake correctly identifies the 6 servers in `.mcp.json`; legacy `--with-runtime` invocation loud-fails per AC-FR-4-d.
- FR-5 four-stage pipeline emits the catalog-specified severities for each patch op type; baseline auto-write on absence; `--accept-drift` semantics work.
- FR-6 design-composer block fires when trigger condition 1 (agent file diff) is satisfied; SA-14 backstop fires at Stage 11.
- FR-9 orchestrator parser handles multi-marker Discovery outputs; state-transitions log entries land with reserved `transition_name` values.
- Bridge table (ADR-0061) translates correctly for non-monotonic edges (NIT vs recommended; MAJOR-branching in PV vocabulary).

## Verification Strategy

### Correctness Proof Method

- **Correctness definition**: "The pipeline structurally refuses to ship a feature that violates any of the 11 invariants" (PRD-v2 thesis). Each FR's AC anchor is the concrete success criterion.
- **Verification method**: (1) PV-tier integration tests assert FR surfaces emit correct shape; (2) acceptance tests map PRD-v2 ACs to behavior; (3) the FR-1 audit dimension self-applies — this Blueprint's own ADR companion files (none yet because this Blueprint's ADRs are decision-narrative ADRs, not prescription ADRs) demonstrate the discipline.
- **Verification timing**: PV authoring (Stage 10); acceptance test authoring (Stage 10); architecture audit re-run of this Blueprint at Stage 8 (eat-own-dogfood — the Lens 4 audit dimension this feature establishes is the same audit dimension that audits this Blueprint).

### Early Verification Point

- **First verification target**: FR-8 + FR-6 + FR-10 together — the smallest cluster that proves the design-time gap closure (B2 + B1 + B5 mechanisms).
- **Success criteria**: design-cc authors the 37-row agent-roster-impact-matrix for this feature; FR-10 SA-14 backstop validates row count parity; Principle 9 active framing cited verbatim in `design-claude-code.md:56`.
- **Failure response**: If matrix authoring time exceeds NFR-7 30-min budget on this 37-row instance, FR-6 cell-granularity (positive-evidence string) is reconsidered per Risks-table mitigation.

### Output Comparison (When Replacing or Modifying Existing Behavior)

- **Comparison input**: Same feature pipeline run on identical input artifacts.
- **Expected output fields**: NFR-5 byte-identical findings JSON (AC-NFR-5-a).
- **Diff method**: JSON field-by-field, byte-exact.
- **Transformation pipeline coverage**: For FR-5, the four-stage pipeline output (Stage 4 severity-catalog routing decisions) must be byte-identical across two identical-input runs.

### Operational Verification (When Pipeline / Infra / Migration in Scope)

- **Pre-merge gates**: shared-document-reviewer Gate 0/1 on this Blueprint; Architecture Audit (Stage 8) on this Blueprint; cross-artifact audit (Stage 9) when Plan + Tests + Phase Validators are authored.
- **Post-deploy verification**: The first feature run that touches the agent surface AFTER this feature ships is the natural operational validation point.
- **Migration verification**: N/A — no schema/data migration. Companion-file backfill is event-triggered.
- **Rollback rehearsal**: N/A — pipeline-internal change; rollback is removing the new affordances (reverting the commits).

## Future Extensibility

- **Extension points**:
  - Companion-file `assertion.kind` vocabulary (per ADR-0059) — new kinds added as new prescription patterns emerge.
  - CFI-NNN catalog (per ADR-0060) — append-only; deprecation via supersession per ADR-0005.
  - Severity bridge table (per ADR-0061) — translator utility (`translate_severity.py`) is optional in v1; may be promoted to mandatory in v2 if mechanical translation becomes more frequent.
  - Drift-detection severity catalog (per ADR-0062) — additive routing rows.
  - Blocks-X grammar (per ADR-0063) — additional `transition_name` values may be reserved in future features.
- **Known future requirements**:
  - H2 (orchestrator-driven Codespace rebuild loop) is the deferred R4 feature.
  - Legacy ADR companion-file backfill is event-triggered; a future feature may bulk-backfill when the operational signal accumulates.
- **Intentional limitations**:
  - No new sub-agents (per `per-agent-design-evaluation-gap` §6.3 non-recommendation).
  - No retroactive register edits (per AC-FR-11-c + register §O.5).
  - No splitting of the Claude Code layer into sub-layers.
  - The hybrid advisory-predicate (D-5) for FR-6 triggers 3+4 is intentionally non-authoritative — the human ratification step scores substance.

## Alternative Solutions

### Alternative 1: Unify severity vocabularies across all audit/review/PV surfaces

- **Overview**: Pick one vocabulary (e.g., auditor `BLOCKER/MAJOR/MINOR/NIT`) and migrate all surfaces.
- **Advantages**: Single canonical vocabulary.
- **Disadvantages**: Destroys audience-fit; one-way reversibility; highest migration cost.
- **Reason for Rejection**: Per ADR-0061 rationale — each vocabulary serves a different audience (auditor for machines; reviewer for humans; PV for gate decisions).

### Alternative 2: NLP-parse ADR prose for FR-1 prescription extraction

- **Overview**: Architecture auditor extracts prescriptions from ADR prose using LLM parsing at audit time.
- **Advantages**: No new companion-file convention; legacy ADRs work as-is.
- **Disadvantages**: 44.57% documented misinterpretation rate (arXiv 2602.07609); non-deterministic; falsifies NFR-5 idempotency.
- **Reason for Rejection**: Per ADR-0059 rationale — 9 of 9 surveyed production systems use schema-anchored separation; non-determinism falsifies NFR-5.

### Alternative 3: R2a/R2b split

- **Overview**: Ship the 11 mechanisms as two feature runs (R2a = design-time discipline; R2b = gate/validator hardening).
- **Advantages**: Smaller per-feature scope; lower per-feature reviewer load.
- **Disadvantages**: Cross-cluster bridges (FR-1 ↔ FR-4/5 via severity bridge; FR-9 ↔ FR-2 via Discovery marker emission) become inter-feature contracts; split is one-way (downstream artifacts ship separately).
- **Reason for Rejection (provisional)**: Routed to user at Gate 4 per Q-CC-1. Single-feature is the default absent contradicting Gate-4 evidence. **See §Contingency Split Decision Record below.**

### Alternative 4: Fully-centralized cross-file invariant catalog (no PV declarations)

- **Overview**: One catalog file owns all invariants; PVs do not declare.
- **Advantages**: Single source of truth.
- **Disadvantages**: Shopify Packwerk v3.0 retrospective is the direct counter; PV authors lose locality; centralized authorship becomes a bottleneck.
- **Reason for Rejection**: Per ADR-0060 rationale — 6 of 6 surveyed systems use hybrid shape; Packwerk migration retrospective is the strongest available counter to fully-centralized.

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|---|---|---|---|---|
| Q-CC-1 Contingency Split — user ratifies split at Gate 4, forcing this Blueprint to be decomposed into two | Claude Code | High | Medium | This Blueprint already organizes Implementation Plan as Phase 0 + R2a-shaped Phase 1 + R2b-shaped Phase 2 — split is mechanical if ratified. |
| NFR-4 (<5% drift FP rate) target not achievable with mechanistic severity catalog | Claude Code | Medium | Medium | Pilot at PV-authoring time measures; severity catalog (per ADR-0062) is the operator dial; description/title/icon rows tuned first if FP > 5%. |
| Companion-file backfill for legacy ADRs (ADR-0001..ADR-0058) becomes operationally costly | Claude Code | Medium | Low–Medium | Per ADR-0059 — backfill is event-triggered (FR-11 framing); hybrid escape hatch (NLP-as-draft, companion-as-canonical) documented as v2 escape. |
| Roster matrix authoring burden creep beyond NFR-7 30-min budget at scale | Claude Code | Medium | Medium | NFR-7 caps wall-clock; FR-6 cell-granularity (positive-evidence string) is first dial to relax per PRD Rollout Plan kill criteria. |
| Em-dash payload separator (` — `) in Blocks-X markers brittle across editor environments | Claude Code | Low | Low–Medium | Per ADR-0063 — separator can be relaxed to ` -- ` two-hyphen-space fallback if brittleness measured operationally. |
| Hybrid CFI catalog grows past ~30 entries without deprecation pressure | Claude Code | Low | Low | Per ADR-0060 kill criteria — denormalized half reconsidered if observable. |
| FR-6 trigger conditions 3+4 advisory predicate produces uneven enforcement (false negatives missed by human ratification) | Claude Code | Medium | Medium | Override events log to state-transitions.log for retrospective tuning per D-5; FR-10 SA-14 backstop is the safety net. |
| Severity bridge table maintenance cost as vocabularies evolve independently | Claude Code | Low | Low | Per ADR-0061 — any vocabulary surface change requires same-PR update to bridge; bridge becomes part of the schema-evolution discipline. |
| The retroactive sweep of devcontainer-mcp-provisioning-r1 caught the gap by chance, not by mechanism | Claude Code | High (was) | (historical) | This feature is the structural prevention; the brief-honor citation is the load-bearing rationale. |
| Q-CC-5 §O.1 row count mismatch (PRD enumerates 4; register has 5) | Claude Code | Low (factual) | High (will surface to user) | Composer surfaces verbatim to user at Gate 4; design grep-tests against all 5 rows. **See §§O.1 Row-Count Correction below.** |

---

## ADRs Authored in This Run

Per FR-5 of the pipeline (only `design-composer` authors ADRs), this Blueprint authors 5 ADRs. Each ADR carries the rationale, decision-details four-row table, options-considered enumeration, and architecture-impact body required by KB-documentation-criteria's ADR template.

| ADR | Title | One-line summary |
|---|---|---|
| **[ADR-0059](../../../adrs/ADR-0059-adr-prescriptions-companion-file.md)** | Companion-File Schema for ADR Design-Realization Audits | Sibling `.prescriptions.yaml` file at `adrs/` carries machine-checkable predicates for FR-1's auditor consumption; ADR prose remains canonical for decision narrative. |
| **[ADR-0060](../../../adrs/ADR-0060-cross-file-invariant-catalog-hybrid.md)** | Cross-File Invariant Catalog Authoring Shape | Hybrid (denormalized declaration per PV + centralized predicate body) at `KB-task-decomposition/cross-file-invariants.md`. |
| **[ADR-0061](../../../adrs/ADR-0061-severity-vocabulary-bridge-table.md)** | Severity Vocabulary Bridge Table Host | Preserve auditor / reviewer / PV trifecta; canonical bridge at `KB-review-disciplines/references/severity-taxonomy.md`. |
| **[ADR-0062](../../../adrs/ADR-0062-mcp-tool-surface-drift-detection-pipeline.md)** | MCP Tool-Surface Drift Detection — Four-Stage Pipeline | RFC 8785 → baseline → RFC 6902 → severity-catalog routing; baselines committed at `auditing-mcp/baselines/`. |
| **[ADR-0063](../../../adrs/ADR-0063-blocks-x-marker-grammar.md)** | Blocks-X Marker Grammar Canonicalization | `<!-- BLOCKS: <stage-slug>-completion -->` HTML-comment pragma; three reserved state-transition `transition_name` values. |

**ADRs deliberately NOT authored in this run:**

- **Implementation-class decisions (D-3, D-5, D-8, D-9)** — these are implementation-shape choices arbitrated in the Blueprint (Q-CC-7, Q-CC-8 dispositions) rather than first-class architectural decisions.
- **§O.1 row-count correction** — this is a PRD-edit-requiring item (Q-CC-5), routed to user ratification at Gate 4 rather than an ADR path.
- **Skill-coverage decisions for this feature** — these are eat-own-dogfood artifacts authored in cc-design.md §Skill-coverage decisions for THIS feature (all 11 via option a), not first-class architectural decisions.
- **Single-feature posture commitment (Q-CC-1 / D-6)** — the framer's instruction is route-to-gate, not lock-in; an ADR would commit a posture the user has not yet ratified. Recorded instead in §Contingency Split Decision Record below.

## Open Items (Q-CC-N) — Composer Arbitration

This Blueprint resolves 7 of the 8 Q-CC items raised by cc-design and surfaces 1 to user ratification at Gate 4. Each disposition is recorded with rationale + evidence.

| Q-CC | Question | Disposition | Rationale | Closing artifact |
|---|---|---|---|---|
| **Q-CC-1** | D-6 Contingency Split posture (R1 vs R2a/R2b) | **Surface to user at Gate 4** with single-feature recommendation. | Per synthesis §Contingency-Split Resolution Substrate, framer's instruction is route-to-gate. Both readings have direct PRD evidence; reversibility asymmetry weighs toward single (split-later is mechanical; merge-later is one-way). User authority required per PRD Won't-Have ("split" is in Won't-Have; changing posture requires user ratification). | §Contingency Split Decision Record (below) |
| **Q-CC-2** | D-10 severity vocabulary bridge table publication target | **Resolved: `KB-review-disciplines/references/severity-taxonomy.md`** | Composer ratifies cc-design's recommendation. Rationale: all three reviewer-surface agents already load `KB-review-disciplines`; bridge lives where primary readers look. Alternative (`auditing-shared/`) considered but rejected because audience-fit is weaker (auditing-shared is utility-host, not reviewer-discipline). | ADR-0061 (authored) |
| **Q-CC-3** | FR-1 companion-file schema versioning policy | **Resolved: additive minor / breaking major** | Composer ratifies cc-design's recommendation. Rationale: matches ADR-0018 + ADR-0038 precedent; new `assertion.kind` values are additive minor bumps; incompatible reorganization is major. | ADR-0059 (authored) |
| **Q-CC-4** | FR-5 baseline storage location | **Resolved: `.claude/skills/auditing-mcp/baselines/<server-name>.json` (committed)** | Composer ratifies cc-design's recommendation. Rationale: reproducibility (cross-operator, cross-CI) requires committed baselines; gitignored runtime path loses the audit trail; `--accept-drift` semantics preserve operator action visibility via git history. | ADR-0062 (authored) |
| **Q-CC-5** | §O.1 row count correction (5 not 4) | **Surface to user at Gate 4** with "preserve all 5 rows" recommendation. | This is a PRD-AC enumeration discrepancy: PRD AC-FR-11-c enumerates 4 rows (E-3, A-3, D-5, I-1); register §O.1 actually contains 5 (A-3, D-5, **E-2**, E-3, I-1). PRD-edit-requiring; user authority needed per ADR-0029 (no silent scope changes). | §§O.1 Row-Count Correction (below) |
| **Q-CC-6** | FR-7 synthesis-side emission agent | **Resolved: `synth-synthesizer.md` (primary)** | Composer ratifies cc-design's recommendation. Rationale: synth-synthesizer composes the final synthesis.md; the Decisions Substrate lives in synth output naturally. synth-framer.md may cross-reference for decision-framing context but emission site is synthesizer. | None (Blueprint procedure-edit only) |
| **Q-CC-7** | D-3 auditing-skills reverse-check separation | **Resolved: separate sibling rule under `auditing-skills`** | Composer ratifies cc-design + synthesis recommendation. Rationale: separation of concerns (auditing-subagents = agent-side reverse refs; auditing-skills = skill-side); low blast radius; reversible; each audit family owns its surface cleanly. | None (Blueprint procedure-edit only) |
| **Q-CC-8** | FR-11 §O posture wording placement | **Resolved: sub-section under Principle 9 of KB-cc-design (option a)** | Composer ratifies cc-design's recommendation. Rationale: avoids principle proliferation (jumping from 9 → 11 across two coupled extensions is messier than two sub-sections); FR-8's active framing and FR-11's deferral framings both attach to "intentional reasoning + intentional discipline" — Principle 9 is the natural locus. Alternative (new Principle 11) considered but rejected for principle-count economy. | None (Blueprint procedure-edit only) |

**Disposition summary**: 6 resolved by composer (Q-CC-2/3/4/6/7/8); 1 closed by authored ADR (each of the 4 ADRs above); 2 surfaced to user at Gate 4 (Q-CC-1 Contingency Split + Q-CC-5 §O.1 row count). The two user-facing items are the only ones requiring user input before the Blueprint advances.

## Contingency Split Decision Record (Q-CC-1 / D-6)

The user's brief explicitly named the contingency split as a watch-item. This section preserves the dual-reading and composer recommendation for Gate 4 user review.

### Reading A — Orchestrator's currently-open count = 6

PRD-v2 declares OI-A1..OI-A6 at PRD time (six open items entering synthesis). Six does not trip the threshold of 12 (per PRD §Contingency Split). Under this reading, the synthesis-stage view is: IC OIs are resolved upstream by PRD authoring; PRD-v2 OIs are the live count entering Design. **Conclusion: ship single feature.**

### Reading B — Codebase researcher's cumulative count = 14

The codebase researcher counts cumulatively: 8 IC OIs + 6 PRD-v2 OIs = 14 (codebase-analysis-report.md line 263 verbatim). PRD calibration text (line 472) reads: "the threshold of 12 is calibrated as follows: the 4-cycle reconciliation cap, empirically across recent feature runs, terminates around 12–15 active open items; choosing 12 gives a margin and surfaces the question before the cap is hit." Under this reading, the threshold is already met at synthesis dispatch — the split-recommendation has pre-fired. **Conclusion: recommend split.**

### Composer recommendation: ship single-feature R1 absent contradicting Gate-4 evidence

The framer's instruction in synthesis §Contingency-Split Resolution Substrate is route-to-gate. The composer ratifies that routing rather than overriding it. Rationale for the single-feature default:

1. **Reversibility asymmetry**: R1 → R2 split later is mechanical because cluster boundaries are already drawn and evidence-grounded (R2a = FR-1, FR-6, FR-7, FR-8, FR-9, FR-10; R2b = FR-2, FR-3, FR-4, FR-5, FR-11; cross-cluster bridges identified). R2 → R1 merge later is one-way because downstream artifacts (Blueprints, ADRs, phase-validators) will have been authored separately.
2. **Won't-Have authority**: PRD Won't-Have excludes split; changing posture requires user ratification at Gate 4.
3. **Synthesis confidence**: synthesis recommends single absent contradicting evidence; this composer pass surfaced no new contradicting evidence (no per-FR sub-decision exceeded 3 distinct sub-decisions; no Gate 0/1 reviewer twice-`needs_revision` on the same FRs).
4. **Implementation-plan organization**: this Blueprint's Implementation Plan already organizes work as Phase 0 (foundations) + Phase 1 (R2a-shaped) + Phase 2 (R2b-shaped) — internal sequencing matches the split cluster boundaries, so the work is split-ready if the user ratifies split.

### Contradicting evidence the user should evaluate at Gate 4

The user should ratify split if any of these hold:

- The 14 cumulative OI count (Reading B) is the count the user wishes to weight.
- R1 design-time scope exceeds reviewer capacity (reviewer estimates that a single-Blueprint review at this scale is more than they want to absorb).
- R1 ADR count (5 in this Blueprint) plus the 6+ PRD OIs together exceed the 4-cycle cap risk-tolerance the user wishes to set.
- Coordination cost between R2a/R2b clusters exceeds the cost of one larger feature (the composer's reading is the opposite — coordination cost is lower in a single feature because the bridges are internal contracts; but the user may weight differently).

### What happens on user ratification

- **User ratifies single feature**: Blueprint advances as-is to Architecture Audit. The Contingency Split watch-item is closed for this feature.
- **User ratifies split**: This Blueprint is decomposed into two — R2a-shaped (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) and R2b-shaped (FR-2, FR-3, FR-4, FR-5, FR-11). The Phase 0 foundations (ADR-0061 bridge table, ADR-0063 grammar spec, deferral conventions) ship with whichever cluster goes first; the cross-cluster bridges (severity bridge; Blocks-X grammar consumed by §Protocol Conformance schema) become shared contracts authored in whichever cluster ships first.

## §O.1 Row-Count Correction (Q-CC-5) — User-Facing Gate 4 Item

This is a small but factual PRD-AC enumeration discrepancy that the user should review at Gate 4.

### The discrepancy

- **PRD AC-FR-11-c** enumerates **FOUR** rows to preserve verbatim: **E-3, A-3, D-5, I-1**.
- **Register §O.1** (the actual `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1) actually contains **FIVE** rows: **A-3, D-5, E-2, E-3, I-1**.

The fifth row, **E-2 — "Serena felt-utility review post-ship"**, has the same post-ship anti-pattern shape as the other four (it is a deferral with a "post-ship" trigger phrasing that has no firing mechanism in the project).

### Composer recommendation

**Preserve all FIVE rows verbatim.** The PRD's omission of E-2 from AC-FR-11-c is best read as oversight rather than deliberate exclusion (the synthesizer's verification surfaced the discrepancy; no PRD-level rationale for excluding E-2 exists in the PRD prose). Preservation is purely additive (no edits to existing rows; AC-FR-11-c grep-tests against the verbatim §O.1 content regardless of row count).

### What the user should ratify at Gate 4

Two paths:

1. **Ratify "preserve five"** (composer recommendation): AC-FR-11-c is updated to enumerate all five rows. Design ships as written.
2. **Ratify "preserve four, exclude E-2 deliberately"**: AC-FR-11-c stays at four-row enumeration; design adjusts the FR-11 implementation grep-test accordingly. User provides rationale for the exclusion.

### Constraint preserved either way

Per AC-FR-11-c + register §O.5: **no retroactive edits** to the register's §O.1 content. Both paths preserve this — only the AC enumeration changes, not the register.

## Decisions Adopted (D-1 .. D-10) — Final Disposition

| Decision | Topic | Final disposition | Authored ADR |
|---|---|---|---|
| **D-1 (OI-A1)** | FR-1 prescription-extraction mechanism | **Companion file** at `adrs/ADR-NNNN-<slug>.prescriptions.yaml`. Schema v1.0; additive-minor versioning. | ADR-0059 |
| **D-2 (OI-A2)** | FR-3 invariant authoring shape | **Hybrid** — denormalized declaration in PV body + centralized catalog at `KB-task-decomposition/cross-file-invariants.md`. | ADR-0060 |
| **D-3 (OI-A3)** | auditing-skills reverse-check scope | **Separate rule** under `auditing-skills` (Q-CC-7 resolved). | None (Blueprint procedure-edit) |
| **D-4 (OI-A5)** | Blocks-X marker grammar | **Structured HTML-comment pragma** `<!-- BLOCKS: <stage-slug>-completion -->`. | ADR-0063 |
| **D-5 (OI-A6)** | FR-6 trigger 3+4 evaluator | **Hybrid advisory predicate + human ratification** at Design Composition Gate. | None (Blueprint procedure-edit + Plan-time script) |
| **D-6 (Contingency Split)** | R2a vs R2b posture | **Single-feature R1** (composer recommendation; user ratifies at Gate 4 per Q-CC-1). | None (route-to-gate, not lock-in) |
| **D-7 (FR-5 algorithm)** | Drift-detection pipeline | **Four-stage** RFC 8785 → baseline → RFC 6902 → severity catalog; baselines committed at `auditing-mcp/baselines/`. | ADR-0062 |
| **D-8 (FR-7 W/H/A)** | Skill-coverage trifecta posture | **Substance-as-rubric** for skill-coverage decisions; **mandate-as-artifact** for new-skill proposals (carve-out). | None (Blueprint procedure-edit) |
| **D-9 (FR-11 §O placement)** | Posture wording host | **Three-host placement** — KB-cc-design (sub-section under Principle 9 per Q-CC-8) + test-phase-validator-author + KB-documentation-criteria deferral conventions. | None (Blueprint procedure-edit) |
| **D-10 (severity vocabulary)** | Reconciliation across FR-1/4/5/9/10 | **Preserve trifecta + explicit bridge table** at `KB-review-disciplines/references/severity-taxonomy.md` (Q-CC-2 resolved). | ADR-0061 |

## Reasoning-Configuration Audit Table

Per FR-8 active framing (KB-cc-design Principle 9 post-this-feature), every sub-agent on the touched agent surface — changed and unchanged alike — receives a per-agent consideration on the three reasoning fields (`model:`, `effort:`, `skills:`). This Blueprint records the consideration for each modified agent **plus the two new dogfood-additions** per advisory finding R-DR-CC-002.

| Sub-agent | Current `model:` | Current `effort:` | Current `skills:` | Reasoning-load delta | Final disposition |
|---|---|---|---|---|---|
| `review-architecture-auditor` | opus | xhigh | KB-review-disciplines, others | New Phase 7 adds cross-document reconciliation; xhigh remains warranted | **No change** — model/effort/skills preserved |
| `discovery-codebase-researcher` | opus | high | KB-codebase-research, KB-documentation-criteria, others | Protocol-conformance enumeration is bounded per-interface; high covers it | **No change** |
| `test-phase-validator-author` | opus | high | KB-task-decomposition, KB-review-disciplines, others | Cross-file invariant authoring is bounded; high covers it | **No change** |
| `design-cc` | opus | high | KB-cc-platform, KB-cc-design, KB-documentation-criteria, others | Matrix authoring bounded by NFR-7 30-min budget at 100 agents; high covers it | **No change** |
| `execute-orchestrator` | inherits from caller | inherits | recipe-feature-pipeline | Blocks-X parser is mechanical (regex match); no reasoning load delta | **No change** |
| `intake-prd-author` | opus | high | KB-documentation-criteria, others | Undetermined Items prompt cross-reference is mechanical (one-line addition); no reasoning load delta | **No change** |
| `design-composer` (this agent, R-DR-CC-002 dogfood) | opus | xhigh | KB-documentation-criteria, KB-review-disciplines, KB-general-coding-principles, all per-layer KBs | Cross-layer arbitration with 8 Q-CC items + 5 ADR authoring + integration discipline; reasoning load is high but consistent with xhigh baseline for cross-layer fan-in role | **No change** — xhigh is the right baseline for composer role |
| `synth-synthesizer` (R-DR-CC-002 dogfood; FR-7 emission site) | opus | xhigh | KB-task-decomposition, KB-review-disciplines, KB-documentation-criteria, others | New Skill-Coverage Decisions section emission adds one bounded enumeration step; existing xhigh covers the cross-source reconciliation reasoning that drives the synthesis pass | **No change** |
| `cc-critique` | (inherits/varies) | (inherits/varies) | various | Flag-rename references only (FR-4); no reasoning load delta | **No change** |

**Consideration recorded for every agent on the touched surface; no `bare no-change` cells per FR-6 cell discipline.** This table is the eat-own-dogfood instance of FR-6 + FR-8 active-framing applied to this Blueprint's own composition; the full 37-row `agent-roster-impact-matrix.md` for this feature run is authored at Plan / Task Decomposition time (per cc-design.md §Agent-roster impact for THIS feature).

## Constraint Propagation Check

This Blueprint's design honors every PRD-v2 constraint and every inherited-ADR constraint:

| Constraint | Source | Honored? | Evidence |
|---|---|---|---|
| Claude Code layer only | PRD-v2 Layer Scope | Yes | All 41 touchpoints under `.claude/`, `adrs/`, `Issues/` (annotate-only); no edits to product-surface layers |
| No new sub-agents | PRD-v2 Won't-Have | Yes | 9 existing sub-agents edited; 0 new sub-agents authored |
| No retroactive register edits | PRD AC-FR-11-c + register §O.5 | Yes | `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` marked `annotate-only` in cc-dependencies.json |
| No CI/CD workflow changes | PRD-v2 Won't-Have (parallel run owns these) | Yes | Zero `.github/workflows/` edits |
| 4-cycle reconciliation cap | PRD-v2 §Constraints | Provisionally Yes | Contingency Split mechanism active; threshold-12 check applied; composer recommends single-feature with route to user at Gate 4 (Q-CC-1) |
| ADR-0036 + ADR-0054 + ADR-0056 (canonical placement, no carve-outs) | Inherited ADRs | Yes | All 5 new ADRs at `adrs/`; companion files (when authored) at `adrs/`; no subdirectories; no extension-based carve-out (ADR-0059 §Placement discipline) |
| ADR-0005 (append-only supersession) | Inherited ADR | Yes | Principle 9 edited in place per ADR-0005 + ADR-0022; existing principle ID preserved |
| ADR-0044 (state-transitions log free-string `transition_name`) | Inherited ADR | Yes | Three reserved values added without schema evolution (per ADR-0063) |
| ADR-0045 (review-architecture-auditor has no Agent/Task tool) | Inherited ADR | Yes | FR-1's Phase 7 runs inline; no sub-agent spawn-out |
| ADR-0018 + ADR-0038 (additive schema-extension discipline) | Inherited ADRs | Yes | FR-2 `protocol_conformance[]` extension is additive; legacy consumers unaffected |
| ADR-0039 (credential indirection) | Inherited ADR | Yes | NFR-6 redaction posture rides on it; no credentials in audit output |
| NFR-9 (grep-checkable affordance referencing) | PRD-v2 NFR-9 | Yes | All 14 new affordances reachable from a consuming agent's `skills:` list (template files reachable via KB-documentation-criteria load; catalog reachable via KB-task-decomposition load; etc.) |

**No violations.** The Blueprint is constraint-clean.

## Cross-References

### Inherited ADRs Applied

ADR-0005, ADR-0009, ADR-0010, ADR-0013, ADR-0016, ADR-0017, ADR-0018, ADR-0020, ADR-0022, ADR-0027, ADR-0030, ADR-0036, ADR-0038, ADR-0039, ADR-0040, ADR-0041, ADR-0042, ADR-0044, ADR-0045, ADR-0046, ADR-0054, ADR-0056. See `Background and Context / Prerequisite ADRs` for each ADR's relevance.

### ADRs Authored in This Run

ADR-0059 (companion file), ADR-0060 (cross-file invariant hybrid), ADR-0061 (severity bridge), ADR-0062 (drift-detection pipeline + baseline location), ADR-0063 (Blocks-X grammar). See `ADRs Authored in This Run` table above.

### Q-CC Dispositions

| ID | Status | Resolution location |
|---|---|---|
| Q-CC-1 | Surface to user at Gate 4 | §Contingency Split Decision Record |
| Q-CC-2 | Resolved | ADR-0061 |
| Q-CC-3 | Resolved | ADR-0059 §Versioning policy |
| Q-CC-4 | Resolved | ADR-0062 §Baseline location |
| Q-CC-5 | Surface to user at Gate 4 | §§O.1 Row-Count Correction |
| Q-CC-6 | Resolved | Open Items table |
| Q-CC-7 | Resolved | Open Items table |
| Q-CC-8 | Resolved | Open Items table |

### Advisory Findings from shared-document-reviewer

Per the orchestrator's pass-through of R-DR-CC-001 through R-DR-CC-005:

- **R-DR-CC-001** (prose-vs-sidecar create-count drift 11 vs 14): addressed in `Existing Codebase Analysis / Reconciliation of summary counts` above. Adopted sidecar's 14 as canonical.
- **R-DR-CC-002** (reasoning-config dogfood for synth-synthesizer + design-composer): addressed in §Reasoning-Configuration Audit Table above. Both agents added; both evaluated for reasoning-load delta; both `no-change` with positive evidence.
- **R-DR-CC-003** (NFR-4 FP-pilot deferral framing): addressed in `Risks and Mitigation` and `Verification Strategy / Early Verification Point` — the pilot is event-triggered ("at PV-authoring time"), an honest-acceptance framing of the mechanistic <5% claim, and concrete machinery (`check_tool_surface_drift.py` Stage 4 catalog is the operator dial).
- **R-DR-CC-004** (cardinality of templated companion-file path): addressed by ADR-0059 stating the companion is **optional** per ADR; cardinality is 0..N companions across the ADR registry (one per ADR with machine-checkable prescriptions); the path template `adrs/ADR-NNNN-<slug>.prescriptions.yaml` is parameterized by the ADR's NNNN + slug.
- **R-DR-CC-005** (11-FR / 11-new-concept coincidence): noted here — the 11 functional requirements in PRD-v2 and the 11 new domain concepts enumerated in cc-design.md §Skill-coverage decisions for THIS feature are coincidentally aligned but not structurally coupled. Future features may introduce more or fewer new domain concepts than functional requirements; the alignment in this feature is a property of its mechanism enumeration, not a design pattern to preserve.

## References

- `working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md` — the approved PRD this Blueprint derives from.
- `working/feature/pipeline-cross-artifact-discipline-r1/intent-clarification.md` — the IC approved upstream.
- `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` — the per-layer Claude Code design integrated by reference.
- `working/feature/pipeline-cross-artifact-discipline-r1/cc-dependencies.json` — the per-layer dependencies sidecar (canonical create-count: 14).
- `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` — the synthesis output (D-1..D-10 decision substrate).
- `working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json` and `codebase-analysis-report.md` — the discovery output.
- `working/feature/pipeline-cross-artifact-discipline-r1/research-notes/T-001.md` through `T-004.md` — the external research grounding.
- `Issues/cross-artifact-divergence-detection-gap/analysis.md` — source for H1, H3, H6, H8, H9 mechanisms.
- `Issues/per-agent-design-evaluation-gap/analysis.md` — source for B1, B2, B3, B4, B5 mechanisms.
- `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` — source for §O posture; preserved verbatim per AC-FR-11-c + §O.5.
- `adrs/ADR-0041-install-mechanism-hybrid.md` — the canonical exemplar of prescription drift that FR-1 + ADR-0059 close.
- `adrs/ADR-0040-serena-narrowed-always-on.md` — the canonical exemplar of the per-agent-design-evaluation-gap that FR-6 closes.
- `adrs/ADR-0059-adr-prescriptions-companion-file.md`, `ADR-0060-cross-file-invariant-catalog-hybrid.md`, `ADR-0061-severity-vocabulary-bridge-table.md`, `ADR-0062-mcp-tool-surface-drift-detection-pipeline.md`, `ADR-0063-blocks-x-marker-grammar.md` — the 5 ADRs authored in this run.
- RFC 8785 (JSON Canonicalization Scheme); RFC 6902 (JSON-Patch).
- `KB-documentation-criteria/references/templates/blueprint-template.md` — the template this Blueprint conforms to (per ADR-0013).

## Update History

| Date | Version | Changes | Author |
|---|---|---|---|
| 2026-05-26 | 1.0.0 | Initial Blueprint composition. Integrates `cc-design.md` per-layer design; arbitrates 8 Q-CC items (6 resolved, 2 surfaced to user at Gate 4); authors 5 ADRs (ADR-0059..ADR-0063); addresses 5 advisory findings R-DR-CC-001..005 from shared-document-reviewer. Implementation Plan organized as Phase 0 (foundations) + Phase 1 (R2a-shaped) + Phase 2 (R2b-shaped) + Phase 3 (eat-own-dogfood) — split-ready if user ratifies Contingency Split at Gate 4. | design-composer |

---

*End of Blueprint v1.0. Awaiting `shared-document-reviewer` (invocation 4) Gate 0 / Gate 1 review, then `review-architecture-auditor` (Stage 8 — including the self-applied Lens 4 audit dimension this Blueprint establishes), then user ratification of Q-CC-1 (Contingency Split) and Q-CC-5 (§O.1 row count) at Gate 4.*
