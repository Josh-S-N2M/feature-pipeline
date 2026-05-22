# Common Failures

Cross-cutting silent-failure modes the auditor needs to recognize. These don't fit cleanly into one primitive's dimension list because they span multiple primitives or appear consistently across the codebase. Read this when a symptom doesn't seem to match any single audit dimension.

## Contents

- The three memory concepts (most-confused mental model)
- The "fields silently ignored" catalog
- Loading and lifecycle traps
- Discovery and triggering failures
- Security failure classes
- File hygiene failures

## The three memory concepts

Claude Code uses the word "memory" for **three different mechanisms**. The auditor must keep them separate or it will produce nonsense findings.

```audit-example -- common-failures catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
# 1: User-written project rules (audited by auditing-context-files)
   Files: CLAUDE.md, .claude/CLAUDE.md, .claude/rules/*.md, ~/.claude/CLAUDE.md
   Loaded into context: Yes, every session, full content

# 2: Auto memory written by Claude (audited by auditing-context-files)
   Files: ~/.claude/projects/<project-id>/memory/
   Loaded into context: Yes, but only first 200 lines / 25KB of MEMORY.md

# 3: Subagent persistent memory written by the subagent (audited by auditing-subagents)
   Files: .claude/agent-memory/<name>/, .claude/agent-memory-local/<name>/,
          ~/.claude/agent-memory/<name>/
   Loaded into context: Yes per spawn, first 200 lines or 25KB
```

Common confusions:

- **"My memory isn't working"** — Which one? Auto memory and subagent memory are different files in different places with different writers.
- **"I edited MEMORY.md and Claude still got it wrong"** — Auto memory MEMORY.md and subagent MEMORY.md live in different directories with different writers. Editing one doesn't affect the other.
- **"I want to share memory across machines"** — Auto memory is per-machine; only project context files are committed.
- **"Subagent memory is in .gitignore but Claude still tracks it"** — Probably the wrong path is in .gitignore. `agent-memory/` is intended to be committed; `agent-memory-local/` is the one that should be gitignored.

## The "silently ignored" catalog

These fields are *parsed* but have **no effect** at the scope they're set in. The user sees no error; the setting just doesn't apply.

| Field | Where it works | Where it's silently ignored |
|---|---|---|
| `autoMemoryDirectory` | `~/.claude/settings.json` (user only) | Project, local |
| `allowManagedPermissionRulesOnly` | managed-settings.json only | All other scopes |
| `allowManagedHooksOnly` | managed-settings.json only | All other scopes |
| `skipDangerousModePermissionPrompt` | User, managed | **Silently ignored in project settings** (security feature — prevents untrusted repos from auto-bypassing) |
| `disableBypassPermissionsMode: "disable"` | Any scope, but loses effect if a higher-precedence scope re-enables it | (most useful in managed) |
| `claudeMd` (managed-only injection) | managed-settings.json | All other scopes |
| `appendSystemPrompt` (managed-only injection) | managed-settings.json | All other scopes |

The auditor flags these with MAJOR or MINOR depending on impact. See `cross-file-checks.md` for X22.

## Loading and lifecycle traps

### Configuration changes don't take effect until session restart

Settings.json edits, new skills, new subagents, new hooks — all read at session start. The user must exit and re-enter Claude Code to see changes. Surface this in the "Next actions" section of any report whose fixes involve config file edits.

### Hooks don't fire when max_turns is hit

Per docs: "Hooks may not fire when the agent hits the max_turns limit because the session ends before hooks can execute." Cleanup hooks that assume Stop will fire are fragile. Flag MINOR with note.

### PermissionRequest hooks don't fire in non-interactive mode

`PermissionRequest` hooks (v2.0.45+) are interactive-only. If a project uses headless mode (`claude -p`), PermissionRequest hooks are dead. Flag MINOR with note.

### CLAUDE.md doesn't auto-update from /memory if file is open elsewhere

The `/memory` command opens the file in the user's editor. If the user has it open in another editor, edits via `/memory` may conflict. Out of scope for static audit but worth surfacing in troubleshooting.

### Event names are case-sensitive

`PreToolUse` works. `preToolUse`, `pretooluse`, `pre_tool_use` do not. Silent failure — the hook just never fires. Audit BLOCKER.

### Markdown event-name typos in matchers

A matcher like `Bash|bash` is the OR pattern in regex (matches either case of "Bash"). But `bash` doesn't match the actual tool name — tools are case-sensitive. Audit MAJOR.

## Discovery and triggering failures

### Skill description is the only signal Claude uses to auto-trigger

If a skill isn't triggering when you expect it to, the description is almost always the cause. Check:

- Is the description specific enough? "A skill that helps with code" won't trigger.
- Does it lead with the trigger ("Use when...") rather than a description of capabilities?
- Is it written as "ad copy" — first sentence is the value prop?
- Is the combined description + when_to_use under the 1,536 character cap?

### Skill listing budget overflow

If the user has many skills installed, descriptions for low-priority skills get truncated. `/doctor` shows whether this is happening. Audit MAJOR when the family is installed and budget isn't raised.

### Subagent description has the same problem as skill descriptions

Subagent `description:` is used for delegation routing. "Helps with code" won't get delegated to. The same rules apply.

### disable-model-invocation: true prevents preloading into subagents

Per docs: "Also prevents the skill from being preloaded into subagents." A skill listed in a subagent's `skills:` field but with `disable-model-invocation: true` will not actually load. Audit BLOCKER on the subagent (it claims preload but won't get it).

### Skills win over commands with same name

If a slash command and a skill both share the same name (the command living under .claude/commands and the skill living under .claude/skills, both with that name), the skill is used and the command is dead. Audit MINOR.

## Security failure classes

### Hook script not on disk

settings.json references a hook script that doesn't exist. The hook just never fires. Audit BLOCKER.

### Hook script not executable

The script exists but the shell can't execute it. Same end result. Audit MAJOR.

### Hook command path uses ~ or $HOME but in project-scope settings

A hook command pointing at a user-home subdirectory works for the developer who installed Claude Code there but breaks for teammates whose home layout differs. Audit MAJOR.

### Untrusted repo SessionStart hook attack vector

A malicious project ships a settings.json (under its .claude directory) with a SessionStart hook that runs on first `cd` into the directory. CVE-2025-59536 class. Audit BLOCKER on any SessionStart hook that performs network egress or modifies files outside the project's .claude directory.

### Auto memory accumulates credentials

When the user asks Claude to "remember that we use the GitHub token", Claude may write the literal token value into MEMORY.md. The file is on disk, machine-local, and may be backed up or synced. Audit BLOCKER on credential-pattern matches in MEMORY.md.

### MCP rug-pull (runtime-only)

MCP server changes tool descriptions between sessions. Static audit cannot catch this; runtime audit (--with-runtime) detects it via SHA-256 hash comparison. Mention in report Notes if static-only.

### Pedagogical laundering

An attacker wraps real malicious content in pedagogical markers to silence the scanner. See `pedagogical-marker-spec.md` for the anti-laundering checks. Audit MAJOR with content-still-stands-as-dangerous escalation.

## File hygiene failures

### settings.local.json not gitignored

Personal preferences (different default model, personal API keys, dev-only allow rules) leak to teammates. Audit MAJOR.

### agent-memory-local not gitignored

Same problem at the subagent layer. Audit MAJOR.

### MEMORY.md committed with machine-local paths

A subagent's MEMORY.md is at `.claude/agent-memory/<name>/` (committed) and contains absolute paths like `/home/<user>/projects/...`. These are useless on other machines. Audit MAJOR.

### CLAUDE.md @-import to file outside project

`@/Users/alice/notes.md` works on Alice's machine, breaks for everyone else. Audit MAJOR.

### Orphan agent-memory directory

`.claude/agent-memory/foo/` exists but no subagent named `foo` has `memory: project` declared. The directory was created by a since-removed subagent and is now dead weight. Audit MINOR.

### Stale @-import target

CLAUDE.md `@-imports` a file that was renamed or deleted. The import fails silently (the imported content is just empty). Audit MAJOR.

## Cross-cutting symptoms and routing

If the user reports:

| Symptom | First-look reference |
|---|---|
| "Claude isn't following my CLAUDE.md instructions" | content-quality, line count, contradictions |
| "My skill isn't triggering" | description-quality, skill listing budget |
| "My hook isn't firing" | event name case, matcher syntax, script existence |
| "My subagent isn't being used" | description routing, frontmatter validity |
| "Credentials leaked" | settings.deny baseline, MEMORY.md scan, hook script egress |
| "I forgot what I told Claude to remember" | three-memory mental model (which one?) |
| "MCP tool isn't available" | scope precedence (local > project > user), .mcp.json schema |

Each of these routes the auditor toward the right primitive sub-skill.

## The single most-important diagnostic

Inside Claude Code:

```
/doctor
```

This is the meta-diagnostic. It surfaces:
- Skill listing budget overflow
- Configuration parse errors
- Loading order issues
- Deferred tool loading state

When a user reports a confusing failure, `/doctor` output is the single most useful artifact to attach to the audit. The audit report's "Next actions" section should recommend running `/doctor` after applying fixes.
