---
name: auditing-settings
description: >-
  Audits Claude Code settings files — settings.json, settings.local.json,
  ~/.claude/settings.json, and managed-settings.json — plus output-styles
  files. ALWAYS invoke when reviewing, auditing, evaluating, scoring,
  vetting, fixing, or critiquing these files, when triaging "my permission
  rules aren't working," when running --managed lint, or when a sub-agent
  is asked to assess settings quality. Validates schema fields, permission
  rule syntax, deny-baseline coverage, env block safety, lockdown knob
  presence (managed mode), settings.local.json gitignore status, and
  output-style frontmatter. Report-only.
allowed-tools: Read Grep Glob Bash(python3 *)
pedagogical_sections:
  - path: references/settings-spec.md
    justification: "Settings spec reference; contains anti-pattern examples of unsafe settings.json the auditor flags"
  - path: references/permission-rules-spec.md
    justification: "Permission rules spec reference; documents overly-broad permission patterns the auditor scans for"
  - path: references/managed-settings-spec.md
    justification: "Managed settings spec reference; documents enterprise-policy patterns + anti-pattern catalog"
  - path: references/anti-patterns.md
    justification: "Settings anti-pattern reference catalog documenting what the auditing-settings scanner detects"
  - path: references/common-failures.md
    justification: "Settings common-failures catalog with negative-example fixtures the auditing-settings scanners flag"
  - path: examples/bad-settings-annotated.md
    justification: "Bad-settings annotated negative-example fixture; multiple anti-patterns illustrated for scanner training"
  - path: examples/good-settings-annotated.md
    justification: "Good-settings annotated positive-example fixture; demonstrates correct patterns for contrast against anti-patterns"
---

# Auditing Claude Code Settings

Audits Claude Code settings.json files at all scopes, plus output-style files. The settings schema is **override-style** between scopes (managed > local > project > user), unlike CLAUDE.md (additive) and hooks (additive). Permission rules within a scope use a precedence model: ask > deny > allow.

This skill is part of the **auditing-cc-configs** family. Shared rubric, weights, thresholds, and triage live in the coordinator skill.

It writes one file: an audit report. It does not modify settings.

## The audit loop

1. **Locate the target.** A settings.json at any scope, an output-styles file, or (in `--managed` mode) the managed-settings.json.

2. **Run deterministic checks:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_settings.py <path>
   ```

3. **Apply verification step.**

4. **Run pedagogical-marker prefilter** if applicable.

5. **Compute verdict and write report.**

## Routing table — dimensions

| # | Dimension | Reference |
|---|---|---|
| 1 | Schema validity | `references/settings-spec.md` |
| 2 | Scope correctness | `references/settings-spec.md` |
| 3 | Permission rule syntax | `references/permission-rules-spec.md` |
| 4 | Deny-baseline coverage | `references/permission-rules-spec.md` |
| 5 | Env block safety | `references/settings-spec.md` |
| 6 | Lockdown knobs (managed) | `references/managed-settings-spec.md` |
| 7 | File hygiene (gitignore) | `references/anti-patterns.md` |
| 8 | Output styles | `references/settings-spec.md` |
| 9 | Anti-pattern absence | `references/anti-patterns.md` |
| 10 | Cross-scope interactions | `references/common-failures.md` |

## Critical: --managed mode

When invoked with `--managed`, the auditor applies stricter lint rules tailored to enterprise managed-settings deployment:

- All lockdown knobs (`disableBypassPermissionsMode`, `disableAllPlugins`, etc.) checked for presence with safe values
- `permissions.deny` checked for baseline coverage (the canonical safety list)
- `env` block checked for sensitive variables that should be locked at managed scope

In default mode, these become MINOR informational findings.

## Severity meanings (v2)

- **BLOCKER** — settings won't parse, has security issue, locks user out, or breaks core functionality.
- **MAJOR** — works but degrades security/behavior.
- **MINOR** — deviates from best practice.
- **NIT** — taste.

PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70. SECURITY-BLOCK on confirmed CRITICAL.

## Calibration examples

- [`examples/good-settings-annotated.md`](examples/good-settings-annotated.md) — well-formed settings scoring 95+
- [`examples/bad-settings-annotated.md`](examples/bad-settings-annotated.md) — multiple issues, SECURITY-BLOCK class

## Scope

In scope: settings.json at all scopes, output-styles files, managed-settings.json (with `--managed` flag).

Not in scope: hooks block contents (route to `auditing-hooks`), agents (route to `auditing-subagents`), CLAUDE.md (route to `auditing-context-files`), MCP server configs (route to `auditing-mcp`).

When auditing a full settings.json, this skill validates the schema and surrounding fields; it delegates the hooks block to `auditing-hooks` for in-depth analysis.

## Report-only contract

This skill never modifies settings or output styles. The report contains fix suggestions, but applying them is the user's job.
