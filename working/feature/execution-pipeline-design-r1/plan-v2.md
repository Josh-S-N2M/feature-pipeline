---
id: Plan-execution-pipeline-design-r1
version: 2.0.0
status: draft
predecessor: working/feature/execution-pipeline-design-r1/plan-v1.md
supersedes: [working/feature/execution-pipeline-design-r1/plan-v1.md]
feature_slug: execution-pipeline-design-r1
derived_from: working/feature/execution-pipeline-design-r1/blueprint-v5.md
doc_type: plan
phases: 7
total_tasks: 31
generated: 2026-05-22T23:30:00Z
generated_by: plan-author (Claude Code subagent dispatch, authoritative)
agent_invocation_simulation: false
agent_invocation_note: |
  FIRST authoritative (non-simulated) plan-author dispatch. plan-v1.md was a claude.ai
  simulation derived from blueprint-v4 (now superseded by v5). plan-v2 derives from
  the authoritative blueprint-v5 (passed audit r7) and incorporates v5's I-AA-602
  through I-AA-609 cycle-3 corrections that plan-v1 could not reflect.
addresses_v5_introduced_items:
  - I-AA-602 (Bash widening on execute-task-quality-handler — unrestricted; reflected in T3.3 frontmatter)
  - I-AA-603 / ADR-0035 (auditing-shared Skill binding for 4 execute-* agents; T3.1, T3.3, T3.4, T3.5; NOT T3.2)
  - I-AA-604 (AC correction-surface footnotes — Plan task L1/L2/L3 traceability references ADR-0017 for AC-FR-6-e and AC-FR-10-b, not ADR-0021)
  - I-AA-605 (doc_type backfill scope — enumerated ~20+ planning-side agents; surfaced as forward dependency / out-of-scope for primary execution-pipeline-design-r1 feature run; Phase 6 carries an OPT-IN batch task with explicit scope-deviation guard per ADR-0033)
  - I-AA-606 (ADR-0033 §Context bidirectional cross-reference — Phase 5 template tasks reference the cross-reference)
  - I-AA-608 (orchestrator HAS Write — T3.1 frontmatter includes Write)
  - I-AA-609 (T0/T13 boundary transitions — T1.2 log_state_transition.py contract + T3.1 orchestrator state machine explicitly cover 14 transitions = 12 substantive + 2 boundary)
derived_from_extended:
  - working/feature/execution-pipeline-design-r1/blueprint-v5.md (v5.0.0, draft; authoritative; audit-r7 verdict=pass)
  - working/feature/execution-pipeline-design-r1/architecture-audit-issues-r7.json (round 7 pass verdict)
  - working/feature/execution-pipeline-design-r1/architecture-audit-report-r7.md (round 7 companion report)
  - working/feature/execution-pipeline-design-r1/prd-v1.1.0.md (v1.1.0, gate_passed=2; 13 FRs / 60 ACs)
  - working/feature/execution-pipeline-design-r1/synthesis.md (v1.1.0; 18 substantive decisions)
  - working/feature/execution-pipeline-design-r1/codebase-analysis.md (v1.1.1)
  - working/feature/execution-pipeline-design-r1/plan-v1.md (v1.0.0; predecessor; simulated; structurally reused)
  - adrs/ADR-0005-append-only-supersession.md (supersession discipline; plan-v1 → plan-v2)
  - adrs/ADR-0017-document-reviewer-integration.md (4-cycle reconciliation cap; canonical home per ADR-0034 forward correction)
  - adrs/ADR-0029-no-silent-scope-changes-principle.md
  - adrs/ADR-0031-auditing-shared-skill-module.md (canonical-helper-home)
  - adrs/ADR-0032-conventions-canonicalization.md (universal frontmatter + doc_type)
  - adrs/ADR-0033-adr-0029-execution-extension.md (execution-phase Scope-Deviation surfacing)
  - adrs/ADR-0034-prd-mis-credit-cleanup.md (AC-FR-6-e + AC-FR-10-b cite ADR-0017 forward)
  - adrs/ADR-0035-auditing-shared-skill-binding-convention.md (cycle-3 new; Skill-binding opt-in)
  - .claude/skills/KB-documentation-criteria/references/templates/plan-template.md
  - .claude/skills/KB-cc-platform/references/extensions.md (effort enum {low, medium, high, xhigh, max})
---

# Plan: Execution Pipeline Design (run r1) — v2 (authoritative)

## Contents

Section completion checklist — each box checked when the corresponding section is complete (per the Plan template).

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — auditing-shared scripts cluster
- [x] Phase 2 — Skill installs (extract / stub / new install)
- [x] Phase 3 — Execution-phase agent authoring
- [x] Phase 4 — Existing-agent extensions + convention updates
- [x] Phase 5 — Template authoring for new artifact types
- [x] Phase 6 — Rollout (planning-side `doc_type` backfill + end-to-end smoke test)
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

This Plan decomposes the **execution-pipeline-design-r1** Blueprint **v5.0.0** (now authoritative; passed Architecture Audit round 7 with verdict `pass`) into **31 executable tasks across 7 phases**. The feature introduces the execution side of the feature pipeline:

- **5 new subagents** (`execute-orchestrator`, `execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`)
- **1 modified subagent** (`shared-document-reviewer` — extended `doc_type` taxonomy per ADR-0032)
- **3 new skills** (`ai-development-guide` install per AC-FR-9-e; `auditing-github-actions` extraction per FR-8-a; `auditing-codespaces` stub per FR-8-b + Q-CC-4)
- **7 new scripts** under `auditing-shared/scripts/` + `auditing-github-actions/scripts/` + `auditing-codespaces/scripts/`
- **4 new ADRs** (ADR-0032, ADR-0033, ADR-0034 authored in earlier Blueprint cycles; ADR-0035 authored cycle 3 per I-AA-603 / D-RC3-2) — Plan binds to all four as `proposed` and stages them to `accepted` at Phase 0
- **`shared-conventions.md` v1 → v2 spec edits** per ADR-0032 (5 changes)
- **5 new templates** under `KB-documentation-criteria/references/templates/` (Path B disposition per Blueprint § AC-FR-7 floor coverage)
- **Permission policy additions** in `.claude/settings.json`
- **A wildcard set of ~20+ planning-side agent author-prompt edits** to emit `doc_type` per ADR-0032 Change 4 — surfaced explicitly in Phase 6 as an **opt-in batch task** with the Blueprint's Migration Strategy "Incremental rollout option" honored (see Open Item #5 + Phase 6 / T6.1)

The Plan honors:

- **Blueprint v5 Agent Frontmatter Specifications** (canonical YAML for all 5 new agents, verified Gate 4 platform-valid; incorporates cycle-3 widening of `execute-task-quality-handler` Bash to unrestricted per I-AA-602 and Write retention on `execute-orchestrator` per I-AA-608)
- **AC-FR-9-e sequencing constraint** (`ai-development-guide` skill install MUST precede code-producer + quality-handler agent-authoring)
- **ADR-0017 4-cycle cap** (symmetric per D-12; canonical home per ADR-0034 — `AC-FR-6-e` and `AC-FR-10-b` reference ADR-0017 in this Plan's traceability, not the PRD-inherited ADR-0021)
- **ADR-0031 ↔ ADR-0035 structural pairing** (canonical-helper-home location ↔ opt-in Skill-binding convention; 4 of 5 new agents bind `auditing-shared`; `execute-task-code-producer` does NOT per single-script criterion)
- **ADR-0033 execution-phase Scope-Deviation surfacing** (every phase exit + every reconciliation cycle produces an artifact in which deviations surface)
- **Claude Code platform constraints** verified at Gate 4 (memory field is OPTIONAL; valid values when present `{user, project, local}` only — `none` is REJECTED; `Agent` vs `TaskCreate`/`TaskUpdate` are SEPARATE tool families; `Edit` is VALID; effort enum `{low, medium, high, xhigh, max}`)
- **T0 INIT + T13 TERMINATED boundary transitions** per I-AA-609 (state machine has 12 substantive + 2 boundary = 14 transitions; the orchestrator's body and `log_state_transition.py`'s schema both include T0/T13)

## Source

- **Blueprint**: `working/feature/execution-pipeline-design-r1/blueprint-v5.md` (v5.0.0, draft; Architecture Audit round 7 verdict=`pass`, 0 BLOCKER / 0 MAJOR / 0 MINOR / 0 INFO / 3 `recommended` non-verdict items)
- **PRD**: `working/feature/execution-pipeline-design-r1/prd-v1.1.0.md` (v1.1.0, gate_passed=2; 13 FRs / 60 ACs)
- **ADRs new this feature** (all advance from `proposed` → `accepted` at Phase 0 / T0.2):
  - **ADR-0032** (conventions canonicalization + per-doc-type state vocabulary; pairs D-4 + D-18)
  - **ADR-0033** (ADR-0029 execution-phase extension; pairs D-7; §Context revised cycle 3 per I-AA-606 — bidirectional cross-reference with Blueprint § AC-FR-7 floor coverage)
  - **ADR-0034** (PRD v1.1.0 mis-credit cleanup; canonical home for 4-cycle cap is ADR-0017; PRD prose unchanged per ADR-0005)
  - **ADR-0035** (cycle-3 new; auditing-shared Skill-binding convention; pairs structurally with ADR-0031)
- **ADRs inherited**: ADR-0005 (append-only supersession), ADR-0013 (Blueprint template), ADR-0016 (design fan-out/fan-in), ADR-0017 (4-cycle cap canonical home), ADR-0021 (discovery-phase architecture), ADR-0028 (skill-design fixes v4.5.0), ADR-0029 (no-silent-scope-changes), ADR-0030 (mechanism-α), ADR-0031 (auditing-shared canonical-helper-home)
- **Predecessor Plan**: `working/feature/execution-pipeline-design-r1/plan-v1.md` (v1.0.0; simulated; structurally reused — task IDs preserved where the underlying work is unchanged; new tasks added for v5-introduced items; corrected tasks marked in Update History)
- **Phase taxonomy used**: Phase 0 (Setup) through Phase 5 (Feature Delivery), Phase 6 (Rollout — planning-side `doc_type` backfill option + end-to-end smoke test). Phase 6 is structurally the Phase N+1 Rollout phase per the canonical template, retitled to describe its concrete activities for this single-layer infrastructure feature.

## Phase 0 — Setup

### Goal

Pre-flight: confirm Blueprint v5 audit-r7 pass, advance the 4 new ADRs from `proposed` → `accepted`, prepare working directories, and stage placeholder files for the 7 new scripts so Phase 1 task-authoring has its file inventory ready.

### Tasks

#### T0.1: Verify Blueprint v5 audit verdict and supersession state

- **Layer:** Claude Code / Project Filesystem
- **Description:** Confirm `blueprint-v5.md` frontmatter shows `status: draft` (correct for the post-audit-pass state; ratification of `accepted` happens at the Plan/Test Authoring Gate per ADR-0017 sequencing) AND `audit-pass` for round 7 has been recorded (verify `architecture-audit-issues-r7.json` shows `verdict: pass`). Confirm `blueprint-v4.md` carries `status: superseded` with `superseded_by: working/feature/execution-pipeline-design-r1/blueprint-v5.md`. Gating only; no execution work proceeds without verified upstream state.
- **Dependencies:** none
- **Estimate:** XS (10 min check)
- **Satisfies AC:** N/A — setup (gating)
- **L1 verification:** `grep` for `version: 5.0.0` and `status: draft` in blueprint-v5.md frontmatter; `grep` for `verdict: pass` in architecture-audit-issues-r7.json; `grep` for `status: superseded` in blueprint-v4.md.
- **L2 verification:** Manual inspection that the audit-r7 report companion (`architecture-audit-report-r7.md`) is present and references the same set of issues.
- **L3 verification:** N/A.

#### T0.2: Advance ADR-0032, ADR-0033, ADR-0034, ADR-0035 from `proposed` → `accepted`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Update each of the 4 ADRs' frontmatter `status: proposed` → `status: accepted` per the per-doc-type ADR 4-state vocabulary in ADR-0032 (`proposed → accepted | superseded | rejected`). Per ADR-0005, this is a frontmatter-only edit; ADR bodies remain unchanged. ADR-0035 is the newest (cycle-3 new); the other three were authored in earlier Blueprint cycles (ADR-0032 / 0033 / 0034 in v1; ADR-0033 §Context revised in-place cycle 3 per I-AA-606 + ADR-0005 proposed-status exception). All four advance to `accepted` together so downstream tasks (T4.1, T4.2, agent author-prompt edits) have ratified spec dependencies. **Note (per ADR-0005)**: this transition is governance, not content; the substantive content was accepted at audit-r7 pass.
- **Dependencies:** T0.1
- **Estimate:** S (20 min total — frontmatter edits + reviewer pass on each)
- **Satisfies AC:** N/A — setup (ADR governance precondition for AC-FR-4-f, AC-FR-10-a, AC-FR-11-e, and ADR-0035's role in implementing the Skill-binding convention referenced by AC-FR-9 and the Blueprint Agent Frontmatter Specifications)
- **L1 verification:** `grep` for `status: accepted` in each of `adrs/ADR-0032-conventions-canonicalization.md`, `adrs/ADR-0033-adr-0029-execution-extension.md`, `adrs/ADR-0034-prd-mis-credit-cleanup.md`, `adrs/ADR-0035-auditing-shared-skill-binding-convention.md`.
- **L2 verification:** Run `shared-document-reviewer` against each ADR (doc_type=adr) and verify the `proposed → accepted` transition is recognized as valid per the new per-doc-type vocabulary (Blueprint Conventions Touched table; ADR-0032 Change 3).
- **L3 verification:** N/A — one-time governance action; the operational verification is that downstream tasks (T4.1 spec edits, T3.x agent authoring) can cite the ratified ADRs without further blocking.

#### T0.3: Create working directory for execution-phase artifact templates

- **Layer:** Claude Code / Project Filesystem
- **Description:** Create the canonical templates directory `.claude/skills/KB-documentation-criteria/references/templates/` if not already present (it exists per IN-015; this task ensures it is writable and that the planned 5 new templates per Phase 5 land at canonical paths). No subdirectory for "execution-phase" is created — per IN-015 the templates directory is flat, and the 5 new templates take the standard `<artifact-name>-template.md` form.
- **Dependencies:** T0.1
- **Estimate:** XS (5 min)
- **Satisfies AC:** N/A — setup (scaffolding for AC-FR-7-a)
- **L1 verification:** Directory exists and is writable.
- **L2 verification:** N/A.
- **L3 verification:** N/A.

#### T0.4: Stage `auditing-shared` 5-script + `auditing-codespaces` stub + `auditing-github-actions` migration placeholders

- **Layer:** Claude Code / Project Filesystem
- **Description:** Create empty placeholder files at the canonical paths for the 7 new/relocated scripts per Blueprint Change Impact Map:
  - 5 new in `.claude/skills/auditing-shared/scripts/`: `detect_stubs.py`, `run_phase_checks.py`, `log_state_transition.py`, `validate_pipeline_frontmatter.py`, `check_pipeline_discipline.py`
  - 1 new stub in `.claude/skills/auditing-codespaces/scripts/`: `audit_codespaces.py` (file created here; populated as stub in T1.6)
  - 1 git-mv target in `.claude/skills/auditing-github-actions/scripts/`: `audit_workflow.py` (the target path is created here; the actual `git mv` happens in T2.1)
  Each placeholder contains only `#!/usr/bin/env python3` + a one-line docstring naming the script's purpose. This stages the file inventory so Phase 1 task-authoring tasks (T1.1–T1.6) can populate without filesystem-create overhead, and so the Phase 1 smoke test (T1.7) has a complete file inventory to scan.
- **Dependencies:** T0.1
- **Estimate:** S (20 min)
- **Satisfies AC:** N/A — setup (staging for FR-5, FR-6, FR-8-a, FR-8-b, AC-FR-2-d, AC-FR-3-c, D-15)
- **L1 verification:** 7 placeholder files exist at the canonical paths; each parses as valid Python (the shebang + docstring form is trivially valid).
- **L2 verification:** `python3 -c "import ast, glob; [ast.parse(open(f).read()) for f in glob.glob('.claude/skills/auditing-shared/scripts/*.py') + glob.glob('.claude/skills/auditing-codespaces/scripts/*.py')]"` parses all.
- **L3 verification:** Deferred to Phase 1 task-completion (the placeholders get populated by T1.1–T1.6).

#### T0.5: Stage `.claude/settings.json` permission allow-list extension entries

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per Blueprint § Security Considerations Permission policy. Add narrow allow-list entries to `.claude/settings.json` for the 8 script invocation patterns (5 in auditing-shared, 1 in auditing-codespaces stub, 1 relocated in auditing-github-actions, plus reserved entry for the future scope-deviation-scan script flagged in Future Extensibility but NOT in scope this feature). Each entry matches the exact script path; no glob expansion. Per KB-cc-design Principle 6 (permissions-as-safety-net). One-shot edit covering all 7 in-scope scripts at once (the 8th reserved entry is added as a commented placeholder to surface the future-extensibility hook).
- **Dependencies:** T0.4 (placeholder paths must exist before they can be allow-listed)
- **Estimate:** S (30 min — narrow JSON edit + careful review against script paths)
- **Satisfies AC:** N/A — setup (gating for AC-FR-3-b, AC-FR-5-d, AC-FR-6-a script invocations; supports Blueprint § Security)
- **L1 verification:** `.claude/settings.json` parses as valid JSON; the 7 new allow-list entries are present (grep for each script basename).
- **L2 verification:** Invoke each placeholder script once via the orchestrator-simulation harness; verify the permission policy permits invocation (no permission-denied error).
- **L3 verification:** Verified during T1.7 (Phase 1 smoke test) which exercises all 7 scripts under the actual permission policy.

### Phase 0 Exit Criteria

- Blueprint v5 audit-r7 pass verified (T0.1)
- 4 ADRs (ADR-0032, ADR-0033, ADR-0034, ADR-0035) advanced to `status: accepted` (T0.2)
- Templates directory writable (T0.3)
- 7 placeholder script files staged at canonical paths (T0.4)
- `.claude/settings.json` permission policy extended with narrow allow-list entries (T0.5)

Phase Validator (per `KB-task-decomposition`): the Phase Validator for Phase 0 tests these exit criteria. If the Phase Validator fails, Phase 0 isn't done.

## Phase 1 — auditing-shared scripts cluster

### Goal

Author the 7 new/relocated scripts per Blueprint Component 10 + FR-8-a/b. These scripts are the substrate the rest of the feature depends on: the frontmatter validator (FR-6), state-transition logger (FR-5 + D-16 + T0/T13 boundary coverage per I-AA-609), stub detector (FR-2 + Q-CC-2 path-aware), phase-quality coordinator (FR-3 + D-3 third-option), discipline-5 mechanical check (D-15 worked example via ADR-0030 pattern), GHA audit (relocated from `KB-github-actions-platform`), and codespaces audit stub (Q-CC-4 stub-vs-real surfacing per ADR-0033).

### Tasks

#### T1.1: Author `validate_pipeline_frontmatter.py`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per FR-6 + ADR-0032's per-doc-type schemas. Path: `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` (disambiguated from existing `auditing-skills/scripts/validate_frontmatter.py` per IN-017). Reads target file path(s); emits structured JSON output (finding objects per Blueprint § Field Propagation Map finding schema). Validates: required fields per doc_type schema; `status` value in canonical state vocabulary for that doc_type (per ADR-0032 D-18 3-tier vocab); current-state correctness (a ratified artifact is not still `draft`); `superseded_by` back-link on superseded artifacts. **Per Blueprint § Frontmatter validator coverage subsection (rewritten cycle 3 per I-AA-601)**: the validator MUST treat `memory` as OPTIONAL (not required); MUST REJECT `memory: none` as INVALID Claude Code syntax; MUST treat `Agent` and `TaskUpdate` as SEPARATE tool-family entries (not synonyms); MUST accept `Task` as alias for `Agent`; MUST accept `Edit` as VALID; MUST accept `Bash` and `Bash(<pattern>:*)` BOTH as valid; MUST accept the 5-value effort enum `{low, medium, high, xhigh, max}`.
- **Dependencies:** T0.4 (placeholder file exists), T0.5 (allow-list permits invocation), T4.1 (shared-conventions.md v2 spec — for the canonical vocabulary; this creates a forward dependency, so the validator's vocab tables are coded against the Blueprint's canonical reference until T4.1 lands, then a small follow-up tightening commit re-points to shared-conventions.md as the source). **Note**: this dependency arrangement is documented in Open Items #3.
- **Estimate:** L (4-6 hours; the 20+5 doc_type enum coverage + per-doc-type schemas is substantial)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b, AC-FR-6-c, AC-FR-9-c (binding check for `ai-development-guide`), AC-FR-11-c (state-value vocabulary check)
- **L1 verification:** Script parses; `--help` prints; module-level imports resolve.
- **L2 verification:** Run against fixture frontmatter blocks covering each of the 20+5 doc_types from the ADR-0032 enum (one happy + one known-bad fixture per doc_type); assert correct severity per AC-FR-6-c (Level 0 for auto-fixable; Level 1 for manual correction). Specifically verify: `memory: none` triggers REJECTION; `Agent` recognized as subagent dispatch; `TaskUpdate` recognized as task-board; `Task` recognized as alias for `Agent`; effort enum accepts `max`.
- **L3 verification:** Run against all existing artifacts in `working/feature/execution-pipeline-design-r1/`; verify findings are surface-correct (most existing artifacts pass; any that fail produce a Level-0 or Level-1 finding properly classified). Run as part of T1.7 smoke test against the synthetic feature scaffolding.

#### T1.2: Author `log_state_transition.py`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per FR-5 + D-16 + Blueprint § Contract 5 (state-transition payload) + Blueprint § State Transitions and Invariants. Path: `.claude/skills/auditing-shared/scripts/log_state_transition.py`. Reads transition payload from stdin (JSON conforming to Contract 5); appends one JSONL line to `working/feature/<feature-slug>/state-transitions.log`. Hook is **observer-only** in v1 per D-16 — failure does NOT block the substantive transition; failure surfaces as Level-1 finding per AC-FR-5-e. **Per I-AA-609 cycle 3**: the payload schema explicitly includes T0 (`from_state: INIT, to_state: pending, transition_name: T0`) and T13 (`to_state: TERMINATED, transition_name: T13`); the script does NOT special-case boundary transitions — they use the same append protocol. **Per Blueprint § Invariant 10 (scope clarified per I-AA-609)**: T0 and T13 events are logged but do NOT increment the cycle counters; only T4 (per-task NEEDS_REVISION) and T10 (phase reconciliation cycle complete) increment counters.
- **Dependencies:** T0.4, T0.5
- **Estimate:** S (2-3 hours; small append-only + schema validation logic)
- **Satisfies AC:** AC-FR-5-a, AC-FR-5-b, AC-FR-5-c, AC-FR-5-d, AC-FR-5-e
- **L1 verification:** Script parses; `--help` prints.
- **L2 verification:** Pipe a valid JSON payload (one substantive transition + one T0 boundary + one T13 boundary across 3 invocations); verify 3 JSONL lines appended with correct fields. Pipe an invalid payload (missing required field per Contract 5); verify non-blocking failure with exit code reflecting hook-failure-surfaced-as-finding semantics (AC-FR-5-e).
- **L3 verification:** Invoked by the orchestrator (T3.1) during T6.2 smoke test; verify `state-transitions.log` accumulates correctly across all 14 transitions during a synthetic full-pipeline run; verify boundary transitions are present.

#### T1.3: Author `detect_stubs.py` (Q-CC-2 path-aware patterns)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-2-d + Q-CC-2 path-aware patterns + D-2d centralized stub detection. Path: `.claude/skills/auditing-shared/scripts/detect_stubs.py`. Takes a file-list argument (or stdin); scans for stub patterns. **Per Q-CC-2 resolution (Blueprint § Q-CC-N Arbitration)**: maintains TWO pattern sets:
  - **Implementation files** (`*.py`, `*.js`, `*.ts`, `*.sh`, etc.; excluding `tests/`, `test_*`, `*_test.*`): `pass\s*$` in non-trivial function bodies, `raise NotImplementedError`, `TODO`, `FIXME`, `// stub`, `# stub`.
  - **Test files** (paths matching `tests/`, `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`): `assert True\s*$` as sole assertion, `assert False\s*$`, `# TODO: test`, `// TODO: assert`, completely-empty test function bodies (after docstring), test names containing `_stub` or `_placeholder`.
  Emits findings per Blueprint § Field Propagation Map finding schema. Findings carry `severity: blocker` for impl-file stubs and `severity: major` for test-file stubs (per Q-CC-2 rationale).
- **Dependencies:** T0.4, T0.5
- **Estimate:** M (3-4 hours; two pattern-set machinery + fixtures)
- **Satisfies AC:** AC-FR-2-d (stub_detected status), Q-CC-2 (path-aware)
- **L1 verification:** Script parses; `--help` prints.
- **L2 verification:** Run against a fixture impl-file containing `raise NotImplementedError`; verify stub finding with `severity: blocker`. Run against a fixture test file containing `assert True\n` as sole assertion; verify stub finding with `severity: major`. Run against a clean fixture; verify zero findings. Run against an impl-file containing a legitimate `pass` placeholder inside a trivially empty exception handler (e.g., `except KeyError: pass`); verify the false-positive is correctly suppressed by the non-trivial-function-body requirement.
- **L3 verification:** Invoked by `execute-task-quality-handler` (T3.3) during T6.2 smoke test; verify a synthetic code-producer output containing a known stub correctly triggers `STUB_DETECTED` verdict.

#### T1.4: Author `run_phase_checks.py` (D-3 third-option thin coordinator)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-3-b + AC-FR-3-c + D-3 third-option (thin coordinator at `auditing-shared/scripts/` per ADR-0031 canonical-helper-home discipline). Path: `.claude/skills/auditing-shared/scripts/run_phase_checks.py`. Coordinates parallel invocation of: unit/integration/E2E test runners (for activated layers — for this single-layer feature, Claude Code only); `auditing-cc-configs/scripts/audit_cc.py`; `auditing-github-actions/scripts/audit_workflow.py` (relocated by T2.1); `auditing-codespaces/scripts/audit_codespaces.py` (stub per T1.6); `validate_pipeline_frontmatter.py` (T1.1); `check_pipeline_discipline.py` (T1.5). Aggregates per-check JSON outputs into a single structured result with the 5 dimensions per Blueprint § Contract 2 (tests, audits, validator, discipline, scope_deviations). **Per AC-FR-3-f**: when a Layer Scope-activated layer has no test suite, emits a Level-5 finding ("plan-level gap"); does NOT silently pass.
- **Dependencies:** T0.4, T0.5, T1.1 (validator must exist as invocation target), T1.3 (stub detector — invoked by quality-handler, NOT directly by run_phase_checks; but its absence would cascade), T1.5 (discipline check), T1.6 (codespaces stub), T2.1 (auditing-github-actions extraction — provides `audit_workflow.py` at the relocated path)
- **Estimate:** L (5-7 hours; parallel invocation orchestration + JSON aggregation + 5-dimension structure)
- **Satisfies AC:** AC-FR-3-a, AC-FR-3-b, AC-FR-3-c, AC-FR-3-f (no-test-suite finding)
- **L1 verification:** Script parses; `--help` prints; module-level imports resolve.
- **L2 verification:** Run against a synthetic phase with all checks passing; verify aggregated output is `verdict: PASS` per Contract 2 rollup rule. Run against a synthetic phase with one failing audit; verify `verdict: NEEDS_RECONCILIATION` and findings array contains the failing check's finding. Run against a synthetic phase where the `cicd` layer is activated but no test suite exists; verify the Level-5 finding is emitted per AC-FR-3-f.
- **L3 verification:** Invoked by `execute-phase-quality-reviewer` (T3.4) during T6.2 smoke test; verify dimensional verdict structure conforms to Blueprint § Contract 2 and that the audit-counter delta per FR-12 is correctly computed in the consumer.

#### T1.5: Author `check_pipeline_discipline.py` (D-15 worked example)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per D-15 worked example (mechanism-α pattern per ADR-0030) + AC-OP-2. Path: `.claude/skills/auditing-shared/scripts/check_pipeline_discipline.py`. Scans target artifact text for pipeline-stage-by-number references (e.g., `stage 12`, `phase 7` when referring to pipeline stages rather than Plan phases). Mechanical check that fixes the historical statement-only enforcement gap (cf. discipline 5 of `recipe-feature-pipeline/SKILL.md`). Emits findings per the standard finding schema; default severity `minor` (Level 0 auto-fixable); `severity: major` when context-sensitive (e.g., the reference is in normative content rather than a code comment). **Per cycle-3+ refinement**: matches inside backtick-delimited inline code spans are suppressed (those are unambiguously code/literal-example references; this allows pedagogical patterns like `stage 12` to be discussed in prose without false positives).
- **Dependencies:** T0.4, T0.5
- **Estimate:** M (2-3 hours; pattern set + scope rules)
- **Satisfies AC:** AC-OP-2 (discipline-5 mechanical enforcement), supports AC-FR-3-d (finding classification by depth)
- **L1 verification:** Script parses; `--help` prints.
- **L2 verification:** Run against a fixture containing a pipeline-stage-by-number reference (e.g., the literal string `stage 12` outside backticks); verify Level-0 finding. Run against a fixture containing "Phase 1" (referring to the Plan's Phase 1, NOT a pipeline stage); verify zero findings — the discipline targets pipeline-stage-by-number, not all numeric phase references. Run against `recipe-feature-pipeline/SKILL.md` itself (which references discipline numbers, NOT stage numbers); verify zero findings. Run against a fixture containing the pattern inside backticks; verify zero findings (cycle-3+ backtick-suppression).
- **L3 verification:** Invoked by `run_phase_checks.py` (T1.4) during T6.2 smoke test; verify findings flow correctly into the discipline dimension of the dimensional verdict per Blueprint § Contract 2.

#### T1.6: Author `audit_codespaces.py` (stub per AC-FR-8-b + Q-CC-4)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-8-b + Q-CC-4 resolution. Path: `.claude/skills/auditing-codespaces/scripts/audit_codespaces.py`. Stub implementation: returns exactly `{"stub": true, "findings": []}` per Q-CC-4 rationale (Blueprint § Q-CC-N Arbitration). **Critical per ADR-0033 stub-vs-real surfacing**: the `"stub": true` field is what distinguishes this from a real-but-empty clean audit; the downstream phase-quality-reviewer treats stub as "not measured" rather than "measured zero". The audit-counter delta computation MUST honor this distinction.
- **Dependencies:** T0.4, T0.5
- **Estimate:** XS (30 min — trivial stub)
- **Satisfies AC:** AC-FR-8-b (stub semantics), Q-CC-4 (stub vs real)
- **L1 verification:** Script parses; running emits exactly `{"stub": true, "findings": []}` to stdout.
- **L2 verification:** Verify `stub: true` field present in JSON output; verify the output is parsable JSON; verify NO other fields are present (deterministic stub).
- **L3 verification:** Invoked by `run_phase_checks.py` (T1.4) during T6.2 smoke test; verify the phase-quality-reviewer's audit-counter delta treats this dimension as "not measured" rather than "0 findings" per Q-CC-4 implementation note.

#### T1.7: Author end-to-end `auditing-shared` smoke test

- **Layer:** Claude Code / Project Filesystem
- **Description:** Author a single integration test (`smoke_test_auditing_shared.py` or analog under the conventional test-location for this repo — see existing patterns in `auditing-shared`). Exercises T1.1 through T1.6 end-to-end against curated test fixtures; verifies the auditing-shared module is internally consistent (each script's output conforms to the schemas in Blueprint § Field Propagation Map finding schema and § Contract Definitions). Also verifies that `run_phase_checks.py` (the coordinator) correctly aggregates outputs from the other 5 scripts plus the stub.
- **Dependencies:** T1.1, T1.2, T1.3, T1.4, T1.5, T1.6
- **Estimate:** M (3-4 hours; fixture authoring + assertion writing)
- **Satisfies AC:** Substrate for AC-FR-3 (full phase-quality stage exercisable); enables T6.2 end-to-end smoke test.
- **L1 verification:** Test file parses; smoke-test runner discovers it.
- **L2 verification:** Smoke test runs to completion against fixtures covering: (a) all-clean (verdict PASS); (b) mixed-findings (verdict NEEDS_RECONCILIATION with finding-classification); (c) blocker (verdict BLOCKER); (d) stub-codespaces dimension distinguishable from "0 findings" per Q-CC-4. All four scenarios produce expected results.
- **L3 verification:** Run the smoke test in the future CI substrate (out of scope for this feature; flagged in Open Item #6) and verify regression detection works.

### Phase 1 Exit Criteria

- 7 scripts authored at canonical paths (5 in auditing-shared + 1 stub in auditing-codespaces + 1 placeholder for the auditing-github-actions relocation target — actual `git mv` in T2.1)
- All 7 scripts parse and `--help` prints
- Smoke test (T1.7) passes against fixtures
- Frontmatter validator (T1.1) self-checks: runs against `blueprint-v5.md` and `plan-v2.md` (this Plan) and reports them clean

## Phase 2 — Skill installs (extract / stub / new install)

### Goal

Per FR-8 + FR-9 + AC-FR-9-e sequencing: extract `auditing-github-actions` from `KB-github-actions-platform` (git mv to preserve history); stub `auditing-codespaces`; install new `ai-development-guide`. **Phase 2 MUST complete BEFORE Phase 3** because Phase 3's agent definitions bind to these skills — and per AC-FR-9-c, the FR-6 frontmatter validator (T1.1) fails an agent whose `skills:` field references a skill that doesn't exist on disk.

### Tasks

#### T2.1: Extract `auditing-github-actions` from `KB-github-actions-platform` (git mv)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-8-a + IN-002 resolution + ADR-0031 canonical-helper-home pattern. Create `.claude/skills/auditing-github-actions/` with: (a) `SKILL.md` describing the audit pattern (frontmatter + body following the existing 9 `auditing-*` skills' SKILL.md pattern); (b) `scripts/audit_workflow.py` via `git mv` from `.claude/skills/KB-github-actions-platform/scripts/audit_workflow.py` (preserves history per IN-002 resolution; **NOT a copy-and-delete**); (c) `references/action_versions.md` via `git mv` from `.claude/skills/KB-github-actions-platform/scripts/action_versions.md`. Update `KB-github-actions-platform/SKILL.md` Contents list per AC-FR-8-e to point to the new `auditing-github-actions` skill for audit functionality (NOT a copy of the content).
- **Dependencies:** T0.1, T0.4 (placeholder script path created in T0.4 must be removed before `git mv` lands the actual file — this is a small ordering wrinkle resolvable by deleting the placeholder before git-mv)
- **Estimate:** L (4-6 hours; SKILL.md authoring + 2 git-mvs + KB-github-actions-platform SKILL.md edit + verification of history preservation)
- **Satisfies AC:** AC-FR-8-a, AC-FR-8-c (helpers in auditing-shared — unchanged here; supports the structural pattern), AC-FR-8-d (downstream consumers will reference auditing-X), AC-FR-8-e (KB Contents list update)
- **L1 verification:** Directory `.claude/skills/auditing-github-actions/` exists with `SKILL.md`, `scripts/audit_workflow.py`, `references/action_versions.md`. SKILL.md frontmatter parses; T1.1 frontmatter validator passes.
- **L2 verification:** `git log --follow .claude/skills/auditing-github-actions/scripts/audit_workflow.py` shows the historical commits from the prior path (verifies `git mv` was used, not copy-and-delete). Existing `design-cicd` agent invocations still find the audit logic (verified after T4.3 update).
- **L3 verification:** Run a full `design-cicd` agent invocation in a test pipeline; verify it discovers the audit logic at the new canonical location.

#### T2.2: Create `auditing-codespaces` skill (stub per AC-FR-8-b + Q-CC-4)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-8-b + Q-CC-4. Create `.claude/skills/auditing-codespaces/` with: (a) `SKILL.md` describing the future audit functionality (clearly marked as stub state per ADR-0033 stub-vs-real surfacing); (b) `scripts/audit_codespaces.py` (the stub authored in T1.6 lives here; T1.6 created the file at this location). The stub's `{"stub": true, "findings": []}` output is the canonical stub-surfacing contract per Q-CC-4.
- **Dependencies:** T1.6 (the stub script exists at the canonical path)
- **Estimate:** S (1-2 hours — SKILL.md authoring is the bulk)
- **Satisfies AC:** AC-FR-8-b (codespaces stub skill), AC-FR-8-c (helpers in auditing-shared — structural pattern), AC-FR-8-d (downstream references go to auditing-X), Q-CC-4
- **L1 verification:** Directory exists; SKILL.md parses; T1.1 frontmatter validator passes.
- **L2 verification:** Skill loads without error in a test agent invocation harness.
- **L3 verification:** Integrated into `run_phase_checks.py` (T1.4); verify the stub envelope surfaces correctly per ADR-0033 (i.e., the codespaces dimension is reported as "stub: not measured" in the dimensional verdict, not "0 findings clean").

#### T2.3: Install `ai-development-guide` skill (per AC-FR-9-e)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-9-e + IN-001 + IN-003 + D-11 binding criterion. Create `.claude/skills/ai-development-guide/SKILL.md` with the 4-phase pattern (lint → build → test → final gate) + technical decision criteria + anti-pattern detection + debugging techniques + quality-check workflow. **Source content from `/mnt/user-data/uploads/SKILL__2_.md`** (302 lines / 9 sections per Blueprint § External Resources Used). Frontmatter normalization: ensure the skill's `name` field is canonical `ai-development-guide` (matches the directory name per project convention). **This task MUST complete before T3.2 (`execute-task-code-producer` agent file) and T3.3 (`execute-task-quality-handler` agent file)** because both bind this skill in their `skills:` field per D-11 binding criterion; AC-FR-9-c specifies the validator fails an agent whose `skills:` references a non-existent skill.
- **Dependencies:** T0.1 (Blueprint approved)
- **Estimate:** L (4-6 hours; non-trivial skill content — translating the uploaded reference into canonical-form SKILL.md + body)
- **Satisfies AC:** AC-FR-9-a (skill binding becomes possible), AC-FR-9-b (Blueprint identifies which agents bind — already in Blueprint Component 2 and 3), AC-FR-9-c (validator can now check binding without false negatives), AC-FR-9-d (Blueprint cites the skill's purpose — already in Blueprint), AC-FR-9-e (the task itself)
- **L1 verification:** SKILL.md exists at `.claude/skills/ai-development-guide/SKILL.md`; frontmatter parses; T1.1 frontmatter validator passes; the 4-phase pattern is described in the body (grep for "lint", "build", "test", "final gate" or equivalents).
- **L2 verification:** Skill loads in a test agent invocation harness; the 4-phase pattern is invocable via prompt-content inspection (the agent context includes the pattern when bound).
- **L3 verification:** Bound by `execute-task-code-producer` (T3.2) in a synthetic agent invocation during T6.2 smoke test; verify the agent's behavior conforms to the 4-phase pattern.

### Phase 2 Exit Criteria

- 3 skills present at canonical paths (`ai-development-guide`, `auditing-github-actions`, `auditing-codespaces`)
- All 3 skills' SKILL.md frontmatter passes T1.1 frontmatter validator
- `git log --follow` on `audit_workflow.py` and `action_versions.md` shows history preserved (T2.1 git-mv verification)
- AC-FR-9-e sequencing precondition met (`ai-development-guide` exists; agents in Phase 3 can bind it without validator failure)
- `KB-github-actions-platform/SKILL.md` Contents list updated to point to new `auditing-github-actions` skill (T2.1)

## Phase 3 — Execution-phase agent authoring

### Goal

Author the 5 new agent files per Blueprint § Agent Frontmatter Specifications + Components 1-5. Each agent file contains canonical YAML frontmatter (transcribed verbatim from Blueprint v5; this includes the cycle-3 corrections for unrestricted Bash on `execute-task-quality-handler` per I-AA-602, Write on `execute-orchestrator` per I-AA-608, and `auditing-shared` Skill binding on the 4 affected agents per I-AA-603 / ADR-0035) + agent body (system prompt expanding Component descriptions). All 5 files placed at `.claude/agents/execute-*.md`.

### Tasks

#### T3.1: Author `.claude/agents/execute-orchestrator.md`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per Blueprint § Agent Frontmatter Specifications (subsection "Agent: execute-orchestrator") + Component 1 description. **Frontmatter (verbatim from Blueprint v5)**:
  ```yaml
  ---
  name: execute-orchestrator
  description: Centralized owner of the execution-pipeline 12-substantive-state machine (plus 2 boundary states INIT/TERMINATED). Invokes the four execution-side specialist agents (code-producer, quality-handler, phase-quality-reviewer, execute-finalize-reconciler) in defined sequences. Routes dispatch matrix outputs back to upstream agents. Tracks per-task and phase-level cycle counters against ADR-0017's 4-cycle cap (symmetric application per D-12).
  model: opus
  effort: high
  tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]
  skills: [KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]
  memory: project
  ---
  ```
  **Per I-AA-608 cycle 3**: `Write` IS included in `tools` (the orchestrator authors `pipeline-run-summary.json` and `state-transitions.log` directly; earlier v3+ Security sections were stale on this). **Per I-AA-603 / ADR-0035**: `auditing-shared` IS in `skills` (orchestrator materially depends on 5 auditing-shared scripts). **Per I-AA-609**: the agent body explicitly enumerates 14 transitions = 12 substantive (T1-T12) + 2 boundary (T0 INIT→pending, T13 any→TERMINATED); invariant 10 cycle-counter equivalence scoped to T4+T10 only (T0/T13 do NOT affect cycle counters). **Body content**: 12-substantive-state machine spec (Blueprint § State Transitions table); cycle counter management per D-12; application-level hook invocation pattern per Q-CC-5; dispatch routing per Blueprint § Contract 4 dispatch taxonomy.
- **Dependencies:** T2.1, T2.2, T2.3 (the agent's `skills:` field references `auditing-shared` (pre-existing), `KB-cc-platform` (pre-existing), `KB-cc-design` (pre-existing), `recipe-feature-pipeline` (pre-existing), and `KB-review-disciplines` (pre-existing) — strictly speaking, T3.1 has NO Phase-2 hard dependency because all of orchestrator's bound skills pre-exist; the Phase-2 dependency listed here is for clean staging so that the FULL set of Phase 3 agents can pass T1.1 validator together). T0.2 (ADR-0035 ratified — provides governance for the new `auditing-shared` binding convention).
- **Estimate:** L (6-8 hours; the body content is substantial — 14-transition state machine + cycle counters + hook invocations + dispatch routing)
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-FR-1-c, AC-FR-1-d (orchestrator owns the stage sequence + transitions); AC-FR-2-a (orchestrator invokes code-producer); AC-FR-2-b (orchestrator invokes quality-handler); AC-FR-2-c, AC-FR-2-d, AC-FR-2-e, AC-FR-2-f (orchestrator handles all 4 verdict-return values); AC-FR-3-a (orchestrator transitions to phase-quality stage on done_n_of_n); AC-FR-3-e (orchestrator advances to Deliverable Packaging on PASS); AC-FR-5-a, AC-FR-5-b, AC-FR-5-c (orchestrator fires state-transition hooks); AC-FR-10-c (orchestrator emits budget-exhausted artifact + escalates); AC-FR-10-d (orchestrator honors per-feature configurable cap default 4)
- **L1 verification:** File exists at `.claude/agents/execute-orchestrator.md`; frontmatter parses; T1.1 frontmatter validator passes (specifically verifies: `Write` present in tools per I-AA-608; `auditing-shared` present in skills per I-AA-603 / ADR-0035; `Agent` and `TaskUpdate` recognized as SEPARATE tool entries per I-AA-601; `memory: project` is in valid enum; `effort: high` is in valid 5-value enum).
- **L2 verification:** Agent loads in a test Claude Code session; `/agents` lists it; tools and skills are visible. The agent body content is parseable and references the 14-transition table.
- **L3 verification:** Spawn the agent with a synthetic `tasks.json` fixture during T6.2 smoke test; verify it walks the 14-transition state machine (including T0 boundary at startup and T13 boundary at terminal gate-pass); verify `state-transitions.log` accumulates 14+ entries (one per transition occurrence) with correct schemas; verify cycle-counter equivalence invariant (#10) holds at every gate.

#### T3.2: Author `.claude/agents/execute-task-code-producer.md`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per Blueprint § Agent Frontmatter Specifications (subsection "Agent: execute-task-code-producer") + Component 2 description. **Frontmatter (verbatim from Blueprint v5)**:
  ```yaml
  ---
  name: execute-task-code-producer
  description: Authors or modifies code per a single task spec (from tasks.json). Operates within the task's declared Target Files scope. Applies the ai-development-guide 4-phase pattern (lint → build → test → final gate). Returns task-execution-result.json with status (COMPLETED | INCOMPLETE | BLOCKED) and files_modified list per D-2a's selective BLOCKING discipline.
  model: sonnet
  effort: medium
  tools: [Read, Glob, Grep, Write, Edit, Bash]
  skills: [ai-development-guide, KB-cc-design]
  ---
  ```
  **Note**: `memory` field is INTENTIONALLY OMITTED (v4 cycle-3 correction preserved in v5 per Frontmatter validator coverage subsection — `memory: none` is invalid Claude Code syntax; absence is the canonical way to express no persistent memory). **Note (per ADR-0035 + Blueprint Component 2)**: `auditing-shared` is NOT in `skills` — code-producer does not materially depend on auditing-shared scripts; the single-script criterion of ADR-0035 does not apply. **Body content**: task-spec consumption pattern; ai-development-guide 4-phase application; scope-deviation surfacing per ADR-0033 (deviations appear in `per-task-execution-result.md` Scope-deviation findings section).
- **Dependencies:** T2.3 (ai-development-guide must exist per AC-FR-9-e sequencing)
- **Estimate:** M (4-5 hours)
- **Satisfies AC:** AC-FR-2-a (orchestrator invokes with allowed-file scope — code-producer respects), AC-FR-9-a (ai-development-guide in skills), AC-FR-9-b (bound per D-11 criterion)
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes; specifically verifies `ai-development-guide` is in `skills` per AC-FR-9-c; `memory` field is ABSENT (validator should NOT flag absence as error per I-AA-601 Frontmatter validator coverage rewrite); `Edit` is present and accepted; `Bash` (unrestricted) is accepted.
- **L2 verification:** Agent loads; the `ai-development-guide` skill content is injected into the agent's context (verify via `/agents` introspection that the skill's body is loaded).
- **L3 verification:** Spawn the agent with a sample task spec during T6.2 smoke test; verify it produces a `per-task-execution-result.{json,md}` pair conforming to the schemas per Blueprint § Contract Definitions; verify the return value status enum is one of `{completed, escalation_needed}` per AC-FR-2-f.

#### T3.3: Author `.claude/agents/execute-task-quality-handler.md`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per Blueprint § Agent Frontmatter Specifications (subsection "Agent: execute-task-quality-handler") + Component 3 description. **Frontmatter (verbatim from Blueprint v5; reflects cycle-3 I-AA-602 Bash widening to UNRESTRICTED + I-AA-603 / ADR-0035 auditing-shared binding)**:
  ```yaml
  ---
  name: execute-task-quality-handler
  description: Per-task quality verdict-issuer. Runs the ai-development-guide 4-phase verification + detect_stubs.py with Q-CC-2 path-aware patterns. Emits APPROVED | NEEDS_REVISION | STUB_DETECTED | BLOCKER status enum per D-2c. STUB_DETECTED is distinct per D-2d (returned before quality checks, prevents silent-success failure mode).
  model: sonnet
  effort: medium
  tools: [Read, Glob, Grep, Bash]
  skills: [ai-development-guide, KB-cc-design, auditing-shared]
  ---
  ```
  **Per I-AA-602 cycle 3 critical**: `Bash` is UNRESTRICTED (no `Bash(python3:*)` narrowing). The agent invokes language-stack-specific test commands (pytest, npm test, cargo test, go test, dotnet test, mvn test, etc.); restricting to python3-only would mechanically break the agent for non-Python stacks. The trade-off is documented in Blueprint § Risk 9 + § Security Considerations § Bash-widening security note; the `.claude/settings.json` allow-list (T0.5) + project sandbox provides the mitigation. **Per I-AA-603 / ADR-0035**: `auditing-shared` IS in `skills` (quality-handler materially depends on `detect_stubs.py` + acceptance-test runners delegated via auditing-shared). **Per Frontmatter validator coverage (v5 rewrite)**: `memory` is OMITTED — `memory: none` would be REJECTED by T1.1 validator. `Write` is INTENTIONALLY ABSENT — the agent does NOT modify code, only evaluates; revisions go back via orchestrator. **Body content**: 4-phase verification per ai-development-guide; `detect_stubs.py` invocation pattern (BLOCKING per D-2a); APPROVED status enum emission per D-2c; STUB_DETECTED distinct path per D-2d.
- **Dependencies:** T2.3 (ai-development-guide), T1.3 (detect_stubs.py)
- **Estimate:** M (4-5 hours)
- **Satisfies AC:** AC-FR-2-b (orchestrator invokes with filesModified — quality-handler consumes), AC-FR-2-c (returns approved status — APPROVED maps), AC-FR-2-d (returns stub_detected), AC-FR-2-e (returns blocked — BLOCKER maps), AC-FR-9-a, AC-FR-9-b
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes; specifically verifies `Bash` is UNRESTRICTED (the bare `Bash` form, not `Bash(python3:*)`) per I-AA-602; `auditing-shared` is in `skills` per I-AA-603 / ADR-0035; `ai-development-guide` is in `skills` per AC-FR-9-c; `memory` field is ABSENT; `Write` is ABSENT.
- **L2 verification:** Agent loads; `detect_stubs.py` is invocable from the agent's `Bash` tool; the `ai-development-guide` skill content is injected.
- **L3 verification:** Spawn the agent with a code-producer's output during T6.2 smoke test; verify it produces a quality-check verdict with the 4-value status enum per Blueprint § Contract 1; verify it correctly invokes `detect_stubs.py` and routes the STUB_DETECTED case per D-2d (no reconciler involvement; orchestrator transitions to escalated_stub per T6 in state machine).

#### T3.4: Author `.claude/agents/execute-phase-quality-reviewer.md`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per Blueprint § Agent Frontmatter Specifications (subsection "Agent: execute-phase-quality-reviewer") + Component 4 description. **Frontmatter (verbatim from Blueprint v5)**:
  ```yaml
  ---
  name: execute-phase-quality-reviewer
  description: First role of D-9 split. Aggregates phase-quality findings from run_phase_checks.py coordinator into D-13 dimensional verdict structure (tests, audits, frontmatter, discipline, scope-deviations — 5 dimensions per v2). Surfaces Scope-Deviations per ADR-0033. Issues phase-quality-report.{json,md} per FR-7. Includes audit-counter delta per FR-12 + Q-CC-3 (per-domain breakdown).
  model: opus
  effort: high
  tools: [Read, Glob, Grep, Bash(python3:*), Write]
  skills: [KB-cc-design, KB-review-disciplines, auditing-shared]
  ---
  ```
  **Per I-AA-603 / ADR-0035**: `auditing-shared` IS in `skills` (reviewer materially depends on `run_phase_checks.py` + `validate_pipeline_frontmatter.py` + `check_pipeline_discipline.py` — 3+ scripts). `Agent` and `Edit` are INTENTIONALLY ABSENT (reviewer aggregates; does not delegate; does not modify upstream artifacts). `memory` is OMITTED. **Body content**: D-13 dimensional verdict structure (5 dimensions per Blueprint § Contract 2); `run_phase_checks.py` invocation pattern; audit-counter delta computation per FR-12 + Q-CC-3 per-domain breakdown; ADR-0033 Scope-Deviation aggregation as 5th dimension; phase-quality-report.{json,md} authoring per D-5 pair pattern.
- **Dependencies:** T1.4 (run_phase_checks.py must exist as invocation target)
- **Estimate:** L (6-8 hours; dimensional verdict logic + audit-counter delta + Scope-Deviation aggregation is substantial)
- **Satisfies AC:** AC-FR-3-a (orchestrator transitions to phase-quality stage; reviewer is invoked), AC-FR-3-b (executes the full check inventory via run_phase_checks.py), AC-FR-3-c (produces phase-quality-report), AC-FR-3-d (classifies findings by depth before emit), AC-FR-3-e (verdict PASS unblocks Deliverable Packaging), AC-FR-3-f (Level-5 finding for no-test-suite layer activation), AC-FR-12-a (audit-counter delta in frontmatter), AC-FR-12-b (delta surfaces in packager-report — supported by the artifact schema)
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes; specifically verifies `Bash(python3:*)` restriction is accepted; `auditing-shared` is in `skills` per I-AA-603 / ADR-0035; `Write` is present (owns phase-quality-report authoring); `Agent` and `Edit` are ABSENT.
- **L2 verification:** Agent loads; can invoke `run_phase_checks.py`; the bound skills (KB-cc-design, KB-review-disciplines, auditing-shared) are visible in context.
- **L3 verification:** Spawn the agent on a synthetic phase with mixed findings during T6.2 smoke test; verify the phase-quality-report.{json,md} pair conforms to D-13 dimensional verdict schema (Blueprint § Contract 2) AND the FR-12 audit-counter delta schema (Blueprint § Contract 3 — per-domain breakdown + informational aggregate per Q-CC-3); verify the 5th dimension (scope_deviations) is populated when deviations are present in upstream `per-task-execution-result` artifacts.

#### T3.5: Author `.claude/agents/execute-finalize-reconciler.md`

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per Blueprint § Agent Frontmatter Specifications (subsection "Agent: execute-finalize-reconciler") + Component 5 description. **Frontmatter (verbatim from Blueprint v5)**:
  ```yaml
  ---
  name: execute-finalize-reconciler
  description: Classifies phase-quality findings per the 8-row dispatch matrix (D-14 6-row base + 2 additions for D-13 5th-dimension scope-deviations). Routes findings to upstream authoring agents (execute-task-code-producer for in-scope code findings; user-escalation for existing-defect-outside-scope). Tracks 4-cycle cap per D-12 (symmetric ADR-0017 application per ADR-0034). Surfaces budget-exhaustion per AC-FR-10-c.
  model: opus
  effort: high
  tools: [Read, Glob, Grep, Write, Agent]
  skills: [KB-cc-design, KB-review-disciplines, auditing-shared]
  memory: project
  ---
  ```
  **Per I-AA-603 / ADR-0035**: `auditing-shared` IS in `skills`. `Agent` is present (re-invocation of upstream subagents during reconciliation per D-14). `memory: project` per cc-design — shares cycle-count state with orchestrator. `TaskCreate`/`TaskUpdate` are INTENTIONALLY ABSENT — reconciler does not manage the session task-board; it dispatches via `Agent` and writes its log via `Write`. **Body content**: 8-row dispatch matrix walk (Blueprint § Contract 4); 4-cycle cap enforcement per D-12 / ADR-0017 (canonical home per ADR-0034 — NOT ADR-0021); scope-bounded dispatch discipline (D-14 edge case); multi-findings-on-one-artifact consolidation; budget-exhausted artifact emission on cycle 4 per AC-FR-10-c.
- **Dependencies:** none required from Phase 3 (parallelizable with T3.1-T3.4)
- **Estimate:** L (6-8 hours; dispatch matrix logic + cap enforcement + scope-deviation dispatch resolution procedure per Contract 4 is substantial)
- **Satisfies AC:** AC-FR-4-a (9-level depth labels), AC-FR-4-b (single dispatch target per level), AC-FR-4-c (depth semantics implementation), AC-FR-4-d (cascade rules per Level 4+), AC-FR-4-e (dispatch matrix referenced from Blueprint — single source of truth), AC-FR-4-f (ADR-0035 documents the convention; ADR-0017 documents the cap; depth classifier is ratified via cc-design.md), AC-FR-10-a (canonical home is ADR-0017 per ADR-0034; **the Plan's traceability cites ADR-0017, NOT ADR-0021** per I-AA-604 / D-RC3-3), **AC-FR-10-b** (the cap applies to quality-reconciliation loop only; does NOT modify planning-side budget governed by **ADR-0017** per ADR-0034 — **PRD's literal ADR-0021 citation is a transcription artifact corrected forward by ADR-0034 + Blueprint footnote per I-AA-604**), AC-FR-10-c (budget-exhausted artifact + user escalation), AC-FR-10-d (4-cycle default; per-feature configurable)
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes; specifically verifies `Agent` is present (subagent dispatch); `Write` is present (owns quality-reconciliation-log.{json,md}); `auditing-shared` is in `skills` per I-AA-603 / ADR-0035; `memory: project` is valid per Gate 4.
- **L2 verification:** Agent loads; `Agent` tool can be exercised (verified by a mock dispatch invocation against a stub upstream agent).
- **L3 verification:** Spawn the agent with a phase-quality-report containing dispatchable findings across all 8 rows of the dispatch matrix during T6.2 smoke test; verify it routes findings correctly per Blueprint § Contract 4; verify cycle counter increments correctly across multiple reconciliation rounds; verify cycle 4 produces the budget-exhausted artifact and escalates per AC-FR-10-c. Verify the scope-deviation-dispatch-target resolution procedure walks the surfacing-location chain correctly for `scope_deviations` findings.

### Phase 3 Exit Criteria

- 5 agent files at `.claude/agents/execute-*.md`
- All 5 pass T1.1 frontmatter validator with their v5-introduced corrections verified (unrestricted Bash on T3.3; Write on T3.1; auditing-shared in skills on T3.1/T3.3/T3.4/T3.5; absent on T3.2)
- All 5 visible in `/agents` listing
- All 5 can be spawned without binding errors
- The 14-transition state machine (12 substantive + 2 boundary per I-AA-609) is implemented in T3.1 body

## Phase 4 — Existing-agent extensions + convention updates

### Goal

Apply the spec-level edits to `shared-conventions.md` per ADR-0032 (5 coordinated changes); extend `shared-document-reviewer` to dispatch on `doc_type` per D-9 second role; update existing caller agents' skill bindings per AC-FR-8-f.

### Tasks

#### T4.1: Update `shared-conventions.md` per ADR-0032 (5 coordinated changes)

- **Layer:** Claude Code / Project Filesystem
- **Description:** Apply the 5 coordinated changes from ADR-0032 to `.claude/skills/KB-documentation-criteria/references/shared-conventions.md` per Blueprint § Conventions Touched + ADR-0032 Decision section:
  1. **Universal frontmatter fields**: promote `feature_slug` and `derived_from` to universal required; add `gate_passed`, `approved_at`, `reviewer_verdict` as required for gated artifacts; add `revised`, `revision_reason` as optional companions.
  2. **User-token chain pattern**: formalize the chained-token discipline.
  3. **Per-doc-type state vocabulary**: replace single 5-state vocab with three category vocabularies — gated 5-state (`draft → proposed → accepted → superseded OR rejected`), analysis/log 3-state (`draft → complete OR superseded`), ADR 4-state (`proposed → accepted OR superseded OR rejected`, no `draft`).
  4. **`doc_type` field** as universal required with 20-value (planning-side) + 5-value (execution-phase) enum.
  5. **New section "Execution-phase artifact frontmatter"** documenting field schemas for the FR-7-c floor artifacts + the 2 introduced beyond floor (per Blueprint § AC-FR-7 floor coverage Path B disposition).
  Per ADR-0005, the file is updated in-place via git commit; this is a spec evolution, not a supersession (`shared-conventions.md` is a knowledge-base reference, not a versioned artifact in the per-doc-type vocabulary).
- **Dependencies:** T0.2 (ADR-0032 ratified `accepted`)
- **Estimate:** L (5-7 hours; substantive doc edit + careful review against existing references)
- **Satisfies AC:** AC-FR-11-a (canonical state vocabulary documented in shared-conventions.md), AC-FR-11-b (templates use default `status:` from canonical vocab — supports T5.x), AC-FR-11-e (ADR-0032 pins the vocabulary; the spec edit is the implementation)
- **L1 verification:** File parses; all 5 changes present (grep for each: `feature_slug` in universal-required section; user-token chain section heading; 3-tier vocabulary; `doc_type` as universal-required field with the 25-value enum; "Execution-phase artifact frontmatter" section).
- **L2 verification:** Run T1.1 frontmatter validator with the updated spec against existing artifacts in the project; verify reasonable findings (historical artifacts per AC-FR-11-d are not flagged for missing `doc_type` because the validator's enforcement is scoped to post-implementation date forward; the new spec is additive).
- **L3 verification:** Re-run `shared-document-reviewer` (after T4.2) on a sample of existing artifacts; verify the per-doc-type vocabulary correctly dispatches.

#### T4.2: Extend `shared-document-reviewer.md` agent body

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per ADR-0032 + D-9 second role + Blueprint Component 6. Update the agent body to dispatch on the `doc_type` field (per ADR-0032 Change 4) for type-specific review logic; add review logic for the 5 new execution-phase artifact types (`per-task-execution-result`, `phase-quality-report`, `quality-reconciliation-log`, `state-transitions-log`, `pipeline-run-summary`) and 2 analysis/log doc types (`codebase-analysis`, `synthesis`) and 1 layer-design doc type — per the 20+5 enum in ADR-0032. **Frontmatter unchanged** (the agent's `tools`/`skills` stay the same per ADR-0005 — only body content evolves). Per the Blueprint, the doc_type field is the dispatch key; per-doc-type vocabulary checks dispatch on this field.
- **Dependencies:** T4.1 (shared-conventions.md v2 spec is the authoritative source for the new vocabularies)
- **Estimate:** M (3-4 hours)
- **Satisfies AC:** AC-FR-6-d (reviewer is invoked at every gate; recognizes new doc_types), supports AC-FR-6-a (validator can be invoked from reviewer)
- **L1 verification:** File parses; T1.1 frontmatter validator passes (validator coverage rewrite per I-AA-601 means the same agent file can pass before and after this body edit).
- **L2 verification:** Agent runs against a sample `per-task-execution-result.{json,md}` (a manual fixture); correctly applies the new vocabulary (`status: draft` → `complete` analysis/log 3-state); correctly identifies the doc_type from frontmatter.
- **L3 verification:** Full integration during T6.2 smoke test — agent is invoked at every gate; verify dispatch logic correct across all 5 new execution-phase doc_types and all 20 planning-side doc_types (the latter verified against existing artifacts; no regression for pre-existing dispatch).

#### T4.3: Update `design-cicd` agent's `skills` binding per AC-FR-8-f

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-8-f. The `design-cicd` agent currently binds `KB-github-actions-platform`; with the audit functionality extracted to `auditing-github-actions` (T2.1), the agent's `skills:` is updated per Blueprint rationale to additionally (or instead) bind `auditing-github-actions`. **Decision (per existing planning-side agent convention)**: ADDITIONALLY bind — preserves backward compatibility (the agent loads both KBs; `KB-github-actions-platform` retains its non-audit content per AC-FR-8-e).
- **Dependencies:** T2.1
- **Estimate:** XS (5-10 min — narrow frontmatter edit)
- **Satisfies AC:** AC-FR-8-f
- **L1 verification:** Frontmatter updated; T1.1 validator passes; both `KB-github-actions-platform` and `auditing-github-actions` present in `skills`.
- **L2 verification:** Agent loads with both skills visible.
- **L3 verification:** Run a `design-cicd` invocation in a test feature; verify it has access to the audit logic at the new canonical location.

#### T4.4: Update `design-codespaces` agent's `skills` binding per AC-FR-8-f

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per AC-FR-8-f. Same pattern as T4.3 but for `design-codespaces` (additionally binds `auditing-codespaces` stub now per T2.2).
- **Dependencies:** T2.2
- **Estimate:** XS (5-10 min)
- **Satisfies AC:** AC-FR-8-f
- **L1 verification:** Frontmatter updated; T1.1 validator passes.
- **L2 verification:** Agent loads.
- **L3 verification:** N/A — `auditing-codespaces` is a stub per ADR-0033 stub-vs-real surfacing; the binding is structural. The downstream surface (Q-CC-4 distinction) is verified during T6.2 smoke test.

### Phase 4 Exit Criteria

- `shared-conventions.md` v1 → v2 edits land (all 5 ADR-0032 changes present)
- `shared-document-reviewer` body updated; dispatches on `doc_type` for all 25 doc_types
- `design-cicd` and `design-codespaces` agents additionally bind the corresponding `auditing-X` skills per AC-FR-8-f
- T1.1 frontmatter validator passes against the updated `shared-conventions.md` and the updated existing-agent files

## Phase 5 — Template authoring for new artifact types

### Goal

Author canonical templates for the 5 new execution-phase artifact types per Blueprint § AC-FR-7 floor coverage (Path B disposition). **Per I-AA-606 cycle 3**: this Phase honors the bidirectional cross-reference with ADR-0033 §Context (revised cycle 3) — `pipeline-run-summary` serves as the PRD AC-FR-7-c "execution-reconciliation log" floor item; `frontmatter-validation report` is covered by the script-output schema inline in `validate_pipeline_frontmatter.py` source (T1.1), NOT by a separate template file. The 5 templates produced here cover 4 of 5 AC-FR-7-c floor items + 1 beyond-floor item.

### Tasks

#### T5.1: Author template for `per-task-execution-result` (D-5 pair pattern)

- **Layer:** Claude Code / Project Filesystem
- **Description:** New template at `.claude/skills/KB-documentation-criteria/references/templates/per-task-execution-result-template.md` per AC-FR-7-a + D-5 pair pattern. The template defines: frontmatter schema (per ADR-0032 + shared-conventions.md v2 new section "Execution-phase artifact frontmatter"); body sections including `## Status`, `## Files Modified`, `## Findings`, `## Scope Deviations` (per ADR-0033 surfacing requirement — Blueprint § Risk 7 + ADR-0033 §Context Path B). **Pair-pattern note**: the template authored here is the `.md` half; the `.json` schema for the matching half is documented in the template's body as the canonical schema (downstream tools generate the `.json` from this schema).
- **Dependencies:** T0.3, T4.1
- **Estimate:** S (2 hours)
- **Satisfies AC:** AC-FR-7-a (template file exists with `-template.md` suffix), AC-FR-7-b (frontmatter schema documented in shared-conventions.md per T4.1 supports this template), AC-FR-7-c (floor item 1 of 5: "per-task execution log"), AC-FR-11-b (default `status:` value drawn from canonical vocab — analysis/log 3-state default `draft`)
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes against the template's frontmatter; the template body conforms to the structure of existing templates in the same directory.
- **L2 verification:** Sample `per-task-execution-result-<task-id>.md` authored from template; T1.1 validates it.
- **L3 verification:** A real artifact authored by `execute-task-code-producer` (T3.2) during T6.2 smoke test conforms to the template; `shared-document-reviewer` (T4.2) accepts it.

#### T5.2: Author template for `phase-quality-report` (D-5 pair pattern; D-13 dimensional verdict)

- **Layer:** Claude Code / Project Filesystem
- **Description:** New template at `.claude/skills/KB-documentation-criteria/references/templates/phase-quality-report-template.md`. The template defines the D-13 5-dimensional verdict structure (tests, audits, validator, discipline, scope_deviations per Blueprint § Contract 2); the audit-counter delta schema per Blueprint § Contract 3 (per-domain breakdown + informational aggregate per Q-CC-3); the rollup rule (blocker in any dimension → overall BLOCKER); body sections for the .md narrative half.
- **Dependencies:** T0.3, T4.1
- **Estimate:** M (3 hours)
- **Satisfies AC:** AC-FR-7-a, AC-FR-7-b, AC-FR-7-c (floor item 2 of 5: "phase-quality report"), AC-FR-11-b, AC-FR-12-a (audit-counter delta schema substrate)
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes.
- **L2 verification:** A sample phase-quality-report authored from template conforms to schema; T1.1 validates it.
- **L3 verification:** A real artifact authored by `execute-phase-quality-reviewer` (T3.4) during T6.2 smoke test conforms to the template.

#### T5.3: Author template for `quality-reconciliation-log` (D-5 pair pattern; per-cycle)

- **Layer:** Claude Code / Project Filesystem
- **Description:** New template at `.claude/skills/KB-documentation-criteria/references/templates/quality-reconciliation-log-template.md`. The template defines the per-cycle dispatch-records structure per Blueprint § Contract 4 (8-row dispatch taxonomy); cycle counter per D-12; outcome enum (CONVERGED / RECONCILIATION_EXHAUSTED) per FR-10. Per FR-13 machine-parseable requirement, the .json half schema documents finding-depth distribution + dispatch-target frequency + budget-utilization fields.
- **Dependencies:** T0.3, T4.1
- **Estimate:** M (3 hours)
- **Satisfies AC:** AC-FR-7-a, AC-FR-7-b, AC-FR-7-c (floor item 3 of 5: "quality-reconciliation log (per cycle)"), AC-FR-11-b, AC-FR-13-a (machine-parseable per-entry structure), AC-FR-13-b (analytics-extractable fields)
- **L1 verification:** File exists; frontmatter parses; T1.1 validator passes.
- **L2 verification:** Sample log conforms; JSONL-equivalent machine-parseable check passes against the .json half schema.
- **L3 verification:** A real artifact authored by `execute-finalize-reconciler` (T3.5) during T6.2 smoke test conforms.

#### T5.4: Author template for `state-transitions-log-entry` (JSONL entry schema)

- **Layer:** Claude Code / Project Filesystem
- **Description:** New template at `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`. Per FR-5 + D-16 + Blueprint § Contract 5 (state-transition payload). The template documents one JSONL entry per line; the entry schema per Contract 5 includes T0 + T13 boundary transition coverage per I-AA-609. **Note**: this is a beyond-floor artifact (per AC-FR-7-d permission) — the 5th floor item ("frontmatter-validation report") is covered by the script-output schema inline in `validate_pipeline_frontmatter.py` source (T1.1), per Blueprint § AC-FR-7 floor coverage Path B disposition cross-referenced by ADR-0033 §Context (per I-AA-606 bidirectional cross-reference).
- **Dependencies:** T0.3, T4.1
- **Estimate:** S (2 hours)
- **Satisfies AC:** AC-FR-7-a, AC-FR-7-b, AC-FR-7-d (beyond-floor artifact conforms to AC-FR-7-a + AC-FR-7-b), AC-FR-5-d (state-transitions log is observable in deliverable archive)
- **L1 verification:** Template parses; documents a valid JSONL entry schema; T1.1 validator passes.
- **L2 verification:** A sample log entry from T1.2 `log_state_transition.py` conforms to the template schema.
- **L3 verification:** During T6.2 smoke test, the orchestrator produces `state-transitions.log` with entries conforming to this template; verify boundary entries (T0, T13) are present and conform.

#### T5.5: Author template for `pipeline-run-summary` (single JSON; per-run)

- **Layer:** Claude Code / Project Filesystem
- **Description:** New template at `.claude/skills/KB-documentation-criteria/references/templates/pipeline-run-summary-template.md`. Per Blueprint § Data Representation Decision 3 (no `.md` pair — single JSON artifact per run). The template defines: `run_id`, `feature_slug`, start/end timestamps, per-stage gate outcomes, total reconciliation cycles, findings dispatched per level, final ship status. **Per Blueprint § AC-FR-7 floor coverage Path B disposition (cross-referenced by ADR-0033 §Context per I-AA-606)**: `pipeline-run-summary` serves as the PRD AC-FR-7-c "execution-reconciliation log" floor item — the per-feature-run reconciliation aggregation is the same artifact under a different framing. The 5th floor item ("frontmatter-validation report") is NOT covered by a template here — it is satisfied by the script-output schema inline in `validate_pipeline_frontmatter.py` source (T1.1) per Path B.
- **Dependencies:** T0.3, T4.1
- **Estimate:** S (2 hours)
- **Satisfies AC:** AC-FR-7-a (template file exists), AC-FR-7-b (frontmatter schema documented in shared-conventions.md per T4.1), AC-FR-7-c (floor item 4 of 5: "execution-reconciliation log" per Path B equivalence), AC-FR-11-b, AC-FR-12-b (delta in packager-report summary — pipeline-run-summary is the source)
- **L1 verification:** Template exists; parses; T1.1 validator passes.
- **L2 verification:** A sample summary from `execute-orchestrator` simulation conforms.
- **L3 verification:** During T6.2 smoke test, the orchestrator produces `pipeline-run-summary.json` conforming to this template.

### Phase 5 Exit Criteria

- 5 templates at `.claude/skills/KB-documentation-criteria/references/templates/` (per-task-execution-result, phase-quality-report, quality-reconciliation-log, state-transitions-log-entry, pipeline-run-summary)
- All templates parse and pass T1.1 frontmatter validator
- `shared-document-reviewer` (post T4.2) recognizes all 5 new doc_types and dispatches correctly
- Blueprint § AC-FR-7 floor coverage Path B disposition honored: 4 of 5 floor items covered by templates here; the 5th (frontmatter-validation report) is covered by the script-output schema in T1.1 source; 1 beyond-floor item (state-transitions-log-entry) added per AC-FR-7-d permission. Bidirectional cross-reference with ADR-0033 §Context (per I-AA-606) is preserved.

## Phase 6 — Rollout (planning-side `doc_type` backfill option + end-to-end smoke test)

### Goal

This Phase is the canonical Phase N+1 Rollout for this single-layer infrastructure feature. It performs two activities:

1. **Conditional / opt-in batch task** (T6.1): edit ~20+ planning-side agent author-prompts to emit `doc_type` in their authored artifacts going forward, per ADR-0032 Change 4 + Blueprint § Migration Strategy (`doc_type backfill — author-prompt vs historical artifact distinction (NEW per I-AA-605 / D-RC3 enumeration)`). **This task is OPT-IN per Blueprint § Migration Strategy's "Incremental rollout option"** — see Open Item #5 + the surface caution note below. The Blueprint EXPLICITLY notes this is INCREMENTAL ROLLOUT, NOT in execution-pipeline-design-r1's primary scope; it is surfaced here as the canonical Phase N+1 rollout activity for the next post-ratification feature run.
2. **End-to-end pipeline smoke test** (T6.2): exercise all 5 new agents + the auditing-shared script cluster + the new templates + the spec/conventions edits + (if T6.1 was executed) the planning-side agent edits, end-to-end against a synthetic mini-pipeline scaffolding. Verifies the integration substrate works.

### Tasks

#### T6.1: (OPT-IN) Apply `doc_type` emission edits to ~20+ planning-side agent author-prompts

- **Layer:** Claude Code / Project Filesystem
- **Description:** Per ADR-0032 Change 4 + Blueprint § Migration Strategy + Blueprint Change Impact Map wildcard row (per I-AA-605 / D-RC3 enumeration). Apply ~1-line edits to each of the ~20+ planning-side agent files at `.claude/agents/intake-*.md`, `.claude/agents/design-*.md`, `.claude/agents/discovery-*.md`, `.claude/agents/finalize-*.md`, `.claude/agents/plan-author.md`, `.claude/agents/test-*.md` — adding `doc_type: <appropriate-value>` emission to each agent's author-prompt frontmatter section. The agents' bodies (substantive authoring logic) are NOT modified — only the author-prompt frontmatter section gains the `doc_type` field per the appropriate value from the 20+5 enum in ADR-0032.
  
  **Scope caution (CRITICAL per Blueprint § Migration Strategy + Open Item #5)**: this batch task is INCREMENTAL ROLLOUT per the Blueprint's explicit Migration Strategy language, NOT in execution-pipeline-design-r1's primary scope. Two valid execution postures:
  - **Posture A (primary; default for this feature run)**: SKIP T6.1 in this feature run. The ~20+ planning-side agent edits ship as a dedicated follow-on feature OR as the first post-ratification feature run's Phase 0. The validator's enforcement is forward-scoped (per AC-FR-11-d); the rollout sequencing has no historical-artifact impact. **Without T6.1, the next post-ratification feature run will trigger validator failures at Gate 0 for every artifact those agents author** — surfaced explicitly in Open Item #5 per ADR-0033's no-silent-absorption discipline. Marked as a Scope-Deviation per ADR-0033 if posture A is chosen — the deviation is the agents-not-yet-emitting-doc_type state. The Plan documents this explicitly so the next feature run inherits the awareness.
  - **Posture B**: EXECUTE T6.1 in this feature run as a batched single task per the plan-author's discretion per Blueprint § Migration Strategy. The 20+ edits are mechanical; the per-agent risk is low (per Blueprint § Verification Strategy backward-compatibility analysis). Estimate scales linearly: ~5 min per agent × 20 agents = ~2 hours plus review.
  
  **Plan-stage default (this Plan v2)**: Posture A — defer to follow-on / first post-ratification feature run. The Plan's `total_tasks: 31` includes T6.1 as a defined task but with Posture A as the default execution disposition. If the user / orchestrator selects Posture B, T6.1 is executed as-is. **The decision posture surfaces explicitly per ADR-0029 + ADR-0033 no-silent-absorption.**
- **Dependencies (Posture B execution)**: T0.2 (ADR-0032 ratified), T4.1 (shared-conventions.md v2 documents the 25-value `doc_type` enum)
- **Estimate:** XL (Posture B: 2-3 hours batched; Posture A: 0 — task skipped with explicit Scope-Deviation surfacing)
- **Satisfies AC:** Forward-supports AC-FR-11-c (validator can flag missing `doc_type` for post-implementation-date artifacts authored by these agents); enables AC-FR-6-d frontmatter validator coverage at every gate without false positives for those agents' authored artifacts. **Does NOT directly satisfy a primary FR for this feature**; the AC satisfaction is forward-scoped.
- **L1 verification (Posture B)**: All ~20+ edited agent files parse; T1.1 frontmatter validator passes on each (validator should NOT flag the `doc_type` addition; it should accept the new field per the ADR-0032 enum).
- **L1 verification (Posture A)**: Scope-Deviation entry recorded in this Plan's Update History + Open Items + (during T6.2) the smoke test's `pipeline-run-summary.json` surfaces the deferred-edits state.
- **L2 verification (Posture B)**: Spawn each edited agent in a test harness; verify it emits `doc_type` in its authored artifact's frontmatter per the ADR-0032 enum.
- **L2 verification (Posture A)**: No L2 — the Scope-Deviation surfacing is the contract.
- **L3 verification (Posture B)**: A full planning-side pipeline run (out of scope for THIS feature; verified by the next post-ratification feature run) produces artifacts whose `doc_type` is correctly emitted at every gate.
- **L3 verification (Posture A)**: Verified by the absence of validator-false-positive cascades during T6.2 (smoke test does not exercise planning-side agents).

#### T6.2: Author synthetic test feature scaffolding + run end-to-end pipeline smoke test

- **Layer:** Claude Code / Project Filesystem
- **Description:** Two coupled sub-activities:
  
  **(a) Author synthetic test feature scaffolding** at `working/feature/_smoke_test_execution_pipeline/`: a minimal test feature with stub PRD + Blueprint + tasks.json + acceptance-tests.md + phase-validators.md. Used only for the smoke test. The scaffolding artifacts carry `status: scaffolding` (or analogous marker — alternatively a `feature_slug` indicating non-production, per shared-conventions.md v2 conventions per T4.1) so that downstream reviewers do not treat it as a real feature.
  
  **(b) Run end-to-end smoke test**: spawn `execute-orchestrator` (T3.1) against the test scaffolding's `tasks.json`. Let it run end-to-end through the 14-transition state machine. Capture: `state-transitions.log` (verify all 14 transitions exercised including T0 + T13 per I-AA-609); 1+ `per-task-execution-result.{json,md}` pairs (per T3.2 + T3.3); 1 `phase-quality-report.{json,md}` pair (per T3.4); 0+ `quality-reconciliation-log-cycle-<N>.{json,md}` pairs depending on the scaffolding's intentional findings (per T3.5); final `pipeline-run-summary.json` (per T3.1).
  
  **The smoke test scaffolding intentionally includes**: (i) a clean happy-path task to verify T1-T3 + T7-T8 transitions; (ii) a task with a fixable lint issue to verify T4 cycle increment + Level-0 dispatch; (iii) a task with a stub to verify T6 STUB_DETECTED + escalated_stub state; (iv) a phase-quality finding that reaches the 4-cycle cap to verify T11 exhaustion + AC-FR-10-c escalation path; (v) (if T6.1 Posture B was executed) verification that planning-side agent edits do not break the smoke test.
- **Dependencies:** T0.5 + T1.* + T2.* + T3.* + T4.* + T5.* (all preceding tasks; T6.2 is the integration L3 for the entire feature). T6.1 disposition (Posture A or B) is INDEPENDENT — T6.2 runs regardless.
- **Estimate:** L (6-8 hours; scaffolding authoring is the bulk; the smoke run itself is fast; assertion authoring against captured artifacts is moderate)
- **Satisfies AC:** AC-FR-1-d (terminal stage gate passes; orchestrator transitions to Deliverable Packaging — verified via T13 boundary transition in state-transitions.log), AC-FR-5-d (state transitions observable in deliverable archive — verified via state-transitions.log content), AC-FR-13-a (per-entry structure verified via machine-parseable quality-reconciliation-log inspection), AC-OP-1 (artifacts in standard layout), AC-OP-2 (discipline-5 mechanical enforcement at every gate — verified via `check_pipeline_discipline.py` invocation in T1.4), AC-OP-3 (`pipeline-run-summary.json` produced at run termination)
- **L1 verification:** Scaffolding directory exists; all 5+ scaffolding artifacts present and parse; smoke-test orchestrator invocation runs to completion (state advances to TERMINATED).
- **L2 verification:** All expected artifacts present at expected paths after the run; `state-transitions.log` contains the expected transitions (T0 → ... → T13); the dimensional verdict in the synthetic phase-quality-report matches expectations for the scaffolding's intentional finding mix.
- **L3 verification:** Re-run `shared-document-reviewer` (per T4.2) + a fresh invocation of `execute-phase-quality-reviewer` (per T3.4) on the smoke-test output; verify all artifacts conform to schemas; verify a deterministic re-execution produces equivalent state-transitions.log entries (replayability per Blueprint § Risk 1 mitigation).

### Phase 6 Exit Criteria

- T6.1 disposition recorded (Posture A default for this Plan v2 — Scope-Deviation entry surfaced; OR Posture B executed with all ~20+ edits applied + L1/L2 verified)
- T6.2 smoke test passes L1/L2/L3
- All 14 state transitions (T0 + T1-T12 + T13) observed at least once across the smoke test
- 5 new agents demonstrably functional in an end-to-end run
- No regression in pre-existing planning-side agents (verified by re-running a known-good planning-side smoke test if available; out of scope to author such a regression suite — flagged in Open Item #6)

---

## Cross-Phase Dependencies

```
Phase 0 (Setup)
   ├──► T0.1 ────► T0.2 ─┬─► (Phase 4: T4.1, T4.2)
   │                     └─► (Phase 6: T6.1 if Posture B)
   ├──► T0.3 ──────────────► (Phase 5: T5.1-T5.5)
   ├──► T0.4 ──────────────► (Phase 1: T1.1-T1.6)
   └──► T0.5 ──────────────► (Phase 1: T1.1-T1.6)

Phase 1 (auditing-shared scripts)
   ├──► T1.1 ────────────────────────► T1.4 ──► T3.4
   │           └─► T3.1 (validator self-check at T1.1 L2)
   ├──► T1.2 ────────────────────────────────► T3.1 (orchestrator invokes)
   ├──► T1.3 ────────────────────────────────► T3.3 (quality-handler invokes)
   ├──► T1.4 ────────────────────────────────► T3.4 (phase-quality-reviewer invokes)
   ├──► T1.5 ─► T1.4 (run_phase_checks invokes discipline-check)
   ├──► T1.6 ─► T1.4 (run_phase_checks invokes codespaces stub)
   │      └─► T2.2 (auditing-codespaces wraps T1.6 stub)
   └──► T1.7 ─► (Phase 1 exit gate; depends on T1.1-T1.6)

Phase 2 (Skills)
   ├──► T2.1 (extract auditing-github-actions; depends on T0.4 placeholder cleanup)
   │      └─► T4.3 (design-cicd skill binding update)
   │      └─► T1.4 (run_phase_checks needs auditing-github-actions/scripts/audit_workflow.py)
   ├──► T2.2 (auditing-codespaces stub; depends on T1.6)
   │      └─► T4.4 (design-codespaces skill binding update)
   └──► T2.3 (ai-development-guide install per AC-FR-9-e sequencing)
          └─► T3.2 (code-producer binds ai-development-guide)
          └─► T3.3 (quality-handler binds ai-development-guide)

Phase 3 (Agents — all parallel once their substrate lands)
   ├──► T3.1 (orchestrator; needs T0.2, T2.x clean staging)
   ├──► T3.2 (code-producer; needs T2.3)
   ├──► T3.3 (quality-handler; needs T2.3, T1.3)
   ├──► T3.4 (phase-quality-reviewer; needs T1.4)
   └──► T3.5 (finalize-reconciler; parallel with T3.1-T3.4)

Phase 4 (Extensions + conventions)
   ├──► T4.1 (shared-conventions.md v2 edits; needs T0.2)
   │      └─► T4.2 (shared-document-reviewer body update)
   │      └─► T5.1-T5.5 (template authoring needs canonical vocab spec)
   │      └─► T1.1 tightening (validator vocab tables → shared-conventions.md as canonical source; see Open Item #3)
   ├──► T4.2 (depends on T4.1)
   ├──► T4.3 (depends on T2.1)
   └──► T4.4 (depends on T2.2)

Phase 5 (Templates — all parallel)
   └──► T5.1, T5.2, T5.3, T5.4, T5.5 (all depend on T0.3 + T4.1)

Phase 6 (Rollout)
   ├──► T6.1 (OPT-IN; Posture A default in v2 — surfaces as Scope-Deviation; Posture B depends on T0.2 + T4.1)
   └──► T6.2 (smoke test; depends on ALL preceding tasks)
```

**Parallelism analysis**:
- **Phases 1 + 2 partially overlap**: T1.4 (run_phase_checks) needs T2.1's auditing-github-actions extraction as an invocation target; the rest of Phase 1 is independent of Phase 2.
- **Phase 3 is mostly parallel internally** once Phase 2 lands (T3.1-T3.5 can run concurrently with mild substrate ordering).
- **Phase 5 (templates) is fully parallelizable internally** (T5.1-T5.5 all depend on T0.3 + T4.1; no internal cross-dependencies).
- **Phase 4 has a sequential pair** (T4.1 → T4.2); T4.3 and T4.4 are parallel with each other and with T4.1/T4.2 (with the T2.1/T2.2 dependency).
- **Phase 6's two tasks are independent of each other** (T6.1 Posture-A is a no-op; Posture-B is an independent ~20+ edit batch; T6.2 runs regardless).

**Critical path**: T0.1 → T0.2 → T4.1 → T5.x (templates) and T0.2 → T2.3 → T3.2/T3.3 → T6.2. Estimated: ~4-5 days serial work; ~2.5-3 days with full parallelism. The single most expensive task is T3.1 (orchestrator body — 14-transition state machine + cycle counters + dispatch routing) at L (6-8 hours).

## L1/L2/L3 Verification Discipline

Every task above carries three verification criteria per the canonical discipline (KB-documentation-criteria `references/disciplines/plan-authoring.md`):

- **L1 — Lowest-cost check** (seconds): file existence, frontmatter parse, `--help` prints, lint passes, type-check passes. Catches "did the task happen at all" failures. Implementor confirms before claiming work-complete.
- **L2 — Functional check** (minutes): unit test green, smoke test pass, isolated invocation produces expected output. Catches "did the task implement the intended behavior in isolation" failures.
- **L3 — Integration / acceptance check** (10+ minutes): full pipeline run, cross-component invocation, real-data validation. For this Plan, L3 is most commonly satisfied during T6.2 end-to-end smoke test — many tasks' L3s reference T6.2 because the integration surface is what they ultimately serve.

Execution-phase agents enforce L1 + L2 per task (via `execute-task-quality-handler` T3.3 at runtime, post-this-feature). L3 enforcement is phase-level (via `execute-phase-quality-reviewer` T3.4 + `execute-finalize-reconciler` T3.5 at runtime).

The Phase Validator authoring stage (downstream of this Plan, authored by `test-phase-validator-author`) consumes the Phase Exit Criteria sections of this Plan as its contract. The Phase Validator's tests verify L3 aggregation across each phase's tasks.

## Acceptance Test Cross-Reference

Every PRD AC (60 total across 13 FRs + 3 cross-layer/operational ACs) maps to one or more Plan tasks. The mapping below is exhaustive (no orphan ACs, no orphan tasks per the `review-cross-artifact-auditor` discipline).

| PRD AC | Plan Task(s) primary | Notes |
|---|---|---|
| **AC-FR-1-a** (ordered sequence of stages in Blueprint) | T3.1 | Orchestrator body codifies the sequence per Blueprint § State Transitions |
| **AC-FR-1-b** (per-stage name + owning agent + named gate + named artifact) | T3.1, T5.x | Orchestrator + templates jointly define this |
| **AC-FR-1-c** (Task Decomposition complete → orchestrator enters first stage) | T3.1 | Orchestrator's INIT → pending transition (T0 boundary per I-AA-609) |
| **AC-FR-1-d** (terminal gate passes → Deliverable Packaging) | T3.1, T6.2 | T13 boundary; verified end-to-end in smoke test |
| **AC-FR-2-a** (task selected → orchestrator invokes code-producer w/ scope) | T3.1, T3.2 | |
| **AC-FR-2-b** (code-producer returns completed → orchestrator invokes quality-handler) | T3.1, T3.3 | |
| **AC-FR-2-c** (quality-handler returns approved → mark complete + advance) | T3.1, T3.3 | |
| **AC-FR-2-d** (quality-handler returns stub_detected → route through dispatch) | T3.1, T3.3, T1.3 | detect_stubs.py + quality-handler + orchestrator |
| **AC-FR-2-e** (quality-handler returns blocked → route through dispatch) | T3.1, T3.3, T3.5 | |
| **AC-FR-2-f** (code-producer returns escalation_needed → route) | T3.1, T3.2, T3.5 | |
| **AC-FR-3-a** (all tasks completed → enter phase-quality stage) | T3.1, T3.4 | done_n_of_n → phase_quality_check transition |
| **AC-FR-3-b** (phase-quality executes tests + cc-audit + GHA + Codespaces + validator) | T3.4, T1.4, T2.1, T2.2, T1.1 | run_phase_checks coordinator fans out |
| **AC-FR-3-c** (phase-quality produces phase-quality-report) | T3.4, T5.2 | reviewer + template |
| **AC-FR-3-d** (any check fails → classify by depth before emit) | T3.4, T3.5 | reviewer classifies; reconciler dispatches |
| **AC-FR-3-e** (all checks pass / named-exempt → gate pass → Deliverable Packaging) | T3.1, T3.4 | reviewer PASS → orchestrator T8 transition |
| **AC-FR-3-f** (layer activated without test suite → Level-5 finding) | T1.4, T3.4 | run_phase_checks emits; reviewer aggregates |
| **AC-FR-4-a** (9-level depth labels) | T3.5 | reconciler emits |
| **AC-FR-4-b** (single dispatch target per level) | T3.5 | dispatch matrix |
| **AC-FR-4-c** (depth semantics Level 0-8) | T3.5 | |
| **AC-FR-4-d** (Level 4+ cascade rules) | T3.5 | |
| **AC-FR-4-e** (Blueprint publishes dispatch matrix as single source of truth) | T3.5 | reconciler references Blueprint § Contract 4 |
| **AC-FR-4-f** (ADR documents classifier + matrix) | T0.2 | ADR-0035 (Skill-binding convention; cycle-3 new) + ADR-0017 (canonical 4-cycle cap home per ADR-0034) + the depth-classifier semantics ratified via Blueprint integration of cc-design.md — the AC is satisfied by the substrate ratification at T0.2 |
| **AC-FR-5-a** (gate pass → fire state-transition hook updating status) | T1.2, T3.1 | log_state_transition.py + orchestrator |
| **AC-FR-5-b** (reconciliation re-authors → update prior status superseded + superseded_by) | T1.2, T3.1, T3.5 | |
| **AC-FR-5-c** (phase-quality gate passes → update each ratified artifact's status to final ship state) | T1.2, T3.1 | |
| **AC-FR-5-d** (state transitions observable in deliverable archive) | T1.2, T3.1, T5.4, T6.2 | state-transitions.log + smoke-test verifies |
| **AC-FR-5-e** (hook fails → gate failed + Level-1 finding) | T1.2, T3.1 | observer-only hook with finding surface |
| **AC-FR-6-a** (validator invokable as script) | T1.1 | |
| **AC-FR-6-b** (validator checks required fields + status + canonical vocab + superseded_by + execution-phase schemas) | T1.1, T4.1 | |
| **AC-FR-6-c** (validator emits Level 0 / Level 1 findings) | T1.1 | |
| **AC-FR-6-d** (validator runs at phase-quality stage + invokable at every gate) | T1.1, T1.4, T3.1, T4.2 | |
| **AC-FR-6-e** (planning-side validator failure → planning reconciliation flow governed by **ADR-0017** per ADR-0034; execution-side → execution flow governed by **ADR-0017** canonical home) | T3.5, T1.1, T0.2 | **Plan cites ADR-0017 forward per ADR-0034 + Blueprint footnote per I-AA-604 / D-RC3-3; the PRD's literal text references ADR-0021 as a transcription artifact only** |
| **AC-FR-7-a** (each execution-phase artifact has `-template.md` template file) | T5.1, T5.2, T5.3, T5.4, T5.5 | 4 of 5 floor items as templates + 1 beyond-floor; the 5th floor item (frontmatter-validation report) is covered by script-output schema in T1.1 source per Blueprint § AC-FR-7 floor coverage Path B |
| **AC-FR-7-b** (frontmatter schemas in shared-conventions.md "Execution-phase artifact frontmatter") | T4.1 | |
| **AC-FR-7-c** (floor enumeration: per-task execution log + phase-quality report + quality-reconciliation log + frontmatter-validation report + execution-reconciliation log) | T5.1 (1/5), T5.2 (2/5), T5.3 (3/5), T1.1 (4/5 via script-output schema per Path B), T5.5 (5/5 = execution-reconciliation log per Path B equivalence with pipeline-run-summary) | All 5 floor items covered via Blueprint § AC-FR-7 floor coverage Path B disposition |
| **AC-FR-7-d** (additional artifacts beyond floor conform to -a + -b) | T5.4 | state-transitions-log-entry as beyond-floor item per AC-FR-7-d permission |
| **AC-FR-8-a** (auditing-github-actions skill exists; scripts moved out of KB-github-actions-platform) | T2.1 | git mv preserves history |
| **AC-FR-8-b** (auditing-codespaces skill exists; SKILL.md only when stub; audit_codespaces.py stub returns `{"stub": true, "findings": []}`) | T2.2, T1.6 | |
| **AC-FR-8-c** (helpers shared between auditing-* skills in auditing-shared per ADR-0031) | T1.1, T1.2, T1.3, T1.4, T1.5 | All 5 new scripts under auditing-shared |
| **AC-FR-8-d** (sub-agents reference auditing-X not KB-X-platform) | T4.3, T4.4 | |
| **AC-FR-8-e** (KB-X-platform/SKILL.md Contents updated) | T2.1 (includes KB-github-actions-platform SKILL.md edit) | |
| **AC-FR-8-f** (caller agent skills frontmatter updated) | T4.3, T4.4 | |
| **AC-FR-9-a** (task-execution sub-agent lists ai-development-guide in skills) | T3.2, T3.3 | |
| **AC-FR-9-b** (Blueprint documents which agents qualify — already in Blueprint Components 2 + 3) | T0.1 (Blueprint approved) | substrate ratification |
| **AC-FR-9-c** (validator fails if ai-development-guide absent from code-producing agent's skills) | T1.1, T3.2, T3.3 | |
| **AC-FR-9-d** (Blueprint cites skill's purpose) | T0.1 | substrate ratification |
| **AC-FR-9-e** (Plan includes ai-development-guide install task at canonical path before binding agents) | T2.3 → T3.2 / T3.3 sequencing | **This AC is satisfied by THIS PLAN's structure** |
| **AC-FR-10-a** (ADR authored defining execution-side reconciliation budget) | T0.2 | **ADR-0017 is the canonical home per ADR-0034**; the ADR is inherited, not authored anew. The AC's "ADR shall be authored" is satisfied historically by ADR-0017 + closed via ADR-0034 cleanup. **The Plan's traceability cites ADR-0017, NOT ADR-0021 per I-AA-604 / D-RC3-3** |
| **AC-FR-10-b** (budget cap applies to quality-reconciliation loop; does NOT modify planning-side budget governed by **ADR-0017** per ADR-0034) | T3.5 | **Plan cites ADR-0017 forward per ADR-0034 + Blueprint footnote per I-AA-604 / D-RC3-3; the PRD's literal text references ADR-0021 as a transcription artifact only** |
| **AC-FR-10-c** (budget exhausted → budget-exhausted artifact + escalation) | T3.1, T3.5 | |
| **AC-FR-10-d** (per-feature configurable; default 4 cycles in ADR-0017 canonical home) | T3.1, T3.5, T0.2 | |
| **AC-FR-11-a** (canonical state vocabulary in shared-conventions.md) | T4.1 | |
| **AC-FR-11-b** (every template uses default `status:` from canonical vocab) | T5.1, T5.2, T5.3, T5.4, T5.5 | |
| **AC-FR-11-c** (validator flags status not in canonical vocab) | T1.1 | per-doc-type dispatch |
| **AC-FR-11-d** (historical archives not migrated; validator scoped to post-implementation date) | T1.1, T4.1 | validator's enforcement honors timestamp scope |
| **AC-FR-11-e** (ADR pins canonical vocabulary + resolves drift) | T0.2 | ADR-0032 ratification |
| **AC-FR-12-a** (phase-quality-report frontmatter includes audit_baseline + audit_final per platform audit family) | T3.4, T5.2 | per Q-CC-3 per-domain breakdown |
| **AC-FR-12-b** (deliverable archive surfaces delta in packager-report summary) | T3.4, T5.5 | pipeline-run-summary.json contains aggregated delta |
| **AC-FR-13-a** (quality-reconciliation log per-entry structure machine-parseable) | T5.3 | |
| **AC-FR-13-b** (future analytics can extract metrics without bespoke parsing) | T5.3 | schema-conformance |
| **AC-OP-1** (artifacts archived to working/feature/<slug>/ in standard layout; state-transitions.log location) | T3.1, T1.2, T6.2 | |
| **AC-OP-2** (discipline-5 mechanical enforcement at every gate via check_pipeline_discipline.py; default Level 0) | T1.5, T1.4, T3.4 | |
| **AC-OP-3** (pipeline-run-summary.json produced at run termination) | T3.1, T5.5, T6.2 | |

**Coverage check**: every PRD AC (60 + 3 op-level = 63 ACs total per Blueprint § Acceptance Criteria) has at least one Plan task. **No orphan ACs** (one-direction). **No orphan tasks** (other direction): T0.1, T0.2, T0.3, T0.4, T0.5, T1.7 are setup-only / staging / smoke-test verification per the `N/A — setup` exception per the Plan-template + plan-authoring discipline. T6.1 is rollout (opt-in per Migration Strategy; surfaces explicitly per ADR-0029 + ADR-0033 no-silent-absorption). All other tasks (T1.1-T1.6, T2.x, T3.x, T4.x, T5.x, T6.2) map to one or more ACs above.

## Estimation Methodology

T-shirt sizing (project-conventional; same as plan-v1):
- **XS**: < 1 hour
- **S**: 1-2 hours
- **M**: 2-4 hours
- **L**: 4-8 hours
- **XL**: 8+ hours (used only for T6.1 Posture B; the batched ~20+ planning-side agent edits in a single task)

Estimates assume familiarity with the codebase (the project's own pipeline). Total project estimate:
- **Serial** (single executor; no parallelism): ~110-150 hours of focused implementation work
- **With full parallelization** (multiple Claude Code sessions in parallel where dependencies allow per Blueprint § Implementation Plan): ~70-90 hours limited by critical path (T0.1 → T0.2 → T4.1 → T5.x AND T0.2 → T2.3 → T3.2/T3.3 → T6.2)

These estimates are illustrative; the task decomposer (downstream) will recompute per-task estimates as inputs to the task DAG. Estimates here are intended for capacity-checking the phase and identifying tasks that may need splitting (no L or XL task in this Plan splits a single discrete deliverable per the plan-authoring anti-pattern guidance).

## Resourcing Posture

This Plan assumes the user (Josh) executes via Claude Code, with the 5 new execution-phase agents handling per-task execution and Josh reviewing at gates. Single-developer pipeline; agents handle execution; user reviews at gates.

If the user later wants to run multiple `execute-task-code-producer` invocations in parallel (e.g., T3.2 + T3.5 concurrently via separate Claude Code sessions or via background subagents per the [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents#run-subagents-in-foreground-or-background)), the Plan supports it — Phase 3 tasks are mostly parallelizable.

The Plan assumes no team parallelization (single contributor). For a multi-contributor execution, the task descriptions are sufficiently self-contained that the work could be distributed; the dependency graph is the constraint.

## Open Items (Pending Cross-Artifact Audit)

These items are surfaced for Cross-Artifact Audit (downstream of this Plan, after Test Authoring) to verify or escalate. Each is anchored to substrate from the Blueprint v5 or this Plan's authoring process.

1. **L3 verification of state-transition hooks (T1.2 + T3.1) requires a full pipeline run.** Until T6.2 lands, T1.2's and T3.1's L3 verifications are pending. Acceptable per the plan-authoring discipline (most tasks have similar L3-on-smoke-test dependency); the smoke test is the integration substrate.

2. **Q-CC-1 opus-escalation hook (Q-CC-1 monitoring trigger from Blueprint).** Blueprint Q-CC-1 defers the model upgrade for `execute-task-quality-handler` to "follow-on feature if operational evidence justifies." This Plan does NOT include an opus-escalation task; the substrate (the agent at sonnet/medium per T3.3) is what ships. If the user observes classification errors in early use (≥2 ambiguous verdicts per feature run in first 3 runs), a follow-on feature ships the upgrade per the Q-CC-1 monitoring trigger. Reservation only; not a Plan-stage open item to resolve here.

3. **T1.1 (validate_pipeline_frontmatter.py) ↔ T4.1 (shared-conventions.md) circular dependency softened by staged authoring.** T1.1 codes its vocab tables against the Blueprint's canonical reference (Blueprint § Conventions Touched + ADR-0032's enumeration); after T4.1 lands the shared-conventions.md v2 spec, a small tightening commit re-points T1.1's vocab tables to read from shared-conventions.md directly. This is documented in the T1.1 description; it is NOT a true cycle (the Blueprint is the substrate for both; the spec file becomes the runtime source post-T4.1). Surface for Cross-Artifact Audit verification that the staging is sound.

4. **Phase 4 (T4.1 shared-conventions.md update) interaction with existing artifacts.** Updating shared-conventions.md mid-feature means existing artifacts (Blueprint, PRD, ADRs, prior planning-side outputs) may begin to fail the new validation if the validator's enforcement is not scoped to post-implementation-date forward per AC-FR-11-d. T1.1 implements the scope-to-post-implementation-date behavior; the new schemas are additive-only per ADR-0032's archive-authoritative direction. Cross-Artifact Audit at Gate 6 will verify the additive-only property.

5. **Phase 6 / T6.1 disposition (Posture A vs Posture B for ~20+ planning-side agent `doc_type` emission edits).** This Plan v2 selects **Posture A (defer)** as the default per Blueprint § Migration Strategy "Incremental rollout option" — the ~20+ edits ship as a dedicated follow-on feature OR as the first post-ratification feature run's Phase 0. **The deferred-edits state is a Scope-Deviation per ADR-0033** and surfaces in this Open Items list AND in this Plan's Update History AND (during T6.2) in the smoke-test `pipeline-run-summary.json`. **Without those edits, the next post-ratification feature run will trigger validator failures at Gate 0 for every artifact those agents author** — the next feature run inherits this awareness from this Plan's surfacing. **Surface for Cross-Artifact Audit + user decision**: if the user prefers Posture B (execute the ~20+ edits as a batched task in this feature run), T6.1 is re-classed as "executed" and the Scope-Deviation entry is closed. Per ADR-0029 no-silent-scope-changes, this disposition is explicit.

6. **Regression suite for pre-existing planning-side agents.** T6.2's Phase 6 Exit Criteria mentions "no regression in pre-existing planning-side agents (verified by re-running a known-good planning-side smoke test if available)" — but authoring such a regression suite is out of scope for THIS feature. Surface for the next feature run or a dedicated regression-suite-authoring feature. No-op for this Plan; flagged for awareness.

7. **`scan_unsurfaced_deviations.py` mechanical script (deferred per Blueprint § Risk 7 + Future Extensibility).** ADR-0033 articulates the audit-stage enforcement requirement (execute-phase-quality-reviewer + execute-finalize-reconciler scan upstream artifacts for unsurfaced deviations); v1 ships the requirement statement in agent prompts (T3.4 + T3.5 body content). Mechanical enforcement via `scan_unsurfaced_deviations.py` is deferred to a follow-on feature per Blueprint Risk 7 mitigation. Plan-stage no-op; flagged for awareness.

8. **`I-AA-602 Path b` deferred re-route of quality-handler test invocation through `run_phase_checks.py`.** Per Blueprint § Future Extensibility, the cycle-3 D-RC3-1 decision widened quality-handler's Bash to unrestricted to match cc-design.md verbatim. The audit's Path b alternative (re-architect so quality-handler only consumes results) is a candidate follow-on architectural decision. Plan-stage no-op; flagged for awareness.

9. **Reconciliation budget consumed during Blueprint authoring**: Cycle 3 of 4 was used in the Blueprint authoring (cycles 1+2 were claude.ai simulations; cycle 3 was the first authoritative reconciliation per blueprint-v5.md frontmatter `re_author_reason`). Per ADR-0017 4-cycle cap symmetric per ADR-0034, **1 reconciliation cycle remains for the Plan / Test / Cross-Artifact-Audit sequence**. If Cross-Artifact Audit surfaces issues beyond 1 cycle of reconciliation, surface for user decision per ADR-0017 cap-exhaustion discipline + AC-FR-10-c escalation procedure. **CAUTION FOR DOWNSTREAM**: the Plan + Tests + Audit budget is tight; downstream reviewers should consolidate findings per cycle to maximize the remaining budget.

## Update History

This document follows ADR-0005 append-only supersession discipline. v2 supersedes v1 (which was a claude.ai simulation derived from blueprint-v4, now superseded by blueprint-v5).

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-22 | claude.ai simulation (acting as plan-author; `agent_invocation_simulation: true`) | Initial Plan authoring. 28 tasks across 7 phases (Phase 0 Setup → Phase 6 End-to-end smoke test). Derived from `blueprint-v4.md`. Structurally correct per plan template; task-level detail flagged for refinement by authoritative dispatch. Marked superseded by v2 per ADR-0005. |
| **2.0.0** | **2026-05-22** | **plan-author (Claude Code subagent dispatch, authoritative; `agent_invocation_simulation: false`)** | **FIRST authoritative plan-author dispatch. Derived from `blueprint-v5.md` (which passed Architecture Audit round 7 verdict=pass). 34 tasks across 7 phases. Plan v1's task structure structurally preserved where Blueprint v4 → v5 work is unchanged; new tasks + updates added for the v5-introduced cycle-3 items: (1) I-AA-602: T3.3 frontmatter codes Bash as UNRESTRICTED per cc-design.md verbatim, with Risk-9 surfacing + Future-Extensibility Path-b hook; (2) I-AA-603 / ADR-0035: T3.1, T3.3, T3.4, T3.5 frontmatters include `auditing-shared` in `skills` per the opt-in Skill-binding convention; T3.2 does NOT (per single-script criterion); ADR-0035 ratified at T0.2; (3) I-AA-604: AC-FR-6-e + AC-FR-10-b traceability rows cite ADR-0017 forward (not the PRD-inherited ADR-0021) per ADR-0034 + Blueprint cycle-3 footnotes; (4) I-AA-605: T6.1 (OPT-IN) batch task covers the ~20+ planning-side agent author-prompt `doc_type` emission edits; Posture A (defer) selected as default per Blueprint Migration Strategy; surfaces as Scope-Deviation per ADR-0033; Open Item #5 carries the disposition; (5) I-AA-606: T5.4 + T5.5 + Phase 5 Exit Criteria reference the Blueprint § AC-FR-7 floor coverage Path B bidirectional cross-reference with ADR-0033 §Context; (6) I-AA-608: T3.1 frontmatter includes `Write` per the v3+-defensive reading; orchestrator-HAS-Write is reflected in the description + AC mapping; (7) I-AA-609: T1.2 contract + T3.1 body explicitly include T0 INIT and T13 TERMINATED boundary transitions; the state-machine cardinality is "12 substantive + 2 boundary = 14"; invariant 10 scope explicitly limited to T4 + T10. All ADR ratifications in T0.2 now cover 4 ADRs (added ADR-0035). Open Items #5 + #9 surface the reconciliation budget caution + Posture-A scope deviation explicitly per ADR-0029 + ADR-0033 no-silent-absorption. Predecessor plan-v1.md marked superseded.** |

Future amendments will append new rows here; the prior version is preserved per ADR-0005 (the file at `plan-v1.md` carries `status: superseded` with `superseded_by: plan-v2.md`; its substantive content is unchanged per append-only discipline).
