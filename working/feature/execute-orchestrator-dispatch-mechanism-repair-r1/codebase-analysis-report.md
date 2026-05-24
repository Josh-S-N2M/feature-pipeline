---
id: codebase-analysis-report-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: codebase-analysis-report
schema_version: 1.1.0
status: draft
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
run_id: execute-orchestrator-dispatch-mechanism-repair-r1-20260523-202235
extraction_method: manual-grep-and-read
generated: 2026-05-23T20:35:00Z
generated_by: discovery-codebase-researcher
companion_artifact: working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json
---

# Codebase Analysis Report — execute-orchestrator Dispatch Mechanism Repair (r1)

## Contents

- [x] Executive summary
- [x] Extraction method + provenance
- [x] Touchpoint-by-touchpoint findings (8 items per Research Plan)
- [x] PRD FR-5 inventory sweep
- [x] Inherited ADR confirmations + newly-surfaced ADRs
- [x] Blast-radius preview per §6 option
- [x] Conventions observed (cc layer)
- [x] Schemas extracted
- [x] Open items for design-composer
- [x] Risks observed

## Executive Summary

The codebase-side research for `execute-orchestrator-dispatch-mechanism-repair-r1` confirms the source analysis (`Issues/analysis-execute-orchestrator-dispatch-limitation.md`) at every load-bearing claim and surfaces additional findings the per-layer cc Designer will need:

1. **Two affected dispatchers, not one.** The FR-5 sweep over all 36 `.claude/agents/*.md` files identifies **two** agents declaring `Agent` in `tools:`: `execute-orchestrator` (line 6) and `execute-finalize-reconciler` (line 6). Source analysis directly observed the defect only in execute-orchestrator; the parallel defect in execute-finalize-reconciler is inferred with high confidence (same harness, same Agent-tool-grant pattern, same sub-agent role). The PRD's affected-files inventory (FR-4) already includes both files, so this is confirmation rather than scope expansion.

2. **The parent recipe-feature-pipeline/SKILL.md does NOT document the execution phase.** The skill's 13-stage taxonomy ends at Gate 6 (line 299). The execute-* agents are mentioned in NO part of the skill — only in `KB-documentation-criteria/SKILL.md:67-71` (template assignments) and in the agent files themselves. §6 option (b) "retire execute-orchestrator and fold its state-machine into recipe-feature-pipeline" REQUIRES adding an entire 14th stage (or its equivalent) to the parent skill. This is a larger scope-of-edits than the PRD's 8-file inventory anticipates.

3. **§6 option (b) escapes the PRD's 8-file inventory.** At least **5 files outside the inventory** require coordinated edits under option (b): KB-documentation-criteria/SKILL.md template-assignment table, state-transitions-log-entry-template.md `invoking_agent` v1 invariant, pipeline-run-summary-template.md `Authored by execute-orchestrator` reference, smoke_test_auditing_shared.py test data, and auditing-codespaces/SKILL.md consumer note. Per AC-FR-4-a this triggers an open-item user check. Options (a) and (c) require only 1 file each outside the inventory.

4. **Documentary mis-attribution: ADR-0034 ≠ symmetric D-12.** The Research Plan §38 and the orchestrator dispatch prompt §6 attribute "ADR-0034 symmetric D-12 application" as a load-bearing inherited ADR. **The canonical home for symmetric D-12 application is ADR-0033 line 71**, not ADR-0034 (which covers an unrelated PRD v1.1.0 mis-credit cleanup). This is itself the kind of mis-attribution ADR-0034 was authored to prevent. The PRD's FR-3-c invariant set should cite ADR-0017 + ADR-0033, not ADR-0034.

5. **Canonical schema reference for checkpoint.json is incomplete.** `recipe-feature-pipeline/SKILL.md:96-128` documents only planning-side fields. The de facto execution-phase fields observed in the in-flight `devcontainer-mcp-provisioning-r1/checkpoint.json` (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`) are NOT documented anywhere. Per NFR-5-a, any §6 option touching the schema must close this gap in lockstep.

The JSON companion (`codebase-analysis.json`) carries the full evidence base and citations; this report summarizes for design-composer consumption.

## Extraction Method + Provenance

- **Method:** `manual-grep-and-read` (Read + Bash grep + Glob).
- **GitNexus availability:** GitNexus MCP is configured in `.mcp.json` but the `$GITNEXUS_TAG` environment variable is unset, so no `mcp__gitnexus__*` tools were exposed to this researcher session. Same fallback as `devcontainer-mcp-provisioning-r1` (whose `checkpoint.json:67` records `extraction_method: manual-grep-and-read`).
- **codebase-memory-mcp availability:** not registered in `.mcp.json`.
- Per `recipe-feature-pipeline/SKILL.md:44` hard exclusion #4 ("No silent fallback from GitNexus to codebase-memory-mcp"), the fallback is recorded explicitly.

## Touchpoint-by-touchpoint Findings

### 1. execute-orchestrator.md + 4 specialists

**execute-orchestrator** (`.claude/agents/execute-orchestrator.md`, 121 lines, dispatcher):

- Frontmatter line 6: `tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` — 7 tools declared.
- Runtime tool surface observed (per source analysis §1.2): `[Read, Write, Bash, Edit]` — 4 tools, with `Agent`/`Glob`/`Grep`/`TaskUpdate` MISSING, `Edit` ADDED despite not being declared, and `Bash(python3:*)` scope STRIPPED.
- `model: opus`, `effort: high`, `skills: [KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]`, `memory: project`.
- Body lines 24-43 document the 14-row state machine (T0..T13 + 12 substantive states + 2 boundary states INIT/TERMINATED).
- Per-task loop (lines 56-71) and per-phase loop (lines 73-82) describe exactly the dispatches that require `Agent`.
- Hard exclusions (lines 91-94): "You do NOT author code. You do NOT issue quality verdicts. You do NOT classify findings." → without `Agent`, the agent can do nothing.
- Body line 7 declares `skills: [..., recipe-feature-pipeline, ...]` — a sub-agent declaring its own parent orchestrator skill in its skills array (open question OQ-CR-003 for design-composer).

**execute-task-code-producer** (`.claude/agents/execute-task-code-producer.md`, 110 lines, leaf):

- Frontmatter line 6: `tools: [Read, Glob, Grep, Write, Edit, Bash]` — 6 tools; NO Agent (correct for a leaf).
- `model: sonnet`, `effort: medium`, `skills: [ai-development-guide, KB-cc-design]`. **No `memory:` field.**
- Input contract (lines 20-37): task spec from tasks.json with `{id, description, type, target_files, satisfies_ac, tests, per_task_skills, revision_context}`.
- Output contract (lines 42-57): per-task-execution-result.{json,md} pair, status enum `COMPLETED|INCOMPLETE|BLOCKED`.
- Applies ai-development-guide 4-phase pattern (Format/Lint → Build → Test → Final Gate) (lines 60-66).

**execute-task-quality-handler** (`.claude/agents/execute-task-quality-handler.md`, 104 lines, leaf):

- Frontmatter line 6: `tools: [Read, Glob, Grep, Bash]` — 4 tools; NO Agent.
- `model: sonnet`, `effort: medium`, `skills: [ai-development-guide, KB-cc-design, auditing-shared]`. No `memory:`.
- Verdict enum line 33: `APPROVED | NEEDS_REVISION | STUB_DETECTED | BLOCKER` per D-2c/d.
- D-2d STUB_DETECTED runs FIRST (line 54) to prevent silent-success failure mode.
- `Bash` is unrestricted (line 73) to accommodate multi-language test commands per FR-2 + D-11.

**execute-phase-quality-reviewer** (`.claude/agents/execute-phase-quality-reviewer.md`, 97 lines, leaf):

- Frontmatter line 6: `tools: [Read, Glob, Grep, Bash(python3:*), Write]` — 5 tools; NO Agent.
- `model: opus`, `effort: high`, `skills: [KB-cc-design, KB-review-disciplines, auditing-shared]`. No `memory:`.
- Output: phase-quality-report.{json,md} per Contract 2 with 5-dimensional verdict `{tests, audits, validator, discipline, scope_deviations}` (lines 32-48).
- Per D-13 reframing (line 85), does NOT collapse dimensions into a single number.
- Honors Q-CC-4 stub-vs-real distinction (line 69) per ADR-0033.

**execute-finalize-reconciler** (`.claude/agents/execute-finalize-reconciler.md`, 110 lines, **dispatcher #2**):

- Frontmatter line 6: `tools: [Read, Glob, Grep, Write, Agent]` — 5 tools, **Agent INCLUDED**.
- `model: opus`, `effort: high`, `skills: [KB-cc-design, KB-review-disciplines, auditing-shared]`, `memory: project`.
- Body line 76: "Dispatch via Agent — invoke the target subagent with the revision_context payload." → same defect would manifest at T9 dispatch.
- Contract 4 8-row dispatch matrix (lines 57-69): tests / audits-cc / audits-gha / audits-codespaces / validator / discipline / stub / scope_deviations.
- Cycle counter shared with execute-orchestrator via `memory: project` (line 76, 88).
- Body line 110 explicitly references ADR-0035 for the auditing-shared skill binding (newly-surfaced ADR — see §"Newly Surfaced ADRs" below).

### 2. recipe-feature-pipeline/SKILL.md

`.claude/skills/recipe-feature-pipeline/SKILL.md` (414 lines):

- The skill is the user-invocable `/feature-pipeline` orchestrator.
- **Critical finding:** the skill has ZERO references to `execute-orchestrator` or any execute-* specialist (verified by grep). The 13-stage taxonomy stops at Gate 6 (Step 14 / line 299).
- The "Activated Sub-Agents Inventory" (lines 354-373) lists 27 pipeline sub-agents, EXCLUDING the 5 execute-* agents. The skill's stated agent count is 27 + 1 shared-document-reviewer; the actual `.claude/agents/` directory contains 36 files (5 of which are the execute-* family).
- Hard exclusion #4 (line 44): "No silent fallback from GitNexus to codebase-memory-mcp." Relevant to this researcher's extraction_method discipline.
- Working-directory precondition (lines 47-53): cwd MUST equal repo root, per ADR-0027.
- Checkpoint.json canonical schema reference (lines 96-128): documents planning-side fields ONLY. Execution-phase fields are NOT documented here.
- The execution phase is invoked OUTSIDE this skill's documented surface (post-Gate-6). The dispatch mechanism is the workaround in source analysis §5 (parent-driven dispatch); there is no documented design for the post-Gate-6 mechanism.

**What changes under each §6 option?**

- **Option (a) flatten:** the skill gains a 14th post-Gate-6 step where the parent dispatches the 4 specialists directly. The 13-stage taxonomy may or may not be re-numbered (per the skill's hard exclusion #5, pipeline stages are named not numbered, so renumbering is not a concern).
- **Option (b) retire execute-orchestrator:** the entire state machine (14-row table + per-task + per-phase loops + cycle-cap discipline) folds into this skill. Largest scope-of-change. Requires updating the skill's "Activated Sub-Agents Inventory" to drop execute-orchestrator and clarify which agents the parent skill dispatches in the execution phase.
- **Option (c) Bash-script dispatch:** the skill is largely unchanged; a new script is introduced and the post-Gate-6 invocation calls into it.

### 3. Sweep of ALL `.claude/agents/*.md` for `Agent` in tools (PRD FR-5)

Sweep target: `.claude/agents/*.md`. Total files: **36** (Research Plan claimed 35 — minor discrepancy noted as OI-CR-F).

| Agent | Path | Exact tools array (line 6) | Dispatch in current codebase? | Same defect if attempted? |
|---|---|---|---|---|
| `execute-orchestrator` | `.claude/agents/execute-orchestrator.md` | `[Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` | **NO** — Agent stripped at runtime per source analysis §1.2 | **YES** (directly observed) |
| `execute-finalize-reconciler` | `.claude/agents/execute-finalize-reconciler.md` | `[Read, Glob, Grep, Write, Agent]` | **NO** — never reached at T9 in devcontainer-mcp-provisioning-r1 (workaround halted before phase-reconciliation) | **YES** (inferred with high confidence; structurally identical) |

**No other agent** in the 36-file sweep declares `Agent` in its `tools:` array. The FR-5 inventory is exhaustive at 2 entries.

Several agents declare `TaskCreate` and/or `TaskUpdate` (27 of 36). These are task-tracking primitives, semantically distinct from `Agent` (the dispatch tool); NOT flagged as affected. Out of FR-5 scope.

### 4. Schemas affected — checkpoint.json + state-transitions.log

**checkpoint.json (in-flight at `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json`):**

Top-level keys observed (snapshot):

```
run_id, feature_slug, started_at, current_stage, stage_status, next_action,
execution_pipeline_state_transitions,   // ← execution-phase field; NOT in canonical reference
cycle_3_closure, phase_0_findings,
execution_mode,                          // ← execution-phase field
execution_mode_rationale,
execution_pipeline_cycle_counters,       // ← execution-phase field
gate_6_decision, gate_history,
artifact_versions, adrs_authored,
reconciliation_cycles, cross_artifact_audit, architecture_audit, deliverable_packaging,
activated_layers, extraction_method, scope_class,
synthesis_stats, reviewer_invocations, plan_stats,
open_items, q3_closure, systemic_followup, params
```

`execution_pipeline_state_transitions` shape (array of objects per row):

```json
{
  "transition": "T0",
  "from": "INIT",
  "to": "pending",
  "timestamp": "2026-05-23T03:20:00Z",
  "trigger": "execution-pipeline-invocation; gate-6-approved at ...",
  "void": true,                  // optional
  "void_reason": "..."           // optional, paired with void
}
```

`execution_mode` is a free-form string. Observed value: `"single-agent-fallback"` (workaround posture per source analysis §5).

`execution_pipeline_cycle_counters` is a nested object: `{per_task: {<id>: <int>}, per_phase: {<id>: <int>}}`. Observed all-zero (workaround did not exercise counters per analysis §3.2).

**Gap:** these three execution-phase fields are NOT documented in `recipe-feature-pipeline/SKILL.md:96-128` (the canonical checkpoint.json schema reference). The de facto schema IS the schema. NFR-5-a requires the canonical reference to update in lockstep with any schema change under any §6 option.

**state-transitions.log (in-flight; JSONL):**

Per-entry schema, verified from the first 12 entries:

```json
{
  "timestamp": "<ISO-8601-UTC>",
  "transition_name": "T0|T1|T5|T13|T0-prime|...",  // T0-prime suffix observed (not in template)
  "from_state": "<state>",
  "to_state": "<state>",
  "trigger": "<free-form>",
  "invoking_agent": "execute-orchestrator",         // v1 invariant per template:63
  "task_id": "<id>|null",
  "phase_id": "Phase-0",                            // capitalized; template uses lowercase
  "cycle_counter": <int>|null,
  "artifact_paths_affected": ["<path>", ...],
  "context": {... free-form ...},
  "void": true,                                     // optional; not documented in template
  "void_reason": "..."                              // optional; paired
}
```

Canonical schema documented at `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md:34-54`.

**De facto extensions NOT in template:**

- `void: true` + `void_reason: string` — used to invalidate a prior T13 when a subsequent corrective brief voids it. Observed at line 2 of the in-flight log.
- `transition_name` suffix `-prime` — used to re-enter `pending` from `TERMINATED` after a voided T13. Observed at line 3.
- Case inconsistency: template line 88 uses lowercase `phase-0`; actual artifact uses capitalized `Phase-0`.

**v1 invariant incompatibility:** template line 63 declares `invoking_agent — always 'execute-orchestrator' in v1`. Under §6 option (b) retire-execute-orchestrator, this invariant is violated unless updated.

### 5. Blast-radius preview per §6 option

See §"Blast-radius preview per §6 option" below for the consolidated cross-option analysis. Per-touchpoint blast-radius shapes are in `codebase-analysis.json` `blast_radius` section.

### 6. Inherited-ADR confirmation

See §"Inherited ADR confirmations + newly-surfaced ADRs" below.

### 7. Per-agent design discipline note

The Research Plan's special-discipline note references the per-agent design discipline gap (`Issues/analysis-per-agent-design-evaluation-gap.md`). For this feature: the FR-5 sweep is mechanical and the affected SET is exhaustive at 2 agents (both already in the PRD inventory). No other agent in the project declares `Agent`, so the "potentially-applies-to-others" surface is empty. The broader per-agent-design-discipline gap remains a separate saved-for-later meta-feature.

## PRD FR-5 Inventory Sweep

| # | Agent | Path | tools: declaration (verbatim) | Dispatch purpose (from body) | Currently dispatching at runtime? | §6 design impact |
|---|---|---|---|---|---|---|
| 1 | execute-orchestrator | `.claude/agents/execute-orchestrator.md` | `[Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` | Dispatches the 4 execute-* specialists per the 14-row state machine | NO (tool surface stripped per source analysis §1.2) | (a) retire dispatch responsibility / (b) retire whole agent / (c) replace Agent with Bash(<script>:*) |
| 2 | execute-finalize-reconciler | `.claude/agents/execute-finalize-reconciler.md` | `[Read, Glob, Grep, Write, Agent]` | Dispatches via Contract 4 8-row matrix to upstream agents (mostly execute-task-code-producer for revision cycles) | NO (never reached at T9 in devcontainer-mcp-provisioning-r1; halted before phase-reconciliation) | (a) routing-target output to dispatch JSON consumed by parent / (b) same as option (a) but parent is recipe-feature-pipeline / (c) Bash(<dispatch-script>:*) and consume the dispatch JSON |

**No other agent in the 36-file `.claude/agents/` directory declares `Agent` in its `tools:` array.**

## Inherited ADR Confirmations + Newly-Surfaced ADRs

### Research Plan's claimed inherited ADRs — confirmation table

| ADR | Status | Confirmed? | Constraint imposed | Citation |
|---|---|---|---|---|
| ADR-0017 (document-reviewer + 4-cycle cap) | Accepted | **YES** — verified directly | The 4-cycle reconciliation cap is canonical here (Decision section line 155). PRD FR-3-c invariant. | `adrs/ADR-0017-document-reviewer-integration.md:155` |
| ADR-0019 (naming convention) | Accepted | **YES** | Phase-prefix `execute-` for execution-phase agents; `recipe-` for the orchestrator skill. Constrains any new sub-agent introduced under §6. | `adrs/ADR-0019-naming-convention.md:43-49` |
| ADR-0022 (sub-agent reasoning configuration) | Accepted | **YES** | Intentional `model:`/`effort:`/`skills:` triplet, audited (SA-13). ADR-0022 explicitly does NOT cover the `tools:` field's runtime behavior (that's T-001's scope). | `adrs/ADR-0022-subagent-reasoning-configuration.md:54-60` |
| ADR-0027 (deliverable-archive gap) | Accepted | **YES** | cwd MUST equal repo root precondition. The execution phase inherits this implicitly. | `adrs/ADR-0027-pipeline-skill-design-gap-deliverable-archive.md:30-44` |
| ADR-0029 (no silent scope changes) | Accepted | **YES** | Kill-criterion-#1 pause-and-rescope (PRD FR-2) IS the application of this principle. | `adrs/ADR-0029-no-silent-scope-changes-principle.md:26-29` |
| ADR-0033 (ADR-0029 execution-phase extension) | Accepted | **YES** | Names execute-orchestrator + 4 specialists explicitly (line 51). Line 71 specifies symmetric D-12: "cycle-cap exhaustion (per ADR-0017 4-cycle cap, symmetric per D-12) IS a deviation". **This is the canonical home for symmetric D-12 application — NOT ADR-0034.** | `adrs/ADR-0033-adr-0029-execution-extension.md:51, :71, :77-83` |
| ADR-0034 (PRD mis-credit cleanup) | Accepted | **YES, but mis-applied in Research Plan** | The actual scope of ADR-0034 is: ADR-0017 is canonical home for the 4-cycle cap, NOT ADR-0021 (which the PRD v1.1.0 mis-credited). ADR-0034 does NOT cover symmetric D-12. The Research Plan §38 attributes "ADR-0034 — PRD mis-credit cleanup; symmetric D-12" — the second half is incorrect. | `adrs/ADR-0034-prd-mis-credit-cleanup.md:46-51` |
| ADR-0036 (single-location ADR placement) | Accepted | **YES** | Any ADR design-composer authors lands at `adrs/ADR-NNNN-<title>.md` only. | `adrs/ADR-0036-single-location-adr-placement.md:13-21` |
| ADR-0037 (mcp-events.jsonl transition surfacing) | Accepted | **YES, but applicability is conditional** | Constrains this feature only if a §6 option introduces a new MCP-dispatch mechanism. Likely N/A for options (a)/(b). | `adrs/ADR-0037-mcp-events-jsonl-transition-surfacing.md:42-50` |
| ADR-0040 (Serena narrowed always-on) | Accepted | **YES, but marginal** | None of the execute-* agents are in the Serena allowlist; unlikely constraint. | `adrs/ADR-0040-serena-narrowed-always-on.md:42-49` |
| ADR-0041 (install-mechanism hybrid) | Accepted | **YES, but marginal** | Install-path discipline; unlikely constraint unless option (c) introduces a new script. | `adrs/ADR-0041-install-mechanism-hybrid.md:43-49` |

### Newly-Surfaced ADRs Not in Research Plan's List

| ADR | Title | Why relevant | Design-composer disposition |
|---|---|---|---|
| **ADR-0035** | auditing-shared skill-binding convention | execute-finalize-reconciler's frontmatter line 7 declares `skills: [..., auditing-shared]` and the file body line 110 explicitly references ADR-0035: "The auditing-shared binding is the new convention per ADR-0035 (cycle 3 of this design feature run)." Inherit at the Blueprint. | Consider inheriting |
| ADR-0042 | auditing-mcp family graduation | References execute-phase-quality-reviewer in consumer notes. Cross-impact UNLIKELY. | Read for cross-impact; likely no constraint |
| ADR-0043 | auditing-mcp Gate-6 hard gate | Same as ADR-0042; cross-references the execute-* family. | Same |

**Net new ADR to inherit: ADR-0035.** Surfaced as OI-CR-E.

## Blast-Radius Preview per §6 Option

The PRD FR-4 inventory enumerates 8 files. The codebase researcher's blast-radius analysis finds **additional files** that would need coordinated edits under each option:

### Files in the PRD's 8-file inventory (touched-or-may-be-touched, per FR-4)

1. `.claude/skills/recipe-feature-pipeline/SKILL.md`
2. `.claude/agents/execute-orchestrator.md`
3. `.claude/agents/execute-task-code-producer.md`
4. `.claude/agents/execute-task-quality-handler.md`
5. `.claude/agents/execute-phase-quality-reviewer.md`
6. `.claude/agents/execute-finalize-reconciler.md`
7. `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json` (schema reference; NFR-6-a says actual artifact is NOT migrated)
8. `working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log` (schema reference; not migrated)

### Files OUTSIDE the inventory that may be touched

| File | Why touched | §6 option that touches | Severity |
|---|---|---|---|
| `.claude/skills/KB-documentation-criteria/SKILL.md` (lines 67-71) | Template-assignment table names execute-orchestrator + 4 specialists as generated_by | (b) retire-orch (updates 2 rows); (a)/(c) probably none | Important |
| `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` (line 63) | v1 invariant `invoking_agent — always execute-orchestrator` is incompatible with option (b) | (b) retire-orch | Important |
| `.claude/skills/KB-documentation-criteria/references/templates/pipeline-run-summary-template.md` (line 113) | "Authored by execute-orchestrator at T12" | (b) retire-orch | Minor |
| `.claude/skills/KB-documentation-criteria/references/templates/per-task-execution-result-template.md` (line 10) | `generated_by: execute-task-code-producer` — likely unchanged | none | n/a |
| `.claude/skills/KB-documentation-criteria/references/templates/phase-quality-report-template.md` (line 9) | `generated_by: execute-phase-quality-reviewer` — likely unchanged | none | n/a |
| `.claude/skills/KB-documentation-criteria/references/templates/quality-reconciliation-log-template.md` (lines 13, 47, 56) | `generated_by: execute-finalize-reconciler` + Contract 4 examples | (a)/(b)/(c) depending on whether the reconciler's dispatch role is restructured | Minor |
| `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` (line 212) | Test data uses `invoking_agent: execute-orchestrator` | (b) retire-orch | Minor |
| `.claude/skills/auditing-codespaces/SKILL.md` (line 73) | Consumer note "consumers (especially `execute-phase-quality-reviewer`) MUST treat this..." | UNLIKELY any option | Minor |
| New file: `.claude/skills/auditing-shared/scripts/<dispatch-script>.py` (or equivalent) | Bash-script dispatch surface | (c) Bash-script | Important — design decision |

### Per-option summary

| Option | Files inside inventory | Files outside inventory | AC-FR-4-a open-item count |
|---|---|---|---|
| **(a) Flatten dispatch hierarchy** (parent dispatches 4 specialists directly; execute-orchestrator becomes state-machine documentation) | All 8 | ~1 (state-transitions-log-entry-template.md:63 invariant — needs minor edit if parent's identity replaces execute-orchestrator in log entries) | 1 |
| **(b) Retire execute-orchestrator** (state-machine folds into recipe-feature-pipeline; execute-orchestrator.md DELETED) | All 8 | **5+** (KB-documentation-criteria template-assignment table; state-transitions-log-entry-template.md v1 invariant; pipeline-run-summary-template.md generated-by; smoke_test_auditing_shared.py test data; auditing-codespaces consumer note) | **5+ — NEEDS USER CHECK** |
| **(c) Bash-script dispatch surface** | All 8 (Agent → Bash(<script>:*) in execute-orchestrator) | 1 (a new script under `.claude/skills/auditing-shared/scripts/` or equivalent — design-composer decides path) | 1 |

**Recommendation surfaced as evidence (NOT a design pre-decision):** option (b) carries materially larger blast-radius outside the inventory; options (a) and (c) stay closer to the PRD scope. Per AC-FR-4-a, option (b)'s scope-expansion needs explicit operator disposition.

## Conventions Observed (cc layer)

### Sub-agent frontmatter

- YAML frontmatter delimited by `---` at top of file.
- Common fields: `name`, `description`, `tools`, `model`, `effort`, `skills`, `memory` (optional).
- `tools:` is consistently expressed as an inline YAML array `[A, B, C]` across 33 of 36 files; 3 files use bare comma-separated lists (cc-critique.md:13, finalize-deliverable-packager.md:6, shared-document-reviewer.md:4). Both affected agents use the array form.

### Tool-grant taxonomy

- **Leaf agents (no Agent):** 34 of 36. All design-* / synth-* / intake-* / plan- / test- / review- / finalize- (except execute-finalize-reconciler) / shared-document-reviewer / cc-critique. All 4 execute-* specialists below the dispatcher.
- **Dispatcher agents (declare Agent):** 2 of 36. execute-orchestrator + execute-finalize-reconciler. Both belong to the execution-phase family.
- **Task-tracking primitives:** 27 of 36 declare TaskCreate or TaskUpdate. Distinct from Agent dispatch — task-tracking is in-context, dispatch creates new contexts.

### Skill naming (per ADR-0019)

- All knowledge KBs prefix `KB-` (24 files under `.claude/skills/`).
- The parent orchestrator prefixes `recipe-` (single file: recipe-feature-pipeline).
- Auditing skills prefix `auditing-` (9 files). No deviation observed.

### Error handling in execution-side specialists

Status-enum / errors-as-values pattern, NOT exception-throwing:

- code-producer: `COMPLETED | INCOMPLETE | BLOCKED`
- quality-handler: `APPROVED | NEEDS_REVISION | STUB_DETECTED | BLOCKER`
- phase-quality-reviewer: `PASS | NEEDS_RECONCILIATION | BLOCKER`
- finalize-reconciler: emits `cycle_cap_reached: boolean` + dispatches array
- orchestrator: emits `state-transitions.log` entries; emits TERMINATED on cycle-cap exhaustion

Consistent across all 5 execute-* agents.

### Audit-trail / artifact-pair pattern

- Per-task / per-phase artifacts use the D-5 pair pattern: JSON for machine consumption + .md companion for human review.
- `state-transitions.log` is JSONL-only (no .md companion — it's a streaming log).
- `checkpoint.json` is JSON-only (no .md companion).

### State-machine documentation

- Documented in execute-orchestrator.md body (lines 24-43) as a 14-row table.
- NOT documented in recipe-feature-pipeline/SKILL.md.
- Under §6 option (b), the state-machine table must move OR be re-created in the parent skill.

## Schemas Extracted

### checkpoint.json (from the in-flight devcontainer-mcp-provisioning-r1 artifact)

See §"Touchpoint #4" above for the detailed shape. Key observations:

- **Documented schema (planning-side fields):** at `recipe-feature-pipeline/SKILL.md:96-128`. Complete for planning fields.
- **De facto schema (execution-phase fields):** `execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`, `execution_mode_rationale`, `cycle_3_closure`, `phase_0_findings`. **NOT documented anywhere.**
- Per NFR-5-a, any §6 option that touches the schema MUST close this gap in lockstep with the change.

### state-transitions.log per-entry JSONL schema

See §"Touchpoint #4" above for the detailed shape. Key observations:

- **Canonical schema:** `state-transitions-log-entry-template.md:34-54`.
- **De facto extensions observed but not in template:** `void: true` + `void_reason`; `transition_name` suffix `-prime`. Both used during the workaround in devcontainer-mcp-provisioning-r1 to invalidate and re-enter a transition.
- **v1 invariant:** template line 63 fixes `invoking_agent = "execute-orchestrator"`. Incompatible with §6 option (b).
- **Case inconsistency:** template uses `phase-0` (lowercase); actual artifact uses `Phase-0` (capitalized).

## Open Items for Design-Composer

These are findings the codebase researcher cannot resolve. The per-layer cc Designer and design-composer decide handling.

| ID | Summary | Recommended disposition |
|---|---|---|
| **OI-CR-A** | Documentary mis-attribution: Research Plan §38 and PRD attribute "ADR-0034 symmetric D-12 application" — canonical home for symmetric D-12 is **ADR-0033 line 71** (ADR-0034 is unrelated PRD mis-credit cleanup). | Correct in the Blueprint/Plan/ACs (cite ADR-0017 + ADR-0033); do NOT propagate the ADR-0034 mis-attribution. |
| **OI-CR-B** | §6 option (b) escapes the PRD 8-file inventory (5+ files outside); per AC-FR-4-a this needs operator disposition. Options (a) and (c) each touch 1 file outside. | Surface to operator before per-layer cc Design commits to option (b). |
| **OI-CR-C** | Canonical checkpoint.json schema reference at `recipe-feature-pipeline/SKILL.md:96-128` lacks execution-phase fields — pre-existing documentation gap. Per NFR-5-a, any §6 option changing the schema must close this gap. | Close the gap in any chosen option's Plan. Even if option (b) doesn't change the schema shape, the canonical reference must document the de facto fields. |
| **OI-CR-D** | `state-transitions-log-entry-template.md:63` declares `invoking_agent — always execute-orchestrator in v1` — incompatible with §6 option (b). Template also lacks the `void` + `-prime` conventions observed in the in-flight log. | If option (b), update the template to either drop the invariant or shift it to whatever agent dispatches. Document `void` + `-prime` as accepted patterns OR explicitly reject them. |
| **OI-CR-E** | ADR-0035 (auditing-shared skill-binding convention) is NOT in the Research Plan's inherited-ADR list but is referenced explicitly in execute-finalize-reconciler.md:110. ADRs 0042/0043 also touch the execute-* family but are less directly load-bearing. | Inherit ADR-0035 at the Blueprint. Read ADR-0042/0043 for cross-impact. |
| **OI-CR-F** | Agent count discrepancy: Research Plan claims 35 sub-agent files; actual is 36. Minor, non-blocking. | Note in design-composer's review of the Research Plan's accuracy. No corrective action required. |
| **OI-CR-G** | execute-orchestrator.md:7 declares `skills: [..., recipe-feature-pipeline, ...]` — a sub-agent declaring its own parent's orchestrator skill in its skills array. May be a SA-13 finding under ADR-0022. | KB-cc-design author judgment. Surfaced as OQ-CR-003 for design-composer awareness. |

## Risks Observed

| Risk | Severity | For design-composer |
|---|---|---|
| Pre-existing schema-drift between recipe-feature-pipeline/SKILL.md canonical reference and the in-flight checkpoint.json (execution-phase fields are de facto only). Any §6 schema change must close this gap or perpetuate it. | Important | NFR-5-a is the relevant AC. The Blueprint/Plan must specify the canonical-reference update in lockstep with any schema change. |
| The `void` field and `-prime` transition-name suffix in state-transitions.log are de facto schema not documented anywhere. They worked once (during the workaround). A future workaround might re-invent them differently. | Minor | Document the `void` + `-prime` convention OR explicitly reject them as repair-time-only patches. |
| Both execute-orchestrator AND execute-finalize-reconciler declare Agent. Source analysis directly observed the defect in execute-orchestrator only. The defect in execute-finalize-reconciler is INFERRED with high confidence. T-001's probe must exercise BOTH agents OR generalize from one. | Important | If the chosen §6 option does NOT retire execute-finalize-reconciler's Agent declaration, the design must either confirm the agent works OR explicitly handle the parallel defect. |
| PRD FR-3-c names the load-bearing invariant set incompletely (cites ADR-0034 for symmetric D-12 when the canonical home is ADR-0033). | Minor (documentary) | Cite both ADR-0017 and ADR-0033 for the 4-cycle cap + symmetric application; drop the ADR-0034 reference to symmetric D-12. |
| "potentially-applies-to-others" finding: the FR-5 sweep is exhaustive (2 agents). No other agent declares Agent. The broader per-agent-design-discipline gap is a separate saved-for-later meta-feature (agent-roster-design-discipline-r1). | Informational | The FR-5 sweep result is unambiguous; no further sweep needed for this feature. |

---

**This report is the human-readable companion to `codebase-analysis.json`.** The JSON carries the full evidence base and citations; design-composer, per-layer cc Design, and shared-document-reviewer consume the JSON. The Markdown is for human review at the (optional) Discovery Research gate or as direct context for downstream agents.
