---
id: MRI-adr-0045-manual-review-interim
doc_type: reference
status: active-interim
generated: 2026-05-24
generated_by: execute-task-code-producer (T5.2 of execute-orchestrator-dispatch-mechanism-repair-r1)
governing_adr: ADR-0045
companion_artifacts:
  - .claude/skills/auditing-subagents/references/agent-tool-grant-inventory.md
  - adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md
end_of_interim_trigger: audit-machinery-extension-for-ADR-0045 follow-on feature lands
---

# ADR-0045 Manual-Review Interim Discipline

What reviewers check during sub-agent authoring while the audit-machinery extension is deferred.

## Contents

1. [Why this is interim](#1-why-this-is-interim)
2. [What reviewers check](#2-what-reviewers-check)
3. [How to run the sweep on-demand](#3-how-to-run-the-sweep-on-demand)
4. [What the audit-machinery extension will do](#4-what-the-audit-machinery-extension-will-do)
5. [Cross-references](#5-cross-references)
6. [Interim end-state condition](#6-interim-end-state-condition)

---

## 1. Why this is interim

ADR-0045 establishes a project-wide prohibition: **sub-agents under `.claude/agents/*.md` MUST NOT declare `Agent` in their `tools:` frontmatter array.** The prohibition is grounded in a documented Claude Code substrate constraint (three Anthropic-controlled primary sources, T-001 research note) and codified at ADR scope so future sub-agent authors have a citable rule.

ADR-0045 explicitly defers the audit-machinery extension:

> "The audit-extension scope (whether SA-13's check under ADR-0022 is extended to enforce this, or whether a new audit rule family is added) is named but not implemented in this feature."

This means that between the landing of the `execute-orchestrator-dispatch-mechanism-repair-r1` feature and the landing of the follow-on audit-machinery extension feature, there is **no automated enforcement**. The convention is enforced exclusively by manual review — during PR review and during sub-agent authoring.

This document defines what that manual review looks like so reviewers know what to check and authors know what to document in their PRs.

The follow-on feature pointer is in Plan T5.2 of `execute-orchestrator-dispatch-mechanism-repair-r1`. When that feature lands, this document's `status:` transitions to `archived` (or the file is deleted; see §6).

---

## 2. What reviewers check

### PR adds a new file under `.claude/agents/`

1. Open the new file and locate the `tools:` line in the frontmatter.
2. Check whether the literal token `Agent` appears as an entry in that array.
   - A value like `Agent` or `"Agent"` in the array is a violation.
   - A value like `Bash(python3:*)` or `TaskUpdate` is NOT a violation.
   - The check is **case-sensitive**: `Agent` (capital A) is the prohibited token.
3. If `Agent` is present in the `tools:` array, flag the PR for revision citing ADR-0045. The comment text should be: "This sub-agent's `tools:` array declares `Agent`, which is a documented runtime no-op per ADR-0045. Remove `Agent` from the `tools:` array before merging."

### PR modifies an existing `.claude/agents/*.md`

Apply the check to the diff:

1. Review the diff for any lines that touch the `tools:` frontmatter key.
2. If the diff **adds** `Agent` to a `tools:` array (i.e., the `+` line contains `Agent`), **block the PR** citing ADR-0045.
3. If the diff removes `Agent` from a `tools:` array, no action needed — this is a compliant cleanup.
4. If the `tools:` line is unchanged or the diff does not touch `tools:`, no action needed for this check.

### PR modifies `.claude/skills/recipe-feature-pipeline/SKILL.md` Execution Phase Dispatch section

The Execution Phase Dispatch section documents the orchestrator dispatch contracts. Verify:

1. Contract 5 (sub-agent tool-grant prohibition) still cites ADR-0045.
2. Contract 6 (dispatch mechanism) still cites ADR-0044.

If either citation is missing or dropped from the diff, flag for restoration before merging.

### When authoring a new sub-agent yourself

Before opening a PR, copy the following block into the PR description under an "ADR-0045 compliance" section:

```
## ADR-0045 compliance

- [ ] Verified: the new sub-agent's `tools:` array does NOT include `Agent`.
- [ ] If the agent requires dispatch capability, confirm the dispatch happens
      at the main-conversation level (parent skill or main orchestrator) and the
      agent emits a `dispatch_directives[]`-style structured hand-off per ADR-0044.
- [ ] If `Agent` was removed from an existing `tools:` array in this PR,
      confirm the agent still functions correctly with the revised tools list.
```

---

## 3. How to run the sweep on-demand

Any reviewer wanting to verify the current state of the entire sub-agent directory can run:

```bash
grep -E '^tools:.*Agent' .claude/agents/*.md | grep -v 'Bash('
```

**Expected result: zero matches.**

If the command returns any lines, those files contain `Agent` in a `tools:` frontmatter declaration (filtered to exclude `Bash(...)` patterns which incidentally contain the substring). Each match is a violation requiring correction per ADR-0045. The `agent-tool-grant-inventory.md` sibling artifact should be updated to record the violation and its disposition.

For strict word-boundary matching (reduces false positives if future tool-grant names happen to contain the substring "Agent"):

```bash
grep -E '^tools:.*\bAgent\b' .claude/agents/*.md
```

Both commands work from the repository root. The sweep methodology is documented in detail in §4 of `agent-tool-grant-inventory.md` — do not duplicate it here.

---

## 4. What the audit-machinery extension will do

This section is informational. It describes the scope of the follow-on feature so its author has a stated starting point and so reviewers understand what the interim is standing in for.

When the audit-machinery extension for ADR-0045 is authored, it is expected to:

- **Integrate with the `auditing-subagents` skill family.** The recommended integration point is SA-13 (the sub-agent reasoning-configuration audit under ADR-0022), extended with a new check for `Agent` in `tools:` arrays. If SA-13's scope is judged orthogonal, the alternative is a new audit rule family `auditing-cc-tool-grants`.

- **Add a PR-level hook or CI check** that runs the sweep command (§3) automatically on every PR that touches `.claude/agents/*.md`. The check produces a BLOCKER finding per match.

- **Block PRs that introduce `Agent` in a sub-agent's `tools:` array.** The BLOCKER finding prevents merge until the violation is resolved, replacing the manual reviewer responsibility described in §2.

- **Update the `agent-tool-grant-inventory.md` artifact on every change.** When a violation is caught and corrected, the inventory table in §3 of that artifact is updated with the agent file, pre-cleanup tools, post-cleanup tools, and cleanup commit. This keeps the historical record current without requiring manual inventory maintenance.

Once the audit-machinery extension is in place, §2 of this document becomes redundant — the automated check enforces what reviewers currently enforce by hand.

---

## 5. Cross-references

| Artifact | Role |
|---|---|
| `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` | Governing ADR — establishes the prohibition, defers audit-extension. |
| `adrs/ADR-0044-flatten-execution-phase-dispatch-hierarchy.md` | Companion ADR — cleans up the two pre-existing violations; establishes `dispatch_directives[]` hand-off pattern. |
| `.claude/skills/auditing-subagents/references/agent-tool-grant-inventory.md` | Sibling artifact (T5.1) — canonical inventory of all affected sub-agents, sweep methodology, and sweep verification. Do NOT duplicate that content here. |
| `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md` | T-001 research note — three Anthropic primary sources that establish the substrate constraint. |

The three Anthropic primary sources (summarized from T-001):

1. **https://code.claude.com/docs/en/sub-agents** — "Subagents cannot spawn other subagents."
2. **https://code.claude.com/docs/en/agent-sdk/subagents** — "Subagents cannot spawn their own subagents. Don't include Agent in a subagent's tools array."
3. **https://github.com/anthropics/claude-code/issues/29677** — corroborates the v2.1.63 Task → Agent rename date.

Source 2 is the direct developer instruction that ADR-0045 codifies as a project-level rule.

---

## 6. Interim end-state condition

This document's `status: active-interim` reflects that it exists to fill a gap — the period between ADR-0045 landing and the audit-machinery extension landing.

When the follow-on audit-machinery extension feature lands:

- This file's `status:` SHOULD be flipped from `active-interim` to `archived`, OR the file SHOULD be deleted. The follow-on feature author decides which is cleaner given the state of the `auditing-subagents` skill family at that time.
- If archived: add a `superseded_by:` frontmatter field pointing to the new automated check artifact.
- If deleted: ensure the deletion commit message references ADR-0045 and cites the follow-on feature name so the history is traceable.

Either way, the `agent-tool-grant-inventory.md` sibling artifact and ADR-0045 itself remain as permanent records — they do not expire when the interim ends.
