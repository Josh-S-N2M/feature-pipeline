# Hook Anti-Patterns

## Contents

- 10 named hook anti-patterns (HK-1 through HK-10)
- Detection map

The dangerous-looking content shown in `audit-example` blocks below is illustrative.

## HK-1: Misspelled event name — BLOCKER

Symptom: `"pretooluse"`, `"PreToolUSE"`, `"pre_tool_use"`.

Why bad: Event names are case-sensitive. Misspelled events silently never fire.

Fix: Use one of the 12 canonical names. See `references/hook-spec.md`.

## HK-2: Empty hooks list — MINOR

Symptom: `"hooks": []` or `"PreToolUse": []` configured but contains no actions.

Why bad: Dead configuration. May confuse maintainers.

Fix: Remove the event entry, or add at least one hook action.

## HK-3: Matcher uses comma — MAJOR

Symptom: `"matcher": "Bash, Read"`.

Why bad: Comma is not regex syntax. Hook never fires (matches no tool name literally).

Fix: Use regex pipe: `"Bash|Read"`.

## HK-4: Matcher uses bare `*` — BLOCKER

Symptom: `"matcher": "*"`.

Why bad: Not valid regex; matches nothing.

Fix: Use `".*"` for "match anything", or omit the matcher.

## HK-5: Hook command path doesn't exist — BLOCKER

Symptom: `"command": ".claude/hooks/missing.sh"` and no such file.

Why bad: Hook silently never runs.

Fix: Create the script, or remove the hook entry.

## HK-6: Hook script not executable — MAJOR

Symptom: Script exists but doesn't have execute permission.

Why bad: Shell can't run it; silent failure.

Fix: `chmod +x .claude/hooks/<script>`.

## HK-7: Hook missing shebang — MAJOR

Symptom: First line of hook script isn't `#!/usr/bin/env bash` or equivalent.

Why bad: Depending on the user's shell, the script may not run or run with wrong interpreter.

Fix: Add a shebang line.

## HK-8: PreToolUse hook exits 1 to deny — MAJOR

Symptom: Hook script exits 1 in a code path that should deny.

Why bad: For PreToolUse, only exit code 2 denies; exit 1 is "error, continue."

Fix: Change `exit 1` to `exit 2` for deny paths.

## HK-9: Cleanup hook on Stop, assumes always runs — MINOR

Symptom: Stop hook performs cleanup the system depends on.

Why bad: At max_turns, Stop hooks don't fire. Cleanup is skipped.

Fix: Move cleanup to a separate trigger (cron, file-system watcher, post-session check).

## HK-10: Hook with side-effect, no idempotency guard — MINOR

Symptom: Hook appends a line to a log file every run.

Why bad: Multiple invocations during a session multiply the side-effect.

Fix: Add an idempotency check (read existing state before writing) or accept that the side-effect is per-invocation.

## Detection map

| Pattern | Detected by |
|---|---|
| HK-1 | `scripts/validate_hooks_config.py` (event-name allow-list) |
| HK-2 | `scripts/validate_hooks_config.py` |
| HK-3, HK-4 | `scripts/validate_hooks_config.py` (matcher syntax check) |
| HK-5 | `scripts/validate_hooks_config.py` (path existence) |
| HK-6, HK-7 | `scripts/analyze_hook_script.py` |
| HK-8 | `scripts/analyze_hook_script.py` (exit-code static analysis) |
| HK-9, HK-10 | agent judgment after reading the script |
