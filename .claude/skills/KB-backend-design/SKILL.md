---
name: kb-backend-design
description: >-
  Design discipline for the Backend layer — the service-side logic that
  implements domain rules, orchestrates persistence, and serves the API. Covers
  service boundaries, persistence patterns, transaction semantics, idempotency,
  domain modeling, error contracts, observability, and the per-layer designer's
  workflow for producing the Backend Design subsection of a Blueprint. Use when
  the feature touches server-side application logic. Pairs with KB-api-design
  (the contract the Backend serves), KB-query-design (the data-access layer
  the Backend consumes), and KB-general-coding-principles.
allowed-tools: Read, Grep, Glob
---

# KB-backend-design — Backend Layer Design Discipline

Design discipline for the Backend layer. The per-layer Backend Designer (`design-backend`) loads this KB during per-layer Design to produce the `### Backend Design` subsection of the Blueprint. Like Frontend, this is design-discipline-only — there is no platform partner KB because backend platforms vary widely (Go, Java/Kotlin, Python, Node, Rust, Ruby, .NET, Elixir, etc.) and the discipline is largely language-agnostic.

## Contents

- When this KB is loaded
- The layer's responsibility
- Design decisions this layer owns
- Patterns and anti-patterns at a glance
- Interaction with other layers
- Surfacing architectural questions
- When to load each reference file

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Backend** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the Backend Design subsection of the Blueprint
- Plan Authoring produces tasks that touch service-side application logic
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include Backend Design

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-backend` (per-layer Design, when Backend layer is in scope)
- `design-composer` (Design Composition, integrating Backend design with cross-cutting concerns)
- `plan-author` (when tasks touch backend services)
- `shared-document-reviewer` (Gate 1 Backend-specific checks)
- `review-architecture-auditor` (CoVe checks on Backend claims)

For language- or framework-specific knowledge (Spring idioms, Django patterns, Express middleware, etc.), Backend Designers consult the Synthesis output of the current pipeline run.

## The layer's responsibility

The Backend layer implements the domain logic of the application. It owns:

- **Domain rules** — what's allowed, what's required, what's invariant. The rules a user can't break without breaking the business model.
- **Orchestration** — sequencing across multiple data sources, external services, and side effects so the system reaches a consistent state.
- **Transaction semantics** — what's atomic together, what's eventually consistent, what's idempotent.
- **Error models** — what kind of failure can happen, what the caller can do about each, how the system recovers.
- **Observability** — what gets logged, what gets metricized, what gets traced; the postmortem-ability of the service.

The Backend layer does NOT own:

- The wire contract — that's the API layer (`KB-api-design`). The Backend implements behavior; the API exposes it.
- The SQL — that's the Query layer (`KB-query-design`). The Backend asks the Query layer for data; the Query layer decides how to fetch it.
- The schema — that's the Database layer (`KB-database-design`). The Backend reads from the Query layer; the Query layer reads from the Database.
- The deployment — that's CI/CD (`KB-github-actions-platform` / `KB-github-actions-design`) and IaC (`KB-iac-design`).

## Design decisions this layer owns

The Backend Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Service granularity (monolith / modular monolith / services / microservices) | The feature affects multiple bounded contexts; team independence matters |
| Language / framework | Greenfield; brownfield usually inherits |
| Module / package layout (hexagonal, layered, vertical-slice, package-by-feature) | The codebase has >~10 modules |
| Domain modeling style (anemic data + service, rich domain objects, event sourcing) | Domain rules are non-trivial |
| Transaction boundaries (single DB tx, saga, two-phase commit, outbox pattern) | Multiple data stores or external services participate |
| Idempotency strategy (idempotency keys, natural keys, tombstones) | Mutations are retried at any layer |
| Error model (exceptions / errors-as-values, error envelopes, fault categories) | The service has more than one failure mode |
| Concurrency model (sync / async / actor / channels) | Throughput or latency constraints push past sync |
| Background work (cron, queue, scheduler) | Non-request-driven processing exists |
| Authentication / authorization (where checks live; how identity propagates) | Any non-public endpoint |
| Logging / metrics / tracing baseline | The service is non-trivial |
| External-service interaction (timeout, retry, circuit-breaker policies) | Any external call is made |

Designers do NOT author ADRs (per FR-5 in Blueprint v4.3.1). Cross-cutting decisions (e.g., the system-wide error model, the canonical idempotency mechanism) get surfaced as open items in the per-layer output's "Architectural Questions for Composer" section.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Bounded context per service** — one team's invariants don't leak into another team's. Even within a monolith, modules respect bounded-context boundaries.
- **Hexagonal / ports-and-adapters** — domain logic at the core, adapters at the edges. External dependencies (DB, queue, HTTP client) sit behind interfaces the domain owns.
- **Idempotent mutations by default** — every mutating endpoint supports safe retry. Either the operation is naturally idempotent or it accepts an idempotency key.
- **Outbox pattern for "DB change + external event"** — writing to the DB and emitting a Kafka/SQS event atomically requires the outbox; otherwise you get inconsistency.
- **Domain events at module boundaries** — modules communicate via events, not direct calls, when independence matters.
- **Errors as first-class** — typed errors (or error envelopes) with documented categories (`validation`, `not_found`, `conflict`, `unavailable`, `internal`). Generic 500s are a failure of the design.
- **Tracing context flowing through every async boundary** — request ID, trace ID, span ID propagated explicitly.

**Anti-patterns to flag:**

- **God service** — one service touches every bounded context.
- **Leaky abstractions** — the domain layer imports the ORM directly; SQL details bleed into business code.
- **Transactions that span HTTP calls** — locks held while waiting for a remote system.
- **Catch-all `except Exception`** without re-raising — swallowed failures.
- **Mutations without idempotency** — retries cause duplicate side effects.
- **"Just queue it"** without thinking about ordering, retries, and dead-letter handling.
- **Logging at error severity for normal control flow** — alert fatigue.

## Interaction with other layers

The Backend layer's typical position:

```
Frontend ──► API ──► [Backend] ──► Query ──► Database
                          │
                          ├──► External services (auth, mail, payment)
                          ├──► Queue / event bus
                          └──► Background workers
```

The Backend Designer's responsibility:

- **API (downstream)** — the Backend implements what the API exposes. The Backend Designer should NOT design the API contract; they may surface needed API changes via `dependencies_on_other_layers`.
- **Query / Database (upstream)** — the Backend consumes the Query layer's interface. Coupling to specific SQL or ORM details from inside Backend code is a smell (use the repository pattern; let the Query layer own the SQL).
- **CI/CD and IaC** — deploy concerns belong to those layers. The Backend Designer documents *what configuration the service needs* (env vars, secrets, scaling expectations); the CI/CD and IaC designers turn that into deployable infrastructure.
- **Frontend** — no direct relationship. Frontend ↔ Backend coupling happens via the API layer.

## Surfacing architectural questions

The Backend Designer cannot author ADRs (per FR-5). Surface decisions that warrant an ADR via:

```markdown
## Architectural Questions for Composer

- **Q-BE-1**: Should we adopt a unified error envelope (`{ code, message, retriable, details }`) across all services? The choice affects API design (HTTP status codes vs. envelope), Frontend's error rendering, and observability (whether errors are categorized in metrics). Evidence: 4 of the 9 services in scope currently use ad-hoc error shapes; new feature creates a 5th. Options: (a) adopt RFC 7807 Problem Details; (b) custom envelope; (c) let each service define its own. Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a Backend Design subsection — covers the foundational principles (bounded contexts, hexagonal architecture, idempotency, error contracts, observability, transaction semantics) |
| `references/patterns-and-anti-patterns.md` | Choosing between competing service-boundary / persistence / transaction approaches — covers common patterns with when-to-use, and the anti-patterns reviewers should flag |
