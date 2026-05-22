# Permission Rules Specification

## Contents

- The permissions object shape
- Rule precedence: ask > deny > allow
- Rule syntax
- The deny baseline
- Tool-scoped permission patterns
- Common mistakes

## Source

`code.claude.com/docs/en/permissions`, last verified 2026-05.

## The permissions object

The `permissions` object configures which tool invocations require approval, which are auto-allowed, and which are auto-denied:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "permissions": {
    "allow": [
      "Read(./**)",
      "Grep(**/*.py)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "deny": [
      "Bash(rm -rf /*)",
      "Bash(curl * | bash)",
      "Write(/etc/**)",
      "WebFetch(*)"
    ],
    "ask": [
      "Bash(*)",
      "Write(**)",
      "Edit(**)"
    ]
  }
}
```

## Rule precedence

For each tool call, Claude Code checks rules in this order:

1. **`deny` first.** If any deny rule matches, the call is rejected.
2. **`ask` next.** If any ask rule matches, the user is prompted.
3. **`allow` last.** If any allow rule matches, the call proceeds without prompting.
4. **Default:** if no rule matches, the call is denied (or auto-allowed in `acceptEdits` mode for edits).

This precedence is `deny > ask > allow`. Putting a permissive `Bash(*)` in `allow` doesn't override a specific `Bash(rm -rf *)` in `deny` — the deny wins.

## Rule syntax

Each rule is a string in the format `<Tool>(<scope>)`:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
Bash(git diff *)        # Bash where arg pattern is "git diff *"
Read(./src/**)          # Read where path matches ./src/**
Edit(*.py)              # Edit where target is *.py
WebFetch(github.com)    # WebFetch where domain is github.com
WebFetch(*.example)     # WebFetch where domain matches *.example
```

- `Tool` is one of: Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch, NotebookEdit
- Scope is a glob pattern. `*` matches non-slash; `**` matches anything including slashes.
- For Bash, scope is the **command pattern** (matched against the literal command string).
- For Read/Write/Edit, scope is the **path pattern**.
- For WebFetch, scope is the **domain pattern**.

### Common syntax mistakes

- `Bash("git diff")` — quotes inside parens are treated as part of the literal pattern. Won't match `git diff` without quotes. MAJOR.
- `Bash(git diff)` (no `*`) — matches only the literal `git diff`, not `git diff HEAD`. Probably the author wanted `Bash(git diff *)`. MAJOR.
- `Read(/abs/path)` — absolute path; works only on machines with that exact path. MAJOR if at project scope.
- `Bash` (no parens at all) — matches all Bash calls; same as `Bash(*)`. MAJOR — over-broad.

## The deny baseline

In `--managed` mode (enterprise), the auditor checks that the deny list covers the canonical safety patterns:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
- Bash(rm -rf /*)          # Filesystem destruction at root
- Bash(rm -rf ~)            # Wipe home directory
- Bash(curl * | bash)       # Download-and-execute
- Bash(wget * | sh)         # Same
- Bash(eval *)              # Arbitrary code execution
- Write(/etc/**)            # System config modification
- Write(~/.ssh/**)          # Credential file write
- WebFetch(file://*)        # Local file via URL bypass
```

Coverage of all of these = deny baseline OK. Missing any = MINOR each in `--managed` mode (the user might intend a different baseline).

## Tool-scoped permission patterns

Different tools have different scope semantics:

| Tool | Scope is | Example |
|---|---|---|
| Read | path glob | `Read(./src/**)` |
| Write | path glob | `Write(/tmp/**)` |
| Edit | path glob | `Edit(*.py)` |
| Bash | command pattern | `Bash(git diff *)` |
| Grep | path glob | `Grep(**/*.py)` |
| Glob | path glob | `Glob(**/*.json)` |
| WebFetch | domain pattern | `WebFetch(github.com)` |
| WebSearch | (none — bare `WebSearch` allows) | `WebSearch` |
| NotebookEdit | path glob | `NotebookEdit(notebooks/**)` |

## Common rule-design mistakes

- **Permissive default.** `allow: ["Bash(*)"]` is functionally "approve any shell command". MAJOR — the user is one typo away from disaster.
- **Redundant ask.** Same pattern in `ask` and `allow`. Deny precedence means ask wins; user gets prompted. MINOR.
- **Allowed `WebFetch(*)`.** No domain scoping = approve any outbound HTTP. MAJOR.
- **Empty arrays.** `"deny": []` is dead config. MINOR.
- **Missing deny for known-bad.** No `Bash(rm -rf *)` in deny. In `--managed` mode, MINOR per baseline-item.

## Diagnostic commands

```
/permissions
```

Shows the effective permission rules after scope merging. Useful for verifying that a deny rule isn't shadowed by a higher-scope override.
