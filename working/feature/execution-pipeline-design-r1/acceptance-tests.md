---
id: AcceptanceTests-execution-pipeline-design-r1
version: 1.0.0
status: draft
feature_slug: execution-pipeline-design-r1
doc_type: acceptance-tests
derived_from:
  - working/feature/execution-pipeline-design-r1/prd-v1.1.0.md
  - working/feature/execution-pipeline-design-r1/blueprint-v5.md
  - working/feature/execution-pipeline-design-r1/plan-v2.md
generated: 2026-05-22T23:50:00Z
generated_by: test-acceptance-author (Claude Code subagent dispatch, authoritative)
agent_invocation_simulation: false
agent_invocation_note: |
  FIRST authoritative test-acceptance-author dispatch for this feature. Runs in parallel
  with test-phase-validator-author. Maps every PRD AC (60) + Blueprint operational AC (3)
  to concrete test specifications. v5-introduced items (I-AA-602 through I-AA-609) get
  dedicated test coverage in addition to standard AC coverage.
upstream_references:
  - PRD: prd-v1.1.0.md (gate_passed=2; 13 FRs / 60 ACs)
  - Blueprint: blueprint-v5.md (audit-r7 verdict=pass; +3 operational ACs)
  - Plan: plan-v2.md (Gate 5 approved; 31 tasks across 7 phases)
adrs_honored:
  - ADR-0017 (4-cycle reconciliation cap — canonical home; cited for AC-FR-6-e and AC-FR-10-b per ADR-0034)
  - ADR-0029 (no-silent-scope-changes; tests do not absorb scope silently — Open Items section surfaces judgment calls)
  - ADR-0032 (doc_type universal-required field; this artifact declares `doc_type: acceptance-tests`)
  - ADR-0033 (execution-phase Scope-Deviation surfacing; tests verify §Context bidirectional cross-reference)
  - ADR-0034 (PRD mis-credit cleanup; AC-FR-6-e + AC-FR-10-b tests cite ADR-0017 forward, NOT ADR-0021)
  - ADR-0035 (auditing-shared Skill-binding convention; tests verify 4 of 5 execute-* agents bind; 1 does not)
---

# Acceptance Tests: Execution Pipeline Design (r1)

## Contents

- [Purpose](#purpose)
- [Source Artifacts](#source-artifacts)
- [Coverage Matrix](#coverage-matrix)
- [Test Suite Overview](#test-suite-overview)
- [Test Specifications by FR](#test-specifications-by-fr)
  - [FR-1 Tests](#fr-1-tests-explicit-execution-pipeline-stages)
  - [FR-2 Tests](#fr-2-tests-per-task-execution-and-quality-inner-loop)
  - [FR-3 Tests](#fr-3-tests-phase-level-quality-stage)
  - [FR-4 Tests](#fr-4-tests-quality-finding-depth-classifier-and-dispatch-matrix)
  - [FR-5 Tests](#fr-5-tests-state-transition-hooks)
  - [FR-6 Tests](#fr-6-tests-frontmatter-validator)
  - [FR-7 Tests](#fr-7-tests-execution-phase-artifact-schemas-and-templates)
  - [FR-8 Tests](#fr-8-tests-three-way-auditing-split)
  - [FR-9 Tests](#fr-9-tests-ai-development-guide-skill-binding-and-sequencing)
  - [FR-10 Tests](#fr-10-tests-execution-side-reconciliation-budget)
  - [FR-11 Tests](#fr-11-tests-canonical-state-vocabulary)
  - [FR-12 Tests](#fr-12-tests-phase-quality-report-audit-counter-delta)
  - [FR-13 Tests](#fr-13-tests-reconciliation-log-machine-parseable)
- [Operational AC Tests](#operational-ac-tests)
- [v5-Introduced Items: Dedicated Tests](#v5-introduced-items-dedicated-tests)
- [Test Infrastructure Required](#test-infrastructure-required)
- [CI Execution Plan](#ci-execution-plan)
- [Determinism and Isolation Commitments](#determinism-and-isolation-commitments)
- [Open Items (for Cross-Artifact Audit)](#open-items-for-cross-artifact-audit)
- [Update History](#update-history)

## Purpose

This document specifies one or more concrete tests for every Acceptance Criterion (AC) in the upstream PRD (60 ACs) and Blueprint (3 operational ACs), totaling **63 ACs**. Each test is layered at the lowest verification level that genuinely covers the AC's intent (test pyramid: structural / unit-script / integration / E2E). All tests verify the design artifacts and substrate produced by the Plan; this feature ships design artifacts only, so test types skew toward structural-validation, config-validation, and contract-conformance rather than runtime E2E. The single end-to-end smoke test (AT-EXX) exercises the integration substrate.

This document is the input to:
- `finalize-task-decomposer` (decomposes each test into a test-implementation task)
- `review-cross-artifact-auditor` (checks Blueprint ↔ Plan ↔ Acceptance Tests ↔ Phase Validators alignment)

Per ADR-0034 and Blueprint v5 §AC-FR-6-e / §AC-FR-10-b correction-surface footnotes, tests for those ACs cite **ADR-0017** as the canonical home for the 4-cycle reconciliation cap — NOT ADR-0021. The PRD's verbatim ADR-0021 reference is preserved as a transcription artifact in the PRD but is corrected forward in this acceptance-tests artifact.

## Source Artifacts

| Source | Path | Version | Role |
|---|---|---|---|
| PRD | `working/feature/execution-pipeline-design-r1/prd-v1.1.0.md` | 1.1.0 (gate_passed=2) | 13 FRs / 60 functional ACs |
| Blueprint | `working/feature/execution-pipeline-design-r1/blueprint-v5.md` | 5.0.0 (audit-r7=pass) | Per-layer ACs + 3 operational ACs |
| Plan | `working/feature/execution-pipeline-design-r1/plan-v2.md` | 2.0.0 (Gate 5 approved) | 31 tasks / 7 phases; AC traceability matrix |
| Architecture Audit | `working/feature/execution-pipeline-design-r1/architecture-audit-issues-r7.json` | r7 | Pass verdict (3 RECOMMENDED non-blocking) |
| Plan Review Report | `working/feature/execution-pipeline-design-r1/plan-v2-review-report.md` | n/a | Gate 5 approval; 1 MINOR fixed in-place |
| Synthesis | `working/feature/execution-pipeline-design-r1/synthesis.md` | 1.1.0 | D-1..D-18 decisions referenced by tests |

## Coverage Matrix

Every AC has ≥1 test. Total tests: **78** mapped across **63 ACs**.

### Functional ACs (FR-1 through FR-13)

| AC | EARS Form | Test ID(s) | Plan Task(s) |
|---|---|---|---|
| AC-FR-1-a | Ubiquitous | AT-001 | T3.1 |
| AC-FR-1-b | Ubiquitous | AT-002 | T3.1, T5.* |
| AC-FR-1-c | When | AT-003 | T3.1 |
| AC-FR-1-d | When | AT-004 | T3.1, T6.2 |
| AC-FR-2-a | When | AT-005 | T3.1, T3.2 |
| AC-FR-2-b | When | AT-006 | T3.1, T3.3 |
| AC-FR-2-c | When | AT-007 | T3.1, T3.3 |
| AC-FR-2-d | When | AT-008 | T3.1, T3.3, T1.3 |
| AC-FR-2-e | When | AT-009 | T3.1, T3.3 |
| AC-FR-2-f | When | AT-010 | T3.1, T3.2 |
| AC-FR-3-a | When | AT-011 | T3.1, T3.4 |
| AC-FR-3-b | Ubiquitous | AT-012, AT-013 | T1.4, T3.4 |
| AC-FR-3-c | Ubiquitous | AT-014 | T3.4, T5.2 |
| AC-FR-3-d | When | AT-015 | T3.4, T3.5 |
| AC-FR-3-e | When | AT-016 | T3.1, T3.4 |
| AC-FR-3-f | Where | AT-017 | T1.4, T3.4 |
| AC-FR-4-a | Ubiquitous | AT-018 | T3.5 |
| AC-FR-4-b | Ubiquitous | AT-019 | T3.5 |
| AC-FR-4-c | Ubiquitous | AT-020 | T3.5 |
| AC-FR-4-d | When | AT-021 | T3.5 |
| AC-FR-4-e | Ubiquitous | AT-022 | Blueprint structural |
| AC-FR-4-f | Ubiquitous | AT-023 | T0.2 (ADRs) |
| AC-FR-5-a | When | AT-024 | T1.2, T3.1 |
| AC-FR-5-b | When | AT-025 | T1.2, T3.1 |
| AC-FR-5-c | When | AT-026 | T1.2, T3.1 |
| AC-FR-5-d | Ubiquitous | AT-027 | T1.2, T6.2 |
| AC-FR-5-e | If-Then | AT-028 | T1.2, T3.1 |
| AC-FR-6-a | Ubiquitous | AT-029 | T1.1 |
| AC-FR-6-b | Ubiquitous | AT-030, AT-031 | T1.1, T4.1 |
| AC-FR-6-c | When | AT-032 | T1.1 |
| AC-FR-6-d | Ubiquitous | AT-033 | T1.1, T3.4 |
| AC-FR-6-e | Ubiquitous | AT-034 | T3.5 (cites ADR-0017 per ADR-0034) |
| AC-FR-7-a | Ubiquitous | AT-035 | T5.1, T5.2, T5.3, T5.4, T5.5 |
| AC-FR-7-b | Ubiquitous | AT-036 | T4.1 |
| AC-FR-7-c | Ubiquitous | AT-037 | T5.* |
| AC-FR-7-d | Where | AT-038 | T5.4, T5.5 |
| AC-FR-8-a | Ubiquitous | AT-039 | T2.1 |
| AC-FR-8-b | Where | AT-040 | T2.2, T1.6 |
| AC-FR-8-c | Ubiquitous | AT-041 | T2.1, T2.2, structural |
| AC-FR-8-d | When | AT-042 | T4.3, T4.4 |
| AC-FR-8-e | Ubiquitous | AT-043 | T2.1 |
| AC-FR-8-f | Where | AT-044 | T4.3, T4.4 |
| AC-FR-9-a | Ubiquitous | AT-045 | T3.2, T3.3 |
| AC-FR-9-b | Ubiquitous | AT-046 | Blueprint structural |
| AC-FR-9-c | When | AT-047 | T1.1 |
| AC-FR-9-d | Ubiquitous | AT-048 | Blueprint structural |
| AC-FR-9-e | Ubiquitous | AT-049, AT-050 | T2.3 (with sequencing AT-050) |
| AC-FR-10-a | Ubiquitous | AT-051 | T0.2 (ADR-0017 canonical per ADR-0034) |
| AC-FR-10-b | Ubiquitous | AT-052 | T3.5 (cites ADR-0017 per ADR-0034) |
| AC-FR-10-c | When | AT-053 | T3.5, T3.1 |
| AC-FR-10-d | Ubiquitous | AT-054 | T3.5 |
| AC-FR-11-a | Ubiquitous | AT-055 | T4.1 |
| AC-FR-11-b | Ubiquitous | AT-056 | T5.* |
| AC-FR-11-c | Ubiquitous | AT-057 | T1.1 |
| AC-FR-11-d | Where | AT-058 | T1.1 |
| AC-FR-11-e | Ubiquitous | AT-059 | T0.2 (ADR-0032) |
| AC-FR-12-a | When | AT-060 | T3.4, T5.2 |
| AC-FR-12-b | Ubiquitous | AT-061 | T3.4, T5.5 |
| AC-FR-13-a | Ubiquitous | AT-062 | T5.3 |
| AC-FR-13-b | Ubiquitous | AT-063 | T5.3 |

### Operational ACs (Blueprint-defined)

| AC | EARS Form | Test ID(s) | Plan Task(s) |
|---|---|---|---|
| AC-OP-1 | Ubiquitous | AT-064 | T6.2 |
| AC-OP-2 | Ubiquitous | AT-065 | T1.5, T1.1 |
| AC-OP-3 | Ubiquitous | AT-066 | T3.1, T5.5 |

### v5-Introduced Items (additional dedicated tests)

| Item | Description | Test ID(s) | Plan Task(s) |
|---|---|---|---|
| I-AA-602 | Bash widening — unrestricted on execute-task-quality-handler | AT-067, AT-068 | T3.3, T1.1 |
| I-AA-603 / ADR-0035 | auditing-shared Skill binding (4 of 5 agents bind; 1 does not) | AT-069, AT-070, AT-071 | T3.1, T3.2, T3.3, T3.4, T3.5 |
| I-AA-604 | AC correction-surface cites ADR-0017, NOT ADR-0021 | AT-072 | T3.5 (covers AC-FR-6-e + AC-FR-10-b) |
| I-AA-605 | doc_type backfill: Posture-A explicit surfacing in Plan | AT-073 | T6.1 (Posture A) |
| I-AA-606 | ADR-0033 §Context bidirectional cross-reference | AT-074, AT-075 | T5.4, T5.5 |
| I-AA-608 | orchestrator HAS Write tool | AT-076 | T3.1, T1.1 |
| I-AA-609 | T0/T13 boundary transitions in state machine (14 = 12 + 2) | AT-077, AT-078 | T3.1, T1.2 |

**Coverage assertion**: All 63 ACs (60 PRD + 3 Operational) are covered by ≥1 test. All 7 v5-introduced items have dedicated tests in addition to their AC-level coverage.

## Test Suite Overview

| Type | Count | Notes |
|---|---|---|
| Structural (file/path existence, frontmatter parses, AC field presence) | 28 | Lowest-cost; verifies design-artifact shape |
| Config validation (frontmatter schema, YAML enum, references resolve) | 19 | Verifies declarative correctness without execution |
| Contract conformance (script output schema, JSON shape) | 14 | Verifies inter-component contracts |
| Integration (multi-script / multi-agent interaction) | 8 | Verifies cross-boundary behavior |
| End-to-end smoke (full 14-transition orchestrator run) | 1 | Single integrated run per T6.2; verifies 9 ACs |
| Property-based (state-machine invariants) | 2 | Verifies invariants across all 14 transitions |
| Negative path (validator rejects bad input) | 6 | Verifies validator's discrimination |

**Layer of verification**: All tests run at the **Claude Code / Project Filesystem** layer (single-layer feature). No CI/CD, IaC, Backend, or Frontend layers are activated.

**Test pyramid posture**: This feature ships design-time substrate (agent files, skills, scripts, templates, ADRs, spec edits). The pyramid emphasizes structural and contract-level tests over E2E. The single E2E smoke test (T6.2 substrate verified by AT-066, AT-077, etc.) is sufficient because the agents are validators / orchestrators; their substantive correctness is verified by contract-level tests of their outputs.

## Test Specifications by FR

Every test specification follows AAA structure (Arrange / Act / Assert) and includes deterministic, assertable expected outcomes.

---

### FR-1 Tests: Explicit execution-pipeline stages

#### AT-001 — Blueprint defines an ordered sequence of execution-pipeline stages

- **Maps to AC**: AC-FR-1-a
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T3.1 (orchestrator state machine body)
- **Preconditions**: `blueprint-v5.md` is at `status: accepted` (post-T0.2 stage ratification — or `status: draft` if T0.2 has not yet stages ratification at the Plan/Test gate per ADR-0017 sequencing).
- **Steps**:
  1. Arrange: load `blueprint-v5.md`.
  2. Act: parse the §State Transitions and Invariants section; extract the ordered transition list T1 through T12 (substantive transitions; T0/T13 are boundary, verified in AT-077).
  3. Assert: section contains exactly 12 substantive transitions named T1..T12 in canonical order; each row has a non-empty `from_state`, `to_state`, and `trigger`.
- **Expected outcome**: Section present; 12 rows; no duplicates; ordering monotonic.
- **Negative-path coverage**: AT-077 (boundary T0/T13 present additionally).
- **Determinism notes**: Static document parse; fully deterministic.

#### AT-002 — Each execution-pipeline stage has name, owning sub-agent, gate, and named artifact

- **Maps to AC**: AC-FR-1-b
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T3.1, T5.* (templates name the artifacts)
- **Preconditions**: Blueprint and templates present.
- **Steps**:
  1. Load Blueprint §Architecture Overview and §Main Components.
  2. For each of the 5 execute-* agents enumerated, assert: agent has a unique name, a documented owning gate, and at least one named produced artifact (cross-referenced to a `*-template.md` in `KB-documentation-criteria/references/templates/`).
  3. Assert: `execute-orchestrator` owns no produced-artifact other than `state-transitions.log` and `pipeline-run-summary.json` (per Component 1 description).
- **Expected outcome**: All 5 agents pass the structural check; no agent is missing a gate or an artifact.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static document parse.

#### AT-003 — Orchestrator enters first execution stage when Task Decomposition completes

- **Maps to AC**: AC-FR-1-c
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1
- **Preconditions**: `execute-orchestrator.md` exists; `tasks.json` fixture is available.
- **Steps**:
  1. Arrange: stage a synthetic `tasks.json` and signal Task Decomposition completion (e.g., via the Plan's smoke-test scaffolding from T6.2).
  2. Act: spawn `execute-orchestrator`; observe the first state-transition log entry.
  3. Assert: the first entry in `state-transitions.log` is T0 (INIT → pending), followed by T1 (pending → executing) per the 14-transition state machine.
- **Expected outcome**: T0 logged at startup; T1 logged after orchestrator selects the first task.
- **Negative-path coverage**: Verified via AT-077 (T0/T13 boundary explicit).
- **Determinism notes**: Deterministic given fixed input tasks.json fixture.

#### AT-004 — Orchestrator transitions to Deliverable Packaging when terminal gate passes

- **Maps to AC**: AC-FR-1-d
- **Test type**: integration (end-to-end smoke)
- **Layer**: Claude Code
- **Plan task**: T3.1, T6.2
- **Preconditions**: All-clean synthetic feature scaffolding from T6.2 (Phase 6); all per-task and phase-quality dimensions PASS.
- **Steps**:
  1. Arrange: run `execute-orchestrator` against all-clean scaffolding.
  2. Act: let the run complete; capture `state-transitions.log`.
  3. Assert: final logged transition is T13 (any → TERMINATED); `pipeline-run-summary.json` lists `final_ship_status: ready_for_packaging` (or equivalent terminal-ready marker per AC-OP-3).
- **Expected outcome**: T13 boundary transition present; summary marks ready_for_packaging.
- **Negative-path coverage**: AT-077 verifies T0/T13 are both logged in non-degenerate runs.
- **Determinism notes**: Replayable per Blueprint Risk-1 mitigation.

---

### FR-2 Tests: Per-task execution-and-quality inner loop

#### AT-005 — Orchestrator invokes task-execution sub-agent with allowed-file scope

- **Maps to AC**: AC-FR-2-a
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.2
- **Preconditions**: `execute-orchestrator.md` and `execute-task-code-producer.md` exist; task fixture with declared Target Files.
- **Steps**:
  1. Arrange: synthetic task with `target_files: [<path1>, <path2>]`.
  2. Act: orchestrator dispatches code-producer.
  3. Assert: the dispatch payload includes the `allowed_files` field matching the task's Target Files; the agent body of `execute-task-code-producer.md` references "scope" / "target files" / "allowed-file" semantics.
- **Expected outcome**: Dispatch contract matches; agent body honors scope.
- **Negative-path coverage**: Out-of-scope file write surfaces as a Scope-Deviation finding per ADR-0033 (verified via AT-074).
- **Determinism notes**: Static contract verification.

#### AT-006 — Orchestrator invokes per-task quality sub-agent with filesModified

- **Maps to AC**: AC-FR-2-b
- **Test type**: integration / contract
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.3
- **Preconditions**: `execute-task-code-producer.md` and `execute-task-quality-handler.md` exist.
- **Steps**:
  1. Arrange: simulate a code-producer returning `{ status: COMPLETED, files_modified: ["a.py","b.py"] }`.
  2. Act: orchestrator dispatches quality-handler.
  3. Assert: dispatch payload contains `files_modified` field equal to the code-producer's output; quality-handler agent body confirms it scopes verification to that list.
- **Expected outcome**: Files_modified propagated; quality-handler body cites the propagation.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static contract verification.

#### AT-007 — Orchestrator marks task complete and advances when quality returns approved

- **Maps to AC**: AC-FR-2-c
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.3
- **Preconditions**: same as AT-006.
- **Steps**:
  1. Arrange: simulate quality-handler returning `APPROVED`.
  2. Act: orchestrator processes the verdict.
  3. Assert: transition T3 (review_in_progress → completed) is logged; task counter for the completed task increments; next task is selected (or T7 done_n_of_n if last task).
- **Expected outcome**: T3 logged; advance.
- **Negative-path coverage**: AT-008, AT-009 cover non-approved verdicts.
- **Determinism notes**: Deterministic.

#### AT-008 — Orchestrator routes stub_detected through dispatch matrix

- **Maps to AC**: AC-FR-2-d
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.3, T1.3
- **Preconditions**: `detect_stubs.py` (T1.3) integrated.
- **Steps**:
  1. Arrange: stub-fixture (impl file containing `raise NotImplementedError`) becomes code-producer output.
  2. Act: quality-handler invokes `detect_stubs.py`; returns `STUB_DETECTED` with `severity: blocker`.
  3. Assert: orchestrator transitions T6 (review_in_progress → escalated_stub); the finding routes via dispatch matrix; the routing is recorded in `quality-reconciliation-log` with `depth_label: Level 1` (or Level 3 if security-relevant).
- **Expected outcome**: T6 logged; dispatch matrix record present; level label in {Level 1, Level 3}.
- **Negative-path coverage**: AT-008 also verifies path-aware patterns are honored (impl file gets BLOCKER severity per Q-CC-2).
- **Determinism notes**: Deterministic given fixture.

#### AT-009 — Orchestrator routes blocked findings through dispatch matrix

- **Maps to AC**: AC-FR-2-e
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.3
- **Preconditions**: quality-handler agent file exists.
- **Steps**:
  1. Arrange: synthetic quality-handler output `{ status: BLOCKER, finding: {...} }`.
  2. Act: orchestrator processes verdict.
  3. Assert: finding routes through dispatch matrix at Level 4+ per AC-FR-2-e narrative; `quality-reconciliation-log` records the dispatch with depth_label ∈ {Level 4, Level 5, Level 6, Level 7, Level 8}.
- **Expected outcome**: BLOCKER routes to Level 4+ correctly.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-010 — Orchestrator routes escalation_needed from task-executor through dispatch matrix

- **Maps to AC**: AC-FR-2-f
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.2
- **Preconditions**: code-producer agent exists.
- **Steps**:
  1. Arrange: simulate code-producer returning `{ status: escalation_needed, escalation_type: "scope_deviation_needed" }`.
  2. Act: orchestrator processes.
  3. Assert: dispatch matrix invoked with a depth_label in Level 1–6 (range per AC-FR-2-f); routing logged.
- **Expected outcome**: Level 1–6 depth label; dispatch routing recorded.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

---

### FR-3 Tests: Phase-level quality stage

#### AT-011 — Orchestrator enters phase-level quality stage when all tasks completed

- **Maps to AC**: AC-FR-3-a
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.4
- **Preconditions**: orchestrator + reviewer agents exist; tasks.json fixture with N=3 tasks all completing.
- **Steps**:
  1. Arrange: simulate all 3 tasks reach `completed`.
  2. Act: orchestrator processes.
  3. Assert: T7 (done_n_of_n) transition logged; `execute-phase-quality-reviewer` is dispatched next.
- **Expected outcome**: T7 transition recorded; phase-quality-reviewer invocation present.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-012 — Phase-level quality executes the full check inventory (test suites + 3 audits + validator)

- **Maps to AC**: AC-FR-3-b
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.4 (run_phase_checks.py coordinator), T3.4
- **Preconditions**: `run_phase_checks.py` authored (T1.4).
- **Steps**:
  1. Arrange: scaffold a feature whose Layer Scope activates the Claude Code layer only.
  2. Act: invoke `run_phase_checks.py`.
  3. Assert: output JSON aggregates exactly these dimensions: `unit_tests`, `integration_tests`, `e2e_tests` (these three may be empty/N/A for single-layer pipeline-design features), `cc_audit`, `gha_audit`, `codespaces_audit` (stub-marked per Q-CC-4), `frontmatter_validator`, `discipline_check`.
- **Expected outcome**: All 7+ dimensions present in aggregated output.
- **Negative-path coverage**: AT-013 covers stub-codespaces distinction.
- **Determinism notes**: Deterministic; fixture-based.

#### AT-013 — Codespaces audit stub emits `{"stub": true, "findings": []}` distinct from real-but-empty

- **Maps to AC**: AC-FR-3-b (sub-clause re: stub semantics), AC-FR-8-b (stub semantics)
- **Test type**: contract conformance
- **Layer**: Claude Code
- **Plan task**: T1.6
- **Preconditions**: `audit_codespaces.py` stub authored (T1.6).
- **Steps**:
  1. Arrange: stub script staged.
  2. Act: invoke `python3 .claude/skills/auditing-codespaces/scripts/audit_codespaces.py`.
  3. Assert: stdout parses as JSON; equals exactly `{"stub": true, "findings": []}`; no additional fields present.
- **Expected outcome**: Exact match.
- **Negative-path coverage**: Distinct from a clean audit (which would have `stub: false` or no `stub` key).
- **Determinism notes**: Deterministic.

#### AT-014 — Phase-quality-report artifact summarizes pass/fail counts per check

- **Maps to AC**: AC-FR-3-c
- **Test type**: contract conformance
- **Layer**: Claude Code
- **Plan task**: T3.4, T5.2
- **Preconditions**: `phase-quality-report-template.md` exists (T5.2); `execute-phase-quality-reviewer` produces conforming output.
- **Steps**:
  1. Arrange: synthetic phase with mixed-finding fixture.
  2. Act: invoke phase-quality-reviewer; capture `phase-quality-report.json`.
  3. Assert: report has per-dimension `pass_count`, `fail_count`, `total_count` fields; counts sum correctly.
- **Expected outcome**: Counts present and consistent.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-015 — Failing findings classified by depth before phase-quality-report is emitted

- **Maps to AC**: AC-FR-3-d
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.4, T3.5
- **Preconditions**: phase-quality-reviewer + finalize-reconciler agents exist.
- **Steps**:
  1. Arrange: synthetic phase produces 2 fails (one lint-class, one stub-class).
  2. Act: phase-quality-reviewer aggregates; finalize-reconciler classifies.
  3. Assert: every finding in `phase-quality-report.json` has a `depth_label` field with value in {Level 0..Level 8}; no finding's depth is empty/null.
- **Expected outcome**: All findings depth-classified.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-016 — Orchestrator transitions to Deliverable Packaging on zero or only-named-exempt findings

- **Maps to AC**: AC-FR-3-e
- **Test type**: integration (overlaps with AT-004)
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.4
- **Preconditions**: clean fixture from T6.2; alternative fixture with named-exempt findings (mechanism α).
- **Steps**:
  1. Arrange: clean fixture (variant A); named-exempt fixture (variant B).
  2. Act: run orchestrator end-to-end on each.
  3. Assert: in both A and B, T8 phase_quality_pass transition logged; T13 boundary transition follows.
- **Expected outcome**: Both variants reach TERMINATED.
- **Negative-path coverage**: A variant with un-exempt findings does NOT reach T8 — verified via AT-053.
- **Determinism notes**: Deterministic given fixtures.

#### AT-017 — Phase-quality emits Level-5 finding when activated layer has no test suite

- **Maps to AC**: AC-FR-3-f
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.4, T3.4
- **Preconditions**: `run_phase_checks.py` authored (T1.4).
- **Steps**:
  1. Arrange: synthetic feature with Layer Scope activating Backend, but no Backend test suite in scaffolding.
  2. Act: invoke `run_phase_checks.py`.
  3. Assert: output contains a finding with `depth_label: "Level 5"` and `category: "plan-level gap: layer activated without test infrastructure"`; the dimension does NOT silently pass.
- **Expected outcome**: Level-5 finding emitted.
- **Negative-path coverage**: A scaffolding with all layers having tests produces no such finding.
- **Determinism notes**: Deterministic.

---

### FR-4 Tests: Quality-finding depth classifier and dispatch matrix

#### AT-018 — Depth classifier produces label in {Level 0..Level 8}

- **Maps to AC**: AC-FR-4-a
- **Test type**: contract conformance / property-based
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: finalize-reconciler agent body documents the classifier.
- **Steps**:
  1. Arrange: 9 fixtures, one for each Level 0–8 archetype.
  2. Act: invoke classifier per finding.
  3. Assert: output label ∈ {Level 0, Level 1, Level 2, Level 3, Level 4, Level 5, Level 6, Level 7, Level 8}; no out-of-band labels.
- **Expected outcome**: Every fixture classified within the canonical set.
- **Negative-path coverage**: An unknown finding-type fixture should default to a documented fallback level (not silently fail).
- **Determinism notes**: Deterministic.

#### AT-019 — Each level has a single defined dispatch target

- **Maps to AC**: AC-FR-4-b
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: Blueprint §Contract 4 dispatch matrix is published.
- **Steps**:
  1. Load Blueprint dispatch-matrix section.
  2. For each level 0..8, assert: exactly one `dispatch_target` field is named; no level is missing its target; no level has multiple targets.
- **Expected outcome**: 9 levels, 9 targets, no ambiguity.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.

#### AT-020 — Depth semantics match PRD AC-FR-4-c definitions

- **Maps to AC**: AC-FR-4-c
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: Blueprint defines depth semantics; finalize-reconciler body documents them.
- **Steps**:
  1. Load Blueprint depth-semantics section.
  2. Assert: Level 0 = auto-fixable; Level 1–2 = task-implementation/test bug; Level 3 = security/correctness (mechanism α); Level 4 = task-as-written; Level 5 = plan-level gap; Level 6 = blueprint-level; Level 7 = PRD-level; Level 8 = intent.
- **Expected outcome**: All 9 semantics match the PRD wording.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.

#### AT-021 — Cascade rules apply when finding routes to Level 4+

- **Maps to AC**: AC-FR-4-d
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: finalize-reconciler agent body documents cascade rules.
- **Steps**:
  1. Arrange: a Level-5 finding (plan-level gap).
  2. Act: invoke finalize-reconciler.
  3. Assert: cascade rules in finalize-reconciler body specify that re-authoring the Plan triggers tasks.json regeneration AND affected per-task re-execution; the reconciliation log captures the cascade plan.
- **Expected outcome**: Cascade plan present in log.
- **Negative-path coverage**: A Level-0 finding does NOT trigger cascade.
- **Determinism notes**: Deterministic.

#### AT-022 — Dispatch matrix published in Blueprint as single source of truth

- **Maps to AC**: AC-FR-4-e
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: Blueprint structural
- **Preconditions**: Blueprint published.
- **Steps**:
  1. Search Blueprint for the dispatch-matrix section.
  2. Assert: dispatch matrix appears exactly once (§Contract 4 / §Dispatch Taxonomy); no re-definition of the same matrix in agent bodies (agents reference, not redefine).
- **Expected outcome**: Single source-of-truth confirmed.
- **Negative-path coverage**: An agent body that re-defines the matrix should fail this test.
- **Determinism notes**: Static parse.

#### AT-023 — ADR authored documenting depth classifier and dispatch matrix

- **Maps to AC**: AC-FR-4-f
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T0.2 (ADR ratification)
- **Preconditions**: ADRs ratified.
- **Steps**:
  1. Locate the ADR(s) covering depth classifier + dispatch matrix.
  2. Assert: ADR (most likely ADR-0035 paired with the existing-Blueprint dispatch-matrix content, or referenced via Blueprint §Contract 4) is in `status: accepted`; documents depth classifier and dispatch matrix semantics.
- **Expected outcome**: ADR present and accepted.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.
- **Open item**: Per the Plan, the dispatch-matrix content lives in the Blueprint (§Contract 4); the ADR for the depth classifier may be implicit in the cc-design substrate ratified at Blueprint approval rather than a stand-alone ADR. AT-023 verifies both possibilities. Surfaced to Open Items section.

---

### FR-5 Tests: State-transition hooks

#### AT-024 — State-transition hook fires when any pipeline gate passes

- **Maps to AC**: AC-FR-5-a
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.2 (log_state_transition.py), T3.1 (orchestrator invocation)
- **Preconditions**: `log_state_transition.py` exists; orchestrator integrated.
- **Steps**:
  1. Arrange: synthetic gate-pass event with target artifact at `status: draft`.
  2. Act: orchestrator fires state-transition hook.
  3. Assert: target artifact's frontmatter `status` advances to next canonical state (e.g., `draft` → `proposed` for gated artifacts, or `draft` → `complete` for analysis/log artifacts per ADR-0032 per-doc-type vocab); `state-transitions.log` records the transition.
- **Expected outcome**: Status updated; log entry present.
- **Negative-path coverage**: AT-028 covers hook-failure path.
- **Determinism notes**: Deterministic.

#### AT-025 — Reconciliation marks prior version superseded with superseded_by back-link

- **Maps to AC**: AC-FR-5-b
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.2, T3.1
- **Preconditions**: orchestrator handles supersession.
- **Steps**:
  1. Arrange: synthetic reconciliation re-authors artifact `foo-v1.md` as `foo-v2.md`.
  2. Act: orchestrator fires supersession hook.
  3. Assert: `foo-v1.md` frontmatter shows `status: superseded` AND `superseded_by: foo-v2.md`; `foo-v2.md` is at `status: draft` or appropriate next-state per doc-type vocab.
- **Expected outcome**: Both fields updated on prior version.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-026 — Phase-level quality gate pass updates each ratified artifact to final ship state

- **Maps to AC**: AC-FR-5-c
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.2, T3.1
- **Preconditions**: smoke-test scaffolding from T6.2 reaches T8 (phase_quality_pass).
- **Steps**:
  1. Arrange: clean scaffolding.
  2. Act: orchestrator processes T8 phase_quality_pass.
  3. Assert: every ratified pipeline artifact (PRD, Blueprint, Plan, per-task results, phase-quality-report) has `status` updated to the final ship state per ADR-0032 per-doc-type vocab (`accepted` for gated; `complete` for analysis/log; ADR `accepted`).
- **Expected outcome**: All ratified artifacts at ship state.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-027 — State transitions observable in deliverable archive after the run

- **Maps to AC**: AC-FR-5-d
- **Test type**: integration / end-to-end (T6.2 substrate)
- **Layer**: Claude Code
- **Plan task**: T1.2, T6.2
- **Preconditions**: full smoke-test run completed (T6.2).
- **Steps**:
  1. Arrange: run T6.2 smoke test.
  2. Act: enumerate archive contents.
  3. Assert: `state-transitions.log` is present at `working/feature/<feature-slug>/state-transitions.log`; every artifact's `status` accurately reflects its lifecycle position; the log contains entries for every transition T0..T13 exercised in the run; entries are valid JSONL.
- **Expected outcome**: Log present + complete; artifacts' status accurate.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Replayable.

#### AT-028 — Hook failure marks gate failed and surfaces as Level-1 finding

- **Maps to AC**: AC-FR-5-e
- **Test type**: integration / negative-path
- **Layer**: Claude Code
- **Plan task**: T1.2, T3.1
- **Preconditions**: orchestrator + log_state_transition.py exist.
- **Steps**:
  1. Arrange: synthetic gate-pass event where the target artifact's path is unwritable (e.g., file does not exist).
  2. Act: orchestrator fires hook; hook fails.
  3. Assert: gate is marked failed; the failure surfaces as a finding with `depth_label: "Level 1"`; finding routes through dispatch matrix; (per D-16 observer-only) the substantive state transition still completes — failure does NOT block.
- **Expected outcome**: Failure surfaced; Level-1 finding emitted; transition still recorded.
- **Negative-path coverage**: Verifies the canonical failure path.
- **Determinism notes**: Deterministic given failure-injection.

---

### FR-6 Tests: Frontmatter validator

#### AT-029 — Frontmatter validator is invokable as a callable script

- **Maps to AC**: AC-FR-6-a
- **Test type**: structural / config validation
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: `validate_pipeline_frontmatter.py` authored (T1.1) at `.claude/skills/auditing-shared/scripts/`.
- **Steps**:
  1. Locate the script at the canonical path.
  2. Run `python3 <path> --help`.
  3. Assert: exits 0; prints help text; path is distinct from `auditing-skills/scripts/validate_frontmatter.py` (which validates SKILL.md frontmatter, per IN-017).
- **Expected outcome**: Help works; path disambiguated.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-030 — Validator checks required fields, status vocabulary, superseded_by back-link

- **Maps to AC**: AC-FR-6-b
- **Test type**: contract conformance
- **Layer**: Claude Code
- **Plan task**: T1.1, T4.1 (shared-conventions.md v2 sources)
- **Preconditions**: T1.1 + T4.1 complete.
- **Steps**:
  1. Arrange: 5 fixtures — (i) all-fields-present + valid status; (ii) missing required field; (iii) status not in canonical vocab; (iv) superseded artifact missing `superseded_by`; (v) execution-phase artifact violating FR-7 schema.
  2. Act: run validator against each.
  3. Assert: (i) clean pass; (ii)–(v) each emit a finding at appropriate Level.
- **Expected outcome**: 1 clean + 4 findings, each correctly Level-labeled.
- **Negative-path coverage**: Built-in (4 of 5 fixtures are negative).
- **Determinism notes**: Deterministic.

#### AT-031 — Validator recognizes the 20+5 doc_type enum per ADR-0032

- **Maps to AC**: AC-FR-6-b (extended; covers ADR-0032 Change 4)
- **Test type**: contract conformance
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 + ADR-0032 ratified.
- **Steps**:
  1. Arrange: 25 fixtures, one for each doc_type in the 20-planning + 5-execution enum.
  2. Act: validate each.
  3. Assert: each passes the doc_type recognition check; an additional fixture with `doc_type: <invalid-value>` produces a Level-0 or Level-1 finding.
- **Expected outcome**: 25 valid recognitions + 1 negative.
- **Negative-path coverage**: Built-in.
- **Determinism notes**: Deterministic.

#### AT-032 — Validator emits finding at Level 0 (auto-fixable) or Level 1 (manual) on detected issue

- **Maps to AC**: AC-FR-6-c
- **Test type**: contract conformance
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 complete.
- **Steps**:
  1. Arrange: fixtures triggering each finding class (missing typo-fixable field = Level 0; semantic correctness issue = Level 1).
  2. Act: validate.
  3. Assert: outputs contain `depth_label` ∈ {Level 0, Level 1}; the choice between 0 and 1 is documented and matches the finding type.
- **Expected outcome**: Findings correctly Level-classified.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-033 — Validator runs as part of phase-level quality + at every other gate

- **Maps to AC**: AC-FR-6-d
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.1, T3.4
- **Preconditions**: validator + phase-quality-reviewer integrated.
- **Steps**:
  1. Arrange: run T6.2 smoke test; instrument every gate boundary to log validator invocations.
  2. Act: complete the run.
  3. Assert: validator is invoked at every documented gate (Phase 0 exit, Phase 1 exit, ... Phase 6 exit); validator also runs inside `run_phase_checks.py` (T1.4).
- **Expected outcome**: Validator invocation count ≥ number of gate boundaries.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-034 — Validator's failure on planning-side artifact routes to planning-side reconciliation (governed by ADR-0017)

- **Maps to AC**: AC-FR-6-e
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: finalize-reconciler exists; ADR-0017 ratified as canonical home per ADR-0034.
- **Steps**:
  1. Arrange: synthetic planning-side artifact (e.g., a PRD) with frontmatter violation.
  2. Act: validator detects; orchestrator routes finding.
  3. Assert: finding's `dispatch_target` is a planning-side reconciliation agent (e.g., `intake-prd-author`); `quality-reconciliation-log` entry cites **ADR-0017** as the governing budget ADR (NOT ADR-0021 per ADR-0034 + Blueprint v5 §AC-FR-6-e footnote + cycle-3 D-RC3-3).
- **Expected outcome**: Routing correct; ADR-0017 cited.
- **Negative-path coverage**: Cross-check: AT-052 verifies AC-FR-10-b sibling-case (execution-side budget routing) also cites ADR-0017 forward.
- **Determinism notes**: Deterministic.
- **Citation note (per ADR-0034)**: The PRD AC-FR-6-e text literally cites ADR-0021. This is preserved as a transcription artifact in the PRD per ADR-0005; downstream artifacts (this acceptance-tests doc) cite the corrected ADR-0017 per the Blueprint v5 §AC-FR-6-e footnote. AT-034's assertion uses ADR-0017.

---

### FR-7 Tests: Execution-phase artifact schemas and templates

#### AT-035 — Each execution-phase artifact has a template file with `-template.md` suffix

- **Maps to AC**: AC-FR-7-a
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.1, T5.2, T5.3, T5.4, T5.5
- **Preconditions**: Phase 5 templates authored.
- **Steps**:
  1. Enumerate `KB-documentation-criteria/references/templates/*.md`.
  2. Assert: presence of `per-task-execution-result-template.md`, `phase-quality-report-template.md`, `quality-reconciliation-log-template.md`, `state-transitions-log-entry-template.md`, `pipeline-run-summary-template.md`; each file parses; each ends with `-template.md`.
- **Expected outcome**: 5 templates present; all conform to suffix convention.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.

#### AT-036 — Execution-phase artifact schemas documented in shared-conventions.md

- **Maps to AC**: AC-FR-7-b
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T4.1
- **Preconditions**: T4.1 complete (shared-conventions.md v2 spec).
- **Steps**:
  1. Read `KB-documentation-criteria/references/shared-conventions.md`.
  2. Assert: section "Execution-phase artifact frontmatter" present; documents schemas for `per-task-execution-result`, `phase-quality-report`, `quality-reconciliation-log`, `state-transitions-log-entry`, `pipeline-run-summary`.
- **Expected outcome**: Section + 5 schemas present.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.

#### AT-037 — Execution-phase artifact list includes the AC-FR-7-c minimum-floor inventory

- **Maps to AC**: AC-FR-7-c
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.*
- **Preconditions**: Blueprint published; templates authored.
- **Steps**:
  1. Map the 5 AC-FR-7-c floor items to templates: per-task execution log → `per-task-execution-result-template.md`; phase-quality report → `phase-quality-report-template.md`; quality-reconciliation log (per cycle) → `quality-reconciliation-log-template.md`; frontmatter-validation report → script-output schema inline in `validate_pipeline_frontmatter.py` (T1.1, per Path B); execution-reconciliation log → `pipeline-run-summary-template.md` (per Path B equivalence per Blueprint §AC-FR-7 floor coverage + ADR-0033 §Context cross-reference per I-AA-606).
  2. Assert: all 5 floor items have a canonical surface (template OR inline script schema).
- **Expected outcome**: All 5 floor items covered.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.
- **Note**: AT-074 / AT-075 verify the ADR-0033 §Context bidirectional cross-reference that makes the Path B equivalence rigorous.

#### AT-038 — Additional artifacts beyond AC-FR-7-c floor conform to AC-FR-7-a + AC-FR-7-b

- **Maps to AC**: AC-FR-7-d
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.4 (state-transitions-log-entry), T5.5 (pipeline-run-summary)
- **Preconditions**: Phase 5 templates authored.
- **Steps**:
  1. Identify beyond-floor templates: `state-transitions-log-entry-template.md` and `pipeline-run-summary-template.md`.
  2. Assert: both end with `-template.md` (AC-FR-7-a satisfied); both have schema documented in shared-conventions.md (AC-FR-7-b satisfied per AT-036).
- **Expected outcome**: 2 beyond-floor templates conform.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static parse.

---

### FR-8 Tests: Three-way auditing split

#### AT-039 — `auditing-github-actions` skill exists at canonical path

- **Maps to AC**: AC-FR-8-a
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T2.1
- **Preconditions**: T2.1 complete.
- **Steps**:
  1. Locate `.claude/skills/auditing-github-actions/`.
  2. Assert: directory exists with `SKILL.md`, `scripts/audit_workflow.py`, `references/action_versions.md`.
  3. Assert: `git log --follow .claude/skills/auditing-github-actions/scripts/audit_workflow.py` shows historical commits from the prior `KB-github-actions-platform/scripts/` path (verifies git mv, NOT copy-and-delete).
- **Expected outcome**: Skill directory + scripts + history preservation.
- **Negative-path coverage**: A copy-and-delete would fail step 3.
- **Determinism notes**: Static / git inspection.

#### AT-040 — `auditing-codespaces` skill exists as stub per AC-FR-8-b

- **Maps to AC**: AC-FR-8-b
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T2.2, T1.6
- **Preconditions**: T2.2 + T1.6 complete.
- **Steps**:
  1. Locate `.claude/skills/auditing-codespaces/`.
  2. Assert: directory exists with `SKILL.md` and `scripts/audit_codespaces.py`.
  3. Assert: `audit_codespaces.py` emits `{"stub": true, "findings": []}` exactly (verified via AT-013).
- **Expected outcome**: Stub skill present with canonical stub-marker output.
- **Negative-path coverage**: AT-013.
- **Determinism notes**: Static / runtime stub check.

#### AT-041 — Helpers shared across auditing-X skills are in auditing-shared

- **Maps to AC**: AC-FR-8-c
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T2.1, T2.2, structural
- **Preconditions**: T1.* and T2.* complete.
- **Steps**:
  1. Locate the 5 new auditing-shared scripts (`detect_stubs.py`, `run_phase_checks.py`, `log_state_transition.py`, `validate_pipeline_frontmatter.py`, `check_pipeline_discipline.py`).
  2. Assert: all live under `.claude/skills/auditing-shared/scripts/` per ADR-0031 canonical-helper-home; no duplicate copies exist under any `auditing-X/scripts/` path.
- **Expected outcome**: Shared helpers in shared location only.
- **Negative-path coverage**: A duplicate would fail.
- **Determinism notes**: Static.

#### AT-042 — Sub-agents/scripts reference the new auditing-X skill, not KB-X-platform

- **Maps to AC**: AC-FR-8-d
- **Test type**: structural / contract
- **Layer**: Claude Code
- **Plan task**: T4.3, T4.4
- **Preconditions**: T4.3 + T4.4 complete.
- **Steps**:
  1. Grep all `.claude/agents/*.md` for references to GHA audit functionality.
  2. Assert: references point to `auditing-github-actions` (not `KB-github-actions-platform/scripts/audit_workflow.py` directly).
- **Expected outcome**: Clean transition.
- **Negative-path coverage**: A residual reference would fail.
- **Determinism notes**: Static.

#### AT-043 — KB-X-platform SKILL.md Contents list updated

- **Maps to AC**: AC-FR-8-e
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T2.1
- **Preconditions**: T2.1 complete.
- **Steps**:
  1. Read `KB-github-actions-platform/SKILL.md`.
  2. Assert: Contents list does NOT reference relocated scripts (`audit_workflow.py`, `action_versions.md`); DOES point to `auditing-github-actions` for audit functionality.
- **Expected outcome**: Contents list cleaned + pointer added.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

#### AT-044 — Caller agent skill bindings additionally / instead load auditing-X

- **Maps to AC**: AC-FR-8-f
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T4.3, T4.4
- **Preconditions**: T4.3 + T4.4 complete.
- **Steps**:
  1. Read `design-cicd.md` and `design-codespaces.md`.
  2. Assert: `design-cicd.md` skills frontmatter additionally lists `auditing-github-actions`; `design-codespaces.md` additionally lists `auditing-codespaces`.
- **Expected outcome**: Bindings updated additively.
- **Negative-path coverage**: A binding that drops `KB-X-platform` is permissible per AC-FR-8-f's "additionally (or instead)" language; AT-044 accepts either pattern.
- **Determinism notes**: Static.

---

### FR-9 Tests: ai-development-guide skill binding and sequencing

#### AT-045 — Task-execution sub-agent lists ai-development-guide in skills

- **Maps to AC**: AC-FR-9-a
- **Test type**: structural / config validation
- **Layer**: Claude Code
- **Plan task**: T3.2, T3.3
- **Preconditions**: T3.2 + T3.3 complete.
- **Steps**:
  1. Parse `.claude/agents/execute-task-code-producer.md` and `.claude/agents/execute-task-quality-handler.md` frontmatter.
  2. Assert: both files' `skills:` field contains `ai-development-guide`.
- **Expected outcome**: Binding present on both code-producing agents.
- **Negative-path coverage**: AT-047 verifies validator fails an agent missing this binding.
- **Determinism notes**: Static.

#### AT-046 — Blueprint documents which execution-phase sub-agents qualify as code-producing

- **Maps to AC**: AC-FR-9-b
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: Blueprint structural (D-11)
- **Preconditions**: Blueprint published.
- **Steps**:
  1. Search Blueprint for D-11 binding criterion / agent enumeration.
  2. Assert: Blueprint explicitly enumerates `execute-task-code-producer` and `execute-task-quality-handler` as the two code-producing agents bound to `ai-development-guide`.
- **Expected outcome**: Enumeration present.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

#### AT-047 — Frontmatter validator fails a code-producing agent missing ai-development-guide binding

- **Maps to AC**: AC-FR-9-c
- **Test type**: contract / negative-path
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 complete.
- **Steps**:
  1. Arrange: fixture agent file with name matching code-producer naming convention, but `skills:` missing `ai-development-guide`.
  2. Act: run validator.
  3. Assert: validator emits finding at Level 0 or Level 1 indicating missing required binding.
- **Expected outcome**: Validator fails the fixture; the finding is clearly described.
- **Negative-path coverage**: Built-in.
- **Determinism notes**: Deterministic.

#### AT-048 — Blueprint cites ai-development-guide's purpose as rationale for FR-9

- **Maps to AC**: AC-FR-9-d
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: Blueprint structural
- **Preconditions**: Blueprint published.
- **Steps**:
  1. Search Blueprint for citation of "technical decision criteria", "anti-pattern detection", "debugging techniques", "quality-check workflow".
  2. Assert: all four phrases appear in the Blueprint's rationale for FR-9 / Component 2-3 description.
- **Expected outcome**: All 4 phrases cited.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

#### AT-049 — Plan includes task installing ai-development-guide skill

- **Maps to AC**: AC-FR-9-e
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T2.3
- **Preconditions**: Plan v2 ratified.
- **Steps**:
  1. Read Plan v2 §Phase 2.
  2. Assert: T2.3 task exists; description names installation of `ai-development-guide` skill at `.claude/skills/ai-development-guide/SKILL.md`; sources content from `/mnt/user-data/uploads/SKILL__2_.md`.
- **Expected outcome**: T2.3 present and correct.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

#### AT-050 — ai-development-guide skill install sequencing precedes binding agents

- **Maps to AC**: AC-FR-9-e (sequencing clause); AC-FR-9-c
- **Test type**: structural / dependency check
- **Layer**: Claude Code
- **Plan task**: T2.3 (must precede T3.2 + T3.3)
- **Preconditions**: Plan v2 dependency graph.
- **Steps**:
  1. Read Plan v2 Cross-Phase Dependencies + task `Dependencies:` fields.
  2. Assert: T3.2 lists T2.3 as a dependency; T3.3 lists T2.3 as a dependency (transitively if not directly); Phase 2 (which contains T2.3) is documented to complete before Phase 3 (which contains T3.2 + T3.3).
- **Expected outcome**: Sequencing constraint enforced in plan.
- **Negative-path coverage**: Verifies the FR-9-e "before any execution-phase sub-agent definitions that bind to the skill" sequencing.
- **Determinism notes**: Static.

---

### FR-10 Tests: Execution-side reconciliation budget

#### AT-051 — ADR exists defining the execution-side reconciliation budget (canonical home = ADR-0017)

- **Maps to AC**: AC-FR-10-a
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T0.2 (ADRs ratified)
- **Preconditions**: ADR-0017 + ADR-0034 ratified.
- **Steps**:
  1. Locate ADR-0017 and ADR-0034.
  2. Assert: ADR-0017 defines the 4-cycle cap symmetric to per-task quality loops per D-12; ADR-0034 cleans up the PRD v1.1.0 mis-credit referencing ADR-0021. ADR-0017's `status` is `accepted`; ADR-0034's `status` is `accepted`.
- **Expected outcome**: Canonical home + cleanup ADR both present and ratified.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.
- **Citation note (per ADR-0034)**: AC-FR-10-a in the PRD references "an ADR" without naming it; the Blueprint resolves this to ADR-0017 (with ADR-0034 cleaning up the PRD mis-credit). AT-051 verifies this resolution.

#### AT-052 — Budget cap applies to quality-reconciliation loop; does NOT modify planning-side budget (per ADR-0017 forward citation per ADR-0034)

- **Maps to AC**: AC-FR-10-b
- **Test type**: structural / integration
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: finalize-reconciler agent + ADR-0017 ratified.
- **Steps**:
  1. Read finalize-reconciler agent body.
  2. Assert: agent body cites **ADR-0017** as the canonical home for the 4-cycle cap (NOT ADR-0021 per Blueprint v5 §AC-FR-10-b footnote + ADR-0034 + cycle-3 D-RC3-3); body explicitly states the cap applies to execution-side reconciliation only and does NOT modify planning-side budget.
- **Expected outcome**: ADR-0017 cited (not ADR-0021); scope clarification present.
- **Negative-path coverage**: A reconciler citing ADR-0021 would fail.
- **Determinism notes**: Static.
- **Citation note (per ADR-0034)**: This test mirrors AT-034 — both verify the AC correction-surface per I-AA-604 / cycle-3 D-RC3-3. The PRD's verbatim ADR-0021 reference is preserved as a transcription artifact in the PRD; downstream artifacts cite ADR-0017 forward.

#### AT-053 — Budget exhaustion produces budget-exhausted artifact + escalates to project owner

- **Maps to AC**: AC-FR-10-c
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.5, T3.1
- **Preconditions**: finalize-reconciler integrated; smoke-test scaffolding contains a finding that reaches the 4-cycle cap.
- **Steps**:
  1. Arrange: scaffolding fixture (iv) from T6.2 with a phase-quality finding that reaches cap.
  2. Act: run reconciler 4 times.
  3. Assert: on cycle 4, finalize-reconciler emits a `budget-exhausted` artifact at `working/feature/<feature-slug>/budget-exhausted-<timestamp>.{json,md}` summarizing unresolved findings; orchestrator state transitions to budget-exhausted-escalation per state machine T11; escalation message names the 3 options (extend / accept-named-exempt / abort).
- **Expected outcome**: Budget-exhausted artifact + escalation present.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic given fixture.

#### AT-054 — Budget cap is per-feature configurable with default 4 cycles

- **Maps to AC**: AC-FR-10-d
- **Test type**: structural / config validation
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: ADR-0017 + reconciler agent body.
- **Steps**:
  1. Read ADR-0017 + reconciler agent body.
  2. Assert: 4-cycle default documented; configuration mechanism named (e.g., `reconciliation_budget_cap:` field overridable per-feature); a configured override is documented to take precedence over the default.
- **Expected outcome**: Default + override mechanism present.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

---

### FR-11 Tests: Canonical state vocabulary

#### AT-055 — Canonical state vocabulary documented in shared-conventions.md

- **Maps to AC**: AC-FR-11-a
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T4.1
- **Preconditions**: T4.1 complete (shared-conventions.md v2).
- **Steps**:
  1. Read `shared-conventions.md`.
  2. Assert: per-doc-type 3-tier vocabulary present: gated 5-state (`draft → proposed → accepted → superseded OR rejected`); analysis/log 3-state (`draft → complete OR superseded`); ADR 4-state (`proposed → accepted OR superseded OR rejected`).
- **Expected outcome**: 3-tier vocab documented.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

#### AT-056 — Every template uses default status value from canonical vocabulary

- **Maps to AC**: AC-FR-11-b
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.*
- **Preconditions**: Phase 5 templates authored.
- **Steps**:
  1. Enumerate all `*-template.md` in `KB-documentation-criteria/references/templates/`.
  2. Parse each frontmatter; extract `status:` value.
  3. Assert: every `status:` value belongs to the appropriate doc-type vocabulary tier.
- **Expected outcome**: All templates pass.
- **Negative-path coverage**: A template defaulting to an out-of-vocab value would fail.
- **Determinism notes**: Static.

#### AT-057 — Frontmatter validator flags artifact whose status is not in canonical vocabulary for that doc-type

- **Maps to AC**: AC-FR-11-c
- **Test type**: contract / negative-path
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 complete.
- **Steps**:
  1. Arrange: fixture artifact with `doc_type: prd` (gated 5-state) but `status: complete` (analysis/log term, not in gated vocab).
  2. Act: validate.
  3. Assert: validator emits finding (Level 0 or 1) indicating status-vocabulary mismatch for the artifact's doc_type.
- **Expected outcome**: Mismatch flagged.
- **Negative-path coverage**: Built-in.
- **Determinism notes**: Deterministic.

#### AT-058 — Validator's enforcement scoped to post-implementation date forward (historical archives not flagged)

- **Maps to AC**: AC-FR-11-d
- **Test type**: contract / scope check
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 complete.
- **Steps**:
  1. Arrange: fixture artifact with `generated:` timestamp predating the feature's deployment date and missing `doc_type` field.
  2. Act: validate.
  3. Assert: no finding emitted for the absence of `doc_type` on the historical artifact; current-date fixture without `doc_type` DOES emit a finding.
- **Expected outcome**: Historical tolerance + forward-scoping enforced.
- **Negative-path coverage**: Built-in (current-date fixture comparison).
- **Determinism notes**: Deterministic.

#### AT-059 — ADR pins canonical vocabulary + resolves accepted-vs-approved drift

- **Maps to AC**: AC-FR-11-e
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T0.2 (ADR-0032 ratified)
- **Preconditions**: ADR-0032 ratified.
- **Steps**:
  1. Read ADR-0032.
  2. Assert: ADR-0032 explicitly resolves the `accepted` vs `approved` drift in favor of `accepted` for gated artifacts AND introduces `complete` for analysis/log artifacts; status is `accepted`.
- **Expected outcome**: Resolution documented; ADR accepted.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

---

### FR-12 Tests: Phase-quality-report audit-counter delta

#### AT-060 — Phase-quality-report frontmatter includes audit_baseline and audit_final per platform audit family

- **Maps to AC**: AC-FR-12-a
- **Test type**: contract conformance
- **Layer**: Claude Code
- **Plan task**: T3.4, T5.2
- **Preconditions**: phase-quality-reviewer authors conforming reports.
- **Steps**:
  1. Arrange: synthetic phase with known baseline+final counts.
  2. Act: invoke phase-quality-reviewer.
  3. Assert: `phase-quality-report.json` frontmatter contains `audit_baseline:` and `audit_final:` objects with sub-keys for `cc`, `gha`, `codespaces`, `frontmatter_validator`, `discipline`; counts match the synthetic ground truth.
- **Expected outcome**: All 5 audit families present in both baseline and final.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic given fixture.

#### AT-061 — Deliverable archive surfaces audit-counter delta in packager-report summary

- **Maps to AC**: AC-FR-12-b
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T3.4, T5.5
- **Preconditions**: pipeline-run-summary.json template authored (T5.5); orchestrator generates summary.
- **Steps**:
  1. Run T6.2 smoke test.
  2. Locate `pipeline-run-summary.json`.
  3. Assert: summary contains an `audit_delta:` field surfacing the baseline-vs-final per-domain delta (carried from phase-quality-report).
- **Expected outcome**: Delta in summary.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

---

### FR-13 Tests: Reconciliation-log machine-parseable

#### AT-062 — Quality-reconciliation log template defines per-entry structure with explicit field labels

- **Maps to AC**: AC-FR-13-a
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.3
- **Preconditions**: T5.3 complete.
- **Steps**:
  1. Read `quality-reconciliation-log-template.md`.
  2. Assert: template defines a per-entry block with explicit field labels (e.g., `cycle:`, `finding_id:`, `depth_label:`, `dispatch_target:`, `outcome:`); the `.json` half schema documents identical field names for downstream extraction.
- **Expected outcome**: Per-entry structure documented.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static.

#### AT-063 — Reconciliation logs are machine-parseable for downstream analytics

- **Maps to AC**: AC-FR-13-b
- **Test type**: contract / property-based
- **Layer**: Claude Code
- **Plan task**: T5.3
- **Preconditions**: T5.3 complete; synthetic log fixtures available.
- **Steps**:
  1. Arrange: synthetic `quality-reconciliation-log-cycle-1.json` (the .json half).
  2. Act: parse with a generic JSON-schema validator against the template's documented schema.
  3. Assert: extraction of finding-depth distribution, dispatch-target frequency, and budget-utilization metrics succeeds without bespoke parsing.
- **Expected outcome**: Generic-extractor succeeds.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

---

## Operational AC Tests

#### AT-064 — Execution-phase artifacts archived to standard layout

- **Maps to AC**: AC-OP-1
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T6.2
- **Preconditions**: T6.2 smoke test run completed.
- **Steps**:
  1. Enumerate `working/feature/_smoke_test_execution_pipeline/` (or analogous test scaffolding path).
  2. Assert: per-task results, phase-quality-report, quality-reconciliation-logs (if any), state-transitions.log, and pipeline-run-summary.json are present at canonical paths.
  3. Assert: `state-transitions.log` is at the canonical path `working/feature/<feature-slug>/state-transitions.log`.
- **Expected outcome**: Standard layout honored.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Static post-run inspection.

#### AT-065 — Discipline-5 mechanical enforcement runs at every gate via check_pipeline_discipline.py

- **Maps to AC**: AC-OP-2
- **Test type**: integration
- **Layer**: Claude Code
- **Plan task**: T1.5, T1.1
- **Preconditions**: T1.5 + T1.1 complete; T1.4 integrates the discipline check.
- **Steps**:
  1. Arrange: synthetic artifact containing the phrase "stage 12" (a pipeline-stage-by-number reference, the canonical discipline-5 violation).
  2. Act: invoke `check_pipeline_discipline.py` against the artifact.
  3. Assert: emits a finding with `severity: minor` (Level 0 auto-fixable); a context-sensitive variant (e.g., the reference in normative content) emits `severity: major` (Level 1).
  4. Cross-check: `run_phase_checks.py` (T1.4) invokes `check_pipeline_discipline.py` as one of its dimensions; the finding surfaces in `phase-quality-report.json`'s discipline dimension.
- **Expected outcome**: Discipline check emits findings; integration into phase-quality verified.
- **Negative-path coverage**: A fixture containing "Phase 1" (Plan-phase reference, not stage-by-number) does NOT emit a finding.
- **Determinism notes**: Deterministic.

#### AT-066 — pipeline-run-summary.json produced at run termination

- **Maps to AC**: AC-OP-3
- **Test type**: integration / end-to-end
- **Layer**: Claude Code
- **Plan task**: T3.1, T5.5
- **Preconditions**: T6.2 smoke test run completed.
- **Steps**:
  1. Run T6.2 smoke test.
  2. Locate `pipeline-run-summary.json`.
  3. Assert: file present at canonical path; contains `per_stage_gate_outcomes`, `total_reconciliation_cycles_consumed`, `total_findings_dispatched_per_level` (a 9-row breakdown for Levels 0..8), and `final_ship_status`.
- **Expected outcome**: Summary present + complete.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Replayable.

---

## v5-Introduced Items: Dedicated Tests

These tests verify the cycle-3 cycle-introduced items beyond the standard AC coverage above. They are NOT redundant with the AC tests — they verify the specific corrections made in v5.

#### AT-067 — execute-task-quality-handler declares unrestricted Bash (matches cc-design.md verbatim)

- **Maps to AC**: AC-FR-2-d (substrate), I-AA-602
- **Test type**: structural / config validation
- **Layer**: Claude Code
- **Plan task**: T3.3
- **Preconditions**: T3.3 complete; cc-design.md ratified.
- **Steps**:
  1. Parse `.claude/agents/execute-task-quality-handler.md` frontmatter.
  2. Assert: `tools:` list contains the bare token `Bash` (NOT `Bash(python3:*)` or any other narrowed form).
  3. Cross-check: `cc-design.md` (the substrate doc) shows the same unrestricted form.
- **Expected outcome**: Bash unrestricted; matches cc-design substrate verbatim.
- **Negative-path coverage**: A frontmatter declaring `Bash(python3:*)` would fail this test (per I-AA-602 cycle-3 widening).
- **Determinism notes**: Static parse.

#### AT-068 — Validator accepts unrestricted Bash declaration (does NOT reject)

- **Maps to AC**: AC-FR-2-d (substrate), AC-FR-6-b, I-AA-602
- **Test type**: contract / negative-path
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 complete with v5 Frontmatter validator coverage rewrite per I-AA-601.
- **Steps**:
  1. Arrange: fixture agent file with `tools: [Bash]` (unrestricted).
  2. Act: validate via T1.1 frontmatter validator.
  3. Assert: validator does NOT emit a finding rejecting the unrestricted form; the validator accepts both `Bash` and `Bash(<pattern>:*)` per the v5 coverage rewrite.
- **Expected outcome**: Both forms accepted; no false-positive reject.
- **Negative-path coverage**: Built-in.
- **Determinism notes**: Deterministic.

#### AT-069 — Four of the five execute-* agents declare auditing-shared in skills (ADR-0035)

- **Maps to AC**: AC-FR-9-a (substrate), I-AA-603 / ADR-0035
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T3.1, T3.3, T3.4, T3.5
- **Preconditions**: Phase 3 complete.
- **Steps**:
  1. Parse frontmatter of `execute-orchestrator.md`, `execute-task-quality-handler.md`, `execute-phase-quality-reviewer.md`, `execute-finalize-reconciler.md`.
  2. Assert: each `skills:` list contains `auditing-shared`.
- **Expected outcome**: 4 agents bind.
- **Negative-path coverage**: AT-070.
- **Determinism notes**: Static.

#### AT-070 — execute-task-code-producer does NOT declare auditing-shared (single-script criterion)

- **Maps to AC**: AC-FR-9-a (substrate), I-AA-603 / ADR-0035
- **Test type**: structural / negative
- **Layer**: Claude Code
- **Plan task**: T3.2
- **Preconditions**: T3.2 complete.
- **Steps**:
  1. Parse frontmatter of `execute-task-code-producer.md`.
  2. Assert: `skills:` does NOT contain `auditing-shared`; the agent's body documents the rationale (does not materially depend on multi-script auditing-shared orchestration per ADR-0035 single-script criterion).
- **Expected outcome**: Binding absent; rationale documented.
- **Negative-path coverage**: An agent with `auditing-shared` would (under ADR-0035's optional-binding clause) NOT be a failure if it's truly multi-script-dependent; but for code-producer, the single-script criterion makes the binding inappropriate.
- **Determinism notes**: Static.

#### AT-071 — Validator accepts both binding and non-binding states (ADR-0035 is optional, not mandatory)

- **Maps to AC**: I-AA-603 / ADR-0035
- **Test type**: contract
- **Layer**: Claude Code
- **Plan task**: T1.1
- **Preconditions**: T1.1 complete.
- **Steps**:
  1. Arrange: two fixtures — (a) an execution-phase agent with `auditing-shared` in skills; (b) the same agent without `auditing-shared` in skills.
  2. Act: validate each.
  3. Assert: both pass; ADR-0035 binding is optional convention, not validator-enforced.
- **Expected outcome**: Both accepted.
- **Negative-path coverage**: N/A.
- **Determinism notes**: Deterministic.

#### AT-072 — Correction-surface tests: AC-FR-6-e + AC-FR-10-b downstream artifacts cite ADR-0017 (NOT ADR-0021)

- **Maps to AC**: AC-FR-6-e, AC-FR-10-b, I-AA-604
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T3.5
- **Preconditions**: Blueprint v5 + finalize-reconciler agent body.
- **Steps**:
  1. Read Blueprint v5 §AC-FR-6-e and §AC-FR-10-b correction-surface footnotes.
  2. Assert: both footnotes name ADR-0017 as the canonical home and explicitly mark the PRD's ADR-0021 reference as a transcription artifact (per ADR-0034 + cycle-3 D-RC3-3).
  3. Read finalize-reconciler agent body; assert it cites ADR-0017 (not ADR-0021).
  4. Read this acceptance-tests doc's AT-034 + AT-052 (self-reference): assert they cite ADR-0017 forward.
- **Expected outcome**: All downstream surfaces cite ADR-0017; PRD's ADR-0021 marked as transcription artifact.
- **Negative-path coverage**: A downstream artifact citing ADR-0021 would fail.
- **Determinism notes**: Static.

#### AT-073 — Plan's Posture-A explicit surfacing: doc_type backfill not bundled into primary scope

- **Maps to AC**: I-AA-605
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T6.1 (Posture A surfacing)
- **Preconditions**: Plan v2 ratified.
- **Steps**:
  1. Read Plan v2 §Phase 6 / T6.1 description.
  2. Assert: task description explicitly names two postures — Posture A (default; defer to follow-on) and Posture B (execute as batched task); Posture A is named as the Plan v2 default; the scope deviation (planning-side agents not yet emitting doc_type) is surfaced as a Scope-Deviation per ADR-0033.
  3. Assert: Plan v2 Open Items section names this surfacing as Open Item #5 (or equivalent).
- **Expected outcome**: Postures explicit; default named; ADR-0033 surfacing in place.
- **Negative-path coverage**: A Plan that silently absorbed the backfill into primary scope would fail.
- **Determinism notes**: Static.

#### AT-074 — ADR-0033 §Context bidirectional cross-reference (direction 1: ADR-0033 → Blueprint)

- **Maps to AC**: AC-FR-7-d (substrate), I-AA-606
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.4
- **Preconditions**: ADR-0033 in `status: accepted` post-T0.2; Blueprint v5 §AC-FR-7 floor coverage section present.
- **Steps**:
  1. Read ADR-0033 §Context.
  2. Assert: §Context names Blueprint v5 §AC-FR-7 floor coverage as the cross-reference target (i.e., ADR-0033 → Blueprint).
- **Expected outcome**: Forward cross-reference present.
- **Negative-path coverage**: AT-075 covers the reverse direction.
- **Determinism notes**: Static.

#### AT-075 — ADR-0033 §Context bidirectional cross-reference (direction 2: Blueprint → ADR-0033)

- **Maps to AC**: AC-FR-7-d (substrate), I-AA-606
- **Test type**: structural
- **Layer**: Claude Code
- **Plan task**: T5.5
- **Preconditions**: Blueprint v5 §AC-FR-7 floor coverage present.
- **Steps**:
  1. Read Blueprint v5 §AC-FR-7 floor coverage Path B disposition.
  2. Assert: the section explicitly references ADR-0033 §Context as the cross-reference target (i.e., Blueprint → ADR-0033).
- **Expected outcome**: Reverse cross-reference present.
- **Negative-path coverage**: AT-074 covers the forward direction. Both must hold for bidirectional.
- **Determinism notes**: Static.

#### AT-076 — execute-orchestrator's tools include Write

- **Maps to AC**: AC-FR-5-d (substrate), AC-OP-3 (substrate), I-AA-608
- **Test type**: structural / config validation
- **Layer**: Claude Code
- **Plan task**: T3.1, T1.1
- **Preconditions**: T3.1 complete.
- **Steps**:
  1. Parse `.claude/agents/execute-orchestrator.md` frontmatter.
  2. Assert: `tools:` list contains `Write` (alongside `Read, Glob, Grep, Bash(python3:*), Agent, TaskUpdate`).
  3. Cross-check: agent body documents that orchestrator directly authors `pipeline-run-summary.json` and `state-transitions.log` (which requires Write).
- **Expected outcome**: Write present in tools list.
- **Negative-path coverage**: Earlier v3+ Security sections were stale on this; the v5 cycle-3 correction ensures Write is present per I-AA-608.
- **Determinism notes**: Static.

#### AT-077 — T0 INIT + T13 TERMINATED boundary transitions in state machine inventory

- **Maps to AC**: AC-FR-1-c (substrate), AC-FR-1-d (substrate), AC-FR-5-d (substrate), I-AA-609
- **Test type**: structural / property-based
- **Layer**: Claude Code
- **Plan task**: T3.1, T1.2
- **Preconditions**: Blueprint v5 §State Transitions + execute-orchestrator agent body + log_state_transition.py schema.
- **Steps**:
  1. Read Blueprint v5 §State Transitions and Invariants.
  2. Assert: transition inventory enumerates exactly 14 transitions = 12 substantive (T1..T12) + 2 boundary (T0 INIT→pending; T13 any→TERMINATED).
  3. Read execute-orchestrator agent body; assert it explicitly enumerates all 14.
  4. Read `log_state_transition.py` schema; assert it accepts T0 and T13 transition names (not just T1..T12).
  5. Read invariant 10; assert that cycle-counter equivalence is scoped to T4 and T10 only (T0 and T13 do NOT increment cycle counters).
- **Expected outcome**: All three surfaces (Blueprint, orchestrator body, log script) consistent at 14 transitions.
- **Negative-path coverage**: A surface enumerating only 12 transitions would fail.
- **Determinism notes**: Static parse + property check.

#### AT-078 — log_state_transition.py emits valid JSONL for T0/T13 boundary transitions

- **Maps to AC**: AC-FR-5-d (substrate), I-AA-609
- **Test type**: contract / integration
- **Layer**: Claude Code
- **Plan task**: T1.2
- **Preconditions**: T1.2 complete.
- **Steps**:
  1. Arrange: pipe a T0 boundary payload (`{from_state: INIT, to_state: pending, transition_name: T0}`) into `log_state_transition.py`.
  2. Act: assert stdout / log-append succeeds; one JSONL line added to `state-transitions.log`.
  3. Repeat for T13 boundary payload (`{to_state: TERMINATED, transition_name: T13}`).
  4. Assert: both boundary entries are valid JSONL conforming to Contract 5.
- **Expected outcome**: T0 + T13 boundary entries appended correctly.
- **Negative-path coverage**: An invalid boundary payload (missing required field) fails with non-blocking exit code per AC-FR-5-e.
- **Determinism notes**: Deterministic.

---

## Test Infrastructure Required

The tests above require the following infrastructure. The Plan's tasks produce all of this; no net-new infrastructure beyond what the Plan already authors:

| Item | Source / Location | Provides |
|---|---|---|
| `validate_pipeline_frontmatter.py` | `.claude/skills/auditing-shared/scripts/` (T1.1) | Frontmatter contract verification |
| `log_state_transition.py` | `.claude/skills/auditing-shared/scripts/` (T1.2) | State-transition log integrity |
| `detect_stubs.py` | `.claude/skills/auditing-shared/scripts/` (T1.3) | Stub-pattern detection (Q-CC-2 path-aware) |
| `run_phase_checks.py` | `.claude/skills/auditing-shared/scripts/` (T1.4) | Phase-quality coordinator |
| `check_pipeline_discipline.py` | `.claude/skills/auditing-shared/scripts/` (T1.5) | Discipline-5 mechanical check |
| `audit_codespaces.py` (stub) | `.claude/skills/auditing-codespaces/scripts/` (T1.6) | Stub-vs-real distinction (Q-CC-4) |
| `audit_workflow.py` (relocated) | `.claude/skills/auditing-github-actions/scripts/` (T2.1) | GHA workflow audit |
| 5 templates | `.claude/skills/KB-documentation-criteria/references/templates/` (T5.*) | Schema verification fixtures |
| 5 execute-* agent files | `.claude/agents/` (T3.*) | Agent-body and frontmatter verification |
| Test scaffolding | `working/feature/_smoke_test_execution_pipeline/` (T6.2) | E2E integration substrate |

**No external frameworks required**. All tests run with stock `python3` (3.8+) and standard library; YAML parsing via `pyyaml` (already used in the project); JSON validation via standard library. Static-parse tests use `grep` / file-reads with no test-runner dependency. Integration tests use `subprocess.run` against the canonical script paths. The Plan's T1.7 smoke-test pattern is the template for assertion authoring.

**Fixture catalog needed** (authored alongside test implementation):
- 5 frontmatter-validator fixtures (one per FR-6 negative-path AC-FR-6-b case)
- 25 doc_type fixtures (one per enum value per ADR-0032)
- 1 historical-date fixture (predates feature deployment date) for AT-058
- 9 depth-classifier fixtures (one per Level 0..Level 8) for AT-018
- 1 impl-file stub fixture + 1 test-file stub fixture (Q-CC-2 path-aware) for AT-008 + AT-013
- T6.2 smoke-test scaffolding with 5 intentional content items (clean / fixable / stub / cap-reaching / Posture-B-sensitivity)

## CI Execution Plan

This feature is single-layer Claude Code; no external CI is in scope. Test execution is interactive (project owner runs at gates) per the project's interactive-pipeline posture. The breakdown by execution timing:

| Test category | Timing | Tests | Notes |
|---|---|---|---|
| **PR-fast** (≤30s total; runs at every gate boundary) | Per gate (every transition T1..T12) | All structural tests (AT-001 through AT-002, AT-018 through AT-023, AT-029, AT-035 through AT-038, AT-039, AT-041, AT-043, AT-046, AT-048, AT-051, AT-054 through AT-056, AT-059, AT-062, AT-067, AT-069, AT-070, AT-072, AT-073, AT-074, AT-075, AT-076, AT-077) — approximately 38 static tests | Run via the existing `validate_pipeline_frontmatter.py` invocation at every gate; the FR-6 validator embeds these checks |
| **Phase-quality** (≤5min total; runs at T8 phase_quality_pass) | At T8 | Contract / config tests (AT-029 through AT-034, AT-040, AT-042, AT-044, AT-045, AT-047, AT-049, AT-050, AT-053, AT-057, AT-058, AT-060, AT-061, AT-063, AT-065, AT-068, AT-071, AT-078) — approximately 25 tests | Run via `run_phase_checks.py` orchestration |
| **End-to-end smoke** (≤30min; runs once per feature implementation cycle, in T6.2) | T6.2 | AT-003, AT-004, AT-005 through AT-017, AT-024 through AT-028, AT-064, AT-066 — approximately 15 integration tests | Single orchestrator-spawn against synthetic scaffolding |
| **Property-based** (≤2min; runs at T6.2) | T6.2 | AT-077 (14-transition invariant), AT-078 (T0/T13 schema property) | Verifies invariants across all 14 transitions |

**Triggering**: PR-fast tests fire automatically via the orchestrator's per-gate validator invocation. Phase-quality tests fire when `run_phase_checks.py` invokes its 7-dimension aggregate. E2E smoke fires on T6.2 (rollout phase) and on any subsequent feature's first-execution dry run.

## Determinism and Isolation Commitments

Per KB-general-coding-principles Principle X (deterministic assertions; test isolation):

1. **Time-of-day independence**: No test depends on wall-clock time except AT-058 (historical-date scoping), which uses fixed fixture timestamps; no test compares against `now()`.
2. **Random-seed independence**: No test depends on PRNG output; all fixtures are pre-canned.
3. **Filesystem isolation**: Integration tests run against the synthetic `working/feature/_smoke_test_execution_pipeline/` scaffolding directory; no test writes to or reads from real feature archives.
4. **Process isolation**: Each integration test spawns a fresh `subprocess.run` for the script under test; no test depends on shared in-memory state from a prior test.
5. **Replayability**: Per Blueprint Risk-1 mitigation, the orchestrator's run is replayable — given identical input scaffolding, the resulting `state-transitions.log` and `pipeline-run-summary.json` are byte-equivalent (modulo timestamps, which are recorded but not asserted against in the integration tests).
6. **Flake-risk surface**:
   - AT-053 (budget exhaustion at cycle 4) relies on the reconciler's cycle counter; the counter is documented to increment deterministically per T4/T10 transitions per invariant 10. Should be flake-free.
   - AT-066 / AT-064 (end-to-end) depend on T6.2 scaffolding being byte-stable across runs. The scaffolding is committed to the repo; no flake risk.
   - AT-077 invariant tests verify property-based holds; should the invariant be violated, the failure is deterministic (not flaky).

## Open Items (for Cross-Artifact Audit)

The following AC-to-test mappings required judgment calls and are surfaced explicitly here for Cross-Artifact Audit verification:

1. **AT-023 ↔ AC-FR-4-f**: The PRD requires "An ADR shall be authored documenting the depth classifier's semantics and the dispatch matrix." The Blueprint's resolution publishes the dispatch matrix in §Contract 4 (Blueprint itself) AND references ADR-0035 (Skill-binding convention) + the depth-classifier substrate in cc-design.md. **Judgment call**: AT-023 verifies the ADR-substrate satisfies AC-FR-4-f, but a stricter reading would require a stand-alone ADR-NNNN-depth-classifier-and-dispatch-matrix.md. The Cross-Artifact Auditor should confirm the Blueprint's reading is intended.

2. **AT-037 ↔ AC-FR-7-c floor item "frontmatter-validation report"**: The Blueprint §AC-FR-7 floor coverage Path B disposition treats the frontmatter-validation report as satisfied by `validate_pipeline_frontmatter.py`'s inline script-output schema (T1.1) — NOT by a stand-alone template. **Judgment call**: This is the Plan's documented Path B; AT-037 honors it. The Cross-Artifact Auditor should confirm that the absence of a standalone `frontmatter-validation-report-template.md` is intended (per the bidirectional cross-reference verified by AT-074 + AT-075).

3. **AT-037 ↔ AC-FR-7-c floor item "execution-reconciliation log"**: The Blueprint Path B treats `pipeline-run-summary.json` as the canonical surface for the "execution-reconciliation log" floor item (per-feature-run aggregation). **Judgment call**: Same Path B disposition as #2 above. Cross-Artifact Auditor should verify intent.

4. **AT-053 (budget exhaustion) requires the smoke-test scaffolding to contain a fixture that demonstrably reaches cycle 4**: The Plan's T6.2 scaffolding item (iv) is described as "a phase-quality finding that reaches the 4-cycle cap". **Judgment call**: The exact mechanism of "reaches cap" is implementation-defined — the scaffolding must trigger 4 unconverged cycles. This is documented but not test-spec-driven; the test implementation must construct the fixture. Cross-Artifact Auditor should verify the test-task decomposition surfaces this concretely.

5. **T6.1 Posture-A vs Posture-B test coverage asymmetry**: AT-073 verifies the Plan v2 surfaces the postures explicitly. **However**: if Posture B is selected at execution time, the ~20+ planning-side agent author-prompt edits need their own per-agent verification — AT-073 does NOT enumerate one test per edited agent. **Judgment call**: This is consistent with the Blueprint's Migration Strategy "Incremental rollout option" and the Plan's Posture-A default; per-agent verification would be a follow-on feature's test concern. Cross-Artifact Auditor should confirm.

6. **Bash widening (I-AA-602) test AT-067 + AT-068 verifies both the declared form and the validator's acceptance**: The pair captures both the offensive (the agent declares unrestricted Bash) and defensive (the validator does not reject it) sides. **Judgment call**: This pair is complete; no additional negative-path test (e.g., a fixture declaring `Bash(python3:*)` triggering validator rejection) is needed, because the Plan documents per-agent Bash narrowing as agent-by-agent decision per cc-design.md — not a universal restriction.

7. **ADR-0035 single-script criterion (AT-070)**: The criterion is documented in ADR-0035 + Blueprint Component 2. **Judgment call**: AT-070 verifies code-producer's non-binding; it does NOT verify the precise wording of the single-script criterion in ADR-0035. The Cross-Artifact Auditor should confirm that the ADR-substrate of "auditing-shared binding is opt-in and depends on materially-multi-script dependency" is preserved across Blueprint, ADR-0035, and the agent body.

8. **AC-OP-2 dispatch routing**: AC-OP-2 specifies "A finding from check_pipeline_discipline.py (e.g., a stage-by-number reference in an artifact) shall route through the dispatch matrix at Level 0 (auto-fixable) by default; Level 1 if context-sensitive." AT-065 verifies the script emits both severities. **Judgment call**: The downstream dispatch routing through the depth classifier (verified at AT-018, AT-019) is assumed to apply uniformly; AT-065 does NOT chain through to end-to-end routing of the discipline finding. This is consistent with the test pyramid (AT-018/19 cover the dispatch matrix at the contract level; AT-065 covers the discipline-check at the script-output level).

These items are NON-BLOCKING for the test specifications above; they are surfaced for the Cross-Artifact Auditor's awareness. They do NOT trigger reconciliation per ADR-0033 / ADR-0029 unless the Auditor identifies a substantive misalignment.

## Update History

- **v1.0.0** (2026-05-22T23:50:00Z) — Initial authoritative authoring per test-acceptance-author dispatch. Produced 78 test specifications covering all 63 ACs (60 PRD + 3 Operational) plus 7 v5-introduced items with 12 dedicated tests (AT-067 through AT-078). All ADR-0034 correction-surface tests (AT-034, AT-052, AT-072) cite ADR-0017 forward, NOT ADR-0021. Document declares `doc_type: acceptance-tests` per ADR-0032 Change 4 universal-required field. No prior version superseded (this is the first authoring).
