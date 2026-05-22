# Common Failures — Settings

## Contents

- The override-vs-additive surprise
- Silent failure: settings.local.json leaked to commit
- Silent failure: scope-mismatched field
- Silent failure: managed overrides project
- Diagnostic flow

## The override-vs-additive surprise

CLAUDE.md is additive. Hooks are additive. Settings are **override** — managed > local > project > user. The most common settings.json bug is the user expecting additive behavior.

Symptom: "I set `model: opus` in project settings but it's running Sonnet."

Audit: When fields appear in multiple scopes that the auditor can see, emit INFO "field present at multiple scopes; higher-precedence scope wins."

## Silent failure: settings.local.json leaked

The project's settings.local.json file is meant to be per-developer (gitignored). If not in .gitignore, it gets committed and shipped to the repo — leaking dev-only keys, machine paths, or workflow tweaks.

Audit: ST-1 BLOCKER. The cross-file check X10 in coordinator's project mode catches this.

## Silent failure: scope-mismatched field

`autoMemoryDirectory` only takes effect at user scope. Project-scope `autoMemoryDirectory` is silently ignored.

Symptom: "I set the directory but it's still using the default."

Audit: ST-5 MAJOR.

Other scope-mismatched fields: `disableBypassPermissionsMode` (managed only), `claudeMd` (managed only).

## Silent failure: managed overrides project

A project sets `model: opus`. Managed has `model: sonnet`. The project's setting is silently overridden.

Symptom: user is surprised at the model.

Audit: when both managed and project settings.json are visible to the auditor, INFO note "managed overrides project for field X."

## Silent failure: permission rule shadowed by higher scope

User settings has `permissions.deny: ["Bash(*)"]` to lock down. Project settings has `permissions.allow: ["Bash(*)"]` — but **`allow` doesn't override `deny`** within the same scope. However, between scopes, the merged permissions object's `deny` from project overrides user-scope `deny`.

This gets confusing fast. The auditor's recommendation:
- All deny rules should live at managed or user scope (or both).
- Project allow rules should be specific (not wildcards).

## Silent failure: deny pattern with literal quotes

```audit-example -- common-failures catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "permissions": {
    "deny": ["Bash(\"rm -rf /\")"]
  }
}
```

Doesn't match `Bash(rm -rf /)` because the quotes are part of the literal pattern. The actual rm command doesn't have those quotes.

Audit: detected as a permission-syntax issue → MAJOR.

## Silent failure: output style ignored

A `outputStyles` entry references a file that doesn't exist. Silently dropped from the available styles.

Symptom: `/output-style <name>` shows the style as unavailable.

Audit: file-existence check on each entry → MAJOR.

## Silent failure: env block with shell substitution

```audit-example -- common-failures catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "env": {
    "BUILD_ID": "$(date +%Y%m%d)"
  }
}
```

The `env` block does **not** run shell substitution — `$()` is treated as a literal string. The env var would be the literal `$(date +%Y%m%d)`.

Audit: MINOR with note. Suggest using `${VAR}` reference syntax for vars defined at shell level.

## Diagnostic flow for "my settings aren't taking effect"

1. `/settings` — does the effective value match what's in the file?
   - **No:** scope override. Check higher scopes (managed > local > project > user).
2. Is the field at the wrong scope (ST-5)?
3. For permission rules: is there a more-specific rule shadowing yours?
4. `/doctor` — any parse errors?

## Diagnostic commands

```
/settings              # Show effective settings
/permissions           # Show effective permission rules after scope merge
/doctor                # Validate all settings files
/output-style          # List available output styles
```
