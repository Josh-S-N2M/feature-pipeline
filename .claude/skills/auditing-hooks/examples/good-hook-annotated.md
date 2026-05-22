# Good Hook: Annotated Example

## Contents

- The hooks config
- The hook script
- Per-dimension findings
- Total and verdict

## The hooks config (in settings.json)

```audit-example -- positive-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/check-bash.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## The hook script (the hook script under the project hooks directory)

```audit-example -- positive-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
#!/usr/bin/env bash
set -euo pipefail

# Read the JSON event from stdin
event=$(cat)

# Extract the command
cmd=$(echo "$event" | jq -r '.tool_input.command // ""')

# Refuse the most destructive patterns
case "$cmd" in
    *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf \$HOME"*)
        echo "Refusing destructive rm command: $cmd" >&2
        exit 2
        ;;
    *)
        exit 0
        ;;
esac
```

## Per-dimension findings

### Dimension 1: Configuration validity — 10/10
JSON parses. Hooks block is well-formed.

### Dimension 2: Event-name correctness — 10/10
`PreToolUse` is correct (case-sensitive).

### Dimension 3: Script existence and hygiene — 10/10
Path resolves. Script has shebang. Should be `chmod +x` on install (auditor flags if not).

### Dimension 4: Security posture — 10/10
- No SessionStart hook with network egress.
- No credential file references.
- No persistence vectors.
- No CLAUDE.md modification.
- No cross-subagent writes.

### Dimension 5: Matcher quality — 10/10
Matcher is `"Bash"` — scoped to shell tool calls only.

### Dimension 6: Persistence vectors — 10/10
None.

### Dimension 7: Idempotency — 10/10
The hook is a pure check; no side-effects.

### Dimension 8: Error handling — 10/10
`set -euo pipefail` — bash strict mode.

### Dimension 9: Exit-code protocol adherence — 10/10
Uses exit 2 to deny (correct for PreToolUse). Uses exit 0 to allow.

### Dimension 10: Anti-pattern absence — 10/10
None of HK-1 through HK-10 present.

## Total: 100/100 — PASS

## What this calibrates

- Scoped matcher (`"Bash"`) — not absent, not `*`, not comma-separated.
- Bash strict mode in the script.
- Exit 2 for PreToolUse deny.
- Limited scope: only refuses obvious destruction; doesn't try to police everything.
- 5-second timeout — fast.
