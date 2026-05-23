---
id: PhaseValidators-execution-pipeline-design-r1
version: 1.0.0
status: draft
feature_slug: execution-pipeline-design-r1
doc_type: phase-validators
predecessor: null
derived_from:
  - working/feature/execution-pipeline-design-r1/plan-v2.md
  - working/feature/execution-pipeline-design-r1/blueprint-v5.md
  - working/feature/execution-pipeline-design-r1/prd-v1.1.0.md
derived_from_extended:
  - working/feature/execution-pipeline-design-r1/plan-v2-review-report.md
  - working/feature/execution-pipeline-design-r1/architecture-audit-issues-r7.json
  - adrs/ADR-0017-document-reviewer-integration.md
  - adrs/ADR-0029-no-silent-scope-changes-principle.md
  - adrs/ADR-0032-conventions-canonicalization.md
  - adrs/ADR-0033-adr-0029-execution-extension.md
  - adrs/ADR-0034-prd-mis-credit-cleanup.md
  - adrs/ADR-0035-auditing-shared-skill-binding-convention.md
  - .claude/skills/KB-documentation-criteria/SKILL.md
  - .claude/skills/KB-review-disciplines/references/gate-0-1-procedure.md
generated: 2026-05-22T23:55:00Z
generated_by: test-phase-validator-author (Claude Code subagent dispatch, authoritative)
agent_invocation_simulation: false
phase_count: 7
validator_count: 7
adr_0032_compliance: true
---

# Phase Validators: Execution Pipeline Design (run r1) — v1

## Purpose

This document defines one **Phase Validator** entry per Plan phase in `plan-v2.md`. Each validator is the **gate between phases**: it specifies the assertable conditions that MUST be true before the phase is declared complete and the next phase may begin. Validators are NOT per-task quality checks (those are the L1/L2/L3 verifications in the Plan); validators operate at the **phase-exit boundary**.

Per the test-phase-validator-author discipline + KB-task-decomposition contract:

- Each phase validator consumes its phase's **Exit Criteria** from plan-v2.md as input contract.
- Each validator emits a verdict: `PASS` / `PASS_WITH_DEFERRAL` / `BLOCKED`.
- BLOCKER findings are mandatory phase-blockers (cannot advance).
- MAJOR findings are phase-contract findings (may defer with explicit Scope-Deviation surfacing per ADR-0033).
- MINOR findings are informational (recorded in the run summary; do not block).

## Contents

- [PV-0 — Setup Phase Validator](#pv-0--setup-phase-validator)
- [PV-1 — auditing-shared Scripts Cluster Validator](#pv-1--auditing-shared-scripts-cluster-validator)
- [PV-2 — Skill Installs Validator](#pv-2--skill-installs-validator)
- [PV-3 — Execution-Phase Agent Authoring Validator](#pv-3--execution-phase-agent-authoring-validator)
- [PV-4 — Existing-Agent Extensions + Convention Updates Validator](#pv-4--existing-agent-extensions--convention-updates-validator)
- [PV-5 — Template Authoring Validator](#pv-5--template-authoring-validator)
- [PV-6 — Rollout Validator](#pv-6--rollout-validator)
- [Validator Dependency Graph](#validator-dependency-graph)
- [Critical-Path Validators](#critical-path-validators)
- [Parallelizable Validator Checks](#parallelizable-validator-checks)
- [Shared Validator Infrastructure](#shared-validator-infrastructure)
- [Validator Runbook](#validator-runbook)
- [Severity Rules Summary](#severity-rules-summary)
- [Open Items (Pending Cross-Artifact Audit)](#open-items-pending-cross-artifact-audit)
- [Update History](#update-history)

---

## PV-0 — Setup Phase Validator

### Validator ID
`PV-0`

### Phase Reference
plan-v2.md § "Phase 0 — Setup" (tasks T0.1 through T0.5)

### Validator Goal
Prove that **upstream substrate is ratified and on-disk staging is complete** before any feature-delivery task begins: Blueprint v5 audit verdict is `pass`, the four feature-new ADRs are advanced from `proposed` to `accepted`, the templates directory is writable, the 7 placeholder script files exist at canonical paths, and the `.claude/settings.json` permission allow-list is extended for each of the 7 scripts.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-0.C1** | Blueprint v5 frontmatter shows `version: 5.0.0` AND `status: draft` (ratification to `accepted` occurs at the Plan/Test Authoring Gate per ADR-0017, NOT here). | `grep -E '^version: 5\.0\.0$' blueprint-v5.md && grep -E '^status: draft$' blueprint-v5.md` returns 2 matches. | T0.1 L1 | `grep` invocation in CI / phase-validator script | blocking |
| **PV-0.C2** | Architecture-audit-issues-r7.json shows `verdict: pass`. | `grep '"verdict": "pass"' architecture-audit-issues-r7.json` returns ≥1 match. | T0.1 L1 | `grep` invocation | blocking |
| **PV-0.C3** | Blueprint v4 carries `status: superseded` with `superseded_by: working/feature/execution-pipeline-design-r1/blueprint-v5.md`. | `grep '^status: superseded$' blueprint-v4.md && grep 'superseded_by:.*blueprint-v5\.md' blueprint-v4.md`. | T0.1 L1 | `grep` invocation | blocking |
| **PV-0.C4** | All 4 ADRs (ADR-0032, ADR-0033, ADR-0034, ADR-0035) have frontmatter `status: accepted`. | For each ADR file, `grep '^status: accepted$' <adr-file>` returns ≥1 match. | T0.2 L1 | `grep` over `adrs/ADR-003{2,3,4,5}-*.md` | blocking |
| **PV-0.C5** | `shared-document-reviewer` recognizes the `proposed → accepted` transition as valid per the new per-doc-type vocabulary (ADR-0032 Change 3, ADR 4-state vocab). | Run `shared-document-reviewer` against each of the 4 ADRs; verdict for each must NOT contain a `state_vocabulary_violation` issue. | T0.2 L2 | Subagent invocation (one per ADR) | blocking |
| **PV-0.C6** | Templates directory `.claude/skills/KB-documentation-criteria/references/templates/` exists and is writable. | `[ -d <path> ] && touch <path>/.phase-validator-write-test && rm <path>/.phase-validator-write-test`. | T0.3 L1 | Shell test (validator script) | blocking |
| **PV-0.C7** | 7 placeholder script files exist at canonical paths (5 in auditing-shared/scripts/; 1 in auditing-codespaces/scripts/; 1 in auditing-github-actions/scripts/), each parseable as Python. | `python3 -c "import ast, glob; [ast.parse(open(f).read()) for f in glob.glob('.claude/skills/auditing-shared/scripts/*.py') + glob.glob('.claude/skills/auditing-codespaces/scripts/*.py') + glob.glob('.claude/skills/auditing-github-actions/scripts/*.py')]"` exits 0. | T0.4 L1, L2 | Python ast.parse over file glob | blocking |
| **PV-0.C8** | `.claude/settings.json` parses as valid JSON; allow-list contains entries for all 7 in-scope script basenames + 1 reserved (commented placeholder for scope-deviation-scan future-extensibility). | `python3 -c "import json; json.load(open('.claude/settings.json'))"` exits 0; `grep -c 'validate_pipeline_frontmatter\|log_state_transition\|detect_stubs\|run_phase_checks\|check_pipeline_discipline\|audit_codespaces\|audit_workflow' .claude/settings.json` returns ≥7. | T0.5 L1, L2 | `python3 -c json.load` + grep counts | blocking |
| **PV-0.C9** | Each of the 7 placeholder scripts is invocable under the permission policy without `permission-denied`. | Orchestrator-simulation harness invokes each placeholder script once (e.g., `python3 <path>`); no `permission-denied` error returned. | T0.5 L2 | Permission harness probe | blocking |
| **PV-0.C10** | Audit-r7 report companion `architecture-audit-report-r7.md` is present and references the same issue IDs as `architecture-audit-issues-r7.json`. | `[ -f architecture-audit-report-r7.md ]` AND issue-ID set diff between the two files is empty. | T0.1 L2 | File-exists + JSON/markdown set diff | warning |

### Acceptance Tests Scheduled for This Phase
None directly. Phase 0 is gating/setup; ATs map to feature-delivery phases (1-6). The earliest ATs that depend on PV-0's outputs are in PV-1 (validator + state-transition + stub-detector scripts) which presuppose ADR-0032 ratification and allow-list staging.

### Operational Checks
- **Infrastructure provisioned + reachable:** Working directory exists; canonical script paths are writable. (PV-0.C6, PV-0.C7)
- **Migrations applied successfully:** N/A — no DB migrations in scope (single-layer Claude Code feature).
- **Feature flags declared + default-off:** N/A — no runtime feature flags; ADR ratification is the equivalent governance gate. (PV-0.C4)
- **Observability scaffold live:** N/A in Phase 0 — observability hooks (`log_state_transition.py`) come online in Phase 1.

### Severity Rules
- All 9 blocking criteria (PV-0.C1 through PV-0.C9) MUST pass. Any single failure → `BLOCKED` verdict.
- PV-0.C10 (audit-r7 companion report cross-check) is `warning`. Failure surfaces in the validator log + user-decision request, but does not block Phase 1.

### Failure Response
- PV-0.C1, PV-0.C2, PV-0.C3: Upstream gate not actually passed. **Stop**. Return to Architecture-Audit / Blueprint-supersession discipline. Do NOT proceed to Phase 1.
- PV-0.C4, PV-0.C5: ADR ratification incomplete. Re-run T0.2 (frontmatter status edits + reviewer pass).
- PV-0.C6, PV-0.C7: Working-directory staging incomplete. Re-run T0.3 / T0.4.
- PV-0.C8, PV-0.C9: Permission policy not properly extended. Re-run T0.5 + verify against the allow-list.
- Per Plan § Cross-Phase Dependencies, no rollback past Phase 0 is needed — the changes are purely staging/governance and idempotent to re-apply.

### Validator Metadata
- **When run:** After T0.5 completion claim.
- **Expected duration:** < 2 minutes (all checks are file-existence + grep + 4 subagent invocations).
- **Prerequisites:** None.
- **Manual vs automated:** Fully automatable; PV-0.C5 requires subagent invocation (machine-orchestratable via Claude Code orchestrator harness).

---

## PV-1 — auditing-shared Scripts Cluster Validator

### Validator ID
`PV-1`

### Phase Reference
plan-v2.md § "Phase 1 — auditing-shared scripts cluster" (tasks T1.1 through T1.7)

### Validator Goal
Prove that **all 7 new/relocated scripts are authored, individually correct (L1/L2), and collectively integrated (L3 via T1.7 smoke test)** — and specifically that `validate_pipeline_frontmatter.py` passes its self-test on `blueprint-v5.md` and `plan-v2.md`, and that `log_state_transition.py` accepts the 14-transition payload schema including T0 + T13 boundary transitions per I-AA-609.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-1.C1** | All 7 scripts at canonical paths parse as valid Python AND `--help` prints successfully. | `python3 -c "import ast; ast.parse(open('<path>').read())"` exits 0 for each; `python3 <path> --help` exits 0 for each. | T1.1-T1.7 L1 | Python ast.parse + `--help` probe per script | blocking |
| **PV-1.C2** | `validate_pipeline_frontmatter.py` passes self-checks per Blueprint § Frontmatter validator coverage (rewritten cycle 3 per I-AA-601). Specifically: `memory: none` triggers REJECTION; `Agent` and `TaskUpdate` are SEPARATE tool entries; `Task` is accepted as alias for `Agent`; `Edit` is VALID; `Bash` unrestricted AND `Bash(<pattern>:*)` are BOTH valid; effort enum accepts all 5 values `{low, medium, high, xhigh, max}`. | Run validator against the 6 fixture frontmatter blocks specified in T1.1 L2; assert each produces the expected severity output. | T1.1 L2 | `python3 .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py --self-test` (script provides a self-test mode per spec) | blocking |
| **PV-1.C3** | `validate_pipeline_frontmatter.py` runs cleanly against `blueprint-v5.md` and `plan-v2.md` (zero Level-1 findings; any Level-0 findings are surfaced informationally). | `python3 <validator> working/feature/execution-pipeline-design-r1/blueprint-v5.md working/feature/execution-pipeline-design-r1/plan-v2.md` exits 0 OR exits with only `level: 0` findings. | T1.1 L3 (this PV) | Direct script invocation | blocking |
| **PV-1.C4** | `log_state_transition.py` payload schema covers 14 transitions = 12 substantive (T1-T12) + 2 boundary (T0 INIT→pending, T13 any→TERMINATED) per I-AA-609. | Pipe 3 fixture payloads (one substantive transition + one T0 boundary + one T13 boundary); verify 3 JSONL lines appended with correct fields including `from_state: INIT`/`transition_name: T0` for boundary T0 and `to_state: TERMINATED`/`transition_name: T13` for boundary T13. | T1.2 L2 | Stdin pipe to script + JSONL line inspection | blocking |
| **PV-1.C5** | `log_state_transition.py` failure-mode is observer-only per D-16: invalid payload produces non-blocking failure with finding-surface exit code per AC-FR-5-e. | Pipe an invalid payload (missing required Contract-5 field); verify script does NOT exit non-zero in a way that would block a transition (exit code conforms to the finding-surface contract). | T1.2 L2 | Stdin pipe + exit code inspection | blocking |
| **PV-1.C6** | `detect_stubs.py` Q-CC-2 path-aware patterns: impl-file fixtures produce `severity: blocker` findings; test-file fixtures produce `severity: major`; clean fixtures produce zero findings; legitimate `except KeyError: pass` is NOT flagged. | Run script against 4 fixtures (impl-stub, test-stub, clean, except-pass); assert severity + finding-count per Q-CC-2. | T1.3 L2 | Multi-fixture invocation | blocking |
| **PV-1.C7** | `run_phase_checks.py` aggregates 5 dimensions per Blueprint § Contract 2: tests, audits, validator, discipline, scope_deviations. AC-FR-3-f Level-5 finding emitted when activated layer has no test suite. | Run against 3 synthetic phases (all-clean PASS; one-failing-audit NEEDS_RECONCILIATION; no-test-suite-for-cicd Level-5); assert verdict + dimensional structure per Contract 2. | T1.4 L2 | Multi-fixture invocation + JSON-schema verify | blocking |
| **PV-1.C8** | `check_pipeline_discipline.py` flags `stage 12` references as Level-0; does NOT flag `Phase 1` references (these are Plan phases, not pipeline stages); does NOT flag discipline-number references in `recipe-feature-pipeline/SKILL.md`. | Run against 3 fixtures (stage-by-number positive, Plan-phase negative, discipline-number negative); assert finding count per fixture. | T1.5 L2 | Multi-fixture invocation | blocking |
| **PV-1.C9** | `audit_codespaces.py` stub returns EXACTLY `{"stub": true, "findings": []}` per Q-CC-4. | `python3 .claude/skills/auditing-codespaces/scripts/audit_codespaces.py` stdout parses as JSON; equals exact stub envelope; no extraneous fields. | T1.6 L1, L2 | JSON-equality check | blocking |
| **PV-1.C10** | T1.7 smoke test passes all 4 scenarios (all-clean, mixed-findings, blocker, stub-codespaces-distinguishable). | Invoke `smoke_test_auditing_shared.py` (or analog); exit 0; verbose output shows all 4 scenarios passed. | T1.7 L2 | Smoke-test runner | blocking |
| **PV-1.C11** | Verify the I-AA-609 state-machine 14-transition coverage in `log_state_transition.py` schema: T0 + T13 are present AND do NOT increment cycle counters (Invariant 10 scope limited to T4 + T10 only). | Inspect script source for an explicit cycle-counter scoping check (e.g., a constant `CYCLE_COUNTER_TRANSITIONS = {"T4", "T10"}`) OR run a fixture invocation that asserts the counter delta is zero for T0/T13 logged transitions. | T1.2 L2 | Source inspection + fixture invocation | blocking |
| **PV-1.C12** | All 7 scripts emit finding objects conforming to Blueprint § Field Propagation Map finding schema (`level`, `severity`, `path`, `description`, `dimension`, `dispatch_target`). | Verify each script's emitted JSON output against the canonical finding schema (jsonschema validation or equivalent). | T1.1-T1.6 L2 | jsonschema validation in T1.7 smoke test | blocking |

### Acceptance Tests Scheduled for This Phase
- AC-FR-6-a, -b, -c (validator script behavior — checked at PV-1.C2, C3)
- AC-FR-5-a, -b, -c, -d, -e (state-transition logging — checked at PV-1.C4, C5, C11)
- AC-FR-2-d / Q-CC-2 (stub detection — checked at PV-1.C6)
- AC-FR-3-a, -b, -c, -f (phase-quality coordinator — checked at PV-1.C7)
- AC-OP-2 (discipline-5 mechanical enforcement — checked at PV-1.C8)
- AC-FR-8-b / Q-CC-4 (codespaces stub envelope — checked at PV-1.C9)
- AC-FR-9-c (frontmatter-validator behavior; the binding-check is exercised in PV-3 against the 5 new agent files)

(Final AT-NNN IDs assigned by test-acceptance-author; this list is the AC-reference baseline.)

### Operational Checks
- **Tests pass:** PV-1.C10 (T1.7 smoke test). Phase-specific: this is the substrate test, not an end-to-end test.
- **Performance budgets met:** Phase-1 deliverable is script substrate; no perf budgets per Blueprint (single-script invocations are sub-second).
- **Error rates within thresholds:** N/A — Phase 1 substrate is not runtime-deployed yet.
- **Rollback path drilled:** N/A — scripts are additive; `git revert` is the rollback per ADR-0005.
- **Observability hook live:** PV-1.C4 confirms `log_state_transition.py` is functional. This validator marks the observability scaffold's substrate-test pass.

### Severity Rules
- All 12 criteria are **blocking**. No `warning` because PV-1's deliverable is foundational for Phase 3 + Phase 6 (the script cluster IS the auditing substrate; partial functioning here breaks downstream).
- Per AC-FR-5-e specifically, the validator's invariant-checking severity logic mirrors the observer-only hook semantics: a script that itself fails to load is a blocker; a script that emits a Level-1 finding against fixtures is also a blocker.

### Failure Response
- PV-1.C1 (script parse): correct script source; re-run validator.
- PV-1.C2 (validator self-test): the validator's vocab tables are wrong; per Open Item #3, the staged authoring approach means T1.1 codes against Blueprint as substrate, then tightens to shared-conventions.md after T4.1. **If failure occurs post-T4.1, the tightening commit is incorrect** — re-author the vocab tables.
- PV-1.C4 (state-transition payload schema): re-author per Contract 5 + I-AA-609 explicit T0/T13 inclusion.
- PV-1.C6 (stub patterns): re-author Q-CC-2 path-aware logic per Blueprint § Q-CC-N Arbitration.
- PV-1.C7 (run_phase_checks aggregation): verify Contract 2 5-dimensional rollup logic.
- PV-1.C10 (smoke test): debug failing scenario; re-run.
- **No rollback past Phase 1 needed**: scripts are additive; revert is per-script.

### Validator Metadata
- **When run:** After T1.7 completion claim.
- **Expected duration:** ~5-8 minutes (12 script invocations + smoke test).
- **Prerequisites:** PV-0 PASS.
- **Manual vs automated:** Fully automatable.

---

## PV-2 — Skill Installs Validator

### Validator ID
`PV-2`

### Phase Reference
plan-v2.md § "Phase 2 — Skill installs (extract / stub / new install)" (tasks T2.1 through T2.3)

### Validator Goal
Prove that **all 3 skills are present at canonical paths** before Phase 3 agent authoring begins — specifically, per AC-FR-9-e, that `ai-development-guide` exists so the Phase-3 frontmatter validator (T1.1) will NOT reject `execute-task-code-producer` and `execute-task-quality-handler` for binding a non-existent skill. This validator enforces the hard sequencing gate between Phase 2 and Phase 3.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-2.C1** | All 3 skill directories exist at canonical paths: `.claude/skills/ai-development-guide/`, `.claude/skills/auditing-github-actions/`, `.claude/skills/auditing-codespaces/`. | `[ -d <path> ]` for each of the 3 directories. | T2.1, T2.2, T2.3 L1 | Shell file-test loop | **blocking** (gates Phase 3 per AC-FR-9-e) |
| **PV-2.C2** | Each skill's `SKILL.md` exists; frontmatter parses; T1.1 frontmatter validator passes against each `SKILL.md`. | `[ -f <path>/SKILL.md ] && python3 <validator> <path>/SKILL.md` exits 0 with no Level-1 findings. | T2.1, T2.2, T2.3 L1 | T1.1 frontmatter validator invocation per SKILL.md | **blocking** |
| **PV-2.C3** | `git log --follow .claude/skills/auditing-github-actions/scripts/audit_workflow.py` shows historical commits from the prior path (`KB-github-actions-platform`), proving `git mv` was used. | `git log --follow --oneline .claude/skills/auditing-github-actions/scripts/audit_workflow.py \| wc -l` returns ≥2 commits (the move + at least one prior). | T2.1 L2 | `git log --follow` line-count check | blocking |
| **PV-2.C4** | `git log --follow .claude/skills/auditing-github-actions/references/action_versions.md` shows historical commits. | Same pattern as PV-2.C3 against `action_versions.md`. | T2.1 L2 | `git log --follow` line-count check | blocking |
| **PV-2.C5** | `KB-github-actions-platform/SKILL.md` Contents list has been updated per AC-FR-8-e to point to the new `auditing-github-actions` skill for audit functionality. | `grep -E 'auditing-github-actions' .claude/skills/KB-github-actions-platform/SKILL.md` returns ≥1 match. | T2.1 L1 | grep | blocking |
| **PV-2.C6** | `auditing-codespaces/scripts/audit_codespaces.py` is the stub file from T1.6 (referenced by T2.2); invoking it returns the canonical stub envelope. | `python3 .claude/skills/auditing-codespaces/scripts/audit_codespaces.py` stdout parses as JSON equal to `{"stub": true, "findings": []}`. | T2.2 L1, T1.6 L2 | Direct invocation | blocking |
| **PV-2.C7** | `ai-development-guide/SKILL.md` body documents the 4-phase pattern (lint → build → test → final gate). | `grep -iE 'lint\|build\|test\|final[ -]gate' .claude/skills/ai-development-guide/SKILL.md` returns matches covering all 4 phases (or per spec's phase-naming convention). | T2.3 L1 | grep coverage check | blocking |
| **PV-2.C8** | Each of the 3 skills loads in a test agent invocation harness without binding errors. | Subagent harness probe: spawn a minimal test agent that binds each skill in turn; verify `/agents`-equivalent listing shows the skill's body is in context. | T2.1, T2.2, T2.3 L2 | Subagent invocation probe | blocking |
| **PV-2.C9** | **AC-FR-9-e sequencing gate**: `ai-development-guide` is present at canonical path AND can be referenced in a `skills:` frontmatter field without triggering T1.1 validator's `skill_not_found` finding. | Construct a synthetic agent frontmatter with `skills: [ai-development-guide]`; run T1.1 validator; assert NO `skill_not_found` finding. | T2.3 L1, gates T3.2, T3.3 | T1.1 validator invocation against synthetic agent | **blocking — this is the AC-FR-9-e sequencing enforcement** |
| **PV-2.C10** | **AC-FR-9-e completeness**: ALL 3 skills (`ai-development-guide`, `auditing-shared` (pre-existing — should already pass), `auditing-github-actions`, `auditing-codespaces`) can be referenced in any Phase-3 agent's `skills:` field without `skill_not_found`. | Construct synthetic agents binding each of the 4 skills in `auditing-shared` family + `ai-development-guide`; T1.1 validator emits zero `skill_not_found` findings. | T2.1, T2.2, T2.3 + T0 substrate | T1.1 validator + synthetic-agent batch | **blocking — extension of AC-FR-9-e to the full Phase-3 skill-binding surface per I-AA-603 / ADR-0035** |

### Acceptance Tests Scheduled for This Phase
- AC-FR-8-a (auditing-github-actions extraction with history preservation — PV-2.C3, C4)
- AC-FR-8-b (auditing-codespaces stub — PV-2.C6)
- AC-FR-8-c (helpers in auditing-shared — substrate already in Phase 1; pattern verified)
- AC-FR-8-e (KB-github-actions-platform SKILL.md update — PV-2.C5)
- AC-FR-9-a, -b, -c, -d, -e (ai-development-guide install + sequencing — PV-2.C7, C9, C10)
- Q-CC-4 (codespaces stub semantics — PV-2.C6)

(Final AT-NNN IDs assigned by test-acceptance-author.)

### Operational Checks
- **Skills installed at canonical paths:** PV-2.C1, C2.
- **History preserved on git-mv:** PV-2.C3, C4 — critical because per IN-002 resolution, copy-and-delete loses commit history and breaks downstream blame/audit.
- **Sequencing gate to Phase 3 ENFORCED:** PV-2.C9, C10 — this is the canonical AC-FR-9-e enforcement. **Phase 3 MAY NOT begin until this validator passes.**
- **Rollback path drilled:** Two-step rollback if needed: (a) `git mv` reverse for auditing-github-actions; (b) `rm -rf` the two new skill directories. Per ADR-0005, all rollbacks are version-controlled.

### Severity Rules
- All 10 criteria are **blocking**. PV-2.C9 and PV-2.C10 are the canonical AC-FR-9-e sequencing enforcers; failure of either MUST block Phase 3 entry — this is the load-bearing assertion of this validator.

### Failure Response
- PV-2.C1, C2, C7: Re-author missing skill or fix `SKILL.md` parse error.
- PV-2.C3, C4: **Critical** — if `git mv` was NOT used (copy-and-delete instead), undo by reverting the copy + replaying the move correctly. Document the rollback in run summary.
- PV-2.C5: Update `KB-github-actions-platform/SKILL.md` Contents list.
- PV-2.C6: Re-author the stub envelope exactly per Q-CC-4 contract.
- PV-2.C9, C10: **DO NOT advance to Phase 3.** Re-run the install task (T2.3 for ai-development-guide; T2.1 for auditing-github-actions; T2.2 for auditing-codespaces). Re-run PV-2 in full.

### Validator Metadata
- **When run:** After T2.3 completion claim (all 3 skills installed).
- **Expected duration:** ~3-4 minutes.
- **Prerequisites:** PV-1 PASS (T1.1 validator script exists for PV-2.C9/C10 to invoke).
- **Manual vs automated:** Fully automatable.

---

## PV-3 — Execution-Phase Agent Authoring Validator

### Validator ID
`PV-3`

### Phase Reference
plan-v2.md § "Phase 3 — Execution-phase agent authoring" (tasks T3.1 through T3.5)

### Validator Goal
Prove that **all 5 execute-* agents are authored with cycle-3-corrected frontmatters** (Bash unrestricted on T3.3 per I-AA-602; Write on T3.1 per I-AA-608; auditing-shared in skills on T3.1/T3.3/T3.4/T3.5 per I-AA-603 / ADR-0035, NOT on T3.2 per single-script criterion), pass T1.1 frontmatter validator, are visible in `/agents`, can be spawned without binding errors, and that the 14-transition state machine (12 substantive + 2 boundary per I-AA-609) is implemented in T3.1's body.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-3.C1** | All 5 agent files exist at `.claude/agents/execute-*.md` with correct names: `execute-orchestrator.md`, `execute-task-code-producer.md`, `execute-task-quality-handler.md`, `execute-phase-quality-reviewer.md`, `execute-finalize-reconciler.md`. | `ls .claude/agents/execute-*.md \| wc -l` returns 5 with the canonical filenames. | T3.1-T3.5 L1 | Filesystem ls + filename match | blocking |
| **PV-3.C2** | All 5 agent files pass `validate_pipeline_frontmatter.py` (T1.1) with zero Level-1 findings. | `python3 <validator> .claude/agents/execute-*.md` exits 0 OR exits with only Level-0 findings. | T3.1-T3.5 L1 | T1.1 validator batch invocation | **blocking — primary AC-FR-9-c assertion against the 5 new agent files** |
| **PV-3.C3** | **T3.1 frontmatter cycle-3 corrections present** (I-AA-608 + I-AA-603/ADR-0035): `Write` IS in `tools`; `auditing-shared` IS in `skills`; `Agent` and `TaskUpdate` are SEPARATE entries in `tools`; `memory: project`; `effort: high`. | grep over `execute-orchestrator.md` frontmatter for the 5 conditions. | T3.1 L1 | Frontmatter pattern matching | **blocking — I-AA-608, I-AA-603, I-AA-601 enforcement** |
| **PV-3.C4** | **T3.3 frontmatter cycle-3 correction present** (I-AA-602): `Bash` is UNRESTRICTED in `tools` (the bare `Bash` form, NOT `Bash(python3:*)`); `auditing-shared` IS in `skills`; `ai-development-guide` IS in `skills`; `memory` field is ABSENT; `Write` is ABSENT. | grep over `execute-task-quality-handler.md` frontmatter; assert exact 5 conditions. | T3.3 L1 | Frontmatter pattern matching | **blocking — I-AA-602 enforcement** |
| **PV-3.C5** | **T3.2 frontmatter is NEGATIVE on `auditing-shared` binding per ADR-0035 single-script criterion**: `ai-development-guide` IS in `skills`; `auditing-shared` is ABSENT; `memory` field is ABSENT; `Edit` is present; `Bash` (unrestricted) is present. | grep over `execute-task-code-producer.md` frontmatter; assert exact 4 conditions. | T3.2 L1 | Frontmatter pattern matching | **blocking — ADR-0035 single-script-criterion enforcement** |
| **PV-3.C6** | **T3.4 frontmatter cycle-3 correction present**: `Bash(python3:*)` restriction is present; `auditing-shared` IS in `skills` (I-AA-603); `Write` is present (owns phase-quality-report); `Agent` and `Edit` are ABSENT; `memory` is OMITTED. | grep over `execute-phase-quality-reviewer.md` frontmatter; assert exact 5 conditions. | T3.4 L1 | Frontmatter pattern matching | blocking |
| **PV-3.C7** | **T3.5 frontmatter cycle-3 correction present**: `Agent` IS in `tools` (re-invokes upstream agents); `Write` IS in `tools`; `auditing-shared` IS in `skills` (I-AA-603); `memory: project`; `TaskCreate`/`TaskUpdate` ABSENT. | grep over `execute-finalize-reconciler.md` frontmatter; assert exact 5 conditions. | T3.5 L1 | Frontmatter pattern matching | blocking |
| **PV-3.C8** | All 5 agents visible in `/agents`-equivalent listing in a fresh Claude Code test session. | `claude-code /agents` (or harness equivalent) lists all 5 execute-* agents. | T3.1-T3.5 L2 | CC session probe | blocking |
| **PV-3.C9** | All 5 agents spawnable without binding errors. | For each of 5 agents, dispatch a no-op test invocation; verify no `skill_not_found` / `tool_not_recognized` errors. | T3.1-T3.5 L2 | Subagent dispatch harness × 5 | blocking |
| **PV-3.C10** | **I-AA-609 14-transition state machine implemented in T3.1 body**. Specifically: orchestrator body enumerates 12 substantive transitions (T1-T12) + 2 boundary (T0 INIT→pending, T13 any→TERMINATED); the state-machine description is parseable. | `grep -E 'T0\|T13' .claude/agents/execute-orchestrator.md` returns ≥2 matches; the document contains an explicit table or list of all 14 transitions; grep for boundary transition names "INIT" and "TERMINATED" each returns ≥1 match. | T3.1 body content L1 | grep + structural inspection | **blocking — I-AA-609 enforcement** |
| **PV-3.C11** | **No agent declares a skill that doesn't exist on disk** (extends AC-FR-9-c to the full Phase-3 agent surface). | For each agent's `skills:` field, verify each named skill has a corresponding `.claude/skills/<skill-name>/SKILL.md` file. | T3.1-T3.5 L1 | Skill-existence cross-check per agent | **blocking — AC-FR-9-c primary enforcement against Phase 3 output** |
| **PV-3.C12** | **Invariant 10 scoping in T3.1 body**: cycle-counter equivalence invariant explicitly scoped to T4 + T10 transitions only (per I-AA-609 cycle-3 clarification — T0/T13 do NOT increment counters). | Inspect `execute-orchestrator.md` body for explicit text scoping invariant-10 to T4/T10. | T3.1 body content L1 | Structural inspection / grep | blocking |
| **PV-3.C13** | **Reconciliation budget tracking (ADR-0017 4-cycle cap) visible in T3.1 + T3.5 bodies**: both agents reference ADR-0017 + the 4-cycle cap; T3.5 body describes budget-exhausted artifact emission per AC-FR-10-c. | `grep -E 'ADR-0017\|4-cycle\|budget[ -]exhaust' .claude/agents/execute-orchestrator.md .claude/agents/execute-finalize-reconciler.md` returns matches in both files. | T3.1 + T3.5 body content L1 | grep | blocking |
| **PV-3.C14** | **PRD ADR-0021 transcription artifact**: T3.5 body cites **ADR-0017** for the 4-cycle cap canonical home (NOT ADR-0021, which is the PRD transcription artifact per I-AA-604 / ADR-0034). | `grep 'ADR-0021' .claude/agents/execute-finalize-reconciler.md` returns 0 matches in the budget-cap context; ADR-0017 cited instead. | T3.5 body content L1, I-AA-604 | grep negative + positive | blocking |

### Acceptance Tests Scheduled for This Phase
- AC-FR-1-a, -b, -c, -d (orchestrator owns stage sequence — PV-3.C10)
- AC-FR-2-a, -b, -c, -d, -e, -f (per-task verdict dispatch — exercised at PV-3.C9 + PV-6.C2 smoke test)
- AC-FR-3-a, -e (orchestrator transitions — PV-3.C10)
- AC-FR-4-a through -f (dispatch matrix in T3.5 — PV-3.C7, C13)
- AC-FR-5-a, -b, -c (orchestrator fires hooks — exercised at smoke test PV-6)
- AC-FR-9-a, -b, -c (ai-development-guide binding — PV-3.C2, C5, C11; primary AC-FR-9-c enforcement)
- AC-FR-10-a, -b, -c, -d (4-cycle cap — PV-3.C13, C14)
- AC-FR-12-a (audit-counter delta in frontmatter — exercised at PV-6 smoke test)

### Operational Checks
- **Frontmatter cycle-3 corrections enforced:** PV-3.C3, C4, C5, C6, C7 — these are I-AA-602/603/608/609/601 enforcement points.
- **AC-FR-9-c skill-existence check passes:** PV-3.C2, C11.
- **State machine 14-transition coverage:** PV-3.C10, C12 — I-AA-609 enforcement.
- **Reconciliation budget tracking ratified:** PV-3.C13, C14 — ADR-0017 canonical-home enforcement (NOT ADR-0021).
- **Rollback path drilled:** `git revert` per agent file; agents are additive and idempotent.

### Severity Rules
- All 14 criteria are **blocking**. The cycle-3 corrections (PV-3.C3-C7) and AC-FR-9-c enforcement (PV-3.C2, C11) are the load-bearing assertions; failure of any single corresponds directly to an audit-r7 issue that the Blueprint v5 resolved.

### Failure Response
- PV-3.C2 (validator fails): Identify which agent + which field; correct per Blueprint § Agent Frontmatter Specifications (verbatim copy is the contract).
- PV-3.C3-C7 (cycle-3 corrections missing): Re-author the specific frontmatter field. **These are the cycle-3 corrections; failure here means the agent author did NOT consult Blueprint v5 — re-read Blueprint v5 § Agent Frontmatter Specifications verbatim.**
- PV-3.C10 (14 transitions missing): Re-author orchestrator body per Blueprint § State Transitions table; include T0 + T13 explicit boundary entries.
- PV-3.C11 (skill missing): Confirm PV-2 actually passed; if a skill was renamed since, update the agent's `skills:` field.
- PV-3.C14 (ADR-0021 citation): Replace with ADR-0017 per I-AA-604 / ADR-0034 forward correction.

### Validator Metadata
- **When run:** After T3.5 completion claim.
- **Expected duration:** ~5-7 minutes (frontmatter grep + 5 agent-spawn probes + skill-existence cross-check + body-content inspection).
- **Prerequisites:** PV-2 PASS (skills must exist for PV-3.C11 to succeed).
- **Manual vs automated:** Fully automatable; PV-3.C8 / C9 require subagent harness.

---

## PV-4 — Existing-Agent Extensions + Convention Updates Validator

### Validator ID
`PV-4`

### Phase Reference
plan-v2.md § "Phase 4 — Existing-agent extensions + convention updates" (tasks T4.1 through T4.4)

### Validator Goal
Prove that **shared-conventions.md v1 → v2 spec edits are landed** (all 5 ADR-0032 changes), `shared-document-reviewer` body is extended to dispatch on `doc_type` for all 25 doc_types (20 planning + 5 execution-phase per ADR-0032), and existing planning-side agents (`design-cicd`, `design-codespaces`) additionally bind the corresponding `auditing-X` skills per AC-FR-8-f.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-4.C1** | `shared-conventions.md` contains all 5 ADR-0032 changes per Blueprint § Conventions Touched. | grep for each change-marker: `feature_slug` as universal-required; user-token chain section header; 3-tier per-doc-type vocabulary; `doc_type` universal-required field with 25-value enum (20 planning + 5 execution-phase); "Execution-phase artifact frontmatter" section header. | T4.1 L1 | grep × 5 marker checks | **blocking — primary ADR-0032 enforcement** |
| **PV-4.C2** | `shared-conventions.md` parses cleanly (no broken markdown structure); shared-document-reviewer Gate-0 passes. | Run `shared-document-reviewer` against the file; Gate-0 verdict is not `rejected`. | T4.1 L1 | Subagent invocation | blocking |
| **PV-4.C3** | T1.1 frontmatter validator runs against existing project artifacts (excluding historical-archive scope per AC-FR-11-d) and emits only additive findings (no false-positives for pre-existing artifacts). | Run T1.1 validator against `working/feature/execution-pipeline-design-r1/*.md` + `adrs/*.md` + `.claude/agents/*.md`; assert findings are additive (no Level-1 for missing `doc_type` on historical artifacts dated before implementation). | T4.1 L2 | T1.1 validator batch invocation + finding-classification | **blocking — AC-FR-11-d scope enforcement** |
| **PV-4.C4** | `shared-document-reviewer.md` body now dispatches on `doc_type` for all 25 doc_types (20 planning + 5 execution-phase). | `grep -cE 'per-task-execution-result\|phase-quality-report\|quality-reconciliation-log\|state-transitions-log\|pipeline-run-summary' .claude/agents/shared-document-reviewer.md` returns ≥5 matches; planning-side 20 doc_types similarly cited. | T4.2 L1 | grep coverage check | blocking |
| **PV-4.C5** | `shared-document-reviewer.md` frontmatter is unchanged per Plan T4.2 spec (tools/skills stay the same per ADR-0005). | `git diff <prior-rev> .claude/agents/shared-document-reviewer.md` shows frontmatter block is unmodified or modified only in a non-substantive way (e.g., comment addition); `tools:` and `skills:` lists are unchanged. | T4.2 L1 | git diff frontmatter inspection | blocking |
| **PV-4.C6** | `shared-document-reviewer.md` passes T1.1 frontmatter validator with the updated body. | `python3 <validator> .claude/agents/shared-document-reviewer.md` exits 0. | T4.2 L1 | T1.1 validator invocation | blocking |
| **PV-4.C7** | `design-cicd` agent's `skills:` field additionally binds `auditing-github-actions` per AC-FR-8-f. | `grep 'auditing-github-actions' .claude/agents/design-cicd.md` returns ≥1 match in the `skills:` field; `KB-github-actions-platform` is also still present (additionally bound, not replaced). | T4.3 L1 | grep + structural check | blocking |
| **PV-4.C8** | `design-cicd.md` passes T1.1 frontmatter validator. | `python3 <validator> .claude/agents/design-cicd.md` exits 0. | T4.3 L1 | T1.1 validator invocation | blocking |
| **PV-4.C9** | `design-codespaces` agent's `skills:` field additionally binds `auditing-codespaces` per AC-FR-8-f. | `grep 'auditing-codespaces' .claude/agents/design-codespaces.md` returns ≥1 match in `skills:`. | T4.4 L1 | grep + structural check | blocking |
| **PV-4.C10** | `design-codespaces.md` passes T1.1 frontmatter validator. | `python3 <validator> .claude/agents/design-codespaces.md` exits 0. | T4.4 L1 | T1.1 validator invocation | blocking |
| **PV-4.C11** | Sample `per-task-execution-result.md` (manual fixture) correctly dispatches in `shared-document-reviewer` to the new analysis/log 3-state vocab branch. | Subagent invocation: pass fixture artifact → reviewer; verdict includes correct dispatch (`doc_type: per-task-execution-result` recognized; analysis/log 3-state vocab applied). | T4.2 L2 | Subagent invocation against fixture | blocking |
| **PV-4.C12** | T1.1 validator's vocabulary tables are now (post-T4.1) sourced from `shared-conventions.md` v2 per Open Item #3 tightening commit. | grep `shared-conventions` in `validate_pipeline_frontmatter.py` source returns ≥1 reference to the post-T4.1 spec file as the canonical source. | T1.1 tightening per Open Item #3 | grep | warning |

### Acceptance Tests Scheduled for This Phase
- AC-FR-11-a (canonical state vocabulary in shared-conventions.md — PV-4.C1)
- AC-FR-11-b (templates use default `status:` from canonical vocab — checked at PV-5)
- AC-FR-11-c (validator flags non-canonical status — checked at PV-1; extended here)
- AC-FR-11-d (historical-archive scope — PV-4.C3)
- AC-FR-11-e (ADR-0032 pins vocabulary — substrate at PV-0)
- AC-FR-6-d (validator runs at every gate; reviewer recognizes new doc_types — PV-4.C4, C11)
- AC-FR-8-d, -f (caller agents bind auditing-X — PV-4.C7, C9)

### Operational Checks
- **Spec evolution in-place per ADR-0005:** PV-4.C1, C2 — shared-conventions.md is a knowledge-base reference, updated in-place via git commit (not versioned per per-doc-type vocab).
- **Backward compatibility:** PV-4.C3 — additive-only property of the new schemas; historical artifacts not flagged.
- **Reviewer dispatch on doc_type:** PV-4.C4, C11.
- **Skill rebindings:** PV-4.C7, C9 — design-cicd + design-codespaces.

### Severity Rules
- PV-4.C1 through PV-4.C11 are **blocking** (the spec edit is foundational; the reviewer dispatch is the gate; the skill rebindings are explicit AC-FR-8-f deliverables).
- PV-4.C12 (T1.1 tightening commit to source from shared-conventions.md) is **warning**: it improves the dependency chain but is not blocking if the validator's hard-coded vocab tables (from T1.1 staged authoring) match the v2 spec content.

### Failure Response
- PV-4.C1 missing changes: Re-edit `shared-conventions.md` per ADR-0032 5 changes. Verify against Blueprint § Conventions Touched.
- PV-4.C3 false-positives on historical artifacts: Fix T1.1 validator's scope-to-post-implementation-date logic; this is the AC-FR-11-d enforcement.
- PV-4.C4 missing dispatch: Re-author `shared-document-reviewer.md` body to add the 5 execution-phase doc_type dispatch branches.
- PV-4.C7, C9 missing bindings: Re-edit the existing agent's `skills:` frontmatter to additionally include the corresponding `auditing-X` skill.
- **Rollback per ADR-0005**: All Phase 4 changes are version-controlled; `git revert` restores prior state.

### Validator Metadata
- **When run:** After T4.4 completion claim.
- **Expected duration:** ~4-5 minutes.
- **Prerequisites:** PV-2 PASS, PV-3 PASS (the existing-agent updates conceptually depend on the auditing-X skills landing in Phase 2).
- **Manual vs automated:** Fully automatable.

---

## PV-5 — Template Authoring Validator

### Validator ID
`PV-5`

### Phase Reference
plan-v2.md § "Phase 5 — Template authoring for new artifact types" (tasks T5.1 through T5.5)

### Validator Goal
Prove that **all 5 new templates exist at canonical paths**, parse correctly, pass T1.1 frontmatter validator, conform to existing template-structure conventions in the same directory, and that the Blueprint § AC-FR-7 floor coverage Path B disposition is honored: 4 of 5 floor items are covered by templates (per-task-execution-result, phase-quality-report, quality-reconciliation-log, pipeline-run-summary) + 1 beyond-floor item (state-transitions-log-entry), with the 5th floor item (frontmatter-validation report) covered by the script-output schema inline in `validate_pipeline_frontmatter.py` source (T1.1). The I-AA-606 bidirectional cross-reference with ADR-0033 §Context is preserved.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-5.C1** | All 5 templates exist at canonical paths in `.claude/skills/KB-documentation-criteria/references/templates/`: `per-task-execution-result-template.md`, `phase-quality-report-template.md`, `quality-reconciliation-log-template.md`, `state-transitions-log-entry-template.md`, `pipeline-run-summary-template.md`. | `ls .claude/skills/KB-documentation-criteria/references/templates/*-template.md` includes each of the 5 filenames. | T5.1-T5.5 L1 | Filesystem ls + filename match | blocking |
| **PV-5.C2** | All 5 templates pass T1.1 frontmatter validator (zero Level-1 findings). | `python3 <validator> <path>/*-template.md` exits 0 OR with only Level-0 findings, for each of the 5 new templates. | T5.1-T5.5 L1 | T1.1 validator batch invocation | blocking |
| **PV-5.C3** | All 5 templates' frontmatter use the default `status:` value drawn from the canonical vocab per ADR-0032 (per AC-FR-11-b). For analysis/log doc_types: `status: draft` (3-state default). For pipeline-run-summary: same analysis/log 3-state default. | grep `status:` field in each template; assert each default is in the per-doc-type canonical vocab per shared-conventions.md v2. | T5.1-T5.5 L1 | grep + cross-check against shared-conventions.md | blocking |
| **PV-5.C4** | `per-task-execution-result-template.md` body includes `## Scope Deviations` section per ADR-0033 surfacing requirement (Blueprint § Risk 7 + ADR-0033 §Context Path B). | `grep '## Scope Deviations' <template>` returns ≥1 match. | T5.1 L1 | grep | **blocking — ADR-0033 surfacing enforcement** |
| **PV-5.C5** | `phase-quality-report-template.md` body documents D-13 5-dimensional verdict structure (tests, audits, validator, discipline, scope_deviations per Blueprint § Contract 2) + audit-counter delta schema per Contract 3. | grep for each of the 5 dimension names; grep for "audit_baseline" / "audit_final" / "audit_counter_delta" terminology. | T5.2 L1 | grep coverage check | blocking |
| **PV-5.C6** | `quality-reconciliation-log-template.md` body documents per-cycle dispatch-records structure per Contract 4 (8-row dispatch taxonomy); cycle counter per D-12; outcome enum `{CONVERGED, RECONCILIATION_EXHAUSTED}`. | grep for "CONVERGED" + "RECONCILIATION_EXHAUSTED" + dispatch-row references; assert all 8 rows documented per machine-parseable schema. | T5.3 L1 | grep + structural inspection | blocking |
| **PV-5.C7** | `state-transitions-log-entry-template.md` documents the JSONL entry schema per Contract 5, including T0 + T13 boundary transition coverage per I-AA-609. | grep for "T0", "T13", "INIT", "TERMINATED" in the template; assert each transition name documented. | T5.4 L1 | grep | **blocking — I-AA-609 enforcement** |
| **PV-5.C8** | `pipeline-run-summary-template.md` defines the fields per Blueprint § Data Representation Decision 3: `run_id`, `feature_slug`, start/end timestamps, per-stage gate outcomes, total reconciliation cycles, findings dispatched per level, final ship status. | grep for each field name; assert all present in template. | T5.5 L1 | grep coverage check | blocking |
| **PV-5.C9** | **I-AA-606 cross-reference preserved**: `pipeline-run-summary-template.md` (or its derived_from / cross-references) cites both Blueprint § AC-FR-7 floor coverage Path B AND ADR-0033 §Context. | grep for both references in `pipeline-run-summary-template.md`. | T5.5 L1, I-AA-606 | grep × 2 | blocking |
| **PV-5.C10** | **AC-FR-7-c floor coverage verified**: 4 of 5 floor items covered by templates (per-task execution log, phase-quality report, quality-reconciliation log, execution-reconciliation log = pipeline-run-summary per Path B equivalence); 5th floor item (frontmatter-validation report) covered by `validate_pipeline_frontmatter.py` source schema (NOT a separate template). | Verify by structural inspection: 5 templates present; T1.1 source contains the `frontmatter-validation report` schema in code; cross-reference resolves at audit time. | T5.1-T5.5 + T1.1 L2, Blueprint § AC-FR-7 floor coverage Path B | Structural cross-check | **blocking — Path B disposition enforcement** |
| **PV-5.C11** | Each template's structure is consistent with existing templates in the same directory (use of `---` frontmatter delimiters; conventional section headers; body completion checklist per plan/prd template patterns). | Compare template structure against `prd-template.md`, `blueprint-template.md`, `plan-template.md`; assert structural similarity. | T5.1-T5.5 L1 | Structural inspection / template-similarity check | warning |
| **PV-5.C12** | A sample artifact authored from each template parses and is acceptable to `shared-document-reviewer` (post-T4.2) for the corresponding doc_type. | For each of 5 templates, author a sample artifact; invoke `shared-document-reviewer`; verdict not `rejected`. | T5.1-T5.5 L2 | Subagent invocation × 5 | blocking |

### Acceptance Tests Scheduled for This Phase
- AC-FR-7-a (each artifact has `-template.md` file — PV-5.C1)
- AC-FR-7-b (frontmatter schemas in shared-conventions.md "Execution-phase artifact frontmatter" — substrate at PV-4)
- AC-FR-7-c (5 floor items covered — PV-5.C10)
- AC-FR-7-d (beyond-floor artifacts conform to -a + -b — PV-5.C2 for state-transitions-log-entry)
- AC-FR-11-b (templates use canonical-vocab default `status:` — PV-5.C3)
- AC-FR-12-a (audit-counter delta schema substrate — PV-5.C5)
- AC-FR-13-a, -b (machine-parseable + analytics-extractable — PV-5.C6)

### Operational Checks
- **Path B disposition honored:** PV-5.C10 — the 5th floor item is NOT a separate template (it's the T1.1 script's output schema). This is the Blueprint v5 cycle-3 explicit decision; failure here means the Plan/Test/Validator authors did not honor Blueprint § AC-FR-7 floor coverage Path B.
- **I-AA-606 bidirectional cross-reference preserved:** PV-5.C9 — ADR-0033 §Context references Blueprint § AC-FR-7 floor coverage Path B AND vice versa.
- **Scope-deviation surfacing in template:** PV-5.C4 — per ADR-0033, the `per-task-execution-result` template MUST include a Scope Deviations section.

### Severity Rules
- 11 of 12 criteria are **blocking**. PV-5.C11 (structural similarity to existing templates) is **warning**: divergence is acceptable if rationalized in the template's body, but pure parsing/correctness is captured by C2.

### Failure Response
- PV-5.C1 missing template: Re-author at canonical path.
- PV-5.C2, C3 frontmatter issues: Verify against shared-conventions.md v2 "Execution-phase artifact frontmatter" section + ADR-0032 enum.
- PV-5.C4 missing Scope Deviations section: Re-author per-task-execution-result template per ADR-0033.
- PV-5.C9 cross-reference broken: Update template + verify ADR-0033 §Context still cites Blueprint § AC-FR-7 floor coverage Path B.
- PV-5.C10 Path B disposition violated: Re-read Blueprint § AC-FR-7 floor coverage Path B; the 5th floor item is intentionally NOT a separate template — confirm T1.1's source contains the inline schema.

### Validator Metadata
- **When run:** After T5.5 completion claim.
- **Expected duration:** ~3-4 minutes (template grep + 5 sample-artifact reviewer invocations).
- **Prerequisites:** PV-4 PASS (`shared-conventions.md` v2 + `shared-document-reviewer` body update must exist for PV-5.C12).
- **Manual vs automated:** Fully automatable; PV-5.C12 requires subagent harness.

---

## PV-6 — Rollout Validator

### Validator ID
`PV-6`

### Phase Reference
plan-v2.md § "Phase 6 — Rollout (planning-side doc_type backfill option + end-to-end smoke test)" (tasks T6.1 and T6.2)

### Validator Goal
Prove that **(a)** T6.1 disposition (Posture A defer vs Posture B execute) is recorded per ADR-0029 + ADR-0033 no-silent-absorption discipline; and **(b)** the T6.2 end-to-end smoke test passes L1/L2/L3 — specifically, all 14 state transitions (T0 + T1-T12 + T13) observed at least once; all 5 new agents demonstrably functional in an end-to-end run; pipeline-run-summary.json produced at run termination per AC-OP-3; replayability per Blueprint § Risk 1 mitigation.

### Pass Criteria

| ID | Description | Assertion | Source | Automation Hook | Severity |
|---|---|---|---|---|---|
| **PV-6.C1** | **T6.1 disposition recorded explicitly per ADR-0029 + ADR-0033 no-silent-absorption**: EITHER (Posture A) — Plan v2's Open Items #5 + Update History + T6.2 smoke-test `pipeline-run-summary.json` include the Scope-Deviation entry, OR (Posture B) — all ~20+ planning-side agent author-prompt edits applied + verified per T6.1 L1/L2. | Inspect Plan v2 + smoke-test summary for the disposition record; if Posture B, run T1.1 validator against all ~20+ edited agents and assert each emits `doc_type` correctly. | T6.1 L1 | Inspection + (if Posture B) validator batch | **blocking — primary ADR-0029 + ADR-0033 enforcement** |
| **PV-6.C2** | T6.2(a) synthetic test feature scaffolding exists at `working/feature/_smoke_test_execution_pipeline/` with minimal artifacts (PRD stub, Blueprint stub, tasks.json, acceptance-tests.md, phase-validators.md). Carries `feature_slug` indicating non-production OR `status: scaffolding` marker per shared-conventions.md v2 convention. | `[ -d working/feature/_smoke_test_execution_pipeline/ ]` AND `ls working/feature/_smoke_test_execution_pipeline/` shows expected scaffolding files; frontmatter contains the non-production marker. | T6.2(a) L1 | Filesystem inspection + grep | blocking |
| **PV-6.C3** | T6.2(b) end-to-end smoke test runs to completion: orchestrator spawned against scaffolding's `tasks.json`; advances through 14-transition state machine; terminal state reached (TERMINATED per T13). | Capture orchestrator output; verify exit code 0; verify final state = TERMINATED. | T6.2(b) L1 | Orchestrator harness probe | blocking |
| **PV-6.C4** | **All 14 state transitions observed at least once in `state-transitions.log` during the smoke test**: T0 (INIT→pending), T1-T12 (12 substantive), T13 (any→TERMINATED). | `python3 -c "import json; entries = [json.loads(l) for l in open('working/feature/_smoke_test_execution_pipeline/state-transitions.log')]; observed = set(e['transition_name'] for e in entries); assert observed == set(['T0','T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12','T13'])"` exits 0. | T6.2(b) L2, I-AA-609 | JSONL inspection of state-transitions.log | **blocking — I-AA-609 end-to-end enforcement** |
| **PV-6.C5** | 1+ `per-task-execution-result.{json,md}` pairs exist post-smoke-test, conforming to T5.1 template. | Filesystem inspection + each pair passes T1.1 validator + shared-document-reviewer. | T6.2(b) L2 | File-exists + validator + reviewer chain | blocking |
| **PV-6.C6** | 1 `phase-quality-report.{json,md}` pair exists post-smoke-test, conforming to T5.2 template; dimensional verdict structure conforms to D-13 5-dimensional verdict per Blueprint § Contract 2; audit-counter delta populated per FR-12 + Q-CC-3. | Inspect file pair; T1.1 validator + schema-conformance check against Contract 2 + Contract 3. | T6.2(b) L2, L3 (T3.4) | File inspection + JSON-schema check | blocking |
| **PV-6.C7** | 0+ `quality-reconciliation-log-cycle-N.{json,md}` pairs exist, conforming to T5.3 template (count depends on scaffolding's intentional findings; smoke-test scenario (iv) requires cycle-4-exhaustion case). | File inspection + each pair's JSON half conforms to T5.3 schema. | T6.2(b) L2, L3 (T3.5) | File inspection + schema | blocking |
| **PV-6.C8** | Final `pipeline-run-summary.json` produced at run termination per AC-OP-3, conforming to T5.5 template + Blueprint § Data Representation Decision 3. | File exists; parses as JSON; required fields present. | T6.2(b) L1, L2 | File-exists + JSON parse + schema | blocking |
| **PV-6.C9** | **Smoke test scenario (iii) — STUB_DETECTED path verified**: a task with a stub triggers `T6` transition (STUB_DETECTED → escalated_stub state); orchestrator routes per D-2d (no reconciler involvement). | Inspect state-transitions.log for T6 entry; inspect orchestrator behavior; verify reconciler NOT invoked for that path. | T6.2(b) L3 | JSONL inspection + orchestrator trace | blocking |
| **PV-6.C10** | **Smoke test scenario (iv) — 4-cycle cap exhaustion verified per ADR-0017 + AC-FR-10-c**: a phase-quality finding reaches the 4-cycle cap → T11 exhaustion + budget-exhausted artifact emitted + user escalation surfaced. | Verify `quality-reconciliation-log-cycle-4.{json,md}` outcome = `RECONCILIATION_EXHAUSTED`; budget-exhausted artifact present; pipeline-run-summary.json surfaces the escalation. | T6.2(b) L3, ADR-0017 | File inspection + outcome verify | **blocking — ADR-0017 + AC-FR-10-c enforcement** |
| **PV-6.C11** | **Cycle-Cap Escalation Gate signal emitted on cap exhaustion**: when scenario (iv) hits cycle 4, the orchestrator emits an escalation artifact per AC-FR-10-c that surfaces to the user; this is the canonical execution-time-reconciliation cap surface per ADR-0017. | Inspect orchestrator output for the escalation surface; verify the artifact name/location per FR-10 spec. | T6.2(b) L3, ADR-0017 | Artifact inspection | blocking |
| **PV-6.C12** | **Replayability per Blueprint § Risk 1 mitigation**: a deterministic re-execution of T6.2(b) produces equivalent state-transitions.log entries (modulo timestamps + run_id). | Re-run smoke test; compare state-transitions.log entries (transition names + sequence); assert sequence equality. | T6.2(b) L3 | Two-run diff | blocking |
| **PV-6.C13** | **Posture-A surfacing in smoke-test summary (if Posture A chosen)**: `pipeline-run-summary.json` includes a `scope_deviations` entry documenting the deferred ~20+ planning-side agent edits per ADR-0033. | Inspect pipeline-run-summary.json; assert presence of the Scope-Deviation field with the deferred-edits entry. | T6.1 Posture A L1 | JSON inspection | blocking (if Posture A) |
| **PV-6.C14** | **No regression in pre-existing planning-side agents** (Phase 6 Exit Criteria). | If a known-good planning-side smoke test exists (per Open Item #6), re-run it; assert pass. If not, this criterion is `not_applicable` and surfaced informationally. | Phase 6 exit, Open Item #6 | Regression-suite invocation OR `not_applicable` surface | warning (per Open Item #6 — full regression-suite is out of scope) |
| **PV-6.C15** | **Scope-deviation scanning at audit-stage observed (per ADR-0033 manual scan)**: `execute-phase-quality-reviewer` + `execute-finalize-reconciler` body-content includes the scan requirement; smoke test's per-task-execution-result fixtures include at least one with a scope-deviation; the reviewer surfaces it. | Inspect agent bodies (T3.4, T3.5); inspect smoke-test scenario fixture; verify scope-deviation finding emitted in phase-quality-report. | T6.2(b) L3, ADR-0033 | Body grep + fixture verify | blocking |

### Acceptance Tests Scheduled for This Phase
- AC-FR-1-d (terminal gate passes — PV-6.C3, C4)
- AC-FR-5-d (state transitions observable in deliverable archive — PV-6.C4)
- AC-FR-10-c (budget-exhausted artifact + escalation — PV-6.C10, C11)
- AC-FR-13-a (per-entry machine-parseable structure — PV-6.C7)
- AC-OP-1 (artifacts in standard layout — PV-6.C5-C8)
- AC-OP-2 (discipline-5 mechanical enforcement at every gate — substrate verified at PV-1; end-to-end at PV-6.C3)
- AC-OP-3 (pipeline-run-summary.json produced at run termination — PV-6.C8)
- All ACs whose L3 referenced T6.2 (per Plan § Acceptance Test Cross-Reference)

### Operational Checks
- **End-to-end pipeline functional:** PV-6.C3, C4 — the 14-transition state machine works in full.
- **Replayability (per Risk 1):** PV-6.C12.
- **Cycle-cap escalation signal emitted:** PV-6.C10, C11 — this is the ADR-0017 + AC-FR-10-c surface; the canonical execution-time reconciliation cap behavior.
- **Scope-deviation surfacing observed at runtime (per ADR-0033):** PV-6.C15.
- **Posture-A deferral surfacing (if chosen):** PV-6.C13 — Scope-Deviation entry in run-summary per ADR-0029 + ADR-0033 no-silent-absorption.
- **No regression in planning-side agents:** PV-6.C14 — warning per Open Item #6 (regression suite out of scope this feature).
- **Rollback path drilled:** Phase 6 changes are: T6.1 (Posture B) ~20+ agent edits → revert per file via `git revert`. T6.2 — smoke-test artifacts are throw-away (under `working/feature/_smoke_test_execution_pipeline/` — easily deleted). No production-deploy rollback in scope (feature ships as Claude Code configuration; user installs via git pull).

### Severity Rules
- 13 of 15 criteria are **blocking**. PV-6.C14 is **warning** per Open Item #6. PV-6.C13 is **blocking only if Posture A** chosen (otherwise `not_applicable`).
- PV-6.C1 + PV-6.C10 + PV-6.C11 are load-bearing: T6.1 disposition surfacing (no-silent-absorption per ADR-0029/0033) AND ADR-0017 + AC-FR-10-c cycle-cap enforcement.

### Failure Response
- PV-6.C1 missing disposition: Update Plan v2's Open Items + Update History to record the chosen posture explicitly. **Cannot ship without this record per ADR-0029 + ADR-0033.**
- PV-6.C3 smoke test fails to complete: Debug orchestrator + per-agent dispatch; consult state-transitions.log for last successful transition.
- PV-6.C4 incomplete 14-transition coverage: Scaffold's task mix is insufficient; augment to cover missing transitions; re-run.
- PV-6.C10 cycle-cap not reached: Scaffold's scenario (iv) is missing or misconfigured; verify intentional-finding mix produces the 4-cycle exhaustion path.
- PV-6.C12 replayability failure: Investigate non-determinism source (likely timestamps, run_id, or randomized fixture ordering); pin sources.
- PV-6.C15 scope-deviation not surfaced: Re-verify T3.4 + T3.5 agent body includes the ADR-0033 audit-stage enforcement requirement; re-run smoke test.

### Validator Metadata
- **When run:** After T6.2 completion claim.
- **Expected duration:** ~15-25 minutes (the smoke-test run itself is the bulk; criteria checks are 5-7 minutes additional).
- **Prerequisites:** PV-0 through PV-5 ALL PASS. T6.2 is the integration L3 for the entire feature; it presupposes every preceding phase's substrate.
- **Manual vs automated:** Mostly automatable; PV-6.C14 may require manual judgment per Open Item #6.

---

## Validator Dependency Graph

```
PV-0 (Setup)
   │
   ├──► PV-1 (auditing-shared scripts)
   │      │
   │      └──► PV-2 (Skill installs — depends on T1.1 validator for AC-FR-9-e sequencing enforcement)
   │             │
   │             └──► PV-3 (Execution-phase agent authoring — AC-FR-9-c skill-existence cross-check)
   │                    │
   │                    └──► PV-4 (Existing-agent extensions + convention updates)
   │                           │
   │                           └──► PV-5 (Template authoring — depends on shared-conventions.md v2 + shared-document-reviewer dispatch on doc_type)
   │                                  │
   │                                  └──► PV-6 (Rollout — depends on ALL preceding)
   │
   (PV-0 also gates PV-3 directly via ADR-0035 ratification — but PV-3 conventionally waits for PV-2 too)
```

**Default rule:** PV-(N+1) requires PV-(N) PASS. Two non-trivial cross-phase dependencies:

1. **PV-2 → PV-3 sequencing per AC-FR-9-e** (CRITICAL): PV-2 MUST pass before Phase 3 begins, because the T1.1 frontmatter validator (operational by PV-1) will reject any agent in Phase 3 whose `skills:` field references a skill that doesn't exist. PV-2.C9 + PV-2.C10 are the explicit enforcement points.
2. **PV-1 → PV-3 via T1.1 validator + run_phase_checks.py**: PV-3's Pass Criteria invoke T1.1 validator (PV-3.C2, C11) and depend on the script substrate from Phase 1.

---

## Critical-Path Validators

Validators whose failure most delays the feature:

1. **PV-0** — substrate gate; failure here means upstream is broken and the entire feature run cannot proceed.
2. **PV-1** — auditing-shared scripts are the substrate every downstream phase depends on. T1.1 (validator script) is invoked by PV-2, PV-3, PV-4, PV-5, PV-6.
3. **PV-2** — AC-FR-9-e sequencing gate; failure blocks Phase 3 entirely.
4. **PV-6** — integration L3; failure here means the feature is not operationally functional even though individual components passed. The smoke test is the substrate validation per Blueprint § Operational Verification.

PV-3, PV-4, PV-5 are less critical-path: failures within these phases are typically narrow re-authoring tasks (cycle-3 correction missing on a single agent; a single template missing a section); recovery is per-task.

---

## Parallelizable Validator Checks

Within a single phase validator, criteria that can run concurrently:

- **PV-0:** PV-0.C1, C2, C3 (grep checks on different files) are parallel. PV-0.C5 (subagent invocations per ADR) are parallel.
- **PV-1:** PV-1.C1 (parse check across 7 scripts) is naturally parallel. PV-1.C2 through C9 (per-script L2) are parallel across scripts.
- **PV-2:** PV-2.C1, C2, C7 (per-skill checks) are parallel.
- **PV-3:** PV-3.C3 through C7 (per-agent frontmatter checks) are parallel. PV-3.C8, C9 (per-agent spawn probes) are parallel.
- **PV-4:** PV-4.C1, C7, C9 (per-file edits checked independently) are parallel.
- **PV-5:** PV-5.C2, C12 (per-template checks) are parallel across the 5 templates.
- **PV-6:** Single end-to-end run — most criteria are derived from the same smoke-test execution; assertion checks (C4-C11) are parallel post-execution.

Between phase validators (PV-0..PV-6), the dependency chain enforces serial execution per the Validator Dependency Graph above.

---

## Shared Validator Infrastructure

Common dependencies across validators:

- **T1.1 frontmatter validator (`validate_pipeline_frontmatter.py`)** — invoked by PV-1.C2, C3; PV-2.C2, C9, C10; PV-3.C2; PV-4.C3, C6, C8, C10; PV-5.C2; PV-6.C5. **Substrate authored in Phase 1; operationalized at PV-1 PASS.**
- **`shared-document-reviewer`** — invoked by PV-0.C5; PV-4.C2, C11; PV-5.C12; PV-6.C5. **Substrate updated in Phase 4 (T4.2); operationalized at PV-4 PASS.**
- **Orchestrator harness / subagent dispatch probe** — used by PV-2.C8; PV-3.C8, C9; PV-6.C3. **Existing Claude Code infrastructure; not feature-introduced.**
- **Test fixtures** — fixture artifacts authored as part of T1.7 smoke test + T6.2 scaffolding. Shared across PV-1 and PV-6.
- **`state-transitions.log`** — the operational observability surface; produced by `log_state_transition.py` (T1.2); inspected by PV-6.C4, C9, C10, C12.
- **`.claude/settings.json` allow-list** — referenced by PV-0.C8, C9 and operationally underlying every script invocation in PV-1 through PV-6.

No fixtures, dashboards, or test environments are external to the repo — all infrastructure is in-repo Claude Code configuration.

---

## Validator Runbook

A human operator executes the validators in sequence as Phase N's exit gate. Per the Plan + this document:

1. **Triggering**: After the implementor claims "Phase N done", the operator runs PV-N. Mechanism: the operator invokes the validator's automation hooks (see per-criterion `Automation Hook` columns). For a single Claude Code session, the operator can either (a) manually run each automation hook and aggregate verdicts, OR (b) author a thin `run_phase_validator.py` wrapper that aggregates per-criterion results (DEFERRED — flagged in Open Items below as a follow-on optimization; v1 ships manual orchestration).

2. **Monitoring**: While criteria run, the operator observes outputs. Long-running checks (PV-1.C10 smoke test, PV-6.C3 end-to-end smoke test) take 5-25 minutes; the operator MAY interleave other work but MUST not advance to the next phase until all blocking criteria pass.

3. **Interpreting results**: 
   - **PASS verdict**: All blocking criteria passed. Phase N is complete; advance to Phase N+1.
   - **PASS_WITH_DEFERRAL verdict**: All blocking criteria passed; one or more `warning` criteria failed AND the operator (with user concurrence) elects to defer with explicit Scope-Deviation surface per ADR-0033. The deferral is recorded in the run summary + Open Items.
   - **BLOCKED verdict**: One or more blocking criteria failed. Phase N is NOT complete; the operator triggers the relevant Failure Response (per-criterion). After remediation, the operator re-runs the affected criteria (NOT the whole validator, to save time).

4. **Logging**: Every validator run produces a `phase-validator-result-<phase>.json` artifact under `working/feature/execution-pipeline-design-r1/`. Per the validator-doc_type spec (ADR-0032 + shared-conventions.md v2), this artifact carries doc_type `phase-validator-result` (a `phase-validators` companion artifact — the result of running the validator, not the validator definition itself).

5. **Audit trail**: All Phase Validator runs are appended to the feature's deliverable archive per AC-OP-1. The Cross-Artifact Audit stage (downstream of this document) consumes the validator entries to verify Plan ↔ Phase Validators alignment.

---

## Severity Rules Summary

| Severity | Meaning | Effect on Validator Verdict |
|---|---|---|
| **blocking** | Cannot advance to next phase. | Failure → BLOCKED verdict. |
| **warning** | Should be addressed; deferral requires explicit user concurrence + Scope-Deviation surfacing per ADR-0033. | Failure with user-deferral → PASS_WITH_DEFERRAL. |
| **informational** | Recorded; no verdict impact. | Surface in run summary only. |

Per ADR-0033 audit-stage enforcement extension, BLOCKED verdicts at any phase MUST surface in the smoke-test run-summary as Scope-Deviation entries if work proceeds (which is itself a deviation; warns operator of audit trail).

---

## Open Items (Pending Cross-Artifact Audit)

These items surface to the downstream Cross-Artifact Audit stage. Each is anchored to substrate in Plan v2 or this document.

1. **`run_phase_validator.py` wrapper script not authored in v1.** The Validator Runbook (§ above) flags manual orchestration as the v1 default; a thin wrapper aggregating per-criterion results into a JSON verdict would streamline operator workflow. Deferred to follow-on feature; not in scope for execution-pipeline-design-r1. Surface for Cross-Artifact Audit awareness (the absence is intentional, not a bug).

2. **PV-6.C14 (regression suite for planning-side agents) marked `warning`-severity per Plan Open Item #6.** Authoring a regression suite for the existing planning-side agents is out of scope for this feature; absent suite, the criterion is `not_applicable` and surfaced informationally. Cross-Artifact Audit at Gate 6 will verify the surfacing is correct.

3. **PV-3.C12 invariant-10 scoping inspection is structural (grep-based), not behavioral.** A behavioral verification — actually running the orchestrator across T0/T13 transitions and asserting cycle counter delta is zero — is captured at PV-6.C4 in the end-to-end smoke test. The Phase-3 validator's structural check is sufficient for phase-exit; the end-to-end behavioral check is the integration assertion. Surface for Cross-Artifact Audit verification that the staging is sound.

4. **PV-2.C9 / C10 (AC-FR-9-e sequencing gate) treats Phase-3 entry as the canonical enforcement point.** An alternative would be for the T1.1 validator itself to refuse-to-load agents whose skill bindings have not yet been satisfied at runtime (runtime version of the check). v1 ships the static enforcement at Phase-2-exit; runtime enforcement is out of scope. Per Blueprint § Verification Strategy, this is the intended posture.

5. **PV-6.C1 Posture-A surfacing assumes Plan v2's Open Items / Update History have been updated.** If Plan v2 itself is the source of truth for the disposition record, the validator's automation hook is essentially a grep over Plan v2. A more durable surface would be a dedicated `posture-decision-r1.md` artifact carrying the Posture A/B disposition; this is deferred to follow-on for simplicity. The Plan v2 record is sufficient for v1 per ADR-0029 + ADR-0033 no-silent-absorption.

6. **PV-6.C15 scope-deviation scanning is manual (body-content grep + smoke-test fixture inspection)**, NOT mechanical via `scan_unsurfaced_deviations.py` (deferred per Plan Open Item #7 + Blueprint § Risk 7 + Future Extensibility). The current validator's posture is to verify the agent body documents the requirement; runtime enforcement at audit-stage is per the agent prompts, not a separate script. Cross-Artifact Audit can verify the staging is sound.

7. **Reconciliation budget remaining after this Validator Authoring**: Per Plan Open Item #9, 1 reconciliation cycle remains for the Plan / Test / Cross-Artifact-Audit sequence. This Phase Validators document is co-authored with Test Acceptance per the parallel-dispatch contract; both consume Cross-Artifact Audit budget. **Cross-Artifact Audit findings should be consolidated per cycle to maximize remaining budget.**

---

## Update History

This document follows ADR-0005 append-only supersession discipline.

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-22 | test-phase-validator-author (Claude Code subagent dispatch, authoritative; `agent_invocation_simulation: false`) | Initial authoritative Phase Validators authoring. 7 validators (PV-0 through PV-6), one per Plan v2 phase. Authored in parallel with `test-acceptance-author` per the post-Plan-approval parallel-dispatch contract. Derived from `plan-v2.md` (APPROVED at Gate 5), `blueprint-v5.md` (audit-r7 verdict=pass), `prd-v1.1.0.md` (60 ACs). Honors cycle-3 corrections: I-AA-601 (frontmatter validator coverage) at PV-1.C2; I-AA-602 (unrestricted Bash on T3.3) at PV-3.C4; I-AA-603 / ADR-0035 (auditing-shared Skill binding) at PV-3.C3, C4, C6, C7 (positive on 4 agents; PV-3.C5 negative on T3.2); I-AA-604 (ADR-0017 forward citation, NOT ADR-0021) at PV-3.C14; I-AA-605 (Posture-A T6.1 disposition surfacing) at PV-6.C1, C13; I-AA-606 (bidirectional cross-reference Blueprint ↔ ADR-0033 §Context) at PV-5.C9; I-AA-608 (Write on orchestrator) at PV-3.C3; I-AA-609 (T0+T13 boundary transitions, invariant-10 scope clarified) at PV-1.C4, C11; PV-3.C10, C12; PV-5.C7; PV-6.C4. ADR-0032 compliance enforced via `doc_type: phase-validators` frontmatter field + universal-required fields per shared-conventions.md v2 spec. ADR-0029 + ADR-0033 no-silent-absorption discipline enforced via PV-6.C1 disposition surfacing + Open Items #1-7. AC-FR-9-e sequencing gate is explicit at PV-2.C9 + PV-2.C10 (the load-bearing assertion for Phase 2 → Phase 3 transition). |
