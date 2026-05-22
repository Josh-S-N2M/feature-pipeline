# Common Failures — Hooks

## Contents

- The 5 most common silent failures
- Diagnostic flow

## Silent failure: misspelled event name

A hook with `"preToolUse"` (lowercase 'p') is silently ignored. Event names are case-sensitive.

Symptom: hook never fires.

Audit: HK-1 BLOCKER.

## Silent failure: max_turns ends session, Stop hook doesn't fire

Per Anthropic docs: at max_turns, the session ends without firing Stop hooks.

Symptom: cleanup that the user expected didn't happen.

Audit: HK-9 MINOR with note.

## Silent failure: PermissionRequest hooks in headless mode

PermissionRequest hooks are interactive-only. In `claude -p` mode they never fire.

Symptom: auto-approve hook works locally, breaks in CI.

Audit: MINOR with note when PermissionRequest hook is present and the project may be used in headless mode.

## Silent failure: hook command path not found

`"command": ".claude/hooks/foo.sh"` and the file doesn't exist. The hook is configured but never runs.

Symptom: hook silently doesn't fire.

Audit: HK-5 BLOCKER (cross-file check X1 in coordinator's project mode).

## Silent failure: PreToolUse hook exits 1 to deny

Author wanted to deny a tool call, exited 1. Claude Code interprets 1 as "error, continue" — the tool call proceeds.

Symptom: hook runs, output appears, but the tool call goes through anyway.

Audit: HK-8 MAJOR.

## Diagnostic flow for "my hook isn't firing"

1. `/hooks` inside Claude Code — does the hook appear in the listing?
   - **No:** event-name typo (HK-1), config parse error, or scope problem.
   - **Yes, but doesn't fire on expected tools:** matcher problem (HK-3, HK-4).
2. Is the script path correct and the file executable?
3. For PreToolUse: are you trying to deny with exit 1 instead of exit 2?
4. For Stop: did the session end via max_turns instead of normal stop?
5. For PermissionRequest: are you in headless (`claude -p`) mode?

## The "hook ran but the audit still flags it" symptom

The audit's HA-10 (no matcher) fires even when the hook works. That's intentional — "fires on every tool" is a smell even when it works.

The audit's HA-12 (string-matching that should be a permission rule) fires even when the hook works. The recommendation is a cleaner solution (permission rule).

## The "two scopes of the same hook" symptom

Hooks are additive. User-scope + project-scope = both fire. If the user is surprised to see "my hook fired twice," check both scopes.

Audit: cross-file check X18 (additive primitive duplication) emits MINOR or INFO depending on whether the entries are identical.
