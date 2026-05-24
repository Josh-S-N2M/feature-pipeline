---
id: Plan-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: plan
version: 1.1.0
status: draft
version_history:
  - {version: "1.0.0", date: "2026-05-24T00:00:00Z", note: "Initial composition by plan-author"}
  - {version: "1.1.0", date: "2026-05-24T00:30:00Z", note: "v1.1.0 patch absorbing reviewer findings I-Plan-001 (added Task Inventory section), I-Plan-002 (added 6 missing AC mapping rows for AC-FR-1-a/b/c satisfied-upstream + AC-FR-2-a/b/c vacuous-by-kc2), I-Plan-004 (clarified Cross-Phase Dependencies graph)"}
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
scope_class: FULL
layer_scope: [cc]
derived_from:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/blueprint-v1.md
  - adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md
  - adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis-report.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-dependencies.json
phases: 7
total_tasks: 24
generated: 2026-05-24T00:00:00Z
generated_by: plan-author
---

# Plan: execute-orchestrator Dispatch Mechanism Repair (r1)

## Contents

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — Schema closure on recipe-feature-pipeline/SKILL.md (D-004)
- [x] Phase 2 — Dispatch-section absorption into recipe-feature-pipeline/SKILL.md (D-001)
- [x] Phase 3 — Sub-agent file edits (bundled `Agent`-removal commit + 3-occurrence ADR sweep + prose updates)
- [x] Phase 4 — state-transitions-log-entry-template.md extension folding (1 AC-FR-4-a open item)
- [x] Phase 5 — FR-5 inventory artifact + ADR-0045 manual-review interim documentation
- [x] Phase 6 — Rollout: synthetic minimal test feature (FR-6) verification under F-7 fresh-session constraint
- [x] Cross-Phase Dependencies
- [x] Cross-Phase Sequencing Constraints
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Verification Strategy
- [x] Rollback Procedure
- [x] Risks + Mitigations
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

The Plan is the executable decomposition of the Blueprint (`blueprint-v1.md` v1.1.0, Gate 4 + Architecture Audit pass) into phases and tasks for the kill-criterion-#2 FULL-repair path. ADR-0044 selected option (a) flatten dispatch hierarchy; ADR-0045 codified the project-wide convention that sub-agents MUST NOT declare `Agent` in their `tools:` array. This Plan sequences the implementation under three load-bearing sequencing constraints surfaced by the Blueprint: (1) edit ordering on `recipe-feature-pipeline/SKILL.md` (D-004 schema closure BEFORE D-001 dispatch section absorption per I-DR-004); (2) bundled `Agent`-removal commit across `execute-orchestrator.md` + `execute-finalize-reconciler.md` per synthesis Constraint 5.2; (3) F-7 mid-session-agent-registry constraint requiring a fresh session for FR-6 verification.

This Plan does NOT re-design. Where the Blueprint surfaces a decision (option choice, edit ordering, ADR placement, dispatch_directives[] indirection), the Plan inherits it and sequences delivery accordingly.

## Source

- **Blueprint:** `blueprint-v1.md` v1.1.0 (post-Architecture-Audit pass).
- **ADRs ratified this run:** ADR-0044 (flatten dispatch hierarchy) and ADR-0045 (sub-agent `Agent`-grant prohibition); both at canonical root `adrs/` per ADR-0036 placement disposition.
- **Inherited ADRs constraining sequencing:** ADR-0017 (4-cycle cap), ADR-0019 (naming), ADR-0021 (KB-and-ADR-first), ADR-0022 (reasoning-config audit), ADR-0027 (cwd = repo root), ADR-0029 (no silent scope changes), ADR-0033 (symmetric D-12), ADR-0035 (auditing-shared binding), ADR-0036 (single-location ADR placement).
- **Phase taxonomy:** Phase 0 (setup + ADR placement check) → Phases 1–5 (feature delivery) → Phase 6 (rollout: synthetic test feature verification + F-7 fresh-session gate + archival as regression artifact).

## Phase 0 — Setup

### Goal

Establish pre-edit groundwork: confirm canonical ADR placement, snapshot the affected files for rollback baseline, and document the expected Stage-13 packager interaction (known BLOCKER + waiver path inherited from the ADR-0036 partial-amendment defect).

### Tasks

#### T0.1: Verify ADR-0044 + ADR-0045 placement at canonical root

- **Layer:** Claude Code
- **Description:** Confirm both new ADRs are present at `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md` and `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md`. Confirm NO feature-scoped duplicates exist under `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/adrs/`. This honors the Blueprint's "ADR-0036 placement disposition: honor-adr-0036-canonical-root" + the user's Gate-7 ratification.
- **Dependencies:** none
- **Estimate:** XS (5 min — file existence + path check)
- **Satisfies AC:** N/A (setup-only; supports AC-FR-8-a placement compliance)
- **L1 verification:** `ls adrs/ADR-0044-*.md adrs/ADR-0045-*.md` returns both files; `ls working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/adrs/` does NOT contain ADR-0044 or ADR-0045 duplicates.
- **L2 verification:** Both ADRs parse as valid markdown with required frontmatter (`id`, `status: accepted`, `supersedes` empty, `change_summary` present).
- **L3 verification:** Cross-referenced from Blueprint `adrs_authored:` frontmatter; CodeQL-style grep confirms no stale feature-scoped path strings remain in the Blueprint or PRD.

#### T0.2: Document the expected Stage-13 packager BLOCKER + waiver path

- **Layer:** Claude Code
- **Description:** Record in the working directory's `open-items.md` (or equivalent) that the Stage-13 deliverable-packager will emit a BLOCKER on the absence of feature-scoped ADR copies under `working/feature/<slug>/adrs/`. This is a KNOWN issue inherited from the ADR-0036 partial-amendment defect — the packager check has not been updated to align with the canonical-root-only placement ADR-0036 mandates. The waiver path is: operator explicitly acknowledges the BLOCKER and proceeds, citing the Blueprint's "ADR-0036 placement disposition" entry and the user's ratification token.
- **Dependencies:** T0.1
- **Estimate:** XS (10 min)
- **Satisfies AC:** N/A (operational pre-warning; no AC tied)
- **L1 verification:** `working/feature/<slug>/open-items.md` contains an entry titled "Stage-13 packager BLOCKER on canonical-root-only ADR placement — known issue, waiver path documented".
- **L2 verification:** The entry cites Blueprint's "ADR-0036 placement disposition" section and ADR-0036 itself.
- **L3 verification:** When Stage-13 packager runs (post-execution), the operator confirms the expected BLOCKER fires and applies the documented waiver.

#### T0.3: Snapshot affected-files baseline for rollback

- **Layer:** Claude Code
- **Description:** Capture `git rev-parse HEAD` and confirm working tree is clean (no uncommitted changes in the 8 in-inventory files + 1 outside-inventory file) before Phase 1 begins. Record the baseline commit SHA in `working/feature/<slug>/rollback-baseline.txt`.
- **Dependencies:** none
- **Estimate:** XS (5 min)
- **Satisfies AC:** N/A (rollback infrastructure; supports Rollback Procedure)
- **L1 verification:** `rollback-baseline.txt` exists and contains a 40-char SHA + ISO timestamp.
- **L2 verification:** `git status --porcelain` is empty for the 9 affected paths.
- **L3 verification:** A `git checkout <baseline-sha> -- <path>` for any affected file cleanly reverts.

### Phase 0 Exit Criteria

- Both new ADRs verified at canonical root with no feature-scoped duplicates.
- Stage-13 packager BLOCKER + waiver path documented as a known follow-on.
- Rollback baseline SHA captured.

Phase Validator (downstream `phase-validators.md`): MUST test all three exit criteria; Phase 0 isn't done until all three pass.

## Phase 1 — Schema closure on recipe-feature-pipeline/SKILL.md (D-004)

### Goal

Close the canonical `checkpoint.json` schema-reference gap at `recipe-feature-pipeline/SKILL.md` lines 96–128 by documenting the three execution-phase fields AND fold the `void` / `-prime` extensions and `invoking_agent` logical-owner clarification into the same edit pass — BEFORE the dispatch section is added.

This phase MUST complete before Phase 2 per Blueprint Implementation Plan §1 → §2 ordering (I-DR-004 absorption, synthesis Constraint 5.1: schema closure FIRST, dispatch absorption SECOND).

### Tasks

#### T1.1: Add `execution_pipeline_state_transitions` field to canonical schema reference

- **Layer:** Claude Code
- **Description:** Edit `.claude/skills/recipe-feature-pipeline/SKILL.md` at the canonical `checkpoint.json` schema reference block (currently lines 96–128 per codebase analysis FD-1). Add the `execution_pipeline_state_transitions` array field with the per-entry shape observed in the in-flight `devcontainer-mcp-provisioning-r1/checkpoint.json:8-16`: `{transition, from, to, timestamp, trigger, void?, void_reason?}`. Document as v1 schema. Preserve byte-for-byte the existing planning-side fields above and below the insertion point.
- **Dependencies:** T0.3
- **Estimate:** S (45 min)
- **Satisfies AC:** AC-FR-4-b, AC-NFR-5-a, AC-CC-2
- **L1 verification:** `grep -n 'execution_pipeline_state_transitions' .claude/skills/recipe-feature-pipeline/SKILL.md` returns at least one match inside the lines-96–128 region.
- **L2 verification:** A test reader (e.g., a quick `python -c "import yaml; yaml.safe_load(open('SKILL.md').read())"` on the frontmatter) confirms the file is still well-formed; the schema block parses as expected by visual inspection against codebase-analysis FD-7.
- **L3 verification:** The field's documented shape matches the in-flight artifact at `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json:8-16` (no schema drift between canonical reference and de facto schema).

#### T1.2: Add `execution_mode` and `execution_pipeline_cycle_counters` fields

- **Layer:** Claude Code
- **Description:** In the same schema reference block, add (a) `execution_mode` as a free-form string field with documented v1 values `"single-agent-fallback"` (preserved for the workaround run per NFR-6-b) and `"specialist-isolation"` (the post-repair value); (b) `execution_pipeline_cycle_counters` as a nested object `{per_task: {<task-id>: <int>}, per_phase: {<phase-id>: <int>}}` with the rule that counters increment ONLY at T4 (per_task) and T10 (per_phase) per I-AA-609 invariant 10 (referenced from the dispatch section to be added in Phase 2).
- **Dependencies:** T1.1
- **Estimate:** S (30 min)
- **Satisfies AC:** AC-FR-4-b, AC-NFR-5-a, AC-CC-2
- **L1 verification:** `grep -nE 'execution_mode|execution_pipeline_cycle_counters' .claude/skills/recipe-feature-pipeline/SKILL.md` returns matches inside the schema block.
- **L2 verification:** Schema block describes both v1 values for `execution_mode` and references the T4/T10 increment rule in prose.
- **L3 verification:** Cross-references `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json:37-39` shape exactly.

#### T1.3: Author state-transitions-log per-entry schema sub-section in SKILL.md (or cross-reference it)

- **Layer:** Claude Code
- **Description:** In the same schema-reference region of `recipe-feature-pipeline/SKILL.md`, ensure the per-entry state-transitions.log schema is either inlined or explicitly cross-referenced to `state-transitions-log-entry-template.md` (the file edited in Phase 4). Document the `void` / `void_reason` fields and the `-prime` transition-name suffix convention as observed in the in-flight log. This is the schema half of the lockstep; the template half lives in Phase 4 per Blueprint §5 split.
- **Dependencies:** T1.1
- **Estimate:** S (30 min)
- **Satisfies AC:** AC-FR-4-b, AC-NFR-5-a
- **L1 verification:** A grep for `void` and `-prime` in the schema region returns matches OR a cross-reference link to `state-transitions-log-entry-template.md` exists in the schema region.
- **L2 verification:** The schema region is self-consistent (no broken cross-reference).
- **L3 verification:** Reading the schema region top-to-bottom yields a complete v1 schema picture for both `checkpoint.json` execution-phase fields and `state-transitions.log` per-entry shape.

### Phase 1 Exit Criteria

- `recipe-feature-pipeline/SKILL.md` schema-reference region (lines 96–128 originally) documents all three execution-phase `checkpoint.json` fields with documented v1 semantics.
- The schema-reference region documents (or cross-references) the `void` / `-prime` extensions for state-transitions.log.
- No edits to any other file occurred in this phase.

## Phase 2 — Dispatch-section absorption into recipe-feature-pipeline/SKILL.md (D-001)

### Goal

Add the new "Execution Phase Dispatch" section to `recipe-feature-pipeline/SKILL.md` that documents how the parent skill drives the 14-row T0..T13 state machine, dispatches the four specialists at main-conversation level, consumes `dispatch_directives[]` from the reconciler, and writes per-task/per-phase counters to the schema documented in Phase 1.

This phase MUST follow Phase 1 (the dispatch section references the schema fields documented there).

### Tasks

#### T2.1: Add "Execution Phase Dispatch" section after Step 14 / Gate 6

- **Layer:** Claude Code
- **Description:** Append a new section to `recipe-feature-pipeline/SKILL.md` immediately after the existing Gate-6 section (around line 299 per codebase analysis). The section enumerates the per-task loop (T0 → T1 dispatch code-producer → T2 dispatch quality-handler → T3/T4/T5 verdict handling), the per-phase loop (T7 → T9 → consume `dispatch_directives[]` → T10), and the cycle-cap escalation path (counter == 4 → T13 TERMINATED + escalation-cycle-cap.json + user surface). Cite ADR-0017 (4-cycle cap) and ADR-0033 (symmetric D-12) — NOT ADR-0034.
- **Dependencies:** T1.1, T1.2, T1.3
- **Estimate:** L (3 h — load-bearing section; multi-row state machine narrative)
- **Satisfies AC:** AC-FR-3-a, AC-FR-3-c, AC-CC-1, AC-CC-2, AC-NFR-2-a, AC-NFR-2-b, AC-NFR-3-a, AC-NFR-3-b
- **L1 verification:** `grep -n 'Execution Phase Dispatch' .claude/skills/recipe-feature-pipeline/SKILL.md` returns a section header match below the Gate-6 region.
- **L2 verification:** The section enumerates all 14 T0..T13 rows; ADR-0017 + ADR-0033 are cited at least once each; ADR-0034 is NOT cited.
- **L3 verification:** Phase-6 synthetic test feature run produces a state-transitions.log matching the documented dispatch sequence.

#### T2.2: Document the `dispatch_directives[]` indirection (Contract 6) within the new section

- **Layer:** Claude Code
- **Description:** Within the new Execution Phase Dispatch section, document Contract 6 (new in this Blueprint): `execute-finalize-reconciler` emits `dispatch_directives[]` in `quality-reconciliation-log.json`; the parent reads the array and dispatches each named target via Agent at main-conversation level. Document the malformed-or-empty array failure mode (AC-CC-4 / I-DR-005): surface to user, treat as cycle-cap-equivalent escalation, do NOT silently fall back.
- **Dependencies:** T2.1
- **Estimate:** S (45 min)
- **Satisfies AC:** AC-CC-4
- **L1 verification:** `grep -n 'dispatch_directives' .claude/skills/recipe-feature-pipeline/SKILL.md` returns matches inside the new section.
- **L2 verification:** The malformed-array error path is documented in prose with the user-surface rule explicit.
- **L3 verification:** Phase-6 verification, if the synthetic test exercises a NEEDS_RECONCILIATION path, confirms the parent reads `dispatch_directives[]` correctly.

#### T2.3: Document the `invoking_agent` logical-owner invariant within the dispatch section

- **Layer:** Claude Code
- **Description:** In the same section, document that all state-transitions.log entries written by the parent during the execution phase MUST set `invoking_agent: "execute-orchestrator"` per the v1 logical-owner invariant — even though the parent is the literal emitter. This preserves NFR-6-a compatibility with in-flight artifacts and honors the Q-CC-4 disposition.
- **Dependencies:** T2.1
- **Estimate:** XS (15 min)
- **Satisfies AC:** AC-FR-6-a, AC-NFR-2-b, AC-NFR-6-a
- **L1 verification:** `grep -n 'invoking_agent' .claude/skills/recipe-feature-pipeline/SKILL.md` returns a match inside the new section with the value `execute-orchestrator` named.
- **L2 verification:** The logical-owner vs literal-emitter distinction is explicit in prose.
- **L3 verification:** Phase-6 verification confirms every log entry has `invoking_agent: "execute-orchestrator"`.

### Phase 2 Exit Criteria

- `recipe-feature-pipeline/SKILL.md` contains a complete "Execution Phase Dispatch" section located after Gate 6.
- The section documents per-task loop, per-phase loop, dispatch_directives[] indirection, cycle-cap escalation, and the v1 logical-owner invariant.
- No edits to sub-agent files have occurred yet (those are Phase 3).

## Phase 3 — Sub-agent file edits (bundled `Agent`-removal commit + 3-occurrence ADR sweep + prose updates)

### Goal

Apply all sub-agent file edits in a single bundled commit per synthesis Constraint 5.2. The commit covers: (a) `Agent` + `TaskUpdate` removal from `execute-orchestrator.md` frontmatter + body re-framing as advisor; (b) `Agent` removal from `execute-finalize-reconciler.md` frontmatter + body line 76 re-framing + 3-occurrence ADR-0034 → ADR-0033 sweep (lines 3, 19, 82) per I-DR-001; (c) body-prose dispatcher-reference updates on the three leaf specialists.

**Sequencing constraint:** the two `Agent`-removal edits (execute-orchestrator.md + execute-finalize-reconciler.md) MUST ship in one commit; the commit message MUST document "FR-5 sweep closure: affected set = 2".

### Tasks

#### T3.1: Re-scope execute-orchestrator.md to state-machine advisor

- **Layer:** Claude Code
- **Description:** Edit `.claude/agents/execute-orchestrator.md`. Frontmatter line 6: change `tools:` from `[Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` to `[Read, Glob, Grep, Write, Bash(python3:*)]` (remove `Agent` and `TaskUpdate`). Preserve `model: opus`, `effort: high`, `skills:` array (including `recipe-feature-pipeline` self-reference), and `memory: project` per Q-CC-3 + ADR-0022 preservation. Re-frame body sections from "what this agent does" to "what the parent orchestrator MUST execute" — the 14-row state machine becomes canonical reference rather than runtime dispatch instructions. Body lines 91–94 hard-exclusions remain; they now read as advisor-role boundaries.
- **Dependencies:** T2.1 (the dispatch section is the authoritative reference for the advisor's re-framed body)
- **Estimate:** M (90 min)
- **Satisfies AC:** AC-FR-3-a, AC-FR-5-a (partial — first of two files), AC-CC-3
- **L1 verification:** `grep -n '^tools:' .claude/agents/execute-orchestrator.md` shows the new declaration with no `Agent` and no `TaskUpdate`; `grep -c 'Agent' .claude/agents/execute-orchestrator.md` returns the prose-level count, manually inspected to be advisor-narrative references only.
- **L2 verification:** YAML frontmatter parses; body still describes the 14-row state machine.
- **L3 verification:** Bundled commit T3.6 inspects this file plus T3.2's edit; commit message present and well-formed.

#### T3.2: Add explicit body-prose rationale for recipe-feature-pipeline self-reference (AC-CC-3)

- **Layer:** Claude Code
- **Description:** In `.claude/agents/execute-orchestrator.md`, add an explicit prose rationale paragraph (e.g., near the top of the body or in a clearly-marked "Note on skills self-reference" sub-section) reading approximately: "This advisor documents the state machine that the `recipe-feature-pipeline` parent skill orchestrates. The `recipe-feature-pipeline` entry in the `skills:` array is intentional and load-bearing for SA-13 audit traceability — it ties this advisor file to the canonical orchestrator skill that consumes its narrative." This satisfies I-DR-006 absorption for file-resident evidence of intentionality.
- **Dependencies:** T3.1
- **Estimate:** XS (15 min)
- **Satisfies AC:** AC-CC-3
- **L1 verification:** A grep for the phrase "self-reference is intentional" (or close) returns a match in `execute-orchestrator.md`.
- **L2 verification:** The rationale paragraph is in prose and cites `recipe-feature-pipeline` by name.
- **L3 verification:** Future SA-13 audit would find file-resident evidence on first read.

#### T3.3: Re-frame execute-finalize-reconciler.md — Agent removed + body line 76 + 3-occurrence ADR sweep

- **Layer:** Claude Code
- **Description:** Edit `.claude/agents/execute-finalize-reconciler.md` with three sub-edits, all in one diff:
  1. **Frontmatter:** change `tools:` from `[Read, Glob, Grep, Write, Agent]` to `[Read, Glob, Grep, Write]` (remove `Agent`).
  2. **Body line 76:** re-frame "Dispatch via Agent — invoke the target subagent with the revision_context payload." to "Emit `dispatch_directives[]` in `quality-reconciliation-log.json`; the parent orchestrator consumes the array and dispatches each named target via Agent at main-conversation level."
  3. **ADR-0034 → ADR-0033 sweep, all three occurrences (lines 3, 19, 82 per codebase analysis FD-6 + I-DR-001 absorption):** change every ADR-0034 reference to ADR-0033. Preserve `model: opus`, `effort: high`, `skills:` array, `memory: project` (Q-CC-5 preservation).
- **Dependencies:** T2.1, T2.2 (the dispatch section + Contract 6 documentation are the references for the reconciler's new emission contract)
- **Estimate:** M (75 min — three sub-edits in one file)
- **Satisfies AC:** AC-FR-5-a, AC-FR-3-a, AC-FR-3-c, AC-CC-1
- **L1 verification:** `grep -n '^tools:' .claude/agents/execute-finalize-reconciler.md` shows `Agent` removed; `grep -c 'ADR-0034' .claude/agents/execute-finalize-reconciler.md` returns 0; `grep -c 'ADR-0033' .claude/agents/execute-finalize-reconciler.md` returns at least 3.
- **L2 verification:** Body line 76 (or its equivalent after edits) reads the new "Emit `dispatch_directives[]`" phrasing; frontmatter parses cleanly.
- **L3 verification:** Bundled commit T3.6 inspects all three sub-edits in one diff.

#### T3.4: Body-prose dispatcher-reference update on execute-task-code-producer.md

- **Layer:** Claude Code
- **Description:** Edit `.claude/agents/execute-task-code-producer.md`. Replace body-prose occurrences of "dispatched by execute-orchestrator" (or close paraphrases) with "dispatched by the `recipe-feature-pipeline` parent orchestrator (at main-conversation level)." NO frontmatter changes (substantive responsibilities preserved per FR-3-b). NO changes to Contract 1 input/output schemas.
- **Dependencies:** T2.1
- **Estimate:** XS (15 min — prose-only)
- **Satisfies AC:** AC-FR-3-b, AC-FR-4-c
- **L1 verification:** `grep -c 'execute-orchestrator' .claude/agents/execute-task-code-producer.md` returns a value consistent with prose mentions only (no dispatcher-action references); `grep -c 'recipe-feature-pipeline' .claude/agents/execute-task-code-producer.md` returns at least one new match.
- **L2 verification:** Frontmatter unchanged from baseline (diff covers body only).
- **L3 verification:** Specialist's Contract 1 behavior unchanged in Phase-6 verification.

#### T3.5: Body-prose dispatcher-reference update on execute-task-quality-handler.md and execute-phase-quality-reviewer.md

- **Layer:** Claude Code
- **Description:** Same pattern as T3.4, applied to (a) `.claude/agents/execute-task-quality-handler.md` and (b) `.claude/agents/execute-phase-quality-reviewer.md`. Replace dispatcher-prose references; preserve all frontmatter and Contract 2 / Contract 1-verdict semantics.
- **Dependencies:** T2.1
- **Estimate:** XS (15 min — two files, prose-only)
- **Satisfies AC:** AC-FR-3-b, AC-FR-4-c
- **L1 verification:** Per-file grep counts as in T3.4.
- **L2 verification:** Both files' frontmatter unchanged from baseline.
- **L3 verification:** Both specialists' Contract behaviors unchanged in Phase-6 verification.

#### T3.6: Bundle and commit Phase-3 edits with FR-5-sweep-closure commit message

- **Layer:** Claude Code
- **Description:** Commit all Phase-3 edits (T3.1–T3.5) in a single `git commit` operation. Commit message MUST document: "FR-5 sweep closure: affected set = 2 (execute-orchestrator.md, execute-finalize-reconciler.md). Both `Agent` declarations removed; ADR-0044 + ADR-0045 ratified at adrs/. ADR-0034 → ADR-0033 sweep (3 occurrences) on execute-finalize-reconciler.md per I-DR-001 absorption."
- **Dependencies:** T3.1, T3.2, T3.3, T3.4, T3.5
- **Estimate:** XS (10 min — staging + commit)
- **Satisfies AC:** AC-FR-5-a (commit-message portion; bundled-commit constraint)
- **L1 verification:** `git log -1 --pretty=%B` returns the commit message containing the phrase "FR-5 sweep closure: affected set = 2".
- **L2 verification:** `git show --stat HEAD` lists exactly the 5 sub-agent files modified (no extras).
- **L3 verification:** `git log --grep='FR-5 sweep closure: affected set = 2'` returns the commit.

### Phase 3 Exit Criteria

- All five sub-agent files have their Phase-3 edits applied.
- A single bundled commit with the FR-5-sweep-closure message exists.
- `Agent` no longer appears in any sub-agent's `tools:` array (verified across the full FR-5 sweep set; both violations cleaned).
- All three ADR-0034 occurrences in `execute-finalize-reconciler.md` are corrected to ADR-0033.

## Phase 4 — state-transitions-log-entry-template.md extension folding (outside FR-4 inventory; 1 AC-FR-4-a open item)

### Goal

Update the state-transitions-log per-entry template at `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` to (a) clarify the v1 `invoking_agent` invariant as logical owner per Q-CC-4; (b) fold the de facto `void` / `void_reason` and `-prime` suffix extensions into v1 documentation per Blueprint §5 split.

This file is OUTSIDE the PRD FR-4 8-file inventory. Per AC-FR-4-a, this triggers 1 operator-gate open item — already surfaced to the user and ratified by the Blueprint composition (Blueprint Fact-Disposition row addresses it; user accepted the 8+1 surface).

### Tasks

#### T4.1: Clarify the v1 `invoking_agent` invariant as logical owner

- **Layer:** Claude Code
- **Description:** Edit `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` line 63 (per codebase analysis citation). Change the v1 invariant text from approximately "invoking_agent — always execute-orchestrator in v1 (other agents may emit events via the orchestrator)" to: "`invoking_agent` is the LOGICAL OWNER of the transition — always `execute-orchestrator` in v1, even when emitted by the `recipe-feature-pipeline` parent orchestrator on its behalf. This honors the in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` artifact's existing values without retroactive change."
- **Dependencies:** T1.3 (the SKILL.md schema cross-reference target must exist or be visible)
- **Estimate:** S (30 min)
- **Satisfies AC:** AC-FR-6-a, AC-NFR-6-a
- **L1 verification:** `grep -n 'LOGICAL OWNER' .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` returns a match around line 63.
- **L2 verification:** The clarified text explicitly names `recipe-feature-pipeline` as the literal emitter and `execute-orchestrator` as the logical owner.
- **L3 verification:** Phase-6 verification confirms in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` entries remain semantically valid under the clarified invariant.

#### T4.2: Fold `void` / `void_reason` and `-prime` suffix extensions into v1 documentation

- **Layer:** Claude Code
- **Description:** In the same template file, add documentation for two de facto extensions observed in the in-flight log (per codebase analysis FD-8):
  1. **`void` (boolean) + `void_reason` (string)** — appended to a transition entry when a subsequent corrective brief invalidates it.
  2. **Transition-name `-prime` suffix** (e.g., `T0-prime`) — re-entry from TERMINATED back to pending when a prior T13 is voided.
  Document both as v1 schema extensions (NOT v2 — they fold into v1 to preserve in-flight artifact validity).
- **Dependencies:** T4.1
- **Estimate:** S (30 min)
- **Satisfies AC:** AC-FR-4-b, AC-NFR-6-a, AC-NFR-6-b
- **L1 verification:** Greps for `void` (case-sensitive boolean field) and `-prime` return matches in the template file.
- **L2 verification:** Both extensions are described in prose with examples; the in-flight log entries' usage is referenced as the canonical example.
- **L3 verification:** The schema documentation at `recipe-feature-pipeline/SKILL.md` (Phase 1) and this template file are consistent — no contradiction between the two locations.

### Phase 4 Exit Criteria

- The template file's v1 `invoking_agent` invariant text reads as the clarified logical-owner form.
- The template file documents both the `void` / `void_reason` and `-prime` suffix extensions as v1 schema.
- The 1 AC-FR-4-a open item (this file is outside the FR-4 8-file inventory) is closed by virtue of the Blueprint having captured user ratification.

## Phase 5 — FR-5 inventory artifact + ADR-0045 manual-review interim documentation

### Goal

Produce the FR-5 sweep inventory artifact (AC-FR-5-b) and document the manual-review interim discipline that enforces ADR-0045 in the absence of an automated audit extension. The audit-machinery extension is a follow-on feature; this phase documents the interim.

### Tasks

#### T5.1: Author the FR-5 inventory artifact

- **Layer:** Claude Code
- **Description:** Create `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/agent-tool-grant-inventory.md` (or equivalent per AC-FR-5-b). The artifact MUST enumerate: (a) total files swept (36 per codebase analysis FR-5 sweep result); (b) the 2 violations found pre-repair (execute-orchestrator + execute-finalize-reconciler with their then-current `tools:` arrays cited verbatim); (c) the post-repair state confirming both violations cleaned in this run; (d) ADR-0045 as the forward-looking convention cross-reference; (e) a note that the 34 other agents in the sweep declare no `Agent` and are out of scope.
- **Dependencies:** T3.6 (the bundled commit closes the post-repair state)
- **Estimate:** S (45 min)
- **Satisfies AC:** AC-FR-5-b
- **L1 verification:** The file exists at the documented path; frontmatter parses (or it's a frontmatter-free markdown artifact per project convention).
- **L2 verification:** All 5 enumerated elements are present (counts cite codebase analysis; ADR-0045 cross-referenced; both pre-/post-repair states recorded).
- **L3 verification:** A reviewer reading the artifact can independently verify the post-repair state by greppping the codebase for `Agent` in `.claude/agents/*.md` tools arrays.

#### T5.2: Document the ADR-0045 manual-review interim discipline

- **Layer:** Claude Code
- **Description:** Add a section to the inventory artifact (T5.1) OR to a separate `working/feature/<slug>/adr-0045-manual-review-interim.md` documenting the interim manual-review discipline that enforces ADR-0045 until an audit-machinery extension lands. Content MUST include: (a) where in the agent-authoring lifecycle the manual review fires (per-agent design evaluation gap memory cluster: at design-cc / design-composer review steps for any agent-creating feature); (b) who enforces (currently: shared-document-reviewer Gate 1 + review-architecture-auditor on any feature touching `.claude/agents/`); (c) what triggers the review (any PR or feature that adds/modifies a `tools:` array on a sub-agent file); (d) explicit cross-reference to a yet-to-be-created follow-on feature ticket placeholder for the SA-13-style audit extension.
- **Dependencies:** T5.1
- **Estimate:** S (45 min)
- **Satisfies AC:** AC-FR-8-a (interim discipline portion)
- **L1 verification:** The interim documentation exists at the chosen path; the four enumerated elements are present.
- **L2 verification:** Cross-references to ADR-0045 and to the deferred audit-extension follow-on feature are explicit.
- **L3 verification:** A future agent-authoring feature in this project can locate and apply the interim discipline without ambiguity.

### Phase 5 Exit Criteria

- `agent-tool-grant-inventory.md` (or equivalent) exists and documents the FR-5 sweep result (36 files, 2 violations, both cleaned).
- The ADR-0045 manual-review interim discipline is documented with the four elements (where, who, trigger, follow-on pointer).
- A follow-on feature pointer for the audit-machinery extension is recorded.

## Phase 6 — Rollout: synthetic minimal test feature (FR-6) verification under F-7 fresh-session constraint

### Goal

Verify the repaired dispatch mechanism end-to-end by running a synthetic minimal test feature through the new flatten-dispatch loop. Honor the F-7 mid-session-agent-registry constraint by operating under a fresh session for the verification run.

This phase is the rollout / observability phase per the canonical Plan template. There is no end-user rollout for this cc-only feature; rollout means: the repair is exercised by the synthetic test feature; the synthetic test is archived as a regression artifact.

### Tasks

#### T6.1: Design and author the synthetic minimal test feature

- **Layer:** Claude Code
- **Description:** Author a synthetic 1-phase / 1–2-task test feature under `working/test-features/dispatch-mechanism-regression/` (or equivalent per NFR-7). The test feature's shape is plan-author's decision per IC Open Item #5 — recommended shape: 1 phase, 2 tasks (one minimal code task; one minimal phase-quality boundary) so the per-task + per-phase counter increments are exercised. The synthetic feature MUST NOT author any new sub-agent files (this keeps AC-FR-6-d vacuously satisfied: no session restart needed between authoring and execution).
- **Dependencies:** T5.1 (sweep artifact recorded; pre-rollout state stable)
- **Estimate:** M (2 h — synthetic feature design + minimal task spec)
- **Satisfies AC:** AC-FR-6-c (precondition for verification), AC-NFR-7-a (archival artifact creation), AC-FR-7-a (verification log structure)
- **L1 verification:** The synthetic test feature directory exists with the minimum required artifacts (intent, PRD, blueprint, plan, tasks.json) per the recipe-feature-pipeline taxonomy.
- **L2 verification:** A grep across the synthetic feature's artifacts confirms NO new sub-agent file is authored (`find . -path './working/test-features/*' -name '.claude/agents/*.md'` returns empty); the F-7 conditional in AC-FR-6-d is therefore satisfied without a session-restart task.
- **L3 verification:** The synthetic feature's tasks.json is well-formed per `auditing-shared/scripts/validate_pipeline_frontmatter.py`.

#### T6.2: Fresh-session gate — operator restarts session before invoking the synthetic test

- **Layer:** Claude Code
- **Description:** Before invoking the synthetic test feature through the repaired pipeline, the OPERATOR (human-in-the-loop) MUST restart the Claude Code session. This is the explicit F-7 fresh-session constraint operationalization: the agent registry is loaded at session start; the Phase-3 edits to `execute-orchestrator.md` and `execute-finalize-reconciler.md` frontmatters MUST be picked up by a new registry load. The Plan does NOT assume same-session execution of the synthetic test feature post-edits. The task definition for T6.2 is operator-facing instructions in the run handoff: "Restart session before running T6.3."
- **Dependencies:** T6.1
- **Estimate:** XS (operator-facing; ~5 min of operator action; no edit time)
- **Satisfies AC:** AC-FR-6-d (F-7 honor — even though T6.1 made the AC vacuously satisfiable, applying the fresh-session restart is the safe path)
- **L1 verification:** The Plan handoff document for T6.3 contains the explicit instruction "Restart your Claude Code session before invoking the synthetic test feature."
- **L2 verification:** The operator confirms the restart was performed (e.g., a fresh-session timestamp recorded in the verification log).
- **L3 verification:** The synthetic test feature run in T6.3 occurs in a session distinct from the Phase-3 edit session.

#### T6.3: Run the synthetic minimal test feature end-to-end through the repaired dispatch mechanism

- **Layer:** Claude Code
- **Description:** With the fresh session, invoke `/feature-pipeline` against the synthetic test feature. The parent `recipe-feature-pipeline` skill MUST dispatch the four specialists at main-conversation level per the new Execution Phase Dispatch section. Collect: (a) `state-transitions.log` for the synthetic run; (b) `checkpoint.json` showing per-task and per-phase counter increments at T4 and T10 respectively; (c) confirmation that `invoking_agent: "execute-orchestrator"` is preserved as logical-owner across all log entries; (d) cycle-cap halt path test (if the synthetic test design includes a NEEDS_RECONCILIATION trigger).
- **Dependencies:** T6.1, T6.2
- **Estimate:** L (3–4 h — actual pipeline run + verification)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b, AC-FR-6-c, AC-NFR-1-a, AC-NFR-1-b, AC-NFR-2-a, AC-NFR-2-b, AC-NFR-3-a, AC-NFR-3-b
- **L1 verification:** `state-transitions.log` for the synthetic run exists and is non-empty (JSONL).
- **L2 verification:** Each specialist dispatch boundary produces exactly one log entry; per-task counter increments at T4; per-phase counter at T10; T0 and T13 do NOT increment counters per I-AA-609 invariant 10; `invoking_agent` is `"execute-orchestrator"` across all entries.
- **L3 verification:** The synthetic feature completes through T12 (pipeline_complete) with `pipeline-run-summary.json` written; the four load-bearing audit-trail properties documented in source analysis §3.2 are restored.

#### T6.4: Author the verification log + archive the synthetic test feature as a regression artifact

- **Layer:** Claude Code
- **Description:** Produce `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/verification-log.md` recording: (a) FR-6 synthetic test PASS/FAIL with evidence (log paths + checkpoint paths); (b) optionally, FR-7 real-feature re-run result (non-gating per PRD); (c) explicit marker that FR-6 is gating and FR-7 (if performed) is the confidence check. Archive the synthetic test feature under `working/test-features/<test-slug>/` per NFR-7-a so future dispatch-mechanism changes can re-run it.
- **Dependencies:** T6.3
- **Estimate:** S (60 min)
- **Satisfies AC:** AC-FR-7-a, AC-NFR-7-a
- **L1 verification:** Both `verification-log.md` and the archived synthetic test feature directory exist at the documented paths.
- **L2 verification:** The verification log names FR-6 as gating and (if present) FR-7 as the confidence check.
- **L3 verification:** A future operator can re-run the archived synthetic test feature against any future dispatch-mechanism change without re-authoring it.

#### T6.5: Verification-failure escalation (conditional task)

- **Layer:** Claude Code
- **Description:** If T6.3 fails (any of the AC-FR-6-a/b/c criteria do not hold), surface a `verification-failed` posture per AC-FR-6-c. Do NOT declare the feature complete. Re-engage the per-layer cc Design / Blueprint reconciliation loop via the standard pipeline cycle path. This task is conditional and runs only on T6.3 failure.
- **Dependencies:** T6.3 (only triggered on failure)
- **Estimate:** Conditional (M – L depending on failure mode)
- **Satisfies AC:** AC-FR-6-c (negative path), AC-NFR-1-b
- **L1 verification:** On failure, a `verification-failed.md` posture artifact exists in the working directory; `checkpoint.json` records the failure mode.
- **L2 verification:** The escalation routes through the standard reconciliation pipeline (no silent workaround fallback per AC-NFR-1-b).
- **L3 verification:** Re-engagement produces a Blueprint or ADR amendment addressing the failure root cause.

### Phase 6 Exit Criteria

- A fresh session was used for T6.3 (operator-confirmed).
- The synthetic test feature ran end-to-end with all AC-FR-6-a/b/c criteria satisfied.
- The verification log records FR-6 PASS (and optionally FR-7 result).
- The synthetic test feature is archived as a regression artifact.

## Task Inventory

Flat enumeration of all 24 tasks per phase. Each row: Task ID · Phase · One-line summary · Predecessors (task-dependency edges) · Size.

| Task ID | Phase | Summary | Predecessors | Size |
|---|---|---|---|---|
| T0.1 | Phase 0 | Verify ADR-0044 + ADR-0045 placement at canonical root `adrs/` | — | XS |
| T0.2 | Phase 0 | Document the expected Stage-13 packager BLOCKER + waiver path | T0.1 | S |
| T0.3 | Phase 0 | Snapshot affected-files baseline for rollback | T0.1 | XS |
| T1.1 | Phase 1 | Add `execution_pipeline_state_transitions` field to canonical schema reference | T0.3 | S |
| T1.2 | Phase 1 | Add `execution_mode` and `execution_pipeline_cycle_counters` fields | T1.1 | S |
| T1.3 | Phase 1 | Author state-transitions-log per-entry schema sub-section in SKILL.md (or cross-reference it) | T1.2 | M |
| T2.1 | Phase 2 | Add "Execution Phase Dispatch" section after Step 14 / Gate 6 | T1.3 | L |
| T2.2 | Phase 2 | Document the `dispatch_directives[]` indirection (Contract 6) within the new section | T2.1 | M |
| T2.3 | Phase 2 | Document the `invoking_agent` logical-owner invariant within the dispatch section | T2.2 | S |
| T3.1 | Phase 3 | Re-scope `execute-orchestrator.md` to state-machine advisor (Agent + TaskUpdate removed from `tools:`) | T2.3 | M |
| T3.2 | Phase 3 | Add explicit body-prose rationale for `recipe-feature-pipeline` self-reference (AC-CC-3) | T3.1 | XS |
| T3.3 | Phase 3 | Re-frame `execute-finalize-reconciler.md` — `Agent` removed + body line 76 + 3-occurrence ADR sweep (lines 3, 19, 82) | T2.3 | M |
| T3.4 | Phase 3 | Body-prose dispatcher-reference update on `execute-task-code-producer.md` | T2.3 | XS |
| T3.5 | Phase 3 | Body-prose dispatcher-reference update on `execute-task-quality-handler.md` and `execute-phase-quality-reviewer.md` | T2.3 | XS |
| T3.6 | Phase 3 | Bundle and commit Phase-3 edits with `"FR-5 sweep closure: affected set = 2"` message | T3.1, T3.2, T3.3, T3.4, T3.5 | S |
| T4.1 | Phase 4 | Clarify the v1 `invoking_agent` invariant as logical owner | T1.3 | S |
| T4.2 | Phase 4 | Fold `void` / `void_reason` and `-prime` suffix extensions into v1 documentation | T4.1 | S |
| T5.1 | Phase 5 | Author the FR-5 inventory artifact | T3.6 | S |
| T5.2 | Phase 5 | Document the ADR-0045 manual-review interim discipline | T5.1 | S |
| T6.1 | Phase 6 | Design and author the synthetic minimal test feature | T5.1, T4.2 | M |
| T6.2 | Phase 6 | Fresh-session gate — operator restarts session before invoking the synthetic test | T6.1 | XS (operator) |
| T6.3 | Phase 6 | Run the synthetic minimal test feature end-to-end through the repaired dispatch mechanism | T6.2 | L |
| T6.4 | Phase 6 | Author the verification log + archive the synthetic test feature as a regression artifact | T6.3 | S |
| T6.5 | Phase 6 | **Conditional** — verification-failure escalation; fires only on T6.3 FAIL | T6.3 (FAIL branch) | M |

Total: 24 tasks across 7 phases. T6.5 is conditional (not unconditionally part of the critical path).

## Cross-Phase Dependencies

```
Phase 0:  T0.1 ──┬──► T0.2
                 └──► T0.3
                         │
Phase 1:                 └──► T1.1 ──► T1.2 ──► T1.3
                                                  │
                                                  ├──► (Phase 2)
                                                  └──► T4.1 (Phase 4 fork)
                                                  │
Phase 2:                                          └──► T2.1 ──► T2.2 ──► T2.3
                                                                            │
Phase 3:                                                                    └──► T3.1 ──► T3.2
                                                                            │
                                                                            ├──► T3.3
                                                                            ├──► T3.4
                                                                            └──► T3.5
                                                                                          │
                                                                            (all converge) ▼
                                                                                        T3.6
                                                                                          │
Phase 5:                                                                                  └──► T5.1 ──► T5.2
                                                                                                          │
Phase 4:  (parallel to Phase 2/3)  T4.1 ──► T4.2  ──────────────────────────────────────────────────────┤
                                                                                                          │
Phase 6:                                                                          T6.1 ──► T6.2 ──► T6.3 ──► T6.4
                                                                                  ▲                       │
                                                                                  │              (T6.5 only on T6.3 FAIL)
                                  T5.1 + T4.2 ───────────────────────────────────┘
```

**Reading the graph:** T2.1 appears once (under Phase 2). Phase 3 fan-out (T3.1 / T3.3 / T3.4 / T3.5) converges at T3.6 (the bundled-commit task). Phase 4 (T4.1 → T4.2) forks off Phase 1 and runs in parallel with Phase 2 + Phase 3. Phase 6 starts only after both Phase 5 (T5.1) and Phase 4 (T4.2) complete.

Key edges:

- **T1.1 → T2.1 (load-bearing edit ordering on SKILL.md):** D-004 schema closure precedes D-001 dispatch-section absorption per Blueprint Implementation Plan §1 → §2 and I-DR-004 absorption.
- **T3.1 + T3.3 → T3.6 (bundled `Agent`-removal commit):** the two `Agent`-removals MUST ship in one commit per synthesis Constraint 5.2; T3.6 stages both files together.
- **T6.1 → T6.2 → T6.3 (F-7 fresh-session gate):** the operator MUST restart the session between Phase-3 sub-agent edits and the synthetic test feature run, per AC-FR-6-d and the F-7 substrate observation.

## Cross-Phase Sequencing Constraints

These constraints are surfaced as task-dependency edges above and re-stated here for explicit downstream-stage consumption (task-decomposer, test-acceptance-author, phase-validator-author):

1. **D-004 schema closure BEFORE D-001 dispatch section:** Phase 1 (T1.1–T1.3) MUST complete before Phase 2 (T2.1–T2.3) begins. The dispatch section references the schema fields documented in Phase 1; inverting the order creates schema-references-not-yet-stable risk. (Blueprint Risks row 1.)

2. **Bundled `Agent`-removal commit:** T3.1 (execute-orchestrator.md frontmatter) and T3.3 (execute-finalize-reconciler.md frontmatter) MUST land in a single `git commit` (T3.6) with the commit message documenting "FR-5 sweep closure: affected set = 2". This is non-negotiable per synthesis Constraint 5.2.

3. **F-7 fresh-session gate:** T6.2 is an explicit operator-facing task between the Phase-3 sub-agent edits and the T6.3 synthetic test feature run. Even though T6.1's task design (no new sub-agent files) makes AC-FR-6-d vacuously satisfiable, applying the fresh-session restart is the safe path and is sequenced as a load-bearing task dependency in this Plan.

4. **3-occurrence ADR sweep within T3.3:** all three ADR-0034 occurrences in `execute-finalize-reconciler.md` (lines 3, 19, 82 per codebase analysis FD-6 + I-DR-001 absorption) MUST be corrected in the same edit as the `Agent`-removal and the body line 76 re-framing. The downstream verification (AC-FR-5-a) checks all three corrections.

## L1/L2/L3 Verification Discipline

Every task above carries L1/L2/L3 criteria. The discipline:

- **L1 (cheapest):** Seconds-to-minutes. File-existence, grep, YAML parse, single-line diff inspection.
- **L2 (functional):** Minutes. Structural correctness of edit (section header present, frontmatter parses, prose coherence).
- **L3 (integration):** Tens of minutes to hours. End-to-end behavior under the synthetic test feature run; cross-file consistency; future-reader-applicability.

The Phase Validator for each phase aggregates L3 verifications across the phase's tasks. Phase 6's L3 is the load-bearing one: the synthetic test feature dispatch loop completion under the F-7 fresh-session.

## Acceptance Test Cross-Reference

| AC ID (from Blueprint) | Satisfied by task(s) |
|---|---|
| AC-FR-1-a | `satisfied-upstream` — investigation (FR-1) completed in Stage-4 Discovery Research; T-001 research note at `working/feature/<slug>/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md` is the load-bearing artifact. No new task required in this Plan. |
| AC-FR-1-b | `satisfied-upstream` — KB-gap-justified topic produced finding-with-evidence per Research Plan T-001 acceptance criteria. |
| AC-FR-1-c | `satisfied-upstream` — `dispatch_supported: false` flag emitted in T-001 note; consumed by synthesis (D-001 / D-002 frames) and Blueprint (option (a) selection rationale). |
| AC-FR-2-a | `vacuous-by-kc2` — kill-criterion-#1 path (dispatch IS supported) did NOT fire; the run committed to kill-criterion-#2 (FULL repair) per T-001 evidence. AC verified vacuously by the absence of a `kill-criterion-1-triggered` posture in checkpoint.json. |
| AC-FR-2-b | `vacuous-by-kc2` — no follow-on small-feature stub was opened because kc#1 did not trigger. AC verified vacuously. |
| AC-FR-2-c | `vacuous-by-kc2` — pause-and-rescope path was not exercised. AC verified vacuously; rationale recorded in checkpoint.json `kill_criterion_triggered: 2`. |
| AC-FR-3-a | T2.1, T3.1, T3.3 (option (a) named + rationale carried) |
| AC-FR-3-b | T3.4, T3.5 (specialist substantive responsibilities preserved) |
| AC-FR-3-c | T2.1, T3.3 (ADR-0017 + ADR-0033 invariants preserved; D-12 symmetric) |
| AC-FR-4-a | T0.2 (waiver path documented for known Stage-13 packager BLOCKER); T4.1, T4.2 (the 1 outside-inventory file is sequenced explicitly) |
| AC-FR-4-b | T1.1, T1.2, T1.3, T4.2 (schema lockstep) |
| AC-FR-4-c | T3.4, T3.5 (substantive responsibilities preserved at implementation layer) |
| AC-FR-5-a | T3.1, T3.3, T3.6 (Agent removed from both; 3-occurrence sweep; commit message) |
| AC-FR-5-b | T5.1 (inventory artifact) |
| AC-FR-6-a | T2.3, T6.3 (invoking_agent logical-owner invariant; per-specialist-boundary entries) |
| AC-FR-6-b | T6.3 (counter increments at T4 / T10 observed in checkpoint.json) |
| AC-FR-6-c | T6.3, T6.5 (verification-failed posture path) |
| AC-FR-6-d | T6.1, T6.2 (F-7 fresh-session constraint; vacuously-satisfiable via no-new-subagents design + explicit restart) |
| AC-FR-7-a | T6.1, T6.4 (verification log structure naming gating vs confidence-check) |
| AC-FR-8-a | T0.1 (ADR-0045 placement verified); T5.2 (manual-review interim discipline documented) |
| AC-NFR-1-a | T6.3 (synthetic test completes through all task and phase boundaries) |
| AC-NFR-1-b | T6.5 (no silent fallback on failure) |
| AC-NFR-2-a | T6.3 (one log entry per specialist boundary) |
| AC-NFR-2-b | T2.3, T6.3 (invoking_agent identity preserved in log) |
| AC-NFR-3-a | T6.3 (counter increments at task and phase boundaries) |
| AC-NFR-3-b | T2.1, T6.3 (cycle-cap halt path routed through reconciler equivalent) |
| AC-NFR-4-a | (already satisfied upstream by T-001 research note at `working/feature/<slug>/research-notes/T-001-…md`; no new task required in this Plan) |
| AC-NFR-5-a | T1.1, T1.2, T1.3 (canonical schema reference updated in lockstep) |
| AC-NFR-6-a | T4.1 (logical-owner clarification preserves in-flight artifact validity) |
| AC-NFR-6-b | T1.2, T4.2 (`execution_mode` and v1 extensions documented for downstream-consumer compatibility) |
| AC-NFR-7-a | T6.4 (synthetic test archived as regression artifact) |
| AC-CC-1 | T2.1, T3.3 (ADR-0017 + ADR-0033 cited; NOT ADR-0034) |
| AC-CC-2 | T1.1, T1.2, T2.1 (lockstep on SKILL.md) |
| AC-CC-3 | T3.2 (body-prose rationale for self-reference) |
| AC-CC-4 | T2.2 (malformed dispatch_directives[] surface-to-user; no silent fallback) |

Every AC in the Blueprint is mapped to at least one task. No orphan ACs.

Tasks that satisfy NO AC and are setup-only (Phase 0): T0.1, T0.2, T0.3 — tagged setup-only per the canonical Plan template discipline.

## Estimation Methodology

T-shirt sizes XS / S / M / L based on edit complexity and verification scope. XS ≈ 5–15 min; S ≈ 30–60 min; M ≈ 75 min – 2 h; L ≈ 3–4 h. No precise hour estimates; the synthetic test feature run (T6.3) carries the widest estimate variance because it depends on the operator's available session time and whether T6.5 is triggered.

Total task-time estimate (sum of mid-range): ~16–20 hours of focused operator + agent work, excluding the cycle-time of the Phase-6 synthetic test feature run itself (which is a pipeline-internal run with its own multi-hour cycle).

## Resourcing Posture

Single pipeline operator (Josh-S-N2M per project context). All tasks executable in a single-operator workflow with no cross-team coordination. Phase 6 explicitly requires a session restart by the operator (T6.2 is operator-facing, not agent-facing).

## Verification Strategy

The primary verification surface is Phase 6's synthetic test feature run (FR-6 gating). The verification is end-to-end functional: the parent `recipe-feature-pipeline` skill dispatches the four specialists at main-conversation level; one `state-transitions.log` entry is emitted per specialist boundary; per-task and per-phase cycle counters increment at T4 and T10 respectively; the synthetic feature completes through T12; the four audit-trail properties documented in source analysis §3.2 are restored.

Mechanism: the operator restarts session (T6.2), invokes `/feature-pipeline` against the synthetic test feature directory (T6.3), and inspects the resulting log + checkpoint against the AC-FR-6-a/b/c criteria. The verification log (T6.4) records the result.

Negative-path verification (T6.5) is conditional: only triggered on T6.3 failure. The negative path verifies that `verification-failed` posture is surfaced explicitly per AC-FR-6-c and AC-NFR-1-b (no silent fallback to the parent-driven workaround).

## Rollback Procedure

Per ADR-0029 (no silent scope changes) and ADR-0044 §Implementation Guidance, the repair MUST be reversible.

Per-phase rollback paths:

- **Phase 0:** No code edits; no rollback needed.
- **Phase 1:** `git revert <T1.x-commit>` cleanly restores `recipe-feature-pipeline/SKILL.md` to pre-T1 state. The schema reference reverts to its pre-execution-phase-fields form.
- **Phase 2:** `git revert <T2.x-commit>` removes the Execution Phase Dispatch section. The schema fields documented in Phase 1 remain (orphaned but not breaking).
- **Phase 3 (the bundled `Agent`-removal commit T3.6):** `git revert <T3.6-commit-sha>` restores all 5 sub-agent files to their pre-Phase-3 state in one revert. This is the most consequential rollback boundary because all sub-agent edits land atomically.
- **Phase 4:** `git revert <T4.x-commit>` restores `state-transitions-log-entry-template.md` to its pre-T4 state. NFR-6-a unaffected (in-flight artifacts remain valid under either invariant interpretation).
- **Phase 5:** Artifact-only rollback: delete the `agent-tool-grant-inventory.md` and any ADR-0045 manual-review interim documentation.
- **Phase 6:** Synthetic test feature archive removal (T6.4) + verification-log retraction. The archived test feature is reusable; rollback of Phase 6 doesn't reverse Phases 0–5.

Full rollback to T0.3 baseline SHA: `git reset --hard <baseline-sha>` (recorded in `rollback-baseline.txt`). This is the nuclear option.

A future harness change that enables sub-agent → sub-agent dispatch (kill-criterion-#1 in retrospect) would trigger a forward-rollback path documented in ADR-0044 §Implementation Guidance: restore `Agent` + `TaskUpdate` to `execute-orchestrator.md` frontmatter; restore `Agent` to `execute-finalize-reconciler.md` frontmatter; re-frame the advisor file back to dispatcher narrative; remove the Execution Phase Dispatch section from `recipe-feature-pipeline/SKILL.md` (or mark it as legacy compatibility). The advisor file's preserved `opus/high` triplet keeps this reversal cheap.

## Risks + Mitigations

Surfaced as a per-phase view of the Blueprint's Risks table; downstream stages (test-acceptance-author, test-phase-validator-author, finalize-reconciler at execution) MUST respect these:

| Phase | Risk | Mitigation |
|---|---|---|
| Phase 0 | Stage-13 packager BLOCKER (known issue inherited from ADR-0036 partial-amendment defect) blocks deliverable packaging | T0.2 documents the waiver path; operator applies waiver citing Blueprint's ADR-0036 placement disposition |
| Phase 1 | Plan-author or executor inverts D-004 → D-001 ordering | Phase 1 → Phase 2 sequencing is explicit; T2.1 dependency on T1.1+T1.2+T1.3 is a hard edge |
| Phase 3 | Missed ADR-0034 occurrence (only 2 of 3 corrected) | T3.3 explicitly enumerates lines 3, 19, 82; L1 verification greps for ADR-0034 count == 0 |
| Phase 3 | Bundled-commit constraint violated (separate commits) | T3.6 explicitly stages all 5 files; commit message contains the required phrase |
| Phase 4 | This file is outside FR-4 inventory (1 AC-FR-4-a open item) — risk of out-of-scope expansion | Blueprint composition captured user ratification; no expansion beyond the single file |
| Phase 6 | F-7 mid-session-agent-registry constraint missed | T6.2 is an explicit operator-facing task; T6.1 designs the synthetic test to NOT author new sub-agents (vacuously satisfies AC-FR-6-d) AND T6.2 still applies the restart as defensive |
| Phase 6 | Synthetic test verification fails on the repaired mechanism | T6.5 conditional task escalates per AC-FR-6-c; no silent fallback per AC-NFR-1-b |
| Cross-phase | Audit-extension for ADR-0045 never lands in a follow-on feature | T5.2 documents the manual-review interim; ADR-0045 names the deferred follow-on; this Plan does not gate on the audit-extension |
| Cross-phase | A reviewer flags an additional ADR-0034 mis-credit elsewhere in the codebase | Architecture-auditor CoVe sweep; if found, surface as a follow-on edit during reconciliation (not in scope of this Plan) |

## Open Items (Pending Cross-Artifact Audit)

These items are surfaced by plan-author for the review-cross-artifact-auditor at the next stage:

1. **Stage-13 packager BLOCKER (known issue).** The packager check has not been amended to align with ADR-0036 canonical-root-only placement; this Plan documents the waiver path at T0.2 but does NOT fix the packager. Surface to cross-artifact auditor for confirmation that the waiver path satisfies the deliverable-archive spec.
2. **Follow-on feature pointer for ADR-0045 audit-machinery extension.** T5.2 records a placeholder pointer; the actual follow-on feature slug is not yet created. Surface to cross-artifact auditor: is a placeholder pointer sufficient, or should a concrete follow-on slug exist before this run closes?
3. **Synthetic test feature shape (NEEDS_RECONCILIATION inclusion).** Per Blueprint Verification Strategy, the cycle-cap halt path tests only IF the synthetic feature design includes a NEEDS_RECONCILIATION trigger. T6.1's recommended shape (1 phase, 2 tasks, minimal code work) does NOT necessarily include such a trigger. Surface to cross-artifact auditor: should the synthetic test feature be designed to exercise the NEEDS_RECONCILIATION → `dispatch_directives[]` path as well, or is per-task verification sufficient?
4. **`current_stage` value in checkpoint.json under execution phase.** Blueprint Design Summary (Meta) lists this as an unknown: whether `current_stage` gains a single `"execution"` value or splits into per-substantive-state values. The synthesis substrate prefers single. T2.1 documents the new section but does not finalize the `current_stage` enumeration. Surface to cross-artifact auditor for finalization before T2.1 implementation begins.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-24 | plan-author | Initial Plan derived from blueprint-v1.md v1.1.0 (option (a) flatten dispatch hierarchy). Sequenced under three load-bearing constraints: D-004 → D-001 edit ordering; bundled `Agent`-removal commit (T3.6); F-7 fresh-session gate (T6.2). 7 phases, 24 tasks (incl. 1 conditional). |
| 1.1.0 | 2026-05-24 | parent-orchestrator-surgical-patch | Absorbed plan-v1 review findings I-Plan-001 (added flat Task Inventory section), I-Plan-002 (added 6 missing AC mapping rows: AC-FR-1-a/b/c satisfied-upstream + AC-FR-2-a/b/c vacuous-by-kc2), I-Plan-004 (clarified Cross-Phase Dependencies graph; removed T2.1 duplication; explicit Phase-4 fork). |
| 1.1.1 | 2026-05-24 | parent-orchestrator-surgical-patch | Absorbed cross-artifact-audit finding I-CA-002 (corrected "30 ACs" claim — actual mapping covers 35 ACs including AC-FR-1-a/b/c satisfied-upstream + AC-FR-2-a/b/c vacuous-by-kc2 + the 6 implicit AC-CC-N from Blueprint). |
