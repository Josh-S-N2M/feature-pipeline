---
id: ANALYSIS-per-agent-design-evaluation-gap
doc_type: issue-analysis
status: open
since: 2026-05-23
version: 0.2.0
escalated_to: PROPOSAL-per-agent-design-evaluation-gap
escalated_at: 2026-05-27
escalation_note: A sibling `proposal.md` was authored 2026-05-27 that reshapes Track B from the procedural mechanisms R2a delivered (now shipped via `pipeline-design-time-discipline-r1`) to a substantive whole-inventory review of the 37 sub-agents and 45 skills. The proposal carries the actionable work; this analysis remains the root structural-gap statement. Analysis transitions to `complete` when the review proposed in `proposal.md` runs and its punch list is acted on.
generated: 2026-05-23
generated_by: claude (orchestrator) — manual analysis from feature artifacts
feature_slug: devcontainer-mcp-provisioning-r1
scope: pipeline-wide (not feature-scoped)
mode: report-only
companion_artifacts:
  - working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md
  - working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md
  - working/feature/devcontainer-mcp-provisioning-r1/cc-design.md
  - adrs/ADR-0040-serena-narrowed-always-on.md
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md
---

# Feature-Pipeline Analysis — Per-Agent Design Evaluation Gap

## TL;DR

The feature pipeline has no demand-driven per-agent design step. Whenever a feature touches the agent surface (`.claude/agents/*.md` — tools, model, effort, skills, prompt body), the design discipline today is **supply-driven**: each new capability is mapped onto its likely-consumer agents, and every other agent in the inventory is left implicit under a "preserve invariant" framing. The codebase researcher for the current feature flagged this gap explicitly as Q-3 (`codebase-analysis-report.md` line 200, marked "Blocks design-cc-completion"); synthesis pre-decided D-9 as a single-option decision; the per-layer designer transcribed only the named-consumer set; the Architecture-Audit-bound reviewer caught count-consistency but not coverage; and **the gap reached Gate 4 unclosed.** The user identified it at Gate 4 review. A retroactive 36-row demand-side sweep was authored (`agent-roster-impact-matrix.md`) and confirmed the supply-driven view by coincidence, but the pipeline has no mechanism that *requires* that sweep, no mechanism that requires the parallel sweep for skills / model / effort, and no checkpoint that asks "does an existing skill cover this new domain concept — and if not, propose one with justification."

The bug is **not** "we forgot 28 agents" (this feature happened to be right). The bug is **the pipeline cannot tell whether it forgot them.**

---

## 1. Evidence — the chain that produced the gap in `devcontainer-mcp-provisioning-r1`

### 1.1 Discovery raised the question and marked it blocking

`working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md` (line 200, verbatim):

> "**Agent inventory scope for UI-1** — are the 36 agent files all in-scope, or are some (esp. the six `synth-*` files) deprecated and excluded from MCP wiring consideration? **Blocks design-cc-completion.**"

The researcher named the gap. Marked it blocking. The pipeline proceeded anyway.

### 1.2 Synthesis pre-decided the question as not-a-decision

`working/feature/devcontainer-mcp-provisioning-r1/synthesis/05-substrate-map.json` records D-9 (tool-to-agent allowlist mapping for UI-1) as a **single-option** decision. The synth-substrate agent summary stated:

> "D-9 (tool-to-agent allowlist) — the existing least-privilege convention is the only credible posture; the work is producing the mapping table."

> "Frames with fewer than 2 options (single-option, with no-alternatives rationale): … **D-9** (tool-to-agent allowlist) — the existing least-privilege convention is the only credible posture; the work is producing the mapping table."

This framing is technically correct but operationally insufficient. The "least-privilege convention" doesn't tell you which agents *demand* the new capability — it only tells you, *given* a demand-list, that the answer is narrow rather than broad. The demand-list itself was never produced.

### 1.3 Per-layer design invoked Principle 9 defensively, not actively

`working/feature/devcontainer-mcp-provisioning-r1/cc-design.md` line 204 (verbatim):

> "**Reasoning configuration discipline (KB-cc-design Principle 9):** This feature does **not** modify any agent's `model:`, `effort:`, or `skills:` fields. Only `tools:` is touched. The existing reasoning configuration on each consumer agent is preserved verbatim […]"

`cc-design.md` line 218 (verbatim):

> "The other 29 agents are NOT touched. This is the C-0445 grep-verified zero-`mcp__` invariant preserved for least-privilege."

Both are **defensive** invocations of discipline — they argue *for inaction* on the 29 untouched agents. They do not constitute *evaluation* of those agents against the feature's new domain (MCP). The C-0445 invariant is real, but invariant-preservation is a property of the action taken, not evidence that no other action was warranted.

### 1.4 The ADR carrying the closest related decision admitted the gap in writing

`adrs/ADR-0040-serena-narrowed-always-on.md` line 74 (Known Unknowns row, verbatim):

> "(a) Whether `design-iac` and `design-api` also occasionally touch audit-script Python (no current evidence; if true, they would be added in a follow-up — easy additive change)."

The ADR author named two specific candidate exceptions and explicitly stated *no evidence was sought*. The "follow-up" deferral hands the question to a future feature whose triggering condition is undefined.

### 1.5 The Architecture-Audit-bound reviewer flagged count consistency, not coverage

`blueprint-v1-review-issues.json` raised three blocking conditions (I-DR-BP-001 / 002 / 003). All three were about *propagation of the 7-vs-8 count* — i.e., that the Blueprint internally agreed on its own numbers. None asked whether *the chosen set was complete.* The reviewer's role per `KB-review-disciplines` is brief-honor + structural completeness; coverage of an inventory not enumerated in the brief is structurally outside its remit.

### 1.6 Blueprint v2 was approved with the gap intact

`blueprint-v2-review-issues.json` returned `verdict: APPROVED` with scores 93/92/92/88. No remaining conditions. The gap was undetectable to a reviewer working from the artifacts the pipeline produced.

### 1.7 The user identified the gap at Gate 4 (out-of-band)

Gate 4 conversation, 2026-05-23: the user asked for the rationale on why only 8 agents got MCP. The rationale-extraction pulled the trail above. A retroactive Track-A2 dispatch of `design-cc` produced `agent-roster-impact-matrix.md` (36 rows, demand-driven). The matrix confirmed the supply-driven set by independent evidence — 8 IN_CC_DESIGN, 0 NEWLY_PROPOSED, 28 EXPLICIT_NO. The `synth-*` agents were confirmed **active, not deprecated** (Q-3's hypothesis was false). ADR-0040's `design-iac` / `design-api` hedge was tested and found unsupported by current evidence.

**The matrix didn't change any feature output. It changed the confidence that the feature outputs were correct.** That confidence delta is what the pipeline did not produce.

---

## 2. The pattern is broader than MCP tools

The same defect shape applies to four agent-surface dimensions. Each has the same "preserve-on-untouched" defensive posture and no demand-driven sweep:

| Dimension | Current discipline | Gap |
|---|---|---|
| **`tools:` (MCP / Bash / etc.)** | Supply-side mapping (per server → likely consumer) | No reverse: per agent → which capabilities does this feature now offer that the agent should consume? |
| **`skills:` array** | Authors invoke skills they already know; `auditing-skills` validates structure post-hoc | No "skill-coverage check": when a feature introduces a new domain concept, no checkpoint asks *does an existing skill cover this — and if not, propose one with justification.* FR-11 (the W/H/A trifecta for MCP) was added in this run *only because the user pushed at Gate 3.* Without that push, this feature would have shipped without `KB-mcp-platform` / `KB-mcp-design`. |
| **`model:`** | KB-cc-design Principle 9: "don't change lightly" | No "is `opus` / `sonnet` / `haiku` still right for this agent given its expanded responsibilities?" sweep. The Principle protects from accidental change but doesn't compel intentional reassessment. |
| **`effort:`** | Same as model — Principle 9 defensive | Same gap as model. An agent whose responsibilities expand may genuinely need an effort bump; the discipline doesn't surface the question. |

All four share **one root cause**: the pipeline's design discipline iterates the *changed* surface, not the *full* inventory.

---

## 3. What's missing structurally

### 3.1 No mandatory pipeline artifact for per-agent evaluation

The feature pipeline produces 27 named sub-agent outputs and 5 named human gates. None of them require enumeration of all agents that share the surface a feature touches. `cc-design.md` carries a 7-row mapping table; nothing requires the 36th row to be authored, even with content "no change, no MCP need, evidence: …".

### 3.2 No skill-coverage discipline at Synthesis or Design

Synthesis enumerates decisions (D-1..D-13 in this run). None of those decision frames is "for each new domain concept introduced by this feature, does an existing skill cover it?" The substrate-map's "implementation-strategy mode" allows single-option decisions, which is correct in general but lets a *missing* decision pass undetected. There is no decision frame "should we author a new skill for X?" — even though FR-11 in this feature is exactly that kind of decision.

### 3.3 Existing audit machinery is post-hoc

`auditing-subagents`, `auditing-cc-configs`, `auditing-skills` exist (and are well-built). All three are **post-hoc validators**: they check authored artifacts against rules. None of them runs at *design time* to compel enumeration. The auditing-subagents skill cannot raise "you didn't evaluate `intake-prd-author` against the new MCP capability" because there's no design-time call site for that question.

### 3.4 KB-cc-design Principle 9 is defensive only

The verbatim wording in cc-design.md's invocation: *"This feature does **not** modify any agent's `model:`, `effort:`, or `skills:` fields."* This is a statement of action taken, not a statement of evaluation performed. A positive corollary — "for each existing agent on the touched surface, this feature evaluated and concluded X" — is not part of the Principle today.

### 3.5 The codebase researcher CAN raise the question, but cannot enforce closure

`codebase-analysis-report.md` line 200 demonstrates the discovery layer is structurally capable of surfacing the gap (it did, in writing, with "Blocks design-cc-completion"). The downstream pipeline ignored the block. There is no mechanism that makes a Q-N marked "Blocks X" an actual gate.

---

## 4. Why this is recurring (the meta-problem)

The user's framing at Gate 4: *"I have seen this come up when designing against agents before when we choose the Model and Effort. Also, what skills a new agent should have or if no skill exists the user is asked to consider creating a new one with justification."*

The recurrence pattern:

1. A feature touches the agent surface in one dimension (this run: `tools:`).
2. Design discipline correctly applies *for that dimension on the changed agents*.
3. The other three dimensions on those same agents, and all four dimensions on every untouched agent, **are evaluated by absence** — the design says "no change" without producing "and here is the per-agent evidence I considered."
4. Review machinery validates internal consistency of what was authored, which is necessary but not sufficient.
5. The gap is detectable only by an out-of-band reader who knows what wasn't checked.

The recurrence is structural, not motivational. Every individual sub-agent in this run did its job correctly per its current contract. The contracts themselves do not require demand-driven sweep.

---

## 5. What this means for the current feature

`devcontainer-mcp-provisioning-r1` survives the gap by accident: the retroactive matrix confirmed the supply-driven set. Specifically:

- 8/8 consumer set is correct (the matrix found 0 new agents needing MCP).
- `synth-*` agents are active-not-deprecated (Q-3's deprecated-hypothesis was false).
- ADR-0040's `design-iac` / `design-api` hedge was tested → no current evidence → hedge stands as "easy additive change" path if ever required.

The matrix's existence is itself a *band-aid*: it was authored only because the user caught the gap at Gate 4. Without that catch, the feature would have shipped with implicit-only coverage of 28 agents and no record of having considered them.

**The current feature is safe to advance.** The systemic flaw is not.

---

## 6. Recommended remediation paths

### 6.1 Track A — feature-scoped close-out (already executed)

`agent-roster-impact-matrix.md` exists; OI-7 in Blueprint v2 records the closure; the demand- and supply-driven views agree. Feature can proceed through Gate 4.

### 6.2 Track B — pipeline-scoped fixes (separate meta-feature `agent-roster-design-discipline-r1` recommended)

The recommendations below are options to be picked individually or as a set in a future feature. They are *not* in scope for `devcontainer-mcp-provisioning-r1`.

| Rec | Description | Owner stage | Cost shape |
|---|---|---|---|
| **B1** — Mandatory `agent-roster-impact-matrix.md` artifact | When a feature's Layer Scope activates Claude Code AND the change touches `.claude/agents/`, the per-layer design stage MUST produce a full-inventory matrix with one row per existing agent and per-dimension evaluation (tools / skills / model / effort) + evidence cell. | `design-cc` | New artifact per relevant feature; ~36 rows × 4 columns = ~144 cells; mostly "no change, evidence: …" |
| **B2** — Strengthen KB-cc-design Principle 9 from defensive to active | Update Principle 9 wording from "don't change lightly" to "actively evaluate, defaulting to no-change with explicit per-agent evidence." Forces designers to record the consideration, not just the inaction. | `KB-cc-design` | Discipline-text change; no new artifact |
| **B3** — Skill-Coverage Check as a Synthesis or Design checkpoint | For each new domain concept introduced by a feature, design must either (a) name the existing skill that covers it OR (b) propose a new skill with W/H/A trifecta justification OR (c) document why no skill is warranted. Would have caught FR-11 (W/H/A trifecta for MCP) on its own, without the user's Gate-3 push. | `synth-framer` or new step | New decision frame per concept; usually 1–3 per feature |
| **B4** — Make "Blocks X" markers in Discovery actually block | Today the codebase researcher can write "Blocks design-cc-completion" in a research note and the pipeline ignores it. Introduce a check at stage transitions that scans for unresolved "Blocks X" markers and refuses advance until they are closed (resolved, deferred with explicit OI-N, or marked false-positive). | orchestrator | Stage-transition check; cheap to implement |
| **B5** — Auditing-subagents adds a "feature-touch-coverage" rule | Post-hoc audit rule: for any feature that touched `.claude/agents/*.md`, the feature's working dir MUST contain an agent-roster-impact-matrix.md whose row-count equals the current `.claude/agents/*.md` file count. Catches missing artifacts before deliverable packaging. | `auditing-subagents` | New audit rule; runs at pre-ship |

**Highest-leverage subset** (claim, not directive): B1 + B3 + B4. B1 forces the artifact; B3 forces the skill-coverage question; B4 prevents the "Blocks X" marker from being silently lost.

### 6.3 What is NOT recommended

- **A new sub-agent dedicated to agent-roster review.** The existing `design-cc` is the correct owner; adding a sub-agent would proliferate primitives where a discipline + artifact contract is sufficient.
- **Splitting the Claude Code layer.** `design-cc` already covers `.mcp.json` + agents + skills + hooks + commands + plugins, which is a lot. The remedy is per-artifact-discipline (the matrix), not per-sub-agent decomposition.
- **Blocking this feature on Track B.** The matrix has been authored retroactively; the feature can ship. Track B is a process improvement, not a fix for this artifact.

---

## 7. Open questions for the meta-feature (when it exists)

1. **What counts as "touching the agent surface"?** Does adding a new sub-agent file count (clearly yes)? Does adding a new skill that some agents will load count (probably yes if it's a new dependency)? Does changing an MCP server's tool surface count (almost certainly yes — could invalidate existing allowlists)?
2. **Granularity of the per-agent evidence cell.** "No change" is a valid value, but should evidence be required (e.g., "no responsibility intersect with feature scope") or merely structural (cell exists)?
3. **Composition with the existing C-0445 invariant.** The invariant is grep-verifiable (zero `mcp__` in 28 agents). The matrix is human-authored. They should not duplicate effort. Possible model: invariant is the *enforcement*; matrix is the *evaluation record*.
4. **Skill-coverage check granularity.** Does every new acceptance criterion require a skill-coverage check, or only new *domain concepts*? Risk of false positives if too granular.
5. **Should `auditing-skills` get an `agent-skills-array` reverse-check?** When a new skill is authored, audit could check whether existing agents' `skills:` arrays should include it. Parallel to B5 for the skills dimension.
6. **Backfill for existing features.** Should ratified feature-pipeline runs author retroactive matrices? Probably not — but the next time any agent's surface is touched, the demand-side sweep should run against the then-current inventory.

---

## 8. Cross-references

- This feature's tactical closure: `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md`
- This feature's Blueprint OI-7 (records closure): `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md` §Open Items
- The original gap-raising question: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md` line 200
- Related analysis (different issue, same Issues/ root): `Issues/analysis-adr-placement-rootcause.md` — also a partially-applied-discipline pattern
- Existing audit machinery referenced: `.claude/skills/auditing-subagents/`, `.claude/skills/auditing-cc-configs/`, `.claude/skills/auditing-skills/`
- KB referenced: `.claude/skills/KB-cc-design/references/principles.md` (Principle 9)

---

## 9. Recommended follow-up actions (for the human)

1. Decide whether to open meta-feature `agent-roster-design-discipline-r1` now, on a later date, or not at all.
2. Decide which of B1–B5 are in scope for that meta-feature.
3. If meta-feature is opened: reference this document as part of its Intent Clarification (`derived_from` field).
4. Independent of the meta-feature: consider committing this document and the prior `Issues/analysis-adr-placement-rootcause.md` so the pattern of partially-applied-discipline gaps becomes legible in repo history.

---

*End of analysis. Report-only. No artifacts changed by this document.*
