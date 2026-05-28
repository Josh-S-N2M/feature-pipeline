---
name: auditing-hooks
description: >-
  Audits Claude Code hooks — both the hooks configuration (settings.json
  hooks block or .claude/hooks.json) and the hook scripts in .claude/hooks/.
  ALWAYS invoke when reviewing, auditing, evaluating, scoring, vetting,
  fixing, or critiquing hooks, when triaging "my hook isn't firing," or
  when a sub-agent is asked to assess hook quality. Validates event names
  (case-sensitive), matchers, script existence, persistence vectors,
  exit-code protocol adherence, security posture (CVE-2025-59536 class),
  and idempotency. Report-only.
allowed-tools: Read Grep Glob Bash(python3 *)
pedagogical_sections:
  - path: references/hook-spec.md
    justification: "Hook spec reference; contains anti-pattern examples of unsafe hook scripts the auditor scanner flags"
  - path: references/security-checklist.md
    justification: "Hook security checklist reference; enumerates credential exfiltration patterns the auditor scans hooks for"
  - path: references/anti-patterns.md
    justification: "Hook anti-pattern reference catalog documenting what the auditing-hooks scanner detects as findings"
  - path: references/common-failures.md
    justification: "Hook common-failures catalog with negative-example fixtures the auditing-hooks scanners flag"
  - path: examples/bad-hook-annotated.md
    justification: "Bad-hook annotated negative-example fixture; multiple anti-patterns illustrated for scanner training"
---

# Auditing Claude Code Hooks

Audits Claude Code hooks. A hook is a shell command Claude Code runs at specific lifecycle events: SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, Notification, PermissionRequest. Hooks are an additive feature — all configured hooks at any scope fire when the event triggers.

> **Canonical source.** The authoritative hook **event-name** enumeration is [`.claude/canonical/hook-events.yaml`](../../canonical/hook-events.yaml) (loaded by `canonical.py`; the validators import it). The event names listed in this SKILL and in `references/hook-spec.md` mirror that file — if they disagree, the YAML wins. Per KB-cc-design Principle 11, do not duplicate the event enumeration without a reference back to the canonical source.

This skill is part of the **auditing-cc-configs** family. Shared rubric, weights, thresholds, and triage live in the coordinator skill.

It writes one file: an audit report. It does not modify the audited hooks or scripts.

## The audit loop

1. **Locate the target.** Either:
   - A hooks block in settings.json (or the hooks.json file at project scope)
   - A hook script under the project's hooks directory or the user's home hooks directory

2. **Run deterministic checks:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_hooks.py <path>
   ```

3. **Apply verification step.**

4. **Run pedagogical-marker prefilter** if applicable.

5. **Compute verdict and write report.**

## Routing table — dimensions

| # | Dimension | Reference |
|---|---|---|
| 1 | Configuration validity | `references/hook-spec.md` |
| 2 | Event-name correctness | `references/hook-spec.md` |
| 3 | Script existence and hygiene | `references/hook-spec.md` |
| 4 | Security posture | `references/security-checklist.md` |
| 5 | Matcher quality | `references/hook-spec.md` |
| 6 | Persistence vectors | `references/security-checklist.md` |
| 7 | Idempotency | `references/hook-spec.md` |
| 8 | Error handling | `references/hook-spec.md` |
| 9 | Exit-code protocol adherence | `references/hook-spec.md` |
| 10 | Anti-pattern absence | `references/anti-patterns.md` |

For cross-cutting failure modes, see `references/common-failures.md`.

## Critical security context: CVE-2025-59536

A malicious project shipping a settings.json file (under its .claude directory) with a SessionStart hook can run arbitrary code the first time a user opens the directory in Claude Code. The auditor's security checklist treats SessionStart hooks with network egress or filesystem-write-outside-the-project as BLOCKER (security_critical).

## Event-name case sensitivity

Event names are case-sensitive: `PreToolUse` (correct), `pretooluse` (silently never fires). The validator catches all 12 known event names and warns on misspellings.

## Severity meanings (v2)

- **BLOCKER** — hook won't fire, security issue, or destructive operation. −12 per dim + −12 flat.
- **MAJOR** — works but degrades behavior.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70. SECURITY-BLOCK on confirmed CRITICAL.

## Calibration examples

- [`examples/good-hook-annotated.md`](examples/good-hook-annotated.md) — well-formed hook config + script
- [`examples/bad-hook-annotated.md`](examples/bad-hook-annotated.md) — multiple issues including CVE-2025-59536 pattern

## Scope

In scope: hooks configuration blocks at any scope, hook scripts under the project's hooks directory or the user's home hooks directory.

Not in scope: subagents, skills, CLAUDE.md, settings.json (non-hooks blocks), MCP, output styles.

## Report-only contract

This skill never modifies the audited hook config or scripts. The report contains fix suggestions, but applying them is the user's job.
