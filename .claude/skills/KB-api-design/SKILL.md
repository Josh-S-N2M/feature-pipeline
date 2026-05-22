---
name: kb-api-design
description: >-
  Design discipline for the API layer — the wire contract between clients
  (Frontend, third parties, internal services) and Backend services. Covers
  contract style (REST / GraphQL / gRPC), versioning, error envelopes,
  idempotency contracts, authentication and authorization models, pagination,
  rate limiting, and the per-layer designer's workflow for producing the API
  Design subsection of a Blueprint. Use when the feature touches an externally
  observable interface. Pairs with KB-backend-design (the implementation side)
  and KB-frontend-design (the typical consumer).
allowed-tools: Read, Grep, Glob
---

# KB-api-design — API Layer Design Discipline

Design discipline for the API layer. The per-layer API Designer (`design-api`) loads this KB during per-layer Design to produce the `### API Design` subsection of the Blueprint. Design-discipline-only; specific protocols (HTTP/REST, GraphQL, gRPC) are platform-level concerns the Designer pulls from Synthesis output of the current run as needed.

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

- A feature's PRD or Blueprint declares the **API** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the API Design subsection of the Blueprint
- Plan Authoring produces tasks that touch endpoint definitions, schemas, or contract docs
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include API Design

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-api` (per-layer Design, when API layer is in scope)
- `design-composer` (Design Composition, integrating API design with cross-cutting concerns)
- `plan-author` (when tasks touch API contracts)
- `shared-document-reviewer` (Gate 1 API-specific checks)
- `review-architecture-auditor` (CoVe checks on API claims)

## The layer's responsibility

The API layer is the contract between clients and the system. It owns:

- **The wire format** — the bytes on the wire: paths, methods, headers, request bodies, response bodies, status codes.
- **The contract** — what's allowed, what's required, what's optional. The schema clients can rely on.
- **The error envelope** — how failures are communicated and what callers can do about each.
- **Versioning and evolution** — how the contract changes over time without breaking existing clients.
- **The authentication and authorization surface** — how identity arrives at the endpoint and what's required to access each operation.
- **Cross-cutting policies** — rate limiting, pagination, idempotency contracts, deprecation announcements.

The API layer does NOT own:

- The implementation — that's the Backend layer (`KB-backend-design`). The API is a contract; the Backend fulfills it.
- The data shape at rest — that's the Database (`KB-database-design`) via the Query layer. API responses often differ from DB rows; that's by design.
- The client — the Frontend Designer is a consumer of this API but doesn't dictate its shape (negotiated, not imposed).

## Design decisions this layer owns

The API Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Contract style (REST / GraphQL / gRPC / hybrid) | A new API is introduced or restructured |
| Resource model (REST) or schema (GraphQL) or service definitions (gRPC) | New endpoints / queries / RPCs are added |
| Versioning strategy (URL path / header / never-break) | Breaking changes are anticipated |
| Authentication mechanism (Bearer / OAuth / mTLS / API key / signed requests) | Any non-public endpoint |
| Authorization model (RBAC / ABAC / scoped tokens / per-resource policies) | Multi-actor access patterns |
| Error envelope (RFC 7807 Problem Details / custom envelope / native protocol errors) | Any non-trivial endpoint |
| Idempotency contract (which methods, what key, what window) | Mutating endpoints exist |
| Pagination style (cursor / offset+limit / page+size) | Listing endpoints exist |
| Rate limiting (per-actor, per-endpoint, per-tenant; token bucket / leaky bucket) | Public or high-volume endpoints |
| Deprecation policy (sunset header, deprecation announcements, retention windows) | Long-lived API; clients can't be coordinated |
| Documentation format (OpenAPI / GraphQL SDL / gRPC proto / hand-written) | Any API |

Designers do NOT author ADRs (per FR-5). Cross-cutting API decisions (the canonical error envelope, the system-wide auth model) get surfaced as open items in "Architectural Questions for Composer."

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Generated docs are the docs.** OpenAPI / GraphQL SDL / gRPC proto generated from (or matched to) the implementation, not hand-maintained.
- **Stable error envelope across the API.** RFC 7807 Problem Details or a documented custom envelope. Every error has `code`, `message`, and `retriable`. Categories are finite and documented.
- **Idempotency-Key header for retry-safe mutations.** Server stores `(key, response)` for a 24h–7d window.
- **Cursor pagination for unbounded lists.** Stable under inserts and deletes; offset pagination is broken under concurrent writes.
- **Pessimistic versioning.** Treat the first stable release as v1; never break v1 silently. Add v2 with parallel maintenance, then deprecate.
- **HTTP status codes mean what they mean.** 200/201/204 for success; 4xx for client errors; 5xx for server errors. Not "200 with `success: false` in the body."

**Anti-patterns to flag:**

- **Verbs in paths** (`/getUser/{id}`, `/updateOrder`). REST uses nouns; verbs go in methods.
- **GET with side effects.** Cache layers, browsers, and crawlers re-issue GETs freely.
- **200 OK with error in body.** Breaks every standard HTTP client error-handling path.
- **Status codes that don't match the situation** (`404` for unauthorized, `200` for "not found, empty list"). Standard codes communicate to the rest of the ecosystem.
- **Breaking changes within a version.** Adding required fields, removing fields, changing types. These are v2 events.
- **Auth token in the URL** (`?token=...`). Logged everywhere, history-leaked, indexed by search engines.

## Interaction with other layers

The API layer's typical position:

```
Frontend ──► [API] ──► Backend ──► Query ──► Database
   │           │
   └ contract consumed         contract implemented
```

The API Designer's responsibility:

- **Frontend (consumer)** — the Frontend's data needs are an input to API design. The Designer may iterate with the Frontend Designer (via the composer) but the API contract is the API Designer's output.
- **Backend (implementor)** — the API contract drives the Backend's interface. The Backend Designer implements what the API exposes; both Designers may negotiate via the composer if their views diverge.
- **External clients (third parties)** — if the API is public or partner-facing, the contract has additional constraints: stability windows, sunset policies, deprecation announcements, public docs.
- **CI/CD** — contract testing, schema-diff in CI to flag breaking changes. The CI/CD Designer implements; the API Designer documents the gating rules.

## Surfacing architectural questions

The API Designer cannot author ADRs (per FR-5). Use:

```markdown
## Architectural Questions for Composer

- **Q-API-1**: Should this API adopt a stable error envelope across all endpoints? The choice affects 3 layers: API (envelope spec), Backend (error-to-envelope translation), Frontend (envelope-to-UX rendering). Evidence: existing services use 3 different envelope shapes; this new feature interoperates with all of them. Options: (a) adopt RFC 7807 Problem Details; (b) custom shared envelope; (c) maintain existing per-service envelopes for backward compatibility. Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing an API Design subsection — covers the foundational principles (contracts as commitments, idempotency, error envelopes, versioning, status code discipline) |
| `references/patterns-and-anti-patterns.md` | Choosing between REST/GraphQL/gRPC, picking versioning and pagination strategies — covers common patterns with when-to-use, and the anti-patterns reviewers should flag |
