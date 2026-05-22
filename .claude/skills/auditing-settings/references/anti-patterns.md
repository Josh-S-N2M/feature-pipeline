# Settings Anti-Patterns

## Contents

- 10 named settings anti-patterns (ST-1 through ST-10)
- Detection map

The dangerous-looking content shown in audit-example blocks is illustrative.

## ST-1: settings.local.json not gitignored — BLOCKER

Symptom: a settings.local.json file exists under the project's .claude directory, but the .gitignore doesn't cover it.

Why bad: Local settings may contain dev-only API keys, machine paths, or personal preferences that leak to commits.

Fix: Add the settings.local.json path to .gitignore.

## ST-2: Literal credential in env — BLOCKER (security_critical)

Symptom:

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "env": {
    "GITHUB_TOKEN": "ghp_actualValueHere..."
  }
}
```

Why bad: Credential committed to settings; rotates only when the file is edited.

Fix: Use `${GITHUB_TOKEN}` reference; the user's shell env provides the actual value.

## ST-3: Permissive Bash allow — MAJOR (managed: BLOCKER)

Symptom:

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "permissions": {
    "allow": ["Bash(*)"]
  }
}
```

Why bad: Any shell command auto-allowed. User is one Claude misunderstanding away from disaster.

Fix: Scope allowed commands: `Bash(git status)`, `Bash(npm test *)`, etc.

## ST-4: Missing deny baseline — MINOR (managed: MAJOR)

Symptom: No `permissions.deny` entries, or deny entries missing the canonical baseline (rm, curl|bash, etc.).

Why bad: Known-dangerous patterns not blocked.

Fix: Add the baseline deny items (see permission-rules-spec.md).

## ST-5: Scope-mismatched field — MAJOR

Symptom: `autoMemoryDirectory` in project settings; `disableBypassPermissionsMode` in user settings; `claudeMd` in project settings.

Why bad: Field is silently ignored — user thinks it applies but it doesn't.

Fix: Move to the correct scope.

## ST-6: Unrecognized field — MINOR

Symptom: Field name not in the known schema (typo or new feature).

Why bad: Silently ignored.

Fix: Verify field name, or remove.

## ST-7: WebFetch with no scoping — MAJOR

Symptom:

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "permissions": {
    "allow": ["WebFetch"]
  }
}
```

(or `WebFetch(*)` — same effect)

Why bad: Any outbound HTTP auto-allowed. Exfiltration risk.

Fix: Scope to specific domains, e.g. `WebFetch(github.com)`.

## ST-8: Output style with safety override — BLOCKER (security_critical)

Symptom: Output style body contains "ignore previous safety rules", "always do X regardless of approval", reframing language.

Why bad: Output styles are applied to every response; safety override would persist for the session.

Fix: Remove the offending content.

## ST-9: Bare tool name in permission rules — MAJOR

Symptom: `permissions.allow` contains a tool name with no parens at all (e.g. `"Bash"` instead of `"Bash(git status)"`).

Why bad: Equivalent to `Bash(*)` — all calls allowed.

Fix: Add scoping parens.

## ST-10: Conflicting allow + deny — MINOR

Symptom: Same pattern in `allow` and `deny`.

Why bad: Deny wins; the allow is dead config.

Fix: Remove the allow entry, or remove the deny if it was intended to be a typo.

## Detection map

| Pattern | Detected by |
|---|---|
| ST-1 | cross-file check X10 (.gitignore + settings.local.json presence) |
| ST-2 | `scripts/scan_settings_secrets.py` (credential pattern in env) |
| ST-3, ST-7, ST-9 | `scripts/validate_permissions.py` (permissive-pattern detection) |
| ST-4 | `scripts/validate_permissions.py` (deny-baseline coverage) |
| ST-5 | `scripts/validate_settings_schema.py` (scope-mismatch table) |
| ST-6 | `scripts/validate_settings_schema.py` (field allow-list) |
| ST-8 | `scripts/validate_output_styles.py` (safety-override pattern scan) |
| ST-10 | `scripts/validate_permissions.py` (set intersection) |
