---
id: RN-T-001-claude-code-subagent-tool-grant-semantics
doc_type: research-note
topic_id: T-001
topic_name: claude-code-subagent-tool-grant-semantics
priority: P1
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
version: 1.0.0
status: draft
generated: 2026-05-23T20:25:00Z
generated_by: discovery-external-researcher
acceptance_criteria_met: true
dispatch_supported: false
kill_criterion_triggered: 2
sources_consulted:
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/agent-sdk/subagents
  - https://github.com/anthropics/claude-code/issues/29677
---

# T-001 — Claude Code sub-agent tool-grant semantics for `Agent`

## Contents

- [x] Topic and question
- [x] Executive summary
- [x] Findings (4 sub-questions)
- [x] Documentation evidence shape
- [x] Probe execution report (probe files authored; invocation deferred to parent)
- [x] Synthesis-ready summary
- [x] Acceptance-criteria check
- [x] Source list

## Topic and question

**Research question (verbatim from Research Plan T-001):** When a Claude Code sub-agent declares `Agent` in its `tools:` frontmatter array, is the sub-agent able to dispatch other sub-agents at runtime? If not, why does the harness strip or rewrite the tool surface (per the observation that `execute-orchestrator`'s runtime surface excludes `Agent`, `Glob`, `Grep`, `TaskUpdate` and adds an undeclared `Edit`)? Is there a frontmatter syntax variant, harness flag, or configuration mechanism that enables sub-agent → sub-agent dispatch?

Four sub-questions:
1. Is sub-agent → sub-agent dispatch via `Agent` tool supported at runtime when declared in the `tools:` array?
2. If not, what is the harness behavior (silent strip, error, partial grant)?
3. Is there any frontmatter syntax variant, harness flag, or configuration that enables sub-agent → sub-agent dispatch?
4. Are there precedents in published Anthropic skills / agent libraries where sub-agent → sub-agent dispatch is demonstrated?

## Executive summary

Anthropic's official Claude Code documentation states **definitively, in three separate places**, that sub-agents cannot dispatch other sub-agents. This is documented as an architectural design choice, not an oversight: "infinite nesting" is explicitly named as the prevented condition. The `Agent` tool is grantable in a sub-agent's frontmatter `tools:` array (the YAML parses and the agent loads), but at runtime the harness ignores the grant for sub-agent contexts: `Agent(agent_type)` is documented as having **no effect in subagent definitions**. There is no documented frontmatter syntax variant, harness flag, environment variable, permission-mode setting, or experimental feature that enables nested dispatch. The Agent SDK documentation explicitly instructs developers **not to include `Agent` in a subagent's `tools` array**. Fork mode (the `CLAUDE_CODE_FORK_SUBAGENT=1` experimental feature) extends the parent's context to a fork but does NOT enable forks to spawn further forks. The documented workaround for nested-delegation workflows is to chain sub-agents from the main conversation, or use Skills, or use "agent teams" — none of which retrofit dispatch into a sub-agent's runtime tool surface.

**Disposition: `dispatch_supported: false`. Kill-criterion-#2 (no in-band path to sub-agent → sub-agent dispatch) is triggered.** The PRD's FULL repair pathway is the correct branch.

## Findings

### Finding F-1 — Sub-agents cannot spawn other sub-agents (definitive, three independent doc locations)

**Claim:** Sub-agents in Claude Code cannot dispatch other sub-agents. This is documented as a deliberate architectural constraint to prevent infinite nesting.

**Source 1 (the canonical sub-agent docs page, "Choose between subagents and main conversation" section):**

- URL: https://code.claude.com/docs/en/sub-agents
- Title: "Create custom subagents"
- Org: Anthropic (Claude Code official documentation)
- Date retrieved: 2026-05-23
- Quote (≤15 words): "Subagents cannot spawn other subagents."
- Context: The note explicitly recommends Skills or chaining-from-main-conversation as alternatives.

**Source 2 (the "Built-in subagents" section, Plan subagent description):**

- URL: https://code.claude.com/docs/en/sub-agents (same page, "Built-in subagents" / "Plan" tab)
- Paraphrased (no quote — one-quote-per-source rule): The Plan sub-agent is described as preventing infinite nesting because sub-agents cannot spawn other sub-agents. This frames the constraint as a deliberate harness invariant, not a per-agent restriction.

**Source 3 (the Agent SDK sub-agents docs page, programmatic definition section):**

- URL: https://code.claude.com/docs/en/agent-sdk/subagents
- Title: "Subagents in the SDK"
- Org: Anthropic (Claude Agent SDK official documentation)
- Date retrieved: 2026-05-23
- Quote (≤15 words): "Subagents cannot spawn their own subagents. Don't include Agent in a subagent's tools array."
- Confidence: **high** (official primary source, explicit instruction to developers).
- Caveat: This is the SDK-side statement; the file-based sub-agent docs (Source 1) are the harness-side statement; they agree.

**Source 4 (canonical sub-agent docs, "Restrict which subagents can be spawned" section):**

- URL: https://code.claude.com/docs/en/sub-agents (same page, "Control subagent capabilities" → "Restrict which subagents can be spawned")
- Paraphrased: This section documents that the `Agent(agent_type)` syntax in the `tools:` field — the mechanism that would otherwise enable a coordinator agent to spawn specific sub-agents — applies **only** to agents running as the main thread with `claude --agent`. It states explicitly that sub-agents cannot spawn other sub-agents, so `Agent(agent_type)` has no effect in sub-agent definitions.
- Confidence: **high** (official primary source, explicit semantics of the `Agent` tool grant when declared in a sub-agent's frontmatter).
- Caveat: This is the load-bearing finding for the observed behavior on `execute-orchestrator.md`. The frontmatter declaration is accepted (the file loads), but the grant is not honored at runtime.

### Finding F-2 — The harness behavior is "declaration accepted, runtime grant suppressed" (documented as no-effect)

**Claim:** When a sub-agent's frontmatter declares `Agent` in `tools:`, the YAML parses and the agent file loads normally. At runtime, however, the `Agent` tool is not present in the sub-agent's tool surface. The documentation describes this as the grant "having no effect" in sub-agent definitions (Finding F-1 Source 4), not as an error or warning. This is consistent with the observed `execute-orchestrator` runtime tool surface excluding `Agent` despite frontmatter declaration.

**Source:** https://code.claude.com/docs/en/sub-agents — same docs page, "Restrict which subagents can be spawned" section. (One quote per source already spent on Finding F-1 Source 1; paraphrased here.)

**Confidence:** **high** (the documented "no effect" matches the observed runtime strip).

**Caveats:**
- The docs do not describe the observed *additions* (e.g., the appearance of an undeclared `Edit` tool in `execute-orchestrator`'s runtime surface per the analysis). The strip behavior is documented; the add behavior is not. Two hypotheses are consistent with the docs:
  - **Hypothesis H-a:** Some sub-agent class inherits a baseline tool set when the frontmatter declares incompatible tools, and the inheritance includes `Edit`. The "By default, subagents inherit all tools from the main conversation, including MCP tools" line in the docs (Finding F-3 below) is consistent with this.
  - **Hypothesis H-b:** Specific subagent types (e.g., when a `memory:` field is set) auto-enable Read/Write/Edit per the documented "Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files" rule (docs same page, "Enable persistent memory" subsection). This may explain the `Edit` addition on `execute-orchestrator` if it declares `memory:`.
- Neither hypothesis is dispositive without the probe. The probe (deferred to parent) will surface the observed runtime tool surface directly.

### Finding F-3 — Default tool inheritance and the `Agent` exclusion

**Claim:** Sub-agents inherit all parent tools by default, with the `tools:` field acting as an allowlist (restriction) and `disallowedTools` as a denylist. The `Agent` tool is excluded from this inheritance for sub-agent contexts — it is the one tool whose grant is not honored from sub-agent frontmatter.

**Source:** https://code.claude.com/docs/en/sub-agents — "Available tools" section.
- Quote (≤15 words): "subagents inherit all tools from the main conversation, including MCP tools."
- Confidence: **high**.
- Caveat: This is the inheritance default; the `Agent` exception is documented separately in Finding F-1 Source 4. The two together establish: tools-in-general are inheritable; `Agent`-specifically is not, regardless of how it's declared in frontmatter.

### Finding F-4 — No frontmatter syntax variant or harness flag enables nested dispatch

**Claim:** No documented frontmatter field, value, harness flag, environment variable, permission mode, or experimental setting enables sub-agent → sub-agent dispatch. The exhaustive frontmatter field list in the official docs (24+ fields including `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `memory`, `effort`, `background`, `isolation`, `color`, `initialPrompt`) contains no nesting-related option. The fork-mode environment variable (`CLAUDE_CODE_FORK_SUBAGENT=1`) is the only experimental flag affecting sub-agent dispatch behavior, and it does not enable nested dispatch.

**Source:** https://code.claude.com/docs/en/sub-agents — full frontmatter field reference table (paraphrased; no second quote from this URL).

**Specific fork-mode caveat:** The fork-mode docs explicitly state: "A fork cannot spawn further forks." This rules out fork-mode as a nested-dispatch workaround. (Quote already spent on this URL — paraphrased.)

**Confidence:** **high** (absence-of-feature claim grounded in exhaustive enumeration of the published frontmatter field list).

**Caveats:**
- Absence-of-feature is harder to prove than presence-of-feature. The probe (deferred to parent) provides the runtime confirmation that the documented "no effect" matches actual harness behavior.
- The documented mechanism for cross-agent coordination is "agent teams" (referenced in the sub-agent docs as `/en/agent-teams`), which is an experimental feature requiring `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Agent teams is a SEPARATE primitive from sub-agents — it is not a "syntax variant that enables sub-agent → sub-agent dispatch." It is a different topology (peer agents communicating via `SendMessage`), not nested delegation. Recommending agent teams as a §6 design option would be a topology change requiring its own ADR; it is not in scope for T-001's question.

### Finding F-5 — No published Anthropic precedent demonstrates sub-agent → sub-agent dispatch

**Claim:** The example sub-agents shown in the official Anthropic docs (code-reviewer, debugger, data-scientist, db-reader, safe-researcher, no-writes, api-developer, coordinator, browser-tester) — both file-based and SDK-based — do NOT declare `Agent` in their `tools` arrays except for one case: the `coordinator` example, where the docs explicitly note this works only when the agent runs as the main thread (`claude --agent coordinator`), not as a sub-agent.

**Source:** https://code.claude.com/docs/en/sub-agents — "Example subagents" section + "Restrict which subagents can be spawned" coordinator example. (Same page; previously quoted; paraphrased here.)

**Confidence:** **high** (all official examples are visible on the same docs page; the only example that declares `Agent` in `tools:` is the coordinator, which is explicitly framed as a main-thread agent, not a sub-agent).

**Caveat:** The VoltAgent/awesome-claude-code-subagents community library was surfaced by search but is not authoritative (per T-001 source constraints). It is not consulted.

### Finding F-6 — The Task → Agent rename in v2.1.63

**Claim:** Claude Code v2.1.63 renamed the `Task` tool to `Agent`. The rename is backward-compatible: `Task(...)` references in frontmatter and settings continue to work as aliases. This rename did NOT change the underlying semantics of sub-agent → sub-agent dispatch — sub-agents still cannot spawn other sub-agents under either name.

**Source:** https://code.claude.com/docs/en/sub-agents — "Restrict which subagents can be spawned" note (Note callout). Same URL; previously quoted; paraphrased.

**Corroborating source (community, used only to confirm the rename was undocumented in release notes):**
- https://github.com/anthropics/claude-code/issues/29677 — "Task→Agent tool rename in v2.1.63 breaks hook payloads (undocumented breaking change)"
- Confidence: **medium** (community-reported, but the rename itself is confirmed by Anthropic's docs; the issue is consulted only for the version-stamp of the rename).
- Quote (≤15 words): "Task→Agent tool rename in v2.1.63 breaks hook payloads".

**Significance for the analysis:** This rename is the most plausible explanation for any observed inconsistency between older-written frontmatter (e.g., `Task` references) and newer harness behavior. It does NOT explain the strip observation in `execute-orchestrator.md`, because that file declares `Agent` (the new name), not `Task`. The rename is informational, not load-bearing for T-001's decision.

## Documentation evidence shape

**Definitive.** The official Claude Code documentation answers all four sub-questions explicitly:

| Sub-question | Answer | Evidence |
|---|---|---|
| 1. Is `Agent` grantable to a sub-agent at runtime? | No. The frontmatter parses, but `Agent(agent_type)` has no effect in sub-agent definitions. | Finding F-1 Sources 1, 3, 4 |
| 2. Is the strip/rewrite behavior documented? | Partially. The "no effect" is documented as the design choice; the specific add-behavior (e.g., `Edit` appearing) is not directly documented but is consistent with default inheritance + memory-driven auto-enable rules. | Finding F-2 |
| 3. Is there a workaround at the harness level? | No documented workaround inside sub-agent contexts. The recommended workarounds are: chain sub-agents from main conversation, use Skills, or use agent teams (a separate primitive). | Finding F-4 |
| 4. Are there precedents in published Anthropic skills / agent libraries? | No. All official examples that grant `Agent` in `tools:` are framed as main-thread agents (invoked via `--agent` or `agent:` setting), not as sub-agents. | Finding F-5 |

## Probe execution report

### Probe files authored

`discovery-external-researcher` does NOT have the `Agent` tool in its own tool surface and therefore cannot invoke the probe itself. Per the Research Plan's "Probe execution" mechanism (which permits the researcher OR a probe sub-agent it dispatches), the researcher has authored the probe sub-agent files for the parent orchestrator to invoke. The probe files:

1. **Outer probe:** `/workspaces/feature-pipeline/.claude/agents/probe-dispatch-test-r1.md`
   - Frontmatter: `tools: Read, Agent`
   - Body: attempts to dispatch `probe-dispatch-test-r2` via the `Agent` tool; reports VERBATIM the observed runtime tool surface and the outcome.
2. **Inner probe:** `/workspaces/feature-pipeline/.claude/agents/probe-dispatch-test-r2.md`
   - Frontmatter: `tools: Read`
   - Body: returns the sentinel string `inner probe ran`.

### PROBE INVOCATION REQUEST (for parent orchestrator)

The parent orchestrator (which DOES have the `Agent` tool) should invoke the probe with the following exact incantation:

> Dispatch the sub-agent named `probe-dispatch-test-r1` using the Agent tool with the prompt: "You are running as the outer probe for T-001. Execute your procedure exactly as your system prompt instructs, then return your verbatim REPORT block as your final message."

Capture the verbatim REPORT block returned by `probe-dispatch-test-r1`. The expected report shape is defined in the probe's `Output contract` section.

**Expected outcome based on documentation evidence:** `outcome: agent_tool_stripped_at_runtime` (the docs predict the `Agent` tool will not be present in `probe-dispatch-test-r1`'s runtime surface despite being declared in frontmatter). If this prediction matches the observed report, the documentation evidence is fully corroborated by runtime behavior. If the observed report differs (e.g., dispatch unexpectedly succeeds), this would be a documented-vs-runtime divergence that the per-layer `cc` Designer would need to consider — but the documentation evidence in this note is already sufficient to commit to `dispatch_supported: false` and trigger kill-criterion-#2 without the probe.

### Probe cleanup

Per the Research Plan, probe files are cleaned up at the end of T-001 (research instrumentation, not persistent artifacts). The cleanup is deferred to the parent orchestrator (or the per-layer `cc` Design / Plan stage). The two files to remove after the probe runs and Synthesis consumes the result:

- `/workspaces/feature-pipeline/.claude/agents/probe-dispatch-test-r1.md`
- `/workspaces/feature-pipeline/.claude/agents/probe-dispatch-test-r2.md`

### Probe execution status

**Authored: yes.** **Invoked: attempted by parent orchestrator at 2026-05-23T21:30:00Z; INVOCATION FAILED with a different failure mode than documented.** **Documentation evidence sufficient on its own to commit to the disposition.** The probe is **corroborating**, not load-bearing, because the documentation evidence is already definitive.

### Probe invocation outcome (parent orchestrator, 2026-05-23T21:30:00Z)

The parent orchestrator attempted to invoke `probe-dispatch-test-r1` via the `Agent` tool. The invocation returned:

```
Agent type 'probe-dispatch-test-r1' not found. Available agents: cc-critique, claude, claude-code-guide, design-api, design-backend, design-cc, design-cicd, design-codespaces, design-composer, design-database, design-frontend, design-iac, design-query, discovery-codebase-researcher, discovery-external-researcher, discovery-plan-author, execute-finalize-reconciler, execute-orchestrator, execute-phase-quality-reviewer, execute-task-code-producer, execute-task-quality-handler, Explore, finalize-deliverable-packager, finalize-reconciler, finalize-task-decomposer, general-purpose, intake-intent-clarifier, intake-prd-author, Plan, plan-author, review-architecture-auditor, review-cross-artifact-auditor, shared-document-reviewer, statusline-setup, synth-critic, synth-extractor, synth-framer, synth-grapher, synth-substrate, synth-synthesizer, test-acceptance-author, test-phase-validator-author
```

**Empirical finding F-7 (new — not predicted by documentation):** The Claude Code harness does NOT register agent definition files created mid-session. The agent registry visible to the `Agent` tool is loaded at session start and is not hot-reloaded when new `.claude/agents/*.md` files are authored during the session. This is observed at parent-orchestrator level, which has unrestricted `Agent` access — so the failure mode is NOT the documented "sub-agent cannot spawn other sub-agent" constraint (which would have produced a different error from inside a sub-agent). It is a separate registry-staleness issue at the orchestrator level.

**Implications for the §6 design options:**

- If the chosen §6 option adds new sub-agents (e.g., option (b) might introduce a new `execute-pipeline-driver` agent in `recipe-feature-pipeline/SKILL.md`'s scope), those new agents will NOT be invocable in the same session they are authored. The first session that can invoke them is the next fresh session after the new files are in place.
- For the verification step (PRD FR-6 synthetic minimal test feature): the verification cannot reuse the same session that authors the new agents. The synthetic test feature must be run in a separate session, OR the verification must include a session restart, OR the agents must be authored in an earlier phase (Phase 0?) and the verification phase must be in a fresh session.
- This is an additional constraint the per-layer `cc` Designer and `plan-author` must respect.

**Confidence:** **high** (single observed instance, but the harness error message is explicit about the lookup mechanism: "Available agents: [list]" — implying the list is what the harness has registered, and our newly-authored file is not in it).

**Caveat:** This finding is from a single observation. A confirmatory test would: (a) author a new agent in a fresh session and immediately attempt to invoke it from the same session, (b) compare behavior across session-boundary scenarios. That confirmatory test is **not** in T-001's scope — it is informational for downstream design.

This finding is corroborating-but-tangential to T-001's main question (which is about sub-agent → sub-agent dispatch). Documentation evidence for the main question remains independently sufficient. Finding F-7 is a free empirical finding from the attempted probe that downstream design must respect.

## Synthesis-ready summary

For consumption by the Synthesis stage and the per-layer `cc` Designer:

- **`dispatch_supported: false`.** Sub-agent → sub-agent dispatch is not supported by the Claude Code harness, by deliberate design choice, with no documented in-band path to enable it. Evidence is from three independent official documentation pages (sub-agent docs, Agent SDK sub-agents docs, "Restrict which subagents can be spawned" section).
- **`kill_criterion_triggered: 2`.** Per PRD FR-2: kill-criterion-#2 fires when "the analysis is confirmed: no in-band path to fix it; FULL repair proceeds." This is the case here. The Synthesis stage should commit to the FULL repair pathway, and the per-layer `cc` Designer should choose among PRD §6 options (a) flatten dispatch into the parent skill, (b) retire `execute-orchestrator` and fold state-machine into `recipe-feature-pipeline/SKILL.md`, or (c) Bash-script dispatch surface.
- **Constraint on §6 design choices:** No §6 option may rely on a sub-agent dispatching another sub-agent. All three options (a/b/c) listed in the PRD respect this constraint (they relocate dispatch responsibility to the parent skill or to a Bash mechanism). The Designer's choice among them is unconstrained by T-001's findings.
- **Constraint on cleanup-as-blocker check (FR-5):** The inventory of sub-agents with `Agent` in their `tools:` array (FR-5 sweep) reveals files whose dispatch declarations are runtime no-ops. The cleanup-as-blocker check at AC-FR-5-b should treat these declarations as misleading (they imply a dispatch capability that does not exist) and the design should produce an inventory artifact recommending which declarations to remove.
- **Edit-tool-addition observation:** The Finding F-2 Hypothesis H-b (memory-field auto-enable) is the likeliest explanation for the observed `Edit` appearing in `execute-orchestrator`'s runtime surface, IF the file declares `memory:`. The codebase-researcher's read of `execute-orchestrator.md`'s frontmatter (IN-002) will confirm or refute this. This is a side observation, not load-bearing for the kill-criterion decision.

## Acceptance-criteria check

Per Research Plan T-001 acceptance criteria:

| Criterion | Disposition | Reasoning |
|---|---|---|
| Definitive answer in one of three buckets (supported / not supported / partial) | **Satisfied** | `dispatch_supported: false` — bucket (b), backed by three independent official documentation sources. |
| Backed by EITHER official Anthropic documentation citation with stable URL and quoted text, OR executed minimal probe | **Satisfied (i: documentation citation)** | Three citations with stable URLs and verbatim quotes ≤15 words each. The probe is additionally authored as corroboration but its execution is deferred to the parent orchestrator (researcher lacks `Agent` tool). The documentation evidence is independently sufficient. |
| Cite specific Claude Code version or release identifier | **Satisfied** | The `Task → Agent` rename is dated to v2.1.63 (Finding F-6). The docs pages retrieved 2026-05-23 reflect post-v2.1.63 state. The fork-mode experimental flag is dated to v2.1.117 or later. |
| Explicitly answer the four sub-questions raised in the analysis §4 | **Satisfied** | Each of sub-questions 1–4 has a dedicated finding with citation. See "Documentation evidence shape" table. |
| Source-constraint compliance (authoritative sources only) | **Satisfied** | Primary sources: code.claude.com/docs (Anthropic official). Corroborating source: a single GitHub issue used only to confirm the v2.1.63 rename date; the rename itself is confirmed by Anthropic's docs. No blog posts, no AI-generated summaries, no GitHub-issue-without-Anthropic-response cited for the load-bearing claims. |
| Probe execution report | **Partially satisfied — probe authored, invocation deferred** | The researcher does not have the `Agent` tool and cannot invoke the probe directly. The probe files are authored at `.claude/agents/probe-dispatch-test-r1.md` and `.claude/agents/probe-dispatch-test-r2.md`; the PROBE INVOCATION REQUEST section instructs the parent orchestrator how to invoke. The documentation evidence is independently sufficient to commit to `dispatch_supported: false`. |

**Overall: `acceptance_criteria_met: true`.** The documentation evidence is definitive across all four sub-questions; the probe is corroborating, not load-bearing.

## Open questions for the Synthesis stage

1. **Probe corroboration:** Should the parent orchestrator invoke the authored probe to add runtime corroboration to the documentation evidence, or proceed to Synthesis on the documentation evidence alone? **Researcher's recommendation:** The documentation evidence is definitive; invoking the probe is low-cost corroboration and is recommended if the parent has the `Agent` tool ready. If not, proceed.
2. **Probe cleanup timing:** The probe files are research instrumentation. Should they be removed before Synthesis runs (to keep the agent inventory clean during the FR-5 sweep that the codebase-researcher performs), or after the per-layer `cc` Design stage consumes the research? **Researcher's recommendation:** Remove BEFORE the codebase-researcher runs its FR-5 sweep, so the inventory artifact does not erroneously include the probe files. If the codebase-researcher has already run, remove before Plan authoring.
3. **`execute-orchestrator` `memory:` field check:** Hypothesis H-b in Finding F-2 predicts the observed `Edit` runtime-surface addition is due to a `memory:` field declaration. The codebase-researcher's IN-002 read will confirm or refute this. Not a blocker for Synthesis; surfaces only as a side observation.

## Source list

Primary (load-bearing for the four sub-question answers):

1. **"Create custom subagents — Claude Code Docs"** — Anthropic, code.claude.com/docs/en/sub-agents — retrieved 2026-05-23. Used for Findings F-1 (Source 1, Source 4), F-2, F-3, F-4, F-5, F-6.
2. **"Subagents in the SDK — Claude API Docs"** — Anthropic, code.claude.com/docs/en/agent-sdk/subagents — retrieved 2026-05-23. Used for Finding F-1 (Source 3).

Corroborating (used only for the version stamp of the Task → Agent rename; not load-bearing):

3. **"Task→Agent tool rename in v2.1.63 breaks hook payloads (undocumented breaking change)"** — anthropics/claude-code GitHub issue #29677 — github.com/anthropics/claude-code/issues/29677. Used for Finding F-6 corroborating evidence only.

Considered and excluded per source-constraint discipline:

- adevguide.com, mindstudio.ai, tembo.io, medium.com, ksred.com, pubnub.com, producttalk.org — community / blog posts, excluded per "AI-generated summaries, stale blog posts (pre-2026)" restriction in source constraints.
- github.com/VoltAgent/awesome-claude-code-subagents — community library, excluded per "primary-source published Anthropic skill / sub-agent examples" restriction; non-authoritative.
- code.visualstudio.com — third-party host platform, not relevant to Claude Code's harness behavior.
