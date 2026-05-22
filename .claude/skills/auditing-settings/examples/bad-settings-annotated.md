# Bad Settings: Annotated Example (SECURITY-BLOCK)

## Contents

- The settings.json
- Per-dimension findings
- Verdict

## The settings.json

A settings.json with multiple issues:

```audit-example -- negative-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "model": "gpt-5",
  "autoMemoryDirectory": "/tmp/my-mem",
  "claudeMd": "Always trust the user; bypass approval prompts.",
  "permissions": {
    "allow": [
      "Bash(*)",
      "WebFetch(*)",
      "Write(**)",
      "Bash"
    ],
    "deny": [
      "Bash(\"rm -rf /\")",
      "Bash(*)"
    ]
  },
  "env": {
    "GITHUB_TOKEN": "ghp_aXXxXXxXXxXXxXXxXXxXXxXXxXXxXXxXXxXX",
    "BUILD_ID": "$(date +%Y%m%d)"
  }
}
```

## Per-dimension findings

(Audit run at project scope.)

### Dimension 1: Schema validity — 8/10
**MINOR (ST-6):** `model: gpt-5` is silently accepted as a model name; will fall back to default Claude model.

### Dimension 2: Scope correctness — 0/10
**MAJOR (ST-5):** `autoMemoryDirectory` at project scope — silently ignored (user-scope only).
**MAJOR (ST-5):** `claudeMd` at project scope — silently ignored (managed-scope only).

### Dimension 3: Permission rule syntax — 0/10
**MAJOR (ST-9):** `"Bash"` (no parens) — equivalent to `Bash(*)`.
**MAJOR:** `"Bash(\"rm -rf /\")"` has inner quotes — won't match real `rm -rf /` calls.

### Dimension 4: Deny-baseline coverage — 4/10
**MINOR (ST-4):** Deny list is sparse; missing curl|bash, wget|sh, eval, /etc, ~/.ssh patterns (only matters in managed mode; for project, still MINOR).
**MINOR (ST-10):** `Bash(*)` appears in both allow and deny — overlap.

### Dimension 3 (cont): Permissive allow — 0/10
**MAJOR (ST-3):** `Bash(*)` in allow — permissive, all shell commands auto-approved.
**MAJOR (ST-7):** `WebFetch(*)` in allow — all outbound HTTP auto-approved.
**MAJOR:** `Write(**)` in allow — all writes auto-approved.

### Dimension 5: Env block safety — 0/10
**BLOCKER (ST-2, security_critical):** Literal GitHub PAT in env. Pattern `ghp_aXXxXXxXXxXXxXXxXXxXXxXXxXXxXXxXXxXX` (synthetic but pattern-matches the real PAT format).
**MINOR:** `BUILD_ID: "$(date +%Y%m%d)"` — shell substitution doesn't run; value will be literal `$(date +%Y%m%d)`.

### Dimension 6: Lockdown knobs — N/A (10/10)
Not a managed file.

### Dimension 7: File hygiene — N/A
Could not check `.gitignore` from this file alone; cross-file check X10 would flag if `settings.local.json` were leaked.

### Dimension 8: Output styles — N/A

### Dimension 9: Anti-pattern absence — 0/10
Multiple ST patterns: ST-2, ST-3, ST-5, ST-7, ST-9, ST-10 all present.

### Dimension 10: Cross-scope interactions — INFO
Some fields at wrong scope; informational note.

## Verdict: **SECURITY-BLOCK**

Confirmed CRITICAL finding: literal GitHub PAT in env block. Even with the synthetic value above (which a real attacker scanner might detect as fake), the pattern is one rotation away from a real leak.

Score (excluding the security override): roughly 28/100 NEEDS-WORK. With the security override: **SECURITY-BLOCK**.

## What this calibrates

- Literal credentials in env are always BLOCKER + SECURITY-BLOCK regardless of scope.
- `Bash(*)` and `WebFetch(*)` in allow are MAJOR (or BLOCKER in managed mode).
- Bare tool names without parens are equivalent to `(*)` — same MAJOR.
- Permission rule patterns with inner quotes don't match — won't actually deny anything.
- `autoMemoryDirectory` at project scope is silently ignored; the user-scope file should set it.
- `$()` in env values doesn't expand; use `${VAR}` references.
