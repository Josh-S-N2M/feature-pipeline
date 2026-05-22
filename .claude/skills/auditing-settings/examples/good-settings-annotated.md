# Good Settings: Annotated Example (95+/100)

## Contents

- The settings.json (full)
- Per-dimension findings
- Verdict
- What this calibrates

## The settings.json

A well-formed project-scope `settings.json`:

```audit-example -- positive-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "model": "sonnet",
  "permissions": {
    "allow": [
      "Read(./**)",
      "Grep(**/*)",
      "Glob(**/*)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(npm test *)",
      "Bash(npm run *)",
      "WebFetch(github.com)",
      "WebFetch(docs.anthropic.com)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(rm -rf ~)",
      "Bash(curl * | bash)",
      "Bash(wget * | sh)",
      "Bash(eval *)",
      "Write(/etc/**)",
      "Write(~/.ssh/**)",
      "WebFetch(file://*)"
    ],
    "ask": [
      "Bash(*)",
      "Write(**)",
      "Edit(**)"
    ]
  },
  "env": {
    "NODE_ENV": "development",
    "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  },
  "outputStyles": [
    "concise"
  ]
}
```

## Per-dimension findings

### Dimension 1: Schema validity — 10/10
JSON parses. All top-level fields recognized.

### Dimension 2: Scope correctness — 10/10
No scope-mismatched fields (`autoMemoryDirectory`, `disableBypassPermissionsMode`, `claudeMd` all absent or at correct scope).

### Dimension 3: Permission rule syntax — 10/10
All rules use `Tool(pattern)` form. No bare tool names. No quoted-pattern issues.

### Dimension 4: Deny-baseline coverage — 10/10
All canonical baseline patterns present (rm, curl|bash, wget|sh, eval, /etc, ~/.ssh, file://).

### Dimension 5: Env block safety — 10/10
`GITHUB_TOKEN` uses reference syntax `${GITHUB_TOKEN}`. No literal credentials.

### Dimension 6: Lockdown knobs — N/A (10/10)
Not a managed file; lockdown checks don't apply.

### Dimension 7: File hygiene — depends on .gitignore — assumed OK
Note: This is a project `settings.json`; it should be committed. `settings.local.json` (if present alongside) should be gitignored.

### Dimension 8: Output styles — 10/10
Single style named; if `concise` exists as a file, it would be validated separately.

### Dimension 9: Anti-pattern absence — 10/10
None of ST-1 through ST-10 present.

### Dimension 10: Cross-scope interactions — informational only
The fields are at project scope; if managed scope sets the same fields, managed wins. (Cross-file check; not a finding by itself.)

## Total: 100/100 — PASS

## What this calibrates

- Specific scoped allow rules (`Bash(npm test *)`, `WebFetch(github.com)`).
- Complete deny baseline.
- `ask` for unscoped Bash, Write, Edit — prompt-by-default.
- Env vars use reference syntax.
- Output-style entries by name (not absolute path).
