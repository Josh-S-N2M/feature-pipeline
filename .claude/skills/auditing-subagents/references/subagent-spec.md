# Subagent Specification

## Contents

- Frontmatter schema
- tools field
- model aliases
- memory scopes
- skills field
- effort field
- permissionMode
- File locations and precedence

## Source

`code.claude.com/docs/en/sub-agents`, last verified 2026-05.

## Frontmatter schema

Subagent files at `.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md` (user). Frontmatter is YAML; body is the system prompt.

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
---
name: code-reviewer
description: Reviews pull-request diffs for code quality, style, and obvious bugs.
tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *)
model: sonnet
memory: project
permissionMode: default
---

You are a senior code reviewer...
```

Required:
- `name` — kebab-case identifier
- `description` — used for delegation routing; rules below

Optional:
- `tools` — comma-separated tool list (NOT `allowed-tools:` — that's the skills field)
- `model` — alias (`sonnet`, `opus`, `haiku`, `inherit`) or full model ID
- `effort` — reasoning depth: `low` | `medium` | `high` | `xhigh` | `max` (see `effort field` below)
- `memory` — `project` | `local` | `user`
- `permissionMode` — `default` | `acceptEdits` | `bypassPermissions` | `plan`
- `skills` — list of skill names to preload (cost considerations apply)
- `disallowedTools` — tools the subagent must NOT have, even if the parent has them

## tools field

The `tools:` field is the canonical subagent tool list. **It is not `allowed-tools:` like skills.** Field-name confusion is the most common subagent authoring bug:

| Field | Used by |
|---|---|
| `allowed-tools` | Skills |
| `tools` | Subagents |

If a subagent file has `allowed-tools:` instead of `tools:`, the tool list is silently ignored and the subagent inherits the parent's full tool set. BLOCKER.

Syntax for the value:
- Comma-separated list, or YAML list
- Tool names may include argument-scoping in parens: `Bash(git diff *)`, `WebFetch(github.com)`
- Wildcard `Bash(*)` is allowed but signals over-broad permission — MINOR

## model field

Accepts:

| Alias | Resolves to | Notes |
|---|---|---|
| `sonnet` | Latest Sonnet | Default for most subagents |
| `opus` | Latest Opus | For complex reasoning |
| `haiku` | Latest Haiku | Fast, cheap |
| `inherit` | Parent's model | Use when no specific model needed |

A full model ID (e.g., `claude-sonnet-4-5`) also works. Anything else is silently treated as `inherit`. MAJOR if value isn't recognized.

## memory field

Optional. Declares whether and where the subagent's persistent memory lives.

| Value | Path |
|---|---|
| (absent) | No memory; subagent has no persistent state |
| `project` | `.claude/agent-memory/<name>/` |
| `local` | `.claude/agent-memory-local/<name>/` (must be in .gitignore) |
| `user` | `~/.claude/agent-memory/<name>/` |

The subagent reads up to 200 lines / 25 KB from `MEMORY.md` in its directory at each spawn, and may write to it during execution if it has `Write` or `Edit` in `tools:`.

A subagent declaring `memory:` but having `disallowedTools:` that includes `Write` or `Edit` cannot write to its memory — it will only ever read. BLOCKER (cross-file check X20).

## skills field

Optional list of skill names to preload into the subagent's context at spawn:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
---
name: data-analyst
skills:
  - pandas-recipes
  - matplotlib-quick-reference
---
```

Each skill's full SKILL.md content loads into the subagent's context. This has real token cost — a subagent listing many large skills can blow its context budget at spawn time.

Audit rules:
- Each skill must actually exist in a discoverable location → otherwise BLOCKER (**SA-13**, implemented by `scripts/validate_subagent_frontmatter.py`). X9 escalation applies if the skill is found but has SECURITY-BLOCK verdict.
- Total preloaded skill body should be under ~5,000 tokens combined → MAJOR if total exceeds
- Skills with `disable-model-invocation: true` cannot be preloaded into subagents → BLOCKER (these are silently dropped)
- Do NOT use the `skills:` array to express reasoning depth. The `skills:` array preloads SKILL.md *content* (domain knowledge, protocols, rubrics). Reasoning depth is controlled by `model:` (sonnet/opus/haiku) and/or `effort:` (low/medium/high/xhigh/max — see `effort field` below). Patterns like `skills: [deep-reasoning, …]` are a category error — see SA-13.

## effort field

Optional. Controls how eagerly the model spends thinking tokens, independently of the chosen model.

| Value | Documented as |
|---|---|
| `low` | Minimal thinking, fastest responses |
| `medium` | Moderate thinking |
| `high` | Deep reasoning |
| `xhigh` | Extended reasoning (Opus 4.7 only; falls back to `high` on other models) |
| `max` | Maximum effort |

Source: Claude Code Agent SDK reference (`EffortLevel` literal). When unset, the subagent inherits the parent's effort. Authors should pick `effort:` intentionally when the subagent's reasoning load warrants it even on a sonnet-class model, or when a default-opus subagent should economize. Combining `model:` and `effort:` choices is the documented mechanism for tuning reasoning depth — not the `skills:` array.

## permissionMode

| Value | Behavior |
|---|---|
| `default` | Standard permission prompts |
| `acceptEdits` | Auto-approves edit operations |
| `bypassPermissions` | No permission prompts (dangerous) |
| `plan` | Read-only; reports a plan rather than executing |

In a managed environment with `disableBypassPermissionsMode: "disable"`, a subagent declaring `permissionMode: bypassPermissions` is silently downgraded to default. The audit notes this (cross-file check X2).

## File locations and precedence

Order of precedence (highest first):

1. Managed-settings subagent declarations
2. CLI flag `--agent <name>`
3. `.claude/agents/<name>.md` (project)
4. `~/.claude/agents/<name>.md` (user)
5. Plugin-shipped subagents

When two scopes define the same `<name>`, the higher-precedence wins; the lower-scope file is **dead** — emit MINOR per cross-file check X18.

## Diagnostic command

```
/agents
```

Shows which subagents are active after precedence resolution. Reveals shadowed definitions, missing files, and broken frontmatter.
