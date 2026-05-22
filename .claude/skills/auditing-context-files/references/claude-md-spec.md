# CLAUDE.md Specification

Authoritative reference for the structure and constraints of CLAUDE.md and its variants. Use when scoring dimensions 1, 2, and 8.
## Contents

- File locations and precedence
- Size guideline
- @-imports
- Structural constraints
- Hardcoded dates
- Managed CLAUDE.md
- Verification commands


## Source

`code.claude.com/docs/en/memory`, last verified 2026-05.

## File locations & precedence

CLAUDE.md is loaded **additively** from multiple scopes — all loaded files contribute simultaneously. There is no override.

| Path | Scope | Committed? |
|---|---|---|
| `~/.claude/CLAUDE.md` | User-global | No (user's home) |
| `<project>/CLAUDE.md` | Project | Usually yes |
| `<project>/.claude/CLAUDE.md` | Project (Anthropic-internal convention) | Usually yes |
| `<project>/CLAUDE.local.md` | Project local | **Must be in .gitignore** |
| `~/CLAUDE.md` | Enterprise-level user file | Per organization policy |

When multiple files are present, content concatenates. There is no de-duplication. Two files saying the same thing waste tokens.

## Size guideline

**The 200-line guideline.** Anthropic recommends CLAUDE.md stay under 200 lines. This is a guideline, not a hard limit — but every line is loaded into context at every session start. Bloated CLAUDE.md is the #1 cause of context-budget overflow.

Audit thresholds:

- ≤ 200 lines: clean.
- 201–500 lines: MINOR — "exceeds 200-line guideline; review for trimming."
- 501–1000 lines: MAJOR — "significantly exceeds guideline; risks context budget."
- > 1000 lines: BLOCKER — "CLAUDE.md is so large it consumes a substantial fraction of every context window."

CLAUDE.local.md is subject to the same guideline.

## @-imports

Files can include other files via `@`-prefixed paths:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
See @docs/architecture.md for the system design.

Authentication: @./auth-rules.md
```

The path resolves relative to the importing file. Imported content is inlined into the loaded context.

### Constraints

- **Max depth: 5.** A imports B imports C imports D imports E imports F → F is silently dropped or the chain errors (behavior version-dependent). Depth > 5 is BLOCKER.
- **No cycles.** A → B → A causes infinite expansion or error. BLOCKER.
- **Path must exist.** Missing target = silently empty include. MAJOR.
- **Path must be within project (or user's CLAUDE.md scope).** Absolute path to a teammate's home directory works on one machine, breaks for everyone else. MAJOR.

### Validation script

`scripts/validate_at_imports.py` traverses @-imports recursively, detects cycles, and flags missing targets.

## Structural constraints

CLAUDE.md is markdown, but Claude treats certain patterns specially:

- **Headings (`#`, `##`)** delineate sections. Heading hierarchy gives Claude a navigable structure.
- **Bullet lists** are read as rule lists.
- **Code fences** are read as examples (do not get treated as prose instructions).
- **Tables** are read as reference data.

A CLAUDE.md with no headings is harder to navigate. MINOR.

A CLAUDE.md with contradictory rules (e.g. "always use TypeScript" + "always use JavaScript") will produce non-deterministic behavior. MAJOR.

## Hardcoded dates

CLAUDE.md often contains "as of <date>" or "before <date>". These age badly. If the file says "As of August 2025" and it's now May 2026, the rule may be stale. MINOR with note. Not BLOCKER (the user may want hardcoded dates for explicit transitions).

## Managed CLAUDE.md (enterprise)

Managed-settings.json can inject CLAUDE.md content via the `claudeMd` field. This appears at the bottom of the loaded memory and cannot be overridden by project or user CLAUDE.md. Audit the managed injection separately from the project's own CLAUDE.md.

## What good CLAUDE.md looks like

- Concise, action-oriented.
- Clear rules (do this, don't do this).
- No "About this project" essays — that's README's job, not CLAUDE.md's.
- Concrete examples in code fences.
- Updated when project conventions change.
- No credentials, API keys, or absolute paths.

See `examples/good-claude-md-annotated.md` for a scoring-95+ example.

## What bad CLAUDE.md looks like

- 500+ lines of narrative prose.
- Conflicting rules ("always use X" + "never use X").
- Aspirational language ("we should consider trying...").
- @-imports to files that don't exist.
- Credentials in plain text.
- Machine-local paths (`/home/alice/...`).

See `examples/bad-claude-md-annotated.md` for an annotated FAIL.

## Verification commands

After modifying the file, the user should run:

```
/memory
```

This shows what Claude has actually loaded — exposes @-import resolution failures, .gitignore problems with CLAUDE.local.md, and reveals when project vs user CLAUDE.md merge unexpectedly.
