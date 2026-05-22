---
id: CC-Design-execution-pipeline-design-r1
version: 1.0.0
status: draft
feature_slug: execution-pipeline-design-r1
generated: 2026-05-22T05:00:00Z
generated_by: claude (acting as design-claude-code, single invocation per pipeline run)
derived_from:
  - working/feature/execution-pipeline-design-r1/synthesis.md (v1.1.0)
  - working/feature/execution-pipeline-design-r1/codebase-analysis.md (v1.1.1)
  - working/feature/execution-pipeline-design-r1/research-plan.md (v1.1.0)
  - working/feature/execution-pipeline-design-r1/prd-v1.1.0.md (v1.1.0)
  - working/feature/execution-pipeline-design-r1/intent-clarification.md (v1.0.0)
  - .claude/skills/KB-cc-platform/SKILL.md
  - .claude/skills/KB-cc-design/SKILL.md
  - .claude/skills/KB-cc-design/references/principles.md
  - .claude/skills/KB-cc-design/references/patterns-and-anti-patterns.md
  - .claude/skills/KB-documentation-criteria/references/shared-conventions.md
  - .claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md
  - .claude/skills/recipe-feature-pipeline/SKILL.md
  - adrs/ADR-0017-document-reviewer-integration.md
  - adrs/ADR-0021-discovery-phase-architecture.md
  - adrs/ADR-0028-skill-design-fixes-v4-5-0.md
  - adrs/ADR-0029-no-silent-scope-changes-principle.md
  - adrs/ADR-0030-mechanism-alpha-pedagogical-marker-justification.md
  - adrs/ADR-0031-auditing-shared-skill-module.md
reviewer_verdict: approved (Gate 0 pass, Gate 1 pass — Consistency 95, Completeness 96, Rule compliance 95, Clarity 93)
reviewed_at: 2026-05-22T05:45:00Z
---

# Claude Code Design — execution-pipeline-design-r1

## Note on layer scope

This feature is **single-layer** per PRD Layer Scope: only the Claude Code layer is activated. No other per-layer designers fire. Cross-layer dependencies that would normally surface (CI/CD, MCP, Backend, etc.) are noted in "Dependencies on other layers" but no parallel layer designs exist to integrate with.

## Source map

The 18 substantive Blueprint decisions (D-1 through D-18, with D-2 split into D-2a-d → 21 decision targets) are carried forward from synthesis.md v1.1.0. This document resolves each via per-pass deliberation; resolutions populate the Blueprint-template subsections below. A decision-to-subsection trace is maintained inline as "Pass N resolution summary" blocks.

## Layer responsibility scope

This feature lives entirely in the Claude Code layer. The execution pipeline that this feature designs is realized as Claude Code primitives — agents (subagents), skills (KB-* and auditing-*), scripts (under skill `scripts/` directories), and hooks. No CI/CD, no Codespaces, no backend, no database. The execution pipeline runs locally under the developer's Claude Code session.

The Claude Code layer owns, for this feature:

- **The execution orchestration shape** — what agent (if any) coordinates state transitions; how task execution, phase-quality review, and reconciliation flow between agents.
- **Agent inventory and shape** — which new subagents are added, their model/effort/tool/skill configuration per Principle 9, their isolation boundaries per Principle 4.
- **Skill family extensions** — auditing-* family additions (FR-8 GHA + Codespaces extraction), auditing-shared/ scripts (FR-6 validator, possibly D-15 enforcement check), ai-development-guide skill install (AC-FR-9-e).
- **Hook surface** — FR-5 state-transition hooks fire at each gate transition; their event binding, contract, and output destination are CC-layer design.
- **Permission policy** — execution requires test-running and code-mutation tools; the permission scope balances determinism (Principle 3) against developer autonomy.
- **Document templates** — KB-documentation-criteria/references/templates/ additions for execution-phase artifacts (FR-7).
- **Discipline enforcement mechanisms** — mechanical defenses for `recipe-feature-pipeline/SKILL.md` disciplines (per D-15 broadened scope; discipline 5 worked example).

What the CC layer does NOT own here:

- Per-task acceptance criteria authoring — that's the planning-side `test-acceptance-author` agent (already exists; not modified).
- ADR authoring — per FR-5 of the layer's general spec, designers don't author ADRs. ADRs are authored alongside Blueprint per ADR-0021's flow.
- The substantive content of audit findings — the auditing skills (`auditing-cc-configs`, `auditing-github-actions` new, `auditing-codespaces` stub) own that.

## Inventory of CC primitives being introduced or modified

This inventory is built incrementally across passes. Pass 1 entries below; later passes append.

### Subagents (new)

| Name | Filename | Path | Purpose | Scope | Activation |
|---|---|---|---|---|---|
| `execute-orchestrator` | `execute-orchestrator.md` | `.claude/agents/` | Owns execution-side state machine; coordinates per-task loops, phase-quality aggregation, reconciliation cycles, hook invocation. Per D-6. | project | model-invocable (lead-agent invokes when execution begins) |
| `execute-phase-quality-reviewer` | `execute-phase-quality-reviewer.md` | `.claude/agents/` | Aggregates structured outputs from N audit/test/validator invocations into a single phase-quality verdict. Per D-9 first role. | project | model-invocable (invoked by `execute-orchestrator` at phase-quality stage) |
| `execute-finalize-reconciler` | `execute-finalize-reconciler.md` | `.claude/agents/` | Dispatches reconciliation revisions to upstream stages when findings surface; tracks reconciliation cycle count against hard cap. Analog of planning-side `finalize-reconciler`. Per D-14 (Pass 4) for dispatch taxonomy; per D-12 (Pass 4) for cycle-cap value. | project | model-invocable (invoked by `execute-orchestrator` when phase-quality reviewer surfaces dispatchable findings) |
| `execute-task-code-producer` | `execute-task-code-producer.md` | `.claude/agents/` | Produces code for one task per task spec + acceptance criteria. Binds to `ai-development-guide` per D-11. Per D-2 sub-decisions; inherits selective BLOCKING annotations (D-2a) and APPROVED-discipline interplay with quality-handler (D-2c). | project | model-invocable (invoked by `execute-orchestrator` per-task) |
| `execute-task-quality-handler` | `execute-task-quality-handler.md` | `.claude/agents/` | Runs stub detection (D-2d) → lint → test → final aggregation; returns status enum (APPROVED / NEEDS_REVISION / STUB_DETECTED / BLOCKER) per D-2c. Binds to `ai-development-guide` per D-11. | project | model-invocable (invoked by `execute-orchestrator` after `execute-task-code-producer` completes) |

### Subagents (modified)

| Name | Modification | Per |
|---|---|---|
| `shared-document-reviewer` | Extend `doc_type` taxonomy to include execution-phase artifacts (per-task-execution-log, phase-quality-report, quality-reconciliation-log). Per D-9 second role; resolution to be authored in Pass 5 via D-4. | D-9 + D-4 |

### Skills (new)

| Name | Location | Purpose | Scope |
|---|---|---|---|
| `ai-development-guide` | `.claude/skills/ai-development-guide/SKILL.md` | Code-level quality discipline (lint → build → test → final gate). Source: reference upload at `/mnt/user-data/uploads/SKILL__2_.md`. Per AC-FR-9-e + D-11. Bound by `execute-task-code-producer` + `execute-task-quality-handler`. | project |

### Scripts (new, under skill `scripts/` directories)

| Path | Purpose | Caller(s) | Per |
|---|---|---|---|
| `.claude/skills/auditing-shared/scripts/detect_stubs.py` | Pattern-based incomplete-implementation detection across languages (Python `pass`, JS `throw Error("not implemented")`, Rust `unimplemented!()`, etc.). Returns JSON findings. Language-aware (auto-detects from file extension or takes language arg). | `execute-task-quality-handler` first step | D-2d, ADR-0031 |
| `.claude/skills/auditing-shared/scripts/run_phase_checks.py` | Thin coordinator that fans out to each canonical audit-family entry point (`auditing-cc-configs`, `auditing-github-actions`, `auditing-codespaces`), test runners (unit/integration/E2E), and frontmatter validator. Aggregates findings into hybrid domain+severity structure (D-1). Returns JSON output consumed by `execute-phase-quality-reviewer`. | `execute-orchestrator` at phase-quality gate; invoked once per phase | D-3, D-1, ADR-0031 |
| `.claude/skills/auditing-github-actions/scripts/audit_workflow.py` | GHA workflow audit. Already exists at `.claude/skills/KB-github-actions-platform/scripts/audit_workflow.py` (per IN-002 Batch B); extracted to canonical auditing- home per FR-8 + ADR-0031. | `run_phase_checks.py` (audits-domain dispatch) | FR-8, D-3 |
| `.claude/skills/auditing-codespaces/scripts/<TBD>` | Codespaces audit stub per AC-FR-8-b. Initial stub may be a no-op script that returns empty findings; substantive implementation deferred to future feature. | `run_phase_checks.py` (audits-domain dispatch) | FR-8, AC-FR-8-b |

### Skills (new, supporting audit-family extractions per FR-8)

| Name | Location | Purpose | Per |
|---|---|---|---|
| `auditing-github-actions` | `.claude/skills/auditing-github-actions/` | Houses GHA audit script + `references/action_versions.md` (currently misplaced at `KB-github-actions-platform/scripts/` per IN-002). Symmetric structure with `auditing-cc-configs`. | FR-8, ADR-0031 |
| `auditing-codespaces` | `.claude/skills/auditing-codespaces/` | Stub skill for Codespaces audit. AC-FR-8-b mandates existence; substantive content deferred. | AC-FR-8-b |

[Pass 4 will add: FR-5 state-transition hook implementation. Pass 5 may add: discipline-check script (auditing-shared/scripts/check_pipeline_discipline.py) per D-15 if option 2 is taken.]

## CLAUDE.md changes

**No CLAUDE.md changes for this feature.**

Rationale per KB-cc-design Principle 5 (one source of truth) and Principle 1 (lowest-cost primitive): the disciplines this feature codifies are either (a) per-feature pipeline workflow that belongs in `recipe-feature-pipeline/SKILL.md` (already exists; not in CLAUDE.md scope), or (b) mechanically enforced via scripts (FR-6 validator, detect_stubs, check_pipeline_discipline). Adding CLAUDE.md prose would create a second source of truth that drifts; the established discipline lives in the recipe skill.

The orchestrator agent's prompt references `recipe-feature-pipeline/SKILL.md` directly (the agent's `skills:` list includes the recipe). Other agents don't need recipe knowledge in CLAUDE.md; they're invoked by the orchestrator with the context they need.

## Rule patterns

**No new rules needed for this feature.**

Rationale: rules per KB-cc-design Principle 2 are file-domain-specific guidance loaded via `paths:` glob matching. This feature introduces agents, skills, and scripts — none of which produce file-domain-specific guidance that would benefit from path-gated rules. The disciplines this feature codifies (stub detection, no-stage-by-number, frontmatter validity) are mechanically enforced via scripts (D-2d, D-15, FR-6), not via path-gated rule prose.

If future patterns emerge (e.g., a guidance rule for authors of execution-phase artifacts), a path-gated rule scoped to `working/feature/*/cc-design.md` or similar could be added. Out of scope for this feature.

## Skill patterns

### `ai-development-guide` (new install, per AC-FR-9-e + D-11)

**Source**: reference upload at `/mnt/user-data/uploads/SKILL__2_.md` (302 lines / 9 sections per IN-001 Batch A finding). The skill codifies the code-level quality discipline: lint → build → test → final gate.

**Install location**: `.claude/skills/ai-development-guide/SKILL.md`.

**Activation**: model-invocable. The description (to be authored at install time) should match contexts where code-level quality discipline is being applied — task execution, code review, debugging quality failures.

**Bound by**: `execute-task-code-producer` + `execute-task-quality-handler` (per D-11 boundary). Other agents do not bind.

**Install timing**: must happen before the per-task agents are functional. Plan-stage task should sequence the install before agent prompts that reference the skill are authored.

**Open item**: the reference upload is named `SKILL__2_.md` (system filename); the canonical install name is `ai-development-guide`. The Plan-stage task should copy + rename, not move (preserve the upload as reference). Frontmatter `name:` field needs to be `ai-development-guide` (verify the upload's frontmatter matches; if mismatched, fix during install).

[Pass 3 adds:]

### `auditing-github-actions` (new skill, per FR-8 + ADR-0031)

**Source**: extracted from currently-misplaced `KB-github-actions-platform/scripts/audit_workflow.py` + `KB-github-actions-platform/scripts/action_versions.md` (per IN-002 Batch B). The script and references move to a canonical auditing-* home symmetric with `auditing-cc-configs`.

**Install location**: `.claude/skills/auditing-github-actions/SKILL.md` + supporting `scripts/audit_workflow.py` + `references/action_versions.md`.

**Activation**: model-invocable (when GHA workflow audits are needed) + script-callable from `auditing-shared/scripts/run_phase_checks.py` (D-3).

**Symmetric structure with `auditing-cc-configs`**: SKILL.md + scripts/ + references/ pattern.

**Migration sequencing**: existing files MUST move (not copy) to preserve git history; sourcing references at `KB-github-actions-platform/scripts/` will break after extraction. Plan-stage task should sequence: (1) author new skill SKILL.md; (2) move script and references; (3) update any other references pointing to old paths.

### `auditing-codespaces` (new stub skill, per AC-FR-8-b)

**Stub scope**: AC-FR-8-b requires the skill exist; substantive Codespaces audit logic is deferred. Initial implementation: SKILL.md describing intent + a no-op script that returns empty findings (so `run_phase_checks.py` can invoke it cleanly without conditional logic).

**Install location**: `.claude/skills/auditing-codespaces/SKILL.md` + stub `scripts/audit_codespaces.py` (returns `{"findings": []}`).

**Migration sequencing**: no migration; net-new skill.

**Open item**: stub script's exact name + entry-point signature deferred to Plan-stage task. Q-CC-N noted below: should the stub script declare a "stub" status in its output, so downstream consumers can distinguish "ran cleanly, no findings" from "stub, didn't actually run anything"?

[Pass 4 + Pass 5 may add more skills as state-transition + discipline-enforcement decisions resolve.]

## Subagent patterns

Per KB-cc-design Principle 9, reasoning configuration is intentional, not default. Each subagent entry below explicitly justifies its `model:` and `effort:` choices.

### `execute-orchestrator`

**Trigger**: User (or lead agent) invokes when entering the execution phase of the pipeline after Plan Authoring + Acceptance Test Authoring + Phase Validator Authoring stages complete. Reads `tasks.json` (output of `finalize-task-decomposer`) + acceptance tests + phase validators. Drives the full execution-phase state machine.

**Tools**: `[Read, Glob, Grep, Bash, Task, TaskUpdate]`. Read for inputs; Bash for invoking auditing scripts + test scripts; Task for delegating to other subagents (code-producer, quality-handler, phase-quality-reviewer, finalize-reconciler); TaskUpdate for task-state transitions. Does NOT have Write — does not author files itself; delegated subagents do that.

**Skills**: `[KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]`. KB-cc-platform/design for primitive knowledge; recipe-feature-pipeline for the discipline statements being enforced; auditing-shared for FR-6 validator + (per D-15 if option 2 taken) the discipline-check invocation; KB-review-disciplines for understanding what phase-quality-reviewer applies.

**Memory**: `project`. The orchestrator tracks reconciliation cycle counts across invocations within a feature run — that state needs to persist when control transfers between subagent calls. Project scope is correct (per-feature; not per-user).

**Reasoning configuration**:
- `model: opus` — cross-cutting orchestration that arbitrates between multiple specialized agents' outputs is exactly the case KB-cc-design Principle 9 identifies as opus. Mirrors planning-side `finalize-reconciler` choice.
- `effort: high` — state-machine correctness is high-stakes; mistakes here cascade. The state space is large (task selection, gate transitions, reconciliation tracking, hook invocation timing).

**Expected output shape**: orchestration does not produce a primary artifact; it produces side effects (subagent invocations + tasks.json state mutations + state-transitions.log entries per D-16) and a final `pipeline-run-summary.json` per FR-7 when the execution phase completes.

**Hard caps owned by orchestrator (per D-12)**:
- **Per-task quality loop cap**: 4 cycles. The orchestrator iterates `code-producer → quality-handler` up to 4 times; cycle 4 is terminal (escalate `TASK_QUALITY_EXHAUSTED` to user). Discipline 3 symmetric application.
- **Phase-level reconciliation cap**: 4 cycles. The orchestrator iterates `phase-quality-reviewer → finalize-reconciler → re-invoke → re-review` up to 4 times; cycle 4 is terminal. The orchestrator increments the counter; finalize-reconciler checks against cap. Direct analog of planning-side ADR-0017.

**State-transition hook invocation (per D-16)**: at each procedural transition point in the orchestrator, invoke `auditing-shared/scripts/log_state_transition.py` with transition payload (JSON via stdin). Transitions to log:

| Transition | from_state | to_state | trigger |
|---|---|---|---|
| Task start | `pending` | `producing` | orchestrator selects task from tasks.json |
| Code-producer completes | `producing` | `quality_checking` | code-producer returns COMPLETED |
| Quality-handler approves | `quality_checking` | `done` | quality-handler returns APPROVED |
| Quality-handler needs revision | `quality_checking` | `producing` | quality-handler returns NEEDS_REVISION (cycle counter incremented) |
| Per-task cap reached | `producing` | `escalated_task_quality` | cycle 4 NEEDS_REVISION |
| Stub detected | `quality_checking` | `escalated_stub` | quality-handler returns STUB_DETECTED |
| Phase complete | `done_n_of_n` | `phase_quality_check` | all phase tasks done |
| Phase-quality pass | `phase_quality_check` | `phase_complete` | reviewer verdict PASS |
| Phase-quality needs reconciliation | `phase_quality_check` | `reconciling` | reviewer verdict NEEDS_RECONCILIATION |
| Reconciliation cycle complete | `reconciling` | `phase_quality_check` | reconciler dispatches; re-execution + re-review (cycle counter incremented) |
| Phase reconciliation exhausted | `reconciling` | `escalated_phase_reconciliation` | cycle 4 reconciliation |
| Phase-quality blocker | `phase_quality_check` | `escalated_phase_blocker` | reviewer verdict BLOCKER |

The hook is observer-only in v1 (audit-log writes). Hook failure does NOT block the transition.

### `execute-phase-quality-reviewer`

**Trigger**: `execute-orchestrator` invokes at the end of a phase, after all phase tasks have completed their per-task quality loops. Reads structured outputs from: 3 test layers (unit/integration/E2E), 3 audit families (cc-audit / GHA audit / Codespaces audit), the FR-6 frontmatter validator, and (per D-15 if option 2) the discipline-check script.

**Tools**: `[Read, Glob, Grep, Bash, Write]`. Read for structured outputs; Bash for any aggregation scripts; Write to produce the `phase-quality-report.{json,md}` pair (per D-5, pair pattern). Does NOT have Task — does not delegate; performs aggregation directly. Does NOT have Edit/StrReplace — does not modify upstream artifacts.

**Skills**: `[KB-cc-design, KB-review-disciplines, auditing-shared]`. KB-cc-design for understanding what the audit families check; KB-review-disciplines for scoring rubric (per D-13 in Pass 3); auditing-shared for utility helpers.

**Memory**: none. Each phase-quality review is stateless; the orchestrator carries state.

**Reasoning configuration**:
- `model: opus` — verdict-issuing on phase quality is consistency-critical (the same set of inputs should always produce the same verdict). Opus's consistency favors this. An alternative argument for sonnet exists (the work is well-bounded: read N inputs, apply rubric, output verdict) — but verdict-issuing failures cascade into either false-negatives (ship broken work) or false-positives (block valid work), both expensive. Choosing opus.
- `effort: high` — rubric application is where the subtle calls happen.

**Expected output shape**: `phase-quality-report.json` (machine-parseable) + `phase-quality-report.md` (narrative for human review). Both per D-5's pair pattern (Pass 5).

**Verdict structure (per D-13)**: NOT numeric scoring. Dimensional verdict instead.

```json
{
  "verdict": "PASS | NEEDS_RECONCILIATION | BLOCKER",
  "per_dimension_status": {
    "tests": "PASS | NEEDS_RECONCILIATION | BLOCKER",
    "audits": "PASS | NEEDS_RECONCILIATION | BLOCKER",
    "validator": "PASS | NEEDS_RECONCILIATION | BLOCKER",
    "discipline": "PASS | NEEDS_RECONCILIATION | BLOCKER"  // if D-15 option 2 is taken
  },
  "findings": [
    {
      "domain": "tests | audits | validator | discipline",
      "severity": "blocker | major | minor | info",
      "source_activity": "unit | integration | e2e | cc-audit | gha-audit | codespaces-audit | frontmatter-validator | discipline-check",
      "file_path": "<path>",
      "message": "<finding description>",
      "dispatch_hint": "<upstream stage suggestion for finalize-reconciler>"
    }
  ]
}
```

Rollup rule: blocking finding in any dimension → overall BLOCKER; revisable in any dimension → overall NEEDS_RECONCILIATION; all clean → overall PASS.

**Audit-counter delta (per D-17 / FR-12)**: report includes:

```json
{
  "audit_counter_delta": {
    "baseline_type": "feature_start | prior_phase",
    "primary_baseline": "feature_start",
    "feature_start": {
      "per_domain": { "tests": "N1→N2", "audits": "N3→N4", ... },
      "aggregate": "N5→N6"
    },
    "prior_phase": {
      "per_domain": { ... },
      "aggregate": "N7→N8"
    },
    "gating": "informational | gating",  // default informational; intent-clarification feature config can elevate
    "gating_rule": null  // populated if gating=true; e.g., "FAIL if audits_aggregate delta > 0"
  }
}
```

[Future-feature scope: severity-weighted aggregation. Current scope per-domain + aggregate raw counts only — over-engineering deferred per Q-CC-N entry below.]

### `execute-finalize-reconciler`

**Trigger**: `execute-orchestrator` invokes when `execute-phase-quality-reviewer` returns a verdict containing dispatchable findings (findings that warrant revision of upstream stages). Walks the dispatch taxonomy (per D-14) to determine which upstream stage each finding routes to.

**Tools**: `[Read, Glob, Grep, Task, Write]`. Read to inspect findings; Task to dispatch revisions to upstream-stage agents (e.g., re-invoke `execute-task-code-producer` for a specific task, or re-invoke phase-quality-reviewer for re-evaluation after revisions); Write to author the `quality-reconciliation-log.{json,md}` per D-5.

**Skills**: `[KB-cc-design, KB-review-disciplines, auditing-shared]`. Symmetric with phase-quality-reviewer's skill set; the reconciler reads the same artifacts and applies a complementary discipline (dispatch rather than aggregate).

**Memory**: `project`. Cycle-count state shared with `execute-orchestrator` (the orchestrator increments; the reconciler reads to check against cap).

**Reasoning configuration**:
- `model: opus` — direct analog of planning-side `finalize-reconciler` (opus, high). Cross-cutting reconciliation pattern.
- `effort: high` — finding-to-stage dispatch decisions are precedent-shaping. A wrong dispatch wastes a reconciliation cycle.

**Dispatch taxonomy (per D-14)**:

| Finding domain | source_activity | Dispatch target | Revision context payload |
|---|---|---|---|
| tests | unit / integration / e2e | `execute-task-code-producer` (for the task whose surface failed) | failing tests + expected behavior + original task spec |
| audits | cc-audit | code-producer (if file in current task scope) OR escalate-to-user (if existing-defect outside scope) | audit finding + file context |
| audits | gha-audit | code-producer (if .github/ files in scope) OR escalate-to-user | audit finding |
| audits | codespaces-audit | code-producer (if devcontainer/ files in scope) OR escalate-to-user | audit finding |
| validator | frontmatter-validator | the agent that authored the malformed artifact (code-producer / phase-quality-reviewer / etc.) | validator output + artifact path |
| discipline | discipline-check (if D-15 option 2) | the agent that committed the violation | discipline finding + artifact path |
| stub | (directly returned by quality-handler; no reconciler involvement in v1) | n/a | n/a |

**Scope-bounded dispatch (edge case discipline)**: when an audit finding is on a file NOT in the current task's scope (existing defect surfaced by broader-scope audit), the reconciler does NOT auto-dispatch a fix. It surfaces to user as `existing_defect_outside_scope`. Auto-dispatching would expand execution work to fix legacy issues — out of scope per FR-4's discipline-bounded reconciliation.

**Multi-findings-on-one-artifact**: consolidated re-invocation. The reconciler groups findings by `(target_agent, target_artifact)` tuples; single re-invocation with all findings in revision context. Avoids redundant re-execution.

**Hard cap (per D-12)**: 4 reconciliation cycles per phase. Counter increments on each dispatch round; cycle 4 is terminal — finalize-reconciler returns `RECONCILIATION_EXHAUSTED` and orchestrator escalates to user. Symmetric with planning-side ADR-0017 hard cap.

**Expected output shape**: `quality-reconciliation-log.json` + `quality-reconciliation-log.md` pair per D-5. JSON carries per-cycle dispatch records (cycle_number + dispatched_findings + dispatched_targets); MD narrates per-cycle progression. Final entry per cycle includes either `CONVERGED` (no findings on re-review) or `RECONCILIATION_EXHAUSTED` (cap reached).

### `execute-task-code-producer`

**Trigger**: `execute-orchestrator` invokes per-task. Receives task spec (from `tasks.json`) + acceptance criteria + relevant context files. Produces code changes to satisfy the task spec.

**Tools**: `[Read, Glob, Grep, Write, Edit, Bash]`. Read/Glob/Grep for understanding context; Write/Edit for code changes; Bash for running individual commands during development (not for full quality checks — those belong to quality-handler). Does NOT have Task — does not delegate; the orchestrator coordinates the loop.

**Skills**: `[ai-development-guide, KB-cc-design]` plus any language-specific or domain-specific skills declared in the task spec. `ai-development-guide` per D-11 binding; KB-cc-design for design discipline awareness during code authoring. Skill set kept tight (anti-pattern: subagent listing 15 skills).

**Memory**: none. Each task invocation is stateless; the orchestrator carries cross-task state.

**Reasoning configuration**:
- `model: sonnet` — bounded transformation (one task, defined acceptance criteria, defined test surface). KB-cc-design Principle 9 explicitly identifies sonnet as the right model for bounded transformations. Opus would be wasteful here unless the task spec itself indicates unusual complexity (rare; orchestrator could escalate to opus per-task in that case — open question Q-CC-1 below).
- `effort: medium` — code production within bounded scope; not multi-artifact arbitration. High would be over-allocated for routine task execution.

**Selective BLOCKING annotations (per D-2a)**: the agent prompt includes BLOCKING-style gates only for safety-critical checkpoints: (a) before declaring task complete, the agent MUST verify all files referenced in the task spec exist and are populated (no empty stubs left behind); (b) before declaring complete, the agent MUST confirm any new tests required by ACs have been authored. These two are BLOCKING. Other procedure steps are prose-style, matching the planning-side agent pattern.

**Expected output shape**: a `task-execution-result.json` written to the task's working location (per FR-7 pair pattern via D-5 in Pass 5). Schema: `task_id`, `status` (proposed: COMPLETED / INCOMPLETE / BLOCKED), `files_modified` (list of paths), `tests_authored` (list of paths), `notes` (prose), `escalation` (optional structured field if status != COMPLETED).

### `execute-task-quality-handler`

**Trigger**: `execute-orchestrator` invokes after `execute-task-code-producer` returns a COMPLETED result. Reads the modified files + new tests; runs the code-level quality pipeline.

**Tools**: `[Read, Glob, Grep, Bash]`. Read for inputs; Bash for invoking detect_stubs.py + lint + test commands. Does NOT have Write or Edit — does not modify code; only evaluates. (If revision is needed, control returns to orchestrator which re-invokes code-producer with finding context.)

**Skills**: `[ai-development-guide, KB-cc-design, auditing-shared]`. ai-development-guide per D-11; KB-cc-design for context; auditing-shared for the detect_stubs.py invocation pattern and other shared utilities.

**Memory**: none.

**Reasoning configuration**:
- `model: sonnet` — bounded transformation (read N files, run M commands, aggregate verdict). Mostly mechanical with judgment on the APPROVED-vs-NOT classification. Sonnet handles this consistently.
- `effort: medium` — verdict-issuing requires care but not opus-level. High effort would be over-allocated.
- **However**, see Q-CC-1 below: there's an argument for opus/high on the verdict-classification step. If the classification surfaces as a frequent error source in early operation, model upgrade is the natural lever.

**Selective BLOCKING annotation (per D-2a)**: one BLOCKING gate at procedure start — "BLOCKING: Run detect_stubs.py first; if stubs found, return STUB_DETECTED immediately. Do NOT proceed to quality checks." This makes the silent-success failure mode mechanically prevented.

**Status enum (per D-2c)**: agent returns JSON with `status` field taking values:
- `APPROVED` — all quality checks pass; no stubs; no test failures; no lint errors above threshold.
- `NEEDS_REVISION` — quality checks identify revisable findings (failing test on the task's surface; lint errors). Orchestrator re-invokes code-producer with findings context. Loop continues.
- `STUB_DETECTED` — detect_stubs.py found incomplete-implementation patterns. Returned BEFORE running tests/lint. Orchestrator escalates immediately; does NOT loop on this status (the code-producer's expected output should not have stubs; this is a contract violation).
- `BLOCKER` — quality findings exceed revisable scope (e.g., test failures in unrelated code; environment misconfiguration; external service dependency). Orchestrator surfaces to user.

**Expected output shape**: a `quality-check-result.json` written to the task's working location. Schema: `task_id`, `status` (enum above), `stub_findings` (list, may be empty), `lint_findings`, `test_results` (per language), `notes`, `next_action` (suggested orchestrator action).

## Hook patterns

### FR-5 state-transition hooks — implementation note

**Important clarification (Q-CC-5)**: FR-5's "state-transition hooks" are **application-level**, not Claude Code platform-level. Claude Code's platform hooks (PreToolUse / PostToolUse / SessionStart / Stop / etc.) fire on tool invocations and session lifecycle events. The execution pipeline's state transitions (task→quality-handler, quality-handler→code-producer-revision, phase-quality→reconciliation, etc.) are application-level events the orchestrator agent owns.

Implementation: the orchestrator invokes a hook script at each transition point in its procedure. Pattern:

```
At transition point in orchestrator procedure:
  1. Construct transition payload JSON (transition_name, from_state, to_state, task_id, phase_id, artifact_paths_affected, invoking_agent, timestamp)
  2. Invoke `auditing-shared/scripts/log_state_transition.py` with payload as stdin
  3. Await script completion (synchronous; script is fast)
  4. If script errors, log warning but proceed (hook is observer, not blocker)
  5. Proceed with the substantive transition work
```

**Why not platform hooks**: platform hooks fire on tool calls; the transitions FR-5 cares about happen in the orchestrator's procedural logic between tool calls. Trying to encode application-level transitions as platform hooks would require either (a) instrumenting every tool call as a transition (high false-positive rate; tools fire many times per task), or (b) using a sentinel tool call to signal transitions (hacky; not what platform hooks are for). Application-level hook is the right shape.

### Hook contract (D-16 resolution)

**Trigger semantics**: hooks fire on ALL state transitions (not just gate passes). Forward, backward, gate-pass, gate-fail, escalation all trigger. Default informational (audit-log purposes); the hook contract permits future extensions but v1 is observation-only.

**Inputs (JSON payload via stdin)**:

```json
{
  "transition_name": "string (e.g., 'task_completed_to_quality_check', 'phase_quality_pass', 'reconciliation_dispatch')",
  "from_state": "string (state machine state)",
  "to_state": "string",
  "task_id": "string|null (if per-task transition)",
  "phase_id": "string|null (if phase-level transition)",
  "artifact_paths_affected": ["<path1>", "<path2>"],
  "invoking_agent": "string (which agent triggered the transition)",
  "timestamp": "ISO 8601 string"
}
```

**Outputs**: void. The script returns exit code 0 on success; non-zero codes log warnings but do NOT block transitions. Hook failure is a warning, not a blocker — the transition has already occurred logically; the hook observes.

**Synchronicity**: synchronous. Orchestrator awaits hook completion before proceeding. Script is fast (file-append operation); blocking briefly prevents log-write-out-of-order.

**Output destination**: append-only JSONL log at `working/feature/<feature-slug>/state-transitions.log`. Each transition is one line. Machine-parseable for downstream consumers (audit-counter delta computation could potentially consume this; future feature).

### Hook script (new entry in Inventory)

| Path | Purpose | Caller | Per |
|---|---|---|---|
| `.claude/skills/auditing-shared/scripts/log_state_transition.py` | Append a JSONL transition record to the feature's state-transitions.log. Reads JSON payload from stdin; writes one line to `working/feature/<slug>/state-transitions.log`. Idempotent within a single transition (timestamps in record body; no dedup at script level — orchestrator is responsible for invoking once per transition). | `execute-orchestrator` at transition points | D-16, FR-5 |
| `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` | Frontmatter validator per FR-6. Scans pipeline documents against the per-doc-type frontmatter spec (canonicalized in `shared-conventions.md` per D-4); reports missing required fields, invalid state values per D-18 per-doc-type vocabulary, broken `derived_from` paths. Returns JSON findings consumed by `run_phase_checks.py`. | `run_phase_checks.py` (validator-domain dispatch) | FR-6, D-4, D-18, ADR-0031 |
| `.claude/skills/auditing-shared/scripts/check_pipeline_discipline.py` | Discipline-5 enforcement per D-15 (v1 worked example). Body-prose scan of pipeline documents for stage-by-number references (`\bStage[ -]?[0-9]+\b` patterns, excluding amendment_log/revision_reason quotation contexts per OBS-PLAN-001 precedent). Architected for extensibility: function-per-discipline pattern permits future additions for disciplines 1, 2, 4. v1 ships discipline 5 only. | `run_phase_checks.py` (discipline-domain dispatch) | D-15, ADR-0030 symmetric, ADR-0031 |

[All scripts inventoried; Pass 5 adds 2 (validator + discipline-check). Finalize batch may identify additional minor scripts as agent procedures are detailed in Plan-stage.]

### Permission policy addition

Per Permission policy section above, append to allow list:

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 .claude/skills/auditing-shared/scripts/log_state_transition.py:*)"
    ]
  }
}
```

### Platform-hook scope (no FR-5 use)

For completeness: Claude Code platform hooks (PreToolUse / PostToolUse / etc.) are NOT used by this feature. No `.claude/settings.json` hooks block; no hook scripts in `.claude/hooks/`. The execution pipeline operates entirely within agent procedures + scripts invoked from those procedures.

## Permission policy

Per KB-cc-design Principle 6 (permissions are the safety net, not the design). The execution pipeline requires Bash for invoking test runners + audit scripts + the phase-checks coordinator. The permission policy scopes Bash narrowly to known-safe entry points and uses ask/allow defaults responsibly.

### Recommended additions to `.claude/settings.json` permissions

These are recommendations for the project's settings.json; this design subsection documents the policy, not the literal file edit (that's Plan-stage).

**Allow list extensions** (for routine execution-pipeline operation):

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 .claude/skills/auditing-shared/scripts/run_phase_checks.py:*)",
      "Bash(python3 .claude/skills/auditing-shared/scripts/detect_stubs.py:*)",
      "Bash(python3 .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py:*)",
      "Bash(python3 .claude/skills/auditing-shared/scripts/check_pipeline_discipline.py:*)",
      "Bash(python3 .claude/skills/auditing-shared/scripts/log_state_transition.py:*)",
      "Bash(python3 .claude/skills/auditing-cc-configs/scripts/*:*)",
      "Bash(python3 .claude/skills/auditing-github-actions/scripts/*:*)",
      "Bash(python3 .claude/skills/auditing-codespaces/scripts/*:*)"
    ]
  }
}
```

**Test runner allow** (project-specific; documented here as a class):

Test runner commands (pytest / vitest / cargo test / etc.) need allow entries. Specific commands are language-dependent and authored at Plan-stage when the project's test infrastructure is known. The policy: test runner invocations are allow-listed per command pattern; never `Bash(*)` (anti-pattern: "permissions.allow: [Bash(*)]").

**Deny list considerations**:

No new deny rules are needed for this feature. The existing project deny list (if any) continues to apply.

### Permission-policy discipline notes

Per Principle 3 (enforce when safety-critical; instruct when guidance-critical):
- The coordinator script + auditing scripts are READ-mostly (Read + Bash for sub-process spawning). Allow without `ask` is appropriate.
- The orchestrator's `Task` tool (delegating to subagents) does not need explicit permission allow (built into the platform).
- The hook implementation (Pass 4) MAY introduce additional permission considerations depending on what the hook does.

[Pass 4 will revisit if FR-5 hook implementation requires permission policy changes.]

## MCP server policy

**No new MCP servers introduced by this feature.**

Rationale: this feature's scope is internal execution-pipeline tooling — agents, skills, scripts that run locally in the Claude Code session. No external services are integrated. The existing project MCP configuration (whatever it is at the project level) is unchanged.

If future execution-pipeline features need external integration (e.g., a CI status checker, a test-result aggregator running outside Claude Code), MCP would be the right shape per KB-cc-design Principle 1 (lowest-cost primitive for external service connection). Out of scope for this feature.

## Plugin packaging

**No plugin packaging for this feature.**

Per KB-cc-design Principle 7: plugins are for cross-project distribution, not for organization within a project. This feature's artifacts (5 agents, 3 skills, 7 scripts) serve THIS project's execution pipeline; they are not shared across projects. Plugin packaging would add overhead without benefit.

All artifacts ship as direct `.claude/` commits.

If a future need arises to distribute the execution-pipeline tooling to other projects (e.g., an Anthropic-internal pattern catalog of feature-pipeline implementations), plugin packaging is the right mechanism. Out of scope for this feature.

## Command-to-skill migration

**No legacy commands in scope for this feature; no migration work.**

Per IN-001 Batch A finding: there are no `.claude/commands/*.md` files for the execution-pipeline domain. The pipeline orchestration this feature introduces is a new capability, not a migration from existing commands.

If, during execution-pipeline implementation, any pattern emerges that would benefit from a user-invocable shortcut (e.g., `/run-execution-phase` as a wrapper for invoking `execute-orchestrator`), a skill with `disable-model-invocation: true` would be the right shape per KB-cc-design Principle 8 — NOT a `.claude/commands/` entry. Plan-stage discretion if such a shortcut is needed.

## Acceptance criteria contribution

This feature is single-layer (Claude Code only). All 13 FRs' acceptance criteria are CC-layer obligations. The table below maps each FR to the design elements that satisfy its ACs.

| FR | Design elements satisfying ACs | Key AC mappings (illustrative; not exhaustive) |
|---|---|---|
| FR-1 (named execution stages with gates) | `execute-orchestrator` 12-row transition table; named gates (PASS / NEEDS_RECONCILIATION / BLOCKER per phase); D-6 + D-9 + D-10 joint architectural-shape | AC-FR-1-a: each pipeline stage has a named identifier (transition_name in hook payload). AC-FR-1-b: each gate has a named verdict ({APPROVED, NEEDS_REVISION, STUB_DETECTED, BLOCKER} per-task; {PASS, NEEDS_RECONCILIATION, BLOCKER} per-phase). |
| FR-2 (per-task code/test/review/refactor loop with quality gates) | `execute-task-code-producer` + `execute-task-quality-handler` multi-agent loop (D-8); status enum (D-2c); selective BLOCKING annotations (D-2a); per-task 4-cycle hard cap (D-12); stub detection (D-2d) | AC-FR-2-a: per-task loop exists. AC-FR-2-c: hard cap on iterations (4 cycles symmetric with planning-side). AC-FR-2-other: stub detection before quality checks. |
| FR-3 (phase-quality stage invokes 7 activities) | `execute-phase-quality-reviewer` + `run_phase_checks.py` coordinator; hybrid finding-organization (D-1); dimensional verdict structure (D-13); third-option invocation model (D-3) | AC-FR-3-a: phase-quality stage exists per phase. AC-FR-3-b: 7 activities invoked (3 test layers + 3 audit families + 1 frontmatter validator) — extended to 8 if D-15 option 2 ships discipline-check. |
| FR-4 (FR-4 dispatch reconciliation) | `execute-finalize-reconciler` with 6-row dispatch table (D-14); scope-bounded edge case discipline; multi-finding consolidation; phase-level 4-cycle hard cap (D-12) | AC-FR-4-a: reconciler dispatches findings to upstream stages. AC-FR-4-b: hard cap on reconciliation cycles. |
| FR-5 (state-transition hooks fire at gates) | `log_state_transition.py` script + application-level hook invocation procedure in orchestrator; D-16 contract; JSONL log destination | AC-FR-5-a: hooks fire at each named transition. AC-FR-5-other: hook output is machine-parseable (JSONL). |
| FR-6 (frontmatter validator) | `validate_pipeline_frontmatter.py` script per AC-FR-6-c; FR-6 scope kept clean (frontmatter only; D-15 separated body-prose discipline checks into separate script) | AC-FR-6-a: validator exists at canonical location. AC-FR-6-c: validator location is `auditing-shared/scripts/` (foregone under ADR-0031). |
| FR-7 (execution-phase artifacts with machine-parseable format) | Pair pattern (.json + .md) for: per-task-execution-result, quality-check-result, phase-quality-report, quality-reconciliation-log (D-5). State-transitions.log is JSONL (separate category). | AC-FR-7-c: artifact floor (5+; expansion to 9-11 surfaced for Blueprint per OBS-EXEC). AC-FR-7-d: machine-parseable component for each artifact (JSON half of pair). |
| FR-8 (3-way audit split) | `auditing-github-actions` skill extracted from KB-github-actions-platform (per IN-002); `auditing-codespaces` stub created (AC-FR-8-b); `run_phase_checks.py` coordinator invokes both alongside existing `auditing-cc-configs` | AC-FR-8-a: GHA audit lives at canonical auditing- location. AC-FR-8-b: Codespaces audit stub exists. |
| FR-9 (code-producing subagents bind to ai-development-guide) | `ai-development-guide` skill install (AC-FR-9-e); D-11 boundary defines binding (code-producer + quality-handler bind; orchestrator + reviewer + reconciler do not) | AC-FR-9-e: skill installed at canonical CC location. AC-FR-9-other: each code-producing subagent's `skills:` list includes `ai-development-guide`. |
| FR-10 (orchestrator manages reconciliation budget) | `execute-orchestrator` increments cycle counter; `execute-finalize-reconciler` checks against cap; D-12 sets value (4); cap is hard (cycle 4 escalates to user) | AC-FR-10-a: budget tracked across reconciliation cycles. AC-FR-10-b: budget enforced (cycle 4 terminal). |
| FR-11 (canonical state vocabulary) | D-18 per-doc-type vocabulary; codified via ADR-A in Open items + `shared-conventions.md` updates | AC-FR-11-a: canonical vocabulary documented. AC-FR-11-b: each doc type's valid states enumerated. |
| FR-12 (phase-quality-report audit-counter delta) | `execute-phase-quality-reviewer` emits audit_counter_delta in phase-quality-report.{json,md}; D-17 contract (feature-start + prior-phase baselines; per-domain + aggregate; informational default with opt-in gating) | AC-FR-12-a: delta reported. AC-FR-12-other: baseline configurable. |
| FR-13 (machine-parseable reconciliation log) | quality-reconciliation-log.json half of D-5 pair; per-cycle dispatch records | AC-FR-13-a: log is machine-parseable (JSON). AC-FR-13-b: per-cycle structure preserves dispatch history. |

**Cross-FR enforcement mechanisms** (not tied to a single FR):
- Discipline 5 mechanical enforcement via `check_pipeline_discipline.py` (D-15 v1 worked example).
- Discipline 3 mechanical enforcement via cycle-counter checks (already exists; extended to per-task per D-12).
- Frontmatter spec canonicalization (D-4 + D-18 via ADR-A) — backstop ensuring validator (FR-6) has a clear spec to validate against.

**Plan-stage AC verification responsibility**: detailed AC text and verification procedures are authored at Plan-stage when test-acceptance-author runs. This cc-design section establishes WHICH design elements satisfy each FR; the specific AC text + verification commands are downstream work.

## Dependencies on other layers

This feature is **single-layer** per PRD Layer Scope. The Claude Code layer is the only activated layer; no other per-layer designers fire; no cross-layer integration design is needed.

### Cross-layer dependency declarations (formal record)

| Dependency direction | Other layer | Status |
|---|---|---|
| `depends_on` | CI/CD | None — no CI integration in scope |
| `depends_on` | MCP servers | None — no MCP server introduced (see MCP server policy section) |
| `depends_on` | External services | None |
| `provides_to` | CI/CD | None — execution pipeline runs in local Claude Code session, not in CI |
| `provides_to` | Other layers | None — pipeline is internal tooling for this project |

### Inter-component dependencies (within CC layer)

Substantial; relevant for Plan-stage task ordering. Not strictly "other-layer dependencies" but documented here to preserve the dependency-trace audit:

| Component | Depends on | Notes |
|---|---|---|
| `execute-orchestrator` | `tasks.json` (existing output of planning-side `finalize-task-decomposer`) + the 4 invoked subagents (code-producer, quality-handler, phase-quality-reviewer, finalize-reconciler) + `auditing-shared` skill family + `recipe-feature-pipeline` skill | Lead component; cannot run until all dependents exist |
| `execute-task-code-producer` | `ai-development-guide` skill (must be installed first) + `KB-cc-design` | Depends on ai-development-guide install timing |
| `execute-task-quality-handler` | `ai-development-guide` + `auditing-shared` + `detect_stubs.py` | Depends on ai-development-guide install + detect_stubs.py existence |
| `execute-phase-quality-reviewer` | `auditing-shared` + `run_phase_checks.py` + `KB-review-disciplines` | Depends on run_phase_checks.py existence |
| `execute-finalize-reconciler` | `auditing-shared` + `KB-review-disciplines` + `KB-cc-design` | Symmetric with phase-quality-reviewer dependencies |
| `run_phase_checks.py` | `auditing-cc-configs` (existing) + `auditing-github-actions` (must be extracted from KB-github-actions-platform first) + `auditing-codespaces` (must be stub-created first) + `validate_pipeline_frontmatter.py` + (optionally per D-15) `check_pipeline_discipline.py` | Coordinator depends on all dispatchees |
| `validate_pipeline_frontmatter.py` | `shared-conventions.md` (must be updated per ADR-A first) | Spec must precede validator |
| `check_pipeline_discipline.py` | (none — leaf) | Standalone discipline-5 check |
| `detect_stubs.py` | (none — leaf) | Standalone stub detection |
| `log_state_transition.py` | (none — leaf) | Standalone JSONL append |
| `ai-development-guide` skill install | (source upload at `/mnt/user-data/uploads/SKILL__2_.md`) | One-time install |
| `auditing-github-actions` skill | Existing `KB-github-actions-platform/scripts/audit_workflow.py` + `references/action_versions.md` (must be moved, not copied, to preserve git history) | Migration with git mv |
| `auditing-codespaces` stub | (none) | Net-new stub |
| `shared-conventions.md` updates | ADR-A authoring (Blueprint-stage) | Spec update follows ADR proposal |
| `shared-document-reviewer` doc_type extension | ADR-A's doc_type taxonomy decision | Modification follows ADR |

The cc-dependencies.json sidecar codifies this dependency graph in machine-readable form (Plan-stage input).

## Architectural Questions for Composer (Q-CC-N)

Five architectural questions surfaced across Passes 2-4 for design-composer to resolve when composing the Blueprint. Each is summarized below; full context is in the pass-by-pass resolution audit trail at the bottom of this document.

### Q-CC-1: Quality-handler model/effort allocation

The verdict-classification step (APPROVED / NEEDS_REVISION / STUB_DETECTED / BLOCKER) requires judgment that may not always be cleanly sonnet-bounded. Initial choice is `model: sonnet, effort: medium` per Principle 9's bounded-transformation framing. Alternatives:
- `model: opus, effort: high` — over-allocated for routine cases; potentially right when verdict-classification edges are subtle
- Hybrid — sonnet by default; orchestrator escalates uncertain verdicts to opus re-invocation

Composer should choose between "sonnet/medium with optional opus escalation as configuration" vs. "opus/high uniform." First operation may surface evidence; conservative choice (sonnet) is reversible cheaply.

### Q-CC-2: detect_stubs.py path-awareness

Should `detect_stubs.py` scan test files as well as implementation files? Test files have legitimate use of `pass` (placeholder bodies during exploration); but a test file containing only `// TODO: actually test this later` IS structurally a stub.

Options:
- Scan all files matching task's modified-files list (uniform; treats test files same as impl files)
- Path-filter to exclude test files (lenient on placeholder patterns)
- Path-filter with separate test-file stub patterns (heavier; more accurate)

Composer to resolve based on project's testing culture.

### Q-CC-3: Severity-weighted audit-counter aggregation

Current resolution defers severity-weighted aggregation to future feature (per D-17). Per-domain breakdown is the primary signal; aggregate-total is a raw count.

Concern: 100 minor findings + 1 blocker aggregates to "101 findings, delta +1" — misleading when the blocker is the operational signal.

Composer to consider: is v1 sufficient (per-domain breakdown surfaces blockers in the right column), or should severity-weighted aggregation ship in v1 (additional computation; small implementation cost)?

### Q-CC-4: auditing-codespaces stub semantics

The stub returns `{"findings": []}`. Downstream consumers count "0 findings" — indistinguishable from "ran cleanly, no findings."

Options:
- Stub script declares `{"stub": true, "findings": []}` — downstream can treat differently
- No declaration — phase-quality-report shows "no codespaces findings" identical to a passing real audit

Composer to decide based on whether the stub-vs-real distinction matters for verdict-issuing or audit-counter computation.

### Q-CC-5: Platform-hooks vs application-hooks (FR-5 terminology)

FR-5's "hooks" terminology overloads with Claude Code platform hooks (PreToolUse / PostToolUse / etc.). This design resolved the ambiguity to application-level hooks (orchestrator-invoked scripts at transition points).

Composer should consider:
- Is the FR-5 phrasing in the PRD likely to mislead Plan-stage readers?
- Should cc-design.md introduce a renaming (e.g., "state-transition log invocations") OR keep FR-5 terminology with inline disambiguation?

Current cc-design takes the latter (keep terminology + disambiguate inline). Composer should sanity-check; if renaming is preferred, propagate through Blueprint and any downstream artifacts.

## Open items

This section consolidates items requiring resolution outside the cc-design.md authoring scope. Items are grouped by who owns the resolution.

### New ADRs to be authored (Blueprint-stage work; designers don't author ADRs per FR-5)

**ADR-A: Convention canonicalization + per-doc-type state vocabulary** (pairs D-4 + D-18)

- Author scope: `shared-conventions.md` updates + new ADR documenting the canonicalization decision
- Content:
  - Add 4 archive-practice fields to canonical frontmatter spec: `intent_user_token` (PRD + ResearchPlan), `gate_passed` (all gated artifacts), `reviewer_verdict` (artifacts passing through reviewer), `approved_at` (paired with reviewer_verdict)
  - Extend doc_type taxonomy in `shared-document-reviewer`: add `Synthesis`, `CodebaseAnalysis`, `PhaseQualityReport`, `PerTaskExecutionLog`, `QualityReconciliationLog`, `StateTransitionsLog`
  - Per-doc-type state vocabulary (per D-18 option 3):
    - **Gated artifacts** (PRD, ResearchPlan, Plan, Blueprint, AcceptanceTest, PhaseValidator, DeliverableArchive): `draft, proposed, accepted, superseded, rejected`
    - **Analysis/log artifacts** (Synthesis, CodebaseAnalysis, PhaseQualityReport, PerTaskExecutionLog, QualityReconciliationLog): `draft, complete, superseded`
    - **ADRs**: `proposed, accepted, superseded, rejected` (no `draft`)
    - **State-transitions.log**: JSONL event log; no state field
- Rationale: archive practice was empirically validated; spec catches up to practice (archive-authoritative direction).
- Authoring sequence: ADR proposes; user reviews; ADR accepted; `shared-conventions.md` updated to reflect canonical spec; FR-6 validator (Pass 5 inventory entry above) reads the updated spec.

**ADR-B: ADR-0029 execution-phase extension** (D-7)

- Author scope: new ADR extending ADR-0029's per-stage Scope-Deviation surfacing table with execution-phase rows
- Content:
  - Per-task → `per-task-execution-log.{json,md}` Scope-Deviation entries
  - Phase-quality → `phase-quality-report.{json,md}` Scope-Deviation entries (analog of planning-side `observations.md` per OBS-EXEC entries)
  - Quality-reconciliation → `quality-reconciliation-log.{json,md}` Scope-Deviation entries
- Substrate: ADR-0029's own Forward Implications section explicitly anticipated this; this ADR closes that forward-looking commitment.
- Could be paired with ADR-A or authored independently; Blueprint discretion.

**ADR-C: ADR-0017 vs ADR-0021 mis-credit cleanup**

- Author scope: minor amendment to PRD v1.1.0 (or note in ADR-A) acknowledging that the 4-cycle cap's canonical home is ADR-0017 (not ADR-0021 as PRD v1.1.0 informally credited). Codebase-analysis.md v1.1.1 already corrected its in-table caption; this is the deferred PRD-narrative correction.
- Low-stakes; could be folded into ADR-A's housekeeping or stand alone.

### Systematic discipline-enforcement inventory (D-15 broadened scope; Blueprint-stage)

| Discipline | Statement | Current enforcement | This feature ships | Future-feature scope |
|---|---|---|---|---|
| 1 | No stage advance without gate pass | Procedural (per-agent prompt) | No change | Add mechanical gate-pass check before agent invocation |
| 2 | No ADRs from non-design-composer | Procedural | No change | Add hook/permission enforcing ADR write origin |
| 3 | 4-cycle cap | Mechanical (`finalize-reconciler`) | Extend to per-task quality loop (D-12 Pass 4) | None |
| 4 | No silent GitNexus fallback | Field-recording (`extraction_method`); validation status unclear | No change | Add validator confirming `extraction_method` populated when fallback occurred |
| 5 | No pipeline-stage references by number | None | `check_pipeline_discipline.py` (v1) | Generalize to other disciplines via function-per-discipline pattern |

Blueprint should explicitly approve the v1 scope (discipline 5 only) and document the future-feature roadmap.

### Skill installation prerequisites (Plan-stage sequencing)

- `ai-development-guide` skill install (per AC-FR-9-e) must precede `execute-task-code-producer` + `execute-task-quality-handler` agent prompts that reference the skill
- `auditing-github-actions` skill extraction (FR-8) must precede agent invocations that depend on the canonical location

### Architectural questions for composer (consolidated as Q-CC-N below)

See "Architectural Questions for Composer" section. Five questions surfaced across Passes 2-4.

### Synthesis substrate revisions (post-cc-design refinements)

Three material refinements of synthesis substrate emerged during cc-design authoring:

1. **D-9 role-split**: synthesis framed three options around "reviewer architecture as a single role"; actual answer is two roles (phase-quality aggregator + extended shared-document-reviewer). Pass 1 refinement.
2. **D-3 third option**: synthesis offered two options (extend auditing-cc-configs / 3 parallel); actual answer is third option (thin coordinator at auditing-shared per ADR-0031 canonical-home discipline). Pass 3 refinement.
3. **D-13 reframing**: synthesis framed as "scoring dimensions" (numeric); actual answer is dimensional verdict structure (per-domain status, no numeric scores). Pass 3 refinement.
4. **D-16 platform-vs-application clarification**: FR-5's "hooks" terminology overloaded with Claude Code platform hooks; resolved to application-level (orchestrator-invoked scripts). Pass 4 disambiguation.

These refinements should be noted in synthesis.md (future patch by future session); the cc-design.md resolutions are canonical answers.

### Existing-defect carry-forwards (from prior reviewer passes)

- `doc_type` taxonomy gap (instances noted in codebase-analysis.md + synthesis.md reviewer passes; closed by ADR-A above)
- `status: complete` vocabulary drift (closed by ADR-A's per-doc-type vocabulary)
- FR-7-c floor editorial expansion 5 → 9-11 artifacts per AC-FR-7-d (not yet addressed; flag for Blueprint cross-artifact-audit)

## Pass-by-pass resolution audit trail

This section accumulates "Pass N resolution summary" blocks as each pass completes. Provides the decision-to-subsection trace per the discipline of separating "what's the answer to each decision" from "where the answer is expressed in the Blueprint template structure."

### Pass 1 resolution summary

**Decisions resolved**: D-6, D-9 (with refinement), D-10 (partial — orchestrator + reviewer + reconciler; per-task agents deferred to Pass 2), D-8.

**D-6 — orchestration shape — RESOLVED**: centralized orchestrator agent. New subagent `execute-orchestrator` owns the execution-side state machine; delegates substantive work to specialized agents (per-task agents, phase-quality reviewer, finalize-reconciler). Synthesis option 2. Rationale: execution-side flow is non-linear (per-task loops, phase-quality aggregation, reconciliation with cycle caps, hook invocation at gate transitions); distributed orchestration doesn't naturally hold cycle counters or coordinate hook timing across stages. Centralized orchestrator naturally owns state-transitions (FR-1's "named gates") and reconciliation budget tracking (FR-4 + D-12).

**D-9 — execution-side reviewer architecture — RESOLVED with refinement**: synthesis option 1 (single agent + multiple modes) was the right direction but the framing didn't fit cleanly. Refinement: the role split into two — (a) **phase-quality aggregator** (new `execute-phase-quality-reviewer` agent) which reads structured outputs from N audit/test/validator invocations and issues a verdict; (b) **document review of execution artifacts** which is `shared-document-reviewer`'s existing role extended to new doc_types (per-task-execution-log, phase-quality-report, quality-reconciliation-log) via D-4 (Pass 5). The "modes" framing of synthesis option 1 doesn't apply because the aggregator and the document-reviewer have fundamentally different inputs (structured tool outputs vs. authored documents).

This refinement should be noted back to synthesis.md if future Blueprint-stage work re-reads the substrate; the decision was answered differently than the framing implied. **Open item**: revise synthesis D-9 framing or annotate the resolution here as the canonical answer.

**D-10 — agent inventory — PARTIAL (3 of N agents)**: this pass enumerates 3 new subagents (`execute-orchestrator`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`) plus 1 extended (`shared-document-reviewer`). Per-task agents are deferred to Pass 2 per D-2a-d. Audit-family scripts (FR-8 GHA + Codespaces stub) are deferred to Pass 3 per D-3 invocation model. Hook implementation is deferred to Pass 4 per D-16. Discipline-check script is deferred to Pass 5 per D-15. Final inventory count is the sum across all passes.

**D-8 — per-task loop topology — RESOLVED**: multi-agent loop. `execute-orchestrator` invokes code-producer → quality-handler iteratively until quality-handler returns APPROVED or hard cap is reached. Rationale: KB-cc-design Principle 4 ("isolate with subagents when isolation pays for itself") favors splitting; fresh context on the quality-handler side prevents code-investment drift; references task-executor + quality-fixer follow this split. The shapes of code-producer and quality-handler are D-2a-d (Pass 2). Hard cap value per D-12 (Pass 4).

**Subsections populated by this pass**:
- Layer responsibility scope (full)
- Inventory of CC primitives → Subagents (new) — 3 entries; Subagents (modified) — 1 entry
- Subagent patterns — 3 detailed entries with Principle 9 reasoning-configuration justifications

**Forward dependencies surfaced**:
- D-13 (Pass 3, scoring dimensions) constrains the rubric `execute-phase-quality-reviewer` applies
- D-14 (Pass 4, FR-4 dispatch taxonomy) constrains what `execute-finalize-reconciler` dispatches
- D-12 (Pass 4, reconciliation budget value) is the cap value both `execute-orchestrator` (for per-task quality loop hard cap, FR-2-c) and `execute-finalize-reconciler` (for phase-level reconciliation cycle cap, FR-4) check against
- D-15 (Pass 5, discipline enforcement) determines whether `execute-orchestrator` invokes an additional discipline-check script
- D-16 (Pass 4, state-transition hooks contract) determines whether the orchestrator's `tools:` array needs an additional capability or whether hooks fire from a Claude-Code-platform hook (PreToolUse / PostToolUse / Stop) outside the orchestrator's loop

**Pressure-test note**: the D-9 refinement (single-agent → role-split) is exactly the kind of "answer differently than the framing implied" outcome the pressure-test was warning against. This is honest progress, not a defect — but it does mean the synthesis's resolution recommendations carry less weight than the framings might suggest. Subsequent passes should treat resolution recommendations as defaults to be defended, consistent with the pre-flight anchoring note.

### Pass 2 resolution summary

**Decisions resolved**: D-2a, D-2b, D-2c, D-2d, D-11.

**D-2a — BLOCKING-gate annotations — RESOLVED**: selective BLOCKING annotations applied only to safety-critical gates (stub-detection check, file-existence verification, AC-test-authoring verification). Rejected the universal-BLOCKING-annotation pattern of task-executor reference; kept the procedural-prose style of planning-side agents elsewhere. This is the explicit task-executor-weight-reduction the synthesis anchoring concern flagged.

**D-2b — escalation taxonomy — RESOLVED**: one escalation gate, not a multi-category taxonomy. Status enum (per D-2c) carries category nuance in payload, not in named procedural steps. Rejected task-executor reference's 3+ named escalation steps as over-engineered for execution-side.

**D-2c — APPROVED status discipline — RESOLVED**: adopted with explicit enum. Status values: `APPROVED | NEEDS_REVISION | STUB_DETECTED | BLOCKER`. JSON contract documented in `execute-task-quality-handler` agent prompt and Subagent patterns section above. Direct adoption from quality-fixer reference; clean state-machine signal for orchestrator.

**D-2d — Stub detection — RESOLVED**: adopted; centralized as a shared script (`auditing-shared/scripts/detect_stubs.py`) per ADR-0031 canonical-helper home pattern. Quality-handler invokes the script FIRST, BEFORE any other quality checks; returns STUB_DETECTED if findings exist. Language-aware (auto-detects from file extension; takes language arg as override).

**D-11 — code-producing boundary — RESOLVED**: criterion is "an agent binds to `ai-development-guide` if it either authors code OR applies code-level quality gates to authored code." Two agents bind: `execute-task-code-producer` (authors) + `execute-task-quality-handler` (applies gates). Three agents do not: `execute-orchestrator` + `execute-phase-quality-reviewer` + `execute-finalize-reconciler` (none author code; none apply code-level quality directly — they coordinate, aggregate, dispatch).

**Subsections populated by this pass**:
- Inventory of CC primitives → Subagents (new) — 2 entries appended (code-producer + quality-handler)
- Inventory of CC primitives → Skills (new) — 1 entry (ai-development-guide install)
- Inventory of CC primitives → Scripts (new) — 1 entry (detect_stubs.py)
- Skill patterns — 1 entry (ai-development-guide install details)
- Subagent patterns — 2 entries appended (code-producer + quality-handler) with Principle 9 reasoning-config + selective-BLOCKING + status-enum contracts

**Q-CC-1 (first architectural question for composer)**: quality-handler model/effort allocation. The verdict-classification step (APPROVED / NEEDS_REVISION / STUB_DETECTED / BLOCKER) requires judgment that may not always be cleanly sonnet-bounded — e.g., a test failure that's flaky vs. a real regression requires reasoning about the test's recent history. Initial choice is sonnet/medium per Principle 9's bounded-transformation framing, but Composer should consider whether early operation calls for an opus-with-effort-high alternative. The fallback path (orchestrator escalates a sonnet-uncertain verdict to a re-invocation under opus) is also viable and may be the right architectural answer. Surfacing now; Composer to resolve.

**Q-CC-2 (second architectural question for composer)**: should `detect_stubs.py` be path-aware? The reference quality-fixer Step 1 BLOCKING applies stub-detection to "the implementation files." But execution-side tasks may also produce test files — should the script scan test files too? A test file containing `pass` or `// TODO: assert this works later` is also a stub, structurally. But test files have legitimate use of `pass` (placeholder test bodies during exploration). The right path-filter design is non-obvious. Surfacing for Composer.

**Forward dependencies surfaced**:
- D-13 (Pass 3) scoring dimensions interact with how the phase-quality-reviewer reads quality-handler outputs.
- D-3 (Pass 3) FR-3 invocation model determines how the audit families (cc-audit + GHA + Codespaces) plug into the phase-quality flow alongside quality-handler outputs.
- The "Plan-stage task should sequence install" notes (ai-development-guide install, agent-prompt authoring order) are inputs to Plan Authoring stage downstream.

**Inventory growth check**: 5 new subagents now declared (orchestrator, phase-quality-reviewer, finalize-reconciler, code-producer, quality-handler). 1 modified subagent (shared-document-reviewer). 1 new skill (ai-development-guide). 1 new script (detect_stubs.py). Total CC artifacts in flight: 8 (5 agents + 1 modified + 1 skill + 1 script). Reasonable count; not over-decomposed. Future passes will add audit-family scripts + hook implementation + possibly discipline-check script.

### Pass 3 resolution summary

**Decisions resolved**: D-1, D-3 (with refinement), D-13 (with reframing), D-17.

**D-1 — FR-3 finding-organization dimension — RESOLVED**: hybrid (domain + severity as orthogonal tags). Pure-domain loses severity info needed for verdict-issuing; pure-severity loses dispatch info needed by reconciler; flat loses both; hybrid serves both downstream consumers. Findings carry `domain` + `severity` + `source_activity` + `file_path` + `message` + `dispatch_hint` fields.

**D-3 — FR-3 invocation model — RESOLVED with refinement**: third option (not in synthesis's two-option framing). New script `auditing-shared/scripts/run_phase_checks.py` acts as a thin coordinator that fans out to each canonical audit/test/validator entry point. Preserves ADR-0031 canonical-home discipline (extending `auditing-cc-configs` to dispatch non-CC audits would be a category error); gives orchestrator single-call simplicity; new audit families add via coordinator's invocation list. Naming: "phase-checks" (not "audits") because the script handles 7 activities across 3 categories.

This is the second material refinement of synthesis substrate (Pass 1's D-9 was the first). Both refinements share a pattern: the synthesis's framing presented two options, the actual best answer was a third option that emerged from substrate detail. **Open item**: synthesis.md D-3's framing should be revised in a future patch; consolidate with D-9 refinement note.

**D-13 — Phase-quality scoring dimensions — RESOLVED with reframing**: NOT numeric scoring (the planning-side reviewer's 4-dimension model doesn't transplant cleanly to execution-side observable counts). **Dimensional verdict structure instead**: overall verdict + per-dimension status (tests / audits / validator / discipline). Rollup rule: blocker in any dimension → overall BLOCKER; revisable in any dimension → NEEDS_RECONCILIATION; all clean → PASS. Inherits D-1's tagging structure.

The synthesis's framing as "scoring dimensions" prefigured numeric-scoring; the substrate didn't support that. Reframing to dimensional-status structure is honest. **Open item**: synthesis.md D-13's framing should be revised.

**D-17 — FR-12 audit-counter-delta computation contract — RESOLVED**: all four sub-questions answered. (a) Both feature-start AND prior-phase baselines reported; feature-start is primary, matches prior archive precedent. (b) Per-domain raw counts + aggregate total; severity-weighted aggregation deferred to future feature as over-engineering. (c) Lives in phase-quality-report.{json,md} pair (no separate sidecar). (d) Informational by default; explicit feature-config can elevate to gating.

**Subsections populated by this pass**:
- Inventory of CC primitives → Scripts (new) — 3 entries appended (run_phase_checks.py + auditing-github-actions + auditing-codespaces stub)
- Inventory of CC primitives → Skills (new) — 2 entries appended (auditing-github-actions + auditing-codespaces)
- Skill patterns — 2 detailed entries (auditing-github-actions extraction + auditing-codespaces stub)
- Subagent patterns → `execute-phase-quality-reviewer` updated with full verdict schema + audit-counter-delta schema
- Rule patterns — full (declares "no new rules"; rationale given)
- Permission policy — full (allow-list extensions for the 5 audit/check scripts + test runners as a class + discipline notes)

**Q-CC-3 (third architectural question for composer)**: severity-weighted aggregation in audit-counter delta. Current resolution defers to future feature ("over-engineering"). But there's a real argument that 100 minor findings + 1 blocker shouldn't aggregate to "101 findings, delta +1" the same way "100 minor findings + 0 blockers" aggregates. The per-domain breakdown partially mitigates (the blocker shows in the per-domain detail). But the aggregate-total field will be misleading in mixed-severity cases. Surface for Composer: is severity-weighted aggregation needed at v1, or is the per-domain breakdown sufficient as the primary signal?

**Q-CC-4 (fourth architectural question for composer)**: `auditing-codespaces` stub semantics. The stub returns empty findings. Downstream consumers (the phase-quality reviewer; the audit-counter delta computation) will count "0 findings" — indistinguishable from "ran cleanly, no findings." Should the stub explicitly declare `"stub": true` in its output so downstream consumers can treat it differently? Or is the stub-vs-real distinction immaterial at the phase-quality-report level?

**Forward dependencies surfaced**:
- D-14 (Pass 4) FR-4 dispatch taxonomy: the `dispatch_hint` field in finding objects is what finalize-reconciler consumes; the taxonomy determines what dispatch_hint values are valid + what each maps to in terms of upstream-stage re-invocation.
- D-12 (Pass 4) reconciliation budget value: applies to phase-level reconciliation cycle cap (analog to planning-side 4-cycle cap); also potentially to per-task quality loop cap (FR-2-c).
- D-5 (Pass 5) FR-7 artifact format pair pattern: the phase-quality-report.{json,md} structure prefigured above assumes pair pattern; Pass 5 confirms.

**Anti-pattern checks (mechanical sweep)**:
- "Subagent without `tools:` restriction" — phase-quality-reviewer's tools are explicitly listed.
- "Permissions allow with Bash(*)" — permission policy uses scoped patterns; never Bash(*).
- "Subagent listing 15 skills" — phase-quality-reviewer has 3 skills; well under threshold.

**Inventory growth check**: 5 new subagents (unchanged from Pass 2). 1 modified subagent (unchanged). 3 new skills (ai-development-guide + auditing-github-actions + auditing-codespaces). 4 new scripts (detect_stubs + run_phase_checks + audit_workflow extracted + audit_codespaces stub). Total CC artifacts: 13 (5 agents + 1 modified + 3 skills + 4 scripts). Still reasonable count; concentrated growth in scripts (which is appropriate — execution-pipeline implementation lives in scripts more than agents).

### Pass 4 resolution summary

**Decisions resolved**: D-14, D-12, D-16.

**D-14 — FR-4 dispatch taxonomy — RESOLVED**: 6-row dispatch table (tests / audits / validator / discipline / stub findings) mapping `(domain, source_activity)` tuples to target agents and revision context payloads. Edge case: scope-bounded dispatch — audit findings outside current task scope are NOT auto-dispatched; surface as `existing_defect_outside_scope` to user. Multi-finding consolidation: group by `(target_agent, target_artifact)` and re-invoke once with consolidated findings.

**D-12 — Reconciliation budget value — RESOLVED**: 4 cycles for both per-task quality loop AND phase-level reconciliation. Symmetric with planning-side discipline-3 + ADR-0017 4-cycle cap. Rationale: empirically validated value; transfer reuses validation; differentiating would need new empirical justification. Counter increments managed by `execute-orchestrator`; cap-check applied by both orchestrator (per-task) and finalize-reconciler (phase-level).

**D-16 — FR-5 state-transition hooks contract — RESOLVED**: 
- Trigger semantics: ALL state transitions (12-row transition table documented in orchestrator entry above; forward, backward, gate-pass, gate-fail, escalation all logged).
- Hook contract: synchronous; JSON payload via stdin; void output; failure logs warning but does NOT block transition.
- Implementation locus: application-level (NOT Claude Code platform hooks). Script-based; orchestrator invokes at transition points.
- Hook output destination: append-only JSONL at `working/feature/<slug>/state-transitions.log`. Not per-artifact frontmatter (would require version-bump-on-every-transition; signal-to-noise too low).

**Q-CC-5 (fifth architectural question for composer)**: platform-hooks-vs-application-hooks distinction. FR-5 uses "hooks" terminology that overloads with Claude Code platform hooks (PreToolUse / PostToolUse / etc.). This design resolved the ambiguity to application-level hooks (orchestrator-invoked scripts at transition points). Worth Composer attention: is the FR-5 phrasing in the PRD likely to mislead Plan-stage readers? Should the cc-design.md introduce a renaming (e.g., "state-transition log invocations" instead of "hooks") for clarity, OR keep the FR-5 terminology and disambiguate inline? Current design takes the latter; Composer should sanity-check.

**Subsections populated by this pass**:
- Hook patterns — full (application-level hook clarification + contract + script implementation + permission policy note)
- Inventory of CC primitives → Scripts (new) — 1 entry appended (log_state_transition.py)
- Subagent patterns → `execute-finalize-reconciler` updated with D-14 dispatch table + D-12 hard cap + scope-bounded edge case + multi-finding consolidation
- Subagent patterns → `execute-orchestrator` updated with D-12 hard caps + D-16 12-row transition table

**Forward dependencies surfaced**:
- D-5 (Pass 5) FR-7 pair pattern: quality-reconciliation-log.{json,md} structure assumes pair pattern; Pass 5 confirms.
- D-4 (Pass 5) convention drift: doc_type taxonomy extension needed for `state_transitions_log` JSONL artifact + the 3 execution-phase doc types already listed in D-9 modification entry.
- D-15 (Pass 5) discipline-enforcement: if option 2 is taken, discipline-check findings feed into D-14 dispatch taxonomy (already pre-listed in the dispatch table above).

**Anti-pattern checks (mechanical sweep)**:
- "Hook running an LLM call" — verified: `log_state_transition.py` is a pure script (file-append + JSON-encode); no LLM invocation. Compliant.
- "Hook that silently rewrites Claude's output" — verified: log_state_transition is append-only and observational; does not modify any other artifact. Compliant.
- "Hook with unhandled error" — addressed: script returns prompt-completion exit code; orchestrator handles non-zero exit codes by logging warning + proceeding. Hook failure does not block transitions.

**Inventory growth check**: 5 new subagents (unchanged). 1 modified subagent (unchanged). 3 new skills (unchanged from Pass 3). 5 new scripts (4 from Pass 3 + log_state_transition.py from Pass 4). Total CC artifacts: 14. Concentrated growth in scripts (now 5); this remains appropriate — execution-pipeline implementation lives in scripts more than agents.

### Pass 5 resolution summary

**Decisions resolved**: D-4, D-18, D-5, D-7, D-15. **All 21 decision targets now resolved.**

**D-4 — Convention drift / spec authority — RESOLVED**: archive-authoritative. The 4 fields (`intent_user_token`, `gate_passed`, `reviewer_verdict`, `approved_at`) plus the doc_type taxonomy gap are canonicalized in `shared-conventions.md` updates. Surfaced as ADR-A in Open items (paired with D-18 since both touch the same spec file).

**D-18 — Canonical state vocabulary scope — RESOLVED**: per-doc-type vocabulary (synthesis option 3). Three base categories — gated artifacts (5-state); analysis/log artifacts (3-state: draft/complete/superseded); ADRs (4-state: no draft). State-transitions.log is JSONL event log (no state field). Surfaced as part of ADR-A in Open items.

**D-5 — FR-7 artifact format — RESOLVED**: pair pattern (.json + .md). Direct application of established convention. Special case: state-transitions.log is JSONL event log (different category from pair-pattern artifacts). FR-13 (machine-parseable reconciliation log) is satisfied by the .json half of quality-reconciliation-log pair.

**D-7 — ADR-0029 execution extension — RESOLVED**: new ADR (ADR-B in Open items) extending ADR-0029's per-stage Scope-Deviation table with execution-phase rows (per-task / phase-quality / quality-reconciliation). Designers don't author ADRs per FR-5; Blueprint-stage owns the authoring. Substrate: ADR-0029's own Forward Implications anticipated this feature.

**D-15 — Discipline enforcement mechanism (systematic) — RESOLVED**:
- For discipline 5 (worked example): option 2 — separate `auditing-shared/scripts/check_pipeline_discipline.py`. v1 ships discipline 5 only; function-per-discipline architecture permits future generalization.
- Systematic question: enforcement-status inventory documented in Open items (5-row table covering all 5 disciplines). Blueprint approves the v1 scope (discipline 5) and acknowledges the future-feature roadmap (discipline 4 validator next; disciplines 1+2 mechanical enforcement medium-term).

**Subsections populated by this pass**:
- CLAUDE.md changes — full ("no changes"; rationale: recipe-feature-pipeline already owns the discipline; second source of truth would drift)
- Inventory of CC primitives → Scripts (new) — 2 entries appended (`validate_pipeline_frontmatter.py`, `check_pipeline_discipline.py`)
- Permission policy — extended with 2 new script allow entries
- Open items — full consolidated section (3 new ADRs to author + systematic enforcement inventory + skill install sequencing + synthesis substrate revisions + existing-defect carry-forwards)

**All 21 decision targets now resolved**:

| Decision | Pass | Status |
|---|---|---|
| D-1 (FR-3 organizing dim) | Pass 3 | RESOLVED |
| D-2a (BLOCKING annotations) | Pass 2 | RESOLVED |
| D-2b (escalation taxonomy) | Pass 2 | RESOLVED |
| D-2c (APPROVED status) | Pass 2 | RESOLVED |
| D-2d (stub detection) | Pass 2 | RESOLVED |
| D-3 (FR-3 invocation) | Pass 3 | RESOLVED with refinement |
| D-4 (convention drift) | Pass 5 | RESOLVED |
| D-5 (FR-7 format) | Pass 5 | RESOLVED |
| D-6 (orchestration shape) | Pass 1 | RESOLVED |
| D-7 (ADR-0029 extension) | Pass 5 | RESOLVED |
| D-8 (per-task loop) | Pass 1 | RESOLVED |
| D-9 (reviewer architecture) | Pass 1 | RESOLVED with refinement |
| D-10 (agent inventory) | Passes 1-4 | RESOLVED (incremental) |
| D-11 (code-producing boundary) | Pass 2 | RESOLVED |
| D-12 (reconciliation budget) | Pass 4 | RESOLVED |
| D-13 (scoring dimensions) | Pass 3 | RESOLVED with reframing |
| D-14 (FR-4 dispatch taxonomy) | Pass 4 | RESOLVED |
| D-15 (discipline enforcement) | Pass 5 | RESOLVED (v1 scope; broader inventory in Open items) |
| D-16 (FR-5 hooks contract) | Pass 4 | RESOLVED with disambiguation |
| D-17 (FR-12 audit-counter-delta) | Pass 3 | RESOLVED |
| D-18 (canonical state vocab) | Pass 5 | RESOLVED |

**Final inventory growth check**: 5 new subagents. 1 modified subagent. 3 new skills (ai-development-guide + auditing-github-actions + auditing-codespaces). 7 new scripts (detect_stubs, run_phase_checks, audit_workflow extracted, audit_codespaces stub, log_state_transition, validate_pipeline_frontmatter, check_pipeline_discipline). Total CC artifacts: 16. Substantial growth but concentrated in scripts (where execution-pipeline implementation belongs). Subagent count (5) is modest and well-justified.

**Anti-pattern checks (cumulative across all passes)**:
- "Subagent without `tools:` restriction" — all 5 new subagents have explicit `tools:` lists. ✓
- "Subagent listing 15 skills" — max skill count across new subagents is 5 (`execute-orchestrator`). ✓ Well below threshold.
- "`skills:` array for reasoning depth" — explicitly avoided. ✓
- "Hook running an LLM call" — log_state_transition.py is pure script (file-append). ✓
- "Hook with unhandled error" — script's non-zero exit code triggers warning, not block. ✓
- "Permissions allow with Bash(*)" — all Bash entries scoped to specific script paths. ✓
- "Two sources of truth (rule + CLAUDE.md)" — no CLAUDE.md changes; no rule patterns added; disciplines live in recipe skill or mechanical scripts, never duplicated. ✓
- "Plugin bundling a single skill" — no plugin packaging proposed (covered in finalize batch). ✓ in advance.
- "Skill description vague" — install-time concern; flagged in skill-pattern entries as Plan-stage authoring discipline.

**Pass 5 produced no new Q-CC-N items** (the 5 questions from Passes 2-4 are sufficient for Composer). All Pass-5 questions are resolved either inline or as Open Items routed to Blueprint-stage.
