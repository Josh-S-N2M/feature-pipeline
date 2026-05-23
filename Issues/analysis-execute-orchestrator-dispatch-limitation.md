---
id: ANALYSIS-execute-orchestrator-dispatch-limitation
doc_type: analysis
status: draft
generated: 2026-05-23
generated_by: claude (orchestrator) — surfaced at execution-pipeline start in devcontainer-mcp-provisioning-r1
feature_slug: devcontainer-mcp-provisioning-r1
scope: pipeline-wide (not feature-scoped)
mode: report-only
companion_artifacts:
  - .claude/agents/execute-orchestrator.md (frontmatter declares Agent tool; runtime grant differs)
  - .claude/agents/execute-task-code-producer.md
  - .claude/agents/execute-task-quality-handler.md
  - .claude/agents/execute-phase-quality-reviewer.md
  - .claude/agents/execute-finalize-reconciler.md
  - working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log
  - working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json (execution_pipeline_state_transitions + execution_mode fields)
proposes_future_feature: execute-orchestrator-dispatch-mechanism-repair-r1 (suggested slug)
---

# Pipeline Analysis — execute-orchestrator cannot dispatch its specialist sub-agents

## TL;DR

The `execute-orchestrator` sub-agent's frontmatter at `.claude/agents/execute-orchestrator.md:6` declares `tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]`. At runtime, when the agent is invoked, its actual tool surface (the `<functions>` block visible to the agent itself) contains only `[Read, Write, Bash, Edit]` — `Agent` is missing, three declared tools are missing (`Glob`, `Grep`, `TaskUpdate`), and one undeclared tool is present (`Edit`).

The hard consequence: **execute-orchestrator cannot perform its single core responsibility — dispatching the four specialist agents** (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`). The agent's body explicitly excludes self-authoring of code ("You do NOT author code. That's code-producer."), so without `Agent` the orchestrator is stranded at the INIT → pending boundary unable to advance any task.

This was surfaced during the `devcontainer-mcp-provisioning-r1` execution-pipeline start (2026-05-23), where execute-orchestrator was invoked twice — once at first attempt, once with an explicit corrective brief telling it that its tools list includes Agent. Both attempts returned the same tool-surface report (`[Read, Write, Bash, Edit]`). The second attempt proceeded in single-agent fallback mode (orchestrator authors tasks directly with quality criteria applied inline), which is option-(c) of the original escalation but loses specialist-isolation and the audit trail of separate state-transitioned dispatches per Contract 5.

The bug is **not** specific to execute-orchestrator. It is the symptom of a harness-level behavior: sub-agent tool surfaces are stripped or rewritten between frontmatter declaration and runtime exposure. The next time any sub-agent in this project declares `Agent` in its tools list and expects to dispatch other sub-agents, the same failure mode will recur.

---

## 1. Evidence — observed tool surface drift

### 1.1 Frontmatter declaration

`/workspaces/feature-pipeline/.claude/agents/execute-orchestrator.md` line 6:

```yaml
tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]
```

This is unambiguous: 7 tools declared, `Agent` among them.

### 1.2 Runtime tool surface (from the agent's own report)

Verbatim from the execute-orchestrator's return after the corrective-brief invocation (2026-05-23T03:25:00Z):

> "My actual session `<functions>` block exposes only `Read, Write, Bash, Edit`."

That's 4 tools, of which:

- 3 match frontmatter (`Read`, `Write`, `Bash`) — but `Bash` lacks the declared `(python3:*)` scope restriction
- 1 does NOT match frontmatter (`Edit` — undeclared)
- 4 declared tools are MISSING (`Glob`, `Grep`, `Agent`, `TaskUpdate`)

### 1.3 Consistency across invocations

Two separate invocations of execute-orchestrator returned the same tool surface. The first attempt could be dismissed as a self-perception error (the agent misreading its own grant); the second invocation, given an explicit corrective brief that quoted the frontmatter back to the agent and instructed it not to return with "missing tool" claims, returned the same finding. The agent proceeded in option-(c) fallback mode rather than the option-(iv) re-dispatch path. This consistency rules out misperception.

---

## 2. Affected agents

Sub-agents in this project that declare `Agent` in their tool grants (any of which would hit the same failure):

| Agent | Tool declaration | Dispatch purpose |
|---|---|---|
| `execute-orchestrator` | `[..., Agent, ...]` | Dispatches the 4 execute-* specialists |
| (others, if any, would also be affected — sweep needed) | — | — |

A sweep of `.claude/agents/*.md` for `Agent` in tools arrays would identify the full affected set. This analysis does not perform the sweep; it establishes the failure mode in the execute-orchestrator case.

---

## 3. Behavioral consequence for the feature pipeline

### 3.1 Execution-side specialist-isolation pattern is unavailable

The pipeline's design intent (per `recipe-feature-pipeline/SKILL.md` and the execute-* agent family) is that execution decomposes into:

- `execute-orchestrator` drives the state machine + cycle counters + dispatch sequencing
- `execute-task-code-producer` authors code in isolation per task spec
- `execute-task-quality-handler` issues verdicts in isolation
- `execute-phase-quality-reviewer` aggregates 5-dimensional phase verdicts
- `execute-finalize-reconciler` classifies findings and re-routes

This isolation is load-bearing for: (a) auditability (each dispatch is its own context, logged), (b) cycle-cap enforcement per ADR-0017, (c) the dispatch matrix per Blueprint Contract 5, and (d) the symmetric ADR-0034 application of D-12 cap.

Without sub-agent dispatch from execute-orchestrator, the pipeline either runs in single-agent fallback (collapsing specialist isolation) or stalls.

### 3.2 The single-agent fallback's loss

In the `devcontainer-mcp-provisioning-r1` execution attempt, execute-orchestrator proceeded in single-agent fallback for Phase 0. The findings surfaced (3 supply-chain drift issues) were real and valuable — Phase 0's verify-at-execution discipline did its job. But:

- State transitions per Contract 5 collapsed into a single agent context rather than being log-emitted across dispatch boundaries
- Cycle counters were tracked in checkpoint.json but not exercised against per-task / per-phase boundaries (which require distinct dispatches)
- The dispatch matrix (D-14 6-row + D-13 2-row for scope deviations) was applied inline rather than routed via execute-finalize-reconciler
- Quality verdicts (APPROVED / NEEDS_REVISION / STUB_DETECTED / BLOCKER per D-2a/c/d) were applied inline rather than issued by execute-task-quality-handler with its KB-cc-design discipline + ai-development-guide 4-phase verification

These are real audit-trail losses, not just architectural cleanliness.

### 3.3 Comparison to other pipeline gaps

This analysis joins the pipeline-defect family already documented in `Issues/`:

| Gap | Symptom | Documented in |
|---|---|---|
| ADR placement / single-location mechanism missing | 7 ADRs land at feature-scoped only; canonical registry empty | `Issues/analysis-adr-placement-rootcause.md` |
| Per-agent design evaluation absent | Pipeline can't tell if it forgot an agent | `Issues/analysis-per-agent-design-evaluation-gap.md` |
| Auditing family graduation precedent uncodified | First graduation done ad-hoc; no rubric for the others | `Issues/proposal-auditing-family-graduation-review.md` |
| **execute-orchestrator dispatch limitation** | **Sub-agents can't dispatch sub-agents at runtime** | **THIS DOCUMENT** |

All four share the shape: design intent expressed at a high level (in agent descriptions, ADRs, KB skills) without corresponding mechanism in the runtime / orchestration layer. The pattern suggests a systemic project-wide cleanup is warranted.

---

## 4. Hypothesis on root cause

Two plausible explanations (this analysis does not pick one; the follow-up feature investigates):

### 4.1 Harness behavior (most likely)

The Claude Code harness may, by design, restrict sub-agent tool surfaces to a safety-bounded subset, regardless of frontmatter declaration. Reasons could include:

- **Recursion prevention**: sub-agents dispatching sub-agents could spawn unbounded chains
- **Context-cost containment**: each sub-agent dispatch consumes additional tokens; restricting Agent from sub-agents bounds the cost
- **Surface-area minimization**: sub-agents are intentionally narrower than top-level agents
- **Untested code path**: the harness may not have ever been used in a pattern that requires sub-agent dispatch

If this is the cause, the fix is one of: (a) reading the harness docs to understand the supported pattern and migrating the pipeline to it, (b) modifying agent definitions to not assume Agent dispatch capability, (c) coordinating with Anthropic on whether sub-agent Agent dispatch is supported.

### 4.2 Frontmatter parsing bug (less likely)

The harness might parse the frontmatter `tools:` array but rewrite it during agent instantiation. Possibilities: the inline syntax `[Read, Glob, Grep, ...]` might be normalized differently than the multi-line YAML list form; specific tool names like `Agent` might be filtered; the `Bash(python3:*)` scope syntax might be unrecognized and the parser might silently drop the parenthetical.

The presence of `Edit` in the runtime surface (despite NOT being in the frontmatter) suggests something more than simple filtering — there's at least some active mutation between declaration and runtime. This weakens the simple-filtering hypothesis and strengthens the active-harness-behavior hypothesis.

---

## 5. Workaround used in this feature run

For `devcontainer-mcp-provisioning-r1`, the parent recipe-feature-pipeline orchestrator (the top-level user-facing Claude session) is taking over the execution-pipeline state-machine drive directly:

- The parent has `Agent` available at its tool surface (top-level grants are not restricted the same way)
- The parent dispatches the 4 specialists per task, sequenced according to the execute-orchestrator's intended state-machine
- The audit trail is partially preserved: each dispatch is its own logged sub-agent invocation; checkpoint.json + state-transitions.log capture the transitions

What's lost vs. the designed pattern:

- The execute-orchestrator agent's specialized context (it carries KB-cc-platform, KB-cc-design, recipe-feature-pipeline, auditing-shared, KB-review-disciplines as skills) is not active during execution drive
- The parent orchestrator has to carry both design-side and execution-side context simultaneously, which is more context-expensive
- Cycle-cap discipline (ADR-0017's 4-cycle cap) requires manual tracking by the parent rather than being state-machine-enforced by execute-orchestrator

These are real costs but not blockers. The pattern can ship the feature; it just doesn't exercise the designed execution-pipeline machinery cleanly.

---

## 6. Recommended follow-up feature

Suggested slug: **`execute-orchestrator-dispatch-mechanism-repair-r1`**.

Suggested in-scope:

- **Investigation step**: determine whether sub-agent Agent dispatch is supported by the harness at all. Read Claude Code's documentation on sub-agent tool grants; test with a minimal sub-agent that declares Agent and tries to dispatch. Confirm or refute the harness-restriction hypothesis.
- **Design decision**: if sub-agent Agent dispatch is NOT supported, the execute-orchestrator pattern needs redesign. Options:
  - **Flatten the dispatch hierarchy**: top-level orchestrator (recipe-feature-pipeline) directly dispatches the 4 specialists; execute-orchestrator becomes an advisor / state-machine documentation rather than an active agent
  - **Move state-machine logic into the recipe-feature-pipeline orchestrator**: it owns design-side and execution-side both; execute-orchestrator is retired
  - **Use Bash scripts as the dispatch surface**: execute-orchestrator stays an agent but dispatches scripts (which it CAN run) rather than sub-agents; the scripts then invoke specialists via some other mechanism (queues, lock files, external triggers)
- **Implementation**: realize the chosen design across the affected files. Likely touches: `recipe-feature-pipeline/SKILL.md`, `execute-orchestrator.md`, each of the 4 specialist agent files, `checkpoint.json` schema, `state-transitions.log` schema.
- **Verification**: re-run the execute-orchestrator pattern against a small test feature to confirm the dispatch loop works end-to-end.

Suggested out-of-scope:

- Migrating completed features that already shipped under the parent-driven workaround. They stay as-shipped.
- Redesigning the agent-roster more broadly. This feature focuses on the dispatch mechanism only.

Suggested kill criteria for this follow-up feature:

- If investigation reveals that sub-agent Agent dispatch IS supported (e.g., a frontmatter syntax change or harness flag enables it), the follow-up shrinks to: apply the fix; no design change.
- If sub-agent Agent dispatch is NOT supported and won't be, the follow-up commits to flattening — execute-orchestrator either gets retired or restructured.

---

## 7. What this report does NOT do

Report-only per project convention. It does not:

- Modify any agent definition file.
- Edit `recipe-feature-pipeline/SKILL.md` or any of the 4 execute-* specialist files.
- Decide between the design options in §6 (that's the follow-up feature's job).
- Move forward with `devcontainer-mcp-provisioning-r1` execution — that proceeds under the parent-driven workaround per the user's Gate-6 disposition.

The follow-up feature `execute-orchestrator-dispatch-mechanism-repair-r1` is recorded here as the canonical entry point for the repair work.

---

## 8. Cross-references

- Sibling pipeline-defect analyses:
  - `Issues/analysis-adr-placement-rootcause.md`
  - `Issues/analysis-per-agent-design-evaluation-gap.md`
  - `Issues/proposal-auditing-family-graduation-review.md`
- This feature's deferral register: `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` (the §O event-trigger posture applies — the follow-up feature is event-triggered on user prioritization, not calendared)
- Execution-pipeline artifacts touched in the partial run: `working/feature/devcontainer-mcp-provisioning-r1/state-transitions.log`, `working/feature/devcontainer-mcp-provisioning-r1/checkpoint.json`, `working/feature/devcontainer-mcp-provisioning-r1/verify-at-execution.md` (Phase 0 partial — T0.1/T0.3 PASS, T0.2/T0.4/T0.5 FINDING entries)
- Memory: this analysis joins the project-wide pipeline-gap memory cluster; orchestrator should surface it on next pipeline-improvements review.
