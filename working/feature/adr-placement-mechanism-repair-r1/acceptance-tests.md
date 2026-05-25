---
id: AT-adr-placement-mechanism-repair-r1
version: 1.0.0
status: draft
doc_type: acceptance-tests
feature_slug: adr-placement-mechanism-repair-r1
derived_from:
  - working/feature/adr-placement-mechanism-repair-r1/prd-v1.md
  - working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md
prd_version: 1.0.2
blueprint_version: 1.2.0
plan_version: 1.0.1
scope_class: FULL
layer_scope: ["claude-code"]
total_tests: 76
total_acs_covered: 60
generated: 2026-05-25T03:00:00Z
generated_by: test-acceptance-author
---

# Acceptance Tests — ADR Placement Mechanism Repair

## Contents

- [x] Purpose
- [x] Sources
- [x] Test taxonomy and layer notes
- [x] Coverage matrix (AC ↔ Test ID)
- [x] Test specifications
- [x] Test infrastructure required
- [x] CI / execution plan
- [x] Determinism and isolation commitments
- [x] Open coverage gaps
- [x] Update History

## Purpose

This document specifies the concrete acceptance-test set that maps every PRD + Blueprint EARS-format Acceptance Criterion to one or more executable tests. Each test names: test type, preconditions, steps (commands or actions), expected outcome, layer of verification (L1 mechanical / L2 structural / L3 semantic per the Plan's discipline), and the AC(s) it satisfies.

Author guidance: this is a CC-only / tooling-repair feature. Most tests are **structural** (grep/diff/ls/file-content assertions), **integration** (subprocess invocation against the real repo), or **empirical-run** (full pipeline simulation). The test pyramid for this feature is inverted relative to a product feature: there is no UI to E2E and no service to load-test, but there are high-stakes integration tests (three-surface enforcement; 368-occurrence bare-ID disambiguation) where weak coverage would directly enable regression.

## Sources

- **PRD**: `working/feature/adr-placement-mechanism-repair-r1/prd-v1.md` (v1.0.2). All AC IDs (AC-US-*, AC-FR-*, AC-OP-*, AC-NFR-*) inherited from this document.
- **Blueprint**: `working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md` (v1.2.0). Inherits PRD ACs and adds AC-CC-1 through AC-CC-7 plus AC-FR-8b-1.1, AC-FR-8d-2.1, AC-FR-9-b.1.
- **Plan** (context for L1/L2/L3 discipline + per-task-AC mapping): `working/feature/adr-placement-mechanism-repair-r1/plan-v1.md` (v1.0.1).
- **Authored ADRs** (constrain assertions): `adrs/ADR-0053-adr-renumbering-collision-resolution-algorithm.md`, `adrs/ADR-0054-canonical-helper-three-surface-enforcement-pattern.md`, `adrs/ADR-0055-archive-wins-consolidation-policy-for-version-divergent-collisions.md` (all v1.0.1).
- **Codebase analysis**: `working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json` (schema v1.1.0). IN-001 through IN-012 are the load-bearing fact set.

## Test taxonomy and layer notes

This feature uses six test types:

| Type | Definition | Example for this feature |
|---|---|---|
| **structural** | A grep / ls / diff / file-content assertion against the repo state. No code execution. Cheapest. | AC-FR-1-a (grep returns 0 matches) |
| **unit** | A Python function or behavior in isolation, exercised by a smoke test or test harness. | `validate_adr_placement.py --help` exits 0 |
| **integration** | Real subprocess invocation against the real repo, possibly with a controlled fixture; covers script-to-script handoffs. | `run_phase_checks.py` dispatches validator and folds findings into `validator` dimension |
| **empirical-run** | A controlled simulation or live invocation of a multi-stage flow (e.g., orchestrator → composer → validator → reviewer). Tests an end-to-end pipeline behavior. | AC-OP-1 fresh feature-pipeline run probe |
| **negative-path** | A test that intentionally introduces a violation (e.g., writes `ADR-9999-fixture.md` to a non-canonical path) and confirms the system rejects it. Subset of integration; called out separately because of its security-net role. | AC-OP-4 three-surface block on negative fixture |
| **review-gate** | A test that invokes `shared-document-reviewer` (or another gate sub-agent) on a sample artifact and inspects its JSON output. | AC-FR-2-b reviewer does not flag canonical-only Blueprint |

**Layer of verification** values mirror the Plan's discipline:

- **L1 (mechanical)**: file exists; `grep` returns expected count; YAML/JSON parses. Seconds.
- **L2 (structural)**: file content matches expected shape; diff confirms expected change; per-task audit-log entry exists. Minutes.
- **L3 (semantic)**: end-to-end behavior; full pipeline or full-three-surface harness; the EARS AC's binding semantic check. Tens of minutes to hours.

Per-test "Layer of verification" is the lowest level at which the AC's binding claim is verified. Many tests have L1 + L2 + L3 verifications layered (matching the Plan's per-task verification structure); the Layer field below names the **load-bearing** layer for that test.

**Test pyramid posture**: for the validator script (FR-10-a), unit + integration tests carry the load; the three-surface integration tests (AC-FR-10-b/c/d) and the negative-path harness (AC-OP-4) are the binding semantic tests. Empirical-run tests (AC-OP-1) are reserved for the irreducibly end-to-end claims.

## Coverage matrix (AC ↔ Test ID)

Every AC enumerated in the Plan's Acceptance Test Cross-Reference table (60 unique ACs) maps to one or more tests below. ACs that are "Satisfied at Blueprint composition" or "Satisfied by design" are mapped to a structural test that confirms the Blueprint artifact contains the required content.

| AC ID | EARS form | Test ID(s) |
|---|---|---|
| AC-US-1-a | When | AT-001 |
| AC-US-1-b | When | AT-002 |
| AC-US-2-a | When | AT-003 |
| AC-US-2-b | When | AT-004 |
| AC-US-3-a | When | AT-005 |
| AC-US-3-b | When | AT-006 |
| AC-US-4-a | When | AT-007 |
| AC-US-4-b | When | AT-008 |
| AC-FR-1-a | When | AT-009 |
| AC-FR-1-b | When | AT-010 |
| AC-FR-2-a | When | AT-011 |
| AC-FR-2-b | When | AT-012 |
| AC-FR-3-a | When | AT-013 |
| AC-FR-3-b | When | AT-014 |
| AC-FR-4-a | When | AT-015 |
| AC-FR-4-b | Ubiquitous | AT-016 |
| AC-FR-5-a | Ubiquitous | AT-017 |
| AC-FR-5-b | Where | AT-018 |
| AC-FR-6-a | Ubiquitous | AT-019 |
| AC-FR-6-b | Ubiquitous | AT-020 |
| AC-FR-7-a | n/a (SUPERSEDED) | AT-021 |
| AC-FR-8a-1 | When | AT-022 |
| AC-FR-8a-2 | Where | AT-023 |
| AC-FR-8b-1 | When | AT-024 |
| AC-FR-8b-1.1 | Where + If-then | AT-025, AT-026 |
| AC-FR-8b-2 | When | AT-027, AT-028 |
| AC-FR-8c-1 | When | AT-029 |
| AC-FR-8c-2 | Where | AT-030 |
| AC-FR-8d-1 | When | AT-031, AT-032 |
| AC-FR-8d-2 | Ubiquitous | AT-033 |
| AC-FR-8d-2.1 | When | AT-034 |
| AC-FR-8d-3 | When | AT-035 |
| AC-FR-9-a | When | AT-036 |
| AC-FR-9-b | Ubiquitous | AT-037, AT-038 |
| AC-FR-9-b.1 | Ubiquitous (procedure) | AT-039, AT-040 |
| AC-FR-9-c | Ubiquitous | AT-041 |
| AC-FR-10-a | Ubiquitous | AT-042 |
| AC-FR-10-b | When | AT-043 |
| AC-FR-10-c | When | AT-044 |
| AC-FR-10-d | When | AT-045 |
| AC-FR-10-e | Where | AT-046 |
| AC-FR-10-f | When | AT-047 |
| AC-FR-11-a | When | AT-048 |
| AC-FR-11-b | Where | AT-049 |
| AC-FR-11-c | Ubiquitous | AT-050 |
| AC-CC-1 | When | AT-051 |
| AC-CC-2 | Where | AT-052 |
| AC-CC-3 | When | AT-053 |
| AC-CC-4 | Ubiquitous | AT-054 |
| AC-CC-5 | When | AT-055 |
| AC-CC-6 | When | AT-056 |
| AC-CC-7 | When | AT-057 |
| AC-OP-1 | When | AT-058 |
| AC-OP-2 | When | AT-059 |
| AC-OP-3 | When | AT-060 |
| AC-OP-4 | When | AT-061 |
| AC-OP-5 | When | AT-062 |
| AC-NFR-1-a | When | AT-063 |
| AC-NFR-1-b | When | AT-064 |
| AC-NFR-2-a | When | AT-065 |
| AC-NFR-3-a | When | AT-066 |
| AC-NFR-3-b | When | AT-067 |
| AC-NFR-4-a | When | AT-068 |
| AC-NFR-4-b | If-then | AT-069 |
| AC-NFR-5-a | When | AT-070 |
| AC-NFR-5-b | When | AT-071 |
| AC-NFR-6-a | When | AT-072 |
| AC-NFR-6-b | When | AT-073 (cross-references AT-072 + AT-061; primary verification is Architecture Audit) |
| AC-NFR-7-a | When | AT-074 |
| AC-NFR-7-b | If-then | AT-075 |
| AC-NFR-8-a | When | AT-076 |

**Test count by AC group**:
- AC-US-*: 8 ACs → 8 tests
- AC-FR-1 through AC-FR-7: 9 ACs → 9 tests (AC-FR-7-a is a slot retention; included as structural no-op)
- AC-FR-8 (sub-FRs a/b/c/d): 13 ACs → 14 tests (AC-FR-8b-1.1 splits into 2 tests; AC-FR-8d-1 splits into 2)
- AC-FR-9: 4 ACs → 6 tests (AC-FR-9-b splits into 2; AC-FR-9-b.1 splits into 2)
- AC-FR-10: 6 ACs → 6 tests
- AC-FR-11: 3 ACs → 3 tests
- AC-CC-*: 7 ACs → 7 tests
- AC-OP-*: 5 ACs → 5 tests
- AC-NFR-*: 14 (8 NFRs decomposed into AC-NFR-N-a/b): 14 tests

**Total tests**: 76 test entries (AT-001 through AT-076). Critical-path tests flagged in the per-spec table.

**Coverage gap analysis**: 0 ACs unmapped. Every PRD AC + every Blueprint-added AC maps to ≥1 test. AC-FR-7-a (SUPERSEDED) gets a structural test that asserts the slot remains documented but produces no behavior. See §Open coverage gaps for weak-coverage notes.

## Test specifications

Conventions used below:

- All grep commands assume invocation from the repo root unless noted.
- `migration-log.md` refers to `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` (the per-task audit substrate established by Plan T0.3).
- Commands shown in test steps are illustrative; final test implementation may use the project's preferred test harness (`smoke_test_auditing_shared.py` extension for Python-script tests; shell-based assertions for repo-state tests).
- `Plan-task` references link back to plan-v1.md so finalize-task-decomposer can derive test-implementation tasks.

---

### AT-001 — AC-US-1-a: Fresh pipeline run writes ADRs to canonical-root only

- **Maps to AC**: AC-US-1-a (CC)
- **EARS form**: When (event-driven)
- **Test type**: empirical-run
- **Layer of verification**: L3
- **Critical path**: yes (binds the user-story-level commitment for future pipeline runs)
- **Preconditions**:
  - All Phase 1 + Phase 4 + Phase 5 tasks complete (operator-file edits + validator authored + three surfaces wired).
  - `recipe-feature-pipeline/SKILL.md:273` carries the `default: "adrs/" per ADR-0036` annotation per T1.3.
  - Caller-side invocation provides no explicit `output_adrs_dir` override.
- **Steps** (AAA):
  1. (Arrange) Capture the orchestrator's parameter-resolution prose at SKILL.md:273 area; confirm the canonical-root default annotation is present.
  2. (Act) Simulate a Step-8 dispatch (per Plan T6.2 simulation): read SKILL.md Step 8 → confirm the canonical-root value would be passed to `design-composer` → invoke `validate_adr_placement.py` against the post-Phase-5 repo as a proxy for "no ADR has been authored to a non-canonical path".
  3. (Assert) The orchestrator's prescribed `output_adrs_dir` value equals `"adrs/"`; the validator returns exit 0 with empty findings.
- **Expected outcome**: `output_adrs_dir = "adrs/"` resolved by the orchestrator; validator exit code 0; validator JSON `verdict == "PASS"`.
- **Negative-path coverage**: AT-005 (negative-path packager test); AT-061 (full three-surface negative).
- **Data dependencies**: Post-Phase-5 repo state.
- **Determinism notes**: Validator's `elapsed_ms` is the only timing observable; orchestrator parameter resolution is deterministic.
- **Plan-task reference**: T6.2.

---

### AT-002 — AC-US-1-b: Three-surface enforcement blocks contrived feature-scoped write

- **Maps to AC**: AC-US-1-b (CC)
- **EARS form**: When
- **Test type**: negative-path (integration across 3 surfaces)
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**:
  - All three surfaces wired (Plan T5.1, T5.2, T5.3).
  - Validator authored (Plan T4.1).
- **Steps**:
  1. (Arrange) Write `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/` (contrived).
  2. (Act surface a) Invoke `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` (proxy for orchestrator Step-8 gate). Capture exit code + JSON.
  3. (Act surface b) Invoke `python3 .claude/skills/auditing-shared/scripts/run_phase_checks.py` with the post-fixture repo. Capture exit code + dimension rollup.
  4. (Act surface c) Invoke the packager's subprocess command (`python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py`) via the same allow-list grant the packager uses. Capture exit code + `packager-report.json` shape.
  5. (Cleanup) `git rm -rf working/feature/test-fixture/`.
  6. (Assert) All three surfaces return non-zero (exit 2 for the direct validator invocations; the `run_phase_checks.py` rollup shows `validator` dimension == BLOCK).
- **Expected outcome**: Each surface returns exit 2 + JSON `verdict == "BLOCK"` + findings[] entry citing `working/feature/test-fixture/adrs/ADR-9999-fixture.md` with `category == "feature-scoped"`.
- **Negative-path coverage**: This IS the negative-path test for AC-US-1-b; companion full-orchestrated test is AT-061.
- **Data dependencies**: Test fixture file; cleanup required to avoid polluting repo.
- **Determinism notes**: Fixture creation + cleanup must be atomic. If the test crashes mid-execution, the fixture must be cleaned up manually before re-running (orphaned fixture would falsify subsequent runs of any positive-path test).
- **Plan-task reference**: T6.7.

---

### AT-003 — AC-US-2-a: Reviewer does not flag canonical-only Blueprint

- **Maps to AC**: AC-US-2-a (CC)
- **EARS form**: When
- **Test type**: review-gate
- **Layer of verification**: L3
- **Preconditions**: Plan T1.2 complete (reviewer line 349 deleted).
- **Steps**:
  1. (Arrange) Select a representative Blueprint with canonical-only ADR references (this feature's own Blueprint v1.2.0 is the natural specimen).
  2. (Act) Invoke `shared-document-reviewer` on the Blueprint.
  3. (Assert) Reviewer JSON output contains zero entries with `issue.category == "adr-placement"` and zero with `issue.severity == "critical"` referencing ADR placement.
- **Expected outcome**: Reviewer JSON shows no ADR-placement flag.
- **Negative-path coverage**: N/A — the AC asserts a non-flag.
- **Data dependencies**: A canonical-only Blueprint sample. Post-feature Blueprint v1.2.0 itself qualifies.
- **Determinism notes**: Reviewer output may include other unrelated flags; the assertion is narrowed to ADR-placement category only.
- **Plan-task reference**: T6.1.

---

### AT-004 — AC-US-2-b: Four operator files express one consistent convention

- **Maps to AC**: AC-US-2-b (CC); also satisfies AC-OP-2 partially.
- **EARS form**: When
- **Test type**: structural (4-file read + cross-reference)
- **Layer of verification**: L2
- **Critical path**: yes (binds the foundational consistency claim)
- **Preconditions**: Plan T1.1–T1.4 complete.
- **Steps**:
  1. (Arrange) Identify the four operator files: `.claude/agents/finalize-deliverable-packager.md`, `.claude/agents/shared-document-reviewer.md`, `.claude/agents/design-composer.md`, `.claude/skills/recipe-feature-pipeline/SKILL.md`.
  2. (Act) For each file: `grep -n "dual-location" <file>` (expect 0); `grep -n "ADR-0036" <file>` (expect ≥1 for files touching the convention); read the ADR-placement-touching sections and verify they describe canonical-only.
  3. (Assert) Across all four files: zero "dual-location" matches; every file that mentions the convention cites ADR-0036; no file contradicts another.
- **Expected outcome**: `grep -rn "dual-location" .claude/agents/ .claude/skills/recipe-feature-pipeline/` returns zero matches. Reading the four files in sequence reveals no contradictions.
- **Negative-path coverage**: N/A — invariant.
- **Data dependencies**: Post-Phase-1 repo state.
- **Determinism notes**: Pure grep + read; fully deterministic.
- **Plan-task reference**: T1.5, T6.1.

---

### AT-005 — AC-US-3-a: Packager passes on clean-canonical feature

- **Maps to AC**: AC-US-3-a (CC)
- **EARS form**: When
- **Test type**: integration
- **Layer of verification**: L3
- **Preconditions**: Plan T1.1 + T5.3 complete (packager's old prose deleted, validator-call wired).
- **Steps**:
  1. (Arrange) Use the post-Phase-5 repo (no off-canonical ADRs present).
  2. (Act) Invoke the packager's validator-call: `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py`.
  3. (Assert) Exit code 0; `packager-report.json` (or equivalent finalize-time output) contains no BLOCKER finding under `category == "adr-placement"`; no PKG-BLOCKER-001 string anywhere in the report.
- **Expected outcome**: Packager passes; zero ADR-placement BLOCKERs.
- **Negative-path coverage**: AT-006.
- **Determinism notes**: Pure validator invocation; deterministic.
- **Plan-task reference**: T5.3, T6.2.

---

### AT-006 — AC-US-3-b: Packager raises BLOCKER on feature whose ADRs include non-canonical entry

- **Maps to AC**: AC-US-3-b (CC)
- **EARS form**: When
- **Test type**: negative-path
- **Layer of verification**: L3
- **Preconditions**: Plan T5.3 complete (packager wired to validator).
- **Steps**:
  1. (Arrange) Write `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/`.
  2. (Act) Invoke packager subprocess: `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py`.
  3. (Assert) Exit code 2; JSON `verdict == "BLOCK"`; finding entry with `path == "working/feature/test-fixture/adrs/ADR-9999-fixture.md"` and `category == "feature-scoped"`.
  4. (Cleanup) Remove the fixture file.
- **Expected outcome**: Packager raises BLOCKER via the FR-10 validator.
- **Plan-task reference**: T6.7 (subset).

---

### AT-007 — AC-US-4-a: Future-run orchestrator passes canonical-root by default

- **Maps to AC**: AC-US-4-a (CC)
- **EARS form**: When
- **Test type**: structural + empirical-run
- **Layer of verification**: L2 (structural prose check) + L3 (simulation)
- **Preconditions**: Plan T1.3 complete.
- **Steps**:
  1. (Arrange) Read `recipe-feature-pipeline/SKILL.md` near line 273.
  2. (Act) Verify the `output_adrs_dir` parameter annotation reads `default: "adrs/" per ADR-0036` (or substantively equivalent).
  3. (Act-2 — simulation) Per Plan T6.2 simulation: confirm the orchestrator's documented behavior when no override is supplied is to pass `"adrs/"`.
  4. (Assert) Parameter description matches the FR-3 contract.
- **Expected outcome**: `grep -n "default.*adrs/" .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥1 match near line 273 with the ADR-0036 citation.
- **Plan-task reference**: T1.3, T6.2.

---

### AT-008 — AC-US-4-b: All audited skills present canonical-only as the only path

- **Maps to AC**: AC-US-4-b (CC)
- **EARS form**: When
- **Test type**: structural (sweep across audited skill files)
- **Layer of verification**: L2
- **Preconditions**: Plan T5.4 + T5.5 + T5.6 complete (all 8 file-level skill remediations landed).
- **Steps**:
  1. (Arrange) Enumerate audited skill files from Blueprint §Skill audit table.
  2. (Act) For each file in the in-scope list: `grep -n "working/feature/.*/adrs/" <file>` (expect 0 outside legitimate audit-trail contexts).
  3. (Assert) No audited skill describes feature-scoped placement as a permitted path; every example path uses `adrs/ADR-NNNN-*` form.
- **Expected outcome**: Combined grep across the 5+ audited skill families returns zero matches for `working/feature/<slug>/adrs/` paths in normative prose. Test acknowledges that audit-trail file contexts (per Blueprint §Skill audit table) are excluded.
- **Plan-task reference**: T5.4, T5.5, T5.6, T6.8.

---

### AT-009 — AC-FR-1-a: Packager file no longer contains dual-location BLOCKER prose

- **Maps to AC**: AC-FR-1-a (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T1.1 complete.
- **Steps**:
  1. (Act) `grep -n "dual-location" .claude/agents/finalize-deliverable-packager.md`.
  2. (Assert) Returns zero matches.
- **Expected outcome**: Zero matches.
- **Determinism notes**: Pure grep; deterministic.
- **Plan-task reference**: T1.1.

---

### AT-010 — AC-FR-1-b: PKG-BLOCKER-001 does not fire on canonical-only feature; replacement validator passes

- **Maps to AC**: AC-FR-1-b (CC)
- **EARS form**: When
- **Test type**: integration
- **Layer of verification**: L3
- **Preconditions**: Plan T1.1 + T5.3 complete.
- **Steps**: See AT-005 steps.
- **Expected outcome**: Packager exits with no PKG-BLOCKER-001 entry; FR-10 validator returns exit 0.
- **Plan-task reference**: T1.1, T5.3, T6.2.

---

### AT-011 — AC-FR-2-a: Reviewer file no longer contains line-349 dual-location check

- **Maps to AC**: AC-FR-2-a (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T1.2 complete.
- **Steps**:
  1. (Act) `grep -n "dual-location" .claude/agents/shared-document-reviewer.md`.
  2. (Assert) Returns zero matches.
- **Expected outcome**: Zero matches.
- **Plan-task reference**: T1.2.

---

### AT-012 — AC-FR-2-b: Reviewer does not flag canonical-only placement as violation

- **Maps to AC**: AC-FR-2-b (CC)
- **EARS form**: When
- **Test type**: review-gate
- **Layer of verification**: L3
- **Preconditions**: Plan T1.2 complete; AT-003 covers the same assertion.
- **Steps**: See AT-003.
- **Expected outcome**: Reviewer JSON contains no `issue.category == "adr-placement"` entry.
- **Plan-task reference**: T6.1.

---

### AT-013 — AC-FR-3-a: Orchestrator passes canonical-root when no override supplied

- **Maps to AC**: AC-FR-3-a (CC)
- **EARS form**: When
- **Test type**: structural + empirical-run
- **Layer of verification**: L2 + L3
- **Preconditions**: Plan T1.3 complete.
- **Steps**:
  1. (Act-L2) `grep -n "default.*adrs/" .claude/skills/recipe-feature-pipeline/SKILL.md` near line 273.
  2. (Act-L3) Per Plan T6.2 simulation: confirm the orchestrator passes `"adrs/"` to `design-composer` when no explicit `output_adrs_dir` is supplied.
  3. (Assert) Both checks pass.
- **Expected outcome**: SKILL.md prose mandates canonical-root default; simulation confirms behavior.
- **Plan-task reference**: T1.3, T6.2.

---

### AT-014 — AC-FR-3-b: Orchestrator forwards explicit caller-supplied override unmodified

- **Maps to AC**: AC-FR-3-b (CC)
- **EARS form**: When
- **Test type**: structural (prose check) + integration (if simulation supports override-mode)
- **Layer of verification**: L2
- **Preconditions**: Plan T1.3 complete.
- **Steps**:
  1. (Act) Read SKILL.md at line 273 area; verify the prose specifies pass-through fidelity: "if caller passes `output_adrs_dir` explicitly, orchestrator forwards unmodified".
  2. (Act-2 — if executable) Construct a test simulation where the caller supplies `output_adrs_dir = "test-only/path/"`; confirm the orchestrator passes that value unmodified.
  3. (Assert) Prose check passes; simulation (if run) shows pass-through fidelity.
- **Expected outcome**: SKILL.md describes pass-through fidelity; simulation confirms.
- **Plan-task reference**: T1.3.

---

### AT-015 — AC-FR-4-a: design-composer.md cites ADR-0036 at output_adrs_dir parameter

- **Maps to AC**: AC-FR-4-a (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T1.4 complete.
- **Steps**:
  1. (Act) `grep -cn "ADR-0036" .claude/agents/design-composer.md`.
  2. (Assert) ≥3 matches (one per the three anchor lines 48, 129, 187 per IN-007) plus ≥1 in the new "Test-only override" subsection.
- **Expected outcome**: ≥4 ADR-0036 references in design-composer.md.
- **Plan-task reference**: T1.4.

---

### AT-016 — AC-FR-4-b: design-composer.md documents the test-only override mechanism

- **Maps to AC**: AC-FR-4-b (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Plan T1.4 complete.
- **Steps**:
  1. (Act) `grep -n "Test-only override" .claude/agents/design-composer.md`.
  2. (Act-2) Read the matched subsection; verify it describes the override surface (same `output_adrs_dir` parameter; test-harness or contrived caller).
  3. (Assert) Subsection exists; the override surface is named.
- **Expected outcome**: Test-only override subsection present and describes the override mechanism.
- **Plan-task reference**: T1.4.

---

### AT-017 — AC-FR-5-a: `output_adrs_dir` parameter is not eliminated

- **Maps to AC**: AC-FR-5-a (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T1.4 complete.
- **Steps**:
  1. (Act) `grep -cn "output_adrs_dir" .claude/agents/design-composer.md .claude/skills/recipe-feature-pipeline/SKILL.md`.
  2. (Assert) ≥1 match in each file (parameter still present, not removed).
- **Expected outcome**: Parameter retained in both files.
- **Plan-task reference**: T1.4 (composer file); T1.3 (SKILL.md).

---

### AT-018 — AC-FR-5-b: Explicit caller override is honored

- **Maps to AC**: AC-FR-5-b (CC)
- **EARS form**: Where (configuration-gated)
- **Test type**: structural + integration (if override-mode simulation supported)
- **Layer of verification**: L2
- **Preconditions**: Plan T1.4 complete.
- **Steps**: See AT-014; same semantic check applied from the design-composer side.
- **Expected outcome**: design-composer's prose describes override-honor; simulation (if run) confirms.
- **Plan-task reference**: T1.4.

---

### AT-019 — AC-FR-6-a: Blueprint enumerates every off-canonical ADR with classification

- **Maps to AC**: AC-FR-6-a (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural (Blueprint content check)
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read `blueprint-v1.md` §Existing Codebase Analysis / Fact Disposition Table and §Design / Migration map.
  2. (Assert) Every off-canonical ADR enumerated by codebase-analysis.json IN-001 through IN-004 appears in the Blueprint's Migration map with a classification (byte-identical-dedupe / status-lift / numbering-collision / feature-scoped-relocation / legacy-archive: no-collision / archive-wins / canonical-wins / canonical-only).
- **Expected outcome**: All Migration-map entries enumerated; cross-reference to IN-001 through IN-004 is verifiable.
- **Plan-task reference**: T0.1.

---

### AT-020 — AC-FR-6-b: Blueprint documents migration disposition per FR-8 sub-phase

- **Maps to AC**: AC-FR-6-b (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read Blueprint §Design / Migration map; confirm sub-tables exist for FR-8a, FR-8b (status-lift + renumber), FR-8c, FR-8d (4 sub-procedures).
  2. (Assert) Every ADR enumerated in §AT-019 has a disposition (dedupe / git mv / archive / consolidate-with-suffix / delete-with-git-history).
- **Expected outcome**: All dispositions documented; no TBDs.
- **Plan-task reference**: T0.1.

---

### AT-021 — AC-FR-7-a: SUPERSEDED slot retained for traceability

- **Maps to AC**: AC-FR-7-a (CC)
- **EARS form**: n/a (SUPERSEDED marker)
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: PRD v1.0.2 present.
- **Steps**:
  1. (Act) `grep -n "FR-7.*SUPERSEDED" .` in PRD.
  2. (Assert) The FR-7 row exists, marked SUPERSEDED; no behavior implied.
- **Expected outcome**: Slot retained.
- **Plan-task reference**: N/A — Plan AC mapping marks as "N/A — slot retained".

---

### AT-022 — AC-FR-8a-1: 12 byte-identical duplicates deleted; canonicals retained

- **Maps to AC**: AC-FR-8a-1 (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Critical path**: yes (Phase 2a binding mass)
- **Preconditions**: Plan T2a.1 complete.
- **Steps**:
  1. (Act) For each of 12 IDs (0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043): `ls working/feature/{audit-machinery-fixes-r1,pipeline-skill-design-fixes-r1,audit-findings-remediation-r1,devcontainer-mcp-provisioning-r1}/adrs/ADR-NNNN-*.md` → expect zero matches.
  2. (Act-2) For each of 12 IDs: `ls adrs/ADR-NNNN-*.md` → expect 1 match.
  3. (Assert) 12 feature-scoped copies absent; 12 canonical copies present.
- **Expected outcome**: 12 deletions confirmed; 12 canonicals retained.
- **Plan-task reference**: T2a.1.

---

### AT-023 — AC-FR-8a-2: Per-ADR byte-equality verification logged in migration-log

- **Maps to AC**: AC-FR-8a-2 (CC)
- **EARS form**: Where
- **Test type**: structural (audit-log check)
- **Layer of verification**: L2
- **Preconditions**: Plan T2a.1 complete; `migration-log.md` populated.
- **Steps**:
  1. (Act) Read `working/feature/adr-placement-mechanism-repair-r1/migration-log.md`.
  2. (Assert) 12 per-ADR entries exist, each with a byte-equality check timestamp and a deletion timestamp.
- **Expected outcome**: 12 audit entries present.
- **Plan-task reference**: T2a.1.

---

### AT-024 — AC-FR-8b-1: ADR-0024 dedupes with status precedence (Accepted retained, body unchanged)

- **Maps to AC**: AC-FR-8b-1 (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T2b.1 complete.
- **Steps**:
  1. (Act) `ls working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md` → expect zero matches.
  2. (Act-2) `ls adrs/ADR-0024-*.md` → expect 1 match.
  3. (Act-3) `grep -n "^status:" adrs/ADR-0024-*.md` → expect "Accepted" value.
  4. (Assert) Feature-scoped copy deleted; canonical retained at Accepted status.
- **Expected outcome**: ADR-0024 exists at canonical only; status Accepted.
- **Plan-task reference**: T2b.1.

---

### AT-025 — AC-FR-8b-1.1 (happy path): `diff` excluding frontmatter `status:` confirms no body divergence

- **Maps to AC**: AC-FR-8b-1.1 (CC) — fail-safe operationalization
- **EARS form**: Where (procedure-gated)
- **Test type**: structural (audit-log check)
- **Layer of verification**: L2
- **Preconditions**: Plan T2b.1 complete; migration-log entry for ADR-0024.
- **Steps**:
  1. (Act) Read `migration-log.md` ADR-0024 entry.
  2. (Assert) Disposition recorded as "dedupe-clean" (no fail-safe triggered); or, if "fail-safe-archive" triggered, the next test (AT-026) covers it.
- **Expected outcome**: Disposition recorded; if dedupe-clean, no archival file expected.
- **Plan-task reference**: T2b.1.

---

### AT-026 — AC-FR-8b-1.1 (fail-safe path): Non-frontmatter divergence triggers archival

- **Maps to AC**: AC-FR-8b-1.1 (CC) — fail-safe-archive case
- **EARS form**: If-then
- **Test type**: structural (conditional — only applies if Discovery's "status-lift only" claim is wrong)
- **Layer of verification**: L2
- **Preconditions**: Plan T2b.1 triggers fail-safe (only if non-frontmatter body line differs).
- **Steps**:
  1. (If — fail-safe was triggered) `ls adrs/superseded/ADR-0024-feature-scoped-body.md` → expect 1 file.
  2. (Then) Read the file; confirm provenance footer identifies originating feature folder + canonical-body-decision rationale.
  3. (Assert) Archival file present with provenance footer.
- **Expected outcome** (conditional): If triggered, archival file exists with provenance footer.
- **Negative-path coverage**: AT-025 is the happy-path companion.
- **Plan-task reference**: T2b.1.

---

### AT-027 — AC-FR-8b-2 (existence): ADR-0044/0045 renumbered to ADR-0051/0052 at canonical

- **Maps to AC**: AC-FR-8b-2 (CC) — renumber existence
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Critical path**: yes (binds renumber correctness per ADR-0053)
- **Preconditions**: Plan T2b.2 complete (sequenced last per ADR-0053).
- **Steps**:
  1. (Act) `ls adrs/ADR-0051-per-issue-folder-model.md adrs/ADR-0052-three-doctypes-preserved.md` → expect 2 files.
  2. (Act-2) `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-*.md working/feature/issue-capture-mechanism-r1/adrs/ADR-0045-*.md` → expect zero files.
  3. (Assert) Renumbered files exist at canonical; originals removed from feature folder.
- **Expected outcome**: Renumber executed.
- **Plan-task reference**: T2b.2.

---

### AT-028 — AC-FR-8b-2 (provenance): Renumbered ADRs carry `original_id` frontmatter

- **Maps to AC**: AC-FR-8b-2 (CC) — provenance frontmatter
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T2b.2 complete.
- **Steps**:
  1. (Act) `grep -n "original_id: ADR-0044" adrs/ADR-0051-*.md`.
  2. (Act-2) `grep -n "original_id: ADR-0045" adrs/ADR-0052-*.md`.
  3. (Act-3) Confirm `id:` frontmatter on each renumbered file equals the new canonical ID (`ADR-0051`, `ADR-0052`).
  4. (Assert) All three asserts pass.
- **Expected outcome**: Provenance fields and updated `id:` confirmed.
- **Plan-task reference**: T2b.2.

---

### AT-029 — AC-FR-8c-1: ADRs 0046–0050 at canonical with Git history preserved

- **Maps to AC**: AC-FR-8c-1 (CC)
- **EARS form**: When
- **Test type**: structural + integration (`git log --follow`)
- **Layer of verification**: L2 + L3
- **Preconditions**: Plan T2c.1 complete.
- **Steps**:
  1. (Act-L1) `ls adrs/ADR-{0046,0047,0048,0049,0050}-*.md` → expect 5 files.
  2. (Act-L1-2) `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}-*.md` → expect zero files.
  3. (Act-L3) For each of the 5 IDs: `git log --follow adrs/ADR-NNNN-*.md` → confirm history traces back to `working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN-*.md`.
  4. (Assert) All checks pass.
- **Expected outcome**: 5 files relocated; Git history preserved per `git mv` (NFR-5).
- **Plan-task reference**: T2c.1.

---

### AT-030 — AC-FR-8c-2: Tombstone redirect notes in originating feature folder

- **Maps to AC**: AC-FR-8c-2 (CC)
- **EARS form**: Where
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Plan T2c.1 complete.
- **Steps**:
  1. (Act) `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}.tombstone` → expect 5 files.
  2. (Act-2) For each `.tombstone` file: read; confirm content matches the 3-line template ("# Moved" header + redirect prose + ADR-0036 citation).
  3. (Assert) 5 tombstones present and template-conformant.
- **Expected outcome**: 5 tombstones present; format consistent.
- **Plan-task reference**: T2c.1.

---

### AT-031 — AC-FR-8d-1 (archive empty + variants deleted): `adrs-migrated/` removed

- **Maps to AC**: AC-FR-8d-1 (CC) — directory removal
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Critical path**: yes (binds Phase 2d closure)
- **Preconditions**: Plan T2d.1–T2d.4 complete.
- **Steps**:
  1. (Act) `ls adrs-migrated/` → expect "No such file or directory".
  2. (Assert) Directory absent.
- **Expected outcome**: `adrs-migrated/` directory removed.
- **Plan-task reference**: T2d.4.

---

### AT-032 — AC-FR-8d-1 (final-variants at canonical with suffix policy)

- **Maps to AC**: AC-FR-8d-1 (CC) — final-variant placement + variant-deletion enumeration
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Plan T2d.1–T2d.4 complete.
- **Steps**:
  1. (Act-L1) `ls adrs/ADR-{0001..0006,0008..0018}-*.md` → expect 17 files at canonical (9 no-collision + 7 archive-wins + 1 canonical-wins; the 1 canonical-only = ADR-0007 is verified separately).
  2. (Act-L1-2) `git log --diff-filter=D --name-only HEAD~N..HEAD -- adrs-migrated/` → confirms all source files deleted across Phase 2d (where N covers the Phase 2d commits).
  3. (Act-L2) Confirm `-pre-naming-convention`, `-pre-template-migration`, and `-v1-superseded` variants do not exist anywhere in the repo (`git ls-files | grep -E "(pre-naming-convention|pre-template-migration|v1-superseded)"` returns zero matches).
  4. (Assert) Canonical population correct; variant deletions complete.
- **Expected outcome**: Canonical population per Blueprint §Architecture Overview; variant files removed.
- **Plan-task reference**: T2d.1–T2d.4.

---

### AT-033 — AC-FR-8d-2: Archive-wins frontmatter fields + superseded-canonical archival

- **Maps to AC**: AC-FR-8d-2 (CC)
- **EARS form**: Ubiquitous (applies to all 7 archive-wins cases)
- **Test type**: structural
- **Layer of verification**: L2
- **Critical path**: yes (binds ADR-0055 correctness)
- **Preconditions**: Plan T2d.2 complete.
- **Steps**:
  1. (Act) `ls adrs/superseded/ADR-{0011..0017}-pre-consolidation-canonical.md` → expect 7 files.
  2. (Act-2) For each of 7 IDs: `grep -n "superseded_by_consolidation: true" adrs/ADR-NNNN-*.md` → expect 1 match.
  3. (Act-3) For each of 7 IDs: `grep -n "superseded_canonical_archived_to: adrs/superseded" adrs/ADR-NNNN-*.md` → expect 1 match.
  4. (Act-4) For each of 7 superseded files: confirm provenance footer identifies pre-consolidation canonical version + this-feature slug + consolidation date.
  5. (Assert) All 7 cases: archive present + new canonical frontmatter fields + provenance footer.
- **Expected outcome**: 7 archive-wins cases fully realized.
- **Plan-task reference**: T2d.2.

---

### AT-034 — AC-FR-8d-2.1: ADR-0007 v1-superseded variant deleted (canonical-only-procedure glob)

- **Maps to AC**: AC-FR-8d-2.1 (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T2d.4 complete.
- **Steps**:
  1. (Act) `ls adrs-migrated/ADR-0007*` → expect "No such file or directory" (parent dir removed).
  2. (Act-2) Confirm via Git history: `git log --diff-filter=D --name-only HEAD~N..HEAD -- adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-superseded.md` shows deletion.
  3. (Act-3) `ls adrs/ADR-0007-code-graph-mcp-selection.md` → expect 1 file (canonical untouched).
  4. (Assert) v1-superseded variant deleted; canonical untouched.
- **Expected outcome**: Variant deleted; canonical untouched.
- **Plan-task reference**: T2d.4.

---

### AT-035 — AC-FR-8d-3: Validator does not allowlist `adrs-migrated/` post-Phase-2d

- **Maps to AC**: AC-FR-8d-3 (CC)
- **EARS form**: When
- **Test type**: structural (validator script inspection)
- **Layer of verification**: L1
- **Preconditions**: Plan T4.1 + T2d.4 complete.
- **Steps**:
  1. (Act) `grep -n "adrs-migrated" .claude/skills/auditing-shared/scripts/validate_adr_placement.py` → expect zero matches (no hard-coded allowlist).
  2. (Act-2) Read the validator's allowlist default; confirm it is empty.
  3. (Act-3) Read Blueprint §Allowlist enumeration; confirm `adrs-migrated/` is not enumerated.
  4. (Assert) No allowlist entry for `adrs-migrated/`.
- **Expected outcome**: No allowlist mention of `adrs-migrated/`; default policy is canonical-only.
- **Plan-task reference**: T2d.4, T6.4.

---

### AT-036 — AC-FR-9-a: Zero in-repo references to former ADR paths

- **Maps to AC**: AC-FR-9-a (CC)
- **EARS form**: When
- **Test type**: structural (sweep)
- **Layer of verification**: L2
- **Critical path**: yes (binds sweep completeness)
- **Preconditions**: Plan T3.2 + T3.3 complete.
- **Steps**:
  1. (Act-path-form) `grep -rn "working/feature/.*adrs/ADR-" --include="*.md" .` excluding `.tombstone` files, `migration-log.md`, per-task execution result files, this Plan, the Blueprint cycle-1/cycle-2 prose, and ADRs 0053/0054/0055.
  2. (Act-archive-paths) `grep -rn "adrs-migrated/" --include="*.md" .` with the same exclusions.
  3. (Assert) Both grep counts equal 0.
- **Expected outcome**: Zero remaining references at the 14 + 18 = 32 known former paths.
- **Plan-task reference**: T3.2, T3.3, T6.6.

---

### AT-037 — AC-FR-9-b (path-only constraint): Path-form edits change only path tokens

- **Maps to AC**: AC-FR-9-b (CC) — path-only constraint
- **EARS form**: Ubiquitous
- **Test type**: structural (diff inspection)
- **Layer of verification**: L2
- **Preconditions**: Plan T3.2 complete.
- **Steps**:
  1. (Act) For each of the 32 path-form edits: read `migration-log.md` Phase-3 section entry; confirm the entry shows the diff was path-only (no semantic edits).
  2. (Assert) All 32 entries confirm path-only diff.
- **Expected outcome**: 32 entries; all path-only.
- **Plan-task reference**: T3.2.

---

### AT-038 — AC-FR-9-b (368 bare-ID sweep): Per-occurrence disposition for renumbered IDs

- **Maps to AC**: AC-FR-9-b (CC) — expanded bare-ID sweep per AA-011
- **EARS form**: Ubiquitous
- **Test type**: structural (inventory check)
- **Layer of verification**: L2
- **Critical path**: yes (binds the AA-011 user binding decision)
- **Preconditions**: Plan T3.3 complete; `bare-id-inventory.json` populated.
- **Steps**:
  1. (Act) Load `working/feature/adr-placement-mechanism-repair-r1/bare-id-inventory.json`.
  2. (Act-2) Count entries; expect ≥368 occurrences (ADR-0044: 223; ADR-0045: 145 per IN-008 expansion).
  3. (Act-3) For each entry: confirm `disposition` field is one of (renumbered-to-0051 / renumbered-to-0052 / preserved / user-escalation-resolved); no TBDs.
  4. (Assert) All 368 entries dispositioned.
- **Expected outcome**: Inventory fully populated; no TBD entries.
- **Plan-task reference**: T3.3.

---

### AT-039 — AC-FR-9-b.1: Baseline-heuristic procedure applied per-occurrence

- **Maps to AC**: AC-FR-9-b.1 (CC) — heuristic application + rationale recording
- **EARS form**: Ubiquitous (procedure)
- **Test type**: structural (inventory + per-task execution result check)
- **Layer of verification**: L2
- **Preconditions**: Plan T3.3 complete.
- **Steps**:
  1. (Act) For each entry in `bare-id-inventory.json`: confirm `rationale` field is one of (heuristic-clear / heuristic-confirmed / user-escalation-resolved).
  2. (Act-2) Spot-check 10 entries: confirm the rationale is plausibly applied (e.g., an entry inside `working/feature/issue-capture-mechanism-r1/*` has rationale "heuristic-clear" with disposition matching the feature-meaning).
  3. (Assert) All entries carry rationale; spot-checks pass.
- **Expected outcome**: Per-occurrence dispositions reasoned and recorded.
- **Plan-task reference**: T3.3.

---

### AT-040 — AC-FR-9-b.1: Ambiguous cases escalated via AskUserQuestion (audit trail)

- **Maps to AC**: AC-FR-9-b.1 (CC) — escalation discipline
- **EARS form**: Ubiquitous
- **Test type**: structural (audit-log check)
- **Layer of verification**: L2
- **Preconditions**: Plan T3.3 complete.
- **Steps**:
  1. (Act) Filter `bare-id-inventory.json` for entries with `rationale == "user-escalation-resolved"`.
  2. (Act-2) For each such entry: confirm a corresponding `AskUserQuestion` invocation is recorded in the per-task execution result.
  3. (Assert) No guess-based disposition exists; all uncertain cases went to user.
- **Expected outcome**: Escalation audit trail complete for every ambiguous case.
- **Plan-task reference**: T3.3.

---

### AT-041 — AC-FR-9-c: Cross-reference inventory enumerates every reference site

- **Maps to AC**: AC-FR-9-c (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Plan T3.1 complete (bare-ID inventory) + codebase-analysis.json IN-008 (path-form inventory).
- **Steps**:
  1. (Act) Load `codebase-analysis.json` IN-008; confirm 32 path-form entries with `<file>:<line>`.
  2. (Act-2) Load `bare-id-inventory.json`; confirm ≥368 bare-ID entries.
  3. (Assert) Combined inventory = 32 + 368 = 400 entries; every Phase 3 sweep target enumerated.
- **Expected outcome**: Inventory complete.
- **Plan-task reference**: T0.2, T3.1.

---

### AT-042 — AC-FR-10-a: Validator script returns non-zero on any non-canonical ADR

- **Maps to AC**: AC-FR-10-a (CC)
- **EARS form**: Ubiquitous
- **Test type**: integration (positive + negative invocation pair)
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**: Plan T4.1 complete.
- **Steps**:
  1. (Act-positive) Run `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` against the post-Phase-5 repo. Expect exit 0.
  2. (Act-negative) Write `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/`; re-run validator. Expect exit 2.
  3. (Cleanup) Remove fixture.
  4. (Assert) Positive case: exit 0; negative case: exit 2.
- **Expected outcome**: Validator returns 0 on clean repo; non-zero on any non-canonical ADR.
- **Plan-task reference**: T4.1, T6.4.

---

### AT-043 — AC-FR-10-b: Orchestrator Step 8 invokes validator between composer and reviewer

- **Maps to AC**: AC-FR-10-b (CC)
- **EARS form**: When
- **Test type**: structural (prose check) + integration (negative-path simulation)
- **Layer of verification**: L2 + L3
- **Critical path**: yes
- **Preconditions**: Plan T5.1 complete.
- **Steps**:
  1. (Act-L2) `grep -n "validate_adr_placement" .claude/skills/recipe-feature-pipeline/SKILL.md` → expect ≥1 match in the Step 8 area.
  2. (Act-L2-2) Read SKILL.md Step 8; confirm the prose names the validator path, subprocess pattern, exit-code semantics, and failure-surfacing (`AskUserQuestion`).
  3. (Act-L3) Per AT-002, the negative-path harness exercises this surface.
  4. (Assert) Prose + negative-path block both pass.
- **Expected outcome**: Step 8 prose includes validator call; negative-path test blocks at the orchestrator surface.
- **Plan-task reference**: T5.1, T6.7.

---

### AT-044 — AC-FR-10-c: `run_phase_checks.py` includes validator in dispatch; folds into `validator` dimension

- **Maps to AC**: AC-FR-10-c (CC)
- **EARS form**: When
- **Test type**: structural + integration
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**: Plan T5.2 complete.
- **Steps**:
  1. (Act-L1) `grep -n "validate_adr_placement" .claude/skills/auditing-shared/scripts/run_phase_checks.py` → expect ≥1 match in the dispatch block.
  2. (Act-L1-2) Confirm the dispatch invocation includes the `--allowlist output/synthesis-*/adrs/` flag.
  3. (Act-L3-positive) Invoke `run_phase_checks.py` against the post-Phase-5 repo with no negative fixture; expect exit 0 with `validator` dimension PASS.
  4. (Act-L3-negative) Plant the negative fixture (per AT-002); re-invoke; expect non-zero with `validator` dimension BLOCK.
  5. (Cleanup) Remove fixture.
  6. (Assert) All checks pass.
- **Expected outcome**: Dispatch includes validator; dimension rollup includes findings.
- **Plan-task reference**: T5.2, T6.7.

---

### AT-045 — AC-FR-10-d: Packager invokes validator (via narrow Bash grant) and raises BLOCKER on non-zero exit

- **Maps to AC**: AC-FR-10-d (CC)
- **EARS form**: When
- **Test type**: structural + negative-path
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**: Plan T5.3 complete.
- **Steps**:
  1. (Act-L1) `grep -n "validate_adr_placement" .claude/agents/finalize-deliverable-packager.md` → expect ≥1 match.
  2. (Act-L1-2) `grep -n "Bash" .claude/agents/finalize-deliverable-packager.md` → expect match in frontmatter `tools:` field.
  3. (Act-L1-3) `grep -n "validate_adr_placement.py" .claude/settings.json` → expect ≥1 match in an `allow` entry, narrowly scoped.
  4. (Act-L3) Per AT-002 / AT-006: packager surface negative-path test confirms BLOCKER raised.
  5. (Assert) Wiring + grant + allow-list entry + negative-path block all confirmed.
- **Expected outcome**: Packager wired; tool grant present; allow-list entry narrow; BLOCKER raised on negative fixture.
- **Plan-task reference**: T5.3, T6.7.

---

### AT-046 — AC-FR-10-e: Negative-path test fixture causes validator non-zero + surface block

- **Maps to AC**: AC-FR-10-e (CC)
- **EARS form**: Where
- **Test type**: negative-path
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**: Plan T4.2 + T6.7 complete.
- **Steps**: See AT-002.
- **Expected outcome**: All 3 surfaces block on the negative fixture.
- **Plan-task reference**: T4.2 (smoke); T6.7 (3-surface harness).

---

### AT-047 — AC-FR-10-f: Allowlist enumerated explicitly in Blueprint with justification

- **Maps to AC**: AC-FR-10-f (CC)
- **EARS form**: When
- **Test type**: structural (Blueprint content)
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read Blueprint §Design / Allowlist enumeration.
  2. (Act-2) Confirm: empty default; structural exception for `adrs/superseded/` (hard-coded, not allowlist); one contingent entry `output/synthesis-*/adrs/` with rationale.
  3. (Act-3) Confirm the allowlist entry is passed only at the `run_phase_checks.py` dispatch site (not at orchestrator or packager).
  4. (Assert) Allowlist enumerated with rationale; per-surface application correct.
- **Expected outcome**: Allowlist documented per AC-FR-10-f.
- **Plan-task reference**: T5.2.

---

### AT-048 — AC-FR-11-a: 8 file-level updates + 5 family-CLEAN entries enumerated in audit log

- **Maps to AC**: AC-FR-11-a (CC)
- **EARS form**: When
- **Test type**: structural (audit-log check)
- **Layer of verification**: L2
- **Preconditions**: Plan T5.4 + T5.5 + T5.6 complete.
- **Steps**:
  1. (Act) Read `migration-log.md` Phase-5 section.
  2. (Act-2) Count dispositions; expect 8 file-level update entries + 5 family-CLEAN entries = 13 total.
  3. (Assert) 13 dispositions present.
- **Expected outcome**: 13 audit entries.
- **Plan-task reference**: T5.6, T6.8.

---

### AT-049 — AC-FR-11-b: Each skill remediation updates the prose to canonical-only

- **Maps to AC**: AC-FR-11-b (CC)
- **EARS form**: Where
- **Test type**: structural (per-file spot-check)
- **Layer of verification**: L2
- **Preconditions**: Plan T5.4 + T5.5 complete.
- **Steps**:
  1. (Act) For each of the 8 file-level remediation targets (per Blueprint §Skill audit table): re-read the file; confirm the prescribed edit landed.
  2. (Act-2) `grep -n "working/feature/<slug>/adrs/" <each-file>` → expect zero matches.
  3. (Assert) All 8 edits landed; no normative prose retains feature-scoped paths.
- **Expected outcome**: 8 remediations confirmed.
- **Plan-task reference**: T5.4, T5.5.

---

### AT-050 — AC-FR-11-c: Blueprint records skill audit + remediation summary

- **Maps to AC**: AC-FR-11-c (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural (Blueprint content)
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read Blueprint §Design / Skill audit table (and its CLEAN subsection).
  2. (Assert) 4 file-level finding families enumerated with 8 file-level updates + 5 CLEAN families = 13 dispositions; each disposition is no-change-with-rationale OR update-with-fix OR review-with-disposition (no TBDs).
- **Expected outcome**: Blueprint audit table complete.
- **Plan-task reference**: T5.6, T6.8.

---

### AT-051 — AC-CC-1: Validator returns PASS in <5s on post-feature repo

- **Maps to AC**: AC-CC-1 (CC)
- **EARS form**: When
- **Test type**: integration (latency-sensitive)
- **Layer of verification**: L3
- **Preconditions**: Plan T4.1 complete; post-Phase-5 repo state.
- **Steps**:
  1. (Act) Run `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` (no args).
  2. (Assert) Exit code 0; stdout JSON `verdict == "PASS"`; `findings == []`; `elapsed_ms < 5000`.
- **Expected outcome**: PASS verdict, empty findings, under 5s.
- **Determinism notes**: `elapsed_ms` will vary run-to-run by ~10–30%; the 5s threshold has substantial margin against the expected ~100ms baseline. If `elapsed_ms` regularly approaches 5s, investigate (per Blueprint §Risks: 5s budget is comfortable for current repo).
- **Plan-task reference**: T4.1, T6.3, T6.4.

---

### AT-052 — AC-CC-2: Validator returns BLOCK on contrived negative fixture

- **Maps to AC**: AC-CC-2 (CC)
- **EARS form**: Where
- **Test type**: negative-path (unit / smoke)
- **Layer of verification**: L2
- **Preconditions**: Plan T4.2 complete.
- **Steps**:
  1. (Arrange) Write `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/`.
  2. (Act) Run validator.
  3. (Assert) Exit code 2; JSON `verdict == "BLOCK"`; finding entry with `path == "working/feature/test-fixture/adrs/ADR-9999-fixture.md"` and `category == "feature-scoped"` and `remediation_hint` mentioning canonical `adrs/`.
  4. (Cleanup) Remove fixture.
- **Expected outcome**: BLOCK verdict with structured finding.
- **Plan-task reference**: T4.2, T6.7.

---

### AT-053 — AC-CC-3: `run_phase_checks.py` includes validator + dimension rollup

- **Maps to AC**: AC-CC-3 (CC)
- **EARS form**: When
- **Test type**: integration
- **Layer of verification**: L3
- **Preconditions**: Plan T5.2 complete.
- **Steps**: See AT-044.
- **Expected outcome**: Validator dispatched; `validator` dimension reflects validator findings.
- **Plan-task reference**: T5.2.

---

### AT-054 — AC-CC-4: Packager has Bash tool grant + narrow allow-list entry

- **Maps to AC**: AC-CC-4 (CC)
- **EARS form**: Ubiquitous
- **Test type**: structural
- **Layer of verification**: L1
- **Preconditions**: Plan T5.3 complete.
- **Steps**:
  1. (Act) `grep -n "^tools:" .claude/agents/finalize-deliverable-packager.md` and confirm `Bash` listed.
  2. (Act-2) `grep -n "validate_adr_placement.py" .claude/settings.json` → expect match in an `allow` entry of form `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)`.
  3. (Act-3) Confirm the allow-list pattern does NOT permit arbitrary `Bash(python3 *)` invocations (narrow scope per ADR-0054 commitment 3).
  4. (Assert) All three checks pass.
- **Expected outcome**: Frontmatter grant + narrow allow-list entry both present.
- **Plan-task reference**: T5.3.

---

### AT-055 — AC-CC-5: Orchestrator Step 8 describes validator subprocess invocation

- **Maps to AC**: AC-CC-5 (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Plan T5.1 complete.
- **Steps**:
  1. (Act) Read `recipe-feature-pipeline/SKILL.md` Step 8 area.
  2. (Assert) Prose describes the validator subprocess invocation between design-composer return and shared-document-reviewer invocation; cites the validator script path; describes the exit-code semantics; describes the failure-surfacing mechanism.
- **Expected outcome**: Step 8 prose includes the validator-gate description.
- **Plan-task reference**: T5.1, T6.2.

---

### AT-056 — AC-CC-6: No CLAUDE.md addition / rule / output style / MCP / plugin

- **Maps to AC**: AC-CC-6 (CC)
- **EARS form**: When
- **Test type**: structural (full-feature negative)
- **Layer of verification**: L1
- **Preconditions**: Plan all phases complete.
- **Steps**:
  1. (Act) `git diff <pre-feature-commit>..HEAD -- CLAUDE.md .claude/output-styles/ .claude/mcp.json .claude/plugins/` → expect zero diff for these paths (excluding `.claude/settings.json` which has a narrow allow-list entry per AC-CC-4).
  2. (Act-2) `git log <pre-feature-commit>..HEAD --name-only` → confirm no new files under these paths.
  3. (Assert) No CLAUDE.md / output-style / MCP / plugin additions.
- **Expected outcome**: Zero adds in the excluded categories.
- **Plan-task reference**: Plan AC mapping marks as "no Plan task adds a CLAUDE.md entry".

---

### AT-057 — AC-CC-7: Skill audit table enumerates 8 file-level findings + 5 family CLEAN entries

- **Maps to AC**: AC-CC-7 (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**: See AT-050.
- **Expected outcome**: Skill audit table enumerates 13 dispositions.
- **Plan-task reference**: T5.6, T6.8.

---

### AT-058 — AC-OP-1: Fresh pipeline run writes ADRs to canonical; packager passes

- **Maps to AC**: AC-OP-1 (CC) — composes FR-1, FR-3, FR-4, FR-10
- **EARS form**: When
- **Test type**: empirical-run
- **Layer of verification**: L3
- **Critical path**: yes (the load-bearing operational claim)
- **Preconditions**: All Phase 1 + Phase 4 + Phase 5 tasks complete.
- **Steps**: See AT-001 (full simulation) and AT-005 (packager pass on clean repo); AT-058 composes both.
- **Expected outcome**: Orchestrator passes canonical default; design-composer writes to canonical; validator returns 0; packager returns no BLOCKER.
- **Plan-task reference**: T6.2.

---

### AT-059 — AC-OP-2: Four operator files consistent — composed verification

- **Maps to AC**: AC-OP-2 (CC) — composes FR-1, FR-2, FR-3, FR-4
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L2
- **Critical path**: yes
- **Preconditions**: Plan T1.1–T1.5 complete.
- **Steps**: See AT-004.
- **Expected outcome**: Four files consistent; no contradictions; all cite ADR-0036 where they touch the convention.
- **Plan-task reference**: T1.5, T6.1.

---

### AT-060 — AC-OP-3: Validator returns zero exit on post-feature repository

- **Maps to AC**: AC-OP-3 (CC) — composes FR-8a–d, FR-10
- **EARS form**: When
- **Test type**: integration
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**: All Phase 2 + Phase 3 + Phase 4 + Phase 5 tasks complete.
- **Steps**:
  1. (Act) `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` against repo root.
  2. (Assert) Exit code 0; JSON `verdict == "PASS"`; `findings == []`.
- **Expected outcome**: Validator passes empty.
- **Plan-task reference**: T6.4.

---

### AT-061 — AC-OP-4: Three-surface negative-path harness blocks at all 3 surfaces

- **Maps to AC**: AC-OP-4 (CC) — composes FR-10
- **EARS form**: When
- **Test type**: negative-path (integration)
- **Layer of verification**: L3
- **Critical path**: yes
- **Preconditions**: Plan T5.1 + T5.2 + T5.3 + T4.2 complete.
- **Steps**: See AT-002.
- **Expected outcome**: All 3 surfaces return BLOCK on negative fixture.
- **Plan-task reference**: T6.7.

---

### AT-062 — AC-OP-5: Cross-reference sweep re-confirmation reports zero remaining matches

- **Maps to AC**: AC-OP-5 (CC) — composes FR-8 + FR-9
- **EARS form**: When
- **Test type**: structural (sweep)
- **Layer of verification**: L2
- **Critical path**: yes
- **Preconditions**: Plan T3.2 + T3.3 + T3.4 + T6.5 complete.
- **Steps**:
  1. (Act-path-form) Re-run the IN-008 grep pattern set against the post-Phase-5 repo with documented exclusions; expect 0 matches.
  2. (Act-bare-ID) Re-run T3.1's bare-ID extraction grep; expect the count == inventory's "preserved" disposition count + 0 new occurrences.
  3. (Act-file-arithmetic) Verify file counts: `adrs/` contains 55 files; `adrs/superseded/` contains 7 files; `adrs-migrated/` does not exist; `working/feature/*/adrs/` contains 5 `.tombstone` files + 0 `.md` files.
  4. (Assert) All 3 sub-checks pass.
- **Expected outcome**: Zero remaining former-path matches; bare-ID preserved-count consistent; file-count arithmetic correct.
- **Plan-task reference**: T3.4, T6.6.

---

### AT-063 — AC-NFR-1-a: Each Phase 2 task is one atomic git-reversible operation

- **Maps to AC**: AC-NFR-1-a (CC)
- **EARS form**: When
- **Test type**: structural (Plan + audit-log inspection)
- **Layer of verification**: L2
- **Preconditions**: Plan v1.0.1 present; `migration-log.md` populated.
- **Steps**:
  1. (Act) Read Plan Phase 2 task list; confirm each task corresponds to one atomic git-reversible operation OR to one logical group with explicit rationale (T2a.1's 12-ADR group is the documented exception).
  2. (Act-2) For each Phase 2 task: confirm the migration-log entry's commit hash is git-reachable; `git revert <hash>` would cleanly reverse.
  3. (Assert) Atomicity confirmed across Phase 2.
- **Expected outcome**: All Phase 2 tasks atomic.
- **Plan-task reference**: T6.9.

---

### AT-064 — AC-NFR-1-b: Blueprint includes rollback subsection for each FR-8 sub-phase

- **Maps to AC**: AC-NFR-1-b (CC)
- **EARS form**: When
- **Test type**: structural (Blueprint content)
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read Blueprint §Error Handling table.
  2. (Assert) Rows cover rollback paths for FR-8a (byte-equality re-check failure), FR-8b (status-lift fail-safe per AC-FR-8b-1.1), FR-8c (`git mv` reverse via NFR-5), FR-8d (Git history preserves variants per ADR-0055).
- **Expected outcome**: Rollback rows present per sub-phase.
- **Plan-task reference**: T6.9.

---

### AT-065 — AC-NFR-2-a: Validator latency under 5s on typical Codespace

- **Maps to AC**: AC-NFR-2-a (CC)
- **EARS form**: When
- **Test type**: integration (timing)
- **Layer of verification**: L3
- **Preconditions**: Plan T4.1 complete.
- **Steps**:
  1. (Act) Time 5 invocations of `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` against the post-Phase-5 repo. Capture each `elapsed_ms`.
  2. (Assert) Each individual run: `elapsed_ms < 5000`; mean across 5 runs: `< 5000`.
- **Expected outcome**: All runs under 5s; no outlier above 5s.
- **Determinism notes**: Latency varies by Codespace load; 5s threshold has substantial margin against expected ~100ms baseline. Mean is a more stable metric than any single run.
- **Plan-task reference**: T6.3.

---

### AT-066 — AC-NFR-3-a: Phase 0 inventory documents grep pattern set with edge cases

- **Maps to AC**: AC-NFR-3-a (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 + codebase-analysis.json v1.1.0 + bare-ID inventory present.
- **Steps**:
  1. (Act) Read Blueprint §Verification Strategy / Output Comparison / D5 Option B extended pattern set.
  2. (Act-2) Confirm the pattern set is enumerated with edge-case rationale (e.g., `adrs/ADR-NNNN`, `ADR-NNNN`, `[ADR-NNNN](path)`, `see ADR-NNNN`, `<../adrs/ADR-NNNN.md>`, `ADR NNNN` with a space, frontmatter `supersedes:` fields).
  3. (Assert) Documented and enumerated.
- **Expected outcome**: Pattern set documented with edge-case discussion.
- **Plan-task reference**: T3.1.

---

### AT-067 — AC-NFR-3-b: Re-run of pattern set on post-sweep repo returns zero matches for former paths

- **Maps to AC**: AC-NFR-3-b (CC)
- **EARS form**: When
- **Test type**: structural (sweep re-run)
- **Layer of verification**: L2
- **Preconditions**: Plan T3.4 + T6.6 complete.
- **Steps**: See AT-062.
- **Expected outcome**: Zero matches for former ADR paths (excluding documented exclusions).
- **Plan-task reference**: T6.6.

---

### AT-068 — AC-NFR-4-a: Every audited skill carries a no-TBD disposition

- **Maps to AC**: AC-NFR-4-a (CC)
- **EARS form**: When
- **Test type**: structural
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present; migration-log Phase-5 populated.
- **Steps**:
  1. (Act) Read Blueprint §Skill audit table.
  2. (Act-2) For each row: confirm disposition is no-change-with-rationale / update-with-fix / review-with-disposition. No "TBD" / "needs investigation" entries.
  3. (Act-3) Re-read `migration-log.md` Phase-5 section; confirm same property.
  4. (Assert) Zero TBDs.
- **Expected outcome**: No TBDs in either source.
- **Plan-task reference**: T6.8.

---

### AT-069 — AC-NFR-4-b: Unclassifiable finding triggers Open Item + no Phase 5 task

- **Maps to AC**: AC-NFR-4-b (CC)
- **EARS form**: If-then (conditional precondition)
- **Test type**: structural (conditional)
- **Layer of verification**: L2
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read Blueprint §Skill audit table.
  2. (Assert — precondition check) Confirm no row carries an unclassifiable finding (precondition for the AC's `If` clause is FALSE, satisfying the AC vacuously).
  3. (Act-2 — if precondition were TRUE) Confirm the Blueprint would surface as Open Item and Plan would lack a Phase 5 task. (Per current state: not triggered.)
- **Expected outcome**: No unclassifiable findings; AC vacuously satisfied.
- **Plan-task reference**: T6.8.

---

### AT-070 — AC-NFR-5-a: Plan specifies `git mv` for FR-8b archival + FR-8c relocations

- **Maps to AC**: AC-NFR-5-a (CC)
- **EARS form**: When
- **Test type**: structural (Plan content)
- **Layer of verification**: L1
- **Preconditions**: Plan v1.0.1 present.
- **Steps**:
  1. (Act) `grep -n "git mv" working/feature/adr-placement-mechanism-repair-r1/plan-v1.md` → expect ≥1 match per FR-8b and FR-8c task.
  2. (Act-2) Confirm `grep -n "copy-and-delete\|cp.*rm" working/feature/adr-placement-mechanism-repair-r1/plan-v1.md` → expect zero matches.
  3. (Assert) All relocation tasks specify `git mv`.
- **Expected outcome**: Plan uses `git mv` exclusively for relocations.
- **Plan-task reference**: T2b.2, T2c.1.

---

### AT-071 — AC-NFR-5-b: `git log --follow` traces back to original feature-scoped path

- **Maps to AC**: AC-NFR-5-b (CC)
- **EARS form**: When
- **Test type**: integration (Git history)
- **Layer of verification**: L3
- **Preconditions**: Plan T2c.1 complete.
- **Steps**:
  1. (Act) For each of ADR-0046, 0047, 0048, 0049, 0050: run `git log --follow adrs/ADR-NNNN-*.md`.
  2. (Assert) Each log shows a `rename from working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN-*.md` entry.
- **Expected outcome**: Git history preserved.
- **Plan-task reference**: T2c.1, T6.9.

---

### AT-072 — AC-NFR-6-a: Blueprint documents 3 surfaces with per-surface purpose + identical-validator-invocation

- **Maps to AC**: AC-NFR-6-a (CC)
- **EARS form**: When
- **Test type**: structural (Blueprint content)
- **Layer of verification**: L2
- **Critical path**: yes
- **Preconditions**: Blueprint v1.2.0 present.
- **Steps**:
  1. (Act) Read Blueprint §Design / Three-surface enforcement non-redundancy proof.
  2. (Assert) Three rows describe orchestrator gate (surface a), `run_phase_checks.py` (surface b), packager (surface c). Each row carries a per-surface purpose statement + a failure-window description. All three rows specify the same validator script (`validate_adr_placement.py`) with the same default args + same exit-code semantics + same JSON shape (per ADR-0054 commitment 1).
- **Expected outcome**: Three-surface table fully populated; uniformity demonstrated.
- **Plan-task reference**: T5.1, T5.2, T5.3.

---

### AT-073 — AC-NFR-6-b: Architecture Audit confirms 3 surfaces are non-redundant and non-contradictory

- **Maps to AC**: AC-NFR-6-b (CC)
- **EARS form**: When
- **Test type**: review-gate (Architecture Audit verdict)
- **Layer of verification**: L3
- **Preconditions**: Blueprint v1.2.0; Architecture Audit r2 PASS verdict already recorded.
- **Steps**:
  1. (Act) Read Architecture Audit r2 verdict.
  2. (Act-2) Confirm verdict is PASS for NFR-6 non-redundancy claim; no `critical` issue surfacing redundancy / contradiction across the three surfaces.
  3. (Cross-check) Confirm via AT-072 that the structural pattern survives; AT-061 confirms the runtime pattern blocks at all three.
- **Expected outcome**: Architecture Audit confirms non-redundancy + non-contradiction.
- **Plan-task reference**: AC-NFR-6-b is verified by Architecture Audit (per Plan AC mapping).

---

### AT-074 — AC-NFR-7-a: No `--no-verify` in Plan

- **Maps to AC**: AC-NFR-7-a (CC)
- **EARS form**: When
- **Test type**: structural (grep)
- **Layer of verification**: L1
- **Preconditions**: Plan v1.0.1 + per-task execution result files present.
- **Steps**:
  1. (Act) `grep -rn "no-verify" working/feature/adr-placement-mechanism-repair-r1/` → expect zero matches.
  2. (Act-2) `grep -n "no-verify" .claude/skills/auditing-shared/scripts/validate_adr_placement.py` → expect zero matches.
  3. (Assert) Zero matches in either context.
- **Expected outcome**: Zero `--no-verify` invocations.
- **Plan-task reference**: T6.10.

---

### AT-075 — AC-NFR-7-b: Discovery-surfaced bypass need escalates to user via AskUserQuestion

- **Maps to AC**: AC-NFR-7-b (CC)
- **EARS form**: If-then (conditional)
- **Test type**: structural (conditional)
- **Layer of verification**: L1
- **Preconditions**: Phase 0 Discovery complete (per codebase-analysis.json — no need surfaced).
- **Steps**:
  1. (Act) Read codebase-analysis.json; confirm no IN-NNN row identifies a legitimate need for `--no-verify`.
  2. (Assert — precondition check) Precondition for the AC's `If` clause is FALSE; AC vacuously satisfied.
  3. (Act-2 — if precondition were TRUE) Confirm Plan would include an AskUserQuestion escalation. (Per current state: not triggered.)
- **Expected outcome**: AC vacuously satisfied (no bypass need surfaced).
- **Plan-task reference**: T6.10.

---

### AT-076 — AC-NFR-8-a: Validator uses Python stdlib only

- **Maps to AC**: AC-NFR-8-a (CC)
- **EARS form**: When
- **Test type**: structural (script inspection)
- **Layer of verification**: L1
- **Preconditions**: Plan T4.1 complete.
- **Steps**:
  1. (Act) `grep -n "^import\|^from" .claude/skills/auditing-shared/scripts/validate_adr_placement.py`.
  2. (Assert) All imports are Python stdlib only: `argparse`, `pathlib`, `json`, `sys`, `time` (per Blueprint §Component 1 dependencies). No third-party imports.
- **Expected outcome**: Stdlib-only imports.
- **Plan-task reference**: T4.1, T6.10.

---

## Test infrastructure required

### Existing infrastructure (reusable per codebase-analysis.json)

- **`smoke_test_auditing_shared.py`** (`.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`): Python smoke-test harness for auditing-shared scripts. Plan T4.2 extends this with positive + negative coverage for `validate_adr_placement.py`. AT-051, AT-052 ride on this.
- **`run_phase_checks.py`** (`.claude/skills/auditing-shared/scripts/run_phase_checks.py`): Dispatch coordinator with 5-dimensional verdict rollup. Plan T5.2 wires the validator into its dispatch set. AT-044, AT-053 ride on this.
- **Shell-script-style structural tests**: Most ACs in this feature are verifiable via `grep`, `ls`, `diff`, `git log --follow`. These run against the live repo state. No additional harness needed.
- **`shared-document-reviewer` sub-agent** (`.claude/agents/shared-document-reviewer.md`): Real reviewer invocations during Phase 6 verification cover review-gate tests (AT-003, AT-012, AT-073).

### New infrastructure (authored as part of this feature)

- **`validate_adr_placement.py`** (NEW; `.claude/skills/auditing-shared/scripts/validate_adr_placement.py`): Per Plan T4.1. AT-042, AT-051, AT-052, AT-060, AT-061, AT-076 ride on this.
- **Negative-path test fixture** (transient; `working/feature/test-fixture/adrs/ADR-9999-fixture.md`): Per Plan T6.7 + T4.2. Tests must create + clean up this fixture atomically. AT-002, AT-006, AT-046, AT-052, AT-061 ride on this.
- **`migration-log.md`** (NEW; `working/feature/adr-placement-mechanism-repair-r1/migration-log.md`): Per-task audit substrate established by Plan T0.3. AT-023, AT-025–AT-026, AT-040, AT-048, AT-068 read entries from this file.
- **`bare-id-inventory.json`** (NEW; `working/feature/adr-placement-mechanism-repair-r1/bare-id-inventory.json`): Per Plan T3.1. AT-038, AT-039, AT-040, AT-041, AT-062 read entries from this file.

### Test runners

- **Python tests**: invoked via `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` (extension); exit 0 = pass, non-zero = fail with diagnostic on stderr (per existing pattern in the file).
- **Structural tests**: invoked via shell (`bash` or equivalent); pass/fail per the per-test step assertions.
- **Empirical-run tests**: invoked via a Phase 6 verification harness (per Plan T6.2, T6.7); pass/fail per the per-test JSON assertions.

### No new dependencies introduced

Per NFR-8: `validate_adr_placement.py` uses Python stdlib only. Tests use existing Python smoke-test harness + standard shell tooling. No third-party packages, no MCP servers, no new infrastructure introduced solely for the tests.

## CI / execution plan

This is a CC-only feature with no GitHub Actions integration in scope (per Blueprint §Layer Scope / CI/CD). The "CI execution" for this feature is the per-phase Phase Validators authored separately + the Phase 6 verification harness:

| Test class | When run | Mechanism |
|---|---|---|
| **Structural tests (grep/ls/diff)** | Continuously during Plan execution; Phase 6 final pass | Per-task L1 verification + Phase 6 T6.* tasks |
| **Unit / smoke tests** | Phase 4 close + Phase 6 | `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` |
| **Integration tests** | Phase 5 close + Phase 6 | Direct subprocess invocations from a Phase 6 harness |
| **Negative-path harness** | Phase 6 only (T6.7) | Contrived fixture + 3-surface assertions |
| **Empirical-run tests** | Phase 6 (T6.2) | Live pipeline simulation or 2-step proxy per Plan T6.2 |
| **Review-gate tests** | Phase 6 (T6.1, T6.8) | `shared-document-reviewer` invocations on representative artifacts |

Pre-merge gates per Blueprint §Verification Strategy / Operational Verification:
- Reviewer Gate 0/1 (per ADR-0017): runs on this Acceptance Tests doc + on the Blueprint + on each ADR.
- Architecture Audit: runs on Blueprint v1.2.0 (already PASS).
- Cross-Artifact Audit: runs post-Plan + post-Tests (this doc); ensures Blueprint ↔ Plan ↔ Tests alignment.
- AC-OP-* verification at Phase 6.

Post-deploy verification: first subsequent feature-pipeline run after this feature ships (per AC-US-4-a empirical confirmation at Plan T6.2).

## Determinism and isolation commitments

Per the test pyramid + Principle X of KB-general-coding-principles:

### Determinism

- **Validator output is deterministic** modulo `elapsed_ms` (which varies ~10–30% with Codespace load). Tests with timing-sensitivity (AT-051, AT-065) average across 5 runs to mitigate.
- **grep / ls / diff are deterministic** against a fixed repo state.
- **Git operations are deterministic** against the current `HEAD`; `git log --follow` output is stable across runs.
- **Reviewer JSON output may include unrelated flags** that vary based on reviewer-side prompt evolution; per-test assertions narrow to the relevant `issue.category` to avoid coupling to unrelated reviewer behavior.

### Isolation

- **Negative-path tests must clean up the fixture atomically.** If a test crashes mid-execution, the fixture (`working/feature/test-fixture/`) must be cleaned up manually before re-running. Recommended pattern: `try/finally` in the smoke-test extension; explicit `git rm -rf` in shell harnesses.
- **Tests must not modify the live repo state** beyond the negative-path fixture. Any test that writes to `adrs/`, `working/feature/<other>/`, or any other production path is a test-design bug.
- **Tests should be re-runnable** against the same post-Phase-5 repo state without changing assertions. Tests that depend on a specific commit hash (e.g., AT-063's "git revert" check) name the hash explicitly.
- **No test introduces external dependencies** (no network calls, no cloud-service calls, no MCP-server-dependent tests). All tests run locally in the Codespace.

### Known flake risks

- **AT-051 / AT-065 (validator latency)**: Codespace load may cause individual runs to exceed expected ~100ms baseline. 5s threshold provides substantial margin; mean-of-5 is the stable metric.
- **AT-002 / AT-061 (negative-path harness)**: Fixture cleanup failure between runs would falsify subsequent positive-path tests. Mitigation: every test that creates the fixture also includes a guaranteed cleanup step.
- **AT-038–AT-040 (bare-ID inventory)**: T3.3 is the largest single Plan task (368 occurrences); per-occurrence judgment quality affects test validity. Mitigation: per-occurrence rationale recorded + spot-check sampling in AT-039.
- **AT-073 (Architecture Audit verdict)**: Already PASSed at Blueprint v1.2.0; if a later audit re-run flips the verdict, this test must be re-evaluated. Mitigation: tie the assertion to the specific audit cycle (architecture-audit-r2).

## Open coverage gaps

After authoring all tests, the following weak-coverage notes are surfaced for Cross-Artifact Audit consideration:

### Weak-coverage notes

1. **AT-038 / AT-039 (368 bare-ID disambiguation)** — coverage is per-occurrence inventory check + spot-sampling (10 of 368). Full per-occurrence verification would require re-doing the judgment, which is intractable. Mitigation: per-occurrence rationale + escalation discipline (AT-040) provides traceability; misdisambiguation risk is named in Blueprint Risks-table and mitigated by audit trail. **Recommendation**: accept the spot-sampling approach with the audit trail as the load-bearing verification; flag for Cross-Artifact Audit review.

2. **AT-058 (AC-OP-1 fresh pipeline run)** — Plan T6.2 allows either a full pipeline run OR a 2-step simulation. The simulation is structurally equivalent but does not exercise the orchestrator's full Step-8 dispatch. **Recommendation**: prefer the full pipeline run if cost permits; if simulation is used, the test should explicitly document why (per OPI-3 in the Plan).

3. **AT-026 (AC-FR-8b-1.1 fail-safe path)** — conditional test; only triggers if Discovery's "status-lift only" claim about ADR-0024 turns out to be wrong. If the happy path (AT-025) succeeds, AT-026 is not exercised. **Recommendation**: accept the conditional structure; the fail-safe IS the safety net per the Blueprint's AA-014 resolution.

4. **AT-073 (AC-NFR-6-b Architecture Audit verdict)** — coverage is "read the audit verdict" rather than a separate live test. The Architecture Audit is the binding semantic check for non-redundancy. **Recommendation**: accept that AT-072 (structural) + AT-061 (runtime negative-path) + AT-073 (audit verdict reference) collectively bind the AC; no additional separate test needed.

5. **AT-069 / AT-075 (vacuously satisfied conditionals)** — both AC-NFR-4-b and AC-NFR-7-b have If-then form; their preconditions are currently FALSE (per Blueprint + Discovery findings), so the AC is vacuously satisfied. **Recommendation**: include the precondition check as a structural test (already done); if a future Discovery surfaces the precondition's truth, the conditional test path must be exercised.

### No orphan tests

Every test (AT-001 through AT-076) maps to ≥1 PRD or Blueprint AC. No tests author behavior not covered by an AC.

### No orphan ACs

All 60 unique ACs (per Plan's Acceptance Test Cross-Reference table) are mapped to ≥1 test. The Plan's mapping anchors this coverage check; this Acceptance Tests document preserves the same per-AC anchor.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-25 | test-acceptance-author | Initial Acceptance Tests authored from PRD v1.0.2 + Blueprint v1.2.0 + Plan v1.0.1. 76 tests covering 60 unique ACs. Test type breakdown: 38 structural / 6 unit-or-smoke / 12 integration / 6 negative-path / 4 empirical-run / 4 review-gate / 6 mixed (structural + integration). Critical-path tests flagged for: AT-001/002/004/022/027/031/033/036/038/042/043/044/045/046/058/059/060/061/062/072. 5 weak-coverage gaps surfaced (per §Open coverage gaps) for Cross-Artifact Audit review. |
