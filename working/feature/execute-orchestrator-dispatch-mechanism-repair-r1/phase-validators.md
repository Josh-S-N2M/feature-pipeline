---
id: PV-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: phase-validators
version: 1.0.0
status: draft
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
scope_class: FULL
layer_scope: [cc]
derived_from:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/plan-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md
  - adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/acceptance-tests.md
generated: 2026-05-24T00:45:00Z
generated_by: test-phase-validator-author
phase_count: 7
validator_count: 7
---

# Phase Validators — execute-orchestrator Dispatch Mechanism Repair (r1)

## Purpose

This document defines the gates **between** the Plan's 7 phases. Each validator entry specifies what must be true before the phase can be considered complete and the next phase started. Phase Validators are not per-task gates; they aggregate L3 verification across the phase's tasks plus phase-specific operational checks.

This document was authored in parallel with `acceptance-tests.md`. Where this document references `AT-NNN` IDs, they are the acceptance-test specs being authored in parallel; where the parallel document is not yet available, this document references the PRD/Blueprint AC IDs directly.

## Conventions

- **Validator ID:** `PV-<phase-number>`.
- **Criterion ID:** `PV-<phase>.C<n>`.
- **Severity values:** `blocking` (failure blocks phase advance absolutely), `warning` (failure surfaces to user for explicit deferral decision), `informational` (recorded; doesn't block).
- **Automation hook:** `automated` (CI / shell script / git inspection), `operator-facing` (requires human action or confirmation), `mixed` (automated check + operator confirmation).
- **All shell commands assume cwd = repo root** per ADR-0027.
- **The validator order is the phase order; PV-N requires PV-(N-1) passed unless explicitly stated otherwise.**

---

## PV-0 — Phase 0 Setup Validator

### Phase reference

Plan §"Phase 0 — Setup" (tasks T0.1, T0.2, T0.3).

### Validator goal

Prove that pre-edit groundwork is complete: ADRs exist at canonical root; the known Stage-13 packager BLOCKER + waiver are documented; a rollback baseline SHA is captured. Without PV-0 passing, no Phase 1 edit may begin.

### Pass criteria

#### PV-0.C1 — Canonical-root ADR presence (ADR-0044 + ADR-0045)

- **Description:** Both new ADRs must exist at the canonical root `/workspaces/feature-pipeline/adrs/`, with no feature-scoped duplicates under `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/adrs/` (honoring ADR-0036 placement disposition).
- **Assertion:**
  - `test -f /workspaces/feature-pipeline/adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md` exits 0.
  - `test -f /workspaces/feature-pipeline/adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` exits 0.
  - `ls /workspaces/feature-pipeline/working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/adrs/ 2>/dev/null | grep -E 'ADR-(0044|0045)'` returns NOTHING (exit code 1 acceptable).
- **Source:** T0.1 L1+L2 verification.
- **Automation hook:** `automated` — Phase Validator shell script (file existence + negative grep).
- **Severity:** `blocking`.

#### PV-0.C2 — ADR frontmatter well-formedness

- **Description:** Both ADRs MUST parse as valid markdown with the required frontmatter fields per the canonical ADR template: `id`, `status: accepted`, `change_summary` present.
- **Assertion:**
  - For each of ADR-0044 and ADR-0045: `python3 -c "import yaml,sys; d=yaml.safe_load(open(p).read().split('---')[1]); assert d['status']=='accepted' and d.get('change_summary'); print(d['id'])"` succeeds (where `p` is the ADR path).
- **Source:** T0.1 L2 verification.
- **Automation hook:** `automated` — YAML parse.
- **Severity:** `blocking`.

#### PV-0.C3 — Stage-13 packager BLOCKER waiver documentation

- **Description:** A waiver-path entry documenting the known Stage-13 packager BLOCKER on canonical-root-only ADR placement MUST exist either in `checkpoint.json` (as a known-issues entry) OR as a separate `open-items.md`/`stage-13-waiver.md` document in the feature working directory. Per T0.2, the entry MUST cite both the Blueprint's "ADR-0036 placement disposition" section and ADR-0036 itself.
- **Assertion:**
  - At least one of the following greps returns a match:
    - `grep -r "Stage-13 packager BLOCKER" working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/ -l`
    - `grep -r "stage-13.*packager" working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/checkpoint.json 2>/dev/null`
  - The matched document contains BOTH the strings `ADR-0036` AND `placement disposition` (case-insensitive ok).
- **Source:** T0.2 L1+L2 verification.
- **Automation hook:** `automated` — recursive grep + content check.
- **Severity:** `blocking`.

#### PV-0.C4 — Rollback baseline captured

- **Description:** The pre-Phase-1 baseline commit SHA MUST be recorded in `rollback-baseline.txt` under the feature working directory, with a 40-char SHA and an ISO timestamp.
- **Assertion:**
  - `test -f working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/rollback-baseline.txt` exits 0.
  - File contains a line matching `[0-9a-f]\{40\}` AND a line matching ISO-8601 (`[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T`).
  - At baseline-capture time: `git status --porcelain` against the 9 affected paths is empty.
- **Source:** T0.3 L1+L2 verification.
- **Automation hook:** `automated` — shell script.
- **Severity:** `blocking`.

#### PV-0.C5 — AC-NFR-4-a satisfied-upstream gate (I-CA-003 absorption)

- **Description:** Gate the satisfied-upstream AC-NFR-4-a — confirm the T-001 research note exists with the load-bearing `dispatch_supported: false` and `kill_criterion_triggered: 2` flags intact at Phase-0 exit. The substantive verification happened in Stage 4; this PV guards against silent deletion of the artifact before downstream phases run.
- **Assertion:**
  - `test -f working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md` exits 0.
  - `grep -q '^dispatch_supported: false' <T-001 note>` exits 0.
  - `grep -q '^kill_criterion_triggered: 2' <T-001 note>` exits 0.
- **Source:** T-001 research note (existing artifact from Stage 4 Discovery Research).
- **Automation hook:** `automated` — shell one-liner.
- **Severity:** `blocking`.
- **AC verified:** AC-NFR-4-a. **Test verified:** T-AC-NFR-4-a-finding-artifact in acceptance-tests.md.

### Operational checks (Phase 0 specific)

- **OC-0.1 (informational):** Confirm `git rev-parse HEAD` matches the SHA recorded in `rollback-baseline.txt` at the moment PV-0 runs — protects against a "baseline drift" race where edits land between T0.3 and Phase 1.

### Acceptance tests scheduled for this phase

None directly; PV-0 is setup-only. Supports `AC-FR-8-a` (ADR-0045 placement compliance, partial) and the Stage-13 waiver portion of `AC-FR-4-a`.

### Failure response

- **PV-0.C1 fail:** Halt; copy or move ADRs to canonical root; delete any feature-scoped duplicates. Re-run PV-0.
- **PV-0.C2 fail:** Halt; fix ADR frontmatter; re-run.
- **PV-0.C3 fail:** Halt; author the waiver-path documentation per T0.2 spec; re-run.
- **PV-0.C4 fail:** Halt; re-snapshot baseline (`git rev-parse HEAD` to `rollback-baseline.txt`); re-run.
- **PV-0.C5 fail:** Halt; restore the T-001 research note from VCS history; verify `dispatch_supported: false` and `kill_criterion_triggered: 2` flags; re-run. If the note is genuinely lost, re-dispatch discovery-external-researcher for T-001.

Rollback path: N/A — Phase 0 has no code edits to revert (Plan §Rollback Procedure).

### Validator metadata

- **Run when:** After T0.1, T0.2, T0.3 are reported complete; before Phase 1 begins.
- **Expected duration:** < 2 min (file existence + YAML parse + greps).
- **Prerequisites:** none.

---

## PV-1 — Phase 1 Schema-Closure Validator

### Phase reference

Plan §"Phase 1 — Schema closure on recipe-feature-pipeline/SKILL.md (D-004)" (tasks T1.1, T1.2, T1.3).

### Validator goal

Prove the canonical `checkpoint.json` schema-reference block in `.claude/skills/recipe-feature-pipeline/SKILL.md` (originally lines 96–128) documents the three execution-phase fields (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`) AND captures the `void`/`-prime` extensions or cross-references the template that does. The dispatch section absorption in Phase 2 references the fields documented here; this validator is the precondition gate.

### Pass criteria

#### PV-1.C1 — Three execution-phase fields named in the schema block

- **Description:** All three field names MUST appear inside the schema-reference region of `.claude/skills/recipe-feature-pipeline/SKILL.md`.
- **Assertion:**
  - `grep -c "execution_pipeline_state_transitions" .claude/skills/recipe-feature-pipeline/SKILL.md` ≥ 1.
  - `grep -c "execution_mode" .claude/skills/recipe-feature-pipeline/SKILL.md` ≥ 1.
  - `grep -c "execution_pipeline_cycle_counters" .claude/skills/recipe-feature-pipeline/SKILL.md` ≥ 1.
- **Source:** T1.1 + T1.2 L1 verification.
- **Automation hook:** `automated` — `grep`.
- **Severity:** `blocking`.

#### PV-1.C2 — Field positions within the schema block region

- **Description:** Each of the three field names MUST appear inside the original lines-96–128 schema region OR within a clearly contiguous extension of it (the region may have shifted line numbers post-edit; structural location matters, not line numbers).
- **Assertion:**
  - Locate the schema block via header anchor: `grep -n "^##.*checkpoint\\.json.*schema\\|^### *Canonical checkpoint" .claude/skills/recipe-feature-pipeline/SKILL.md` returns a line number L_start.
  - The next `^##` header line number is L_end.
  - All three field names appear between L_start and L_end (verified via `sed -n "${L_start},${L_end}p" | grep`).
- **Source:** T1.1 + T1.2 L1 verification.
- **Automation hook:** `automated` — sed + grep composition.
- **Severity:** `blocking`.

#### PV-1.C3 — execution_mode v1 values documented

- **Description:** The two v1 values `"single-agent-fallback"` and `"specialist-isolation"` MUST be documented in prose adjacent to the `execution_mode` field.
- **Assertion:**
  - `grep -c "single-agent-fallback" .claude/skills/recipe-feature-pipeline/SKILL.md` ≥ 1.
  - `grep -c "specialist-isolation" .claude/skills/recipe-feature-pipeline/SKILL.md` ≥ 1.
- **Source:** T1.2 L2 verification.
- **Automation hook:** `automated` — grep.
- **Severity:** `blocking`.

#### PV-1.C4 — T4/T10 counter-increment rule referenced

- **Description:** The increment rule for `execution_pipeline_cycle_counters` MUST reference T4 (per_task increment) and T10 (per_phase increment) per I-AA-609 invariant 10.
- **Assertion:**
  - `grep -E "T4.*per[-_ ]task|per[-_ ]task.*T4" .claude/skills/recipe-feature-pipeline/SKILL.md` returns a match.
  - `grep -E "T10.*per[-_ ]phase|per[-_ ]phase.*T10" .claude/skills/recipe-feature-pipeline/SKILL.md` returns a match.
- **Source:** T1.2 L2 verification.
- **Automation hook:** `automated` — grep with alternation.
- **Severity:** `blocking`.

#### PV-1.C5 — void / -prime extensions documented or cross-referenced

- **Description:** Within the schema region, either (a) the `void` / `void_reason` fields and the `-prime` suffix convention are documented, OR (b) a cross-reference to `state-transitions-log-entry-template.md` exists and is non-broken.
- **Assertion:** At least one of the following holds:
  - `grep -E "void|-prime" .claude/skills/recipe-feature-pipeline/SKILL.md` returns a match in the schema region.
  - `grep "state-transitions-log-entry-template.md" .claude/skills/recipe-feature-pipeline/SKILL.md` returns a match AND the referenced file exists at `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`.
- **Source:** T1.3 L1+L2 verification.
- **Automation hook:** `automated` — grep + `test -f`.
- **Severity:** `blocking`.

#### PV-1.C6 — Frontmatter parses; surrounding planning fields untouched

- **Description:** Frontmatter YAML still parses; the planning-side fields above and below the insertion point are byte-for-byte preserved (no accidental clobber).
- **Assertion:**
  - `python3 -c "import yaml; yaml.safe_load(open('.claude/skills/recipe-feature-pipeline/SKILL.md').read().split('---')[1])"` exits 0.
  - `git diff <baseline-sha> -- .claude/skills/recipe-feature-pipeline/SKILL.md` shows ONLY additions inside the schema region (no deletions outside it).
- **Source:** T1.1 L2 verification + Plan §Rollback Procedure.
- **Automation hook:** `automated` — YAML parse + git-diff inspection (semi-automated; the operator visually confirms the diff scope).
- **Severity:** `blocking`.

### Operational checks (Phase 1 specific)

- **OC-1.1 (informational):** Reading the schema region top-to-bottom yields a complete v1 schema picture for both `checkpoint.json` execution-phase fields and `state-transitions.log` per-entry shape (T1.3 L3 verification).
- **OC-1.2 (warning):** Schema documentation at this location is consistent with the in-flight artifact at `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json:8-16` (no drift introduced). Drift → warning (not blocking) because the in-flight artifact is explicitly NOT retrofitted per NFR-6.

### Acceptance tests scheduled for this phase

- ACs satisfied here (per Plan AC-to-Phase mapping): `AC-FR-4-b` (schema lockstep, partial — Phase 4 closes the rest), `AC-NFR-5-a` (canonical schema reference updated), `AC-CC-2` (lockstep on SKILL.md).
- Acceptance-test IDs (parallel doc): `AT-FR-4-b-P1`, `AT-NFR-5-a-P1`, `AT-CC-2-P1` (expected nomenclature).

### Failure response

- Any blocking criterion fail: Halt phase advance. Revert via `git revert <T1.x-commit>` per Plan §Rollback. Re-author the affected sub-edit (T1.1 / T1.2 / T1.3) and re-run PV-1.
- C6 fail (frontmatter break or unintended deletion): Hard revert via `git checkout <baseline-sha> -- .claude/skills/recipe-feature-pipeline/SKILL.md`.

### Validator metadata

- **Run when:** After T1.1, T1.2, T1.3 are reported complete; before T2.1 begins.
- **Expected duration:** < 3 min.
- **Prerequisites:** PV-0 passed.

---

## PV-2 — Phase 2 Dispatch-Section Absorption Validator

### Phase reference

Plan §"Phase 2 — Dispatch-section absorption into recipe-feature-pipeline/SKILL.md (D-001)" (tasks T2.1, T2.2, T2.3).

### Validator goal

Prove the "Execution Phase Dispatch" section was added to `recipe-feature-pipeline/SKILL.md` AFTER the Phase 1 schema closure, references the schema fields documented there, and contains the per-task/per-phase loop narrative, `dispatch_directives[]` indirection, cycle-cap escalation, and v1 logical-owner invariant.

### Pass criteria

#### PV-2.C1 — "Execution Phase Dispatch" section header exists

- **Description:** A section header named "Execution Phase Dispatch" (or close, e.g., `## Execution Phase Dispatch`) MUST exist in `.claude/skills/recipe-feature-pipeline/SKILL.md`, located below the Gate-6 region.
- **Assertion:**
  - `grep -n "^## *Execution Phase Dispatch\\|^### *Execution Phase Dispatch" .claude/skills/recipe-feature-pipeline/SKILL.md` returns a line number.
  - That line number is GREATER than the line number of any "Gate 6" or "Step 14" reference in the same file.
- **Source:** T2.1 L1 verification + Phase 2 Exit Criteria.
- **Automation hook:** `automated` — grep with line-number compare.
- **Severity:** `blocking`.

#### PV-2.C2 — Phase-2 commit ordering postdates Phase-1 commit ordering

- **Description:** The git commit that introduced the Execution Phase Dispatch section MUST timestamp AFTER the commit(s) that closed the schema in Phase 1. This enforces D-004 → D-001 ordering (Blueprint §1 → §2, synthesis Constraint 5.1).
- **Assertion:**
  - `git log --all --oneline --grep="Execution Phase Dispatch\\|dispatch section absorption"` returns a commit SHA C_dispatch.
  - `git log --all --oneline --grep="schema closure\\|execution_pipeline_state_transitions field"` returns a commit SHA C_schema (or set thereof; take the latest).
  - `git log --format=%ct C_schema` < `git log --format=%ct C_dispatch` (committer-time strict less-than).
- **Source:** Plan §Cross-Phase Sequencing Constraints item 1.
- **Automation hook:** `automated` — git log + numeric compare.
- **Severity:** `blocking`.

#### PV-2.C3 — 14-row state machine enumerated; ADR-0017 + ADR-0033 cited; ADR-0034 NOT cited

- **Description:** The new section MUST enumerate the T0..T13 rows (state machine) and MUST cite ADR-0017 (4-cycle cap) and ADR-0033 (symmetric D-12). It MUST NOT cite ADR-0034 per I-DR-001 absorption.
- **Assertion:**
  - In the section (delimited by the section header to next `^##`): grep returns matches for at least 10 distinct `T[0-9]+` tokens (state-machine rows).
  - `grep -c "ADR-0017" <section-slice>` ≥ 1.
  - `grep -c "ADR-0033" <section-slice>` ≥ 1.
  - `grep -c "ADR-0034" <section-slice>` == 0.
- **Source:** T2.1 L2 verification + AC-CC-1.
- **Automation hook:** `automated` — sed slice + grep counts.
- **Severity:** `blocking`.

#### PV-2.C4 — Schema fields documented in Phase 1 are referenced from the section

- **Description:** The Execution Phase Dispatch section MUST reference at least two of the three schema fields documented in Phase 1 (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`). This enforces the "dispatch section references the schema closed in Phase 1" coupling.
- **Assertion:**
  - Within the section slice: at least two of the three field-name greps return matches.
- **Source:** Blueprint Implementation Plan §1 → §2 ordering rationale; Plan §Cross-Phase Sequencing Constraints item 1.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-2.C5 — `dispatch_directives[]` Contract 6 documented with malformed-array surface-to-user rule

- **Description:** The section MUST document `dispatch_directives[]` AND the malformed-or-empty-array escalation rule (surface to user, treat as cycle-cap-equivalent, do NOT silently fall back per AC-CC-4 / I-DR-005).
- **Assertion:**
  - `grep -c "dispatch_directives" <section-slice>` ≥ 2 (at least one for the contract, at least one for the error path).
  - The section contains a phrase matching `surface to user|surface-to-user|escalation|do not.*silently.*fall back|cycle-cap-equivalent` near a `dispatch_directives` reference (within 10 lines).
- **Source:** T2.2 L1+L2 verification.
- **Automation hook:** `automated` — grep + proximity scan via awk.
- **Severity:** `blocking`.

#### PV-2.C6 — `invoking_agent` logical-owner invariant documented with value `execute-orchestrator`

- **Description:** The section MUST document the v1 invariant that all state-transitions.log entries written by the parent during the execution phase set `invoking_agent: "execute-orchestrator"` per Q-CC-4.
- **Assertion:**
  - Within the section slice: `grep -E "invoking_agent.*execute-orchestrator|execute-orchestrator.*invoking_agent"` returns a match.
  - The section contains the words "logical owner" OR "logical-owner" (case-insensitive).
- **Source:** T2.3 L1+L2 verification.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

### Operational checks (Phase 2 specific)

- **OC-2.1 (informational):** No edits to any sub-agent file have occurred yet (those are Phase 3). `git diff <T1.3-commit>..HEAD -- .claude/agents/` returns no output.
- **OC-2.2 (warning):** The section is self-consistent (no broken internal cross-references). Operator skims the section for narrative coherence. Warning rather than blocking because PV-2 cannot fully assess narrative quality automatically.

### Acceptance tests scheduled for this phase

- ACs satisfied here: `AC-FR-3-a`, `AC-FR-3-c`, `AC-CC-1`, `AC-CC-2`, `AC-CC-4`, `AC-NFR-2-a`, `AC-NFR-2-b`, `AC-NFR-3-a`, `AC-NFR-3-b`, `AC-FR-6-a` (partial — the logical-owner invariant), `AC-NFR-6-a`.
- Acceptance-test IDs (parallel doc): `AT-FR-3-a-P2`, `AT-FR-3-c-P2`, `AT-CC-1-P2`, `AT-CC-2-P2`, `AT-CC-4-P2`, `AT-NFR-2-a-P2`, `AT-NFR-2-b-P2`, `AT-NFR-3-a-P2`, `AT-NFR-3-b-P2` (expected nomenclature).

### Failure response

- C1 / C3 / C5 / C6 fail: Halt; amend T2.1 / T2.2 / T2.3 edits; re-run PV-2.
- C2 fail (commit ordering inverted): Halt with `phase-2-pre-phase-1` posture; the situation is recoverable only by reverting and re-applying in correct order. Per Plan §Cross-Phase Sequencing Constraints item 1: schema-references-not-yet-stable risk has fired.
- C4 fail: Amend the section to reference the schema fields; re-run.

Rollback path: `git revert <T2.x-commit>` removes the Execution Phase Dispatch section. The schema fields from Phase 1 remain (orphaned but not breaking) per Plan §Rollback Phase 2.

### Validator metadata

- **Run when:** After T2.1, T2.2, T2.3 are reported complete; before any Phase-3 sub-agent edit begins.
- **Expected duration:** < 4 min.
- **Prerequisites:** PV-1 passed; commits for both phases exist on the current branch.

---

## PV-3 — Phase 3 Sub-Agent Bundled Edits Validator

### Phase reference

Plan §"Phase 3 — Sub-agent file edits (bundled `Agent`-removal commit + 3-occurrence ADR sweep + prose updates)" (tasks T3.1, T3.2, T3.3, T3.4, T3.5, T3.6).

### Validator goal

Prove all five sub-agent file edits landed in a single bundled commit; `Agent` is removed from both target files' `tools:` arrays; the 3-occurrence ADR-0034 → ADR-0033 sweep in `execute-finalize-reconciler.md` is complete; body line 76 prose is re-framed; specialist-body prose updates are applied; and the commit message contains "FR-5 sweep closure: affected set = 2".

This is the most complex validator in the document. The bundled-commit constraint (synthesis Constraint 5.2) is non-negotiable.

### Pass criteria

#### PV-3.C1 — `Agent` removed from execute-orchestrator.md tools array

- **Description:** `.claude/agents/execute-orchestrator.md` frontmatter `tools:` array MUST NOT contain `Agent` or `TaskUpdate`.
- **Assertion:**
  - Extract frontmatter (between first `---` and second `---`); parse YAML; check `tools` array.
  - `python3 -c "import yaml; fm = yaml.safe_load(open('.claude/agents/execute-orchestrator.md').read().split('---')[1]); tools = fm.get('tools', []); assert 'Agent' not in tools, f'Agent still present: {tools}'; assert 'TaskUpdate' not in tools, f'TaskUpdate still present: {tools}'; print('OK', tools)"` exits 0.
- **Source:** T3.1 L1+L2 verification + AC-FR-5-a (part 1 of 2).
- **Automation hook:** `automated` — YAML parse + assert.
- **Severity:** `blocking`.

#### PV-3.C2 — `Agent` removed from execute-finalize-reconciler.md tools array

- **Description:** `.claude/agents/execute-finalize-reconciler.md` frontmatter `tools:` array MUST NOT contain `Agent`.
- **Assertion:**
  - `python3 -c "import yaml; fm = yaml.safe_load(open('.claude/agents/execute-finalize-reconciler.md').read().split('---')[1]); tools = fm.get('tools', []); assert 'Agent' not in tools, f'Agent still present: {tools}'; print('OK', tools)"` exits 0.
- **Source:** T3.3 L1+L2 verification + AC-FR-5-a (part 2 of 2).
- **Automation hook:** `automated` — YAML parse + assert.
- **Severity:** `blocking`.

#### PV-3.C3 — 3-occurrence ADR-0034 → ADR-0033 sweep on execute-finalize-reconciler.md

- **Description:** ZERO ADR-0034 occurrences MUST remain in `.claude/agents/execute-finalize-reconciler.md`; the three previously-existing occurrences (lines 3, 19, 82 per codebase analysis FD-6) MUST all be corrected to ADR-0033.
- **Assertion:**
  - `grep -c "ADR-0034" .claude/agents/execute-finalize-reconciler.md` == 0.
  - `grep -c "ADR-0033" .claude/agents/execute-finalize-reconciler.md` ≥ 3.
- **Source:** T3.3 L1 verification + I-DR-001 absorption.
- **Automation hook:** `automated` — `grep -c`.
- **Severity:** `blocking`.

#### PV-3.C4 — Body line-76 re-framing on execute-finalize-reconciler.md

- **Description:** The previous "Dispatch via Agent — invoke the target subagent with the revision_context payload" phrasing MUST be replaced with the new emission-contract phrasing: "Emit `dispatch_directives[]` in `quality-reconciliation-log.json`; the parent orchestrator consumes the array and dispatches each named target via Agent at main-conversation level."
- **Assertion:**
  - `grep -c "Dispatch via Agent" .claude/agents/execute-finalize-reconciler.md` == 0 (old phrasing gone).
  - `grep -E "Emit .*dispatch_directives|dispatch_directives.*quality-reconciliation-log" .claude/agents/execute-finalize-reconciler.md` returns a match.
- **Source:** T3.3 L2 verification.
- **Automation hook:** `automated` — grep.
- **Severity:** `blocking`.

#### PV-3.C5 — Body-prose rationale for recipe-feature-pipeline self-reference on execute-orchestrator.md (AC-CC-3)

- **Description:** An explicit prose paragraph documenting that the `recipe-feature-pipeline` entry in the `skills:` array is intentional and load-bearing for SA-13 audit traceability MUST exist in `.claude/agents/execute-orchestrator.md` body.
- **Assertion:** At least one of the following greps returns a match:
  - `grep -i "self-reference is intentional" .claude/agents/execute-orchestrator.md`.
  - `grep -i "load-bearing for SA-13" .claude/agents/execute-orchestrator.md`.
  - `grep -i "skills self-reference\\|skills:.*self-reference" .claude/agents/execute-orchestrator.md`.
- **Source:** T3.2 L1+L2 verification + I-DR-006 absorption.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-3.C6 — Body-prose dispatcher-reference updates on three leaf specialists

- **Description:** Each of (a) `execute-task-code-producer.md`, (b) `execute-task-quality-handler.md`, (c) `execute-phase-quality-reviewer.md` MUST contain at least one `recipe-feature-pipeline` reference in body prose (introduced by the dispatcher-reference update); none of the three files' frontmatter MAY have changed.
- **Assertion:** For each of the three files:
  - `grep -c "recipe-feature-pipeline" <file>` ≥ 1 (new dispatcher-reference present).
  - `git diff <baseline-sha>..HEAD -- <file>` shows zero additions/deletions in the lines between the first `---` and the second `---` (frontmatter preserved).
- **Source:** T3.4 + T3.5 L1+L2 verification.
- **Automation hook:** `automated` — grep + git diff line-range inspection.
- **Severity:** `blocking`.

#### PV-3.C7 — Bundled single-commit constraint

- **Description:** All Phase-3 edits MUST land in exactly ONE commit. The commit MUST modify exactly the five sub-agent files (no extras, no fewer). The commit message MUST contain the phrase `"FR-5 sweep closure: affected set = 2"`.
- **Assertion:**
  - `git log --format=%H --grep="FR-5 sweep closure: affected set = 2" | wc -l` ≥ 1.
  - For the matched commit SHA: `git show --stat <sha> -- .claude/agents/` lists EXACTLY the 5 files: `execute-orchestrator.md`, `execute-finalize-reconciler.md`, `execute-task-code-producer.md`, `execute-task-quality-handler.md`, `execute-phase-quality-reviewer.md`.
  - No other files in `.claude/agents/` appear in the diff stat.
  - No file outside `.claude/agents/` appears in the diff stat for THIS commit (other Phase-3 supporting files were committed separately or not at all).
- **Source:** T3.6 L1+L2+L3 verification + synthesis Constraint 5.2.
- **Automation hook:** `automated` — git log + git show + diff-stat parse.
- **Severity:** `blocking`. This is the single most load-bearing criterion in the document.

#### PV-3.C8 — Preserved triplet (model: opus, effort: high, memory: project) per Q-CC-3 + Q-CC-5

- **Description:** Both `execute-orchestrator.md` and `execute-finalize-reconciler.md` MUST preserve their `model: opus`, `effort: high`, `memory: project` frontmatter declarations per ADR-0022 preservation.
- **Assertion:** For each of the two files:
  - `python3 -c "import yaml; fm = yaml.safe_load(open('<file>').read().split('---')[1]); assert fm.get('model')=='opus' and fm.get('effort')=='high' and fm.get('memory')=='project', fm; print('OK')"` exits 0.
- **Source:** T3.1 + T3.3 descriptions; ADR-0022.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

### Operational checks (Phase 3 specific)

- **OC-3.1 (informational):** `recipe-feature-pipeline` self-reference in the `skills:` array of `execute-orchestrator.md` is preserved (the AC-CC-3 rationale-paragraph addition implies the underlying self-reference still exists). Grep confirms `recipe-feature-pipeline` appears in the `skills` block.
- **OC-3.2 (warning):** A full-codebase sweep `grep -rE "ADR-0034" .claude/ adrs/ working/` for any remaining ADR-0034 mis-credit elsewhere. Surfaces as warning if found (per Plan §Risks cross-phase row 2: "if found, surface as a follow-on edit during reconciliation, not in scope of this Plan").

### Acceptance tests scheduled for this phase

- ACs satisfied here: `AC-FR-3-a`, `AC-FR-3-b`, `AC-FR-3-c`, `AC-FR-4-c`, `AC-FR-5-a`, `AC-CC-1`, `AC-CC-3`.
- Acceptance-test IDs (parallel doc): `AT-FR-3-a-P3`, `AT-FR-3-b-P3`, `AT-FR-3-c-P3`, `AT-FR-4-c-P3`, `AT-FR-5-a-P3`, `AT-CC-1-P3`, `AT-CC-3-P3` (expected nomenclature).

### Failure response

- C1 / C2 / C8 fail (frontmatter integrity): Halt; amend frontmatter; bundle the fix into the next commit (NOT a separate commit, since C7 demands one bundled commit). If the bundled commit already exists, revert it (`git revert <T3.6-sha>`), re-do all 5 edits, and re-commit with the same message.
- C3 fail (ADR-0034 occurrence missed): Halt; locate and fix; same revert-and-re-bundle rule applies.
- C4 / C5 / C6 fail: Same revert-and-re-bundle rule.
- C7 fail (separate commits, wrong file set, or missing commit message phrase): Halt with `bundled-commit-constraint-violation` posture. This requires a `git reset --soft <T3.6-parent>` + re-stage + re-commit with the canonical message. Surface to user before executing the reset, because squashing already-pushed commits is destructive.

Rollback path: `git revert <T3.6-commit-sha>` restores all 5 sub-agent files to pre-Phase-3 state in one revert (Plan §Rollback Phase 3). This is the most consequential rollback boundary.

### Validator metadata

- **Run when:** After T3.6 is reported complete (the bundled-commit task). PV-3 has no value if run between T3.1–T3.5 because the bundled-commit constraint hasn't been checked yet.
- **Expected duration:** < 5 min.
- **Prerequisites:** PV-2 passed.

---

## PV-4 — Phase 4 State-Transitions Template Extension Validator

### Phase reference

Plan §"Phase 4 — state-transitions-log-entry-template.md extension folding" (tasks T4.1, T4.2).

### Validator goal

Prove the `state-transitions-log-entry-template.md` file's v1 `invoking_agent` invariant text is clarified as logical-owner form, AND the `void`/`void_reason` and `-prime` suffix extensions are folded into v1 documentation (not v2).

### Pass criteria

#### PV-4.C1 — Logical-owner clarification text present at the v1 invariant location

- **Description:** Around line 63 (or wherever the v1 `invoking_agent` invariant lives post-edit) of `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`, the new clarified text MUST be present, naming `execute-orchestrator` as the logical owner and `recipe-feature-pipeline` as the literal emitter.
- **Assertion:**
  - `grep -i "logical owner\\|LOGICAL OWNER" .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` returns a match.
  - `grep -c "execute-orchestrator" .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` ≥ 1.
  - `grep -c "recipe-feature-pipeline" .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` ≥ 1.
- **Source:** T4.1 L1+L2 verification + AC-FR-6-a, AC-NFR-6-a.
- **Automation hook:** `automated` — grep.
- **Severity:** `blocking`.

#### PV-4.C2 — `void` / `void_reason` extension documented as v1

- **Description:** Both `void` (boolean) and `void_reason` (string) MUST be documented in the template as v1 schema extensions (NOT v2), with at least one example referencing the in-flight log usage.
- **Assertion:**
  - `grep -c "void_reason" .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` ≥ 1.
  - `grep -E "\\bvoid\\b" <file>` returns at least 2 matches (field name + prose discussion).
  - `grep -i "v1 schema\\|v1 extension\\|fold.*into v1\\|v1 documentation" <file>` returns a match indicating the version positioning.
- **Source:** T4.2 L1+L2 verification.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-4.C3 — `-prime` transition-name suffix convention documented

- **Description:** The `-prime` suffix (e.g., `T0-prime`) MUST be documented as the re-entry-from-TERMINATED convention.
- **Assertion:**
  - `grep -c "\\-prime" .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` ≥ 1.
  - Within 5 lines of any `-prime` match: prose mentions "TERMINATED" or "re-entry" or "void".
- **Source:** T4.2 L1+L2 verification.
- **Automation hook:** `automated` — grep + proximity.
- **Severity:** `blocking`.

#### PV-4.C4 — Schema-vs-template consistency cross-check

- **Description:** The schema documentation at `recipe-feature-pipeline/SKILL.md` (Phase 1) and this template file MUST be consistent regarding `void` / `-prime` semantics; no contradictions.
- **Assertion:** Operator opens both files and confirms the `void` and `-prime` descriptions do not contradict each other. (Automated structural check: BOTH files contain the strings `void` AND `-prime`.)
- **Source:** T4.2 L3 verification.
- **Automation hook:** `mixed` — automated cross-file grep; operator confirms semantic consistency.
- **Severity:** `warning`. The contradictions, if any, surface in a manual diff; PV-4 cannot automatically resolve semantic disagreements.

### Operational checks (Phase 4 specific)

- **OC-4.1 (informational):** The 1 AC-FR-4-a open item (this file is outside the FR-4 8-file inventory) is closed by virtue of the Blueprint having captured user ratification — confirm the ratification reference is present in the Blueprint Fact Disposition table or open-items.md.

### Acceptance tests scheduled for this phase

- ACs satisfied here: `AC-FR-4-b` (schema lockstep, closing portion), `AC-FR-6-a` (logical-owner invariant in the template), `AC-NFR-6-a`, `AC-NFR-6-b`.
- Acceptance-test IDs (parallel doc): `AT-FR-4-b-P4`, `AT-FR-6-a-P4`, `AT-NFR-6-a-P4`, `AT-NFR-6-b-P4` (expected nomenclature).

### Failure response

- C1 / C2 / C3 fail: Halt; amend the template; re-run PV-4.
- C4 warning: Surface the inconsistency to the user; allow phase advance if the user explicitly accepts (per `warning` severity definition).

Rollback path: `git revert <T4.x-commit>` restores the template to pre-Phase-4 state. NFR-6-a is unaffected (in-flight artifacts remain valid under either invariant interpretation) per Plan §Rollback Phase 4.

### Validator metadata

- **Run when:** After T4.1, T4.2 reported complete. Phase 4 forks from Phase 1 and runs in parallel with Phases 2+3 per the Plan dependency graph; PV-4 may execute before PV-3 if the parallel branch finishes first.
- **Expected duration:** < 3 min.
- **Prerequisites:** PV-1 passed (T1.3 is the upstream dependency for T4.1 per the Plan graph).

---

## PV-5 — Phase 5 FR-5 Inventory + ADR-0045 Interim Discipline Validator

### Phase reference

Plan §"Phase 5 — FR-5 inventory artifact + ADR-0045 manual-review interim documentation" (tasks T5.1, T5.2).

### Validator goal

Prove the FR-5 inventory artifact exists with the five required enumerated elements, and the ADR-0045 manual-review interim discipline is documented with its four required elements + a follow-on feature pointer.

### Pass criteria

#### PV-5.C1 — FR-5 inventory artifact file existence

- **Description:** `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/agent-tool-grant-inventory.md` (or equivalent) MUST exist.
- **Assertion:**
  - `test -f working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/agent-tool-grant-inventory.md` exits 0, OR an equivalent path is documented and exists.
- **Source:** T5.1 L1 verification + AC-FR-5-b.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-5.C2 — FR-5 inventory artifact contains the five enumerated elements

- **Description:** The artifact MUST enumerate: (a) total files swept (36 per codebase analysis FR-5 sweep result); (b) the 2 violations found pre-repair (with `tools:` arrays cited verbatim); (c) the post-repair confirmation that both violations are cleaned; (d) ADR-0045 cross-reference; (e) note that the 34 other agents declare no `Agent` and are out of scope.
- **Assertion:**
  - `grep -E "36" <inventory-file>` returns a match (total files swept).
  - `grep -c "execute-orchestrator.md" <inventory-file>` ≥ 1 AND `grep -c "execute-finalize-reconciler.md" <inventory-file>` ≥ 1 (the 2 violations).
  - `grep -E "post-repair|cleaned|both violations" <inventory-file>` returns a match.
  - `grep -c "ADR-0045" <inventory-file>` ≥ 1.
  - `grep -E "34 other|34 agents|out of scope" <inventory-file>` returns a match.
- **Source:** T5.1 L2 verification.
- **Automation hook:** `automated` — multi-grep.
- **Severity:** `blocking`.

#### PV-5.C3 — Inventory artifact reproducibly verifies post-repair state

- **Description:** A reviewer reading the artifact can independently verify the post-repair state by grepping the codebase for `Agent` in `.claude/agents/*.md` tools arrays. Both target files now have NO `Agent` declaration.
- **Assertion:**
  - `grep -lE "^tools:.*\\bAgent\\b" .claude/agents/*.md` returns NO matches (or returns ONLY known-acceptable design-time agents per the inventory artifact's out-of-scope note).
  - Cross-reference: any file returned by the above grep MUST be cited in the inventory artifact as out-of-scope, OR PV-5.C3 fails.
- **Source:** T5.1 L3 verification + AC-FR-5-a downstream check.
- **Automation hook:** `automated` — grep across `.claude/agents/`.
- **Severity:** `blocking`.

#### PV-5.C4 — ADR-0045 manual-review interim discipline documented with four elements

- **Description:** A documented interim discipline (either as a section within the inventory artifact OR as a separate `working/feature/<slug>/adr-0045-manual-review-interim.md`) MUST contain all four required elements: (a) where in the agent-authoring lifecycle the manual review fires; (b) who enforces; (c) what triggers the review; (d) explicit cross-reference to a follow-on feature ticket placeholder.
- **Assertion:** Locate the interim-discipline doc:
  - `grep -lE "ADR-0045.*manual.*review|manual.*review.*interim" working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/` returns at least one file.
  - In the matched file: greps for keywords associated with each of the four elements return matches: (a) `design-cc|design-composer|agent-authoring`; (b) `shared-document-reviewer|review-architecture-auditor|Gate 1`; (c) `tools.*array|PR or feature.*adds|trigger`; (d) `follow-on|audit-machinery|SA-13.*extension`.
- **Source:** T5.2 L1+L2 verification + AC-FR-8-a (interim discipline portion).
- **Automation hook:** `automated` — recursive grep + per-element keyword greps.
- **Severity:** `blocking`.

#### PV-5.C5 — Follow-on feature pointer recorded

- **Description:** A pointer to a yet-to-be-created follow-on feature (the audit-machinery extension for ADR-0045) MUST exist either as a placeholder slug or as a TODO marker pointing to the future ticket location.
- **Assertion:**
  - `grep -E "follow-on feature|follow-on slug|TODO.*ADR-0045|audit-extension" <interim-discipline-doc>` returns a match.
- **Source:** T5.2 L1 verification + Plan §Open Items item 2.
- **Automation hook:** `automated`.
- **Severity:** `warning`. The Plan surfaces this as an open item for the cross-artifact auditor; a placeholder pointer is sufficient per Plan §Open Items.

### Operational checks (Phase 5 specific)

- **OC-5.1 (informational):** A future agent-authoring feature in this project can locate and apply the interim discipline without ambiguity — operator skims and confirms readability (T5.2 L3 verification).

### Acceptance tests scheduled for this phase

- ACs satisfied here: `AC-FR-5-a` (closing portion — inventory recording the post-Phase-3 state), `AC-FR-5-b` (inventory artifact), `AC-FR-8-a` (interim discipline portion).
- Acceptance-test IDs (parallel doc): `AT-FR-5-a-P5`, `AT-FR-5-b-P5`, `AT-FR-8-a-P5` (expected nomenclature).

### Failure response

- C1 / C2 / C3 / C4 fail: Halt; author or amend the affected artifact; re-run.
- C5 warning: Surface to user; allow phase advance if user accepts the placeholder.

Rollback path: Artifact-only rollback — delete the inventory file and any interim-discipline doc (Plan §Rollback Phase 5).

### Validator metadata

- **Run when:** After T5.1, T5.2 reported complete.
- **Expected duration:** < 2 min.
- **Prerequisites:** PV-3 passed (the bundled commit closes the post-repair state that T5.1 records).

---

## PV-6 — Phase 6 Rollout: Synthetic Test Feature Verification Validator (F-7 constrained)

### Phase reference

Plan §"Phase 6 — Rollout: synthetic minimal test feature (FR-6) verification under F-7 fresh-session constraint" (tasks T6.1, T6.2, T6.3, T6.4, conditional T6.5).

### Validator goal

Prove the synthetic test feature exists, the operator restarted the session before T6.3, the end-to-end synthetic run produced the expected audit-trail artifacts (state-transitions.log per-specialist-boundary entries; checkpoint.json cycle counters increment at T4/T10; `invoking_agent: "execute-orchestrator"` preserved across log entries), and the synthetic feature is archived as a regression artifact.

This is the load-bearing verification validator for the entire feature; failure here means the repair did NOT achieve its objective.

### Pass criteria

#### PV-6.C1 — Synthetic test feature directory + artifacts exist

- **Description:** The synthetic test feature directory MUST exist under `working/test-features/dispatch-mechanism-regression/` (or equivalent per NFR-7) and MUST contain at minimum: an intent or PRD document, a Blueprint, a Plan, and a tasks.json (per the recipe-feature-pipeline taxonomy).
- **Assertion:**
  - `test -d working/test-features/dispatch-mechanism-regression/` exits 0 (or alternative path is documented and exists).
  - Inside the directory: at least 3 of `intent-clarification.md`, `prd-v1.md`, `blueprint-v1.md`, `plan-v1.md`, `tasks.json` are present.
- **Source:** T6.1 L1 verification + AC-NFR-7-a.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-6.C2 — Synthetic test feature does NOT author new sub-agent files (F-7 vacuous-satisfaction design)

- **Description:** The synthetic test feature MUST NOT have authored any new sub-agent files under `.claude/agents/`. This keeps AC-FR-6-d vacuously satisfied per T6.1's design constraint.
- **Assertion:**
  - `find working/test-features/ -path "*/\\.claude/agents/*.md" -type f` returns NO results.
  - Independently: `git log --since="<T6.1-start>" --diff-filter=A --name-only -- .claude/agents/` returns NO new files added.
- **Source:** T6.1 L2 verification.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-6.C3 — Operator session restart confirmation (T6.2)

- **Description:** Before T6.3 invocation, the operator MUST have restarted the Claude Code session. Evidence: either a confirmation prompt response logged in the verification log, or a fresh-session timestamp explicitly recorded.
- **Assertion:**
  - The verification log (T6.4 output, when written) or a `t6.2-session-restart-confirmation.txt` artifact contains:
    - An ISO-8601 fresh-session timestamp.
    - An operator acknowledgement string (e.g., "session restarted before T6.3" or equivalent).
  - OR: `checkpoint.json` for the synthetic feature contains a `session_restart: { confirmed: true, timestamp: <ISO> }` entry.
- **Source:** T6.2 L1+L2 verification + AC-FR-6-d.
- **Automation hook:** `operator-facing` — the operator records and the validator reads. The validator CANNOT autonomously verify a session restart; it can only confirm the artifact is present. Per the F-7 substrate observation, this gate is non-automatable.
- **Severity:** `blocking`.

#### PV-6.C4 — state-transitions.log emits per-specialist-boundary entries

- **Description:** The synthetic test feature's `state-transitions.log` MUST contain at least one entry per specialist sub-agent dispatch boundary, with each entry attributable to a distinct sub-agent context.
- **Assertion:** Locate `state-transitions.log` for the synthetic run. For each of the 4 specialists (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`) that should dispatch given the synthetic feature's task shape:
  - `grep -c '"to_agent"[ ]*:[ ]*"<specialist-name>"' <log-path>` ≥ 1 (or equivalent field path per the log entry schema).
  - At least 4 dispatch boundary entries total (one per specialist).
- **Source:** T6.3 L1+L2 verification + AC-FR-6-a + AC-NFR-2-a.
- **Automation hook:** `automated` — JSONL grep + count.
- **Severity:** `blocking`.

#### PV-6.C5 — checkpoint.json cycle counters increment at task/phase boundaries (T4 / T10)

- **Description:** The synthetic test feature's `checkpoint.json` MUST show per-task counter increments at T4 transitions and per-phase counter increments at T10 transitions; T0 and T13 MUST NOT increment counters per I-AA-609 invariant 10.
- **Assertion:** Parse `checkpoint.json`:
  - `python3 -c "import json; c=json.load(open('<ckpt>')); per_task = c['execution_pipeline_cycle_counters']['per_task']; per_phase = c['execution_pipeline_cycle_counters']['per_phase']; assert any(v >= 1 for v in per_task.values()), per_task; assert any(v >= 1 for v in per_phase.values()), per_phase; print('OK')"` exits 0.
  - Cross-reference state-transitions.log: each per_task counter increment matches a T4 transition entry; each per_phase increment matches a T10 transition entry. (Manual cross-check; partial automation possible.)
- **Source:** T6.3 L2 verification + AC-FR-6-b + AC-NFR-3-a.
- **Automation hook:** `mixed` — JSON parse + manual cross-check on the transition correspondence.
- **Severity:** `blocking`.

#### PV-6.C6 — invoking_agent: "execute-orchestrator" preserved across all log entries

- **Description:** Every state-transitions.log entry written during the synthetic run MUST set `invoking_agent: "execute-orchestrator"` per the v1 logical-owner invariant (even though the literal emitter is `recipe-feature-pipeline`).
- **Assertion:**
  - For every JSONL line in `<log-path>`: `python3 -c "import json,sys; lines=[l for l in open(sys.argv[1]) if l.strip()]; bad=[l for l in lines if json.loads(l).get('invoking_agent') != 'execute-orchestrator']; assert not bad, f'{len(bad)} entries with wrong invoking_agent'; print(f'{len(lines)} entries OK')" <log-path>` exits 0.
- **Source:** T6.3 L2 verification + AC-FR-6-a + AC-NFR-2-b + AC-NFR-6-a.
- **Automation hook:** `automated` — JSONL parse + assertion.
- **Severity:** `blocking`.

#### PV-6.C7 — Synthetic feature completes through T12 (pipeline_complete)

- **Description:** The synthetic test feature MUST complete through the canonical T12 (pipeline_complete) state-transition; a `pipeline-run-summary.json` MUST be written; the four load-bearing audit-trail properties documented in source analysis §3.2 are restored.
- **Assertion:**
  - `grep -c '"to_state"[ ]*:[ ]*"T12"\\|pipeline_complete' <log-path>` ≥ 1.
  - `test -f <synthetic-feature-dir>/pipeline-run-summary.json` exits 0.
- **Source:** T6.3 L3 verification.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-6.C8 — Verification log + archival exist

- **Description:** `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/verification-log.md` MUST exist, naming FR-6 as gating and (if performed) FR-7 as the confidence check. The synthetic test feature is archived under `working/test-features/<test-slug>/` per NFR-7-a.
- **Assertion:**
  - `test -f working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/verification-log.md` exits 0.
  - The file contains BOTH strings "FR-6" and "gating" within 5 lines of each other.
  - The synthetic feature directory still exists under `working/test-features/` (not deleted post-run).
- **Source:** T6.4 L1+L2+L3 verification + AC-FR-7-a + AC-NFR-7-a.
- **Automation hook:** `automated`.
- **Severity:** `blocking`.

#### PV-6.C9 — Negative-path conditional: verification-failed posture on T6.3 failure

- **Description:** If T6.3 fails (any of AC-FR-6-a/b/c do not hold), a `verification-failed.md` posture artifact MUST exist; `checkpoint.json` records the failure mode; the escalation routes through the standard reconciliation pipeline (no silent workaround fallback per AC-NFR-1-b).
- **Assertion:** (only evaluated if PV-6.C4 or PV-6.C5 or PV-6.C6 or PV-6.C7 failed):
  - `test -f working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/verification-failed.md` exits 0.
  - `checkpoint.json` contains a `verification_failure_mode` or equivalent recorded entry.
- **Source:** T6.5 L1+L2 verification + AC-FR-6-c (negative path) + AC-NFR-1-b.
- **Automation hook:** `automated` — conditional execution.
- **Severity:** `blocking` (conditional).

### Operational checks (Phase 6 specific)

- **OC-6.1 (informational):** A future operator can re-run the archived synthetic test feature against any future dispatch-mechanism change without re-authoring (T6.4 L3).
- **OC-6.2 (warning):** If the synthetic test feature design includes a NEEDS_RECONCILIATION trigger (Plan §Open Items item 3), confirm the `dispatch_directives[]` malformed-array escalation path was exercised (AC-CC-4). If not exercised, surface to the cross-artifact auditor.

### Acceptance tests scheduled for this phase

- ACs satisfied here: `AC-FR-6-a`, `AC-FR-6-b`, `AC-FR-6-c`, `AC-FR-6-d`, `AC-FR-7-a`, `AC-NFR-1-a`, `AC-NFR-1-b`, `AC-NFR-2-a`, `AC-NFR-2-b`, `AC-NFR-3-a`, `AC-NFR-3-b`, `AC-NFR-7-a`.
- Acceptance-test IDs (parallel doc): `AT-FR-6-a-P6` through `AT-FR-6-d-P6`, `AT-FR-7-a-P6`, `AT-NFR-1-a-P6`, `AT-NFR-1-b-P6`, `AT-NFR-2-a-P6`, `AT-NFR-2-b-P6`, `AT-NFR-3-a-P6`, `AT-NFR-3-b-P6`, `AT-NFR-7-a-P6` (expected nomenclature).

### Failure response

- C1 / C2 fail: Author or correct the synthetic test feature; re-run.
- C3 fail (operator session restart not confirmed): The validator CANNOT proceed past this gate without operator action. Pause; surface to user; require operator to restart and confirm before re-running.
- C4 / C5 / C6 / C7 fail: Activate T6.5 negative-path. Surface `verification-failed` posture per AC-FR-6-c. Do NOT declare the feature complete. Re-engage the per-layer cc Design / Blueprint reconciliation loop via the standard pipeline cycle path.
- C8 fail: Author the verification log; archive the synthetic feature; re-run PV-6.C8 only.
- C9 (conditional) fail when T6.5 should have fired: Halt with `negative-path-discipline-violation` posture — the system did not surface failure explicitly; this is a load-bearing AC-NFR-1-b violation requiring escalation.

Rollback path: Synthetic test feature archive removal + verification-log retraction (Plan §Rollback Phase 6). Rollback of Phase 6 does NOT reverse Phases 0–5; for a full rollback see PV-Cross §Full Rollback.

### Validator metadata

- **Run when:** After T6.4 reported complete (and conditionally T6.5 if T6.3 failed).
- **Expected duration:** 10–30 min (the synthetic test feature run itself is multi-hour; PV-6 runs after it completes, inspecting artifacts).
- **Prerequisites:** PV-5 passed AND PV-4 passed (both Phase 5 and Phase 4 must complete before Phase 6 per the Plan dependency graph).

---

## PV-Cross — Cross-Validator Coordination

### Validator dependency graph

```
PV-0 ──► PV-1 ──► PV-2 ──► PV-3 ──┐
              │                    │
              └──► PV-4 ──────────►┤
                                   │
                                   ▼
                                  PV-5 ──► PV-6
```

Notes:

- **PV-0 → PV-1** strict: no Phase-1 edit may begin until baseline is captured and ADRs verified.
- **PV-1 → PV-2** strict: D-004 schema closure precedes D-001 dispatch absorption (synthesis Constraint 5.1, Plan §Cross-Phase Sequencing Constraints item 1).
- **PV-1 → PV-4** valid edge: T4.1 depends on T1.3 per the Plan graph; PV-4 may run in parallel with PV-2 and PV-3.
- **PV-2 → PV-3** strict: dispatch section + Contract 6 are referenced by the reconciler's new emission contract (T3.3 depends on T2.1+T2.2).
- **PV-3 → PV-5** strict: the bundled commit T3.6 closes the post-repair state that T5.1 records.
- **PV-4 → PV-6** AND **PV-5 → PV-6** both required: T6.1 depends on both T5.1 and T4.2.
- **PV-6** is the load-bearing terminal validator.

### Cross-phase prerequisite checks

These checks verify the dependency edges from the Plan's Task Inventory hold:

| Edge | Check | Automation |
|---|---|---|
| PV-0 → PV-1 | `rollback-baseline.txt` exists AND its SHA matches a commit reachable from current HEAD | `automated` |
| PV-1 → PV-2 | `git log --grep="schema closure"` commit-time < `git log --grep="Execution Phase Dispatch"` commit-time | `automated` (covered by PV-2.C2) |
| PV-2 → PV-3 | `git log --grep="dispatch_directives"` commit-time < `git log --grep="FR-5 sweep closure"` commit-time | `automated` |
| PV-3 → PV-5 | The bundled-commit SHA from PV-3.C7 is an ancestor of HEAD when T5.1's inventory artifact is committed | `automated` — `git merge-base --is-ancestor <T3.6-sha> HEAD` |
| PV-1 → PV-4 | T4.1 commit timestamp ≥ T1.3 commit timestamp | `automated` |
| PV-4 → PV-6 AND PV-5 → PV-6 | T6.1 commit timestamp ≥ max(T4.2 timestamp, T5.1 timestamp) | `automated` |
| F-7 fresh-session gate (PV-6.C3) | Operator restart confirmation artifact predates T6.3 invocation timestamp | `operator-facing` |

### Critical-path validators

The critical-path validators (failure of any one most delays the feature):

1. **PV-3** — the bundled-commit constraint is the most failure-prone (atomic-commit discipline). Failure forces a `git reset --soft` cascade.
2. **PV-6** — the load-bearing functional verification; failure forces re-engagement of the per-layer cc Design loop.
3. **PV-1** — schema closure is the precondition for two downstream phases (Phase 2 and Phase 4); failure cascades.

### Parallelizable validator checks

Within a single validator, the following criteria can run in parallel:

- **PV-1:** C1 / C2 / C3 / C4 / C5 (all greps independent); C6 must run after a clean commit.
- **PV-3:** C1, C2, C3, C4, C5, C6, C8 (all file-content checks independent); C7 (bundled-commit) runs after all per-file checks pass.
- **PV-6:** C1, C2 (pre-run artifact checks) parallelizable; C4, C5, C6, C7 (post-run artifact checks) parallelizable.

### Shared validator infrastructure

- **YAML frontmatter parser:** a Python one-liner via `python3 -c "import yaml; ..."`. Used by PV-0.C2, PV-1.C6, PV-3.C1, PV-3.C2, PV-3.C8.
- **JSONL log parser:** Python `json.loads()` line-by-line. Used by PV-6.C4, PV-6.C6.
- **Git ancestry / log-time queries:** `git log --format=%ct`, `git merge-base --is-ancestor`. Used by PV-2.C2, PV-3.C7, all Cross-Phase prerequisite checks.
- **Section-slicing utility:** awk or sed (`sed -n "${L_start},${L_end}p"`) for delimiting a markdown section by header anchors. Used by PV-2.C3 / C4 / C5 / C6.

### Operator-facing validators (cannot be fully automated)

- **PV-6.C3** — operator session restart confirmation. The F-7 substrate constraint makes this gate non-automatable; the validator can only confirm an operator-recorded artifact is present.
- **PV-4.C4** (warning-severity) — semantic consistency between schema and template; structural cross-checks are automated, but final semantic-disagreement adjudication is operator-facing.
- **PV-6.C5** — counter increment vs T4/T10 transition correspondence; the count assertion is automated, but the cross-check of "this increment corresponds to that transition" benefits from operator review.

### Validator runbook

How a human operator triggers, monitors, and interprets validator results during a real execution:

1. **Phase 0 complete:** Operator runs `bash phase-validator.sh PV-0` (or equivalent). Reads pass/fail report. On fail, applies failure-response steps; re-runs until pass.
2. **Phase 1 complete (after T1.3):** `bash phase-validator.sh PV-1`. Note that PV-4 can begin in parallel from this point.
3. **Phase 2 complete (after T2.3):** `bash phase-validator.sh PV-2`. PV-2.C2 (commit-ordering check) is sensitive to rebases — if commits have been amended, re-confirm timestamps.
4. **Phase 3 complete (after T3.6 — the bundled commit):** `bash phase-validator.sh PV-3`. This is the longest-running and most failure-sensitive validator. Pay special attention to PV-3.C7 (the bundled-commit constraint) — if it fails, do NOT proceed to Phase 5.
5. **Phase 4 complete (parallel branch):** `bash phase-validator.sh PV-4`. May complete before or after PV-2/PV-3.
6. **Phase 5 complete:** `bash phase-validator.sh PV-5`. Requires PV-3 passed.
7. **Phase 6 pre-run (after T6.1):** Validate PV-6.C1, PV-6.C2 only — synthetic test feature exists and authors no sub-agents. Operator then performs T6.2 session restart and records the confirmation artifact.
8. **Phase 6 run (T6.3):** Operator invokes `/feature-pipeline` against the synthetic test feature in a fresh session. After the run completes (multi-hour), runs `bash phase-validator.sh PV-6` to validate C3 through C8.
9. **Phase 6 negative path (conditional, if T6.3 failed):** Operator confirms T6.5 ran and PV-6.C9 passes; surfaces `verification-failed` posture.
10. **All PVs passed:** The feature is functionally complete. Stage-13 packager will fire its known BLOCKER on the canonical-root-only ADR placement; operator applies the documented waiver (per PV-0.C3).

### Full rollback (nuclear option)

`git reset --hard <baseline-sha-from-rollback-baseline.txt>` reverts the entire feature to the Phase-0 baseline. This is Plan §Rollback's "nuclear option" and is sequenced as the last-resort response to any cross-phase corruption that per-phase rollback cannot address.

---

## Validator coverage summary

| Phase | Validator | Criteria | Blocking | Warning | Informational | Automation profile |
|---|---|---|---|---|---|---|
| Phase 0 | PV-0 | 4 | 4 | 0 | 1 (OC) | Fully automated |
| Phase 1 | PV-1 | 6 | 6 | 1 (OC) | 1 (OC) | Fully automated |
| Phase 2 | PV-2 | 6 | 6 | 1 (OC) | 1 (OC) | Fully automated |
| Phase 3 | PV-3 | 8 | 8 | 1 (OC) | 1 (OC) | Fully automated |
| Phase 4 | PV-4 | 4 | 3 | 1 | 1 (OC) | Mostly automated; one semantic check is mixed |
| Phase 5 | PV-5 | 5 | 4 | 1 | 1 (OC) | Fully automated |
| Phase 6 | PV-6 | 9 | 9 (one conditional) | 1 (OC) | 1 (OC) | Mostly automated; PV-6.C3 operator-facing; PV-6.C5 mixed |

Total: 42 pass criteria + 7 operational checks across 7 validators. 1 criterion is operator-facing (PV-6.C3); 2 criteria are mixed automation (PV-4.C4, PV-6.C5); the remaining 39 are fully automatable via shell + Python one-liners.

## Update history

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-24 | test-phase-validator-author | Initial composition. 7 validators × 42 pass criteria. Authored in parallel with `acceptance-tests.md`; AC IDs referenced from PRD/Blueprint directly. |
