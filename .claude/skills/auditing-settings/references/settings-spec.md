# Settings Specification

## Contents

- File locations and precedence
- Top-level schema
- Override vs additive behavior
- env block
- Output styles
- Diagnostic commands

## Source

`code.claude.com/docs/en/settings`, last verified 2026-05.

## File locations and precedence

Settings load with **override** semantics — higher-precedence scopes override lower:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
Scope     Path                                                                 Committed?  Notes
Managed   /etc/claude/managed-settings.json (Linux)                            n/a         Highest precedence
          /Library/Application Support/Claude/managed-settings.json (macOS)
Local     .claude/settings.local.json (in project root)                        No — must   Per-developer
                                                                               be gitignored
Project   .claude/settings.json (in project root)                              Yes         Team-shared
User      ~/.claude/settings.json                                              n/a (home)  Per-user
```

When the same field appears in multiple scopes, **managed wins**, then local, then project, then user. Hooks, however, are additive (see the auditing-hooks skill).

## Top-level schema

Known top-level fields (the auditor warns on unrecognized fields):

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "model": "sonnet",
  "permissions": { ... },
  "env": { ... },
  "hooks": { ... },
  "autoMemoryDirectory": "~/.claude/memory",
  "outputStyles": [ ... ],
  "disableBypassPermissionsMode": "disable",
  "disableAllPlugins": false,
  "alwaysThinkingEnabled": false,
  "spinnerTipsEnabled": true,
  "claudeMd": "...",
  "subagents": { ... },
  "maxOutputTokens": 8192,
  "verbose": false
}
```

| Field | Type | Scope rules |
|---|---|---|
| `model` | string | Any scope |
| `permissions` | object | Any scope (see permission-rules-spec.md) |
| `env` | object | Any scope; managed should lock secrets |
| `hooks` | object | Any scope; additive (not override) |
| `autoMemoryDirectory` | string | **User scope only** — silently ignored elsewhere |
| `outputStyles` | array | Any scope |
| `disableBypassPermissionsMode` | string | **Managed scope only** |
| `disableAllPlugins` | boolean | **Managed scope only** |
| `claudeMd` | string | **Managed scope only** |

### Scope-mismatch errors

Some fields only take effect at specific scopes; placing them elsewhere is silent failure:

- `autoMemoryDirectory` at project scope → ignored → MAJOR (cross-file check X22)
- `disableBypassPermissionsMode` at user scope → ignored → MAJOR
- `claudeMd` at project scope → ignored → MAJOR

## Override vs additive behavior

The most common settings.json bug is assuming additive behavior. Symptoms:

- "I set `model: opus` in project settings but it's running Sonnet" — managed scope is overriding with `sonnet`.
- "My `env` variable is missing" — overridden by a higher scope.
- "Why doesn't my permission rule fire?" — see permission-rules-spec.md (deny > ask > allow, and managed deny wins).

Audit informational note: when a field appears in multiple scopes that the auditor can see, emit INFO "field is set at multiple scopes; higher scope wins."

## env block

The `env` block injects environment variables for Claude Code's subprocess calls (hooks, MCP servers, tool calls).

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}",
    "NODE_ENV": "development",
    "DEBUG": "claude:*"
  }
}
```

Security rules:
- A literal credential value in `env` (e.g. `"GITHUB_TOKEN": "ghp_xxx..."`) is BLOCKER + security_critical.
- Reference syntax `${VAR}` reads from the user's shell env — fine.
- A `${HOME}/${SECRET}` pattern is fine; `$(curl ...)` is **not** a valid shell substitution here and won't expand — MINOR.

## Output styles

The `outputStyles` array lists output-style files Claude can apply:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "outputStyles": [
    "concise",
    "verbose-debugging",
    "/abs/path/to/custom.md"
  ]
}
```

Each entry is the name of a file under `.claude/output-styles/<name>.md` or an absolute path. The files themselves have frontmatter like:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
---
name: concise
description: Short responses, no preamble, no postamble.
---

Respond in the most concise way possible. Skip preamble like "Sure!" or
"Here you go." Skip postamble like "Let me know if you need anything else."
```

Audit checks for output-style files:
- Frontmatter must have `name` and `description`.
- Body must be non-empty.
- Body should not contain instructions that would override Claude's safety rules (BLOCKER).

## Diagnostic commands

```
/settings
```

Shows the effective settings after scope merging.

```
/doctor
```

Reports parse errors, missing files, and field mismatches across scopes.
