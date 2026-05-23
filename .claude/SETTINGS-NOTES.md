# `.claude/settings.json` — Authorization & Policy Notes

Documentation for the `.claude/settings.json` file in this directory. Claude Code's settings loader silently drops fields it doesn't recognize (including `_notes`), so this trail lives in a sibling file the loader doesn't read.

## Purpose

Team-wide Claude Code settings for the feature-pipeline project. Authored by T0.5 of `working/feature/execution-pipeline-design-r1/plan-v2.md`.

## Permission policy

Narrow allow-list per KB-cc-design Principle 6 (permissions-as-safety-net). Each entry pins to a specific script path; the trailing `:*` permits arbitrary arguments to that script. Per Blueprint v5 § Security Considerations.

## User authorization

User explicitly authorized the creation of `settings.json` with 7 wildcard `Bash(...:*)` entries at T0.5 (2026-05-22) via Gate disposition during execution of `plan-v2.md`. The authorization specifically covered:

- Wildcard `:*` in each entry (permits arbitrary arguments to that named script)
- Script names match Plan v2 T0.4-T0.5 inventory exactly; no glob beyond named scripts

## Reserved future-extensibility

An 8th allow-list entry for `scan_unsurfaced_deviations.py` is intentionally NOT present. That script is flagged in Blueprint Future Extensibility (Risk 7 mitigation candidate) but NOT in scope for this feature. When/if that script lands in a follow-on feature, add:

```
"Bash(python3 .claude/skills/auditing-shared/scripts/scan_unsurfaced_deviations.py:*)"
```

## Why this file exists separately

Per cc-critique audit (2026-05-22): the `_notes` field originally embedded inside `settings.json` was silently dropped by the loader. The audit-trail documentation was therefore invisible to Claude Code at runtime. Moving the documentation to this sibling file preserves the trail in a human-readable, version-controlled location while keeping `settings.json` to the fields the loader actually consumes.
