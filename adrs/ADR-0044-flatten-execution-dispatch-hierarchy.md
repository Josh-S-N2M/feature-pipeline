---
id: ADR-0044
version: 1.0.0
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0017, ADR-0019, ADR-0022, ADR-0029, ADR-0033, ADR-0035, ADR-0036]
applies_to:
  - execute-orchestrator-dispatch-mechanism-repair-r1
  - .claude/skills/recipe-feature-pipeline/SKILL.md (Execution Phase Dispatch section)
  - .claude/agents/execute-orchestrator.md (re-scoped to advisor)
  - .claude/agents/execute-finalize-reconciler.md (Agent removed; dispatch_directives[] emission)
  - .claude/agents/execute-task-code-producer.md (dispatcher prose only)
  - .claude/agents/execute-task-quality-handler.md (dispatcher prose only)
  - .claude/agents/execute-phase-quality-reviewer.md (dispatcher prose only)
  - .claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md (v1 invariant clarified)
  - all future execution-phase pipeline runs
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: |
  Resolves PRD §6 option selection under kill-criterion-#2 closure. Chooses
  option (a) — flatten the dispatch hierarchy. The parent
  recipe-feature-pipeline/SKILL.md becomes the direct dispatcher of the four
  execution-side specialists at the main-conversation level where Agent
  dispatch IS supported per T-001. execute-orchestrator.md is re-scoped as a
  state-machine advisor (Agent and TaskUpdate removed from its tools array;
  body re-framed). execute-finalize-reconciler emits a dispatch_directives[]
  array consumed by the parent (Agent removed). Specialist isolation, the
  ADR-0017 4-cycle cap, and ADR-0033 symmetric D-12 application are
  preserved.
---

# ADR-0044: Flatten execution-phase dispatch hierarchy — parent orchestrator dispatches the four specialists directly

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Accepted — 2026-05-23.

Authored at the Design Composition stage of the `execute-orchestrator-dispatch-mechanism-repair-r1` feature run, after Discovery Research (T-001) returned `dispatch_supported: false` and `kill_criterion_triggered: 2` (PRD FR-2 / FR-3 path). The PRD FR-3 selection authority lies with the per-layer `cc` Design subsection and the Design Composer; the Composer ratifies the per-layer Designer's option (a) recommendation and authors this ADR per FR-5 (only the Composer authors ADRs).

## Context

`Issues/analysis-execute-orchestrator-dispatch-limitation.md` documents that the `execute-orchestrator` sub-agent declares `tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` in its frontmatter but its runtime tool surface is `[Read, Write, Bash, Edit]`. `Agent`, `Glob`, `Grep`, and `TaskUpdate` are missing; `Edit` is present despite being undeclared; the `Bash(python3:*)` scope restriction is stripped. The defect was observed twice during the `devcontainer-mcp-provisioning-r1` execution-phase entry on 2026-05-23.

The hard consequence is that `execute-orchestrator` cannot perform its single core responsibility — dispatching the four execution-side specialists (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`). The `devcontainer-mcp-provisioning-r1` run shipped via a workaround (parent-driven dispatch) but lost four load-bearing properties documented in analysis §3.2: (a) per-dispatch state-transition logging across distinct sub-agent boundaries; (b) per-task and per-phase cycle-counter enforcement against the ADR-0017 4-cycle cap; (c) dispatch-matrix routing through `execute-finalize-reconciler`; (d) ADR-0033 symmetric D-12 application.

Discovery Research T-001 confirmed via three independent Anthropic-controlled primary sources (https://code.claude.com/docs/en/sub-agents; https://code.claude.com/docs/en/agent-sdk/subagents; https://github.com/anthropics/claude-code/issues/29677) that **sub-agents cannot dispatch other sub-agents at runtime, even when `Agent` is declared in the `tools:` array** — this is a deliberate Claude Code substrate constraint, not a frontmatter-parsing bug nor a one-flag fix. Synthesis §2 records this as anchor claim T-0001 (`dispatch_supported: false`) and the deductive consequence T-0002 (`kill_criterion_triggered: 2`) per PRD FR-2.

The PRD's source analysis §6 enumerated three design options for the kill-criterion-#2 path:

- **(a) Flatten dispatch hierarchy** — top-level `recipe-feature-pipeline` orchestrator directly dispatches the four specialists; `execute-orchestrator` is retained as a state-machine advisor.
- **(b) Retire `execute-orchestrator`** — move its state-machine logic into `recipe-feature-pipeline`; the advisor file is deleted.
- **(c) Bash-script dispatch surface** — `execute-orchestrator` dispatches Bash scripts (which it CAN run) rather than sub-agents; the scripts invoke specialists via another mechanism.

The codebase analysis blast-radius enumeration (codebase-analysis.json `blast_radius` per-option entries) and the synthesis substrate analysis converge on option (a). The per-layer `cc` Design subsection (Designer: `design-cc`) ratified option (a) with three load-bearing reasons; this ADR captures that decision and its rationale.

**Constraint context honored:** PRD FR-3-c (preserve ADR-0017 4-cycle cap, dispatch-matrix definitions, ADR-0033 symmetric D-12 application); PRD FR-4 (8-file inventory cap with AC-FR-4-a operator gate); PRD NFR-5-a (canonical schema reference lockstep); PRD NFR-6 (no migration of in-flight `devcontainer-mcp-provisioning-r1` artifacts).

## Decision

The parent `recipe-feature-pipeline/SKILL.md` becomes the direct dispatcher of the four execution-side specialists at the main-conversation level where Agent dispatch is supported. `execute-orchestrator.md` is **retained** but re-scoped as a state-machine advisor / canonical reference document; `Agent` and `TaskUpdate` are removed from its `tools:` array; its body is re-framed from "what this agent does" to "what the parent orchestrator MUST execute when invoking specialists." `execute-finalize-reconciler.md` has `Agent` removed from its `tools:` array and emits a `dispatch_directives[]` array in `quality-reconciliation-log.json` that the parent orchestrator consumes; the parent dispatches each named target via `Agent` at the main-conversation level.

The four specialists' substantive domain responsibilities (code production, quality handling, phase quality review, finalize reconciliation) are unchanged per PRD FR-3-b / FR-4-c. The ADR-0017 4-cycle cap, the dispatch-matrix definitions, and the ADR-0033 symmetric D-12 application are preserved as load-bearing invariants per PRD FR-3-c.

## Decision Details

| Item | Content |
|---|---|
| Decision | Option (a): the parent `recipe-feature-pipeline/SKILL.md` directly dispatches the four execution-side specialists at the main-conversation level; `execute-orchestrator.md` becomes a state-machine advisor (Agent + TaskUpdate removed); `execute-finalize-reconciler.md` emits `dispatch_directives[]` consumed by the parent (Agent removed). |
| Why now | The dispatch defect is currently exercising the parent-driven workaround, which loses the four load-bearing properties documented in analysis §3.2. Every future execution-phase run re-incurs the audit-trail loss until the repair lands. |
| Why this | (1) PRD FR-4 8-file inventory: option (a) touches 4 files (3 in-inventory + 1 outside) and triggers exactly 1 AC-FR-4-a open item; option (b) escapes by ≥5 outside-inventory files and breaks the state-transitions-log v1 `invoking_agent` invariant; option (c) degrades the specialist-isolation audit trail (the script becomes the audit boundary, not the agent). (2) State-transitions-log v1 `invoking_agent` invariant is preserved by re-interpretation (`execute-orchestrator` remains the logical owner; the parent is the emitter). (3) Specialist isolation across four distinct sub-agent boundaries is preserved because dispatch from the main conversation IS supported per T-001 Finding F-1. |
| Known unknowns | The state-transitions-log v1 `invoking_agent` invariant clarification ("logical owner of the transition, always `execute-orchestrator` in v1, even when emitted by the parent on its behalf") rests on a single observed in-flight artifact (`devcontainer-mcp-provisioning-r1/state-transitions.log`) and Composer ratification (Q-CC-4 disposition). If a future audit consumer interprets `invoking_agent` as the literal emitter rather than the logical owner, the invariant text may need a separate `emitter` field added. |
| Kill criteria | (1) If a future Claude Code harness update enables true sub-agent → sub-agent dispatch (i.e., `Agent` in a sub-agent's `tools:` becomes operational at runtime), reconsider whether the advisor should be restored to dispatcher and the dispatch section migrated back. (2) If the dispatch-directives indirection (reconciler emits, parent dispatches) introduces an unrecoverable failure mode where the reconciler's intent and the parent's action drift, reconsider option (c) (Bash-script dispatch) as a tighter coupling. (3) If three or more future execution-phase runs surface novel cycle-counter or state-transition-log defects attributable to the parent-as-dispatcher model, escalate for a deeper redesign. |

## Rationale

The framer-and-substrate joint recommendation (synthesis §3.1 D-001) selected option (a) on three grounds the Composer ratifies verbatim:

**(1) PRD FR-4 8-file inventory compliance.** The PRD enumerates eight in-inventory files (FR-4 list). Option (a) touches three in-inventory files (`recipe-feature-pipeline/SKILL.md`, `execute-orchestrator.md`, `execute-finalize-reconciler.md`) plus the canonical `checkpoint.json` and `state-transitions.log` schema references that live inside `recipe-feature-pipeline/SKILL.md` and `state-transitions-log-entry-template.md`. The single outside-inventory edit is to `state-transitions-log-entry-template.md` (v1 invariant clarification + `void` / `-prime` extension folding), counted as exactly one AC-FR-4-a open item.

Option (b) escapes the inventory by five or more outside-inventory files (`KB-documentation-criteria/SKILL.md` template assignments; `state-transitions-log-entry-template.md` v1 invariant broken; `pipeline-run-summary-template.md` generated-by; `smoke_test_auditing_shared.py` test data; `auditing-codespaces/SKILL.md` consumer note). It triggers the AC-FR-4-a operator gate with the widest possible surface and would re-promote the schema-ownership-transfer decision to a second ADR.

Option (c) introduces a new dispatch script outside the inventory at the same cost as option (a), but the script becomes the audit boundary instead of the agent. Per source analysis §3.2 / AN-0037, this is a real audit-trail loss — the very property the repair must preserve.

**(2) State-transitions-log v1 `invoking_agent` invariant preservation.** The canonical state-transitions-log per-entry schema in `state-transitions-log-entry-template.md:63` states that `invoking_agent` is "always `execute-orchestrator` in v1." The in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` already shows this value across all entries (the parent emitted on the orchestrator's behalf during the workaround run). Option (a) preserves the invariant by re-interpretation: the value is the **logical owner** of the state transition (i.e., `execute-orchestrator`, which the advisor file canonically documents), even when emitted by the parent. This is the minimal-change interpretation that honors both the v1 invariant and PRD NFR-6-a (in-flight artifact preservation). Option (b) would force a schema-ownership transfer and an additional ADR.

**(3) Specialist-isolation audit-trail preservation.** Per source analysis §3.1, specialist isolation across four distinct sub-agent boundaries is load-bearing for four properties: (a) per-dispatch state-transition logging; (b) per-task and per-phase cycle-counter enforcement per ADR-0017; (c) dispatch-matrix routing through `execute-finalize-reconciler`; (d) ADR-0033 symmetric D-12 application. Option (a) preserves all four because the parent orchestrator dispatches each specialist via `Agent` at the main-conversation level — where dispatch IS supported per T-001 Finding F-1 — yielding four distinct sub-agent boundaries with their own transcripts and state-transition entries. Option (c) collapses these into a Bash sub-process boundary, degrading all four properties.

The rationale brief commitments honored: every reference to the 4-cycle cap and the symmetric D-12 application cites **ADR-0017 + ADR-0033** (NOT ADR-0034) per DISSENT-2 carry-through (synthesis §5.4 / OI-FRAMER-1). The pre-existing PRD FR-3-c mis-attribution to ADR-0034 was surgically corrected post-Gate-2; this ADR does not propagate the mis-credit.

## Options Considered

### Option 1: Retire `execute-orchestrator` entirely (synthesis §3.1 — rejected)

**Pros:**
- Eliminates the advisor-vs-dispatcher ambiguity by removing the file.
- Single locus of state-machine knowledge (the parent skill).

**Cons:**
- Escapes the PRD FR-4 8-file inventory by ≥5 outside-inventory files (KB-documentation-criteria/SKILL.md template assignments; state-transitions-log-entry-template.md v1 invariant; pipeline-run-summary-template.md; smoke_test_auditing_shared.py; auditing-codespaces/SKILL.md).
- Breaks the state-transitions-log v1 `invoking_agent` invariant — would require either schema evolution to v2 (with a separate `emitter` field) or invalidation of the in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` artifact (violating PRD NFR-6-a).
- Roughly 2× the effort of option (a) for the same functional outcome.
- Triggers AC-FR-4-a scope-expansion gate with the widest possible operator surface.

### Option 2: Bash-script dispatch surface (synthesis §3.1 — rejected)

**Pros:**
- Physically possible per T-001 (claim T-0064): the runtime tool surface includes `Bash`, so `execute-orchestrator` could invoke a script.
- Preserves `execute-orchestrator` as a runtime entity rather than re-scoping to advisor.

**Cons:**
- Specialists invoked via Bash sub-process bypass the harness's per-agent transcript and per-agent state-transitions logging.
- The script becomes the audit boundary rather than the agent — per source analysis §3.2 / AN-0037 this is a real audit-trail loss, the very property the repair must preserve.
- Equivalent outside-inventory cost to option (a) (1 file: a new dispatch script) but lowest pattern fidelity.
- Anthropic's documented alternatives (Skills, chain-from-main, agent teams) are stronger if indirection is desired, and chain-from-main IS option (a).

### Option 3 (Selected): Flatten the dispatch hierarchy

**Pros:**
- Minimal-edit option per PRD FR-4 inventory: 3 in-inventory files + 1 outside-inventory file (1 AC-FR-4-a open item).
- Preserves all four specialist-isolation invariants because dispatch at the main-conversation level IS supported per T-001.
- Preserves the state-transitions-log v1 `invoking_agent` invariant via re-interpretation (logical owner vs. emitter).
- Honors NFR-6-a (no in-flight artifact migration).
- Reversal is cheap: if a future Claude Code harness enables sub-agent → sub-agent dispatch, re-add `Agent` + `TaskUpdate` to `execute-orchestrator.md` and migrate the dispatch section back.

**Cons:**
- The advisor-vs-dispatcher framing of `execute-orchestrator.md` is initially less obvious to readers (mitigated by the body re-framing and the dispatch-section pointer in `recipe-feature-pipeline/SKILL.md`).
- The `dispatch_directives[]` indirection introduced for `execute-finalize-reconciler` is a novel pattern (mitigated by Contract 4 wording in the affected agent files and AC-CC-5 enforcement).

## Consequences

### Positive Consequences

- **Repair lands within the PRD FR-4 8-file inventory** with exactly one AC-FR-4-a open item.
- **All four load-bearing audit-trail properties are restored** (per-dispatch logging; per-task and per-phase cycle counters; dispatch-matrix routing; ADR-0033 symmetric D-12 application).
- **In-flight `devcontainer-mcp-provisioning-r1` artifacts remain valid** without migration.
- **Cheap reversibility** if the Claude Code harness later enables sub-agent → sub-agent dispatch.
- **Specialist-isolation discipline (Contract 5)** is exercised end-to-end.

### Negative Consequences

- The advisor role of `execute-orchestrator.md` is a documentation pattern that may confuse new readers — requires deliberate body-prose re-framing.
- The `dispatch_directives[]` indirection adds a small reasoning step for the reconciler-to-parent handoff (one JSON read by the parent, plus per-row dispatch).
- The state-transitions-log `invoking_agent` invariant gains a "logical owner vs. emitter" interpretation that future consumers must understand (mitigated by the schema-closure D-004 documenting this explicitly).

### Neutral Consequences

- Each specialist's frontmatter (model / effort / skills triplet) is unchanged per ADR-0022 audit; only body-prose dispatcher references are updated.
- No new sub-agent files are authored; no MCP servers are introduced; no hooks are added.
- The FR-6 verification surface (synthetic minimal test feature) is unaffected at the design level; the F-7 mid-session-agent-registry constraint is honored if `plan-author` authors any new agent for the synthetic test (two-session verification per synthesis D-002).

## Architecture Impact

### Components that change

- `.claude/skills/recipe-feature-pipeline/SKILL.md` — gains a new "Execution Phase Dispatch" section (after Gate 6) operationalizing the parent-driven dispatch loop; lines 96–128 schema reference is updated in lockstep per synthesis Constraint 5.1 (D-001 + D-004 same-file pressure).
- `.claude/agents/execute-orchestrator.md` — `Agent` and `TaskUpdate` removed from `tools:`; body re-framed from "what this agent does" to "what the parent orchestrator MUST execute when invoking specialists"; the file becomes the canonical state-machine reference the parent skill points to.
- `.claude/agents/execute-finalize-reconciler.md` — `Agent` removed from `tools:`; body line 76 "Dispatch via Agent" prose re-framed to "emit `dispatch_directives[]` in `quality-reconciliation-log.json`"; ADR-0034 mis-citations on lines 3, 19, and 82 all corrected to ADR-0033 per DISSENT-2 carry-through (I-DR-001 absorption).
- `.claude/agents/execute-task-code-producer.md`, `.claude/agents/execute-task-quality-handler.md`, `.claude/agents/execute-phase-quality-reviewer.md` — body-prose-only dispatcher reference updates ("dispatched by execute-orchestrator" → "dispatched by recipe-feature-pipeline parent orchestrator").
- `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` — v1 `invoking_agent` invariant clarified (line 63: logical owner, not literal emitter); `void` / `void_reason` and `-prime` transition-name suffix conventions folded into v1 documentation.

### New dependencies introduced

None at the platform level. One new intra-cc dependency: the parent orchestrator skill becomes a consumer of `quality-reconciliation-log.json.dispatch_directives[]` (emitted by `execute-finalize-reconciler`).

### Architectural constraints added

- The state-transitions-log `invoking_agent` field is interpreted as the **logical owner** of the state transition (always `execute-orchestrator` in v1), not the literal emitting agent. This is a v1 invariant clarification, not a schema evolution.
- The `dispatch_directives[]` array in `quality-reconciliation-log.json` is the canonical hand-off mechanism from the reconciler to the parent orchestrator.
- Future execution-phase additions MUST be designed for parent-driven dispatch from the main conversation, NOT for sub-agent → sub-agent dispatch.

### Architectural constraints removed

None. The four specialist-isolation invariants are explicitly preserved.

### Layers affected (9-layer taxonomy)

- **Claude Code / Project Filesystem** — sole affected layer (cc-only feature).
- All other layers — N/A — out of scope.

## Implementation Guidance

Principled direction only — procedures live in the Blueprint and Plan.

- **Edit ordering on `recipe-feature-pipeline/SKILL.md`.** D-004 schema closure (lines 96–128) lands BEFORE D-001 dispatch-section addition. The schema must stabilize so the dispatch section can reference the documented `execution_pipeline_state_transitions`, `execution_mode`, and `execution_pipeline_cycle_counters` fields. The two edits SHOULD ship in the same commit set; if they cannot, schema closure precedes dispatch-section absorption.
- **Bundled commit for `Agent` removal.** The two `Agent`-removal edits (`execute-orchestrator.md:6` and `execute-finalize-reconciler.md:6`) SHOULD ship in a single commit. The commit message documents "FR-5 sweep closure: affected set = 2" per synthesis Constraint 5.2.
- **Complete ADR-0034 → ADR-0033 sweep on `execute-finalize-reconciler.md`.** All three occurrences (lines 3, 19, 82) are corrected. Lines 3 (description) and 82 (section heading "Cycle-cap escalation (D-12 + ADR-0034)") were missed by the per-layer cc-design's edit list; the Blueprint's edit list extends the cleanup per I-DR-001. (Reviewer's initial finding claimed a 4th occurrence on line 84; direct grep at Blueprint v1.1.0 patch time confirmed only 3 occurrences — line 84 cites ADR-0017, not ADR-0034.)
- **Specialist body-prose updates are prose-only.** No frontmatter / tool-grant / skills-array changes on the three non-reconciler specialists. Only the dispatcher-reference sentence is updated to point at the parent skill.
- **Advisor file documentation discipline.** `execute-orchestrator.md`'s body should make clear at the top that the file is now a state-machine reference, not an invocable dispatcher; the parent skill is the dispatcher. The `recipe-feature-pipeline` skill self-reference in `execute-orchestrator.md`'s `skills:` array is preserved with explicit body-prose rationale (Q-CC-3 disposition: preserve with rationale).
- **F-7 mid-session-agent-registry constraint.** If `plan-author`'s synthetic minimal test feature design (FR-6) authors any new sub-agent file, the plan MUST sequence the authoring task and the test-execution task across a session boundary (two-session verification per synthesis D-002).
- **Reversal path.** If kill-criterion-1 ever fires retroactively (a future Claude Code harness update enables sub-agent → sub-agent dispatch), reversal is: (1) re-add `Agent` + `TaskUpdate` to `execute-orchestrator.md:6`; (2) move the dispatch section back from `recipe-feature-pipeline/SKILL.md` into `execute-orchestrator.md` body; (3) restore `Agent` to `execute-finalize-reconciler.md:6` and switch `dispatch_directives[]` consumption from the parent to the reconciler. The reconciler's `memory: project` declaration is preserved under option (a) (Q-CC-5 disposition: preserve), reducing reversal cost.

## Related Information

### Related ADRs

- **ADR-0017** — 4-cycle cap (per-task + per-phase, symmetric per D-12). Load-bearing invariant; preserved without modification.
- **ADR-0019** — sub-agent / skill / ADR naming conventions. Preserved.
- **ADR-0022** — sub-agent reasoning configuration is intentional and audited (model/effort/skills triplet). Reasoning triplets are preserved across all five execute-* sub-agents; the advisor file retains `opus/high` to keep reversal cheap.
- **ADR-0029** — no-silent-scope-changes principle. Honored: PRD FR-2 kill-criterion-#1 was not exercised (kill-criterion-#2 fired); option (a) is the explicit user-gated FULL repair path.
- **ADR-0033** — ADR-0029 execution-phase extension and canonical home for symmetric D-12 application at per-task + per-phase boundaries. Cited throughout this ADR and across downstream artifacts.
- **ADR-0035** — auditing-shared skill-binding convention. Preserved: `execute-finalize-reconciler.md`'s `skills: [..., auditing-shared]` binding is unchanged.
- **ADR-0036** — single-location ADR placement convention. This ADR honors that convention: written once to `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md`; no feature-scoped duplicate.

### Related ADRs (orthogonal — N/A disposition for this run)

- **ADR-0042** (auditing-mcp family graduation) and **ADR-0043** (auditing-mcp Gate-6 hard gate) — surfaced by the codebase-researcher as "newly_surfaced_adrs_not_in_research_plan_list" with the question of whether they constrain the dispatch repair. Grep verification on both ADRs shows zero references to any execute-* agent. ADR-0042 scopes the `auditing-mcp` family relationships among auditing skills; ADR-0043 scopes the orchestrator-level Gate 6 hard-gate behavior for MCP auditing findings. Neither constrains the execution-phase dispatch mechanism nor the four specialists' tool grants. **Disposition: N/A — orthogonal subject matter.** Disposition recorded in the Blueprint's Fact Disposition Table.

### Inherited from synthesis / referenced rationale-brief

- Synthesis §3.1 (D-001 frame): three-reason joint recommendation that this ADR ratifies.
- Synthesis §5.1 (Constraint 5.1): D-001 + D-004 same-file pressure on `recipe-feature-pipeline/SKILL.md`.
- Synthesis §5.2 (Constraint 5.2): bundled `Agent`-removal commit.
- Synthesis §5.4 / OI-FRAMER-1 (DISSENT-2 carry-through): ADR-0017 + ADR-0033, NOT ADR-0034.
- Research note T-001 (claim T-0001): the harness-level prohibition with three independent Anthropic-controlled primary sources.

### Referenced specs and files

- `Issues/analysis-execute-orchestrator-dispatch-limitation.md` — canonical source analysis; this ADR closes the analysis recommendation in §6.
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md` — PRD authorizing the repair under FR-3 / FR-4 / FR-5.
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design.md` — per-layer Design that ratified option (a) before composition.
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md` — the rationale brief.
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md` — anchor evidence.

### Related KBs

- `KB-cc-platform` (Claude Code primitive surface).
- `KB-cc-design` (per-layer design discipline, principles 1, 3, 4, 5, 9).
- `KB-documentation-criteria` (ADR + Blueprint templates).
- `KB-review-disciplines` (Gate 0/1 procedure for review).
