# Configuration reference

Everything that configures Claude Code's runtime behavior — `settings.json` schema, permissions, permission modes, sandboxing, and UX customization (status line, keybindings, fullscreen, voice dictation).

For directory layout and settings precedence, see `references/architecture.md`. For the extension primitives configured via these settings, see `references/extensions.md`.

## Contents

- `settings.json` overview
- Permissions
- Permission modes
- Hooks (configuration shape)
- Sandboxing
- Environment variables in settings
- Status line
- Keybindings
- Fullscreen rendering
- Voice dictation
- Settings reference

## `settings.json` overview

The same JSON schema applies at every level: `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, and `managed-settings.json`. Settings layer with the precedence rules in `references/architecture.md` — array fields merge across scopes, scalar fields take the highest-precedence value.

The most commonly used keys:

```json
{
  "model": "opus",
  "permissions": { "allow": [...], "ask": [...], "deny": [...] },
  "defaultMode": "default",
  "outputStyle": "default",
  "hooks": { "PreToolUse": [...], "PostToolUse": [...] },
  "env": { "MY_VAR": "value" },
  "statusLine": "...",
  "sandbox": { "enabled": false, ... },
  "autoMemoryEnabled": true,
  "additionalDirectories": ["/path/to/another/project"],
  "outputStyle": "teaching"
}
```

There are many more keys for telemetry, network, OAuth, IDE behavior, and feature toggles. For the complete schema with every available field, fetch `https://code.claude.com/docs/en/settings.md`.

## Permissions

Permissions control what Claude can do without asking the user. Three lists:

```audit-example -- Documents the curl-pipe-shell installer pattern the auditor flags via DE-1 scanner; reference catalog of anti-pattern signatures, not real install instructions. Documents credential-file path patterns (cloud SDK creds, SSH keys, NETRC, dotenv) the auditor flags via DE-2 scanner; reference catalog explaining what to protect, not real credentials.
{
  "permissions": {
    "allow": [
      "Bash(npm test *)",
      "Bash(npm run *)",
      "Bash(git status *)",
      "Bash(git diff *)",
      "Read",
      "Glob",
      "Grep"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl * | sh)",
      "Read(~/.aws/credentials)",
      "Read(~/.ssh/id_*)"
    ]
  }
}
```

**Match patterns:**
- Plain tool name (`Read`, `Edit`, `WebFetch`) — matches all uses of that tool
- `Bash(<pattern>)` — matches bash commands matching the pattern
- `Read(<path>)` — matches reads of paths matching the pattern
- `Edit(<path>)`, `Write(<path>)` — same idea for edits and writes
- `mcp__<server>__<tool>` — matches a specific MCP tool
- `mcp__<server>` — matches all tools from a server

**Wildcards.** `*` matches any sequence of characters within a single argument. `Bash(npm test *)` matches `npm test`, `npm test --watch`, `npm test src/foo.test.ts`, etc.

**Precedence between lists.** Deny wins over ask wins over allow. A deny rule blocks even if allow matches the same pattern.

**Lists merge across scopes.** `permissions.allow` from user, project, and local settings all combine. This means project settings cannot remove allows that user settings granted — only deny rules can block them.

**`additionalDirectories`** lets Claude access files outside the project root. Configuration files are not discovered from these directories — they exist purely as filesystem access grants.

For the complete pattern syntax and examples: `https://code.claude.com/docs/en/permissions.md`.

## Permission modes

Permission modes set the default behavior when a tool call would otherwise prompt. Set via `defaultMode` in settings, or per-session with `--permission-mode <mode>`.

| Mode | Behavior | When to use |
|---|---|---|
| `default` | Standard prompts; user approves each unallowed action | Interactive, supervised work |
| `acceptEdits` | Auto-approves file creation and editing, plus common filesystem bash commands within the working directory | Trusted refactors, large edit loops |
| `plan` | Read-only — Claude can explore and plan but cannot edit anything | Architecture discussions, planning a refactor before execution |
| `auto` | A background classifier replaces manual prompts, deciding which actions to allow based on risk | Heavy automation; lets Claude work at speed with sensible defaults |
| `dontAsk` | Auto-denies anything that would prompt; only explicit allow rules and read-only Bash run | Strict, locked-down environments |
| `bypassPermissions` | Disables all permission prompts and most checks | Dangerous; use only in isolated containers/sandboxes |

In the CLI you can cycle modes with `Shift+Tab` during a session. VS Code, Desktop, and claude.ai have a mode selector in the UI.

**Common pattern: explore-plan-code.**
1. Start in `plan` mode for the discovery phase. Claude reads, searches, and produces a written plan but cannot touch files.
2. Switch to `default` or `acceptEdits` for implementation.
3. Drop back to `plan` when the next tricky decision comes up.

For details on mode behavior: `https://code.claude.com/docs/en/permission-modes.md`.

## Hooks (configuration shape)

Hooks attach to lifecycle events and run shell commands or HTTP endpoints. The full reference for events, input/output schema, and common patterns is in `references/extensions.md` section 5. The configuration shape for `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

Hooks merge across all settings scopes — every registered hook fires for matching events. There is no override.

See `assets/templates/hook-config.json.example` and `references/extensions.md` for hook event details.

## Sandboxing

Claude Code can run bash commands inside an OS-level sandbox that restricts filesystem and network access. When enabled, sandboxed commands can run more freely (auto-approved) because the sandbox enforces boundaries Claude cannot escape.

```audit-example -- Documents credential-file path patterns (cloud SDK creds, SSH keys, NETRC, dotenv) the auditor flags via DE-2 scanner; reference catalog explaining what to protect, not real credentials.
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials", "~/.ssh/id_*"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org", "registry.yarnpkg.com"],
      "deniedDomains": ["uploads.github.com"],
      "allowUnixSockets": ["/var/run/docker.sock"],
      "allowLocalBinding": true
    }
  }
}
```

**How auto-allow interacts with sandboxing.** When `autoAllowBashIfSandboxed: true`, sandboxed bash commands run without prompts because the sandbox is the safety net. Commands that **cannot** be sandboxed — needing network access to disallowed hosts, escaping the filesystem boundary — fall back to the regular permission flow. Explicit deny rules and dangerous commands (`rm`, `rmdir`) targeting critical paths still prompt.

**Excluded commands.** Some commands cannot be meaningfully sandboxed (Docker, VM tooling). List them under `excludedCommands` to bypass the sandbox.

**When to enable.** Sandboxing is the right answer when you want Claude to work autonomously with real consequences blocked. Combine with `acceptEdits` or `auto` permission modes for high-throughput automation that stays safe.

For the full sandbox schema and platform notes: `https://code.claude.com/docs/en/sandboxing.md`.

## Environment variables in settings

The `env` key sets environment variables for every Claude Code session in scope:

```json
{
  "env": {
    "ANTHROPIC_MODEL": "claude-opus-4-7",
    "MY_PROJECT_VAR": "value",
    "DEBUG": "true"
  }
}
```

Useful for setting model defaults, API endpoints, debug flags, or values that hooks and bash commands depend on.

For the full list of recognized environment variables: `https://code.claude.com/docs/en/env-vars.md`.

## Status line

A configurable line shown at the bottom of the CLI while Claude works. Useful for showing context window usage, costs, current git branch, or any custom info from a script.

```json
{
  "statusLine": "${git_branch} | ${context_used}/${context_total} | $${session_cost}"
}
```

Or point at a script that emits the status line:

```json
{
  "statusLine": "${CLAUDE_PROJECT_DIR}/.claude/status.sh"
}
```

For the full template variable list and script contract: `https://code.claude.com/docs/en/statusline.md`.

## Keybindings

Customize keyboard shortcuts in the CLI. Lives in `~/.claude/keybindings.json` (global only — keybindings are personal). Run `/keybindings` to open or create it with a schema reference.

```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "$docs": "https://code.claude.com/docs/en/keybindings",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "ctrl+u": null
      }
    }
  ]
}
```

`null` unbinds a default shortcut. `Ctrl+C`, `Ctrl+D`, `Ctrl+M` are reserved and cannot be rebound. The file hot-reloads when you save it.

For the action list and context names: `https://code.claude.com/docs/en/keybindings.md`.

## Fullscreen rendering

A smoother, flicker-free render mode with mouse support and stable memory usage in long conversations. Especially useful for sessions that stretch into many turns.

Toggle from the CLI or set in settings. For details: `https://code.claude.com/docs/en/fullscreen.md`.

## Voice dictation

Push-to-talk voice input for the CLI. Speak prompts instead of typing.

Setup and platform requirements: `https://code.claude.com/docs/en/voice-dictation.md`.

## Settings reference

This file covers the settings most users touch. The complete schema — including telemetry (`monitoring`), network (`proxy`, custom CAs), feature toggles (`fastMode`, fullscreen, file checkpointing), and dozens of edge-case keys — is at `https://code.claude.com/docs/en/settings.md`. Fetch it when you need a field this reference does not list.
