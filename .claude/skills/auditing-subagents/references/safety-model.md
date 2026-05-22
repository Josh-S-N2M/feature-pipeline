# Safety Model

## Contents

- The threat model for subagents
- Tool scope discipline
- Permission mode discipline
- Cross-subagent isolation
- Memory-write hazards
- What good safety looks like
- What bad safety looks like

## Threat model

A subagent runs with delegated authority — when Claude routes a task to it, the subagent acts on behalf of Claude with access to the tools and permissions in its `tools:` field. Bad subagents can:

```audit-example -- subagent safety-model reference with bypass-approval anti-patterns demonstrating scanner-flagged content; documents what the auditor scanner detects
- Exfiltrate credentials via env-var reads + WebFetch
- Establish persistence by editing shell startup files
- Modify other subagents (cross-subagent attack)
- Write malicious content to CLAUDE.md (memory poisoning)
- Use bypassPermissions to skip approval prompts
```

The auditor checks for each of these classes.

## Tool scope discipline

A subagent should declare only the tools it actually needs. Over-broad tool scoping is the leading subagent security issue.

| Pattern | Severity |
|---|---|
| `tools: Bash` (no scoping) | MAJOR — full shell access |
| `tools: Bash(*)` (wildcard) | MAJOR — explicit wildcard, same effect |
| `tools: Bash(git diff *)` | OK — scoped to specific command |
| `tools:` missing from a subagent that calls shell commands in body | MAJOR — subagent inherits parent's broad tools |
| Includes `Write` or `Edit` for a read-only subagent | MAJOR — exceeds need |
| Includes `WebFetch` for a subagent with no body justification | MAJOR — outbound traffic risk |
| Includes `WebSearch` with no body justification | MAJOR — same |

The verification step matters here: a subagent declaring broad `WebFetch` may be legitimate if its body clearly says it browses external docs. The auditor reads the body before promoting these to MAJOR in the report.

## Permission mode discipline

`permissionMode: bypassPermissions` is dangerous — it skips all permission prompts and lets the subagent perform any operation in `tools:` without user confirmation.

| Use case | OK? |
|---|---|
| Read-only subagent (`tools` is all Read/Grep/Glob) | OK — nothing dangerous to prompt for |
| Subagent with Edit/Write inside the project | MAJOR — user should see prompts |
| Subagent with Bash | MAJOR — shell access without prompts is dangerous |
| Subagent with WebFetch | MAJOR — outbound network without prompts |

A managed environment may disable `bypassPermissions` entirely via `disableBypassPermissionsMode: "disable"`. In that case the setting is silently ignored. The auditor notes both the declaration and the managed override (cross-file check X2).

## Cross-subagent isolation

Subagents should not modify other subagents. If a subagent's body contains instructions to read/write other subagent files:

- `Read` access to other agents — usually fine (the subagent may be a meta-orchestrator)
- `Write` access to other agents — almost never legitimate. BLOCKER.

The auditor scans the body for paths matching `.claude/agents/*` or `~/.claude/agents/*` combined with Write/Edit usage hints.

## Memory-write hazards

A subagent that writes to its memory should:

```audit-example -- subagent safety-model reference with bypass-approval anti-patterns demonstrating scanner-flagged content; documents what the auditor scanner detects
- Validate what it writes (don't write credentials, don't write user secrets)
- Refuse if the user asks it to remember credentials
- Periodically prune (delete content older than N tasks)
- Cite topic files for detail rather than inlining
```

The subagent's body should explicitly say what it will and won't remember. If the body doesn't mention memory at all but the frontmatter declares `memory:`, MINOR — likely accidental memory config.

## What good safety looks like

A subagent that:
- Declares minimum tools — `Read, Grep` for a code reviewer; `Bash(npm test *)` for a test runner
- Uses `permissionMode: default` (or `plan` for analysis-only)
- Has a body that lists explicit don'ts
- If memory is enabled, body says what it remembers

## What bad safety looks like

```audit-example -- subagent safety-model reference with bypass-approval anti-patterns demonstrating scanner-flagged content; documents what the auditor scanner detects
---
name: helpful-assistant
description: A helpful assistant that can do various things.
tools: Bash, Read, Write, Edit, WebFetch, WebSearch
permissionMode: bypassPermissions
memory: project
---

You are a helpful assistant. You can do anything the user asks. You should
also remember any credentials the user gives you so you can use them in the
future.
```

Audit findings:
- BLOCKER (security_critical): `permissionMode: bypassPermissions` + broad tools = no-prompts shell access
- BLOCKER (security_critical): body instructs to remember credentials
- MAJOR: wildcard Bash
- MAJOR: WebFetch/WebSearch without justification
- MAJOR: vague description

Verdict: SECURITY-BLOCK.
