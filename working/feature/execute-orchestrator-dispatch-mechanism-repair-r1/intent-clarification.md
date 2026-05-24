---
id: IC-execute-orchestrator-dispatch-mechanism-repair-r1
doc_type: intent-clarification
version: 0.1.0
status: ratified
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
scope_class: FULL
user_token: gate-1-approved-as-is-2026-05-23T20:32:00Z
generated: 2026-05-23T20:25:00Z
generated_by: intake-intent-clarifier
derived_from: Issues/analysis-execute-orchestrator-dispatch-limitation.md
companion_artifacts:
  - Issues/analysis-execute-orchestrator-dispatch-limitation.md
  - .claude/agents/execute-orchestrator.md
  - .claude/agents/execute-task-code-producer.md
  - .claude/agents/execute-task-quality-handler.md
  - .claude/agents/execute-phase-quality-reviewer.md
  - .claude/agents/execute-finalize-reconciler.md
  - .claude/skills/recipe-feature-pipeline/SKILL.md
  - working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log
  - working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json
---

# Intent Clarification: execute-orchestrator Dispatch Mechanism Repair (r1)

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [x] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

This is the first artifact for follow-up feature `execute-orchestrator-dispatch-mechanism-repair-r1`. It captures the user's intent before PRD or design work begins. The feature has an unusually well-scoped origin: a project-internal analysis document already enumerates the defect, the affected files, suggested in/out scope, and kill criteria. This Intent Clarification therefore ratifies that analysis as the basis for the run and pins down only the genuine remaining ambiguities — scope class, investigation cadence, kill-criteria activation behavior, layer scope, workaround-durability posture, and verification approach.

## Source

> "Pipeline-wide defect documented in `Issues/analysis-execute-orchestrator-dispatch-limitation.md`. The `execute-orchestrator` sub-agent's frontmatter declares `tools: [..., Agent, ...]`, but at runtime its actual tool surface contains only `[Read, Write, Bash, Edit]`. Hard consequence: execute-orchestrator cannot dispatch its 4 execution-side specialists. Observed twice during `devcontainer-mcp-provisioning-r1`'s execution-pipeline start (2026-05-23); proceeded via a parent-orchestrator-driven workaround." — orchestrator dispatch prompt, 2026-05-23T20:22:35Z, paraphrasing the source analysis TL;DR.

Formal seed: `Issues/analysis-execute-orchestrator-dispatch-limitation.md` (`doc_type: analysis`, `proposes_future_feature: execute-orchestrator-dispatch-mechanism-repair-r1`). §6 of that analysis frames suggested in-scope, out-of-scope, and kill criteria; this clarifier treats §6 as the strong default position to refine, not as a settled scope statement.

## Initial Interpretation

The analysis supplies the substance: a sub-agent tool-surface drift defect where the runtime tool grant for `execute-orchestrator` excludes `Agent`, `Glob`, `Grep`, and `TaskUpdate`, includes an undeclared `Edit`, and strips the `Bash(python3:*)` scope restriction. The drift makes the execute-orchestrator unable to perform its single core responsibility (dispatching the 4 execution-side specialists), forcing a parent-orchestrator-driven workaround that loses specialist-isolation, per-dispatch state-transition logging, cycle-cap enforcement at task/phase boundaries, and the dispatch-matrix routing through execute-finalize-reconciler.

The feature has two sequenced concerns: (1) **investigation** — determine whether sub-agent `Agent` dispatch is supported by the Claude Code harness at all (the analysis hypothesizes a harness-level restriction but does not commit); (2) **repair** — apply whichever fix the investigation outcome dictates. The kill-criteria from §6 explicitly distinguish a "supported, shrink to fix" path from a "not supported, commit to flattening" path.

The defect is purely in the Claude Code primitives surface (sub-agent definitions, the recipe-feature-pipeline orchestrator skill, checkpoint/state-transitions schemas). No other engineering layer is plausibly activated. The likely scope class is FULL because: (a) the repair touches 6+ agent definition files plus a SKILL.md plus two schemas, (b) it requires an investigation step with KB-gap justification, (c) it includes a design decision among three architectural options. A MINOR fall-back applies if the investigation reveals a one-flag fix.

What this Stage 1 must still pin down: the scope-class choice, the investigation cadence (in-pipeline Discovery Research vs. pre-pipeline preflight), kill-criteria activation behavior, formal layer-scope declaration across all 9 layers, the user's posture on whether the parent-orchestrator-driven workaround is acceptable as a long-term pattern, and the verification-approach choice (synthetic minimal test feature vs. real feature re-run).

## Clarifying Questions and Answers

Each row records one ambiguity that the clarifier identified and the user's resolution. Because the source request explicitly directs this clarifier to "lean on §6 of the analysis as the default position and only ask where genuine ambiguity remains," answers below are sourced from §6 where it speaks directly, and are framed as `proposed default — pending user confirmation at the Intent Confirmation Gate` where the analysis is silent or under-specified. The Intent Confirmation Gate captures the user's final word on each.

| # | Ambiguity | Question Asked | Proposed Answer (pending user gate) | Resolved? |
|---|---|---|---|---|
| 1 | Scope class per ADR-0023 (FULL / MINOR / PATCH) | "The analysis frames a multi-file repair plus an investigation step. Is this FULL, or do you prefer MINOR with a contingency upgrade if the investigation reveals a structural redesign is required?" | **FULL.** Multi-file repair across 6+ agent definitions, the recipe-feature-pipeline SKILL.md, two schemas (checkpoint.json + state-transitions.log), and a KB-gap-driven Discovery Research topic. The PATCH lane is reserved for the kill-criterion #1 path (investigation reveals one-flag fix) — see Q3. | [x] |
| 2 | Investigation cadence: in-pipeline Discovery Research, or pre-pipeline preflight? | "§6 names 'investigation' as a step. Is the investigation expected to happen *inside* the pipeline run (a Discovery Research topic with KB-gap justification: 'Claude Code harness sub-agent tool-grant semantics are not documented in our KBs'), or should it happen as a pre-feature preflight that informs the PRD scope?" | **In-pipeline Discovery Research, as a `disposition: external-research-topic`.** Rationale: (a) the question genuinely needs Claude Code documentation review + a minimal probe sub-agent test, both of which are research activities the pipeline's Discovery stage is designed for; (b) gating it behind a pre-feature preflight delays the feature and creates an unscoped side-quest with no audit trail; (c) the result feeds directly into the per-layer Design (cc) decision among the three §6 options, which is exactly the synthesis-to-design flow the pipeline supports. | [x] |
| 3 | Kill-criteria activation: automatic scope-shrink or pause-and-rescope? | "If the investigation reveals sub-agent `Agent` dispatch IS supported (e.g., frontmatter syntax change or harness flag enables it), does the feature automatically shrink scope and continue, or does it pause for a re-scoping gate?" | **Pause-and-rescope at the Intent Confirmation Gate of a follow-on run.** Rationale: scope-class shrinks from FULL to MINOR/PATCH would invalidate downstream artifact assumptions (per-layer design count, ADR count, plan phase count). Cleaner to terminate this run with a `kill-criterion-1-triggered` posture, capture the finding as an analysis artifact, and open a fresh small feature for the one-flag fix. The alternative (silent scope-shrink mid-run) would bypass the user's gating discipline. | [x] |
| 4 | Layer scope (9 layers per Blueprint v4.3.1) | "The defect is in the Claude Code primitives surface. Is `cc` (Claude Code / Project Filesystem) the only activated layer, or is there a plausible second activation (e.g., codespaces, cicd)?" | **Only `cc` is activated.** All affected files (agent definitions, SKILL.md, checkpoint.json schema, state-transitions.log schema) live under `.claude/`, `adrs/`, and `working/feature/<slug>/`. None of the other 8 layers (frontend, backend, api, query, database, iac, cicd, codespaces) touch the defect surface. See Scope Posture → Layer Scope below for the formal 9-layer declaration. | [x] |
| 5 | Workaround durability: is the parent-orchestrator-driven workaround acceptable as a long-term fallback? | "The current `devcontainer-mcp-provisioning-r1` run used the parent-orchestrator-driven workaround. Is that workaround acceptable as a long-term fallback (i.e., the feature can retire execute-orchestrator entirely and bless the parent-driven pattern as the design intent), or must the dispatch mechanism be restored to honor the specialist-isolation invariant?" | **Defer to the per-layer Design stage — open item.** The §6 design-options enumeration explicitly includes "execute-orchestrator gets retired or restructured" as a path, AND "specialist isolation is load-bearing for auditability, cycle-cap enforcement, dispatch matrix, and ADR-0033 symmetric D-12 application" as a constraint. These pull in opposite directions and the resolution depends on the investigation outcome (Q2). The PRD will surface this as a constraint-tension to be resolved in per-layer cc Design. | [x] |
| 6 | Verification approach: synthetic minimal test feature vs. real feature re-run? | "§6 mentions 're-run the execute-orchestrator pattern against a small test feature.' Is a synthetic minimal test feature acceptable (cheaper, isolated), or must verification happen via re-running a real feature's execution pipeline (slower, more realistic)?" | **Synthetic minimal test feature is acceptable for primary verification.** A real-feature re-run is welcome as a confidence check but is not gating. Rationale: (a) the defect is at the harness/dispatch primitive level — a 1-task / 1-phase synthetic feature exercises the same dispatch path as a multi-phase real feature; (b) real-feature re-runs are expensive and add unrelated failure modes (Discovery research drift, layer-design churn) that confound the verification signal; (c) the synthetic feature can be archived as a regression artifact for future use. | [x] |

The user retains the right at the Intent Confirmation Gate to overturn any of these proposed answers. The `user_token` in frontmatter remains `pending-intent-confirmation-gate` until that ratification occurs.

## Clarified Intent

Repair the `execute-orchestrator` sub-agent's runtime dispatch capability so it can perform its single core responsibility — dispatching the four execution-side specialists (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`) in the sequences defined by the 12-substantive-state machine. The repair is preceded by an in-pipeline Discovery Research investigation that determines whether sub-agent `Agent` dispatch is supported by the Claude Code harness at all, with kill-criterion #1 (supported → one-flag fix) triggering a pause-and-rescope rather than a silent scope-shrink. The per-layer cc Design selects among three §6 options (flatten dispatch hierarchy / retire execute-orchestrator into recipe-feature-pipeline / use Bash-script dispatch surface), constrained by the investigation outcome and by the load-bearing specialist-isolation invariants (auditability, cycle-cap enforcement, dispatch matrix routing, ADR-0033 symmetric D-12 application). Verification is via a synthetic minimal test feature exercising the dispatch loop end-to-end; a real-feature re-run is welcome as a confidence check but not gating. Layer scope is exclusively `cc`.

## Scope Posture

### What's in scope

- **Investigation (Discovery Research topic, cc-layer):** read Claude Code documentation on sub-agent tool grants; probe with a minimal sub-agent that declares `Agent` and attempts dispatch; produce a finding-with-evidence document that distinguishes harness-level restriction from frontmatter-parsing bug from one-flag-fix. KB-gap justification: "Claude Code harness sub-agent tool-grant semantics are not documented in our KBs."
- **Per-layer cc Design:** select among the three §6 options (flatten dispatch hierarchy via recipe-feature-pipeline; retire execute-orchestrator into recipe-feature-pipeline; use Bash-script dispatch surface), with explicit rationale tied to the investigation outcome and to the specialist-isolation invariants.
- **Implementation across affected files:** the chosen design realized in `.claude/skills/recipe-feature-pipeline/SKILL.md`, `.claude/agents/execute-orchestrator.md`, the four specialist agent files (`execute-task-code-producer.md`, `execute-task-quality-handler.md`, `execute-phase-quality-reviewer.md`, `execute-finalize-reconciler.md`), the `checkpoint.json` schema (specifically `execution_pipeline_state_transitions` + `execution_mode` fields), and the `state-transitions.log` schema/format.
- **Verification:** synthetic minimal test feature (1 phase, 1–2 tasks) exercising the full dispatch loop end-to-end; PASS signal is a clean state-transitions.log emission across distinct sub-agent dispatch boundaries with cycle counters incrementing at the per-task and per-phase boundaries as designed.
- **ADR authorship:** at least one ADR capturing the chosen §6 option and its rationale; possibly a second ADR if the investigation outcome warrants a project-wide convention change (e.g., "sub-agents in this project MUST NOT declare `Agent` in tools lists").

### What's NOT in scope (explicitly excluded)

- **Migrating completed features** that already shipped under the parent-orchestrator-driven workaround. `devcontainer-mcp-provisioning-r1` and any subsequent features-in-flight stay as-shipped; this feature does not retrofit them.
- **Redesigning the agent-roster more broadly.** This feature is narrowly scoped to the dispatch mechanism. The pipeline-gap memory cluster (per-agent design evaluation gap, ADR placement gap, auditing family graduation review) is acknowledged but addressed by their own follow-up features, not bundled here.
- **Changes to other sub-agents that declare `Agent` in their tools lists** but are not part of the execute-* family. The analysis §2 notes a sweep is needed; that sweep is in-scope as a discovery-side enumeration ONLY, with any required cleanup deferred to a follow-on feature unless the chosen §6 design demands it for correctness.
- **Modifications to the four specialist agents' substantive responsibilities.** Their tool grants and dispatch interfaces may change; their domain responsibilities (code production, quality handling, phase quality review, finalize reconciliation) do not.
- **Changes to ADR-0017's 4-cycle cap** or to the dispatch matrix definitions (D-2a/c/d, D-12, D-13, D-14). The repair preserves these as load-bearing invariants — it does not redefine them.
- **A general Claude Code harness investigation** beyond what's needed to answer the dispatch question. The Discovery topic is targeted: "is sub-agent Agent dispatch supported, and if so, how?" — not "audit the entire Claude Code primitives surface."

### What's undecided (deferred to PRD or later)

- **Final §6 design option choice** — depends on the investigation outcome; resolved in per-layer cc Design.
- **Whether execute-orchestrator is retired entirely or restructured** — sub-decision of the above, with knock-on effects on the 5-skill stack carried by execute-orchestrator (`KB-cc-platform`, `KB-cc-design`, `recipe-feature-pipeline`, `auditing-shared`, `KB-review-disciplines`) and on the 12-state machine ownership.
- **Whether a project-wide ADR is warranted** for "sub-agents MUST NOT declare `Agent` in tools lists" — depends on investigation outcome (kill-criterion #2 path makes this load-bearing; kill-criterion #1 path makes it unnecessary).
- **The exact synthetic-test-feature shape** — task count, phase count, what minimal real code work it produces. Resolved in plan-authoring.

### Layer Scope (9-layer declaration per Blueprint v4.3.1)

| # | Layer | Disposition |
|---|---|---|
| 1 | Claude Code / Project Filesystem (`cc`) | **In scope.** All affected files live here. |
| 2 | Frontend | N/A — out of scope. No UI surface affected. |
| 3 | Backend | N/A — out of scope. No backend service affected. |
| 4 | API | N/A — out of scope. No API contract affected. |
| 5 | Query / Data Access | N/A — out of scope. No data-access layer affected. |
| 6 | Database | N/A — out of scope. No schema affected. |
| 7 | CI/CD (GitHub Actions) | N/A — out of scope. No workflow affected. |
| 8 | Infrastructure as Code | N/A — out of scope. No IaC module affected. |
| 9 | Dev Environment (Codespaces / Devcontainer) | N/A — out of scope. The devcontainer-mcp-provisioning-r1 run surfaced the defect but the defect itself is not in the devcontainer layer. |

## Stakeholder Posture (Preliminary)

- **Pipeline operator (Josh-S-N2M):** wants execute-orchestrator's designed dispatch behavior restored so the execution-side specialist-isolation pattern is exercisable, with the audit trail and cycle-cap enforcement that justify the design.
- **Future-feature execution pipelines:** every feature that reaches execution stage after this repair depends on the dispatch mechanism working as designed; any silent fallback to the parent-orchestrator-driven workaround re-incurs the audit-trail losses documented in analysis §3.2.
- **The four execute-* specialist agents:** their existence is contingent on being dispatchable. If the chosen §6 option is "retire execute-orchestrator into recipe-feature-pipeline," they are still dispatched but by a different parent — their domain responsibilities and prompts persist.
- **Auditability / audit-trail consumers:** the state-transitions.log and per-dispatch checkpoint.json transitions are load-bearing for the Contract 5 specialist-isolation discipline; their integrity depends on this repair.

## Success Posture (Preliminary)

The feature is "done" when:

1. A synthetic minimal test feature can be run end-to-end through the (repaired or redesigned) execution-side dispatch mechanism, with state-transitions.log emitting cleanly across distinct sub-agent dispatch boundaries and cycle counters incrementing at per-task and per-phase boundaries as designed.
2. The investigation outcome is documented as an analysis-or-ADR artifact that future Claude Code primitive design work can cite — i.e., the project never has to re-discover the answer to "is sub-agent Agent dispatch supported?"
3. The chosen §6 design option is realized across all affected files (recipe-feature-pipeline SKILL.md, 5 agent files, 2 schemas) without breaking the ADR-0017 4-cycle cap, the dispatch matrix, or the ADR-0033 symmetric D-12 application.
4. (If kill-criterion #1 triggers:) the run terminates cleanly with a `kill-criterion-1-triggered` posture, and a fresh small follow-on feature is opened for the one-flag fix.

## Confirmation

Pending. The orchestrator's AskUserQuestion at the Intent Confirmation Gate captures the user's ratification of:
- The six proposed answers in the Clarifying Questions table
- The scope-class declaration (FULL)
- The layer-scope declaration (cc-only)
- The deferred items in "What's undecided"

The `user_token` field in frontmatter remains `pending-intent-confirmation-gate` until that ratification is recorded.

## Open Items (Pending PRD Authoring)

The following items are surfaced for the PRD author's rationale brief — each is genuinely under-determined until investigation outcomes or downstream design decisions land:

1. **Investigation outcome dependency.** The PRD's Functional Requirements should be authored against the FULL scope-class assumption (kill-criterion #2 path) but with an explicit FR or NFR acknowledging that kill-criterion #1 triggers a pause-and-rescope rather than continuing.
2. **Constraint tension between workaround-acceptability and specialist-isolation invariants.** The per-layer cc Design must resolve this; the PRD should record both as constraints rather than choosing between them.
3. **Sweep of other `Agent`-declaring sub-agents.** The analysis §2 notes a sweep is needed. The PRD should decide whether the sweep produces only an inventory artifact (discovery-only) or whether it triggers cleanup-as-blockers. Recommended posture: inventory-only in this run; cleanup deferred unless the chosen §6 design demands it for correctness.
4. **ADR count and scope.** Likely one ADR for the chosen §6 option; possibly a second ADR for a project-wide convention ("sub-agents MUST NOT declare `Agent` in tools lists") if kill-criterion #2 triggers. The PRD should not prescribe the ADR count — design-composer decides.
5. **Synthetic-test-feature shape.** Task count, phase count, and what minimal real code work it produces. Plan-author decides.
6. **Schema migration concern.** If the `checkpoint.json` `execution_pipeline_state_transitions` field or `state-transitions.log` format changes, the in-flight `devcontainer-mcp-provisioning-r1` run (which used the workaround) has a partial log/checkpoint under the old format. The PRD should declare whether this run's artifacts are migrated, left as-is per the "no retrofit" out-of-scope rule, or formally marked as legacy.
7. **Memory note candidate.** The pattern "sub-agent declares Agent in frontmatter but runtime grant strips it" is a non-obvious recurring failure mode. If kill-criterion #2 triggers, a persistent memory note for future Claude Code primitive design work is warranted. Memory-discipline decision belongs to the design-composer.
