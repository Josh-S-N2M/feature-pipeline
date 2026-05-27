---
id: research-note-T-003
topic_id: T-003
topic_name: Capability-coverage decision frames in agent platforms
status: complete
generated: 2026-05-26T00:00:00Z
generated_by: discovery-external-researcher
feature_run: pipeline-cross-artifact-discipline-r1
---

# T-003 — Capability-coverage decision frames in agent platforms

## Topic and research question

**Topic:** Capability-coverage decision frames in agent platforms.

**Research question (verbatim from prompt):** What's the prior art for capability-fitness analyses in agent ecosystems — LangGraph, AutoGen, AutoGPT, OpenAI Assistants, Anthropic's own agent literature — and is a Why / How / Anti-patterns trifecta a community pattern, an idiosyncratic shape, or novel for the project?

## KB-gap justification (from Research Plan)

No project KB covers cross-platform agent-capability frames. `KB-cc-design` covers Claude-Code-specific skill design (Principle 2 — skill loading on-demand; Principle 1 — pick the lowest-cost primitive); it does not survey alternative frameworks' patterns for new-concept-to-capability mapping. `KB-task-decomposition` covers PV-tier decomposition, not capability decomposition. The W/H/A trifecta in PRD's FR-7 is a specific shape — a designer needs sourced precedent (or its absence) to commit.

## Executive summary

Every major agent platform surveyed (Anthropic Agent Skills, LangGraph/LangChain, OpenAI Assistants + Agents SDK, Microsoft Agent Framework / AutoGen successor, CrewAI, Semantic Kernel, plus Perplexity's production guidance) prescribes a **decision frame for when to add a new capability** (tool, skill, plugin, or specialist agent). The frames are universally **prose principles, not a mandated structured artifact** — no surveyed platform requires a fixed-shape rationale document at design time. The shared substance across platforms collapses to three recurring ideas: (a) **need-justification** ("start simple; add only when measurably necessary"), (b) **scope/lifecycle hygiene** ("when to use, when to stop, how it composes"), and (c) **anti-pattern defenses** ("tool/skill proliferation degrades accuracy"). The Why / How / Anti-patterns trifecta in FR-7 is therefore a **structural codification of community substance, not novel content** — its differentiator is the *mandate to write it down at design time* rather than rely on prose-only principles or post-hoc eval feedback. The strongest anti-pattern the literature documents — and the one FR-7 must defend against — is **capability proliferation**: agents demonstrably degrade in selection accuracy once tool/skill counts exceed roughly 10–20 per context.

## Per-platform findings

### Finding 1 — Anthropic Agent Skills: evaluation-driven, no mandated artifact

**Claim.** Anthropic's official guidance for Agent Skills is **discovery-driven, not specification-driven**: identify capability gaps by running agents on representative tasks, then build skills incrementally to address what's missing. No fixed-shape design artifact (Why/How/Anti-patterns or equivalent) is mandated at design time. The progressive-disclosure mechanism (3-level: metadata → SKILL.md → references) is the architectural defense against context bloat, not a design rubric.

**Source.** Anthropic Engineering Blog, "Equipping agents for the real world with Agent Skills," 2025-10-16. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

**Quote (≤15 words).** "Identify specific gaps in your agents' capabilities by running them on representative tasks."

**Confidence.** High (official primary source from the platform vendor).

**Caveats.** Anthropic's open-standard Agent Skills format codifies *structure* (SKILL.md, frontmatter, optional references/) but not a *decision artifact* that the designer must author per skill. The "design discipline" lives in the Skill Quality Checklist of the skill-creator skill, which lists post-hoc verification items rather than a pre-design rubric.

---

### Finding 2 — Perplexity (production Skills practice): evals-before-skill, three named anti-patterns

**Claim.** Perplexity's published production discipline for Agent Skills is the most explicit cross-platform analog to a structured pre-design rubric. They prescribe (a) **eval-first** — write evals (including negative/forbidden-load examples) before authoring the skill; (b) explicitly named **three anti-patterns**: system-prompt recapitulation (don't promote globally-relevant knowledge to a conditionally-loaded skill), fast-changing remote-dependency drift (don't ship a skill that wraps an MCP endpoint whose surface mutates faster than you can maintain), and off-target side-effects (every new skill risks degrading every existing skill). They also assert there is **no first-principles answer** for whether a skill is needed — only empirical inspection.

**Source.** Perplexity Research, "Designing, Refining, and Maintaining Agent Skills at Perplexity," undated (2026). https://research.perplexity.ai/articles/designing-refining-and-maintaining-agent-skills-at-perplexity

**Quote (≤15 words).** "Every time you add an additional Skill, you risk making every other Skill slightly worse."

**Confidence.** High (engineering blog from a company operating multi-agent Skill systems at scale).

**Caveats.** Even Perplexity's prescription is prose-and-checklist rather than a mandated document template. The closest formal artifact is the eval suite itself. Their stance that there is "no definitive answer from first principles alone" is a direct rebuke of structured-decision-frame approaches that try to short-cut empirical validation.

---

### Finding 3 — LangChain / LangGraph: tool-binding tradeoff prose, no design artifact

**Claim.** LangChain/LangGraph's official documentation frames tool addition as a **runtime-tradeoff decision** (static vs. dynamic tool sets, pre-registered vs. runtime-discovered, "too many tools may overwhelm the model"). It prescribes **principles** for tool design (clear docstrings, one-tool-one-purpose, parallel-safe marking) but mandates no design-time decision artifact. LangGraph's "Thinking in LangGraph" guide walks through *graph composition* decision-making (which steps become nodes) but for *tools* the discipline is a single rule of thumb: clear docstrings + focused tools + handle errors.

**Source.** LangChain Docs, "Agents" page (langchain-ai). https://docs.langchain.com/oss/python/langchain/agents — and "Thinking in LangGraph," https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph

**Quote (≤15 words).** "Too many tools may overwhelm the model (overload context) and increase errors."

**Confidence.** High (official platform documentation).

**Caveats.** LangGraph's existence of `langgraph-bigtool` (a library specifically for agents with hundreds of tools, using semantic-search retrieval) is itself implicit acknowledgement that the unstructured "just bind tools" pattern breaks at scale. The architectural answer is retrieval, not a design-time decision artifact.

---

### Finding 4 — OpenAI Assistants / Agents SDK: "add specialists only when the contract changes"

**Claim.** OpenAI's official orchestration guide for multi-agent workflows prescribes a **prose principle** for when to add a new specialist agent: only when capability isolation, policy isolation, prompt clarity, or trace legibility materially improves. The named anti-pattern is **premature specialization** — splitting too early creates more prompts, more traces, more approval surfaces without quality gain. For function-calling tools, the guidance is similarly prose-only: "fewer than 20 functions available at the start of a turn" is the soft cap; use tool_search to defer the rest. No structured design artifact is mandated.

**Source.** OpenAI API Docs, "Orchestration and handoffs" guide. https://developers.openai.com/api/docs/guides/agents/orchestration — and "Function calling" guide. https://developers.openai.com/api/docs/guides/function-calling

**Quote (≤15 words).** "Add specialists only when they materially improve capability isolation, policy isolation, prompt clarity, or trace legibility."

**Confidence.** High (official platform documentation).

**Caveats.** OpenAI's `tool_search` (gpt-5.4+) and Anthropic's tool-search feature point to a converging architectural pattern (load-on-demand) that aligns with Anthropic's progressive-disclosure principle in Skills. The decision frame is "is it material?" — not "fill out a structured form."

---

### Finding 5 — Microsoft Agent Framework (AutoGen successor): "simplest pattern that meets the requirement"

**Claim.** AutoGen is in maintenance mode; new work routes to Microsoft Agent Framework (MAF). MAF's workflows guide prescribes a **graduated complexity ladder** — single agent with tools → agents-as-tools → handoff → group chat → workflow with graph — and mandates "use the simplest pattern that meets the requirement." The decision factor across the ladder is a **four-way question**: who decides (a) which subtask is next, (b) whether to involve another agent, (c) when to ask a human, (d) how to handle partial failure. "The model" pushes toward agents-as-tools; "the developer" pushes toward workflows. The decision is **prose**; no mandated artifact.

**Source.** Microsoft Learn, "Workflows" in Microsoft Agent Framework documentation. https://learn.microsoft.com/en-us/agent-framework/journey/workflows — and "Workflow-oriented multi-agent patterns," https://learn.microsoft.com/en-us/agents/architecture/multi-agent-workflow-oriented

**Quote (≤15 words).** "Most useful when you need guaranteed execution order that a single agent can't reliably provide."

**Confidence.** High (official Microsoft documentation post-AutoGen transition).

**Caveats.** MAF documents *when to use which orchestration shape* far more rigorously than *whether to add a new capability/specialist at all*. The "specialist count" question is implicit in the ladder ("don't reach higher than you need") rather than codified as a rubric.

---

### Finding 6 — CrewAI: 80/20 rule for tasks-vs-agents, "give agents minimal tools"

**Claim.** CrewAI's official Crafting Effective Agents guide states a **prose discipline rule**: "80% of your effort should go into designing tasks, and only 20% into defining agents." For tools, the explicit principle is "give agents minimal tools" — overloading degrades performance. The "Evaluating Use Cases" guide provides a Crews-vs-Flows decision matrix on complexity × precision axes, which is a **structured decision rubric** (the closest cross-platform analog to the trifecta), but it is a *runtime-architecture* selector, not a per-capability rationale. CrewAI also names a specific anti-pattern: a single "research and write" agent will underperform two specialized agents.

**Source.** CrewAI Documentation, "Crafting Effective Agents." https://docs.crewai.com/en/guides/agents/crafting-effective-agents — and "Evaluating Use Cases." https://docs.crewai.com/en/guides/concepts/evaluating-use-cases

**Quote (≤15 words).** "80% of your effort should go into designing tasks, and only 20% into defining agents."

**Confidence.** High (official platform documentation).

**Caveats.** The Crews-vs-Flows matrix shows the community *does* sometimes codify structured decision rubrics — but it's still prose-tabular, not a mandated authored artifact per agent or per capability.

---

### Finding 7 — Microsoft Semantic Kernel: "import only the necessary plugins"

**Claim.** Semantic Kernel's official guidance is the most explicit "less is more" prose-rule of the surveyed platforms. The plugin-design guidance prescribes (a) "import only the necessary plugins" to reduce false-positive function calls, (b) explicit balance between "single-responsibility functions" (reusable but token-heavy) and "multi-responsibility functions" (cheaper but less reusable), (c) AI-friendly naming. The Skills-to-plugins renaming history (October 2023) demonstrates that even *terminology* for capability-units is unsettled across the ecosystem. No structured per-capability decision artifact is mandated.

**Source.** Microsoft Learn, "Plugins in Semantic Kernel." https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/ — and DevBlogs, "Skills to plugins: fully embracing the OpenAI plugin spec in Semantic Kernel," 2023-10-04. https://devblogs.microsoft.com/semantic-kernel/skills-to-plugins-fully-embracing-the-openai-plugin-spec-in-semantic-kernel/

**Quote (≤15 words).** "Import only the plugins that contain functions necessary for your specific scenario."

**Confidence.** High (official Microsoft documentation).

**Caveats.** Semantic Kernel's architecture (kernel-as-DI-container) leans toward runtime composition rather than design-time prescription; "what plugins exist" is a code-organization question more than a capability-rationale question.

---

### Finding 8 — Cross-platform anti-pattern: tool/skill proliferation degrades selection accuracy

**Claim.** Multiple independent engineering blogs and pattern catalogues document the same anti-pattern using consistent measurements: agent selection accuracy degrades sharply beyond roughly 10–20 tools per reasoning context. Published thresholds: 5–10 tools is the practical sweet spot (per OpenAI guidance, "fewer than 20 functions at the start of a turn"); the Berkeley Function Calling Leaderboard shows isolated tool-calling at ~96% accuracy dropping to ~13–15% in large-toolset multi-turn settings. One widely-cited case study reports paring tools from 16 to 1 raised success from 80% → 100% with 40% lower tokens. The mechanism is consistently described as attention dilution / context rot from tool-description token competition.

**Source.** Multiple corroborating sources:
- Encyclopedia of Agentic Coding Patterns, "Tool Sprawl." https://aipatternbook.com/tool-sprawl
- Agent Patterns, "Too Many Tools (Anti-Pattern)." https://www.agentpatterns.tech/en/anti-patterns/too-many-tools (2026-03-16)
- Tianpan blog (independent engineering analysis), "The Tool Explosion Problem." https://tianpan.co/blog/2026-04-13-tool-explosion-problem-agent-tool-selection-at-scale (2026-04-13)
- Kurtis Van Gent, "Stop Drowning Your Agent in Tools." https://kvg.dev/posts/20260110-tool-bloat-ai-agents/ (2026-01-10)

**Quote (≤15 words).** "Adding tool number seventeen makes the agent worse at the first sixteen." (Tool Sprawl)

**Confidence.** Medium-high (multiple independent corroborating sources naming the same pattern; one source — Tool Sprawl — appears to be a community-curated catalog rather than a vendor primary; the platform-vendor sources (OpenAI, Anthropic) corroborate the underlying mechanism through their tool-search / progressive-disclosure features).

**Caveats.** Exact thresholds vary by model and task complexity. The cliff position (10? 20? 30?) is fuzzy; what's robust is (a) the cliff exists, (b) it sits below intuition's expectation, (c) load-on-demand patterns (Anthropic progressive disclosure, OpenAI tool_search, LangGraph bigtool, MCP allowlist scoping) are the converging architectural defense.

---

## Synthesis (analysis — clearly marked as judgment)

This is my analysis of patterns emerging across the platforms surveyed.

### Substantive convergence

Every platform's decision frame collapses to three recurring categories, regardless of vocabulary:

| Category | Anthropic | LangGraph | OpenAI | MAF | CrewAI | Semantic Kernel |
|---|---|---|---|---|---|---|
| **Need-justification** ("only when materially necessary") | "Identify gaps via eval" | "Start simple, dynamic only when needed" | "Add specialists only when contract changes" | "Simplest pattern that meets the requirement" | "80/20: tasks first" | "Import only the necessary" |
| **Scope/lifecycle hygiene** (when it triggers, when it doesn't) | Description = trigger | Docstring = trigger | Function description + system prompt | Routing rules + handoff edges | Role + goal + backstory | Description attribute + naming |
| **Anti-pattern defense** | Progressive disclosure | Tool search / bigtool | tool_search; ≤20 functions | Graduated ladder; "don't split early" | "Minimal tools per agent" | "Import only necessary" |

The **substance** of the W/H/A trifecta (Why = need-justification, How = scope/trigger hygiene, Anti-patterns = defenses) maps cleanly onto categories every platform addresses. **No platform addresses these in a single mandated structured artifact authored at design time.**

### Structural divergence — the trifecta's distinctive shape

The closest cross-platform analog to a *structured decision artifact* is CrewAI's Crews-vs-Flows matrix (complexity × precision), and that's a runtime-architecture selector, not a per-capability rationale. The closest pre-design discipline is Perplexity's "write evals first" — which is a *practice* with a deliverable (the eval suite), not a *document template*.

The Why/How/Anti-patterns trifecta as a **mandated, authored-at-design-time, per-capability artifact** appears to be **novel as a codification** even though every component of its content is well-trodden community substance.

### Why the codification matters (the value the trifecta adds over prose)

Prose principles produce drift. Across the surveyed sources, the same anti-patterns recur in 2024 → 2025 → 2026 posts — suggesting that even teams who have read the principles continue to violate them in production. The trifecta's contribution is **forcing the rationale into a reviewable artifact**, which:

- Creates an audit point (a reviewer can ask "where's the rationale?" instead of inferring from code).
- Concentrates the decision: "why-now" and "what-could-go-wrong" sit next to each other instead of being scattered across docstrings, system prompts, and tribal memory.
- Defends specifically against proliferation, which is the most universally-documented failure mode (Finding 8).

### Trade-offs the trifecta will face

- **Structured artifact vs. free-form rationale.** Every platform stops short of mandating a structured form, suggesting the cost of the mandate (overhead, ritualistic compliance, "filling in the boxes" without thought) is non-trivial. The trifecta will need anti-ritualism defenses (e.g., reviewers checking *substance* not *presence*).
- **Mandated-per-concept vs. mandated-only-when-proposing-new.** Perplexity's stance ("no first-principles answer; you must run evals") implies that *every* proposed new capability needs justification; but most platforms' "import only the necessary" rules suggest justification is needed *only when adding*, not when proposing-and-rejecting. The trifecta's mandate scope (every potential new capability vs. only authorized new ones) is the design question.
- **Anti-pattern coverage vs. inventory of platform-specific failure modes.** The literature names many anti-patterns (proliferation, off-target trigger, drift from external dependency, system-prompt recapitulation, "god agent," tool-sprawl, premature specialization). The trifecta's Anti-patterns section should default to a curated *short* list with rationale rather than an exhaustive catalogue, to avoid ritual.

## Acceptance-criteria check

| Acceptance criterion | Status | Reasoning |
|---|---|---|
| Identifies ≥ 3 agent platforms' patterns for "we have a new concept; do we need a new tool/skill/capability?" | **Satisfied.** | Seven platforms surveyed in detail: Anthropic Agent Skills, LangGraph, OpenAI Assistants/Agents SDK, Microsoft Agent Framework (AutoGen successor), CrewAI, Semantic Kernel, Perplexity production discipline. |
| For each, names whether a structured decision artifact is required at design time | **Satisfied.** | Each finding addresses this explicitly. Universal answer: **no platform mandates a structured per-capability decision artifact at design time**; all use prose principles, checklists, or eval-first practices. CrewAI's matrix is the closest, but for orchestration-shape selection, not per-capability rationale. |
| Identifies ≥ 2 trade-offs (trifecta-style structured vs. free-form rationale; mandated-per-concept vs. mandated-only-when-proposing-new) | **Satisfied.** | Synthesis section names both, plus a third (anti-pattern coverage breadth). |
| Surfaces any anti-patterns the literature documents (skill-proliferation; orphaned-capability decay) that FR-7's design should defend against | **Satisfied.** | Finding 8 documents tool/skill-proliferation with quantified thresholds and multiple corroborating sources. Finding 2 names three additional anti-patterns from Perplexity (system-prompt recapitulation; drift from fast-changing external dependencies; off-target side effects on existing skills). Finding 4 names "premature specialization." Orphaned-capability decay is touched implicitly by Perplexity's drift anti-pattern (skills wrapping fast-moving endpoints decay) but not surfaced as a named primary anti-pattern in the surveyed sources. |

## Open questions

1. **Orphaned-capability decay** is not named as a primary anti-pattern in the surveyed primary sources. The closest analog is Perplexity's drift-from-fast-changing-MCP-endpoint warning. If FR-7 wants explicit defense against orphaned-capability decay, the design may need to *contribute* the framing rather than cite it. (Could be project-specific.)
2. **Granularity** — when the trifecta is mandated, is it at the level of "every new SKILL.md" or "every new function/tool"? Surveyed platforms differ on what the unit of capability is (skill vs. plugin vs. function vs. specialist agent). The trifecta's unit of mandate should be defined explicitly.
3. **Reviewer enforcement mechanics** — the trifecta's value depends on reviewers checking substance not presence. None of the surveyed sources prescribes review heuristics for capability-rationale documents (because none mandates such a document). This is a green-field design question.

## Source list

- Anthropic. "Equipping agents for the real world with Agent Skills." *Anthropic Engineering Blog*, 2025-10-16. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic / Claude Platform. "Agent Skills — overview." Claude API Docs. https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic. "Building Agents with Skills: Equipping Agents for Specialized Work." Claude.com blog, 2026-01-22. https://claude.com/blog/building-agents-with-skills-equipping-agents-for-specialized-work
- Anthropic. "Building Effective AI Agents." *Anthropic Engineering*. https://www.anthropic.com/engineering/building-effective-agents
- Anthropic GitHub. `skills/claude-api/shared/agent-design.md`. https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/agent-design.md
- Anthropic GitHub. `skills/skill-creator/SKILL.md`. https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- Perplexity Research. "Designing, Refining, and Maintaining Agent Skills at Perplexity." https://research.perplexity.ai/articles/designing-refining-and-maintaining-agent-skills-at-perplexity
- LangChain Docs. "Agents." https://docs.langchain.com/oss/python/langchain/agents
- LangChain Docs. "Thinking in LangGraph." https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
- LangChain Docs. "Choosing between Graph and Functional APIs." https://docs.langchain.com/oss/python/langgraph/choosing-apis
- LangChain GitHub. `langgraph-bigtool`. https://github.com/langchain-ai/langgraph-bigtool
- OpenAI. "Orchestration and handoffs." OpenAI API Docs. https://developers.openai.com/api/docs/guides/agents/orchestration
- OpenAI. "Function calling." OpenAI API Docs, 2025-08-07. https://developers.openai.com/api/docs/guides/function-calling
- OpenAI. "Assistants API tools." OpenAI API Docs. https://developers.openai.com/api/docs/assistants/tools
- Microsoft Research. "AutoGen v0.4: Reimagining the foundation of agentic AI." 2025-02-25. https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/
- Microsoft Learn. "Workflows" (Microsoft Agent Framework). https://learn.microsoft.com/en-us/agent-framework/journey/workflows
- Microsoft Learn. "Workflow-oriented multi-agent patterns." https://learn.microsoft.com/en-us/agents/architecture/multi-agent-workflow-oriented
- Microsoft Learn. "Microsoft Agent Framework Workflows Orchestrations — Handoff." https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff
- Microsoft DevBlogs. "A Tour of Handoff Orchestration Pattern." 2026-05-08. https://devblogs.microsoft.com/agent-framework/a-tour-of-handoff-orchestration-pattern/
- CrewAI Docs. "Crafting Effective Agents." https://docs.crewai.com/en/guides/agents/crafting-effective-agents
- CrewAI Docs. "Evaluating Use Cases for CrewAI." https://docs.crewai.com/en/guides/concepts/evaluating-use-cases
- CrewAI Docs. "Agents." https://docs.crewai.com/en/concepts/agents
- Microsoft Learn. "Plugins in Semantic Kernel." 2024-12-10. https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/
- Microsoft Learn. "Configuring Agents with Semantic Kernel Plugins." https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-functions
- Microsoft DevBlogs. "Skills to plugins: fully embracing the OpenAI plugin spec in Semantic Kernel." 2023-10-04. https://devblogs.microsoft.com/semantic-kernel/skills-to-plugins-fully-embracing-the-openai-plugin-spec-in-semantic-kernel/
- Encyclopedia of Agentic Coding Patterns. "Tool Sprawl." https://aipatternbook.com/tool-sprawl
- Agent Patterns. "Too Many Tools (Anti-Pattern)." 2026-03-16. https://www.agentpatterns.tech/en/anti-patterns/too-many-tools
- Tianpan blog. "The Tool Explosion Problem: Why Your Agent Breaks at 30 Tools." 2026-04-13. https://tianpan.co/blog/2026-04-13-tool-explosion-problem-agent-tool-selection-at-scale
- Tianpan blog. "The Over-Tooled Agent Problem." 2026-04-19. https://tianpan.co/blog/2026-04-19-over-tooled-agent-problem
- Kurtis Van Gent. "Stop Drowning Your Agent in Tools." 2026-01-10. https://kvg.dev/posts/20260110-tool-bloat-ai-agents/
