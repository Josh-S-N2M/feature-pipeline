---
id: Plan-execution-pipeline-design-r1
version: 1.0.0
status: superseded
superseded_by: working/feature/execution-pipeline-design-r1/plan-v2.md
superseded_at: 2026-05-22T23:30:00Z
feature_slug: execution-pipeline-design-r1
derived_from: working/feature/execution-pipeline-design-r1/blueprint-v4.md
phases: 7
total_tasks: 28
generated: 2026-05-22T20:25:00Z
generated_by: claude (acting as plan-author; claude.ai simulation — see scope deviation surfacing below)
agent_invocation_simulation: true
agent_invocation_note: |
  This Plan is produced by claude.ai simulating the plan-author agent. The
  authoritative Claude Code plan-author invocation remains pending Josh's shift.
  This simulated Plan is structurally correct (phase taxonomy, L1/L2/L3
  discipline, dependency edges) but task-level detail may benefit from refinement
  by the authoritative Claude Code pass. Treat task descriptions as a starting
  point; verify acceptance-criterion coverage against the PRD before execution.
supersession_note: |
  Superseded by plan-v2.md (authoritative; non-simulated; derived from blueprint-v5
  which passed Architecture Audit round 7). v1 was structurally correct but task-level
  detail derived from blueprint-v4 (now superseded by v5). Per ADR-0005 append-only
  supersession, the body of this file remains unchanged; only the frontmatter is
  updated to reflect the supersession relationship.
---

# Plan: Execution Pipeline Design (run r1)

## Contents

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — auditing-shared scripts cluster
- [x] Phase 2 — Skill installs (extract / stub / new install)
- [x] Phase 3 — Execution-phase agent authoring
- [x] Phase 4 — Existing-agent extensions + convention updates
- [x] Phase 5 — Template authoring for new artifact types
- [x] Phase 6 — End-to-end pipeline smoke test
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

This Plan decomposes the execution-pipeline-design-r1 Blueprint v4.0.0 into 28 executable tasks across 7 phases. The feature introduces the execution-side of the feature pipeline (12-state machine, 5 new subagents, 4 new auditing scripts, 1 new skill install, 2 skill modifications, and the artifact-frontmatter conventions per ADR-0032). The Plan honors:

- The Blueprint's Agent Frontmatter Specifications subsection (canonical YAML for 5 new agents, verified Gate 4 platform-valid in v4)
- AC-FR-9-e sequencing constraint (`ai-development-guide` skill install MUST precede code-producer + quality-handler agent-authoring)
- ADR-0031 (auditing-shared module pre-exists; new scripts add to it rather than replacing)
- ADR-0017 4-cycle cap (symmetric per ADR-0034; the orchestrator enforces this at runtime, not implementation time)
- The Claude Code platform constraints verified at Gate 4 (memory field enum, Edit tool validity, non-KB skill binding validity, Agent vs TaskCreate/TaskUpdate tool family distinction)

## Source

- **Blueprint**: `working/feature/execution-pipeline-design-r1/blueprint-v4.md` (v4.0.0, draft; Gate 4-verified)
- **PRD**: `working/feature/execution-pipeline-design-r1/prd-v1.1.0.md` (v1.1.0, gate_passed=2)
- **ADRs new this feature**: ADR-0032 (conventions canonicalization), ADR-0033 (ADR-0029 execution extension), ADR-0034 (PRD mis-credit cleanup; revised in v2; all proposed)
- **Phase taxonomy used**: Phase 0 (Setup) through Phase 6 (End-to-end smoke test). No Phase N+1 Rollout because the feature is internal infrastructure — no production-traffic flip, no observability dashboard to configure beyond the state-transitions.log + pipeline-run-summary.json which the orchestrator emits.

## Phase 0 — Setup

### Goal

Pre-flight: confirm Blueprint approval, prepare working directories, ensure the auditing-shared module's pre-existing scripts are intact, and stage ADR transitions from proposed → accepted.

### Tasks

#### T0.1: Verify Blueprint v4 reviewer_verdict

- **Layer:** cc (pipeline scaffolding)
- **Description:** Confirm blueprint-v4.md frontmatter has been updated by Gate 4 reviewer to reflect approval. If still draft, surface as blocker; no execution work proceeds without Blueprint approval.
- **Dependencies:** none
- **Estimate:** XS (5 min check)
- **Satisfies AC:** N/A (gating only)
- **L1 verification:** grep `reviewer_verdict: approved` in blueprint-v4.md frontmatter
- **L2 verification:** N/A
- **L3 verification:** N/A

#### T0.2: Advance ADR-0032, ADR-0033, ADR-0034 from proposed → accepted

- **Layer:** cc
- **Description:** Update each ADR's frontmatter `status: proposed` → `status: accepted` per the per-doc-type ADR vocabulary in ADR-0032 (4-state: `proposed → accepted | superseded | rejected`). Per ADR-0005, this is a frontmatter-only edit; ADR bodies unchanged. Three ADRs total.
- **Dependencies:** T0.1
- **Estimate:** S (15 min)
- **Satisfies AC:** N/A (ADR governance)
- **L1 verification:** grep `status: accepted` in each of ADR-0032, ADR-0033, ADR-0034
- **L2 verification:** Run shared-document-reviewer on each ADR; verify the `proposed → accepted` transition is valid per the new per-doc-type vocabulary
- **L3 verification:** N/A (one-time governance action)

#### T0.3: Create working directory for execution-phase artifact templates

- **Layer:** cc
- **Description:** Create `.claude/skills/KB-documentation-criteria/references/templates/execution-phase/` directory. Sub-templates for the 5 floor artifacts (per AC-FR-7-c) will be authored here in Phase 5.
- **Dependencies:** T0.1
- **Estimate:** XS
- **Satisfies AC:** N/A (scaffolding for AC-FR-7)
- **L1 verification:** Directory exists
- **L2 verification:** N/A
- **L3 verification:** N/A

#### T0.4: Stage auditing-shared module's new-script entries (placeholder files)

- **Layer:** cc
- **Description:** Create placeholder files at `.claude/skills/auditing-shared/scripts/` for each of the 7 new scripts (per Blueprint Component 10). Files contain just a shebang + docstring header. This stages the file inventory so Phase 1 script-authoring tasks can populate them.
- **Dependencies:** T0.1
- **Estimate:** S (15 min)
- **Satisfies AC:** N/A (staging for FR-5, FR-6, AC-FR-2-d, AC-FR-3-c, D-15)
- **L1 verification:** 7 placeholder files exist with valid shebang lines
- **L2 verification:** `python3 -c "import ast; [ast.parse(open(f).read()) for f in glob.glob('.claude/skills/auditing-shared/scripts/*.py')]"` parses all 7
- **L3 verification:** Deferred to Phase 1 task-completion

### Phase 0 Exit Criteria

- Blueprint v4 approved (T0.1 verified)
- 3 ADRs accepted (T0.2 complete)
- Template + script staging directories ready (T0.3, T0.4)

## Phase 1 — auditing-shared scripts cluster

### Goal

Author the 7 new scripts in the auditing-shared module per Blueprint Component 10. These scripts are the substrate other components depend on: the frontmatter validator (FR-6), state-transition logger (FR-5), stub detector (AC-FR-2-d / Q-CC-2), phase-quality coordinator (AC-FR-3-c), and the optional discipline-check (D-15 option 2).

### Tasks

#### T1.1: Author `validate_pipeline_frontmatter.py`

- **Layer:** cc
- **Description:** Per FR-6 + ADR-0032's per-doc-type schemas. Reads target file; emits structured JSON output (per-finding severity + path). Validates all artifact types listed in `doc_type` enum. Honors the auditing-shared schema for findings (per Component 10).
- **Dependencies:** T0.4
- **Estimate:** M (3-4 hours)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b, AC-FR-6-c (frontmatter validator core), AC-FR-9-c (validates `ai-development-guide` binding)
- **L1 verification:** Script parses, --help prints
- **L2 verification:** Run against a known-bad-frontmatter fixture; verify findings emit with correct severity. Run against a known-good fixture; verify zero findings.
- **L3 verification:** Run against all artifacts in `working/feature/execution-pipeline-design-r1/`; verify reasonable findings (most should pass; surfacings should be deliberate)

#### T1.2: Author `log_state_transition.py`

- **Layer:** cc
- **Description:** Per FR-5 + D-16. Reads transition payload from stdin (JSON); appends JSONL entry to `state-transitions.log`. Hook is observer-only in v1 — failure does NOT block transition (Blueprint § Component 1, line referencing D-16 application-level hook).
- **Dependencies:** T0.4
- **Estimate:** S (1-2 hours)
- **Satisfies AC:** AC-FR-5-a, AC-FR-5-b, AC-FR-5-c, AC-FR-5-d, AC-FR-5-e
- **L1 verification:** Script parses, --help prints
- **L2 verification:** Pipe a valid JSON payload; verify JSONL line appended with correct fields. Pipe an invalid payload; verify non-blocking failure with stderr log per AC-FR-5-e.
- **L3 verification:** Invoked from orchestrator simulation; verify state-transitions.log accumulates correctly across a multi-task run

#### T1.3: Author `detect_stubs.py`

- **Layer:** cc
- **Description:** Per AC-FR-2-d + Q-CC-2 path-aware patterns. Scans modified files for stub patterns (TODO, FIXME, pass-only function bodies, etc.). Returns structured findings.
- **Dependencies:** T0.4
- **Estimate:** M (3-4 hours)
- **Satisfies AC:** AC-FR-2-d, AC-FR-2-e, Q-CC-2 (path-aware patterns adapted from `detect_skill_stubs.py`)
- **L1 verification:** Script parses, --help prints
- **L2 verification:** Run against known-stub fixture; verify STUB_DETECTED severity. Run against known-clean fixture; verify zero findings.
- **L3 verification:** Run against an execute-task-code-producer output simulation; verify integration with quality-handler's pre-quality-check invocation per D-2d

#### T1.4: Author `run_phase_checks.py`

- **Layer:** cc
- **Description:** Per AC-FR-3-c + D-3 third-option coordinator. Aggregates 3 test layers (unit/integration/E2E) + 3 audit families (cc-audit, GHA audit, Codespaces audit) + FR-6 validator + optional discipline-check into a single structured-finding stream. The phase-quality-reviewer consumes this.
- **Dependencies:** T1.1, T1.3
- **Estimate:** L (5-7 hours)
- **Satisfies AC:** AC-FR-3-a, AC-FR-3-b, AC-FR-3-c, FR-3 substrate
- **L1 verification:** Script parses, --help prints
- **L2 verification:** Run against a phase with no findings; verify zero findings emitted. Run against a phase with mixed findings; verify aggregation correctness.
- **L3 verification:** Full pipeline integration — invoked by execute-phase-quality-reviewer simulation; verify the JSON structure matches D-13 dimensional verdict schema

#### T1.5: Author `check_pipeline_discipline.py` (D-15 option 2)

- **Layer:** cc
- **Description:** Per D-15 option 2 + AC-FR-3-d. Detects pipeline-stage-by-number references (e.g., "stage 12" instead of "Task Decomposition") in authored artifacts. Mechanical check; surfaces findings via dispatch matrix per ADR-0033.
- **Dependencies:** T0.4
- **Estimate:** M (2-3 hours)
- **Satisfies AC:** AC-FR-3-d, D-15 substrate
- **L1 verification:** Script parses, --help prints
- **L2 verification:** Run against fixture with "stage 12" reference; verify finding. Run against clean fixture; verify zero findings.
- **L3 verification:** Invoked by run_phase_checks coordinator (T1.4); verify findings flow into dispatch matrix correctly

#### T1.6: Author `audit_codespaces.py` (stub per AC-FR-8-b)

- **Layer:** cc
- **Description:** Per AC-FR-8-b + Q-CC-4. Stub implementation: returns `{"stub": true, "findings": []}` per ADR-0033's stub-distinction discipline. Real implementation deferred to follow-on feature.
- **Dependencies:** T0.4
- **Estimate:** XS (30 min — it's a stub)
- **Satisfies AC:** AC-FR-8-b, Q-CC-4
- **L1 verification:** Script parses, returns stub envelope
- **L2 verification:** Verify `stub: true` field present in output (distinguishes from real-but-empty audit per ADR-0033)
- **L3 verification:** Integrated into run_phase_checks (T1.4); verify the stub envelope flows through dispatch correctly per ADR-0033

#### T1.7: Author end-to-end auditing-shared smoke test

- **Layer:** cc
- **Description:** A single script (`smoke_test_auditing_shared.py` or similar) that exercises T1.1-T1.6 end-to-end against test fixtures. Verifies the auditing-shared module is internally consistent.
- **Dependencies:** T1.1, T1.2, T1.3, T1.4, T1.5, T1.6
- **Estimate:** M (2-3 hours)
- **Satisfies AC:** FR-13 substrate (machine-parseable reconciliation log; smoke test validates this)
- **L1 verification:** Script parses; smoke test runs to completion without script-load errors
- **L2 verification:** Test fixtures cover happy + error paths for each script
- **L3 verification:** Smoke test in CI confirms regressions caught

### Phase 1 Exit Criteria

- 7 scripts authored, parse, --help prints
- Smoke test passes
- Frontmatter validator (T1.1) self-checks: runs against blueprint-v4.md and reports clean

## Phase 2 — Skill installs (extract / stub / new install)

### Goal

Per AC-FR-8 and AC-FR-9-e sequencing: extract `auditing-github-actions` from KB-github-actions-platform; stub `auditing-codespaces`; install new `ai-development-guide`. Phase 2 must complete BEFORE Phase 3 because Phase 3 agents bind to these skills.

### Tasks

#### T2.1: Extract `auditing-github-actions` from KB-github-actions-platform

- **Layer:** cc
- **Description:** Per AC-FR-8-a. Create `.claude/skills/auditing-github-actions/` with SKILL.md describing the audit functionality + scripts/ subdirectory. Migrate the relevant audit logic from KB-github-actions-platform. Update KB-github-actions-platform's SKILL.md to reference the new auditing-github-actions skill instead of containing the logic itself.
- **Dependencies:** T0.1 (Blueprint approved)
- **Estimate:** L (4-6 hours)
- **Satisfies AC:** AC-FR-8-a, AC-FR-8-c (per-bound-agent update — see T4.x), AC-FR-8-f
- **L1 verification:** Directory exists; SKILL.md parses; ADR-0031 frontmatter check passes (auditing-X pattern compliance)
- **L2 verification:** Existing design-cicd agent invocations still work; old code paths in KB-github-actions-platform either removed or marked deprecated with migration breadcrumb
- **L3 verification:** Run a full design-cicd invocation in a test pipeline; verify it discovers the audit logic in the new location

#### T2.2: Stub `auditing-codespaces` skill

- **Layer:** cc
- **Description:** Per AC-FR-8-b. Create `.claude/skills/auditing-codespaces/` with SKILL.md describing the future audit functionality. Scripts/ directory contains only the stub `audit_codespaces.py` from T1.6 (or a reference to it if T1.6 placed it in auditing-shared instead). The stub clearly surfaces "stub state" per ADR-0033 + Q-CC-4 discipline.
- **Dependencies:** T1.6
- **Estimate:** S (1-2 hours)
- **Satisfies AC:** AC-FR-8-b, Q-CC-4, ADR-0033 stub-distinction discipline
- **L1 verification:** Directory exists; SKILL.md parses; frontmatter `stub: true` (or equivalent stub marker per ADR-0033) present
- **L2 verification:** Skill loads without error in a test agent invocation
- **L3 verification:** Integrated into a phase-quality-reviewer invocation; verify the stub envelope surfaces per ADR-0033

#### T2.3: Install `ai-development-guide` skill

- **Layer:** cc
- **Description:** Per AC-FR-9 (full text + AC-FR-9-e sequencing). Create `.claude/skills/ai-development-guide/SKILL.md` with the 4-phase pattern (lint → build → test → final gate). This skill is bound by `execute-task-code-producer` and `execute-task-quality-handler` agents per Blueprint § Agent Frontmatter Specifications.
- **Dependencies:** T0.1
- **Estimate:** L (4-6 hours — non-trivial skill content)
- **Satisfies AC:** AC-FR-9-a, AC-FR-9-b, AC-FR-9-c, AC-FR-9-d, AC-FR-9-e
- **L1 verification:** SKILL.md exists at canonical path; frontmatter parses; describes 4-phase pattern
- **L2 verification:** Skill loads in a test agent invocation; the 4-phase pattern is invocable by an agent (via prompt structure inspection)
- **L3 verification:** Bound by execute-task-code-producer in a simulation; verify the agent's behavior conforms to the 4-phase pattern

### Phase 2 Exit Criteria

- 3 skills present at canonical paths
- All 3 skills' frontmatter passes T1.1 (frontmatter validator)
- AC-FR-9-e sequencing requirement met (skill files exist; agents can bind in Phase 3)

## Phase 3 — Execution-phase agent authoring

### Goal

Author the 5 new agent files per Blueprint § Agent Frontmatter Specifications. Each agent file contains canonical YAML frontmatter + agent body (system prompt). All 5 agent files placed at `.claude/agents/execute-*.md`.

### Tasks

#### T3.1: Author `.claude/agents/execute-orchestrator.md`

- **Layer:** cc
- **Description:** Per Blueprint § Agent Frontmatter Specifications + Component 1 description. Frontmatter: model: opus, effort: high, tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate], skills: [KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines], memory: project. Body: 12-state machine spec, hook invocation per D-16, cycle counter management per D-12.
- **Dependencies:** T2.1, T2.2, T2.3 (all bound skills exist) — only T2.3 is strictly required for this agent's bindings, but all 3 should land before Phase 3 for clean staging
- **Estimate:** L (5-8 hours; the body content is substantial — 12-state machine + cycle counters + hook invocations)
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-FR-1-c (sub-agent inventory + 12-state machine), FR-1 substrate
- **L1 verification:** File exists; frontmatter parses; T1.1 frontmatter validator passes
- **L2 verification:** Agent loads in a test Claude Code session; `/agents` lists it; agent's tools and skills are visible
- **L3 verification:** Spawn the agent with a synthetic tasks.json; verify it walks the 12-state machine; verify state-transitions.log entries accumulate correctly

#### T3.2: Author `.claude/agents/execute-task-code-producer.md`

- **Layer:** cc
- **Description:** Per Blueprint § Agent Frontmatter Specifications + Component 2 description. Frontmatter: model: sonnet, effort: medium, tools: [Read, Glob, Grep, Write, Edit, Bash], skills: [ai-development-guide, KB-cc-design], NO memory field (per Gate 4 verified correction). Body: task-spec consumption pattern, 4-phase apply, scope-deviation surfacing per ADR-0033.
- **Dependencies:** T2.3 (ai-development-guide must exist before binding per AC-FR-9-e)
- **Estimate:** M (3-5 hours)
- **Satisfies AC:** AC-FR-2-a, AC-FR-2-b, AC-FR-2-c, AC-FR-2-f, AC-FR-9-a
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes; ai-development-guide present in skills field per AC-FR-9-c
- **L2 verification:** Agent loads; ai-development-guide skill content injects into context
- **L3 verification:** Spawn the agent with a sample task spec; verify it produces a task-execution-result.json conforming to the schema in Blueprint Contract definitions

#### T3.3: Author `.claude/agents/execute-task-quality-handler.md`

- **Layer:** cc
- **Description:** Per Blueprint § Agent Frontmatter Specifications + Component 3 description. Frontmatter: model: sonnet, effort: medium, tools: [Read, Glob, Grep, Bash(python3:*)], skills: [ai-development-guide, KB-cc-design, auditing-shared], NO memory field. Body: 4-phase verification, detect_stubs.py invocation (BLOCKING per D-2a), APPROVED status enum per D-2c, STUB_DETECTED distinct per D-2d.
- **Dependencies:** T2.3, T1.3 (ai-development-guide + detect_stubs.py both must exist)
- **Estimate:** M (3-5 hours)
- **Satisfies AC:** AC-FR-2-c, AC-FR-2-d, AC-FR-2-e, AC-FR-9-a
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes
- **L2 verification:** Agent loads; detect_stubs.py invokable from the agent's Bash tool
- **L3 verification:** Spawn the agent with a code-producer's output; verify it produces a quality-check-result.json with the correct status enum per D-2c

#### T3.4: Author `.claude/agents/execute-phase-quality-reviewer.md`

- **Layer:** cc
- **Description:** Per Blueprint § Agent Frontmatter Specifications + Component 4 description. Frontmatter: model: opus, effort: high, tools: [Read, Glob, Grep, Bash(python3:*), Write], skills: [KB-cc-design, KB-review-disciplines, auditing-shared], NO memory field. Body: D-13 dimensional verdict structure (5 dimensions including scope-deviations), run_phase_checks.py invocation, audit-counter delta per FR-12 + Q-CC-3.
- **Dependencies:** T1.4 (run_phase_checks.py must exist)
- **Estimate:** L (5-7 hours; the dimensional verdict logic + audit-counter delta is substantial)
- **Satisfies AC:** AC-FR-3-a, AC-FR-3-b, AC-FR-3-c, AC-FR-3-d, AC-FR-12-a, AC-FR-12-b, Q-CC-3
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes
- **L2 verification:** Agent loads; can invoke run_phase_checks.py
- **L3 verification:** Spawn the agent on a phase with mixed findings; verify the phase-quality-report.{json,md} pair conforms to D-13 dimensional verdict + FR-12 audit-counter delta schemas

#### T3.5: Author `.claude/agents/execute-finalize-reconciler.md`

- **Layer:** cc
- **Description:** Per Blueprint § Agent Frontmatter Specifications + Component 5 description. Frontmatter: model: opus, effort: high, tools: [Read, Glob, Grep, Write, Agent], skills: [KB-cc-design, KB-review-disciplines, auditing-shared], memory: project. Body: 8-row dispatch matrix (D-14 6-row base + 2 additions), 4-cycle cap enforcement per D-12 / ADR-0017, scope-bounded dispatch discipline per Blueprint Contract 4.
- **Dependencies:** none from Phase 3 (parallelizable with T3.1-T3.4)
- **Estimate:** L (5-7 hours; the dispatch matrix logic is substantial)
- **Satisfies AC:** AC-FR-4-a, AC-FR-4-b, AC-FR-4-c, AC-FR-4-d, AC-FR-10-a, AC-FR-10-b, AC-FR-10-c
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes
- **L2 verification:** Agent loads
- **L3 verification:** Spawn the agent with a phase-quality-report containing dispatchable findings; verify it routes correctly per the 8-row matrix; verify cycle counter increments correctly across multiple invocations

### Phase 3 Exit Criteria

- 5 agent files at canonical paths
- All 5 pass T1.1 frontmatter validator
- All 5 visible in `/agents` listing
- All 5 can be spawned without binding errors

## Phase 4 — Existing-agent extensions + convention updates

### Goal

Extend `shared-document-reviewer` to the new doc_type taxonomy per ADR-0032; update shared-conventions.md with the 5 coordinated changes per ADR-0032; update any agents whose `skills:` should change per AC-FR-8-f.

### Tasks

#### T4.1: Update `shared-conventions.md` per ADR-0032

- **Layer:** cc
- **Description:** Apply the 5 coordinated changes from ADR-0032 to `.claude/skills/KB-documentation-criteria/references/shared-conventions.md`: (1) universal frontmatter field additions; (2) user-token chain pattern formalization; (3) per-doc-type state vocabulary (3-tier: gated 5-state / analysis-log 3-state / ADR 4-state); (4) `doc_type` field as required universal with 20+5 value enum; (5) execution-phase artifact frontmatter section.
- **Dependencies:** T0.2 (ADR-0032 accepted)
- **Estimate:** L (4-6 hours; substantive doc edit + ADR-0005 append-only discipline)
- **Satisfies AC:** ADR-0032 implementation; AC-FR-11-a, AC-FR-11-b (canonical state vocabulary substrate)
- **L1 verification:** File parses; all 5 changes present (grep for each)
- **L2 verification:** Run T1.1 frontmatter validator with new schemas against existing artifacts; verify reasonable findings
- **L3 verification:** Re-run shared-document-reviewer on a sample of existing artifacts; verify per-doc-type vocabulary correctly dispatched

#### T4.2: Extend `shared-document-reviewer.md` agent body

- **Layer:** cc
- **Description:** Update the agent's body to dispatch on `doc_type` (per ADR-0032) and add review logic for the 5 new execution-phase artifact types: per-task-execution-result, phase-quality-report, quality-reconciliation-log, state-transitions-log, pipeline-run-summary. Frontmatter unchanged (skills + tools stay the same per ADR-0005 append-only — only body content evolves).
- **Dependencies:** T4.1 (shared-conventions updated)
- **Estimate:** M (3-4 hours)
- **Satisfies AC:** AC-FR-6-d (shared-document-reviewer recognizes new artifact types), D-9 second role substrate
- **L1 verification:** File parses; agent loads
- **L2 verification:** Agent runs against a sample per-task-execution-result; correctly applies the new vocabulary
- **L3 verification:** Full pipeline test — agent is invoked at every gate; verify dispatch logic correct across all 5 new doc_types

#### T4.3: Update `design-cicd` agent's skills binding per AC-FR-8-f

- **Layer:** cc
- **Description:** Per AC-FR-8-f. The `design-cicd` agent currently binds `KB-github-actions-platform`; with the audit logic extracted in T2.1, it must additionally (or instead) bind `auditing-github-actions`. Decision: ADDITIONALLY bind (preserves backward compatibility; the agent loads both KBs).
- **Dependencies:** T2.1
- **Estimate:** XS
- **Satisfies AC:** AC-FR-8-f
- **L1 verification:** Frontmatter updated; T1.1 validator passes
- **L2 verification:** Agent loads with both skills
- **L3 verification:** Run design-cicd in a test feature; verify it has access to the audit logic in the new location

#### T4.4: Update `design-codespaces` agent's skills binding per AC-FR-8-f

- **Layer:** cc
- **Description:** Per AC-FR-8-f. Same as T4.3 but for design-codespaces (binds auditing-codespaces stub now).
- **Dependencies:** T2.2
- **Estimate:** XS
- **Satisfies AC:** AC-FR-8-f
- **L1 verification:** Frontmatter updated; T1.1 validator passes
- **L2 verification:** Agent loads
- **L3 verification:** N/A (auditing-codespaces is a stub; surface deferral per ADR-0033)

### Phase 4 Exit Criteria

- shared-conventions.md reflects all 5 ADR-0032 changes
- shared-document-reviewer handles new doc_types
- design-cicd, design-codespaces have updated skill bindings

## Phase 5 — Template authoring for new artifact types

### Goal

Author canonical templates for the 5 new execution-phase artifact types per AC-FR-7-c floor coverage. The Path B disposition (per Blueprint § AC-FR-7 floor coverage) maps the 7 named items to 5 templates + 2 schema equivalences (frontmatter-validator output = script-output schema; execution-reconciliation log = pipeline-run-summary equivalence).

### Tasks

#### T5.1: Author template for `per-task-execution-result`

- **Layer:** cc
- **Description:** New template at `.claude/skills/KB-documentation-criteria/references/templates/execution-phase/per-task-execution-result-template.md`. Schema per Blueprint Contract definitions (5b State Transitions section).
- **Dependencies:** T0.3, T4.1
- **Estimate:** S (1-2 hours)
- **Satisfies AC:** AC-FR-7-a, AC-FR-7-c (floor item 1 of 5)
- **L1 verification:** File exists; frontmatter parses
- **L2 verification:** Frontmatter validator (T1.1) recognizes the new template-derived doc_type
- **L3 verification:** Sample per-task-execution-result instance authored from template; review-cross-artifact-auditor passes it

#### T5.2: Author template for `phase-quality-report` ({json + md} pair)

- **Layer:** cc
- **Description:** New templates at `…/execution-phase/phase-quality-report-template.{json,md}`. JSON schema per D-13 dimensional verdict + FR-12 audit-counter delta. MD narrative companion.
- **Dependencies:** T0.3, T4.1
- **Estimate:** M (2-3 hours)
- **Satisfies AC:** AC-FR-7-b (D-5 pair pattern), AC-FR-7-c (floor item 2 of 5), AC-FR-3-* substrate
- **L1 verification:** Both files exist; both parse
- **L2 verification:** A sample phase-quality-report (json + md) authored from templates conforms to schema
- **L3 verification:** Integrated into execute-phase-quality-reviewer (T3.4); the agent produces conforming output

#### T5.3: Author template for `quality-reconciliation-log` ({json + md} pair)

- **Layer:** cc
- **Description:** New templates at `…/execution-phase/quality-reconciliation-log-template.{json,md}`. Schema includes cycle-by-cycle dispatch records per D-14 + cap-status per D-12. JSONL machine-parseable per FR-13.
- **Dependencies:** T0.3, T4.1
- **Estimate:** M (2-3 hours)
- **Satisfies AC:** AC-FR-7-c (floor item 3 of 5), AC-FR-4-a (substrate), FR-13
- **L1 verification:** Files exist; parse
- **L2 verification:** Sample log conforms; JSONL machine-parseable check passes
- **L3 verification:** Integrated into execute-finalize-reconciler (T3.5)

#### T5.4: Author template for `state-transitions-log` (JSONL)

- **Layer:** cc
- **Description:** Template at `…/execution-phase/state-transitions-log-template.jsonl`. Each line: `{transition_id, from_state, to_state, trigger, timestamp, payload}` per FR-5 + D-16.
- **Dependencies:** T0.3, T4.1
- **Estimate:** S (1-2 hours)
- **Satisfies AC:** AC-FR-5-a, AC-FR-5-b, AC-FR-7-c (floor item 4 of 5)
- **L1 verification:** Template parses as valid JSONL
- **L2 verification:** Sample log from T1.2 log_state_transition.py conforms
- **L3 verification:** End-to-end pipeline run (T6.x) produces conforming output

#### T5.5: Author template for `pipeline-run-summary`

- **Layer:** cc
- **Description:** Template at `…/execution-phase/pipeline-run-summary-template.json`. Schema includes: run_id, feature_slug, start/end timestamps, per-phase verdicts, aggregate audit-counter delta, final disposition. Note: per Blueprint § AC-FR-7 floor coverage Path B disposition, this also satisfies the "execution-reconciliation log" floor item via run-level equivalence.
- **Dependencies:** T0.3, T4.1
- **Estimate:** S (1-2 hours)
- **Satisfies AC:** AC-FR-7-c (floor item 5 of 5), Blueprint § AC-FR-7 floor disposition (run-level = execution-reconciliation equivalence)
- **L1 verification:** Template exists; parses
- **L2 verification:** Sample summary from execute-orchestrator simulation conforms
- **L3 verification:** End-to-end pipeline run produces conforming output

### Phase 5 Exit Criteria

- 5 templates (covering 7 named items via Path B disposition) at canonical paths
- All templates parse and pass T1.1 frontmatter validator
- shared-document-reviewer (post T4.2) recognizes all 5 new doc_types

## Phase 6 — End-to-end pipeline smoke test

### Goal

Run a synthetic mini-pipeline end-to-end exercising all 5 new agents + the auditing-shared script cluster + the new templates. Verifies the integration substrate works.

### Tasks

#### T6.1: Author synthetic test feature scaffolding

- **Layer:** cc
- **Description:** Create a minimal test feature at `working/feature/_smoke_test_feature/` with a stub PRD + Blueprint + plan + tasks.json + acceptance tests + phase validators. Used only for the smoke test. Mark with `status: scaffolding` per ADR-0032 (or analogous marker) so reviewers don't treat it as a real feature.
- **Dependencies:** T0.1 (Blueprint approved) — Phase 6 runs after Phase 5 in practice but the scaffolding can be staged earlier
- **Estimate:** M (3-4 hours)
- **Satisfies AC:** Verification substrate for AC-FR-1 through AC-FR-13 collectively
- **L1 verification:** Scaffolding exists; all required artifacts present
- **L2 verification:** Each scaffolding artifact passes T1.1
- **L3 verification:** N/A (Phase 6 itself is the L3 for this)

#### T6.2: Run smoke test: invoke `execute-orchestrator` against the test scaffolding

- **Layer:** cc
- **Description:** Spawn execute-orchestrator with the test feature's tasks.json + acceptance tests + phase validators. Let it run end-to-end. Capture the state-transitions.log + final pipeline-run-summary.json.
- **Dependencies:** T3.1, T3.2, T3.3, T3.4, T3.5, T1.* (all), T2.* (all), T4.*, T5.*, T6.1
- **Estimate:** M (2-3 hours)
- **Satisfies AC:** AC-FR-1-d (12-state machine end-to-end), AC-FR-13-a (machine-parseable log), Blueprint Contract 5 substrate
- **L1 verification:** Pipeline runs without errors; final pipeline-run-summary.json emitted
- **L2 verification:** state-transitions.log has expected transitions; per-task-execution-result + phase-quality-report + quality-reconciliation-log artifacts all created at expected paths
- **L3 verification:** Re-run shared-document-reviewer + a fresh execute-phase-quality-reviewer on the output; verify all artifacts conform to schemas and a deterministic re-execution produces the same logs

### Phase 6 Exit Criteria

- Smoke test passes T6.2 L1/L2/L3
- The 5 new agents are demonstrably functional in an end-to-end run
- No regression in pre-existing planning-side agents (verified by re-running a known-good planning-side smoke test if available)

---

## Cross-Phase Dependencies

```
Phase 0 (Setup)
    │
    ├──► Phase 1 (auditing-shared scripts)
    │       │
    │       └──► T1.3 ──┐
    │       └──► T1.4 ──┤
    │       └──► T1.6 ──┤
    │                    │
    └──► Phase 2 (Skills)
            ├──► T2.1 ──────────┐
            ├──► T2.2 (←T1.6) ──┤
            └──► T2.3 ──────────┤
                                │
                          Phase 3 (Agents)
                            ├──► T3.1 (needs T2.1, T2.2, T2.3)
                            ├──► T3.2 (needs T2.3)
                            ├──► T3.3 (needs T2.3, T1.3)
                            ├──► T3.4 (needs T1.4)
                            └──► T3.5 (parallel)
                                            │
                                      Phase 4 (Extensions + conventions)
                                        ├──► T4.1 (needs T0.2)
                                        ├──► T4.2 (needs T4.1)
                                        ├──► T4.3 (needs T2.1)
                                        └──► T4.4 (needs T2.2)
                                                            │
                                                      Phase 5 (Templates)
                                                        ├──► T5.1, T5.2, T5.3, T5.4, T5.5 (all need T0.3 + T4.1)
                                                                                          │
                                                                                    Phase 6 (Smoke test)
                                                                                      ├──► T6.1 (parallel-able with phases 1-5)
                                                                                      └──► T6.2 (needs all preceding)
```

**Parallelism analysis**: Phases 1 + 2 can largely overlap (Phase 1 doesn't strictly depend on Phase 2's skills; Phase 2 depends on T1.6 only). Phase 3 is mostly parallel internally (T3.1-T3.5 can run concurrently once their skill+script dependencies land). Phase 5 (templates) is fully parallelizable internally. Phase 4 is sequential within itself (T4.1 → T4.2; T4.3 and T4.4 parallel).

**Critical path**: T0.1 → T0.2 → T1.4 → T3.4 → T6.2 (Blueprint approval → ADR acceptance → run_phase_checks.py → phase-quality-reviewer → smoke test). Estimated: ~3-4 days serial; ~2 days with full parallelism.

## L1/L2/L3 Verification Discipline

Every task above carries three verification criteria:

- **L1 — Lowest-cost check**: file existence, frontmatter parse, --help prints. Catches "did the task happen at all" failures. Runs in seconds.
- **L2 — Functional check**: unit test, smoke test, isolated invocation. Catches "did the task implement the intended behavior in isolation" failures. Runs in minutes.
- **L3 — Integration / acceptance check**: full pipeline run, cross-component invocation, real-data validation. Catches "did the task integrate correctly with neighbors" failures. Runs in 10+ minutes.

Execution-phase agents enforce L1 + L2 per task (via `execute-task-quality-handler`). L3 enforcement is phase-level (via `execute-phase-quality-reviewer` + `execute-finalize-reconciler`).

## Acceptance Test Cross-Reference

| PRD Functional AC | Plan Task(s) primary | Notes |
|---|---|---|
| AC-FR-1-a/b/c/d (sub-agent inventory + 12-state machine + end-to-end) | T3.1, T6.2 | orchestrator agent + smoke test |
| AC-FR-2-a/b/c/d/e/f (per-task loop + status + stub + scope-deviations) | T3.2, T3.3, T1.3 | code-producer + quality-handler + detect_stubs.py |
| AC-FR-3-a/b/c/d (phase-quality stage + 3 layers + coordinator + discipline-check) | T3.4, T1.4, T1.5 | phase-quality-reviewer + run_phase_checks.py + check_pipeline_discipline.py |
| AC-FR-4-a/b/c/d (depth classifier + dispatch matrix + cascade) | T3.5 | execute-finalize-reconciler |
| AC-FR-5-a/b/c/d/e (state-transition hooks) | T1.2, T3.1 | log_state_transition.py + orchestrator |
| AC-FR-6-a/b/c/d (frontmatter validator + shared-document-reviewer) | T1.1, T4.2 | validator script + extended reviewer |
| AC-FR-7-a/b/c (schemas + templates + floor coverage) | T5.1–T5.5 | 5 templates (Path B disposition) |
| AC-FR-8-a/b/c/d/e/f (auditing-X three-way split) | T2.1, T2.2, T4.3, T4.4 | skill extract + stub + binding updates |
| AC-FR-9-a/b/c/d/e (ai-development-guide skill binding + validator check + sequencing) | T2.3, T3.2, T3.3, T1.1 | skill install + agent bindings + validator |
| AC-FR-10-a/b/c (4-cycle cap + symmetric + escalation) | T3.5, T3.1 | reconciler + orchestrator (cap enforcement) |
| AC-FR-11-a/b (canonical state vocabulary) | T4.1, ADR-0032 | shared-conventions update |
| AC-FR-12-a/b (audit-counter delta in phase-quality-report) | T3.4, T5.2 | phase-quality-reviewer + template |
| AC-FR-13-a (machine-parseable reconciliation log) | T5.3, T1.7 | template + auditing-shared smoke test |

**Coverage check**: every PRD Functional AC has at least one Plan task. No silent drops.

## Estimation Methodology

T-shirt sizing:
- XS: < 1 hour
- S: 1-2 hours
- M: 2-4 hours
- L: 4-8 hours

These are per-task estimates assuming familiarity with the codebase. Total project: ~120-160 hours of focused implementation work serial; ~70-90 hours with full parallelization (limited by critical path: T0.1 → T0.2 → T1.4 → T3.4 → T6.2).

## Resourcing Posture

This Plan assumes Josh executes via Claude Code with the 5 new execution-phase agents. Single-developer pipeline; agents handle execution; Josh reviews at gates. No team parallelization assumed.

If Josh later wants to run multiple `execute-task-code-producer` invocations in parallel (e.g., T3.1 + T3.5 concurrently via two separate Claude Code sessions or via background subagents per the [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents#run-subagents-in-foreground-or-background)), the Plan supports it — Phase 3 tasks are mostly parallelizable.

## Open Items (Pending Cross-Artifact Audit)

1. **L3 verification of state-transition hooks (T1.2 + T3.1)** requires a full pipeline run to validate. Until T6.2 lands, T1.2's L3 verification is technically pending. Acceptable: most tasks have similar L3-on-smoke-test dependency.

2. **Q-CC-1 opus-escalation hook**: cc-design defers the model upgrade for execute-task-quality-handler to "follow-on feature if operational evidence justifies." This Plan does NOT include an opus-escalation task; the substrate (the agent at sonnet/medium) is what ships. If Josh observes classification errors in early use, a follow-on PRD amendment can revise T3.3.

3. **Phase 0 → Phase 1 sequencing**: T0.4 (script placeholders) creates files that Phase 1 tasks populate. This means the placeholder files have temporary "empty" state during Phase 0. Acceptable per ADR-0033 (the placeholder state is surfaced; not silent). If a more rigorous "skip placeholders" approach is preferred, drop T0.4 and let each Phase 1 task create its own file.

4. **Phase 4 (`T4.1` shared-conventions update) interaction with downstream**: Updating shared-conventions.md mid-feature means existing artifacts (the Blueprint, PRD, etc.) may begin to fail the new validation. The new schemas should be backward-compatible (additive only per ADR-0032). Cross-Artifact Audit at Gate 5/6 will verify.

5. **Cycle 3+ reconciliation budget consumed**: Two reconciliation cycles were used during the Architecture Audit stage (cycles 1 + 2). The remaining 2-cycle budget is reserved for Plan-stage / Cross-Artifact-Audit reconciliation if needed. Out of caution: if cross-artifact audit surfaces > 2 cycles of findings, surface for user decision per ADR-0017 + ADR-0033 cap-exhaustion discipline.

## Update History

This document follows ADR-0005 append-only supersession discipline. Initial version:

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-22 | claude (acting as plan-author; claude.ai simulation) | Initial Plan authoring. 28 tasks across 7 phases (Phase 0 Setup → Phase 6 End-to-end smoke test). All 13 PRD Functional ACs cross-referenced to at least one Plan task. L1/L2/L3 verification discipline applied per KB-documentation-criteria plan-authoring discipline. Honors Blueprint v4.0.0 (post-Gate-4 platform-validity verified) including the Agent Frontmatter Specifications subsection. Open items list flags 5 cross-artifact concerns for Gate 5 reviewer attention. **Claude.ai simulation caveat**: task-level detail may benefit from refinement by an authoritative Claude Code plan-author re-invocation; treat task descriptions as a structurally-correct starting point. |
