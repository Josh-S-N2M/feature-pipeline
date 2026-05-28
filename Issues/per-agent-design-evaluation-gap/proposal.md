---
id: PROPOSAL-per-agent-design-evaluation-gap
doc_type: issue-proposal
status: open
since: 2026-05-27
version: 0.1.0
generated: 2026-05-27
generated_by: claude (main agent) — promotion-prep from sibling analysis, scope reshaped to the user's 2026-05-27 framing
feature_slug: pipeline-wide
scope: pipeline-wide (not feature-scoped)
mode: report-only
companion_artifacts:
  - Issues/per-agent-design-evaluation-gap/analysis.md
  - working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md
  - .claude/agents/
  - .claude/skills/
  - .claude/skills/KB-cc-design/references/principles.md
  - working/feature/pipeline-design-time-discipline-r1/
proposes_future_feature: per-agent-skill-budget-semantic-review-r1 (suggested slug)
escalates_from: ANALYSIS-per-agent-design-evaluation-gap
---

# Proposal — Full Per-Agent and Per-Skill Semantic Review for Pipeline-Value and Budget Balance

## Contents

- [x] TL;DR
- [x] Why this is the right next move
- [x] Scope of the review
- [x] Empirical baseline — what the inventory looks like today
- [x] Context-window budget — surprising finding
- [x] Methodology
- [x] Out of scope
- [x] Open questions
- [x] Cross-links

## TL;DR

The sibling analysis caught a structural gap: the feature pipeline iterates the *changed* surface, not the *full* inventory. R2a (`pipeline-design-time-discipline-r1`) closed the procedural side — feature runs now produce an agent-roster impact matrix and apply skill-coverage checks. What was never done is the substantive side: **walk every existing agent and every existing skill once, on purpose, and ask what value each one adds to the feature pipeline AND the execution pipeline, balanced against its tool + skill + context budget.** The user (2026-05-27) named this as the next thing they want done. This proposal seeds it.

The review is in-scope for direct execution, not a pipeline run — it is fact-gathering and judgment work whose only artifact is a structured matrix per agent and per skill. There is no architectural blast radius for a pipeline to manage. The output should drive concrete edits (deprecations, model/effort downshifts, tool prunes, skill consolidations) made surgically afterwards.

## Why this is the right next move

Three signals converge:

1. **The structural gap surfaced by the sibling analysis is procedural-only after R2a.** The pipeline now compels enumeration; it does not compel re-evaluation of agents and skills that the pipeline has not touched in months. The current inventory is the accumulated residue of every prior feature run plus drift. Nothing has examined the whole inventory at once for fit-to-purpose.

2. **The audit subsystem is clean (100/100) but the runtime cost of the agent surface is unmeasured.** Tool schemas defer, but skill preloads, system prompts, persistent-memory pulls, and MCP allowlist propagation all contribute to per-invocation token cost. 37 agents × 45 skills is a large product without a load-bearing reason for every cell.

3. **The 1M-context lever the user named is already pulled.** The research findings (see §"Context-window budget" below) show that every agent on `model: opus` is already running on 1M Opus 4.7. The lever to balance budget is not "turn on 1M" — it is **which agents need opus vs sonnet, which skills each agent actually loads, and which tools each agent has access to.** The user's intuition about the budget question is right; the specific mechanism is different from what the framing suggested.

## Scope of the review

Two parallel sweeps, one matrix each.

### Sweep A — per agent (37 rows)

For each file in `.claude/agents/*.md`, evaluate against six dimensions:

| Dimension | Question | Evidence to cite |
|---|---|---|
| **Pipeline fit** | Which stage of the feature pipeline OR the execution pipeline does this agent serve? Is it active? | `recipe-feature-pipeline/SKILL.md` dispatch table; execute-orchestrator state machine |
| **Model + effort fit** | Is `model: opus` + `effort: <X>` right for this agent's job? Would `sonnet` or `haiku` work? Does the agent's reasoning work justify the cost? | Frontmatter + body of the agent file; sample outputs from prior feature runs |
| **Tool surface fit** | Does the `tools:` allowlist match what the agent actually uses? Any overgrants (privilege expansion risk)? Any undergrants (forces fallback patterns)? | Agent body invocations; persistent memory if available |
| **Skill load fit** | For each entry in `skills:`, does the agent actually need it? Are any KBs loaded "just in case"? Are any missing? | KB cross-references in the agent body; skill descriptions |
| **Persistent memory fit** | Does the agent use `memory: project / user / none` appropriately? Is the agent's memory directory healthy or stale? | `.claude/agent-memory/<agent>/` contents |
| **Continued existence** | If this agent did not exist, what would break? Is the answer concrete and load-bearing? | Test of removal — would any pipeline stage fail? |

Output: a matrix row per agent with a verdict per dimension (`OK` / `DOWNSHIFT` / `PRUNE` / `EXPAND` / `DEPRECATE`) and a one-line rationale.

### Sweep B — per skill (45 rows)

For each `SKILL.md` under `.claude/skills/`, evaluate against six dimensions:

| Dimension | Question | Evidence to cite |
|---|---|---|
| **Audience and load shape** | Is this skill `model-invocable` (loaded on description-match) or `user-invocable` (slash command)? Is the audience identified correctly? | SKILL.md frontmatter |
| **Pipeline fit** | Which feature-pipeline or execution-pipeline stages reach for this skill? Which agents declare it in `skills:`? | Cross-reference into `.claude/agents/*.md` |
| **Substantive value** | Does the skill earn its preload cost? Or is it a thin pointer that the body of the agent could carry directly? | Skill body word-count, density, uniqueness vs the agent's prompt |
| **Reference set health** | Does `references/*.md` contain what the skill claims? Any stale links, dead pointers, drifted constants? | Direct read of the references directory |
| **Pairing discipline** | Platform-paired-with-design KBs (the 9-layer convention) — is the pairing actually preserved, or has drift opened between the two halves? | Cross-read the two files |
| **Continued existence** | If this skill did not exist, what would the consuming agents do — fall back to KB-general-coding-principles? Inline the content? Fail? | Test of removal |

Output: a matrix row per skill with a verdict per dimension.

### Synthesis

After both sweeps land, a short summary identifies:

- **High-confidence prunes** — agents or skills with `DEPRECATE` verdicts on multiple dimensions.
- **Downshift candidates** — agents on `opus` whose work would survive on `sonnet` at 5x lower per-token cost.
- **Skill consolidations** — pairs/triples of skills with overlapping bodies that should merge.
- **Tool allowlist tightenings** — overgrants found by Sweep A.
- **Pairing-drift repairs** — platform/design KB pairs that have drifted apart.

The summary's recommendations become a punch list for surgical direct-execution work afterwards.

## Empirical baseline — what the inventory looks like today

- **37 sub-agents** under `.claude/agents/`. **34 declare `model: opus`**; **3 declare `model: sonnet`** (need to identify which three and why). No agent uses `claude-opus-4-7[1m]` or any explicit 1M-variant syntax.
- **45 skills** under `.claude/skills/` per the latest project-audit report.
- **22 sub-agent persistent-memory directories** under `.claude/agent-memory/` — confirms most agents have project-scope memory; freshness is unverified.
- **0 hooks** beyond the two scripted ones; **1 MCP config** at `.mcp.json` (5 servers post-gitnexus removal); **1 settings file**.

These are not a problem on their own. They are the inventory we have not looked at as a whole.

## Context-window budget — surprising finding

The user named the 1M context window as a lever they could pull. Research and on-disk inspection of the inventory show that **the lever is already engaged for almost every agent in the pipeline**. Specifically:

- The Claude Code build running this project shows the active model as `claude-opus-4-7[1m]` — the `[1m]` suffix is the harness-side display for the 1M-context variant of Opus 4.7.
- The frontmatter `model:` field accepts the alias `opus` (preferred for legibility) or the full ID `claude-opus-4-7`. The 1M behavior comes from being on Opus 4.7 itself, not from a separate flag — the alias `opus` resolves to the current Opus 4.7 1M behavior in this Claude Code version.
- **34 of 37 sub-agents already use `model: opus`** — meaning they already run on the 1M context window by default. No frontmatter change is needed to unlock more headroom.
- **Pricing is identical** for requests using 200k vs requests using the full 1M window ($5 / $25 per MTok input/output on Opus 4.7). However, **Opus 4.7's new tokenizer can produce up to ~35% more tokens for the same input text** than prior generations, so effective per-request cost rose at the model switch even though per-token pricing did not. Prompt caching (0.1x read multiplier) and batch (50% discount) offset.
- **Sub-agents do NOT inherit the parent's model** — each agent must declare its own `model:`. The current inventory honors this (every agent has an explicit declaration).
- **All major features work at 1M** — tool use, vision, extended thinking, files API, prompt caching. No documented restrictions.

**What this means for the review:**

The interesting budget questions are *not* "should this agent get 1M?" — it already does. The interesting questions are:

1. Does this agent need to be on Opus at all, or would Sonnet 4.6 (also 1M, but ~5x cheaper per token) deliver the same output quality for its workload?
2. What is the actual context cost per invocation, dominated by skill preloads + system prompt + tool schemas (deferred but allowlisted)? Where is the per-invocation budget *going*?
3. Are any of the 3 sub-agents on `sonnet` under-provisioned for reasoning-heavy work they're actually being asked to do? Are any of the 34 on `opus` over-provisioned?

The review should answer these directly.

A secondary finding worth recording: the `[1m]` suffix on the model ID is consistent with how Anthropic differentiates context variants on prior models (e.g. some older Sonnet variants exposed similar variant suffixes). The treatment of `[1m]` as the canonical disambiguator suggests Anthropic intends future model generations to also use bracket-suffix variant notation. The frontmatter alias `opus` insulates the pipeline from that detail.

## Methodology

Direct execution, not a pipeline run. Concretely:

1. **Author the matrix scaffold** — one row per agent (37), one row per skill (45). Header row carries the six dimensions defined above.
2. **Walk the inventory** — for each agent, read the file + its persistent-memory directory + the skills it declares. For each skill, read SKILL.md + references/*.md + grep for consumers.
3. **Fill verdicts and rationale** — per-cell verdict + a one-line evidence-citing rationale.
4. **Cross-check overlaps** — Sweep A reveals which agents declare which skills; Sweep B verifies those declarations from the skill side. Discrepancies are findings.
5. **Synthesize the punch list** — produce a separate `recommendations.md` with high-confidence prunes / downshifts / consolidations / tightenings / pairing repairs.
6. **Halt before action** — the review is fact-gathering only. The punch list is the input to a separate decision the user makes about which recommendations to apply.

Estimated effort: 1–2 working days for the two sweeps + synthesis. The actual edits afterwards are a separate, surgical pass.

## Out of scope

- Authoring new agents or skills. This is a review of what exists.
- Refactoring the pipeline's stage topology. R2a + the unbiased-status review identified that as orthogonal work.
- Re-running R2a's procedural mechanisms. They are in place; this review uses them.
- Pipeline-running this review. Direct execution is the correct mode per the empirical evidence from `Issues/direct-counterfactual-repair/analysis.md`.
- Tool budget changes that affect MCP allowlists at the project level — those go through the MCP design discipline (`KB-mcp-design`).

## Open questions

- **Q1 (Scope size — agents only? skills only? both?)** The user's framing named "each skill"; the analysis names per-agent gaps. The proposal proposes both because they share underlying budget pressure. Confirm: both, or sequence them (skills first)?
- **Q2 (Verdict vocabulary)** The proposed five verdicts (`OK / DOWNSHIFT / PRUNE / EXPAND / DEPRECATE`) cover the action shapes. Is there a verdict shape we're missing — e.g. `MIGRATE` (move skill content into an agent body, retire the skill file)? `REPAIR` (skill is correct but its references are stale)?
- **Q3 (Output artifact location)** Should the matrix and recommendations land under `working/feature/per-agent-skill-budget-semantic-review-r1/` even though no pipeline run is being opened? Or under `Issues/per-agent-design-evaluation-gap/`? Or a new `reviews/` top-level directory?
- **Q4 (Sonnet downshift threshold)** What evidence justifies a recommendation to move an agent from Opus to Sonnet? Sonnet 4.6 is also 1M and ~5x cheaper, but reasoning depth differs. Possible threshold: "the agent's body contains no `effort: xhigh` and produces outputs that pattern-match well-trodden conventions (frontmatter, lint, simple validation)." User input needed.
- **Q5 (Cadence)** Is this a one-shot review (closed when the matrix is filled and the punch list is applied), or a recurring discipline (quarterly review-and-prune)? If recurring, the matrix becomes a living document and needs an event or calendar trigger that this project actually has (per §O of the deferral register, time-based triggers fail here).
- **Q6 (Confirmation of 1M default)** The empirical evidence is that `model: opus` already runs on the 1M context variant in this Claude Code build. Should the review file a small confirming test — author a minimal sub-agent, send it a >200k-token payload, observe whether it succeeds — to make the assumption falsifiable rather than research-derived?

## Cross-links

- **Sibling analysis (root):** [Issues/per-agent-design-evaluation-gap/analysis.md](analysis.md) — the structural gap; remains open as the underlying concern this proposal addresses. After this proposal's review runs, the analysis can move to `complete` because the substantive review the analysis identified as missing will have been performed.
- **R2a procedural mechanisms** (now in place): [working/feature/pipeline-design-time-discipline-r1/](../../working/feature/pipeline-design-time-discipline-r1/) — agent-roster-impact-matrix and skill-coverage checks. The review described here applies those mechanisms once to the whole inventory.
- **Direct-execution precedent:** [Issues/direct-counterfactual-repair/analysis.md](../direct-counterfactual-repair/analysis.md) — establishes that CLEANUP-class and survey-class work is correctly done direct, not through the pipeline.
- **KB-cc-design Principle 9** — defensive vs active reasoning-configuration discipline; the per-agent sweep operationalizes the "active evaluation" half.
- **Context-window research sources** (the §Context-window budget findings):
  - [Claude Pricing Documentation](https://platform.claude.com/docs/en/about-claude/pricing)
  - [What's New in Claude Opus 4.7](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7)
  - [Context Windows Guide](https://platform.claude.com/docs/en/build-with-claude/context-windows)
  - [Subagents Documentation](https://code.claude.com/docs/en/subagents.md)
  - The harness's own runtime report (the active model ID is `claude-opus-4-7[1m]`).
