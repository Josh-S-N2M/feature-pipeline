---
id: DesignDoc-cc-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: DesignDoc
subsection: cc
version: 1.0.0
status: draft
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
scope_class: FULL
layer_scope: [cc]
derived_from:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-dependencies.json
  - Issues/analysis-execute-orchestrator-dispatch-limitation.md
generated: 2026-05-23T20:22:35Z
generated_by: design-cc
inherited_adrs:
  - ADR-0017
  - ADR-0019
  - ADR-0021
  - ADR-0022
  - ADR-0027
  - ADR-0029
  - ADR-0033
  - ADR-0035
  - ADR-0036
  - ADR-0037
  - ADR-0040
  - ADR-0041
---

# Claude Code Design — execute-orchestrator Dispatch Mechanism Repair (r1)

## 1. Layer responsibility scope

This is a **cc-only** feature; this subsection is the Blueprint's design substance. The Claude Code / Project Filesystem layer owns:

- The 4 execution-side specialist sub-agents (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`) — their YAML frontmatter `tools:` declarations, their body-prose dispatch protocols, their reasoning configuration triplets.
- The `execute-orchestrator` sub-agent's posture (preserved-as-advisor vs retired) and `Agent`-grant cleanup.
- The `recipe-feature-pipeline` orchestrator skill — specifically a new "Execution Phase Dispatch" section and the canonical `checkpoint.json` schema reference at lines 96–128.
- The `state-transitions-log-entry-template.md` per-entry schema (the `invoking_agent` v1 invariant carries forward conditionally).
- One project-wide convention proposal (sub-agent `Agent`-grant prohibition) which is surfaced as a Q-CC item for `design-composer` to ratify as an ADR.

Eight other taxonomy layers (frontend, backend, api, query, database, cicd, iac, codespaces) are N/A.

## 2. Chosen §6 option — option (a) flatten dispatch hierarchy

**Decision (D-001 from synthesis §3.1):** Option (a) — flatten the dispatch hierarchy. The parent `recipe-feature-pipeline/SKILL.md` becomes the direct dispatcher of the 4 execution-side specialists. `execute-orchestrator.md` is **retained as a state-machine advisor / reference document** with its `Agent` declaration removed; its body becomes the canonical narrative of the 12-substantive-state machine that the parent skill's new "Execution Phase Dispatch" section operationalizes.

The Designer ratifies the framer-and-substrate joint recommendation. Three reasons that survived primitive-selection discipline:

1. **PRD FR-4 8-file inventory compliance (AC-FR-4-a).** Option (a) touches 4 files (3 in-inventory + 1 outside-inventory: `state-transitions-log-entry-template.md:63` invariant) → exactly 1 operator open-item. Option (b) escapes by ≥5 files (see §3.2 below). Option (c) introduces a new dispatch script with the same outside-inventory cost as (a) but worse pattern fidelity.
2. **Specialist-isolation audit-trail preservation (PRD Constraint B, analysis §3.1).** With the parent dispatching the 4 specialists directly at the main-conversation level (where dispatch IS supported per T-0001), each specialist invocation crosses a distinct sub-agent boundary. Per-dispatch `state-transitions.log` entries, per-task and per-phase cycle counters, and dispatch-matrix routing through `execute-finalize-reconciler` are all preserved. The four load-bearing properties documented in analysis §3.2 survive.
3. **State-transitions-log v1 `invoking_agent` invariant preservation (synthesis §3.1).** Option (b) would force the v1 invariant ("always `execute-orchestrator`" per `state-transitions-log-entry-template.md:63`) to be revised or replaced — promoting D-004 to ADR-worthy schema-ownership transfer. Option (a) preserves the invariant by reinterpreting its meaning: `execute-orchestrator` remains the **logical owner** of the state machine (its body is the canonical reference), even though the **emitter** is the parent orchestrator. This matches the in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` already in the field (workaround run, every entry has `invoking_agent: "execute-orchestrator"`).

### 2.1 Why options (b) and (c) were rejected

**Rejected — option (b) retire `execute-orchestrator` entirely.**

- Escapes FR-4 inventory by ≥5 files (`KB-documentation-criteria/SKILL.md:67–71` template assignments; `state-transitions-log-entry-template.md:63` v1 invariant; `pipeline-run-summary-template.md:113` generated-by; `smoke_test_auditing_shared.py:212` test data; `auditing-codespaces/SKILL.md:73` consumer note). Triggers AC-FR-4-a operator gate with the widest possible surface.
- Breaks the state-transitions-log v1 `invoking_agent` invariant (synthesis §3.1 anchor evidence — CR-0079 / CR-0080 / CR-0135). Promotes D-004 from "schema-section edit" to "schema-ownership transfer + ADR-worthy decision".
- Doubles effort vs option (a) for equivalent functional outcome.
- Per substrate-analysis (codebase-analysis §blast_radius `option_b_retire_execute_orchestrator`), open-item count under AC-FR-4-a is `5+ (NEEDS USER CHECK)`. Option (a)'s open-item count is 1.

**Rejected — option (c) Bash-script dispatch surface.**

- Equivalent outside-inventory cost to (a) (1 file: a new dispatch script) but **lowest pattern fidelity**: specialists invoked via Bash sub-process rather than agent-graph dispatch bypasses the harness's per-agent transcript / per-agent state-transitions logging. The script becomes the audit boundary, not the agent — the very property the repair must preserve is degraded (analysis §3.2 / AN-0037).
- T-001 (claim T-0064) treats (c) as physically possible but not preferred. Anthropic's documented alternatives (Skills, chain-from-main) are stronger if indirection is desired — but per T-0001 chain-from-main IS option (a).

### 2.2 Carry-through from synthesis to this Design

- **DISSENT-2 attribution discipline.** This Design subsection and all downstream artifacts cite ADR-0017 (the 4-cycle cap) + ADR-0033 (symmetric D-12 application). The PRD FR-3-c phrase "ADR-0034 symmetric D-12 application" was a documentary mis-credit (cleaned surgically post-Gate-2 per ADR-0033 §line 71). This subsection does NOT propagate the mis-credit. Note `execute-finalize-reconciler.md:19` body still cites ADR-0034 for symmetric application; that line is corrected as part of the D-003 edit (see §6).
- **F-7 mid-session agent registry constraint (synthesis §4).** No new sub-agent files are authored by this feature. Existing sub-agents are edited only. The synthetic minimal test feature for FR-6 verification (designed by `plan-author`) is invoked in a **fresh session** after this run's authoring tasks complete. Documented as an AC below and as a sequencing constraint in `cc-dependencies.json`.

## 3. Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | Parent orchestrator skill; gains a new "Execution Phase Dispatch" section (§4 below) AND closes the canonical `checkpoint.json` schema-reference gap (D-004 / §5 below). Load-bearing file — single-file shared pressure (synthesis §5.1) | **modified** (additive; ~3 PW combined across D-001 + D-004) |
| `.claude/agents/execute-orchestrator.md` | Re-scoped from dispatcher to **state-machine advisor / canonical reference**. `Agent`, `TaskUpdate` removed from `tools:`. Body retained as the canonical 14-row state-machine narrative; "Per-task loop" / "Per-phase loop" sections re-framed as "what the parent orchestrator MUST execute when invoking specialists" rather than "what this agent does" | **modified** (frontmatter + body re-framing) |
| `.claude/agents/execute-task-code-producer.md` | Specialist; substantive responsibilities unchanged per PRD FR-3-b. Body's "dispatched by execute-orchestrator at T1" prose updated to "dispatched by recipe-feature-pipeline parent orchestrator at T1" | **modified** (prose-only) |
| `.claude/agents/execute-task-quality-handler.md` | Specialist; substantive responsibilities unchanged. Body prose update parallel to code-producer | **modified** (prose-only) |
| `.claude/agents/execute-phase-quality-reviewer.md` | Specialist; substantive responsibilities unchanged. Body prose update parallel to code-producer | **modified** (prose-only) |
| `.claude/agents/execute-finalize-reconciler.md` | Specialist + Contract 4 dispatch-matrix router. `Agent` removed from `tools:` (D-003 / §6 below). Body line 19 ADR-0034 reference corrected to ADR-0033. Body line 76 "Dispatch via Agent" prose re-framed: reconciler emits a `dispatch_directives[]` array in `quality-reconciliation-log.json` that the parent orchestrator consumes (parent then dispatches via Agent at the main-conversation level) | **modified** (frontmatter + body re-framing + ADR citation fix) |
| `working/feature/<slug>/checkpoint.json` schema (canonical reference) | Documented in `recipe-feature-pipeline/SKILL.md:96–128`. Gains 3 new execution-phase fields: `execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`. De facto schema in `devcontainer-mcp-provisioning-r1/checkpoint.json` becomes documented schema | **modified** (canonical-reference update in lockstep with §4 — D-004) |
| `working/feature/<slug>/state-transitions.log` per-entry schema | Documented in `state-transitions-log-entry-template.md`. The v1 `invoking_agent` invariant at template line 63 is **clarified, not changed**: `invoking_agent` is the logical owner of the state transition (i.e., `"execute-orchestrator"`), not the literal emitting agent. The de facto extensions observed in the in-flight log (`void: true` + `void_reason`; transition-name `-prime` suffix) are folded into the template as documented v1 extensions | **modified** (outside-inventory; 1 file → AC-FR-4-a open-item count = 1) |

## 4. The "Execution Phase Dispatch" section (new `recipe-feature-pipeline/SKILL.md` content)

The parent orchestrator skill's existing Step 14 ends at Gate 6. The new "Execution Phase Dispatch" subsection slots in **after** Gate 6 approval (as Step 15, or as a labeled "Stage 14: Execution Phase Dispatch" depending on `plan-author`'s preference). Per Principle 1 (lowest-cost primitive) this content lives in the existing parent skill rather than a new sub-agent — there is no isolation gain (per Principle 4) because the parent already runs the dispatch loop at the main-conversation level.

The content scope (`plan-author` decides exact prose):

1. **State machine reference.** A pointer to `.claude/agents/execute-orchestrator.md` body (lines 24–43 + the per-task / per-phase loop sections) as the canonical narrative. The parent skill does NOT duplicate the 14-row state table (Principle 5 — one source of truth).
2. **Per-task dispatch loop.** A 6-step procedure: (1) read next task from `tasks.json` DAG; (2) verify dependencies APPROVED; (3) invoke `execute-task-code-producer` via Agent with task-spec payload; (4) emit T0/T1 state-transition entries via `auditing-shared/scripts/log_state_transition.py`; (5) on COMPLETED → invoke `execute-task-quality-handler`; (6) loop on quality verdict per Contract 1 (APPROVED → next task; NEEDS_REVISION → re-invoke code-producer with revision context, increment per-task cycle counter; STUB_DETECTED → T5 escalation; BLOCKER → user escalation).
3. **Per-task cycle cap enforcement.** ADR-0017 4-cycle cap, applied symmetrically per ADR-0033 D-12. The parent reads/writes the counter in `checkpoint.json.execution_pipeline_cycle_counters.per_task[<task-id>]`. On cycle 4 without resolution: emit T13 to TERMINATED with `trigger: cycle-cap-exhaustion`, write `escalation-cycle-cap.json`, surface to user.
4. **Per-phase dispatch loop.** A 4-step procedure: (1) when all tasks in current phase APPROVED → invoke `execute-phase-quality-reviewer` (T7); (2) on PASS → next phase OR pipeline_complete (T8/T12); (3) on NEEDS_RECONCILIATION → invoke `execute-finalize-reconciler` (T9); (4) reconciler returns `quality-reconciliation-log.json` with a `dispatch_directives[]` array → parent iterates, dispatching the named upstream agents via Agent (T10 increments per-phase cycle counter).
5. **Per-phase cycle cap enforcement.** Same as per-task; counter in `checkpoint.json.execution_pipeline_cycle_counters.per_phase[<phase-id>]`.
6. **State-transition logging discipline.** For every transition, invoke `auditing-shared/scripts/log_state_transition.py` with `invoking_agent: "execute-orchestrator"` (the logical owner per the preserved v1 invariant). Failure is observer-only per D-16.
7. **Termination.** On pipeline_complete (T12): write `pipeline-run-summary.json`; update `checkpoint.json.current_stage = "complete"`.

This section is the operational mechanization of `execute-orchestrator.md`'s body. The advisor file documents the WHAT (state machine semantics); the parent skill documents the HOW (the dispatch procedure the parent runs).

## 5. Schema closure (D-004)

`recipe-feature-pipeline/SKILL.md` lines 96–128 currently document only the planning-side `checkpoint.json` shape. The execution-phase fields written in flight by `devcontainer-mcp-provisioning-r1` are de facto schema, not documented schema. Per NFR-5-a (canonical-reference consistency), the chosen option's edits to this file MUST close the gap in lockstep with the §4 dispatch-section addition.

New canonical schema shape for `recipe-feature-pipeline/SKILL.md:96–128`:

```json
{
  "run_id": "<run-id>",
  "feature_slug": "<slug>",
  "started_at": "<ISO 8601>",
  "current_stage": "intent_clarification | prd_authoring | discovery_planning | discovery_research | synthesis | per_layer_design | design_composition | architecture_audit | plan_authoring | test_authoring | cross_artifact_audit | task_decomposition | reconciliation | execution | complete",
  "stage_status": "pending | in_progress | awaiting_gate | passed | reconciling",
  "gate_history": [ ... ],
  "artifact_versions": { ... },
  "reconciliation_cycles": { "blueprint": 0, "cross_artifact": 1 },

  "execution_pipeline_state_transitions": [
    {
      "transition": "T0|T1|...|T13",
      "from": "<state>",
      "to": "<state>",
      "timestamp": "<ISO 8601>",
      "trigger": "<free-form rationale>"
    }
  ],
  "execution_mode": "specialist-isolation | single-agent-fallback",
  "execution_pipeline_cycle_counters": {
    "per_task": { "<task-id>": 0 },
    "per_phase": { "<phase-id>": 0 }
  },

  "activated_layers": [ ... ],
  "extraction_method": "gitnexus | manual-grep-and-read",
  "params": { ... }
}
```

Three notes:

- `current_stage` enum gains `"execution"` (it currently jumps from `"complete"` after Gate 6 back to a hardcoded "complete" — no `execution` state). `plan-author` decides whether `"execution"` is a single value or split into per-substantive-state values; the substrate analysis prefers a single `"execution"` value with the substantive state in `execution_pipeline_state_transitions[-1].to`.
- `execution_mode` is documented with two named values: `"specialist-isolation"` (the repaired pattern) and `"single-agent-fallback"` (the workaround pattern observed in the in-flight artifact). NFR-6-b compatibility marker.
- `execution_pipeline_state_transitions[].void` and `void_reason` are documented as v1 extensions (observed in `devcontainer-mcp-provisioning-r1/state-transitions.log:2`). Closes OI-CR-D in lockstep. Similarly the transition-name `-prime` suffix convention is documented.

The schema-section edit and the §4 dispatch-section addition are **the same edit set** on the same file. `plan-author` MUST sequence them coherently (synthesis Constraint 5.1).

## 6. FR-5 cleanup (D-003) — remove `Agent` from `execute-finalize-reconciler`

Per FR-5 sweep (codebase-analysis §fr5_inventory_sweep) the affected set closed at exactly 2 agents: `execute-orchestrator` and `execute-finalize-reconciler`. Both declare `Agent` in their `tools:` arrays; both are subject to T-0001's prohibition.

**Cleanup applied in this feature (D-003.1, synthesis §3.3):**

- `execute-finalize-reconciler.md:6` `tools: [Read, Glob, Grep, Write, Agent]` → `tools: [Read, Glob, Grep, Write]`. **No replacement tool is added** — the reconciler does not directly invoke another agent under option (a). Instead it emits a `dispatch_directives[]` array in `quality-reconciliation-log.json` that the parent orchestrator consumes and dispatches per row.
- `execute-finalize-reconciler.md:19` body reference "ADR-0034" → "ADR-0033" (the canonical home for symmetric D-12; DISSENT-2 propagation per synthesis Constraint 5.4).
- `execute-finalize-reconciler.md:76` body sentence "Dispatch via Agent — invoke the target subagent with the revision_context payload." → "Emit a `dispatch_directives[]` array in `quality-reconciliation-log.json`; each row specifies `dispatch_target`, `revision_context`, and `rationale`. The parent orchestrator (per `recipe-feature-pipeline/SKILL.md` § Execution Phase Dispatch) reads the array and invokes each target via Agent at the main-conversation level."
- Parallel edits on `execute-orchestrator.md:6`: `tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` → `tools: [Read, Glob, Grep, Write, Bash(python3:*)]` (note: `TaskUpdate` is also removed — it never landed in the runtime surface per analysis §1.2 and the advisor role does not need it). `execute-orchestrator.md` becomes a reference document that the parent skill links to.

Evidence: `codebase-analysis-report.md`'s FR-5 sweep finding `affected_set_closed_at: 2`; T-001 claim T-0072 ("the `Agent` declaration is a misleading runtime no-op — cleanup-as-blocker applies"). `execute-finalize-reconciler` never reached T9 in the `devcontainer-mcp-provisioning-r1` run (workaround halted earlier), but the defect is structurally identical per the codebase-analysis "would-same-defect-manifest" inference (HIGH confidence).

**Bundled commit (synthesis Constraint 5.2):** both `Agent`-removals SHOULD ship in one commit; the commit message documents "FR-5 sweep closure: affected set = 2".

## 7. Sub-Agents Inventory

| Sub-Agent | Location | Phase | What It Does | Change |
|---|---|---|---|---|
| `execute-orchestrator` | `.claude/agents/execute-orchestrator.md` | execution-phase | **Re-scoped to advisor / state-machine reference.** No longer dispatched at runtime. Body remains the canonical narrative of the 12-substantive-state machine. | frontmatter (`tools:` `Agent` + `TaskUpdate` removed); body re-framing (sections become "what the parent orchestrator MUST execute" rather than "what I do") |
| `execute-task-code-producer` | `.claude/agents/execute-task-code-producer.md` | execution-phase | Authors code per task spec. Dispatched by parent (was dispatched by execute-orchestrator). | body prose only (dispatcher reference) |
| `execute-task-quality-handler` | `.claude/agents/execute-task-quality-handler.md` | execution-phase | Issues quality verdicts per Contract 1 (D-2a/c/d). Dispatched by parent. | body prose only |
| `execute-phase-quality-reviewer` | `.claude/agents/execute-phase-quality-reviewer.md` | execution-phase | 5-dimensional phase verdict per Contract 2. Dispatched by parent. | body prose only |
| `execute-finalize-reconciler` | `.claude/agents/execute-finalize-reconciler.md` | execution-phase | Classifies phase-quality findings + emits `dispatch_directives[]` for the parent to dispatch. Dispatched by parent. | frontmatter (`Agent` removed); body re-framing (lines 19, 76); ADR-0033 citation fix |

### 7.1 Per-sub-agent reasoning configuration (per ADR-0022, Principle 9)

No reasoning-configuration changes are made. The existing triplets are preserved as-is and re-verified for intentionality:

| Sub-Agent | `model:` | `effort:` | `skills:` | Verdict |
|---|---|---|---|---|
| `execute-orchestrator` | `opus` | `high` | `[KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]` | **PRESERVED**, but see Q-CC-3 on the `recipe-feature-pipeline` self-reference (OQ-CR-003) |
| `execute-task-code-producer` | `sonnet` | `medium` | `[ai-development-guide, KB-cc-design]` | PRESERVED — bounded transformation matches `sonnet`; per-task scope matches `medium` |
| `execute-task-quality-handler` | `sonnet` | `medium` | `[ai-development-guide, KB-cc-design, auditing-shared]` | PRESERVED — verdict issuance per Contract 1; sonnet/medium appropriate |
| `execute-phase-quality-reviewer` | `opus` | `high` | `[KB-cc-design, KB-review-disciplines, auditing-shared]` | PRESERVED — 5-dimensional cross-cutting reasoning matches `opus`; phase scope matches `high` |
| `execute-finalize-reconciler` | `opus` | `high` | `[KB-cc-design, KB-review-disciplines, auditing-shared]` | PRESERVED — dispatch-matrix classification across the 5 dimensions matches `opus/high` |

All `skills:` entries resolve to an existing `.claude/skills/<name>/SKILL.md` (verified by inspection). No `skills:` array is used to encode reasoning depth (per the SA-13 anti-pattern called out in KB-cc-design Principle 9).

## 8. Skills Inventory

| Skill | Location | When Triggered | What It Provides | Change |
|---|---|---|---|---|
| `recipe-feature-pipeline` | `.claude/skills/recipe-feature-pipeline/SKILL.md` | User invokes `/feature-pipeline` (the parent orchestrator skill) | The full 13-stage pipeline + the new Execution Phase Dispatch section; canonical `checkpoint.json` schema reference | **modified** — new section (§4) + schema-reference closure (§5). Load-bearing single-file pressure per synthesis §5.1 |

No new skills are introduced. Per Principle 1 (lowest-cost primitive): the new dispatch behavior fits inside the existing parent skill rather than a new skill, because there is no separate user-invoked entry-point — execution starts automatically after Gate 6 within the same pipeline run.

## 9. Hooks

| Hook Event | Script | Behavior | Failure Mode | Change |
|---|---|---|---|---|
| (existing) State-transition emission | `.claude/skills/auditing-shared/scripts/log_state_transition.py` | Bash-invoked from the parent orchestrator's per-transition step; writes one JSONL line to `working/feature/<slug>/state-transitions.log` | Observer-only per D-16; failure surfaces as Level-1 finding per AC-FR-5-e but does NOT block the substantive transition | **unchanged** — invocation site moves from `execute-orchestrator` body to the parent skill's "Execution Phase Dispatch" section, but the script and its REQUIRED_FIELDS are unchanged |

No new hooks. Per Principle 3 (enforce when safety-critical): the existing log-emission discipline is already an observer hook. No safety-critical guarantee is introduced by this feature beyond what already exists.

## 10. CLAUDE.md Updates

| File | Change | Rationale |
|---|---|---|
| Root `CLAUDE.md` | **No change** | The dispatch repair is a project-internal mechanism. No new convention requires every-request reminder (Principle 5 — one source of truth; the convention lives in `recipe-feature-pipeline/SKILL.md` and in the affected sub-agents' bodies). The proposed convention "sub-agents MUST NOT declare `Agent` in `tools:`" is a Q-CC-1 item for `design-composer` to elevate to an ADR — not a CLAUDE.md directive (Principle 7 / Principle 3) |

## 11. MCP Servers

| Server | Change |
|---|---|
| (existing servers per `.mcp.json`) | **No change** |

The execution-phase dispatch repair does not interact with MCP. ADR-0037 (mcp-events.jsonl) applies only if a §6 option introduces a new MCP-dispatch mechanism (e.g., option (c)); option (a) does not.

## 12. File Naming & Layout Conventions Introduced

None new. The repair operates entirely within existing conventions (ADR-0019 naming, ADR-0036 ADR placement, ADR-0027 cwd discipline).

## 13. Project Filesystem Error State Design

How does the feature behave when expected Claude Code constructs are missing or malformed?

- **`execute-orchestrator.md` missing or unreadable.** The advisor file is a documentation surface, not a dispatchable agent. The parent orchestrator's "Execution Phase Dispatch" section references it for the canonical state-machine narrative; if missing, the parent should surface a clear "advisor reference missing" error at Step 15 entry (before any dispatch). Implementation note for `plan-author`: a precondition check in the parent skill should verify `.claude/agents/execute-orchestrator.md` exists.
- **One of the 4 specialists missing.** The harness reports the missing agent in its loaded-agent-set error message (per T-001 F-7 finding). The parent surfaces this to the user before dispatching. Per F-7, no in-pipeline hot-reload remedy exists; the operator restarts the session.
- **`checkpoint.json` malformed (e.g., missing `execution_pipeline_cycle_counters`).** The parent orchestrator initializes the field with the documented v1 schema (per §5) on first execution-phase entry. Pre-existing in-flight artifacts (per NFR-6-a) are left as-is.
- **`auditing-shared/scripts/log_state_transition.py` fails.** Per D-16, observer-only; transition proceeds, failure surfaces as Level-1 finding. Unchanged from current discipline.

## 14. Acceptance criteria contribution

EARS-format ACs traceable to PRD FRs / NFRs. These propagate to `test-acceptance-author` for the synthetic minimal test feature (FR-6 verification surface).

**AC-CC-1 (FR-3-a, FR-3-c, this Design §2).** When the per-layer cc Design subsection is read by `design-composer`, the chosen §6 option shall be explicitly named as "option (a) flatten dispatch hierarchy" with rationale citing (i) PRD FR-4 8-file inventory compliance, (ii) state-transitions-log v1 `invoking_agent` invariant preservation, (iii) specialist-isolation audit-trail preservation, AND ADR-0017 + ADR-0033 (NOT ADR-0034) cited for the 4-cycle cap + symmetric D-12 application.

**AC-CC-2 (FR-4-a, this Design §3).** When the implementation phase completes, the system shall have modified exactly the 8 files in the PRD FR-4 inventory PLUS exactly 1 file outside the inventory (`state-transitions-log-entry-template.md` — to fold the `void` field + `-prime` suffix conventions into v1 and clarify the `invoking_agent` invariant). Any edit outside this 8+1 set shall trigger an AC-FR-4-a operator-gate open item.

**AC-CC-3 (FR-3-b, FR-4-c, this Design §3).** While the implementation phase is in progress, the four execution-side specialist sub-agents' substantive domain responsibilities (code production, quality handling, phase quality review, finalize reconciliation) shall remain unchanged — only their body-prose dispatcher-reference text and `execute-finalize-reconciler`'s frontmatter (`Agent` removed) and body lines 19/76 are modified.

**AC-CC-4 (FR-4-b, NFR-5-a, this Design §5).** Where the `recipe-feature-pipeline/SKILL.md` Execution Phase Dispatch section is added (D-001), the canonical `checkpoint.json` schema reference at the same file's lines 96–128 shall be updated in the same commit set to document the 3 execution-phase fields (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`) and the `void` / `-prime` extensions to the state-transitions log per-entry schema.

**AC-CC-5 (FR-5, this Design §6).** When the implementation phase completes, `execute-finalize-reconciler.md` shall have `Agent` removed from its `tools:` array, body line 19 ADR citation corrected from "ADR-0034" to "ADR-0033", and body line 76 "Dispatch via Agent" prose re-framed to "emit `dispatch_directives[]` in `quality-reconciliation-log.json`". Bundled with the `execute-orchestrator.md` `Agent`-removal in one commit.

**AC-CC-6 (FR-6, F-7 constraint, this Design §2.2).** While the FR-6 synthetic minimal test feature is being verified, the verification shall occur in a session distinct from the session that authors any new test-artifact sub-agent files (per the F-7 mid-session-agent-registry constraint documented in synthesis §4). If `plan-author`'s synthetic test feature design authors no new sub-agents, this constraint is vacuously satisfied; otherwise the plan MUST include an explicit operator session-restart step between the authoring task and the test-execution task.

**AC-CC-7 (NFR-2-a, NFR-2-b, this Design §4).** When the synthetic minimal test feature runs end-to-end against the repaired mechanism, the system shall emit at least one `state-transitions.log` entry per specialist sub-agent dispatch boundary, with `invoking_agent: "execute-orchestrator"` preserved as the v1 logical-owner invariant (clarified in §5).

**AC-CC-8 (NFR-3-a, this Design §4).** When the synthetic minimal test feature crosses a task or phase boundary, the parent orchestrator shall increment the corresponding cycle counter in `checkpoint.json.execution_pipeline_cycle_counters.per_task[<task-id>]` or `…per_phase[<phase-id>]`, observable post-run.

**AC-CC-9 (NFR-3-b, ADR-0017 4-cycle cap, this Design §4).** If a cycle counter reaches 4 without resolution, then the parent orchestrator shall halt with a TERMINATED transition `trigger: cycle-cap-exhaustion`, write `escalation-cycle-cap.json`, and surface to the user — NOT silently continue.

**AC-CC-10 (Q-CC-1 — see §15).** Where `design-composer` ratifies the proposed project-wide convention "sub-agents MUST NOT declare `Agent` in their `tools:` array" as an ADR (per synthesis §6.1 / D-005), an audit check shall be added (or the SA-13 audit's scope extended) to enforce the convention on every sub-agent under `.claude/agents/`. Conditional on the Q-CC-1 disposition; not authored in this feature.

## 15. Architectural Questions for Composer

**Q-CC-1 (synthesis §6.1 / D-005 disposition).** Should `design-composer` author a second project-wide ADR codifying the convention "sub-agents in this project MUST NOT declare `Agent` in their `tools:` frontmatter array" — generalizing the D-001 + D-003 cleanups into a roster-wide rule? Evidence: T-0001 establishes the prohibition as a deliberate Claude Code substrate constraint (3 independent Anthropic primary sources, synthesis §2.1). The FR-5 sweep result `affected_set_closed_at: 2` (both now cleaned) means the convention is currently honored — the ADR would prevent future violations. Options: (a) author the convention ADR in this feature (synthesis D-005.2 — rejected by synthesizer for scope reasons but the Designer flags it as worth re-considering at composition time); (b) defer to a separate documentation-conventions feature (synthesis D-005.1 — recommended); (c) capture the convention as an explicit constraint statement in the Blueprint (no ADR), with the SA-13 audit's scope extended to enforce. **Recommended:** option (a) — author the ADR in this feature, because the evidence base (T-0001's 3 sources) and the cleanup (D-003) are both in this run, and a follow-on feature would re-incur the source-citation work. Composer decides.

**Q-CC-2 (synthesis §6.1).** The primary ADR captures option (a)'s rationale over (b) and (c). Should this ADR explicitly inherit ADR-0017 + ADR-0033 (the 4-cycle cap + symmetric D-12 invariants) AND ADR-0019 (naming convention) AND ADR-0022 (sub-agent reasoning configuration) in its "Related ADRs" section, OR should those be implicit inheritances? Composer's `KB-documentation-criteria` discipline applies. Recommended: explicit inheritance (the affected sub-agents' frontmatter and body all touch ADR-0022 surface; the load-bearing invariants are ADR-0017 + ADR-0033).

**Q-CC-3 (codebase-analysis OQ-CR-003).** `execute-orchestrator.md:7` declares `skills: [KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines]`. The self-reference of a sub-agent declaring its own parent orchestrator skill (`recipe-feature-pipeline`) in its `skills:` array is unusual and may be a latent SA-13 finding under ADR-0022. Under option (a) the advisor file is preserved; the self-reference persists unless explicitly trimmed. Options: (a) trim `recipe-feature-pipeline` from `execute-orchestrator`'s `skills:` array as part of D-001 cleanup; (b) preserve as-is — the advisor file legitimately documents the state machine the parent skill orchestrates; (c) defer to a separate SA-13-audit-extension feature. Recommended: option (b) preserve, with explicit body-prose rationale ("this advisor documents the state machine the parent skill orchestrates; the self-reference is intentional"). Composer ratifies.

**Q-CC-4 (codebase-analysis OQ-CR-005, this Design §5 v1-invariant clarification).** The state-transitions-log v1 invariant at `state-transitions-log-entry-template.md:63` says "`invoking_agent` — always `execute-orchestrator` in v1". Under option (a) the **emitter** is the parent orchestrator but the **logical owner** is still `execute-orchestrator`. The in-flight `devcontainer-mcp-provisioning-r1/state-transitions.log` already shows `invoking_agent: "execute-orchestrator"` for every entry (the parent emitted on the orchestrator's behalf, per the workaround). This Design proposes to clarify the v1 invariant text to "`invoking_agent` is the LOGICAL OWNER of the transition — always `execute-orchestrator` in v1, even when emitted by the parent orchestrator on its behalf". Composer ratifies: (a) accept this clarification; (b) revise to "the emitting agent" (would invalidate the in-flight artifact under NFR-6); (c) extend the schema with a separate `emitter` field. Recommended: (a) accept the clarification; this is the minimal-change interpretation that preserves both the v1 invariant and the in-flight artifact.

**Q-CC-5 (codebase-analysis OQ-CR-004 — shared cycle-counter state).** Under option (a), `execute-orchestrator` and `execute-finalize-reconciler` previously shared cycle-counter state via `memory: project`. With `execute-orchestrator` re-scoped to advisor, the parent orchestrator owns the counter (in `checkpoint.json.execution_pipeline_cycle_counters`). The reconciler still has `memory: project` in its frontmatter — does it need that memory under option (a)? Options: (a) preserve `memory: project` on the reconciler (it still tracks `budget_used` / `budget_remaining` across cycles within a single phase); (b) trim `memory: project` and move the per-cycle state to a feature-scoped artifact (`quality-reconciliation-log.json` already records `cycle` / `budget_used` / `budget_remaining`); (c) defer to plan-author. Recommended: (a) preserve. The reconciler's `memory: project` predates this feature and is load-bearing for the budget-tracking it does within a single dispatch (per `execute-finalize-reconciler.md` workflow §7). Composer/plan-author confirm.

**Q-CC-6 (synthesis §3.2 DISSENT-4 / OI-FRAMER-2).** The FR-6 synthetic minimal test SHOULD include a sub-question discriminating H-a (baseline-inheritance) vs H-b (memory-field auto-enable) for the Edit-tool addition observed on `execute-orchestrator`'s runtime surface (analysis §1.2). Codebase-research CR-0023 confirms `execute-orchestrator` declares `memory: project`, supporting H-b; a falsifying test would author a probe sub-agent WITHOUT `memory:` and check whether `Edit` still appears. This sub-question is non-load-bearing for kill-criterion-#2 closure but valuable for future cc-design discipline. Owner: `test-acceptance-author`. The Designer surfaces it here so composer can decide whether to require it in the synthetic test design.

## 16. Open items

- **OI-CC-1.** Q-CC-1's disposition determines whether AC-CC-10 lands in the Blueprint's AC set or is dropped. Composer decides.
- **OI-CC-2.** The AC-FR-4-a open-item count for option (a) is exactly 1 (the `state-transitions-log-entry-template.md:63` edit). Operator approval of the framer's recommendation in synthesis is implicit per the PRD draft posture, but composer should ratify in the Blueprint's Fact Disposition Table.
- **OI-CC-3.** `plan-author` decides the exact prose for the new "Execution Phase Dispatch" section per §4; this Design specifies the content scope but not the exact wording.
- **OI-CC-4.** `plan-author` decides whether `current_stage` gains a single `"execution"` value or splits into per-substantive-state values; substrate prefers a single value per §5 note 1.
- **OI-CC-5.** Q-CC-3 / Q-CC-4 / Q-CC-5 dispositions feed into the per-sub-agent edit set; if any is decided differently, the §3 Conventions Touched table updates accordingly.

## 17. Dependencies on other layers

No cross-layer dependencies. This is a cc-only feature. See `cc-dependencies.json` for the structured shape; the only dependency relationships expressed are intra-cc (parent skill → specialist agents).
