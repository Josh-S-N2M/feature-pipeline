# Rules Specification

Authoritative reference for `.claude/rules/*.md` files — Claude Code's conditional rule mechanism. Use when scoring dimensions 5 (rules scope correctness) and 10 (layering interactions).
## Contents

- What rules are
- File shape
- Glob syntax and mistakes
- Loading behavior
- Scope correctness
- Overlap with CLAUDE.md
- Anti-patterns specific to rules


## Source

`code.claude.com/docs/en/memory#rules`, last verified 2026-05.

## What rules are

A file at `.claude/rules/<name>.md` is a **conditional CLAUDE.md fragment** that loads only when its `paths:` frontmatter glob matches a file relevant to the current task. Rules let projects keep CLAUDE.md focused on universal guidance while still applying file-type-specific or directory-specific guidance.

## File shape

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
---
description: TypeScript-specific rules
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript rules

- Use the project's tsconfig strict settings.
- Never `any` without an explanatory comment.
- Prefer `unknown` over `any` for untyped data.
```

Frontmatter fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `description` | string | recommended | What this rule covers (shown in `/memory`) |
| `paths` | list of globs | yes | When to load |

Body is markdown — same conventions as CLAUDE.md but typically shorter (single focused topic).

## Glob syntax

Globs use standard `**`, `*`, `?` patterns:

- `**/*.ts` — any .ts file anywhere
- `src/**/*.py` — any .py file under src/
- `tests/**` — anything under tests/
- `package.json` — exact filename match anywhere

### Common glob mistakes

- **Missing leading `**/`.** `*.ts` only matches at the repo root — usually not intended. MAJOR.
- **Backslash escapes.** `**\*.ts` is Windows syntax that doesn't match on Unix. MAJOR.
- **Trailing slash on file pattern.** `**/*.ts/` matches directories named `.ts`, not files. MAJOR.
- **Empty paths list.** Rule never loads. BLOCKER.

`scripts/glob_validator.py` validates the syntax and warns on common mistakes.

## Loading behavior

When Claude prepares context for a task:

1. Identifies files relevant to the task (the ones being edited, read, or referenced).
2. For each rules file in `.claude/rules/`, evaluates `paths:` against those files.
3. If any match, loads the rule into context.
4. If no rule matches, the rule is silently not loaded.

Loaded rules concatenate to CLAUDE.md content — they don't replace it.

## Scope correctness

A rule's content should match its `paths` declaration:

- A rule with `paths: "**/*.ts"` should contain TypeScript-specific guidance, not universal rules.
- A rule with universal guidance (like coding standards) belongs in CLAUDE.md, not in a rules file.
- A rule with no clear scope is a smell — either move to CLAUDE.md or scope its paths properly.

Audit rule: if the body refers to a language/framework/file-type that the `paths:` glob doesn't actually scope, MINOR finding "scope mismatch between rule content and paths declaration."

## Overlap with CLAUDE.md

A rule duplicating content from CLAUDE.md is double-loaded for matching files — wasted tokens. Cross-file check X7 catches this.

## Maximum number of rules

No hard limit. Each rule's content adds to context only when it matches. Many rules with non-overlapping path scopes is fine. Many rules with overlapping scopes is the same problem as a bloated CLAUDE.md.

Practical guidance: more than 10 rules total is a smell. Consider whether the project has too many idiosyncratic rules, or whether the rules should be consolidated.

## Anti-patterns specific to rules

- **Always-loaded rule.** `paths: "**/*"` — loads on every task. This is equivalent to CLAUDE.md content; move it there.
- **Never-loaded rule.** `paths` glob doesn't match anything in the project. BLOCKER if the project is otherwise complete.
- **Description-as-rule.** The `description:` field is metadata for `/memory` display; putting rules into description doesn't apply them. BLOCKER if the body is empty and the rules are in description.
- **Contradicts CLAUDE.md.** Rule says X for TS files; CLAUDE.md says not-X for all files. MAJOR — Claude must choose, behavior is non-deterministic.

## Diagnostic commands

```
/memory
```

Shows which rules are currently loaded for the active task. Reveals empty bodies, missing files, and broken globs by their absence from the output.

## What good rules look like

- Short — under 100 lines.
- Specific to the scope declared in `paths`.
- Use code fences for examples in the relevant language.
- Don't duplicate CLAUDE.md.

## What bad rules look like

- Empty bodies (description has the content; rules don't load from description).
- Universal content with no scope justification.
- Overlap with CLAUDE.md.
- Path globs that never match.
