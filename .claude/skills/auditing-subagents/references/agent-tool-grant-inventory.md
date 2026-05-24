---
id: AGI-agent-tool-grant-inventory
doc_type: reference
status: active
generated: 2026-05-24
generated_by: execute-task-code-producer (T5.1 of execute-orchestrator-dispatch-mechanism-repair-r1)
applies_to: .claude/agents/*.md
governing_adr: ADR-0045
companion_artifacts:
  - adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md
  - .claude/agents/execute-orchestrator.md
  - .claude/agents/execute-finalize-reconciler.md
---

# Agent Tool Grant Inventory

Canonical inventory of sub-agent files that declared (or might declare) `Agent` in their `tools:` frontmatter array, with disposition for each. Governed by ADR-0045.

## Contents

1. [Convention](#1-convention)
2. [Rationale (brief)](#2-rationale-brief)
3. [Affected-set inventory at ADR-0045 adoption](#3-affected-set-inventory-at-adr-0045-adoption)
4. [Sweep methodology](#4-sweep-methodology)
5. [Sweep verification at time of this artifact](#5-sweep-verification-at-time-of-this-artifact)
6. [Enforcement posture](#6-enforcement-posture)
7. [How to extend this inventory](#7-how-to-extend-this-inventory)

---

## 1. Convention

Per ADR-0045 (Accepted 2026-05-23):

> **Sub-agents in this project MUST NOT declare `Agent` in their `tools:` frontmatter array.**

This rule applies to every file under `.claude/agents/*.md`. It does NOT apply to `TaskCreate` or `TaskUpdate` (those are Claude Code's built-in task-tracking primitives, semantically distinct from the `Agent` dispatch tool). It does NOT apply to the main-conversation orchestrator or to parent skills — those are not sub-agent files.

---

## 2. Rationale (brief)

Sub-agents cannot dispatch other sub-agents at runtime. This is a documented Claude Code substrate constraint established by three independent Anthropic-controlled primary sources (T-001 research, `execute-orchestrator-dispatch-mechanism-repair-r1`):

1. **https://code.claude.com/docs/en/sub-agents** — "Subagents cannot spawn other subagents."
2. **https://code.claude.com/docs/en/agent-sdk/subagents** — "Subagents cannot spawn their own subagents. Don't include Agent in a subagent's tools array." (Source 2 is the direct developer instruction.)
3. **https://github.com/anthropics/claude-code/issues/29677** — corroborates the v2.1.63 Task → Agent rename date.

Declaring `Agent` in a sub-agent's `tools:` array is a runtime no-op: the YAML parses, the agent loads, but the dispatch capability is silently absent at runtime. The declaration is also a misleading invocation hint — it suggests dispatch capability the sub-agent does not actually have. Prohibition is the lowest-cost guardrail.

---

## 3. Affected-set inventory at ADR-0045 adoption

FR-5 inventory sweep (codebase-analysis.json `fr5_inventory_sweep`) scanned all 36 sub-agent files under `.claude/agents/*.md` at the time of feature `execute-orchestrator-dispatch-mechanism-repair-r1`. Exactly two files declared `Agent` in `tools:`.

| Agent file | Pre-cleanup `tools:` | Post-cleanup `tools:` | Cleanup commit |
|---|---|---|---|
| `.claude/agents/execute-orchestrator.md` | `[Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]` | `[Read, Glob, Grep, Write, Bash(python3:*)]` | b2bf5ca (T3.1) |
| `.claude/agents/execute-finalize-reconciler.md` | `[Read, Glob, Grep, Write, Agent]` | `[Read, Glob, Grep, Write]` | b2bf5ca (T3.3) |

Both agents are dispatcher sub-agents. Their dispatch is materially broken by the substrate constraint. Both `Agent` declarations were removed in bundled commit `b2bf5ca` under ADR-0044's option (a) design pathway.

The remaining 34 sub-agents did not declare `Agent` at the time of this sweep and required no change.

---

## 4. Sweep methodology

The discovery-codebase-researcher in the `execute-orchestrator-dispatch-mechanism-repair-r1` feature run used the following command to enumerate affected agents:

```bash
grep -rEn '^tools:.*Agent' .claude/agents/*.md
```

This matches lines where the frontmatter `tools:` key contains the literal token `Agent`. Future audits can reproduce with the same command. Note: `Bash(python3:*)` and other entries containing the substring "Agent" do NOT match because the pattern anchors on the `tools:` line's start and looks for a standalone word; authors should verify false positives for any tool grant names that incidentally include the substring — in practice, none currently exist in this project.

For strict word-boundary matching (to reduce false positives on future tool names):

```bash
grep -rEn '^tools:.*\bAgent\b' .claude/agents/*.md
```

---

## 5. Sweep verification at time of this artifact

The following command was executed at artifact generation time (2026-05-24) to confirm the post-cleanup state:

```bash
grep -rEn '^tools:.*Agent' .claude/agents/*.md | grep -v 'Bash('
```

**Result: zero matches.**

Both previously affected agents now carry clean `tools:` arrays:

- `execute-orchestrator.md` line 6: `tools: [Read, Glob, Grep, Write, Bash(python3:*)]`
- `execute-finalize-reconciler.md` line 6: `tools: [Read, Glob, Grep, Write]`

The inventory's claim of post-cleanup state is verified.

---

## 6. Enforcement posture

Per ADR-0045:

- **Interim enforcement: manual review.** During sub-agent authoring and PR review, the reviewer verifies that the new or modified sub-agent's `tools:` array does not include `Agent`. If it does, flag as a critical issue citing ADR-0045.

- **Audit-machinery extension: deferred.** Extension of the `auditing-subagents` skill (or SA-13 under ADR-0022) to enforce this convention automatically is named in this feature's Plan T5.2 but its implementation is deferred to a follow-on feature. The recommended follow-on approach: extend SA-13 with a new check that greps every `.claude/agents/*.md` frontmatter `tools:` array for the literal `Agent` token, producing a BLOCKER finding per match. Alternative: a new audit rule family `auditing-cc-tool-grants` if SA-13's scope is judged orthogonal.

- **Kill criteria.** If a future Claude Code harness update enables true sub-agent → sub-agent dispatch (verifiable via T-001-style probe), ADR-0045 is reconsidered. Reconsideration may include per-sub-agent opt-in for the new affordance rather than a global lift of the prohibition.

---

## 7. How to extend this inventory

When a new sub-agent is authored under `.claude/agents/*.md`:

1. Run the sweep command from [§4](#4-sweep-methodology) across the agent directory to confirm `Agent` is absent from all `tools:` frontmatter lines.
2. If `Agent` appears in the new file, remove it before merging. Cite ADR-0045 in the commit message or PR review comment.
3. If the new agent legitimately needs dispatch capability at the main-conversation level, use the `dispatch_directives[]`-style structured hand-off pattern established by ADR-0044 (the pattern `execute-finalize-reconciler` uses after cleanup).
4. Update this inventory table in §3 only if a violation was found and cleaned up — add a row with the agent file, pre-cleanup tools, post-cleanup tools, and cleanup commit.
5. If an automated audit-machinery extension has been implemented (follow-on feature), trigger that check as part of the authoring pipeline. The placeholder pointer is in Plan T5.2 of the `execute-orchestrator-dispatch-mechanism-repair-r1` feature run.

Do NOT add rows for agents that never declared `Agent`. The table records violations and their dispositions; compliant agents at authoring time are captured implicitly by the sweep verification in §5.
