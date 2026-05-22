# Content Quality

Writing-quality guidance for CLAUDE.md, rules, and auto memory. Use when scoring dimensions 3 (content quality), 7 (staleness), and 10 (layering interactions).
## Contents

- Three audiences
- Aspirational vs concrete
- Contradictions
- Structure
- Hardcoded dates
- Citation hygiene
- Tone consistency
- The memorable-structure heuristic


## Three audiences

Each file class has a different writer and different quality bars:

| File | Writer | Quality focus |
|---|---|---|
| CLAUDE.md | User | Concise, actionable, no contradictions |
| rules/*.md | User | Scoped to declared paths, focused |
| MEMORY.md (auto) | Claude | Concise summaries, not stream-of-consciousness |
| Topic files (auto) | Claude | One bounded topic each |

The auditor applies different sensitivity. User-written content gets judged on writing quality; Claude-written gets judged primarily on size, structure, and credential safety. The "aspirational language" anti-pattern, for example, doesn't apply to MEMORY.md.

## Aspirational vs concrete

A CLAUDE.md that says "we should consider whether to use TypeScript" gives Claude no rule. A CLAUDE.md that says "use TypeScript with strict tsconfig settings" does.

Aspirational language to flag (MINOR each):

- "we should consider..."
- "it would be nice if..."
- "maybe we'll..."
- "in the future..."
- "we're thinking about..."
- "potentially..."
- "should probably..."

Note: aspirational language is *not* a finding on Claude-written MEMORY.md. Claude's tone may be tentative when reporting observations ("the auth flow seems to be using session cookies") — that's legitimate uncertainty, not aspirational rule-setting.

## Contradictions

Two rules that conflict produce non-deterministic Claude behavior. The auditor catches contradictions by:

1. Detecting opposing modal verbs on the same subject ("always X" + "never X"; "must Y" + "must not Y").
2. Detecting opposing technology choices ("use TypeScript" + "use JavaScript"; "use REST" + "use GraphQL").
3. Detecting opposing style rules ("use tabs" + "use spaces").

Each detected contradiction is MAJOR.

## Structure

CLAUDE.md benefits from heading hierarchy:

- Top-level `#` is the project name or "Rules for [project]".
- `##` for major sections (Tech stack, Coding standards, Workflow).
- `###` for specific topics.

A CLAUDE.md with zero headings — just a long flat list — is MINOR.

A CLAUDE.md whose headings don't match the table of contents (if one is present) — MINOR.

## Hardcoded dates

CLAUDE.md often has "as of <date>" notes. These age:

- "As of August 2025" with a current date of May 2026 — flag MINOR with note "potential staleness; verify still accurate."
- "Before August 2025, use the old API. After August 2025, use the new API." — flag MINOR if it's now well past the cutover.
- Versioned references ("for Python 3.11+", "for v2 of the API") — not flagged. Versions are stable identifiers; dates aren't.

## Citation hygiene

CLAUDE.md sometimes cites project files. For example:

```audit-example -- content-quality anti-pattern reference demonstrating scanner-flagged content; documents what the auditor scanner detects
See the auth implementation at src/auth.py.
```

If the file moves or is deleted, the citation goes stale.

The auditor:

1. Extracts file-path citations from CLAUDE.md (paths in backticks, paths after "see", "in", "at", or in `@`-imports).
2. Checks each path exists on disk.
3. MINOR for each missing path.

## Tone consistency

A CLAUDE.md mixing first-person ("I prefer...") and imperative ("Use TypeScript") works fine for Claude but reads inconsistently. NIT only.

A CLAUDE.md alternating between "you" (addressing Claude) and "we" (project team) gets confusing. NIT.

## Length-density tradeoff

A 100-line CLAUDE.md with every line meaningful is excellent. A 100-line CLAUDE.md with 60 lines of preamble and 40 lines of actual rules is a bad use of context.

Pragmatic test: does each section have ≥ 1 actionable rule? If a section is pure narrative, MINOR.

## The "memorable structure" heuristic

A good CLAUDE.md follows a memorable structure. Common patterns:

- Tech stack → Coding standards → Workflow → Testing → Deployment
- Quick reference → Detailed rules → Conventions → Anti-patterns
- Project basics → Module-specific → Cross-cutting

A CLAUDE.md that just appends new rules to the bottom over time loses structure. MINOR.

## What good looks like

```audit-example -- content-quality anti-pattern reference demonstrating scanner-flagged content; documents what the auditor scanner detects
# Project: Auth Service

## Tech stack

- Python 3.11+
- FastAPI
- PostgreSQL via SQLAlchemy
- pytest for testing

## Coding standards

- Type-hint everything. `mypy --strict` must pass.
- Format with `ruff`.
- No commented-out code; remove or delete.
- Docstrings on public functions.

## Workflow

1. Branch from `main`.
2. Run tests before committing: `pytest --cov`.
3. Open PR; wait for CI green; merge via squash.

## Anti-patterns

- Don't use `print()` for debugging in committed code; use `logging`.
- Don't catch bare `Exception`; specify the type.
```

Each line is actionable. No aspiration. Clear structure.

## What bad looks like

```audit-example -- content-quality anti-pattern reference demonstrating scanner-flagged content; documents what the auditor scanner detects
# About this project

This is a project that we started a while ago. We've been working on it
for some time now. The original idea was to build a system that does some
things, and we've added more features along the way.

The team thinks we should probably use modern best practices when we can.
We're considering moving to TypeScript at some point but we haven't decided
yet. For now we use JavaScript but we should think about whether to switch.

Some files use async, some don't. We should clean this up eventually.
```

No actionable rules. Lots of "should" and "thinking about". The reader (Claude) cannot extract a behavioral rule.
