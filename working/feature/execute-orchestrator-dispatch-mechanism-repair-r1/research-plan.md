---
id: RP-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: research-plan
version: 1.0.0
status: draft
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
scope_class: FULL
layer_scope: [cc]
derived_from: working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
generated: 2026-05-23T21:05:00Z
generated_by: discovery-plan-author
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/intent-clarification.md
  - Issues/analysis-execute-orchestrator-dispatch-limitation.md
---

# Research Plan: execute-orchestrator Dispatch Mechanism Repair (r1)

## Contents

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

## Feature reference

- **Feature slug**: `execute-orchestrator-dispatch-mechanism-repair-r1`
- **PRD path**: `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md`
- **PRD version**: `1.0.0`
- **PRD gate state**: approved at the PRD Approval Gate on 2026-05-23 ("approved as-is" per orchestrator dispatch prompt)
- **Scope class**: `FULL` (multi-file repair plus an in-pipeline investigation)
- **Layer scope**: `[cc]` only (Claude Code / Project Filesystem — sole activated layer per PRD §Layer Scope)
- **Inherited ADRs in scope** (constrain or inform research scope):
  - ADR-0017 — 4-cycle cap + shared-document-reviewer integration (load-bearing invariant per PRD FR-3-c)
  - ADR-0019 — naming convention (constrains any new sub-agent or skill the design might introduce)
  - ADR-0021 — KB-and-ADR-first discipline (governs THIS document)
  - ADR-0022 — sub-agent reasoning configuration (closest existing ADR on sub-agent frontmatter; defines `tools:`, `model:`, `effort:`, `skills:` semantics but does NOT cover the `Agent` tool-grant runtime behavior)
  - ADR-0027 — pipeline skill-design gap; deliverable archive
  - ADR-0029 — no-silent-scope-changes
  - ADR-0033 — ADR-0029 execution extension; symmetric D-12 application at per-task and per-phase boundaries (load-bearing invariant per PRD FR-3-c)
  - ADR-0036 — single-location ADR placement
  - ADR-0037 — mcp-events.jsonl transition surfacing (execution-side event surface)
  - ADR-0040 — serena narrowed always-on
  - ADR-0041 — install mechanism hybrid
- **Applicable KBs** (those whose principles/patterns touch this feature's layer scope):
  - `KB-cc-platform` — platform-half facts on Claude Code primitives (sub-agents, `tools:`, hooks, MCP, plugins)
  - `KB-cc-design` — design-half discipline for choosing primitives and evolving cc configurations
  - `KB-documentation-criteria` — for ADR/Blueprint/Plan authoring under the chosen §6 option
  - `KB-codebase-research` — methodology guide for `discovery-codebase-researcher`'s output
  - `KB-review-disciplines` — applies at Gate 0/1 on every artifact produced

## Information needs inventory

Every information need named below is what a named downstream sub-agent will require to do its job. Dispositions follow the five-way triage in `KB-documentation-criteria/references/disciplines/discovery-planning.md`.

| Need ID | Description | Downstream consumer | Disposition |
|---|---|---|---|
| IN-001 | Whether sub-agent `Agent` dispatch is supported by the Claude Code harness at runtime when declared in the `tools:` frontmatter array; if not, why the harness strips/rewrites the tool surface; whether any frontmatter syntax variant, harness flag, or configuration enables sub-agent → sub-agent dispatch. | `synth-*` (the kill-criterion-#1 vs #2 branch), `design-claude-code` (selects among §6 options conditional on the outcome) | `external-research-topic:T-001` |
| IN-002 | What `execute-orchestrator.md`'s frontmatter declares, what its body specifies as dispatch responsibilities, and what tool surface and tool-grant claims it makes. | `design-claude-code` (rewrites or retires the agent), `plan-author` | `codebase-topic` |
| IN-003 | The shape of the four execute-* specialists (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`): their `tools:` declarations, their substantive domain responsibilities, what they expect their dispatcher to pass them, and what each returns. | `design-claude-code` (preserves substantive responsibilities under any §6 option; redesigns dispatch interfaces), `plan-author` | `codebase-topic` |
| IN-004 | How `recipe-feature-pipeline/SKILL.md` invokes `execute-orchestrator` today: where in the recipe (which step), what arguments it passes, what state it expects back, and which sections would change if `execute-orchestrator` is retired (§6 option b) or restructured (§6 options a / c). | `design-claude-code` (option b folds state-machine into this skill), `plan-author` (sequences edits), `design-composer` (ADR scope) | `codebase-topic` |
| IN-005 | Inventory of all sub-agents under `.claude/agents/*.md` that declare `Agent` in their `tools:` array, plus a note on whether the chosen §6 design would impact each file's dispatch posture (per PRD FR-5 inventory-only posture). | `design-claude-code` (informs cleanup-as-blocker check per AC-FR-5-b), `plan-author` (produces the inventory artifact at the right phase), `synth-*` | `codebase-topic` |
| IN-006 | The current shape of the `checkpoint.json` schema (specifically the `execution_pipeline_state_transitions` and `execution_mode` fields per PRD FR-4-b) and `state-transitions.log` format/schema as written by `devcontainer-mcp-provisioning-r1`. The repair must preserve the load-bearing properties; if the chosen §6 option changes the schema, the canonical reference must update in lockstep. | `design-claude-code` (decides whether schema changes), `plan-author` (sequences the canonical-reference update per AC-FR-4-b / NFR-5-a), `design-composer` (any cross-cutting ADR) | `codebase-topic` |
| IN-007 | Blast-radius preview: every file transitively touched by the four §6 options. The PRD lists 8 affected files as the touched-or-may-be-touched surface; the researcher confirms whether any other file imports / references / dispatches into these and would be affected by the repair. | `design-claude-code` (rules out unintended scope), `plan-author` (open-item user check per AC-FR-4-a if blast-radius reveals anything outside the 8-file inventory) | `codebase-topic` |
| IN-008 | The `tools:` frontmatter parsing rules — what syntax forms are accepted, how comma/array forms differ, whether scope restrictions like `Bash(python3:*)` are honored at runtime (the analysis observed the restriction was stripped). | `design-claude-code` (any §6 option requires picking a tool-grant declaration the harness honors), reviewers | `covered-by-KB:KB-cc-platform:references/extensions.md` (the `tools:` array form is documented at lines 142–174 of extensions.md, including tool-restriction semantics; the runtime strip behavior is itself part of IN-001's external research, not a separate need) |
| IN-009 | Sub-agent reasoning configuration discipline (`model:`, `effort:`, `skills:` fields) — relevant if the chosen §6 option introduces a new sub-agent or restructures one. | `design-claude-code` | `covered-by-ADR:ADR-0022` (specifies `model:` / `effort:` / `skills:` semantics and audit posture for all sub-agents under `.claude/agents/`) |
| IN-010 | The 4-cycle cap definition and which boundaries it applies at; the symmetric D-12 application at per-task and per-phase boundaries; and the dispatch matrix definitions (D-2a/c/d, D-12, D-13, D-14). These are load-bearing invariants the repair must preserve. | `design-claude-code` (preserves invariants per FR-3-c), reviewers (architecture audit) | `covered-by-ADR:ADR-0017` + `covered-by-ADR:ADR-0033` (the 4-cycle cap is ADR-0017's decision; symmetric D-12 application is ADR-0033's) |
| IN-011 | The recipe-feature-pipeline orchestrator skill's overall structure and 12-substantive-state machine reference (the canonical schema reference per PRD NFR-5-a). | `design-claude-code` (option b moves state-machine logic into this skill), `plan-author` | `codebase-topic` (collapsed into IN-004 — same file; named here for traceability) |
| IN-012 | Naming conventions for any new sub-agent, skill, or ADR the design might introduce. | `design-claude-code`, `design-composer` (ADR authoring) | `covered-by-ADR:ADR-0019` |
| IN-013 | The "no silent scope changes" / kill-criterion-#1 pause-and-rescope discipline that PRD FR-2 ratifies. | `design-claude-code`, the orchestrator at the gate that emits the posture | `covered-by-ADR:ADR-0029` + `covered-by-ADR:ADR-0033` |
| IN-014 | How sub-agents are documented and discoverable in this project (the 35-file inventory under `.claude/agents/`); design-time conventions for primitive selection (subagent vs skill vs hook). | `design-claude-code` | `covered-by-KB:KB-cc-design:SKILL.md` (the design-half SKILL, plus its `references/patterns-and-anti-patterns.md` if a primitive-selection question arises) |
| IN-015 | ADR placement convention — where ADRs live, when to move them between `adrs/` and `adrs-migrated/`. | `design-composer` (authors any new ADR per PRD FR-8) | `covered-by-ADR:ADR-0036` |

**FR mapping for codebase-topic information needs** (the contract with `discovery-codebase-researcher`):

| Codebase Need | Consumes for | Cited PRD FRs |
|---|---|---|
| IN-002 (execute-orchestrator shape) | Design rewrites/retires this agent | FR-3, FR-4 (file 2 in inventory) |
| IN-003 (four specialists shape) | Design preserves substantive responsibilities; redesigns dispatch interfaces | FR-3-b, FR-4-c (files 3–6 in inventory) |
| IN-004 / IN-011 (recipe-feature-pipeline) | Design option (b) folds state-machine into the parent skill; canonical schema reference lives here | FR-3, FR-4-b, NFR-5-a (file 1 in inventory) |
| IN-005 (Agent-declaring sweep) | Inventory artifact per FR-5; informs cleanup-as-blocker check | FR-5-a, FR-5-b |
| IN-006 (checkpoint + log schemas) | Schema-changes-in-lockstep with the canonical reference | FR-4-b, NFR-5-a, NFR-6-a/b (files 7–8 in inventory) |
| IN-007 (blast radius) | Open-item user check if any edit would escape the 8-file inventory | AC-FR-4-a |

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. The researcher's input is this Research Plan; the output is `codebase-analysis.json` per the ADR-0018 + ADR-0038 schema v1.1.0 (blast-radius extended).

### Touch points

Specific files in scope. The PRD's affected-files inventory (FR-4) defines the primary touched surface; the researcher uses these as starting points for graph traversal.

- `.claude/agents/execute-orchestrator.md` — the defective agent; frontmatter (line 6) declares `tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` but the runtime surface excludes `Agent` (per analysis §1). Read in full: frontmatter, body, every section describing dispatch behavior. (IN-002; FR-3, FR-4)
- `.claude/agents/execute-task-code-producer.md` — specialist; read frontmatter `tools:`, body responsibilities, expected dispatcher contract, return shape. (IN-003; FR-3-b, FR-4-c)
- `.claude/agents/execute-task-quality-handler.md` — specialist; same depth as code-producer. Note the D-2a/c/d verdict interface specifically. (IN-003; FR-3-b, FR-4-c)
- `.claude/agents/execute-phase-quality-reviewer.md` — specialist; same depth. Note the 5-dimensional phase-verdict interface. (IN-003; FR-3-b, FR-4-c)
- `.claude/agents/execute-finalize-reconciler.md` — specialist; same depth. Note the dispatch-matrix routing (D-12 / D-13 / D-14) the agent applies. (IN-003; FR-3-b, FR-4-c)
- `.claude/skills/recipe-feature-pipeline/SKILL.md` — the parent orchestrator that did the workaround dispatch on 2026-05-23. Specifically: where (which step) it invokes `execute-orchestrator`, what arguments it passes, what state it expects back, the location of the canonical schema reference for `checkpoint.json` / `state-transitions.log`, and the 12-substantive-state machine reference. (IN-004 / IN-011; FR-3, FR-4-b, NFR-5-a)
- `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json` — the in-flight artifact carrying the `execution_pipeline_state_transitions` and `execution_mode` fields. Read for current field shapes. (IN-006; FR-4-b, NFR-6-a/b)
- `working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log` — the in-flight artifact carrying the per-dispatch transition log format. Read for current format/schema. (IN-006; FR-4-b, NFR-6-a/b)
- `.claude/agents/*.md` (full directory) — enumerate every sub-agent file with `Agent` in its `tools:` array (FR-5 inventory sweep). For each match: record file path, declared tool list, current dispatch purpose (1-line from body), and a note on whether the §6 design would impact the file's dispatch posture. (IN-005; FR-5-a)

### Blast-radius questions

Per ADR-0018 + ADR-0038, blast-radius analysis is part of codebase analysis. Questions for each touch point above:

1. **For `execute-orchestrator.md`**: which files reference this agent by name? (Expect: `recipe-feature-pipeline/SKILL.md` at the dispatch site; possibly other recipe skills.) Which sub-agents are named in its body as dispatch targets? (Expected: the four specialists.)
2. **For each of the four specialist agents**: which files reference them by name? Which agents declare these specialists as their dispatch targets? Are there test-feature artifacts that exercise them?
3. **For `recipe-feature-pipeline/SKILL.md`**: which CLAUDE.md or other skills reference this skill? Which step in the recipe currently invokes `execute-orchestrator`? Identify candidate insertion points for option (b) — retire `execute-orchestrator` and fold its state-machine into this skill.
4. **For `checkpoint.json` / `state-transitions.log`**: which files read or write these artifacts? Which sub-agents append entries? Where is the canonical schema documented (expected: `recipe-feature-pipeline/SKILL.md`)?
5. **Whole-repo blast-radius preview**: are there files OUTSIDE the 8-file inventory (PRD FR-4) that would be touched by any of the three §6 options? If yes, the researcher records them with a 1-sentence "why touched" rationale — this list becomes an open-item user check at the Synthesis stage per AC-FR-4-a.

Record findings in `codebase-analysis.json`'s `blast_radius` section, including `hop_tier_distribution` per ADR-0038.

### Convention discovery

What existing patterns must the design respect? The chosen §6 option must conform to:

- **Sub-agent frontmatter conventions** — `name:`, `description:`, `tools:`, `model:`, `effort:`, `skills:`, `memory:` per KB-cc-platform/references/extensions.md and ADR-0022. Researcher confirms what shape the existing 35 sub-agent files actually use, and whether any deviation exists today.
- **Skill SKILL.md conventions** — `name:`, `description:`, `allowed-tools:`, body structure (Contents → When this KB is loaded → routing tables). Researcher confirms `recipe-feature-pipeline/SKILL.md`'s current shape.
- **State-machine documentation conventions** — how the 12-substantive-state machine is referenced today (canonical location, shape of state names, transition descriptions). Option (b) folds state-machine logic into a different skill; option (a) flattens dispatch; either needs to respect this convention.
- **Audit-trail conventions** — `state-transitions.log` line format; `checkpoint.json` field layout; per-dispatch entry conventions. The repair must preserve the load-bearing audit-trail properties documented in analysis §3.2.

### Specific queries / grep targets

The researcher may use any of:

- Grep `\.claude/agents/.*\.md` for the literal token `Agent` in `tools:` arrays — produces IN-005 inventory.
- Grep `\.claude/skills/.*/SKILL\.md` for references to `execute-orchestrator` or `execute-task-*` — finds the dispatch sites that would change under §6 option (a) or (b).
- Grep `recipe-feature-pipeline/SKILL.md` for `checkpoint.json`, `state-transitions.log`, `execution_pipeline_state_transitions`, `execution_mode` — locates the canonical schema reference per NFR-5-a.
- Grep the whole repo for `execute-orchestrator` or `execute-finalize-reconciler` — surfaces any references outside the 8-file inventory (blast-radius preview).

The researcher chooses precise Cypher queries or grep patterns based on the touch points; the above are recommended starting points, not a mandate.

## External research topics

Per ADR-0021, external research is conditional on documented KB gaps. Default budget: 6 topics. This Plan uses **1 of 6** topics.

### T-001 — Claude Code sub-agent tool-grant semantics for `Agent`

| Field | Value |
|---|---|
| **Topic ID** | `T-001` |
| **Name** | `claude-code-subagent-tool-grant-semantics` |
| **Priority** | P1 |
| **Research question** | When a Claude Code sub-agent declares `Agent` in its `tools:` frontmatter array, is the sub-agent able to dispatch other sub-agents at runtime? If not, why does the harness strip or rewrite the tool surface (per the observation that `execute-orchestrator`'s runtime surface excludes `Agent`, `Glob`, `Grep`, `TaskUpdate` and adds an undeclared `Edit`)? Is there a frontmatter syntax variant, harness flag, or configuration mechanism that enables sub-agent → sub-agent dispatch? |
| **KB gap justification** | **KB-cc-platform verification performed**: read `SKILL.md` (full); read `references/extensions.md` lines 140–215 (the sub-agent section) and the cross-reference table at 519–529 (Subagent vs Agent team). KB-cc-platform documents the `tools:` frontmatter array as a *restriction* mechanism ("`tools:` frontmatter limits what the subagent can do … cannot edit anything by construction"). It documents the seven primitives and their frontmatter shapes. It does NOT document: (a) whether the `Agent` tool is grantable to a sub-agent at all, (b) whether the harness's runtime sub-agent tool-surface honors `Agent` when declared, (c) what the rewrite/strip behavior is when the declared tool list contains entries the harness disallows, (d) whether any documented or undocumented configuration enables sub-agent → sub-agent dispatch. The "Subagent vs Agent team" comparison hints that sub-agents are designed as terminal nodes ("Reports back to lead only") and that the cross-agent communication primitive is "agent teams (experimental, disabled by default)" — but it stops short of stating whether the `Agent` tool grant is honored at the sub-agent level. **ADR verification performed**: read `ADR-0022` (the closest existing ADR on sub-agent frontmatter, covers `model:` / `effort:` / `skills:` semantics with explicit Claude Code Agent SDK citations). ADR-0022 does NOT address the `tools:` field's runtime behavior — its scope is reasoning configuration (`model:`, `effort:`, `skills:`), not the tool grant. No other ADR addresses this. **Designer-general-knowledge filter**: this is NOT a question a competent designer would just know; it is harness-runtime behavior that requires sourcing from Claude Code's own documentation, the SDK source, or a primary probe. The question is novel to this project. |
| **Acceptance criteria** | A definitive answer in one of three buckets: (a) **supported** — sub-agent → sub-agent dispatch via `Agent` in `tools:` works under some named condition (frontmatter syntax variant, flag, configuration); (b) **not supported** — the harness strips/rewrites the surface as a design choice and there is no in-supported-band path to enable it; (c) **partially supported / under conditions** — works only in named cases (e.g., specific transport modes, specific SDK versions, specific permission modes). The answer must be backed by EITHER (i) an official Anthropic Claude Code documentation citation with stable URL and quoted text, OR (ii) an executed minimal probe sub-agent test (see "Probe execution" below) whose result is documented with the runtime tool surface the probe reports. The note must cite specific Claude Code version or release identifier (e.g., a date stamp from docs.anthropic.com or code.claude.com). The note must explicitly answer the four sub-questions the analysis raises in §4: (1) is `Agent` grantable; (2) is the tool-surface strip/rewrite documented; (3) is there a known workaround at the harness level; (4) are there precedents in published Anthropic skills / agent libraries for sub-agent → sub-agent dispatch. |
| **Source constraints** | **Authoritative sources only:** (a) Anthropic's official Claude Code documentation — `code.claude.com/docs/en/sub-agents.md`, `code.claude.com/docs/en/agent-teams.md`, `code.claude.com/docs/en/settings.md`, `code.claude.com/docs/en/tools-reference.md`, `code.claude.com/docs/llms.txt` index. (b) Anthropic's Claude Code Agent SDK reference (Python or TypeScript) — `code.claude.com/docs/en/agent-sdk/*`. (c) Claude Code release notes and changelog. (d) Primary-source published Anthropic skill / sub-agent examples (e.g., examples cited in the official docs that demonstrate or rule out sub-agent → sub-agent dispatch). (e) The probe sub-agent's own runtime report (see below). **NOT acceptable**: stale blog posts (pre-2026), AI-generated summaries, GitHub issues without an Anthropic-staff response, frontmatter-inference without runtime verification. |
| **Probe execution** | The note is incomplete without an actual probe result. The probe is part of T-001's acceptance-criteria validation, not deferred to per-layer Design. Mechanism: `discovery-external-researcher` (or a probe sub-agent it dispatches) authors a minimal sub-agent at `.claude/agents/probe-dispatch-test.md` declaring `tools: [Read, Agent]` and a body that asks the sub-agent to attempt to dispatch a second probe sub-agent. The researcher invokes the first probe; the first probe attempts to dispatch the second; the runtime tool surface and outcome (success / failure / strip-behavior) are recorded. Cleanup: probe sub-agent files are removed at the end of T-001 (the probe is research instrumentation, not a persistent artifact). The probe result is the load-bearing evidence the per-layer `cc` Designer uses to choose among the three §6 options. **If the probe cannot be executed safely** (e.g., harness side-effects, doc-only research environment), the researcher records this explicitly as a probe limitation and falls back to documentation-only evidence — but the limitation must be surfaced so the Synthesis stage can decide whether the documentation evidence is sufficient. |
| **Expected output shape** | A research note at `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md` containing: (i) the four-sub-question answer; (ii) source citations with URLs and quoted text; (iii) the probe execution report (probe-agent files, invocation result, runtime tool surface observed); (iv) a `dispatch_supported: {true,false,partial}` flag that downstream FR-2 / FR-3 can branch on; (v) a `kill_criterion_triggered: {1, 2}` annotation that synthesizes into the kill-criterion decision per PRD §Rollout Plan. |

**Topic count: 1 of 6 budget.** No additional topics are authorized. Per the discipline file: "If only Topic 1 is justified, the plan can have a single external topic — that's acceptable per ADR-0021 if every topic is genuinely justified."

**Topics considered but rejected**:

- *`subagent-dispatch-patterns-from-anthropic-skills-library`* — considered as a P2. Rejected because: (a) it would duplicate T-001's source-base (the same Claude Code documentation pages already enumerate or rule out cross-sub-agent dispatch); (b) T-001's acceptance criterion (4) already requires citing precedents in published Anthropic skills / agent libraries, so the sub-question is folded into T-001 rather than fanned out; (c) keeping the topic count to 1 sharpens the research focus on the load-bearing question.
- *`bash-script-as-dispatch-surface-precedents`* — considered as a P3. Rejected because: (a) §6 option (c) (Bash-script dispatch surface) is one of three design options the per-layer Designer chooses among; researching it pre-emptively biases the choice; (b) if the design selects option (c), KB-cc-platform already documents the Hook primitive and the Bash tool extensively (KB-cc-platform/references/extensions.md §5 Hooks; KB-cc-platform/references/configuration.md on `Bash` permissions); a competent designer applies these with documented rationale (designer-general-knowledge). External research is unnecessary unless the designer surfaces a specific gap during Design.

## Topics explicitly NOT researched

Per ADR-0021, this section is the visible artifact of the KB-and-ADR-first discipline. For each information need with disposition `covered-by-KB` or `covered-by-ADR`:

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-008 | KB-cc-platform/references/extensions.md (lines 142–174, the sub-agent section) | The `tools:` frontmatter is documented as an array form (`tools: Read, Grep, Glob`) with restriction semantics. The tool list limits what the sub-agent can do; restricting to `Read, Grep, Glob` prevents edits by construction. The general parsing rules are documented; what is NOT covered (the `Agent` tool's specific runtime behavior, the strip/rewrite mechanism) is folded into T-001's external research. |
| IN-009 | ADR-0022 v1.0.0 | Sub-agent reasoning configuration is intentional and audited. `model:` picks the model; `effort:` controls reasoning depth; `skills:` preloads SKILL.md content. The audit posture (auditing-subagents SA-13 BLOCKER check) is established. Any new sub-agent the §6 design introduces conforms to this. |
| IN-010 | ADR-0017 (4-cycle cap) + ADR-0033 (symmetric D-12 application) | The 4-cycle cap is per-task and per-phase; ADR-0033 codifies the symmetric application of D-12 at both boundaries. The dispatch matrix definitions (D-2a/c/d, D-12, D-13, D-14) are downstream of these ADRs and the Blueprint's dispatch-matrix section. The repair preserves these as load-bearing invariants per PRD FR-3-c — no research needed. |
| IN-012 | ADR-0019 v1 | Sub-agent and skill naming uses role/stage prefix conventions; any new sub-agent or skill the §6 design introduces follows this. No research needed. |
| IN-013 | ADR-0029 + ADR-0033 | No silent scope changes: scope-class shrinks from FULL to MINOR/PATCH require an explicit gate, not silent mid-run shrink. ADR-0033 extends this to execution-phase scope changes. PRD FR-2's kill-criterion-#1 pause-and-rescope is the application of this discipline to the investigation outcome. |
| IN-014 | KB-cc-design/SKILL.md (and its references/patterns-and-anti-patterns.md if a primitive-selection question arises) | The design-half KB covers primitive selection (CLAUDE.md vs rule vs skill vs subagent vs hook vs MCP vs plugin) and the design discipline. The per-layer `design-claude-code` agent loads this KB to choose among the §6 options. |
| IN-015 | ADR-0036 v1 | ADRs live in a single canonical location (`adrs/` for active; `adrs-migrated/` for legacy per the migrated-ADR analysis). Any new ADR the design composer authors lands in `adrs/`. |

These dispositions are auditable: a reviewer at the Research Plan Approval Gate can open each cited KB/ADR and confirm coverage.

## Estimated effort

- **Codebase research effort**: **medium**. The touch points are well-defined (8 files in the PRD inventory) but the researcher must additionally enumerate every sub-agent with `Agent` in `tools:` (FR-5 sweep over `.claude/agents/*.md`, 35 files) and perform a whole-repo blast-radius preview to confirm no edits escape the 8-file inventory. The schema-shape reads on `checkpoint.json` and `state-transitions.log` are quick.
- **External research topic count**: **1 of 6 budget**.
- **Estimated wall-clock**: 1 × codebase-researcher serial pass (single instance) + 1 × external-researcher (single topic, but requires a documentation review AND a probe sub-agent execution). The probe execution is the long-pole — the researcher authors a minimal probe sub-agent, invokes it, observes the runtime tool surface, cleans up. Synthesis fan-in is trivially small (1 external note + 1 codebase analysis).

## Special discipline note for this run

**The investigation outcome materially shapes the design and gates the kill-criterion-#1 vs kill-criterion-#2 branch per PRD FR-2 / FR-3.** Specifically:

- If T-001 returns `dispatch_supported: true` (kill-criterion-#1), the Synthesis stage emits the `kill-criterion-1-triggered` posture; the run halts cleanly at the next gate; the per-layer `cc` Design / ADR / Plan / Execution stages are not invoked in this run; a fresh follow-on feature is opened for the one-flag fix.
- If T-001 returns `dispatch_supported: false` (kill-criterion-#2), the Synthesis stage commits to the FULL repair; the per-layer `cc` Designer chooses among the three §6 options (a) flatten / (b) retire / (c) Bash-script, constrained by the investigation outcome and the load-bearing invariants.
- If T-001 returns `partial` or is inconclusive (`probe could not be executed safely` AND documentation is silent), the operator pauses at the Research Plan / Synthesis transition and surfaces the ambiguity as an open item per the PRD Risks table (Risk 1).

The codebase research scope is independent of the T-001 outcome — both kill-criteria branches consume the codebase-analysis.json to ground their downstream decisions. Therefore `discovery-codebase-researcher` runs regardless.

## Open questions for human resolution

The following items the Research Plan cannot resolve without operator input. Each surfaces at the Research Plan Approval Gate.

1. **Probe execution authority**. The probe sub-agent for T-001 will author a temporary `.claude/agents/probe-dispatch-test.md` file (cleaned up at the end). Is this acceptable, or does the operator want the probe to occur in a more isolated mechanism (e.g., a separate worktree, a scratch slug)? The plan recommends the in-place author-and-cleanup approach as the lowest-overhead mechanism that exercises the actual harness.
2. **External-research budget**. The Plan uses 1 of 6 budget slots. The operator can either confirm (typical) or request additional topics if they have a research question this Plan missed. The two rejected topics (subagent-dispatch-patterns-from-anthropic-skills-library; bash-script-as-dispatch-surface-precedents) are available to reactivate if the operator disagrees with the rejection rationale.
3. **Blast-radius open-item threshold**. AC-FR-4-a says any edit outside the 8-file inventory triggers an open-item user check. The Research Plan recommends the codebase-researcher flag any file the §6 options would touch outside the inventory and surfaces these as open items at the Synthesis stage — does the operator want a tighter or looser threshold?
4. **Probe inconclusiveness handling**. If T-001's probe execution fails (harness side-effects, the second-level dispatch hangs, etc.) AND the official documentation is silent on the precise question, does the operator want the run to halt for re-scoping, or to advance with documentation-only evidence and a documented confidence-level annotation? The Plan recommends halt-for-rescoping per PRD Risk 1.
