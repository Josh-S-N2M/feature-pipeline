# Good CLAUDE.md: Annotated Example (95+/100)

## Contents

- The file (full source)
- Per-dimension findings
- Total and verdict
- What this calibrates

A CLAUDE.md that scores 95+ across all 10 dimensions. Use as a calibration reference — if the audited CLAUDE.md looks like this, it's probably PASS.

## The file (full source)

```markdown
# Project: User Service

## Tech stack

- Python 3.11+, FastAPI, SQLAlchemy 2.0
- PostgreSQL 15
- pytest + pytest-asyncio for testing
- ruff for formatting and linting

## Coding standards

- Type-hint everything. `mypy --strict` must pass.
- Format with `ruff format`. Check with `ruff check`.
- Async by default for I/O; sync for pure functions.
- No commented-out code; delete it.
- Public functions have docstrings (Google style).

## Workflow

1. Branch from `main`.
2. Run `pytest --cov` before pushing.
3. Open PR; wait for CI green; merge via squash.

## Repository layout

- `src/users/` — User entity + service
- `src/auth/` — Authentication and session
- `tests/` — Mirrors src/ layout
- `migrations/` — Alembic migrations
- `docs/architecture.md` — Architecture overview

## Anti-patterns

Don't:

- Use `print()` for debugging in committed code; use the `logging` module.
- Catch bare `Exception`; specify the type.
- Inline raw SQL; use SQLAlchemy ORM or text() with parameters.
- Commit secrets; use environment variables via `pydantic-settings`.

## Dependencies

See `pyproject.toml`. Don't add a new dependency without team review.

## Testing

- Every endpoint has a test in `tests/integration/`.
- Critical paths have property-based tests via `hypothesis`.
- Mock external services with `respx`; never call real APIs in tests.

@docs/auth-flow.md
```

## Why this scores 95+/100

### Dimension 1: Size & density — 10/10

74 lines. Well under the 200-line guideline. Every line is meaningful.

### Dimension 2: @-import integrity — 10/10

One @-import (`@docs/auth-flow.md`). The path resolves (within the project). No cycles, no excessive depth.

### Dimension 3: Content quality — 10/10

Imperative voice throughout. Specific tools and versions. Concrete rules.

### Dimension 4: Anti-pattern absence — 10/10

No AP-1 (Novel — under 200 lines), AP-2 (no aspirational language), AP-3 (no hardcoded dates), AP-6 (no credentials), AP-7 (no machine-local paths), AP-8 (import resolves), AP-15 (mostly imperative).

### Dimension 5: Rules scope correctness — N/A (10/10)

No `.claude/rules/` audited here.

### Dimension 6: Security — 10/10

No credentials. No private URLs. No exfiltration patterns.

### Dimension 7: Staleness — 10/10

No hardcoded "as of <date>" patterns. Version references (Python 3.11+) are stable.

### Dimension 8: Structure — 10/10

Headings at appropriate depth. Max depth 2 (## H2). Clear sections.

### Dimension 9: Auto-memory hygiene — N/A (10/10)

This file isn't auto memory.

### Dimension 10: Layering interactions — 10/10

No detected duplication with rules/ files (none exist). No overlap with managed CLAUDE.md.

## Total: 100/100 — PASS

## What this calibrates

If the audited CLAUDE.md is comparable to this in scope, structure, and tone, the auditor should not find significant issues. Distinguishing features of this example:

- Imperative voice — "Use X", not "We use X" or "We should consider X".
- Specific tools and versions — not "modern best practices".
- Concrete don'ts — not "be careful with".
- Project-relative paths — not absolute.
- Anti-pattern section uses bulleted "don't" form — clear and scannable.
