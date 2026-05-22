# Hook Specification

## Contents

- The 12 event names (case-sensitive)
- Configuration shape
- Matchers
- Exit code protocol
- Lifecycle behavior
- Hook script hygiene

## Source

`code.claude.com/docs/en/hooks`, last verified 2026-05.

## The 12 event names

Event names are **case-sensitive**. Misspellings result in silent no-op — the hook is never invoked.

| Event | When it fires | Common use |
|---|---|---|
| `SessionStart` | Session starts (cd into project, claude.code start) | Initial state load, MOTD |
| `PreToolUse` | Before any tool call | Permission checks, logging |
| `PostToolUse` | After tool call returns | Logging, validation |
| `UserPromptSubmit` | User submits a prompt | Input filtering, command translation |
| `Stop` | Session ends normally | Cleanup, summary save |
| `SubagentStart` | Before subagent spawn | Pre-spawn checks |
| `SubagentStop` | After subagent returns | Subagent-result processing |
| `Notification` | Claude emits a notification | UI augmentation |
| `PermissionRequest` | Claude requests permission (interactive only) | Auto-approve/deny logic |
| `PreCompact` | Before context compaction | Save snapshot |
| `PostCompact` | After context compaction | Inspect what survived |
| `Error` | An error occurs | Logging, alerting |

The validator's known set is exactly these 12. Any other name fires the BLOCKER finding "event name not recognized; hook will never fire."

## Configuration shape

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-bash.sh"
          }
        ]
      }
    ]
  }
}
```

Fields per hook entry:

- `matcher` (optional) — regex or tool-name pattern. If absent, matches all events of this type.
- `hooks` — list of hook actions.
- Each action has `type` (always `"command"` currently) and `command` (the shell command to run).
- `timeout` (optional) — seconds. Default: 30.
- `runInBackground` (optional) — boolean. Default: false.

The `command` value can be a path to a script, an inline command, or a `python3 -m ...` invocation.

## Matchers

For `PreToolUse` and `PostToolUse`, matchers select which tool calls trigger the hook:

- `"Bash"` — matches only Bash tool calls
- `"Read|Grep|Glob"` — regex, matches multiple
- absent or `""` — matches all tool calls (fires on every tool — expensive)

### Common matcher mistakes

- `"bash"` — lowercase doesn't match `Bash`. Hook never fires for shell calls. BLOCKER.
- `"Bash, Read"` — comma is not regex syntax. Probably author meant `"Bash|Read"`. MAJOR.
- `"*"` — not a valid regex; matches nothing in regex engine. Wanted `".*"`. BLOCKER.

## Exit code protocol

Hook commands communicate with Claude Code via exit codes:

| Exit code | Meaning |
|---|---|
| 0 | Success; continue normally |
| 1 | Error; surface to user but continue |
| 2 | Block this operation (PreToolUse only); deny + show stderr |
| Other | Error; treated like 1 |

For `PreToolUse`, exit code 2 is the only way to block a tool call. Scripts that error-check by exiting 1 for "deny" cases are silently allowing the tool call. MAJOR.

For other events, exit code 2 is harmless but conveys no special meaning.

## Lifecycle behavior

- **Hooks are additive across scopes.** User + project + managed all contribute. Each contributes its own hook entries; they all fire.
- **No de-duplication.** Two identical hook entries fire twice.
- **Order:** within an event, hooks fire in the order they appear after scope-merging.
- **Timeout:** if `timeout` elapses, hook is killed; treated as error.
- **Hooks don't fire at max_turns.** If a session ends because of max_turns, Stop hooks don't run.
- **PermissionRequest hooks are interactive-only.** In `claude -p` mode they never fire.

## Hook script hygiene

A good hook script:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
#!/usr/bin/env bash
set -euo pipefail

# Read the JSON event from stdin
event=$(cat)

# Extract a field
tool_name=$(echo "$event" | jq -r '.tool_name')

# Logic
if [[ "$tool_name" == "Bash" ]]; then
    cmd=$(echo "$event" | jq -r '.tool_input.command')
    case "$cmd" in
        *"rm -rf /"*) echo "Refusing destructive rm" >&2; exit 2 ;;
    esac
fi

exit 0
```

Audit checks:
- Has `set -e` or equivalent error-handling — MINOR if absent.
- Is executable (`chmod +x`) — BLOCKER if not (silent failure).
- First line is shebang — MAJOR if absent.
- Reads stdin if it consumes event data — INFO check (hard to verify statically).
- Doesn't `exit 0` blindly when an error occurred — agent judgment, MINOR.

## Idempotency

Hooks should be idempotent when possible. State-modifying hooks (writes to files, modifies env) that are called multiple times in one session can produce wrong results.

- A logging hook (append-only) — idempotent enough, INFO.
- A counter-increment hook — not idempotent. MINOR if it doesn't guard against repeats.
- A "send notification" hook — fires multiple times if multiple matching events. MINOR.

## Diagnostic commands

```
/hooks
```

Shows hooks that will fire, in fire-order, after scope merging. Reveals shadowed entries (none — hooks are additive), misspelled event names (those are absent from the listing), and broken script paths.
