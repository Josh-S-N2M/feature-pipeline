# Anti-Patterns (CLAUDE.md and Rules)

The 15 named anti-patterns the auditor looks for in user-written context files. Use when scoring dimension 4 (anti-pattern absence).
## Contents

- How to read this catalog
- The 15 patterns
- Severity calibration


## How to read this catalog

Each entry has an ID (AP-1 through AP-15), severity, symptom, why it's bad, and fix.

Severities:

- **MAJOR** — actively degrades Claude's behavior.
- **MINOR** — wastes context tokens or signals neglect.

The patterns described in this file are **illustrative** — they describe what to detect. The literal phrases shown in the example blocks are intentionally pattern-matched by the auditor's content-quality scripts so they can be tested.

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
This is a marker for the file-level pedagogical declaration.
```

## The 15 patterns

### AP-1: The Novel — MAJOR

Symptom: CLAUDE.md is hundreds of lines of background, history, architecture narrative.

Why bad: Loads into every session. Costs tokens. Provides no actionable rules.

Fix: Move narrative to README.md. Keep CLAUDE.md to rules.

### AP-2: Wish List — MAJOR

Symptom: "We're planning to migrate to X." "We should consider Y."

Why bad: Aspirational; Claude can't apply. Often becomes stale (the migration happens and CLAUDE.md never updates).

Fix: Either commit to the rule and use imperative voice, or remove until decided.

### AP-3: Stale Instructions — MAJOR

Symptom: "As of August 2025, use the new API" — and it's now May 2026.

Why bad: Claude follows the stale rule.

Fix: Update or remove dated instructions when they age out.

### AP-4: Direct Contradiction — MAJOR

Symptom: One section says "always use TypeScript"; another says "JavaScript for scripts."

Why bad: Claude picks non-deterministically.

Fix: Resolve the contradiction, or scope each rule to the appropriate file pattern.

### AP-5: The README Twin — MINOR

Symptom: CLAUDE.md replicates README.md content.

Why bad: Loads README content into every session. Tokens wasted.

Fix: README is for humans; CLAUDE.md is for Claude. Different audiences, different content.

### AP-6: Credentials In Plain Text — BLOCKER (security_critical)

Symptom: A literal API key, token, or password value in CLAUDE.md.

Why bad: Credentials should be in env vars or a secret manager. Embedding in a file means they're version-controlled.

Fix: Remove. Rotate the credential. Reference the env var name instead.

### AP-7: Path Hardcoding — MAJOR

Symptom: `/home/alice/projects/foo/` or `C:\\Users\\Bob\\...` in CLAUDE.md.

Why bad: Breaks for other contributors.

Fix: Use relative paths or `${PROJECT_ROOT}`.

### AP-8: Broken @-imports — MAJOR

Symptom: `@docs/architecture.md` but the file doesn't exist.

Why bad: Silent empty include — the user thinks the content is loaded but it isn't.

Fix: Create the file, fix the path, or remove the import.

### AP-9: Excessive Nesting — MINOR

Symptom: Headings 5+ levels deep.

Why bad: Readers (Claude included) lose track.

Fix: Flatten — promote subsections or move them to a referenced file.

### AP-10: Repetition Across Scopes — MINOR

Symptom: Same rule appears in user CLAUDE.md and project CLAUDE.md.

Why bad: Loaded twice. Tokens wasted.

Fix: Keep one canonical location.

### AP-11: Cargo-Culted Rules — MINOR

Symptom: Rules copied from another project that don't apply here (e.g. "use Bazel" in a project that uses npm).

Why bad: Confuses Claude when the actual setup contradicts the rule.

Fix: Audit and remove rules that don't apply.

### AP-12: Inline Code Without Language — MINOR

Symptom: Triple-backtick code fences with no language tag.

Why bad: Loses Claude's syntax-awareness hint.

Fix: Add language tag (`python`, `typescript`, `bash`, etc.).

### AP-13: Out-of-scope Rule — MAJOR

Symptom: a `.claude/rules/<lang>-rules.md` file with a language-specific `paths:` glob contains universal rules. Example:

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
---
description: TypeScript rules
paths:
  - "**/*.ts"
---

# Git workflow conventions
- Branch from main.
- Squash-merge.
```

The TypeScript-scoped rule file contains Git rules that should apply universally.

Why bad: Loads the universal rules only when TS files are touched; misses other tasks.

Fix: Move universal rules to CLAUDE.md; keep rule files scoped to their declared paths.

### AP-14: Override-Style Phrasing in Additive Context — MINOR

Symptom: "This file overrides anything else" in a CLAUDE.md.

Why bad: CLAUDE.md is additive — there's no override. The author misunderstands the loading model.

Fix: Re-phrase as additive guidance, or move conflicting rules to a more specific location.

### AP-15: First-Person Plurality — NIT

Symptom: "We at Acme prefer..." or "Our team uses..."

Why bad: Slightly confusing — who is "we"? Doesn't reduce Claude's ability to follow the rule but signals the file is written for humans not Claude.

Fix: Imperative voice — "Use X" rather than "We use X".

## Severity calibration

Single AP-1 alone might score the file MAJOR. Three AP-2/3 instances probably mean a major rewrite. Any AP-6 is SECURITY-BLOCK.

The auditor's content-quality scripts detect AP-1, AP-2, AP-3, AP-4, AP-6, AP-7, AP-8, AP-12 deterministically. The remainder (AP-5, AP-9–11, AP-13–15) need agent judgment after reading the file.
