<!--
Rules live in .claude/rules/*.md (project) or ~/.claude/rules/*.md (user).
Subdirectories are discovered automatically: .claude/rules/frontend/react.md works.

Two flavors:
  1. No `paths:` frontmatter  → loads at every session start, like CLAUDE.md
  2. With `paths:` frontmatter → loads only when Claude reads a file matching the globs

This file shows both. In a real setup, each rule lives in its own file.
Below are three examples separated by `===`.
-->

## In this file

- Example 1 — Unconditional rule (project-wide security guidelines)
- Example 2 — Path-gated rule for test files (testing conventions)
- Example 3 — Path-gated rule for API directory (API design conventions)

=== EXAMPLE 1: Unconditional rule (.claude/rules/security.md) ===

---
description: Project-wide security guidelines applied to all code
---

# Security rules

## Secrets and credentials

- Never hard-code API keys, tokens, passwords, or connection strings
- Read all secrets from environment variables via `process.env`
- Validate that required env vars exist at boot; fail fast if missing
- Never log secret values (mask all but last 4 characters)

## Input validation

- Validate all external input with Zod schemas before use
- For user-facing forms: validate on the client and re-validate on the server
- For database queries: use parameterized queries, never string concatenation
- For file paths from user input: resolve and verify within an allowed root

## Authentication

- All non-public routes require an auth check at the route handler boundary
- Tokens expire after 24 hours; refresh tokens rotate on each use
- Hash passwords with argon2id (preferred) or bcrypt with cost ≥ 12

## Logging

- Use the structured logger from `src/lib/log.ts`
- Log levels: debug (dev only), info, warn, error
- Never log secrets, full request bodies, or PII unless explicitly required and approved


=== EXAMPLE 2: Path-gated rule (.claude/rules/testing.md) ===

---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/__tests__/**"
description: Test conventions, only loaded when test files are in context
---

# Testing rules

## Naming

- Test names follow "should [expected behavior] when [condition]"
- Group related tests with `describe()`; one describe per public function
- Top-level describe matches the module name being tested

## Structure

- Use AAA pattern: Arrange, Act, Assert — separated by blank lines
- One assertion concept per `it()` block (multiple `expect()` calls are fine if they describe the same concept)
- No conditional logic inside tests (`if`, `for`, `try/catch`) — extract to helpers

## Mocking

- Mock at module boundaries (HTTP, DB, filesystem) — never mock internal modules
- Use `vi.mock()` with a factory function; reset mocks in `afterEach`
- For dates: use `vi.useFakeTimers()` and `vi.setSystemTime()` rather than mocking `Date`

## Cleanup

- Clean up side effects in `afterEach`: timers, listeners, DOM nodes
- For Testing Library: use `cleanup()` automatically (configured globally)
- For database tests: use transactions that roll back, not setup/teardown


=== EXAMPLE 3: Path-gated rule for an API directory (.claude/rules/api-design.md) ===

---
paths:
  - "src/api/**/*.ts"
description: API route conventions, loaded when working in src/api
---

# API design rules

## Response shape

- All endpoints return `{ data: T } | { error: string, code: string }`
- Never throw across the route handler boundary — catch and return error shape
- HTTP status codes: 200 for success, 400 for validation, 401 for unauth, 403 for forbidden, 404 for not found, 500 only for unexpected errors

## Validation

- Validate all input with Zod schemas at the top of the handler
- Reject with 400 and a list of field-level errors on validation failure
- Validate path params, query params, and body separately

## Rate limiting

- All public endpoints must use the rate limiter middleware
- Default: 60 req/min per IP
- Auth endpoints: 10 req/min per IP

## Documentation

- Every endpoint has a JSDoc comment with: purpose, auth requirement, rate limit, request shape, response shape
- Update the OpenAPI spec in `src/api/openapi.ts` when adding or changing endpoints
