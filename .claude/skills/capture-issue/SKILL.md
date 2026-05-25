---
name: capture-issue
description: "Slash-command entry point for outside-pipeline issue capture. Parses `/capture-issue <hint>` (create-mode) or `/capture-issue --update <path>` (update-mode); spawns the issue-capture-author sub-agent via Task. Mutually exclusive create-mode positional hint XOR update-mode `--update <path>`."
disable-model-invocation: true
allowed-tools: Task, AskUserQuestion
argument-hint: <hint> | --update <path>
---

# capture-issue — Slash-Command Entry Point for Outside-Pipeline Issue Capture

When invoked via `/capture-issue`, this skill parses the user's arguments and spawns the `issue-capture-author` sub-agent to perform the actual triage + draft + approval-prompt + write workflow.

This skill is **invoked only via slash command** (per F-001; `disable-model-invocation: true`). Main Claude does NOT auto-invoke on description-match.

## Argument parsing

The `argument-hint` field declares two mutually exclusive forms:
- **Create-mode** (positional): `/capture-issue <topic-hint>` — e.g., `/capture-issue noticing pipeline gate-7 lacks rollback-on-failure`
- **Update-mode**: `/capture-issue --update <path-to-existing-issue>` — e.g., `/capture-issue --update Issues/per-agent-design-evaluation-gap/analysis.md`

These two forms are **mutually exclusive** per AC-FR-2-c. Mixing them (e.g., `/capture-issue --update some-path some-hint`) → invalid; use AskUserQuestion to clarify.

## Workflow

1. **Parse `$ARGUMENTS`**:
   - If `$ARGUMENTS` starts with `--update ` → update-mode; path is the rest of the argument.
   - Else → create-mode; the entire `$ARGUMENTS` string is the topic-hint.
   - Empty `$ARGUMENTS` → invalid; AskUserQuestion for clarification.

2. **Validate mutual exclusivity**:
   - If `--update` appears AND there's additional positional content (other than the path itself), → invalid; AskUserQuestion for clarification.

3. **Spawn the sub-agent via Task** (AC-FR-1-a):
   - Create-mode: `Task(subagent_type="issue-capture-author", prompt="create-mode: <topic-hint>")`
   - Update-mode: `Task(subagent_type="issue-capture-author", prompt="update-mode: <path>")`
   - The sub-agent does the triage + draft + AskUserQuestion + Write workflow.

4. **Report back** the sub-agent's result to the user (which path was written, or "no change" for idempotent updates, or "cancelled" for cancelled approvals).

## Cross-references

- Sub-agent: `.claude/agents/issue-capture-author.md` (T4.4a/b/c)
- Discipline KB: `.claude/skills/KB-issue-capture/SKILL.md` (T4.1)
- ADR-0044 per-issue folder model: `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md`
- ADR-0047 (4-option AskUserQuestion archetype for create-mode): `.../adrs/ADR-0047-three-layer-enforcement.md` (referenced for the 4-option pattern)
