# Managed Settings Specification

## Contents

- What managed-settings.json is
- Lockdown knobs
- Managed deny baseline
- Subagent configuration in managed
- Audit checks (--managed mode)

## Source

`code.claude.com/docs/en/managed-settings`, last verified 2026-05.

## What it is

Managed-settings.json is a system-administered Claude Code configuration that wins over all other scopes. It is typically deployed by enterprise IT to a fixed path:

- Linux: `/etc/claude/managed-settings.json`
- macOS: `/Library/Application Support/Claude/managed-settings.json`
- Windows: `C:\ProgramData\Claude\managed-settings.json`

Users cannot override managed settings. The auditor's `--managed` mode applies stricter rules tailored to this enterprise deployment.

## Lockdown knobs

Managed-settings has fields that disable potentially-dangerous Claude Code features. The auditor checks for safe values:

| Field | Safe value | What it does |
|---|---|---|
| `disableBypassPermissionsMode` | `"disable"` | Subagents/sessions cannot use `permissionMode: bypassPermissions` |
| `disableAllPlugins` | `false` or `true` per policy | Disables plugin loading |
| `disableMcpServers` | `false` or `true` per policy | Disables MCP servers |
| `disableExternalConnectors` | `false` or `true` per policy | Disables external connectors |
| `disableTelemetry` | per policy | Anthropic telemetry opt-out |

In `--managed` mode:
- `disableBypassPermissionsMode` should be `"disable"` — MINOR if absent or set to enabling value.
- Other disables: INFO if absent (the admin chose not to disable them).

## Managed deny baseline

A managed-settings.json should include the deny baseline (see permission-rules-spec.md):

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "permissions": {
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(rm -rf ~)",
      "Bash(curl * | bash)",
      "Bash(wget * | sh)",
      "Bash(eval *)",
      "Write(/etc/**)",
      "Write(~/.ssh/**)",
      "WebFetch(file://*)"
    ]
  }
}
```

In `--managed` mode, each missing baseline item = MINOR with note.

## Subagent configuration in managed

Managed-settings can pre-configure subagents that all users get:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "subagents": {
    "code-reviewer": {
      "description": "Reviews PR diffs...",
      "tools": "Read, Grep, Glob, Bash(git diff *)",
      "model": "sonnet"
    }
  }
}
```

This is a hub for the same checks `auditing-subagents` does. The auditor delegates the deep subagent-content check; it just validates the structural integrity of the `subagents` object here.

## env block at managed scope

The managed `env` block is special: secrets locked here cannot be overridden by user/project. This is the right place to inject CI/CD tokens for automation:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "env": {
    "CI_RUNNER_TOKEN": "${CI_RUNNER_TOKEN}",
    "ARTIFACT_REGISTRY_PASSWORD": "${ARTIFACT_REGISTRY_PASSWORD}"
  }
}
```

In `--managed` mode:
- Literal credentials = BLOCKER (security_critical) — same as elsewhere.
- `${VAR}` references = OK.
- Variables that look like they should be locked (TOKEN, KEY, PASSWORD, SECRET in the name) appearing only at lower scopes = INFO with note "consider locking at managed scope."

## claudeMd field

The managed `claudeMd` field injects content at the bottom of CLAUDE.md loaded for every session. It's a way to enforce a baseline ruleset:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "claudeMd": "## Compliance\\n\\nAll PRs must reference a ticket ID."
}
```

Audit:
- Content > 200 lines or > 25KB → MAJOR (the same size limit as CLAUDE.md applies; the injection is silently truncated past the cap).
- Credentials in `claudeMd` → BLOCKER + security_critical.
- The field at non-managed scope → MAJOR (silently ignored).

## Audit checks in --managed mode

When the user invokes the auditor with `--managed`, the following findings escalate in severity:

| Default mode | --managed mode | What |
|---|---|---|
| INFO | MINOR | Missing deny-baseline items |
| INFO | MINOR | `disableBypassPermissionsMode` absent |
| MINOR | MAJOR | Permissive `allow: [Bash(*)]` |
| MINOR | MAJOR | Empty deny list |

## Diagnostic commands

```
/settings --managed
```

Shows managed-settings configuration (if loaded). User cannot edit; admin must.
