---
name: recipe-feature-pipeline
description: Thirteen-stage feature-design pipeline orchestrator (v4.5.0+; was twelve-stage in v4.4.x). Drives a single feature from raw user request to a verified, packaged deliverable archive via Intent Clarification → PRD Authoring → Discovery Planning → Discovery Research → Synthesis → per-layer Design → Design Composition → Architecture Audit → Plan Authoring → Acceptance Test Authoring → Phase Validator Authoring → Cross-Artifact Audit → Reconciliation → Task Decomposition → Deliverable Packaging. Coordinates 28 sub-agents across six human approval gates. Uses checkpoint resumption and 4-cycle reconciliation cap. Working artifacts under `working/feature/{slug}/`. Requires `cwd == repo-root` precondition (see ADR-0027). NOT for synthesis of prior research (use `synthesize` for that); NOT for single-component refactors (skip the pipeline and refactor directly).
user-invocable: true
---

# recipe-feature-pipeline Orchestrator

## Execution Contract

**Inputs accepted from caller:**

- `<feature-slug>` (positional, required) — kebab-case slug for this run (e.g., `add-order-cancellation`, `extract-billing-service`).
- `--raw-request <text-or-path>` (optional) — the user's raw feature request. If omitted, the orchestrator prompts via `AskUserQuestion` at Stage 1.
- `--resume <run-id>` (alternative, mutually exclusive with `<feature-slug>` for fresh runs) — resume a previously-checkpointed run.

**Outputs produced (under `working/feature/<slug>/`):**

| Path | Source agent | Stage |
|---|---|---|
| `intent-clarification.md` | intake-intent-clarifier | Intent Clarification |
| `prd-v<N>.md` | intake-prd-author | PRD Authoring |
| `research-plan.md` | discovery-plan-author | Discovery Planning |
| `codebase-analysis.json` + `codebase-analysis-report.md` | discovery-codebase-researcher | Discovery Research |
| `research-notes/<topic-slug>.md` | discovery-external-researcher (×N parallel) | Discovery Research |
| `synthesis.md` (or `synthesis/`) | synth-* fan-in | Synthesis |
| `<layer>-design.md` + `<layer>-dependencies.json` | design-`<layer>` (×K activated) | per-layer Design |
| `blueprint-v<N>.md` + `adrs/ADR-<NNNN>.md` (×0..M) | design-composer | Design Composition |
| `architecture-audit-issues.json` | review-architecture-auditor | Architecture Audit |
| `plan-v<N>.md` | plan-author | Plan Authoring |
| `acceptance-tests.md` | test-acceptance-author | Acceptance Test Authoring (parallel) |
| `phase-validators.md` | test-phase-validator-author | Phase Validator Authoring (parallel) |
| `cross-artifact-audit-issues.json` | review-cross-artifact-auditor | Cross-Artifact Audit |
| `reconciliation-log-r<R>.md` + `dispatch-r<R>.json` | finalize-reconciler (×R cycles, R ≤ 4) | Reconciliation |
| `tasks.json` | finalize-task-decomposer | Task Decomposition |
| `packager-report.json` | finalize-deliverable-packager | Deliverable Packaging (v4.5.0+) |
| `checkpoint.json` | orchestrator | All stages |

**Hard exclusions** (enforced unconditionally):

1. **No stage advance without gate pass.** The six human approval gates are mandatory; no orchestrator code path skips them.
2. **No ADRs from anyone but design-composer.** Per FR-5. The orchestrator rejects ADR writes from any other sub-agent path.
3. **No more than 4 reconciliation cycles per artifact family.** Per the convergence cap. Cycle 4 is terminal; surface to user.
4. **No silent fallback from GitNexus to codebase-memory-mcp.** The fallback is recorded in `codebase-analysis.json`'s `extraction_method` field; provenance preserved.
5. **No pipeline-stage references by number.** Stage taxonomy is by name only (Intent Clarification, PRD Authoring, etc.); filenames are semantic. Per the v4.3.1 surgery.

## Working-directory precondition

**`cwd` MUST equal the repo root** — the directory containing the `.claude/` configuration tree. All `working/feature/<slug>/` paths in this orchestrator and downstream agents resolve relative to `cwd`. If planning happens in a separate workspace (e.g., an LLM ephemeral filesystem), the orchestrator's first action is to relocate to the repo root or abort.

**Rationale:** ADR-0027 documents the gap that motivated this precondition. Without it, planning artifacts can land in an ephemeral workspace and never reach the deliverable archive. Discovered during integration test #2 (the v4.4.0 frontend-design-knowledge-r1 execution); the gap was the absence of any machinery enforcing `cwd == repo-root`.

**Verification:** Step 1 (run-id allocation) begins with a precondition check. If the check fails, the orchestrator halts before invoking any sub-agent.

## The 13 Pipeline Stages and 6 Human Gates

```
Stage                          | Sub-agent(s)                            | Output                        | Gate after?
-------------------------------|-----------------------------------------|-------------------------------|------------
1. Intent Clarification        | intake-intent-clarifier                 | intent-clarification.md       | Gate 1: Intent Confirmation
2. PRD Authoring               | intake-prd-author                       | prd-v<N>.md                   | Gate 2: PRD Approval
3. Discovery Planning          | discovery-plan-author                   | research-plan.md              | Gate 3: Research Plan Approval
4. Discovery Research          | discovery-codebase-researcher (×1)      | codebase-analysis.json        | — (no gate)
                               | discovery-external-researcher (×N par)  | research-notes/*.md           |
5. Synthesis                   | synth-* (extractor/grapher/critic/...)  | synthesis.md (or synthesis/)  | — (no gate; informational)
6. per-layer Design            | design-<layer> (×K activated, parallel) | <layer>-design.md (×K)        | — (per-layer reviewed)
7. Design Composition          | design-composer                         | blueprint-v<N>.md + adrs/     | Gate 4: Blueprint Approval
8. Architecture Audit          | review-architecture-auditor             | architecture-audit-issues.json| — (auditor-driven)
9. Plan Authoring              | plan-author                             | plan-v<N>.md                  | Gate 5: Plan Approval
10. Test Authoring             | test-acceptance-author (parallel)       | acceptance-tests.md           | — (no gate; reviewed by 11)
                               | test-phase-validator-author (parallel)  | phase-validators.md           |
11. Cross-Artifact Audit       | review-cross-artifact-auditor           | cross-artifact-audit-issues   | — (auditor-driven)
12. Task Decomposition         | finalize-task-decomposer                | tasks.json                    | Gate 6: Final Approval
(Reconciliation, as needed)    | finalize-reconciler                     | reconciliation-log-r<R>.md    | (no human gate; auditor-driven)
```

shared-document-reviewer is invoked at five points per ADR-0017 — see "shared-document-reviewer Invocation Points" below.

## shared-document-reviewer Invocation Points

Per ADR-0017, shared-document-reviewer runs at five points across the pipeline. It performs Gate 0 (structural completeness) and Gate 1 (semantic quality). It is NOT a human approval gate — it's an automated review that can block stage advance.

| Invocation | After stage | doc_type | If Gate 0 fails | If Gate 1 fails |
|---|---|---|---|---|
| 1 | Intent Clarification | `IntentClarification` | re-invoke intake-intent-clarifier | re-invoke intake-intent-clarifier |
| 2 | PRD Authoring | `PRD` | re-invoke intake-prd-author | dispatch to finalize-reconciler |
| 3 | per-layer Design (per layer) | `DesignDoc` | re-invoke design-`<layer>` | re-invoke design-`<layer>` |
| 4 | Design Composition | `DesignDoc` (Blueprint variant) | re-invoke design-composer | dispatch to finalize-reconciler |
| 5 | Plan Authoring | `Plan` | re-invoke plan-author | dispatch to finalize-reconciler |

The doc_type taxonomy is canonical per ADR-0011 + ADR-0017. Invocation 3 (per-layer Design) takes the `codebase_analysis` parameter so the reviewer can check dependency realizability.

## Checkpoint Mechanism

Run ID allocation: `run_id = <slug>-<UTC YYYYMMDD-HHMMSS>`. Deterministic, no LLM.

Checkpoint at `working/feature/<slug>/checkpoint.json` is updated after every stage completion (and after every gate decision):

```json
{
  "run_id": "<run-id>",
  "feature_slug": "<slug>",
  "started_at": "<ISO 8601>",
  "current_stage": "intent_clarification | prd_authoring | discovery_planning | discovery_research | synthesis | per_layer_design | design_composition | architecture_audit | plan_authoring | test_authoring | cross_artifact_audit | task_decomposition | reconciliation | complete",
  "stage_status": "pending | in_progress | awaiting_gate | passed | reconciling",
  "gate_history": [
    {"gate": "intent_confirmation", "decision": "approved", "timestamp": "<ISO>", "user_notes": "..."},
    {"gate": "prd_approval", "decision": "approved_with_revision", "timestamp": "<ISO>"}
  ],
  "artifact_versions": {
    "intent_clarification": 1,
    "prd": 2,
    "research_plan": 1,
    "blueprint": 1,
    "plan": 1
  },
  "reconciliation_cycles": {
    "blueprint": 0,
    "cross_artifact": 1
  },
  "activated_layers": ["frontend", "backend", "api", "database"],
  "extraction_method": "gitnexus",
  "params": {
    "max_external_research_topics": 6,
    "reconciliation_cap": 4
  }
}
```

Atomic write: write to `.tmp`, rename. Update after every meaningful state change.

## Step-by-step Orchestration

### Step 1 — Run-id allocation and working-directory setup

0. **Precondition check.** Verify `cwd / ".claude"` exists. If absent, halt with: "Orchestrator precondition violated — cwd must equal repo root (the directory containing `.claude/`). See ADR-0027 for rationale."
1. Compute `run_id`. Create `working/feature/<slug>/` if absent.
2. Initialize `checkpoint.json` with `current_stage: "intent_clarification"`, `stage_status: "pending"`.

### Step 2 — Stage 1: Intent Clarification

1. Invoke `intake-intent-clarifier` via the Agent tool:
   - `raw_request` — from caller's `--raw-request` flag, or via `AskUserQuestion` if missing.
   - `output_path` — `working/feature/<slug>/intent-clarification.md`.
   - `slug`, `prior_context` (empty on fresh run).
2. After write, invoke `shared-document-reviewer` with `doc_type: IntentClarification` and `target_path: working/feature/<slug>/intent-clarification.md`.
3. If reviewer's Gate 0 or Gate 1 fails: re-invoke `intake-intent-clarifier` with `review_feedback` populated. Re-review. If 4th iteration without pass: surface to user.
4. After reviewer pass: **Gate 1 (Intent Confirmation)** — present the intent-clarification.md to the user via the conversation; require explicit approval to advance. Update `checkpoint.gate_history`.

### Step 3 — Stage 2: PRD Authoring

1. Invoke `intake-prd-author`:
   - `intent_clarification_path`.
   - `output_path` — `working/feature/<slug>/prd-v1.md` (or next version).
   - On re-author after reconciliation: `prior_prd_path` + `review_feedback`.
2. Invoke `shared-document-reviewer` with `doc_type: PRD`.
3. If Gate 0 fails: re-invoke `intake-prd-author`. If Gate 1 fails: dispatch to `finalize-reconciler` with the issues JSON.
4. After reviewer pass: **Gate 2 (PRD Approval)** — present to user; require approval. Update checkpoint.

### Step 4 — Stage 3: Discovery Planning

1. Invoke `discovery-plan-author`:
   - `prd_path`.
   - `output_path` — `working/feature/<slug>/research-plan.md`.
   - Orchestrator may pre-compute `kb_inventory_path` and `adr_inventory_path` (enumerate `.claude/skills/KB-*/SKILL.md` and the project's `adrs/` directory).
2. **No shared-document-reviewer invocation here** (Research Plan is not in the doc_type taxonomy). Lighter review: orchestrator does a sanity check (file exists, sections present, external-topic count ≤ 6).
3. **Gate 3 (Research Plan Approval)** — present to user; require approval (especially the external-research topic list — that's a budget decision).

### Step 5 — Stage 4: Discovery Research (fan-out)

Per ADR-0021, Discovery Research is fan-out: 1 codebase researcher + N external researchers (N from research-plan, max 6) invoked in parallel.

1. Invoke `discovery-codebase-researcher` (single instance):
   - `research_plan_path`, `prd_path`.
   - `output_json_path` — `codebase-analysis.json`.
   - `output_report_path` — `codebase-analysis-report.md`.
   - `code_graph_preference` — optional; default GitNexus, fall back on degradation.
2. **In parallel**, for each external-research topic in the research plan, invoke `discovery-external-researcher`:
   - `topic_name`, `research_question`, `kb_gap_justification`, `acceptance_criteria`, `source_constraints` — from the topic's entry.
   - `output_path` — `working/feature/<slug>/research-notes/<topic-slug>.md`.
3. Wait for all parallel invocations to complete. No gate at this stage; advance to Synthesis.

### Step 6 — Stage 5: Synthesis

Synthesis is itself a sub-pipeline (the existing `synthesize` skill is conceptually similar but operates on different inputs). For the feature pipeline, Synthesis fan-in consumes the Discovery Research outputs and produces `synthesis.md` (or a `synthesis/` directory with structured outputs).

1. Orchestrator invokes the synthesis sub-pipeline:
   - Inputs: `codebase-analysis.json`, `research-notes/*.md`, `prd-v<N>.md`.
   - Internal stages handled by synth-extractor / synth-grapher / synth-critic / synth-framer / synth-substrate / synth-synthesizer.
2. Output: `working/feature/<slug>/synthesis.md` (or `synthesis/` with sub-files).
3. No human gate. Advance to per-layer Design.

#### Feature-pipeline mode of `synth-substrate`

The `synth-substrate` agent has two operating modes:

| Mode | Used by | Decision space | Option enumeration | Output schema |
|---|---|---|---|---|
| **Substrate-comparison mode** (default) | `synthesize` skill | "How do we accomplish X on Claude Code vs. Azure vs. M365?" | Exactly three options (`native`, `adapter`, `substrate_change`), per `substrate-mapping.schema.json` | `05-substrate-map.json` validated by Layer A schema |
| **Implementation-strategy mode** | `recipe-feature-pipeline` | "Within our single substrate (e.g., Node + Express + PostgreSQL), what implementation strategy for decision D-N?" | Variable count (1-N) with explicit rationale for option count | Free-form section in `synthesis.md`; NOT validated against substrate-mapping.schema |

When invoked by the feature pipeline, `synth-substrate` operates in implementation-strategy mode. The three-option enumeration hard exclusion in the `synthesize` SKILL.md does **not** apply — that exclusion is specific to substrate-comparison mode where the three options have semantic meaning (`native`/`adapter`/`substrate_change`). In implementation-strategy mode, forcing three options when only one or two genuinely exist produces straw-men and wastes reviewer attention.

**Discipline in implementation-strategy mode:**

- Each decision enumerates as many options as genuinely exist (1, 2, 3, or more).
- The option count is **justified by genuine option space, not by quota**. A single-option decision is acceptable if the designer can write a credible "no alternatives considered because..." rationale (e.g., "the PRD's NFR-4 constraint excludes all library alternatives; only the in-repo pattern is viable").
- When ≥2 options exist, mark one `recommended` and others `rejected` with named rejection rationale (e.g., "rejected — fails NFR-1 latency budget").
- Straw-men are an anti-pattern: if the rejection rationale boils down to "obviously worse," that option should not have been enumerated.
- Output of the substrate phase in this mode is folded into `synthesis.md` as the **decision substrate** section, not a separate JSON file. Per-layer designers read the substrate section to learn the recommended option + the rejected alternatives' rationale.

This mode is documented here rather than in the `synthesize` skill because it is specific to the feature pipeline's reuse pattern; the original `synthesize` skill's contract remains unchanged.

### Step 7 — Stage 6: per-layer Design (fan-out)

Per FR-3 + ADR-0016, per-layer Design is fan-out: K parallel invocations, one per activated layer (K ≤ 9).

1. From PRD's Layer Scope (which is exhaustive per FR-X), identify activated layers: those marked **in scope**.
2. **In parallel**, for each activated layer, invoke the corresponding `design-<layer>` sub-agent:
   - layer ∈ {frontend, backend, api, query, database, iac, cc (filename: design-claude-code), cicd, codespaces}.
   - Standard inputs per the per-layer designer template: `prd_path`, `research_plan_path`, `codebase_analysis_path`, `research_notes_dir`, `synthesis_path`, `rationale_brief_path`, `output_design_path`, `output_dependencies_path`, `slug`.
3. For each completed per-layer Design output: invoke `shared-document-reviewer` with `doc_type: DesignDoc` and `codebase_analysis: <path-to-codebase-analysis.json>`. If Gate 0 fails: re-invoke that specific design-`<layer>`. If Gate 1 fails: re-invoke (lower-severity than the Blueprint-level re-author).
4. After all per-layer Design outputs pass: advance to Design Composition (no human gate at per-layer level; the gate is on the integrated Blueprint).

### Step 8 — Stage 7: Design Composition

1. Invoke `design-composer`:
   - `prd_path`, `per_layer_designs_dir`, `per_layer_dependencies_dir`, `codebase_analysis_path`, `research_notes_dir`, `synthesis_path`, `rationale_brief_path`, `existing_adrs_dir`, `output_blueprint_path`, `output_adrs_dir`, `slug`.
   - On re-compose after reconciliation: `prior_blueprint_path` + `review_feedback`.
   - Note: design-composer uses `model: opus` (declared in its frontmatter); the orchestrator does NOT need to override.
2. After the Blueprint is written: invoke `shared-document-reviewer` with `doc_type: DesignDoc` (Blueprint variant).
3. If Gate 0 fails: re-invoke `design-composer`. If Gate 1 fails: dispatch to `finalize-reconciler`.
4. After reviewer pass: **Gate 4 (Blueprint Approval)** — present to user; require approval. Update checkpoint.

### Step 9 — Stage 8: Architecture Audit

1. Invoke `review-architecture-auditor`:
   - `blueprint_path`, `rationale_brief_path`, `synthesis_path`, `codebase_analysis_path`, `inherited_adrs_dir`, `new_adrs_dir`, `output_issues_path`, `slug`.
   - `prior_audit_path` if re-audit.
   - `code_graph_preference` — default GitNexus.
2. Read the verdict from `architecture-audit-issues.json`:
   - `verdict: pass` → advance to Plan Authoring.
   - `verdict: conditional_pass` (MAJOR issues, no BLOCKER) → dispatch to `finalize-reconciler` (auditor-driven, no human gate).
   - `verdict: fail` (BLOCKER) → dispatch to `finalize-reconciler` (required revision).
3. Reconciliation cycle increment: `checkpoint.reconciliation_cycles.blueprint += 1`. If `>= 4`: hard cap; surface to user.

### Step 10 — Stage 9: Plan Authoring

1. Invoke `plan-author`:
   - `prd_path`, `blueprint_path`, `adrs_dir`, `codebase_analysis_path`, `output_path`, `slug`.
   - On re-author: `prior_plan_path` + `review_feedback`.
2. Invoke `shared-document-reviewer` with `doc_type: Plan`.
3. If Gate 0 fails: re-invoke plan-author. If Gate 1 fails: dispatch to `finalize-reconciler`.
4. After reviewer pass: **Gate 5 (Plan Approval)** — present to user; require approval.

### Step 11 — Stage 10: Test Authoring (parallel)

In parallel, invoke:

1. `test-acceptance-author`:
   - `prd_path`, `blueprint_path`, `plan_path`, `codebase_analysis_path`, `output_path` — `working/feature/<slug>/acceptance-tests.md`.
2. `test-phase-validator-author`:
   - `plan_path`, `prd_path`, `blueprint_path`, `output_path` — `working/feature/<slug>/phase-validators.md`.
   - `acceptance_tests_path` — pass if test-acceptance-author completed first; null if true parallel.

Wait for both completions. **No shared-document-reviewer invocation** (these are not in the doc_type taxonomy). The cross-artifact auditor catches alignment issues.

### Step 12 — Stage 11: Cross-Artifact Audit

1. Compute the Blueprint diff: `diff working/feature/<slug>/blueprint-v<N-1>.md working/feature/<slug>/blueprint-v<N>.md > working/feature/<slug>/blueprint-diff-v<N>.patch` (if N > 1).
2. Invoke `review-cross-artifact-auditor`:
   - `current_blueprint_path`, `prior_blueprint_path` (if any), `blueprint_diff_path` (if computed), `plan_path`, `acceptance_tests_path`, `phase_validators_path`, `output_issues_path`, `round_number` (1-indexed per cycle), `slug`.
   - Note: auditor uses `model: opus` (declared in frontmatter).
3. Read verdict:
   - `verdict: pass` → advance to Task Decomposition.
   - `verdict: conditional_pass` / `fail` → dispatch to `finalize-reconciler`.
   - `verdict: hard_capped` (round 4) → terminal; surface to user.
4. Reconciliation cycle: `checkpoint.reconciliation_cycles.cross_artifact += 1`. Cap at 4.

### Step 13 — Stage 12: Task Decomposition

1. Invoke `finalize-task-decomposer`:
   - `prd_path`, `blueprint_path`, `adrs_dir`, `plan_path`, `acceptance_tests_path`, `phase_validators_path`, `codebase_analysis_path`, `output_path` — `working/feature/<slug>/tasks.json`.
2. After tasks.json is produced, proceed to Step 14 (Deliverable Packaging) before reaching Gate 6.

### Step 14 — Stage 13: Deliverable Packaging (added in v4.5.0)

1. Invoke `finalize-deliverable-packager`:
   - `feature_slug` — current slug.
   - `scope_class` — read from `working/feature/<slug>/intent-clarification.md`'s `scope_class:` frontmatter (FULL / MINOR / PATCH per ADR-0023).
   - `version_tag` — semver tag for this release if applicable (e.g., `v4.5.0`); when provided, packager produces handoff drafts.
   - `prior_version_handoff_path` — path to the predecessor handoff file (e.g., the prior version's handoff document under `handoff/`) for stylistic reference; optional.
2. The packager:
   - Verifies `working/feature/<slug>/` contains the expected artifact set per the spec at `KB-documentation-criteria/references/deliverable-archive-spec.md`.
   - Invokes `shared-document-reviewer` with `doc_type: DeliverableArchive` for validation.
   - Optionally drafts `handoff/HANDOFF-v<version_tag>.md` + `handoff/CONTINUE_PROMPT-v<version_tag>.md` (marked DRAFT for human review).
   - Emits `working/feature/<slug>/packager-report.json` with verdict (PASS / BLOCK / REVIEW) and finding details.
3. If packager verdict is BLOCK: surface BLOCKER findings to the human; do NOT advance to Gate 6 until findings are resolved.
4. **Gate 6 (Final Approval)** — present `tasks.json` AND `packager-report.json` (plus draft handoff documents if produced) to the user. Require explicit approval to mark the run complete.
5. After approval: update `checkpoint.current_stage = "complete"`. Pipeline run is done.

### Reconciliation Cycles

Whenever a reviewer or auditor surfaces issues that warrant revision:

1. Invoke `finalize-reconciler`:
   - `issues_json_paths` — list of issues JSONs from this trigger.
   - `current_artifact_paths` — map of all in-progress artifacts.
   - `cycle_number` — appropriate counter from checkpoint.
   - `output_log_path` — `working/feature/<slug>/reconciliation-log-r<R>.md`.
   - `output_dispatch_path` — `working/feature/<slug>/dispatch-r<R>.json`.
   - `prior_log_paths` — list of prior cycles' logs.
2. Read the dispatch JSON. For each dispatch entry (in order):
   - Re-invoke the named target_agent with the consolidated feedback_brief.
3. For each user-escalation: surface via `AskUserQuestion`; record the user's decision in `checkpoint.gate_history`.
4. For each acceptance deferral: log and proceed.
5. After all dispatches complete: re-invoke the auditor that triggered this reconciliation. If verdict improves to `pass`: advance. If still failing and cycle < 4: another reconciliation. If cycle == 4: hard cap; surface.

### Resume Handling (`--resume <run-id>`)

When invoked with `--resume`:

1. Read `working/feature/<slug>/checkpoint.json`. If file missing or `current_stage == "complete"`: report status and exit.
2. From `current_stage` + `stage_status`, determine the next action:
   - `awaiting_gate` → re-present the gate question to the user.
   - `in_progress` → re-invoke the current stage's sub-agent (it should be idempotent on re-author; check artifact_versions to determine which version to write).
   - `passed` → advance to the next stage per the orchestration order.
   - `reconciling` → continue the reconciliation cycle.
3. Reconciliation cycle counters are preserved across resumption.

## Error Handling Per Stage

Per Blueprint v4.3.1 + ADR-0021 + the 4-cycle convergence cap:

- **Sub-agent fails to write its output.** Retry once with explicit re-author prompt. On second failure: surface to user with the partial output + sub-agent's TaskUpdate messages.
- **Sub-agent writes malformed output (fails schema or template Gate 0).** Re-invoke with shared-document-reviewer's structural feedback. On second failure: surface to user.
- **Auditor returns fail.** Dispatch to finalize-reconciler. Increment cycle counter. At cycle 4: hard cap.
- **GitNexus MCP degraded.** Fall back to codebase-memory-mcp. Record `extraction_method: codebase-memory-mcp` in `codebase-analysis.json`. Continue without re-invocation.
- **External research returns zero usable findings on a topic.** The topic's research note documents this with "Acceptance-criteria check: not satisfied; recommend escalation." Synthesis surfaces in Limitations. Pipeline continues.
- **User declines at a gate.** Pause the pipeline. Update `checkpoint.stage_status = "awaiting_gate"`. The next `--resume` re-presents the gate. The user may modify upstream artifacts via direct file edit before resuming; checkpoint's `artifact_versions` reflects the latest written version on resume.
- **Convergence hard cap (4 cycles on any artifact family).** The auditor returns `verdict: hard_capped` (in cross-artifact case) or the reconciler's log records it. Orchestrator surfaces to user with the remaining open-issue list and the user's options: ship with documented exceptions, defer the feature, or restart from an earlier stage.

## Resource Budget Defaults

| Resource | Default | Override |
|---|---|---|
| External research topics | 6 max | `--max-external-research-topics N` |
| Reconciliation cycles per artifact family | 4 (hard cap) | NOT overridable; design invariant |
| Per-layer Designer parallelism | 9 (one per layer) | NOT capped; orchestrator dispatches all in scope |
| External Researcher parallelism | min(topic_count, 6) | implicit via topic count cap |

## Activated Sub-Agents Inventory

This orchestrator activates 27 pipeline sub-agents across 12 stages, plus `shared-document-reviewer` (at 5 invocation points). Inventory:

| Stage | Sub-agents |
|---|---|
| Intent Clarification | intake-intent-clarifier |
| PRD Authoring | intake-prd-author |
| Discovery Planning | discovery-plan-author |
| Discovery Research | discovery-codebase-researcher + N × discovery-external-researcher |
| Synthesis | synth-extractor, synth-grapher, synth-critic, synth-framer, synth-substrate, synth-synthesizer |
| per-layer Design | up to 9 of: design-frontend, design-backend, design-api, design-query, design-database, design-iac, design-cc (filename design-claude-code), design-cicd, design-codespaces |
| Design Composition | design-composer |
| Architecture Audit | review-architecture-auditor |
| Plan Authoring | plan-author |
| Test Authoring | test-acceptance-author + test-phase-validator-author |
| Cross-Artifact Audit | review-cross-artifact-auditor |
| Task Decomposition | finalize-task-decomposer |
| Reconciliation (as needed) | finalize-reconciler |
| (Cross-stage) | shared-document-reviewer (5 invocation points per ADR-0017) |

Total: **27 pipeline sub-agents** + 1 shared-document-reviewer.

## Memory

Persistent observations use Claude Code's built-in memory features:

- **Per-sub-agent memory.** Each sub-agent declares `memory: project` in its frontmatter. Claude Code maintains `.claude/agent-memory/<agent-name>/MEMORY.md` automatically. See each agent's "Memory discipline" section.
- **Cross-run main-agent observations.** Ride on Claude Code's auto-memory at `~/.claude/projects/<project>/memory/`.
- **Run index.** A runtime-only append-only log at `working/feature/run-index` (one line per completed run: `- <run-id> — completion <ISO 8601>`). Created by the Stop hook during a real run; not a project-source file.

This skill does not maintain any custom `.memories/` directory.

## Cross-References to Architecture

- Pipeline topology + 12 stages defined in **Blueprint v4.3.1** (`/home/claude/handoff/feature-pipeline-round-3/blueprint-v4.3.1.md`).
- ADRs governing this orchestrator:
  - **ADR-0011** — All templates consolidated in KB-documentation-criteria.
  - **ADR-0016** — Design fan-out + fan-in.
  - **ADR-0017** — shared-document-reviewer at 5 invocation points; renamed critics.
  - **ADR-0018** — canonical codebase-analysis.json schema (v1.1.0).
  - **ADR-0019** — Naming convention (intake-/discovery-/synthesis-/design-/review-/plan-/test-/finalize-/shared-/KB-/recipe-).
  - **ADR-0020** — KB consolidation (KB-review-disciplines absorbs prior critique-1/critique-2/review-disciplines).
  - **ADR-0021** — Discovery refactor; KB-and-ADR-first; fan-out.
- FR-5 (only design-composer authors ADRs) — invariant enforced by the orchestrator.

## Invocation Examples

Fresh run:
```
/feature-pipeline add-order-cancellation --raw-request "Allow customers to cancel pending orders within 30 minutes of placement."
```

Resume:
```
/feature-pipeline --resume add-order-cancellation-20260520-103045
```

Status check (no advance):
```
/feature-pipeline --status <slug>
```
(Reads checkpoint.json and reports current_stage + stage_status; does not invoke any sub-agent.)
